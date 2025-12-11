"""
Test script to verify plugin system implementation.

This tests:
1. Plugin manager initialization
2. HTML evaluator (backwards compatibility)
3. Language detection
"""

from src.praisonaibench import Bench, PluginManager, BaseEvaluator


def test_plugin_manager():
    """Test plugin manager initialization"""
    print("=" * 60)
    print("TEST 1: Plugin Manager Initialization")
    print("=" * 60)
    
    pm = PluginManager()
    languages = pm.list_languages()
    
    print(f"✅ Plugin manager initialized")
    print(f"✅ Supported languages: {', '.join(languages)}")
    
    assert 'html' in languages, "HTML evaluator should be available"
    assert 'javascript' in languages, "JavaScript alias should be available"
    assert 'js' in languages, "JS alias should be available"
    
    print("✅ All built-in evaluators loaded\n")


def test_html_evaluator():
    """Test HTML evaluator (backwards compatibility)"""
    print("=" * 60)
    print("TEST 2: HTML Evaluator (Backwards Compatibility)")
    print("=" * 60)
    
    pm = PluginManager()
    html_eval = pm.get_evaluator('html')
    
    assert html_eval is not None, "HTML evaluator should be available"
    assert isinstance(html_eval, BaseEvaluator), "Should inherit BaseEvaluator"
    assert html_eval.get_language() == 'html', "Should return 'html'"
    
    print("✅ HTML evaluator loaded")
    print(f"✅ Language: {html_eval.get_language()}")
    print(f"✅ Extension: .{html_eval.get_file_extension()}\n")


def test_language_detection():
    """Test language detection"""
    print("=" * 60)
    print("TEST 3: Language Detection")
    print("=" * 60)
    
    bench = Bench(enable_evaluation=False)  # Disable eval for quick test
    
    # Test 1: Python code block
    python_response = "```python\nprint('hello')\n```"
    lang = bench._detect_language(python_response)
    assert lang == 'python', f"Expected 'python', got '{lang}'"
    print(f"✅ Python detection: {lang}")
    
    # Test 2: HTML content
    html_response = "<!DOCTYPE html><html><body>Hello</body></html>"
    lang = bench._detect_language(html_response)
    assert lang == 'html', f"Expected 'html', got '{lang}'"
    print(f"✅ HTML detection: {lang}")
    
    # Test 3: TypeScript code block
    ts_response = "```typescript\nconst x: number = 5;\n```"
    lang = bench._detect_language(ts_response)
    assert lang == 'typescript', f"Expected 'typescript', got '{lang}'"
    print(f"✅ TypeScript detection: {lang}")
    
    # Test 4: Explicit language in config
    lang = bench._detect_language("any content", {'language': 'rust'})
    assert lang == 'rust', f"Expected 'rust', got '{lang}'"
    print(f"✅ Explicit config: {lang}")
    
    print("\n")


def test_bench_initialization():
    """Test Bench initialization with plugin manager"""
    print("=" * 60)
    print("TEST 4: Bench Initialization with Plugin Manager")
    print("=" * 60)
    
    bench = Bench()
    
    assert bench.plugin_manager is not None, "Plugin manager should be initialized"
    
    languages = bench.plugin_manager.list_languages()
    print(f"✅ Bench initialized with plugin manager")
    print(f"✅ Available evaluators: {', '.join(languages)}\n")


def main():
    """Run all tests"""
    print("\n🧪 Testing Plugin System Implementation\n")
    
    try:
        test_plugin_manager()
        test_html_evaluator()
        test_language_detection()
        test_bench_initialization()
        
        print("=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print("\n✅ Plugin system is working correctly!")
        print("✅ HTML evaluation (backwards compatible)")
        print("✅ Plugin discovery ready")
        print("✅ Language detection working")
        print("\n📝 Next steps:")
        print("  1. Create plugins using examples/plugins/python_evaluator.py")
        print("  2. Install plugins with: pip install -e .")
        print("  3. Run tests with: praisonaibench --suite tests.yaml")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
