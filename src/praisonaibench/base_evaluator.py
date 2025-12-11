"""
Base evaluator interface for language-specific evaluation plugins.

This enables volunteers to create evaluators for any language (Python, TypeScript, 
Go, Rust, etc.) by implementing just 2 methods.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseEvaluator(ABC):
    """
    Abstract base class for all language evaluators.
    
    Plugin developers: inherit this class and implement the required methods.
    
    Example:
        class PythonEvaluator(BaseEvaluator):
            def get_language(self):
                return 'python'
            
            def evaluate(self, code, test_name, prompt, expected=None):
                # Your evaluation logic
                return {'score': 85, 'passed': True, 'feedback': [...]}
    """
    
    @abstractmethod
    def get_language(self) -> str:
        """
        Return the language/type this evaluator handles.
        
        Returns:
            Language identifier (lowercase). Examples:
            - 'python'
            - 'typescript'
            - 'go'
            - 'rust'
            - 'java'
            - 'html'
        """
        pass
    
    @abstractmethod
    def evaluate(self, 
                 code: str, 
                 test_name: str,
                 prompt: str,
                 expected: Optional[str] = None) -> Dict[str, Any]:
        """
        Evaluate generated code and return assessment.
        
        Args:
            code: The generated code to evaluate
            test_name: Name of the test being run
            prompt: Original prompt/requirement from test suite
            expected: Optional expected output for comparison
        
        Returns:
            Dictionary with evaluation results:
            {
                'score': int (0-100),              # Required
                'passed': bool,                    # Required (typically score >= 70)
                'feedback': list,                  # Required list of feedback items
                'details': dict                    # Optional additional information
            }
            
            Feedback items format:
            {'level': 'success|warning|error', 'message': '...', 'details': '...'}
        """
        pass
    
    def get_file_extension(self) -> str:
        """
        Return file extension for saving code.
        
        Override this if extension differs from language name.
        Default: returns the language name (e.g., 'python' -> .python)
        
        Examples:
            - 'py' for Python
            - 'ts' for TypeScript
            - 'go' for Go
            - 'html' for HTML
        """
        return self.get_language()
