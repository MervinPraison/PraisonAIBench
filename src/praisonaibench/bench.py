"""
Bench - Main benchmarking class for PraisonAI Bench

This module provides the core benchmarking functionality using multiple agents
to evaluate LLM performance across different tasks and models.
"""

from .agent import BenchAgent
from typing import Dict, List, Any, Optional
import json
import os
import yaml
from datetime import datetime
import re


class Bench:
    """
    Main benchmarking class that orchestrates multiple agents for comprehensive LLM testing.
    
    This class follows the subagent pattern described in the PRD, using specialized
    agents for different types of benchmarking tasks.
    """
    
    def __init__(self, config_file: str = None):
        """
        Initialize the benchmarking suite.
        
        Args:
            config_file: Optional path to configuration file
        """
        self.results = []
        self.config = self._load_config(config_file)
    
    def _load_config(self, config_file: str = None) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        default_config = {
            "default_model": "gpt-4o",
            "output_format": "json",
            "save_results": True,
            "output_dir": "output",
            "max_retries": 3,
            "timeout": 60
        }
        
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    if config_file.endswith('.yaml') or config_file.endswith('.yml'):
                        user_config = yaml.safe_load(f)
                    else:
                        user_config = json.load(f)
                
                # Merge with defaults
                default_config.update(user_config)
            except Exception as e:
                print(f"Warning: Could not load config file {config_file}: {e}")
                print("Using default configuration.")
        
        return default_config
    

    

    
    def run_single_test(self, 
                       prompt: str, 
                       model: str = None,
                       test_name: str = None) -> Dict[str, Any]:
        """
        Run a single benchmark test.
        
        Args:
            prompt: Test prompt (this becomes the instruction to the agent)
            model: LLM model to use (defaults to first model in config)
            test_name: Optional test name
            
        Returns:
            Test result dictionary
        """
        # Use the prompt as the instruction for the agent
        model = model or self.config.get("default_model", "gpt-4o")
        
        # Create agent with prompt as instruction
        agent = BenchAgent(
            name="BenchAgent",
            llm=model,
            instructions=prompt
        )
        
        # Use the agent's run_test method which handles timing and error handling
        result = agent.run_test(prompt, test_name)
        
        # Check if response contains HTML and save it
        if result['status'] == 'success' and result['response']:
            self._extract_and_save_html(result['response'], test_name, model)
        
        self.results.append(result)
        
        return result
    
    def run_test_suite(self, test_file: str, test_filter: str = None, default_model: str = None) -> List[Dict[str, Any]]:
        """
        Run a complete test suite from a YAML or JSON file.
        
        Args:
            test_file: Path to test configuration file
            test_filter: Optional test name to run only that specific test
            default_model: Optional model to use for all tests (overrides individual test models)
            
        Returns:
            List of all test results
        """
        if not os.path.exists(test_file):
            raise FileNotFoundError(f"Test file not found: {test_file}")
        
        # Load test configuration
        with open(test_file, 'r') as f:
            if test_file.endswith('.yaml') or test_file.endswith('.yml'):
                tests = yaml.safe_load(f)
            else:
                tests = json.load(f)
        
        suite_results = []
        
        # Run tests
        if isinstance(tests, dict) and 'tests' in tests:
            test_list = tests['tests']
        else:
            test_list = tests
        
        for test in test_list:
            prompt = test.get('prompt', '')
            model = default_model or test.get('model', None)  # Use default_model if provided
            test_name = test.get('name', f'test_{len(suite_results) + 1}')
            
            # Skip test if filter is specified and doesn't match
            if test_filter and test_name != test_filter:
                continue
            
            print(f"Running test: {test_name}")
            result = self.run_single_test(prompt, model, test_name)
            suite_results.append(result)
            
            if result['status'] == 'success':
                print(f"✅ Completed: {test_name}")
            else:
                print(f"❌ Failed: {test_name} - {result.get('response', 'Unknown error')}")
        
        return suite_results
    
    def run_cross_model_test(self, 
                           prompt: str, 
                           models: List[str] = None) -> List[Dict[str, Any]]:
        """
        Run the same test across multiple models for comparison.
        
        Args:
            prompt: Test prompt
            models: List of models to test (uses config models if None)
            
        Returns:
            List of results from different models
        """
        if models is None:
            models = [self.config.get("default_model", "gpt-4o")]
        
        cross_model_results = []
        
        for model in models:
            result = self.run_single_test(prompt, model, f"cross_model_{model}")
            cross_model_results.append(result)
            
            print(f"✓ Tested model: {model}")
        
        return cross_model_results
    
    def save_results(self, filename: str = None) -> str:
        """
        Save benchmark results to file.
        
        Args:
            filename: Optional custom filename
            
        Returns:
            Path to saved file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"benchmark_results_{timestamp}.json"
        
        output_dir = self.config.get("output_dir", "output")
        os.makedirs(output_dir, exist_ok=True)
        
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"Results saved to: {filepath}")
        return filepath
    
    def _extract_and_save_html(self, response, test_name, model=None):
        """Extract HTML code from response and save to .html file if found."""
        # Look for HTML code blocks in markdown format
        html_pattern = r'```html\s*\n(.*?)\n```'
        matches = re.findall(html_pattern, response, re.DOTALL | re.IGNORECASE)
        
        if matches:
            # Use the first HTML block found
            html_content = matches[0].strip()
            
            # Determine filename - look for specific filenames mentioned in the prompt/response
            filename_patterns = [
                r'save.*?as\s+["\']([^"\'\.]+\.html)["\']',
                r'save.*?to\s+["\']([^"\'\.]+\.html)["\']',
                r'named\s+["\']([^"\'\.]+\.html)["\']',
                r'file\s+["\']([^"\'\.]+\.html)["\']'
            ]
            
            filename = None
            for pattern in filename_patterns:
                match = re.search(pattern, response, re.IGNORECASE)
                if match:
                    filename = match.group(1)
                    break
            
            # Fallback to test name if no specific filename found
            if not filename:
                filename = f"{test_name}.html"
            
            # Create model-specific output directory
            base_output_dir = "output"
            if model:
                output_dir = os.path.join(base_output_dir, model)
            else:
                output_dir = base_output_dir
            os.makedirs(output_dir, exist_ok=True)
            
            # Save HTML file
            html_path = os.path.join(output_dir, filename)
            try:
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print(f"💾 HTML file saved: {html_path}")
            except Exception as e:
                print(f"⚠️  Failed to save HTML file {html_path}: {e}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of benchmark results."""
        if not self.results:
            return {"message": "No results available"}
        
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if r.get("status") == "success"])
        failed_tests = total_tests - successful_tests
        
        models_tested = list(set([r.get("model") for r in self.results]))
        
        avg_execution_time = sum([r.get("execution_time", 0) for r in self.results]) / total_tests
        
        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "success_rate": f"{(successful_tests/total_tests)*100:.1f}%",
            "models_tested": models_tested,
            "average_execution_time": f"{avg_execution_time:.2f}s",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
