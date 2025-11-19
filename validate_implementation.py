#!/usr/bin/env python
"""
Validation Script for PraisonAI Bench Evaluation System

Checks that all components are properly implemented and working.
"""

import sys
import os

def check_files_exist():
    """Check that all required files exist"""
    print("📁 Checking files...")
    
    required_files = [
        'src/praisonaibench/simple_evaluator.py',
        'src/praisonaibench/bench.py',
        'src/praisonaibench/cli.py',
        'src/praisonaibench/agent.py',
        'tests/test_simple_evaluator.py',
        'tests/test_integration.py',
        'EVALUATION_SIMPLIFIED.md',
        'EVALUATION_COMPARISON.md',
        'QUICKSTART_EVALUATION.md',
        'IMPLEMENTATION_COMPLETE.md',
        'TEST_RESULTS.md',
    ]
    
    missing = []
    for file in required_files:
        if not os.path.exists(file):
            missing.append(file)
            print(f"  ❌ Missing: {file}")
        else:
            print(f"  ✅ Found: {file}")
    
    if missing:
        print(f"\n❌ {len(missing)} files missing!")
        return False
    
    print(f"\n✅ All {len(required_files)} required files exist!")
    return True


def check_imports():
    """Check that all modules can be imported"""
    print("\n📦 Checking imports...")
    
    try:
        from praisonaibench.simple_evaluator import SimpleEvaluator, LLMJudge, CombinedEvaluator
        print("  ✅ simple_evaluator imports successfully")
    except ImportError as e:
        print(f"  ❌ simple_evaluator import failed: {e}")
        return False
    
    try:
        from praisonaibench import Bench
        print("  ✅ Bench imports successfully")
    except ImportError as e:
        print(f"  ❌ Bench import failed: {e}")
        return False
    
    try:
        from praisonaibench.agent import BenchAgent
        print("  ✅ BenchAgent imports successfully")
    except ImportError as e:
        print(f"  ❌ BenchAgent import failed: {e}")
        return False
    
    print("\n✅ All imports successful!")
    return True


def check_evaluator_functionality():
    """Check that evaluator works"""
    print("\n🧪 Checking evaluator functionality...")
    
    try:
        from praisonaibench.simple_evaluator import SimpleEvaluator
        
        evaluator = SimpleEvaluator(headless=True)
        html = "<!DOCTYPE html><html><head><title>Test</title></head><body><h1>Test</h1></body></html>"
        result = evaluator.evaluate(html, "validation_test")
        
        # Check result structure
        assert 'score' in result, "Missing 'score' in result"
        assert 'passed' in result, "Missing 'passed' in result"
        assert 'renders' in result, "Missing 'renders' in result"
        assert 'screenshot' in result, "Missing 'screenshot' in result"
        
        # Cleanup
        if result['screenshot'] and os.path.exists(result['screenshot']):
            os.remove(result['screenshot'])
        
        print("  ✅ Evaluator works correctly")
        return True
        
    except Exception as e:
        print(f"  ❌ Evaluator check failed: {e}")
        return False


def check_bench_integration():
    """Check that Bench integrates with evaluator"""
    print("\n🔧 Checking Bench integration...")
    
    try:
        from praisonaibench import Bench
        
        # Test with evaluation enabled
        bench_with_eval = Bench(enable_evaluation=True)
        assert bench_with_eval.enable_evaluation is True
        print("  ✅ Bench with evaluation enabled works")
        
        # Test with evaluation disabled
        bench_without_eval = Bench(enable_evaluation=False)
        assert bench_without_eval.enable_evaluation is False
        assert bench_without_eval.evaluator is None
        print("  ✅ Bench with evaluation disabled works")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Bench integration check failed: {e}")
        return False


def check_cli_flags():
    """Check that CLI has evaluation flags"""
    print("\n⚙️  Checking CLI flags...")
    
    try:
        import subprocess
        result = subprocess.run(
            ['python', '-m', 'praisonaibench.cli', '--help'],
            capture_output=True,
            text=True,
            cwd='src'
        )
        
        if '--no-eval' in result.stdout:
            print("  ✅ --no-eval flag present")
        else:
            print("  ❌ --no-eval flag missing")
            return False
        
        if '--no-llm-judge' in result.stdout:
            print("  ✅ --no-llm-judge flag present")
        else:
            print("  ❌ --no-llm-judge flag missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ CLI check failed: {e}")
        return False


def run_tests():
    """Run the test suite"""
    print("\n🧪 Running test suite...")
    
    try:
        import subprocess
        result = subprocess.run(
            ['python', '-m', 'pytest', 'tests/', '-v', '--tb=short'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Count passed tests
            import re
            match = re.search(r'(\d+) passed', result.stdout)
            if match:
                count = match.group(1)
                print(f"  ✅ All {count} tests passed!")
                return True
        else:
            print(f"  ❌ Tests failed!")
            print(result.stdout[-500:])  # Show last 500 chars
            return False
            
    except Exception as e:
        print(f"  ❌ Test execution failed: {e}")
        return False


def main():
    """Run all validation checks"""
    print("=" * 60)
    print("PraisonAI Bench Evaluation System - Validation")
    print("=" * 60)
    
    checks = [
        ("Files Exist", check_files_exist),
        ("Imports Work", check_imports),
        ("Evaluator Functions", check_evaluator_functionality),
        ("Bench Integration", check_bench_integration),
        ("CLI Flags", check_cli_flags),
        ("Test Suite", run_tests),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} check crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print(f"\n{passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 ALL VALIDATION CHECKS PASSED!")
        print("✅ The evaluation system is production-ready!")
        return 0
    else:
        print(f"\n❌ {total - passed} checks failed")
        print("⚠️  Please fix the issues above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
