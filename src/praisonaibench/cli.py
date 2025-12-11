"""
CLI - Command Line Interface for PraisonAI Bench

Simple command-line interface for running benchmarks.
"""

import argparse
import sys
import os
import json
from .bench import Bench
from .version import __version__


def extract_html_from_results(results_file, bench):
    """Extract HTML content from benchmark results JSON file and save as .html files."""
    try:
        with open(results_file, 'r', encoding='utf-8') as f:
            results_data = json.load(f)
    except Exception as e:
        raise Exception(f"Failed to read results file: {e}")
    
    extracted_count = 0
    
    # Handle both single result and list of results
    if isinstance(results_data, dict):
        results_list = [results_data]
    elif isinstance(results_data, list):
        results_list = results_data
    else:
        raise Exception("Invalid results file format")
    
    for result in results_list:
        if 'response' in result and 'test_name' in result:
            response = result['response']
            test_name = result['test_name']
            model = result.get('model', None)
            
            # Use the existing HTML extraction method from bench
            try:
                bench._extract_and_save_html(response, test_name, model)
                extracted_count += 1
            except Exception as e:
                print(f"⚠️  Failed to extract HTML for test '{test_name}': {e}")
    
    return extracted_count


def main():
    """Main CLI entry point."""
    # Handle --compare FIRST before any other processing
    if '--compare' in sys.argv:
        idx = sys.argv.index('--compare')
        # Collect all file arguments after --compare until next flag
        result_files = []
        i = idx + 1
        while i < len(sys.argv) and not sys.argv[i].startswith('--'):
            result_files.append(sys.argv[i])
            i += 1
        
        if len(result_files) < 2:
            print("❌ Error: --compare requires at least 2 result files")
            sys.exit(1)
        
        output_file = None
        if '--output' in sys.argv:
            out_idx = sys.argv.index('--output')
            if out_idx + 1 < len(sys.argv):
                output_file = sys.argv[out_idx + 1]
        
        # Generate comparison report and exit
        Bench.compare_results(result_files, output_file)
        sys.exit(0)
    
    # Handle --report-from FIRST before any other processing
    if '--report-from' in sys.argv:
        idx = sys.argv.index('--report-from')
        if idx + 1 < len(sys.argv):
            results_file = sys.argv[idx + 1]
            output_file = None
            
            # Check for --output flag
            if '--output' in sys.argv:
                out_idx = sys.argv.index('--output')
                if out_idx + 1 < len(sys.argv):
                    output_file = sys.argv[out_idx + 1]
            
            # Generate report and exit
            Bench.generate_report_from_file(results_file, output_file)
            sys.exit(0)
        else:
            print("❌ Error: --report-from requires a file path")
            sys.exit(1)
    
    parser = argparse.ArgumentParser(
        description="PraisonAI Bench - Simple LLM Benchmarking Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  praisonaibench --test "What is 2+2?"
  praisonaibench --test "Explain quantum computing" --model gpt-4o
  praisonaibench --suite tests.yaml
  praisonaibench --suite tests.yaml --test-name "terrain_simulation"
  praisonaibench --suite tests.yaml --concurrent 3
  praisonaibench --suite tests.yaml --format csv
  praisonaibench --suite tests.yaml --report
  praisonaibench --report-from output/json/benchmark_results_20241211.json
  praisonaibench --compare file1.json file2.json file3.json
  praisonaibench --cross-model "Write a poem" --models gpt-4o,gpt-3.5-turbo
  praisonaibench --extract output/json/benchmark_results_20250829_173322.json
        """
    )
    
    parser.add_argument('--version', action='version', version=f'PraisonAI Bench {__version__}')
    
    # Single test options
    parser.add_argument('--test', type=str, help='Run a single test with the given prompt')
    parser.add_argument('--model', type=str, help='Model to use (defaults to first model in config)')
    
    # Test suite options
    parser.add_argument('--suite', type=str, help='Run test suite from YAML/JSON file')
    parser.add_argument('--test-name', type=str, help='Run only the specified test from the suite (use with --suite)')
    parser.add_argument('--concurrent', type=int, default=1, metavar='N',
                       help='Number of concurrent workers for parallel test execution (default: 1 = sequential)')
    
    # Cross-model testing
    parser.add_argument('--cross-model', type=str, help='Run same test across multiple models')
    parser.add_argument('--models', type=str, help='Comma-separated list of models to test')
    
    # Configuration
    parser.add_argument('--config', type=str, help='Configuration file path')
    
    # Evaluation options
    parser.add_argument('--no-eval', action='store_true', 
                       help='Disable evaluation system (faster, no quality assessment)')
    parser.add_argument('--no-llm-judge', action='store_true',
                       help='Disable LLM-as-a-Judge (functional validation only)')
    
    # Output options
    parser.add_argument('--output', type=str, help='Output file for results')
    parser.add_argument('--format', type=str, choices=['json', 'csv'], default='json',
                       help='Output format: json or csv (default: json)')
    parser.add_argument('--report', action='store_true',
                       help='Generate HTML report with charts and visualizations')
    parser.add_argument('--report-from', type=str, metavar='FILE',
                       help='Generate HTML report from existing JSON results file')
    parser.add_argument('--compare', nargs='+', metavar='FILE',
                       help='Compare multiple test results (provide 2+ JSON files)')
    
    # Extract HTML from existing results
    parser.add_argument('--extract', type=str, help='Extract HTML from existing benchmark results JSON file')
    
    args = parser.parse_args()
    
    # Initialize bench
    try:
        # Prepare config with evaluation settings
        config_overrides = {}
        if args.no_llm_judge:
            config_overrides['use_llm_judge'] = False
        
        bench = Bench(
            config_file=args.config,
            enable_evaluation=not args.no_eval
        )
        
        # Apply config overrides
        if config_overrides:
            bench.config.update(config_overrides)
        print(f"🚀 PraisonAI Bench v{__version__} initialized")
        print("Using LiteLLM - supports any compatible model (e.g., gpt-4o, gemini/gemini-1.5-flash, xai/grok-code-fast-1)")
        
    except Exception as e:
        print(f"❌ Error initializing bench: {e}")
        sys.exit(1)
    
    # Run single test
    if args.test:
        model_name = args.model or bench.config.get('default_model', 'gpt-4o')
        print(f"\n🧪 Running single test with {model_name} model...")
        try:
            result = bench.run_single_test(args.test, args.model)
            print(f"✅ Test completed in {result['execution_time']:.2f}s")
            print(f"Response length: {len(result['response'])} characters")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            sys.exit(1)
    
    # Run test suite
    elif args.suite:
        if not os.path.exists(args.suite):
            print(f"❌ Test suite file not found: {args.suite}")
            sys.exit(1)
            
        if args.test_name:
            print(f"\n📋 Running test '{args.test_name}' from {args.suite}...")
        else:
            concurrent_msg = f" (concurrent: {args.concurrent})" if args.concurrent > 1 else ""
            print(f"\n📋 Running test suite from {args.suite}{concurrent_msg}...")
        try:
            results = bench.run_test_suite(args.suite, test_filter=args.test_name, default_model=args.model, concurrent=args.concurrent)
            if args.test_name:
                print(f"✅ Test '{args.test_name}' completed")
            else:
                print(f"✅ Test suite completed: {len(results)} tests")
            
        except Exception as e:
            print(f"❌ Error running test suite: {e}")
            sys.exit(1)
    
    # Run cross-model test
    elif args.cross_model:
        models = args.models.split(',') if args.models else None
        print(f"\n🔄 Running cross-model test...")
        try:
            results = bench.run_cross_model_test(args.cross_model, models)
            print(f"✅ Cross-model test completed: {len(results)} models tested")
            
        except Exception as e:
            print(f"❌ Cross-model test failed: {e}")
            sys.exit(1)
    
    # Extract HTML from existing results
    elif args.extract:
        if not os.path.exists(args.extract):
            print(f"❌ Results file not found: {args.extract}")
            sys.exit(1)
            
        print(f"\n🔍 Extracting HTML from {args.extract}...")
        try:
            extracted_count = extract_html_from_results(args.extract, bench)
            if extracted_count > 0:
                print(f"✅ Successfully extracted and saved {extracted_count} HTML files")
            else:
                print("ℹ️  No HTML content found in the results file")
            
        except Exception as e:
            print(f"❌ Error extracting HTML: {e}")
            sys.exit(1)
        
        # Exit early for extract operation - no need for summary or saving
        return
    
    # Default to tests.yaml if no specific command provided
    else:
        default_suite = "tests.yaml"
        if os.path.exists(default_suite):
            concurrent_msg = f" (concurrent: {args.concurrent})" if args.concurrent > 1 else ""
            print(f"\n📋 No command specified, running default test suite: {default_suite}{concurrent_msg}...")
            try:
                results = bench.run_test_suite(default_suite, test_filter=args.test_name, default_model=args.model, concurrent=args.concurrent)
                if args.test_name:
                    print(f"✅ Test '{args.test_name}' completed")
                else:
                    print(f"✅ Test suite completed: {len(results)} tests")
                
            except Exception as e:
                print(f"❌ Error running default test suite: {e}")
                sys.exit(1)
        else:
            print(f"\n❌ No command specified and default test suite '{default_suite}' not found.")
            print("\nCreate a tests.yaml file or use one of these commands:")
            print("  praisonaibench --test 'Your prompt here'")
            print("  praisonaibench --suite your_suite.yaml")
            print("  praisonaibench --cross-model 'Your prompt' --models model1,model2")
            parser.print_help()
            sys.exit(1)
    
    # Show summary
    summary = bench.get_summary()
    print(f"\n📊 Summary:")
    print(f"   Total tests: {summary['total_tests']}")
    print(f"   Success rate: {summary['success_rate']}")
    print(f"   Average time: {summary['average_execution_time']}")
    
    # Show cost summary if available
    if 'cost_summary' in summary:
        cost_info = summary['cost_summary']
        print(f"\n💰 Cost Summary:")
        print(f"   Total tokens: {cost_info['total_tokens']:,}")
        print(f"   Total cost: ${cost_info['total_cost_usd']:.4f}")
        
        # Show per-model breakdown if multiple models
        if len(cost_info['by_model']) > 1:
            print(f"\n   By model:")
            for model, data in cost_info['by_model'].items():
                print(f"     {model}: ${data['cost']:.4f} ({data['input_tokens'] + data['output_tokens']:,} tokens)")
    
    # Save results
    if args.output:
        bench.save_results(args.output, format=args.format)
    elif bench.config.get('save_results', True):
        bench.save_results(format=args.format)
    
    # Generate HTML report if requested
    if args.report:
        bench.generate_report()


if __name__ == '__main__':
    main()
