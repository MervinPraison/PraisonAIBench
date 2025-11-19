"""
Tests for Simple Evaluator

Following TDD principles:
1. Write tests first
2. Run tests (they should fail)
3. Implement features
4. Run tests (they should pass)
5. Refactor
"""

import pytest
import os
import json
from pathlib import Path


class TestSimpleEvaluator:
    """Test the SimpleEvaluator class"""
    
    @pytest.fixture
    def simple_html(self):
        """Simple valid HTML for testing"""
        return """<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
</head>
<body>
    <h1>Hello World</h1>
    <canvas id="myCanvas"></canvas>
    <script>
        console.log('Page loaded');
    </script>
</body>
</html>"""
    
    @pytest.fixture
    def html_with_errors(self):
        """HTML that will produce console errors"""
        return """<!DOCTYPE html>
<html>
<head>
    <title>Error Test</title>
</head>
<body>
    <h1>Test</h1>
    <script>
        // This will cause an error
        undefinedFunction();
        console.error('Test error');
    </script>
</body>
</html>"""
    
    @pytest.fixture
    def evaluator(self):
        """Create evaluator instance"""
        try:
            from praisonaibench.simple_evaluator import SimpleEvaluator
            return SimpleEvaluator(headless=True)
        except ImportError:
            pytest.skip("SimpleEvaluator not available")
    
    def test_evaluator_initialization(self, evaluator):
        """Test that evaluator initializes correctly"""
        assert evaluator is not None
        assert evaluator.headless == True
    
    def test_evaluate_simple_html(self, evaluator, simple_html):
        """Test evaluation of simple valid HTML"""
        result = evaluator.evaluate(simple_html, "test_simple")
        
        # Check result structure
        assert 'score' in result
        assert 'passed' in result
        assert 'renders' in result
        assert 'errors' in result
        assert 'screenshot' in result
        assert 'render_time_ms' in result
        assert 'feedback' in result
        
        # Check values
        assert result['renders'] == True
        assert result['score'] > 0
        assert len(result['errors']) == 0
        assert result['screenshot'] is not None
    
    def test_evaluate_html_with_errors(self, evaluator, html_with_errors):
        """Test evaluation of HTML with console errors"""
        result = evaluator.evaluate(html_with_errors, "test_errors")
        
        # Should still render
        assert result['renders'] == True
        
        # But should have errors
        assert len(result['errors']) > 0
        
        # Score should be lower
        assert result['score'] < 100
    
    def test_scoring_system(self, evaluator, simple_html):
        """Test that scoring system works correctly"""
        result = evaluator.evaluate(simple_html, "test_scoring")
        
        # Valid HTML with no errors should score high
        assert result['score'] >= 70
        assert result['passed'] == True
    
    def test_screenshot_creation(self, evaluator, simple_html):
        """Test that screenshot is created"""
        result = evaluator.evaluate(simple_html, "test_screenshot")
        
        # Check screenshot path exists
        assert result['screenshot'] is not None
        screenshot_path = result['screenshot']
        
        # Screenshot file should exist
        assert os.path.exists(screenshot_path)
        
        # Clean up
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)
    
    def test_feedback_generation(self, evaluator, simple_html):
        """Test that feedback is generated"""
        result = evaluator.evaluate(simple_html, "test_feedback")
        
        # Should have feedback
        assert len(result['feedback']) > 0
        
        # Feedback should have structure
        for item in result['feedback']:
            assert 'level' in item
            assert 'message' in item
            assert item['level'] in ['success', 'warning', 'error']


class TestLLMJudge:
    """Test the LLMJudge class"""
    
    @pytest.fixture
    def llm_judge(self):
        """Create LLM judge instance"""
        try:
            from praisonaibench.simple_evaluator import LLMJudge
            return LLMJudge(model="gpt-4o")
        except ImportError:
            pytest.skip("LLMJudge not available")
    
    @pytest.fixture
    def simple_html(self):
        """Simple HTML for testing"""
        return """<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body><h1>Hello</h1></body>
</html>"""
    
    def test_llm_judge_initialization(self, llm_judge):
        """Test LLM judge initializes correctly"""
        assert llm_judge is not None
        assert llm_judge.model == "gpt-4o"
    
    def test_llm_judge_evaluate_structure(self, llm_judge, simple_html):
        """Test LLM judge returns correct structure"""
        result = llm_judge.evaluate(simple_html, "Create a simple HTML page")
        
        # Check structure
        assert 'quality_score' in result
        assert 'feedback' in result
        
        # Score should be 0-100
        assert 0 <= result['quality_score'] <= 100


class TestCombinedEvaluator:
    """Test the CombinedEvaluator class"""
    
    @pytest.fixture
    def combined_evaluator(self):
        """Create combined evaluator instance"""
        try:
            from praisonaibench.simple_evaluator import CombinedEvaluator
            return CombinedEvaluator(use_llm_judge=False, headless=True)
        except ImportError:
            pytest.skip("CombinedEvaluator not available")
    
    @pytest.fixture
    def simple_html(self):
        """Simple HTML for testing"""
        return """<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body><h1>Hello</h1></body>
</html>"""
    
    def test_combined_evaluator_initialization(self, combined_evaluator):
        """Test combined evaluator initializes correctly"""
        assert combined_evaluator is not None
        assert combined_evaluator.functional is not None
    
    def test_combined_evaluate_structure(self, combined_evaluator, simple_html):
        """Test combined evaluator returns correct structure"""
        result = combined_evaluator.evaluate(
            simple_html, 
            "test_combined",
            "Create a simple HTML page"
        )
        
        # Check structure
        assert 'test_name' in result
        assert 'functional' in result
        assert 'quality' in result
        assert 'overall_score' in result
        assert 'passed' in result
        
        # Functional should have results
        assert result['functional']['score'] > 0
    
    def test_combined_evaluate_without_llm_judge(self, combined_evaluator, simple_html):
        """Test evaluation without LLM judge"""
        result = combined_evaluator.evaluate(simple_html, "test_no_judge", "")
        
        # Quality should be None (no LLM judge)
        assert result['quality'] is None
        
        # Overall score should equal functional score
        assert result['overall_score'] == result['functional']['score']


class TestBenchIntegration:
    """Test integration with Bench class"""
    
    @pytest.fixture
    def bench_with_eval(self):
        """Create Bench with evaluation enabled"""
        try:
            from praisonaibench import Bench
            return Bench(enable_evaluation=True)
        except ImportError:
            pytest.skip("Bench not available")
    
    @pytest.fixture
    def bench_without_eval(self):
        """Create Bench with evaluation disabled"""
        try:
            from praisonaibench import Bench
            return Bench(enable_evaluation=False)
        except ImportError:
            pytest.skip("Bench not available")
    
    def test_bench_with_evaluation_enabled(self, bench_with_eval):
        """Test Bench initializes with evaluation"""
        assert bench_with_eval.enable_evaluation == True
        # Evaluator might be None if playwright not installed
        # That's OK - it should fail gracefully
    
    def test_bench_with_evaluation_disabled(self, bench_without_eval):
        """Test Bench initializes without evaluation"""
        assert bench_without_eval.enable_evaluation == False
        assert bench_without_eval.evaluator is None


class TestEndToEnd:
    """End-to-end integration tests"""
    
    def test_full_evaluation_flow(self):
        """Test complete evaluation flow"""
        try:
            from praisonaibench.simple_evaluator import CombinedEvaluator
        except ImportError:
            pytest.skip("Evaluator not available")
        
        # Create evaluator
        evaluator = CombinedEvaluator(use_llm_judge=False, headless=True)
        
        # Simple HTML
        html = """<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
    <h1>Test Page</h1>
    <canvas id="test"></canvas>
</body>
</html>"""
        
        # Evaluate
        result = evaluator.evaluate(html, "e2e_test", "Create a test page")
        
        # Verify complete flow
        assert result['functional']['renders'] == True
        assert result['functional']['score'] > 0
        assert result['overall_score'] > 0
        assert result['passed'] in [True, False]
        
        # Clean up screenshot
        if result['functional']['screenshot'] and os.path.exists(result['functional']['screenshot']):
            os.remove(result['functional']['screenshot'])


# Pytest configuration
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
