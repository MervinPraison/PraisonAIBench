"""
Simple Example - Basic usage of PraisonAI Bench

This example shows how to use PraisonAI Bench for basic LLM benchmarking.
"""

from praisonaibench import Bench

def main():
    print("🚀 PraisonAI Bench - Simple Example")
    
    # Create benchmark suite
    bench = Bench()
    
    # Run a single test with math prompt
    print("\n1. Testing math calculation...")
    result = bench.run_single_test(
        prompt="What is 15 * 23? Show your work step by step.",
        test_name="math_test"
    )
    print(f"✅ Response: {result['response'][:100]}...")
    print(f"⏱️  Time: {result['execution_time']:.2f}s")
    
    # Run a test with creative prompt
    print("\n2. Testing creative writing...")
    result = bench.run_single_test(
        prompt="Write a short poem about artificial intelligence.",
        test_name="poetry_test"
    )
    print(f"✅ Response: {result['response'][:100]}...")
    print(f"⏱️  Time: {result['execution_time']:.2f}s")
    
    # Get summary of all tests
    print("\n3. Results Summary:")
    summary = bench.get_summary()
    for key, value in summary.items():
        print(f"   {key}: {value}")
    
    # Save results
    output_file = bench.save_results("simple_example_results.json")
    print(f"\n💾 Results saved to: {output_file}")

if __name__ == "__main__":
    main()
