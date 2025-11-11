"""
Demonstration of PraisonAI Bench Automated Evaluation System

This script shows how to use the evaluation features including:
- Expected result comparison
- HTML code validation
- Quality scoring
- Custom evaluation metrics
"""

from praisonaibench import Bench

def main():
    print("=" * 60)
    print("PraisonAI Bench - Evaluation Demo")
    print("=" * 60)
    
    # Initialize bench with evaluation enabled (default)
    bench = Bench(enable_evaluation=True)
    print("\n✅ Evaluation system enabled\n")
    
    # Example 1: Simple math test with expected result
    print("🧪 Test 1: Math with Expected Result")
    print("-" * 60)
    result = bench.run_single_test(
        prompt="What is 25 * 4?",
        test_name="simple_math",
        test_config={"expected": "100"}
    )
    
    if 'evaluation' in result:
        eval_data = result['evaluation']
        print(f"Response: {result['response']}")
        print(f"Overall Score: {eval_data['overall_score']}%")
        print(f"Passed: {'✅' if eval_data['overall_passed'] else '❌'}")
    
    print("\n" + "=" * 60 + "\n")
    
    # Example 2: HTML generation with automatic validation
    print("🧪 Test 2: HTML Generation with Validation")
    print("-" * 60)
    result = bench.run_single_test(
        prompt="""Create a simple HTML page with:
        - Proper DOCTYPE
        - A title "Test Page"
        - A heading "Hello World"
        - A paragraph with some text
        - Include meta charset UTF-8""",
        test_name="html_generation"
    )
    
    if 'evaluation' in result:
        eval_data = result['evaluation']
        print(f"Overall Score: {eval_data['overall_score']}%")
        print(f"HTML Validation: {'✅ PASSED' if eval_data['overall_passed'] else '❌ FAILED'}")
        
        # Show HTML-specific scores
        if 'html_code' in eval_data['evaluations']:
            html_eval = eval_data['evaluations']['html_code']
            if 'scores' in html_eval:
                print("\nDetailed HTML Scores:")
                for score_name, score_data in html_eval['scores'].items():
                    print(f"  - {score_name}: {score_data['percentage']:.1f}%")
    
    print("\n" + "=" * 60 + "\n")
    
    # Example 3: Comparison test with and without evaluation
    print("🧪 Test 3: Performance Comparison")
    print("-" * 60)
    
    import time
    
    # With evaluation
    start = time.time()
    bench_with_eval = Bench(enable_evaluation=True)
    result_with_eval = bench_with_eval.run_single_test(
        "Explain Python in one sentence",
        test_name="python_explanation_with_eval"
    )
    time_with_eval = time.time() - start
    
    # Without evaluation
    start = time.time()
    bench_no_eval = Bench(enable_evaluation=False)
    result_no_eval = bench_no_eval.run_single_test(
        "Explain Python in one sentence",
        test_name="python_explanation_no_eval"
    )
    time_no_eval = time.time() - start
    
    print(f"Time with evaluation: {time_with_eval:.2f}s")
    print(f"Time without evaluation: {time_no_eval:.2f}s")
    print(f"Overhead: {(time_with_eval - time_no_eval):.2f}s")
    
    print("\n" + "=" * 60 + "\n")
    
    # Show final summary
    print("📊 Summary")
    print("-" * 60)
    summary = bench.get_summary()
    print(f"Total tests: {summary['total_tests']}")
    print(f"Success rate: {summary['success_rate']}")
    
    if 'evaluation' in summary:
        eval_summary = summary['evaluation']
        print(f"\nEvaluation Metrics:")
        print(f"  Average score: {eval_summary['average_score']}")
        print(f"  Pass rate: {eval_summary['pass_rate']}")
        print(f"  Passed: {eval_summary['passed_evaluations']}")
        print(f"  Failed: {eval_summary['failed_evaluations']}")
    
    # Save results
    filepath = bench.save_results("evaluation_demo_results.json")
    print(f"\n💾 Results saved to: {filepath}")
    
    print("\n" + "=" * 60)
    print("✅ Demo completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()

