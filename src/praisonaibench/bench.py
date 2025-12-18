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
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import csv
from .cost_tracker import CostTracker
from .report_generator import ReportGenerator
from .enhanced_report import EnhancedReportGenerator
from .plugin_manager import PluginManager
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    MofNCompleteColumn,
)


class Bench:
    """
    Main benchmarking class that orchestrates multiple agents for comprehensive LLM testing.
    
    This class follows the subagent pattern described in the PRD, using specialized
    agents for different types of benchmarking tasks.
    """
    
    def __init__(self, config_file: str = None, enable_evaluation: bool = True):
        """
        Initialize the benchmarking suite.
        
        Args:
            config_file: Optional path to configuration file
            enable_evaluation: Enable evaluation system (default: True)
        """
        self.results = []
        self.config = self._load_config(config_file)
        self.enable_evaluation = enable_evaluation
        self.cost_tracker = CostTracker()
        
        # Initialize plugin manager if evaluation enabled
        self.plugin_manager = None
        if self.enable_evaluation:
            try:
                self.plugin_manager = PluginManager()
                supported_langs = ', '.join(self.plugin_manager.list_languages())
                logging.info(f"✅ Loaded evaluators for: {supported_langs}")
            except Exception as e:
                logging.warning(f"⚠️  Could not initialize plugin manager: {e}")
                self.plugin_manager = None
    
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
    
    def _detect_language(self, response: str, test_config: dict = None) -> str:
        """
        Detect language from response or test configuration.
        
        Args:
            response: LLM response
            test_config: Test configuration dict (may contain 'language' key)
        
        Returns:
            Language identifier
        """
        # 1. Check explicit language in test config
        if test_config and 'language' in test_config:
            return test_config['language'].lower()
        
        # 2. Check for code blocks with language tags (```python, ```typescript, etc.)
        match = re.search(r'```(\w+)', response)
        if match:
            lang = match.group(1).lower()
            # Skip generic 'code' tag
            if lang != 'code':
                return lang
        
        # 3. Check for SVG indicators
        if '<svg' in response.lower() and '</svg>' in response.lower():
            return 'svg'
        
        # 4. Check for HTML indicators
        if '<!doctype' in response.lower() or '<html' in response.lower():
            return 'html'
        
        # 5. Default to HTML (backwards compatible)
        return 'html'
    
    def run_single_test(self,
                       prompt: str,
                       model: str = None,
                       test_name: str = None,
                       llm_config: Dict[str, Any] = None,
                       expected: str = None) -> Dict[str, Any]:
        """
        Run a single benchmark test.
        
        Args:
            prompt: Test prompt (this becomes the instruction to the agent)
            model: LLM model to use (defaults to first model in config)
            test_name: Optional test name
            llm_config: Dictionary of LLM configuration parameters (max_tokens, temperature, etc.)
            expected: Optional expected result for objective comparison
            
        Returns:
            Test result dictionary
        """
        # Validate input parameters
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty or None")
        
        # Use the prompt as the instruction for the agent
        model = model or self.config.get("default_model", "gpt-4o")
        test_name = test_name or f"test_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        logging.info(f"🧪 Starting test: {test_name} with model: {model}")
        
        # Build LLM configuration
        if llm_config is not None:
            # Merge model with provided config
            final_llm_config = llm_config.copy()
            final_llm_config["model"] = model
        else:
            final_llm_config = model
        
        # Create agent with prompt as instruction
        agent = BenchAgent(
            name="BenchAgent",
            llm=final_llm_config,
            instructions=prompt
        )
        
        # Use the agent's run_test method which handles timing and error handling
        result = agent.run_test(prompt, test_name)
        
        # Check if response contains HTML or SVG and save it
        if result['status'] == 'success' and result['response']:
            self._extract_and_save_html(result['response'], test_name, model)
            self._extract_and_save_svg(result['response'], test_name, model)
        
        # Run evaluation if enabled
        if self.plugin_manager and result['status'] == 'success' and result['response']:
            print("\n📊 Evaluating output...")
            
            # Detect language
            test_config = {'language': llm_config.get('language')} if llm_config and 'language' in llm_config else {}
            language = self._detect_language(result['response'], test_config)
            
            # Get appropriate evaluator
            evaluator = self.plugin_manager.get_evaluator(language)
            
            if evaluator:
                print(f"  Using {language} evaluator...")
                try:
                    evaluation = evaluator.evaluate(
                        code=result['response'],
                        test_name=test_name,
                        prompt=prompt,
                        expected=expected
                    )
                    result['evaluation'] = evaluation
                    result['language'] = language
                    
                    # Print summary
                    score = evaluation.get('overall_score', evaluation.get('score', 0))
                    print(f"  Overall Score: {score}/100")
                    status_emoji = '✅ PASSED' if evaluation['passed'] else '❌ FAILED'
                    print(f"  Status: {status_emoji}")
                    
                    # Print feedback
                    for item in evaluation.get('feedback', []):
                        print(f"  {item.get('message', '')}")
                        
                except Exception as e:
                    logging.warning(f"⚠️  Evaluation failed: {str(e)}")
            else:
                print(f"  ⚠️  No evaluator found for language: {language}")
                print(f"  Available: {', '.join(self.plugin_manager.list_languages())}")
        
        # Track costs if available
        if result['status'] == 'success' and 'token_usage' in result:
            token_usage = result['token_usage']
            cost_info = result.get('cost', {})
            self.cost_tracker.add_usage(
                input_tokens=token_usage.get('input_tokens', 0),
                output_tokens=token_usage.get('output_tokens', 0),
                model=model,
                cost=cost_info.get('total_usd', None)
            )
            
            # Print cost info
            if cost_info.get('total_usd', 0) > 0:
                print(f"💰 Cost: ${cost_info['total_usd']:.6f} ({token_usage['total_tokens']} tokens)")
        
        self.results.append(result)
        
        return result
    
    def run_test_suite(self, test_file: str, test_filter: str = None, default_model: str = None, concurrent: int = 1) -> List[Dict[str, Any]]:
        """
        Run a complete test suite from a YAML or JSON file.
        
        Args:
            test_file: Path to test configuration file
            test_filter: Optional test name to run only that specific test
            default_model: Optional model to use for all tests (overrides individual test models)
            concurrent: Number of concurrent workers (default: 1 = sequential)
            
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
        
        # Extract config and tests sections
        if isinstance(tests, dict) and 'tests' in tests:
            test_list = tests['tests']
            suite_config = tests.get('config', {})
        else:
            test_list = tests
            suite_config = {}
        
        # Filter tests if specified
        filtered_tests = []
        for idx, test in enumerate(test_list):
            test_name = test.get('name', f'test_{idx + 1}')
            if test_filter and test_name != test_filter:
                continue
            filtered_tests.append(test)
        
        # Sequential execution (default)
        if concurrent <= 1:
            return self._run_tests_sequential(filtered_tests, suite_config, default_model)
        
        # Parallel execution
        return self._run_tests_parallel(filtered_tests, suite_config, default_model, concurrent)
    
    def _run_tests_sequential(self, test_list: List[Dict], suite_config: Dict, default_model: str = None) -> List[Dict[str, Any]]:
        """Run tests sequentially with progress bar."""
        suite_results = []
        total_tests = len(test_list)
        
        # Create progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style="green", finished_style="bold green"),
            MofNCompleteColumn(),
            TextColumn("•"),
            TimeElapsedColumn(),
            TextColumn("•"),
            TimeRemainingColumn(),
        ) as progress:
            
            # Add overall progress task
            overall_task = progress.add_task(
                "[cyan]Running tests...",
                total=total_tests
            )
            
            for idx, test in enumerate(test_list, 1):
                prompt = test.get('prompt', '')
                model = default_model or test.get('model', None)
                test_name = test.get('name', f'test_{idx}')
                expected = test.get('expected', None)
                
                # Update progress description
                progress.update(
                    overall_task,
                    description=f"[cyan]Test {idx}/{total_tests}: {test_name}"
                )
                
                result = self.run_single_test(prompt, model, test_name, llm_config=suite_config, expected=expected)
                suite_results.append(result)
                
                # Update progress
                progress.update(overall_task, advance=1)
                
                # Show completion message
                if result['status'] == 'success':
                    print(f"  ✅ Completed: {test_name}")
                else:
                    print(f"  ❌ Failed: {test_name} - {result.get('response', 'Unknown error')}")
        
        return suite_results
    
    def _run_tests_parallel(self, test_list: List[Dict], suite_config: Dict, default_model: str = None, max_workers: int = 3) -> List[Dict[str, Any]]:
        """Run tests in parallel with progress bar."""
        suite_results = []
        results_lock = threading.Lock()
        total_tests = len(test_list)
        
        print(f"⚡ Running {total_tests} tests with {max_workers} concurrent workers...\n")
        
        # Create progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style="green", finished_style="bold green"),
            MofNCompleteColumn(),
            TextColumn("•"),
            TimeElapsedColumn(),
            TextColumn("•"),
            TimeRemainingColumn(),
        ) as progress:
            
            overall_task = progress.add_task(
                "[cyan]Running tests (concurrent)...",
                total=total_tests
            )
            
            completed_count = [0]
            
            def run_test_wrapper(test_info):
                """Wrapper for running a single test in a thread."""
                idx, test = test_info
                prompt = test.get('prompt', '')
                model = default_model or test.get('model', None)
                test_name = test.get('name', f'test_{idx + 1}')
                expected = test.get('expected', None)
                
                try:
                    result = self.run_single_test(prompt, model, test_name, llm_config=suite_config, expected=expected)
                    
                    with results_lock:
                        completed_count[0] += 1
                        progress.update(
                            overall_task,
                            advance=1,
                            description=f"[cyan]Running tests... [{completed_count[0]}/{total_tests}]"
                        )
                        
                        if result['status'] == 'success':
                            print(f"  ✅ [{completed_count[0]}/{total_tests}] Completed: {test_name}")
                        else:
                            print(f"  ❌ [{completed_count[0]}/{total_tests}] Failed: {test_name}")
                    
                    return result
                except Exception as e:
                    with results_lock:
                        completed_count[0] += 1
                        progress.update(overall_task, advance=1)
                        print(f"  ❌ [{completed_count[0]}/{total_tests}] Error: {test_name}")
                    return {
                        'test_name': test_name,
                        'status': 'error',
                        'response': str(e),
                        'execution_time': 0
                    }
            
            # Run tests in parallel
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(run_test_wrapper, (idx, test)): idx 
                          for idx, test in enumerate(test_list)}
                
                for future in as_completed(futures):
                    result = future.result()
                    suite_results.append(result)
        
        # Sort results by test_name to maintain consistent ordering
        suite_results.sort(key=lambda x: x.get('test_name', ''))
        
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
    
    def save_results(self, filename: str = None, format: str = "json") -> str:
        """
        Save benchmark results to file.
        
        Args:
            filename: Optional custom filename
            format: Output format - "json" or "csv" (default: "json")
            
        Returns:
            Path to saved file
        """
        if format.lower() == "csv":
            return self.save_results_csv(filename)
        else:
            return self.save_results_json(filename)
    
    def save_results_json(self, filename: str = None) -> str:
        """
        Save benchmark results to JSON file.
        
        Args:
            filename: Optional custom filename
            
        Returns:
            Path to saved file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"benchmark_results_{timestamp}.json"
        
        # Create json subdirectory for better organization
        output_dir = self.config.get("output_dir", "output")
        json_dir = os.path.join(output_dir, "json")
        os.makedirs(json_dir, exist_ok=True)
        
        filepath = os.path.join(json_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"Results saved to: {filepath}")
        return filepath
    
    def save_results_csv(self, filename: str = None) -> str:
        """
        Save benchmark results to CSV file.
        
        Args:
            filename: Optional custom filename
            
        Returns:
            Path to saved file
        """
        if not self.results:
            print("No results to save")
            return None
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"benchmark_results_{timestamp}.csv"
        
        # Ensure .csv extension
        if not filename.endswith('.csv'):
            if filename.endswith('.json'):
                filename = filename.replace('.json', '.csv')
            else:
                filename = filename + '.csv'
        
        # Create csv subdirectory for better organization
        output_dir = self.config.get("output_dir", "output")
        csv_dir = os.path.join(output_dir, "csv")
        os.makedirs(csv_dir, exist_ok=True)
        
        filepath = os.path.join(csv_dir, filename)
        
        # Define CSV columns
        fieldnames = [
            'test_name',
            'status',
            'model',
            'execution_time',
            'timestamp',
            'input_tokens',
            'output_tokens',
            'total_tokens',
            'cost_usd',
            'evaluation_score',
            'evaluation_passed',
            'prompt',
            'response_length',
            'retry_attempts',
            'error'
        ]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            
            for result in self.results:
                # Extract model name (handle both string and dict)
                model = result.get('model')
                if isinstance(model, dict):
                    model_name = model.get('model', str(model))
                else:
                    model_name = str(model) if model else ''
                
                # Extract token usage
                token_usage = result.get('token_usage', {})
                cost_info = result.get('cost', {})
                
                # Extract evaluation info
                evaluation = result.get('evaluation', {})
                eval_score = evaluation.get('overall_score', '') if evaluation else ''
                eval_passed = evaluation.get('passed', '') if evaluation else ''
                
                # Create CSV row
                row = {
                    'test_name': result.get('test_name', ''),
                    'status': result.get('status', ''),
                    'model': model_name,
                    'execution_time': f"{result.get('execution_time', 0):.2f}",
                    'timestamp': result.get('timestamp', ''),
                    'input_tokens': token_usage.get('input_tokens', ''),
                    'output_tokens': token_usage.get('output_tokens', ''),
                    'total_tokens': token_usage.get('total_tokens', ''),
                    'cost_usd': f"{cost_info.get('total_usd', 0):.6f}" if cost_info.get('total_usd') else '',
                    'evaluation_score': eval_score,
                    'evaluation_passed': eval_passed,
                    'prompt': result.get('prompt', ''),
                    'response_length': len(result.get('response', '')) if result.get('response') else 0,
                    'retry_attempts': result.get('retry_attempts', ''),
                    'error': result.get('error', '')
                }
                
                writer.writerow(row)
        
        print(f"Results saved to: {filepath}")
        return filepath
    
    def generate_report(self, output_path: str = None, enhanced: bool = True) -> str:
        """
        Generate HTML report from results.
        
        Args:
            output_path: Optional path for report file
            enhanced: Use enhanced report with all UI features (default: True)
            
        Returns:
            Path to generated report
        """
        if not self.results:
            print("No results to generate report from")
            return None
        
        summary = self.get_summary()
        
        if enhanced:
            return EnhancedReportGenerator.generate(self.results, summary, output_path)
        else:
            return ReportGenerator.generate_html_report(self.results, summary, output_path)
    
    @staticmethod
    def generate_report_from_file(results_file: str, output_path: str = None) -> str:
        """
        Generate HTML report from existing results file.
        
        Args:
            results_file: Path to JSON results file
            output_path: Optional path for report file
            
        Returns:
            Path to generated report
        """
        if not os.path.exists(results_file):
            print(f"❌ Results file not found: {results_file}")
            return None
        
        print(f"📖 Reading results from: {results_file}")
        
        # Load results from file
        with open(results_file, 'r') as f:
            data = json.load(f)
        
        # Handle different JSON structures
        if isinstance(data, list):
            # Direct list of results
            results = data
            summary = {}
        elif isinstance(data, dict):
            # Dict with 'results' key or single result
            results = data.get('results', [data] if data else [])
            summary = data.get('summary', {})
        else:
            print("❌ Invalid JSON format")
            return None
        
        if not results:
            print("❌ No results found in file")
            return None
        
        # If no summary exists, build basic one from results
        if not summary:
            total = len(results)
            success = sum(1 for r in results if r.get('status') == 'success')
            total_time = sum(r.get('execution_time', 0) for r in results)
            
            summary = {
                'total_tests': total,
                'successful_tests': success,
                'failed_tests': total - success,
                'success_rate': f"{(success/total*100):.1f}%" if total > 0 else "0%",
                'total_execution_time': f"{total_time:.2f}s",
                'average_execution_time': f"{(total_time/total):.2f}s" if total > 0 else "0s",
                'cost_summary': {}
            }
            
            # Try to build cost summary if token data exists
            total_input = sum(r.get('token_usage', {}).get('input_tokens', 0) for r in results)
            total_output = sum(r.get('token_usage', {}).get('output_tokens', 0) for r in results)
            total_cost = sum(r.get('cost', {}).get('total_usd', 0) for r in results)
            
            if total_input > 0 or total_output > 0:
                summary['cost_summary'] = {
                    'total_input_tokens': total_input,
                    'total_output_tokens': total_output,
                    'total_tokens': total_input + total_output,
                    'total_cost_usd': total_cost
                }
        
        print(f"✅ Loaded {len(results)} test results")
        return EnhancedReportGenerator.generate(results, summary, output_path)
    
    @staticmethod
    def compare_results(result_files: list, output_path: str = None) -> str:
        """
        Generate comparison report from multiple results files.
        
        Args:
            result_files: List of paths to JSON results files
            output_path: Optional path for comparison report
            
        Returns:
            Path to generated comparison report
        """
        if not result_files or len(result_files) < 2:
            print("❌ Need at least 2 result files to compare")
            return None
        
        print(f"📊 Comparing {len(result_files)} test runs...")
        
        all_runs = []
        for i, file_path in enumerate(result_files):
            if not os.path.exists(file_path):
                print(f"⚠️  Skipping missing file: {file_path}")
                continue
            
            print(f"  [{i+1}] Loading: {file_path}")
            
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Handle different JSON structures
            if isinstance(data, list):
                results = data
                summary = {}
            elif isinstance(data, dict):
                results = data.get('results', [data] if data else [])
                summary = data.get('summary', {})
            else:
                continue
            
            # Build run info
            run_info = {
                'file': os.path.basename(file_path),
                'full_path': file_path,
                'results': results,
                'summary': summary,
                'timestamp': file_path.split('_')[-2:] if '_' in file_path else ['unknown'],
            }
            all_runs.append(run_info)
        
        if len(all_runs) < 2:
            print("❌ Need at least 2 valid result files")
            return None
        
        print(f"✅ Loaded {len(all_runs)} runs for comparison")
        return ReportGenerator.generate_comparison_report(all_runs, output_path)
    
    def _extract_and_save_html(self, response, test_name, model=None):
        """Extract HTML code from response and save to .html file if found."""
        html_content = None
        
        # First, look for complete HTML code blocks in markdown format
        html_pattern = r'```html\s*\n(.*?)\n```'
        matches = re.findall(html_pattern, response, re.DOTALL | re.IGNORECASE)
        
        if matches:
            # Use the first complete HTML block found
            html_content = matches[0].strip()
            print(f"✅ Found complete HTML block ({len(html_content)} chars)")
        else:
            # Check for truncated HTML blocks (starts with ```html but no closing ```)
            truncated_pattern = r'```html\s*\n(.*)'
            truncated_matches = re.findall(truncated_pattern, response, re.DOTALL | re.IGNORECASE)
            
            if truncated_matches:
                # Use the truncated HTML content
                html_content = truncated_matches[0].strip()
                print(f"⚠️  Found truncated HTML block ({len(html_content)} chars) - attempting to extract")
            else:
                # Check if the entire response is raw HTML (starts with <!doctype or <html)
                response_stripped = response.strip()
                if (response_stripped.lower().startswith('<!doctype') or 
                    response_stripped.lower().startswith('<html')):
                    html_content = response_stripped
                    print(f"✅ Found raw HTML content ({len(html_content)} chars)")
            
        if html_content:
            
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
    
    def _extract_and_save_svg(self, response, test_name, model=None):
        """Extract SVG code from response and save to .svg file if found."""
        svg_content = None
        
        # Look for SVG code blocks in markdown format
        svg_pattern = r'```(?:svg|xml)\s*\n(.*?)\n```'
        matches = re.findall(svg_pattern, response, re.DOTALL | re.IGNORECASE)
        
        if matches:
            for match in matches:
                if '<svg' in match.lower():
                    svg_content = match.strip()
                    print(f"✅ Found complete SVG block ({len(svg_content)} chars)")
                    break
        
        if not svg_content:
            # Try to find raw SVG
            svg_raw_pattern = r'(<svg[^>]*>.*?</svg>)'
            raw_matches = re.findall(svg_raw_pattern, response, re.DOTALL | re.IGNORECASE)
            
            if raw_matches:
                svg_content = raw_matches[0].strip()
                print(f"✅ Found raw SVG content ({len(svg_content)} chars)")
        
        if svg_content:
            filename = f"{test_name}.svg"
            
            # Create model-specific output directory
            base_output_dir = "output/svg"
            if model:
                output_dir = os.path.join(base_output_dir, model)
            else:
                output_dir = base_output_dir
            os.makedirs(output_dir, exist_ok=True)
            
            # Save SVG file
            svg_path = os.path.join(output_dir, filename)
            try:
                with open(svg_path, 'w', encoding='utf-8') as f:
                    f.write(svg_content)
                print(f"💾 SVG file saved: {svg_path}")
            except Exception as e:
                print(f"⚠️  Failed to save SVG file {svg_path}: {e}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of benchmark results including costs."""
        if not self.results:
            return {"message": "No results available"}
        
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if r.get("status") == "success"])
        failed_tests = total_tests - successful_tests
        
        # Extract model names, handling both string and dict model configs
        model_names = []
        for r in self.results:
            model = r.get("model")
            if isinstance(model, dict):
                # If model is a dict (LLM config), extract the model name
                model_names.append(model.get("model", "unknown"))
            elif isinstance(model, str):
                model_names.append(model)
            else:
                model_names.append("unknown")
        models_tested = list(set(model_names))
        
        avg_execution_time = sum([r.get("execution_time", 0) for r in self.results]) / total_tests
        
        # Get cost summary
        cost_summary = self.cost_tracker.get_summary()
        
        summary = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "success_rate": f"{(successful_tests/total_tests)*100:.1f}%",
            "models_tested": models_tested,
            "average_execution_time": f"{avg_execution_time:.2f}s",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Add cost information if available
        if cost_summary["total_tokens"] > 0:
            summary["cost_summary"] = {
                "total_tokens": cost_summary["total_tokens"],
                "total_cost_usd": cost_summary["total_cost_usd"],
                "by_model": cost_summary["by_model"]
            }
        
        return summary
