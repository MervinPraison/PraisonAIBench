"""
Plugin manager for discovering and loading evaluator plugins.

Uses Python entry points for automatic plugin discovery.
"""

import logging
from typing import Dict, Optional

try:
    # Python 3.10+
    from importlib.metadata import entry_points
except ImportError:
    # Python 3.8-3.9
    from importlib_metadata import entry_points

from .base_evaluator import BaseEvaluator


class PluginManager:
    """
    Manages evaluator plugins for different languages.
    
    Plugins are discovered automatically via entry points.
    """
    
    def __init__(self):
        """Initialize plugin manager and discover plugins."""
        self.evaluators: Dict[str, BaseEvaluator] = {}
        self._load_builtin_evaluators()
        self._discover_plugins()
    
    def _load_builtin_evaluators(self):
        """Load built-in evaluators (HTML/JavaScript, SVG)."""
        # Load HTML evaluator
        try:
            from .evaluators.html_evaluator import HTMLEvaluator
            html_eval = HTMLEvaluator()
            
            # Register with multiple aliases
            self.register('html', html_eval)
            self.register('javascript', html_eval)
            self.register('js', html_eval)
            
            logging.info("✅ Loaded built-in HTML/JavaScript evaluator")
        except ImportError as e:
            logging.warning(f"⚠️  Could not load HTML evaluator: {e}")
        
        # Load SVG evaluator
        try:
            from .evaluators.svg_evaluator import SVGEvaluator
            svg_eval = SVGEvaluator(use_llm_judge=False)  # Disable LLM by default
            
            self.register('svg', svg_eval)
            
            logging.info("✅ Loaded built-in SVG evaluator")
        except ImportError as e:
            logging.warning(f"⚠️  Could not load SVG evaluator: {e}")
    
    def _discover_plugins(self):
        """Discover and load plugins via entry points."""
        try:
            # Get all entry points in our group
            try:
                # Python 3.10+ syntax
                eps = entry_points(group='praisonaibench.evaluators')
            except TypeError:
                # Python 3.8-3.9 syntax
                all_eps = entry_points()
                eps = all_eps.get('praisonaibench.evaluators', [])
            
            loaded_count = 0
            for ep in eps:
                try:
                    # Load the evaluator class
                    evaluator_class = ep.load()
                    
                    # Instantiate it
                    evaluator = evaluator_class()
                    
                    # Validate it's a BaseEvaluator
                    if not isinstance(evaluator, BaseEvaluator):
                        logging.warning(
                            f"⚠️  Plugin {ep.name} does not inherit from BaseEvaluator"
                        )
                        continue
                    
                    # Register it
                    language = evaluator.get_language()
                    self.register(language, evaluator)
                    
                    print(f"  ✅ Loaded plugin: {language} (from {ep.name})")
                    loaded_count += 1
                    
                except Exception as e:
                    logging.warning(f"⚠️  Failed to load plugin {ep.name}: {e}")
            
            if loaded_count > 0:
                logging.info(f"✅ Loaded {loaded_count} plugin(s)")
                
        except Exception as e:
            logging.warning(f"⚠️  Plugin discovery failed: {e}")
    
    def register(self, language: str, evaluator: BaseEvaluator):
        """
        Register an evaluator for a language.
        
        Args:
            language: Language identifier (case-insensitive)
            evaluator: Evaluator instance
        """
        self.evaluators[language.lower()] = evaluator
    
    def get_evaluator(self, language: str) -> Optional[BaseEvaluator]:
        """
        Get evaluator for a language.
        
        Args:
            language: Language identifier (case-insensitive)
        
        Returns:
            Evaluator instance or None if not found
        """
        return self.evaluators.get(language.lower())
    
    def list_languages(self) -> list:
        """
        Get list of all supported languages.
        
        Returns:
            List of language identifiers
        """
        return sorted(self.evaluators.keys())
    
    def has_evaluator(self, language: str) -> bool:
        """
        Check if evaluator exists for a language.
        
        Args:
            language: Language identifier (case-insensitive)
        
        Returns:
            True if evaluator exists
        """
        return language.lower() in self.evaluators
