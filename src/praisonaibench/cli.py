"""
CLI - Command Line Interface for PraisonAI Bench

Simple command-line interface for running benchmarks.
"""

import argparse
import sys
import os
from .bench import Bench
from .version import __version__


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="PraisonAI Bench - Simple LLM Benchmarking Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  praisonaibench --test "What is 2+2?"
  praisonaibench --test "Explain quantum computing" --model gpt-4o
  praisonaibench --suite tests.yaml
  praisonaibench --suite tests.yaml --test-name "terrain_simulation"
  praisonaibench --cross-model "Write a poem" --models gpt-4o,gpt-3.5-turbo
        """
    )
    
    parser.add_argument('--version', action='version', version=f'PraisonAI Bench {__version__}')
    
    # Single test options
    parser.add_argument('--test', type=str, help='Run a single test with the given prompt')
    parser.add_argument('--model', type=str, help='Model to use (defaults to first model in config)')
    
    # Test suite options
    parser.add_argument('--suite', type=str, help='Run test suite from YAML/JSON file')
    parser.add_argument('--test-name', type=str, help='Run only the specified test from the suite (use with --suite)')
    
    # Cross-model testing
    parser.add_argument('--cross-model', type=str, help='Run same test across multiple models')
    parser.add_argument('--models', type=str, help='Comma-separated list of models to test')
    
    # Configuration
    parser.add_argument('--config', type=str, help='Configuration file path')
    parser.add_argument('--output', type=str, help='Output file for results')
    
    args = parser.parse_args()
    
    # Initialize bench
    try:
        bench = Bench(config_file=args.config)
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
            print(f"Response: {result['response'][:200]}...")
            
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
            print(f"\n📋 Running test suite from {args.suite}...")
        try:
            results = bench.run_test_suite(args.suite, test_filter=args.test_name, default_model=args.model)
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
    
    # Default to tests.yaml if no specific command provided
    else:
        default_suite = "tests.yaml"
        if os.path.exists(default_suite):
            print(f"\n📋 No command specified, running default test suite: {default_suite}...")
            try:
                results = bench.run_test_suite(default_suite, test_filter=args.test_name, default_model=args.model)
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
    
    # Save results
    if args.output:
        bench.save_results(args.output)
    elif bench.config.get('save_results', True):
        bench.save_results()


if __name__ == '__main__':
    main()
