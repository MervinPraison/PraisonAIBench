"""
Integration Tests for PraisonAI Bench Evaluation System

Tests the complete workflow from CLI to evaluation output
"""

import pytest
import os
import json
import tempfile
import shutil
from pathlib import Path


class TestCLIIntegration:
    """Test CLI integration with evaluation system"""
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_test_yaml(self, temp_output_dir):
        """Create a sample test YAML file"""
        yaml_content = """
tests:
  - name: "simple_html_test"
    prompt: "Create a simple HTML page with a heading that says 'Test Page'"

config:
  max_tokens: 1000
"""
        yaml_path = os.path.join(temp_output_dir, "test.yaml")
        with open(yaml_path, 'w') as f:
            f.write(yaml_content)
        return yaml_path
    
    def test_cli_help_shows_eval_flags(self):
        """Test that CLI help shows evaluation flags"""
        import subprocess
        result = subprocess.run(
            ['python', '-m', 'praisonaibench.cli', '--help'],
            capture_output=True,
            text=True,
            cwd='src'
        )
        
        assert result.returncode == 0
        assert '--no-eval' in result.stdout
        assert '--no-llm-judge' in result.stdout
    
    def test_bench_initialization_with_eval(self):
        """Test Bench initializes with evaluation enabled"""
        try:
            from praisonaibench import Bench
        except ImportError:
            pytest.skip("Bench not available")
        
        bench = Bench(enable_evaluation=True)
        assert bench.enable_evaluation is True
    
    def test_bench_initialization_without_eval(self):
        """Test Bench initializes with evaluation disabled"""
        try:
            from praisonaibench import Bench
        except ImportError:
            pytest.skip("Bench not available")
        
        bench = Bench(enable_evaluation=False)
        assert bench.enable_evaluation is False
        assert bench.plugin_manager is None


class TestEvaluationWorkflow:
    """Test complete evaluation workflow"""
    
    @pytest.fixture
    def simple_html_response(self):
        """Sample HTML response from LLM"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Test Page</title>
</head>
<body>
    <h1>Test Page</h1>
    <p>This is a test page.</p>
</body>
</html>"""
    
    def test_evaluation_result_structure(self, simple_html_response):
        """Test that evaluation returns correct structure"""
        try:
            from praisonaibench.simple_evaluator import CombinedEvaluator
        except ImportError:
            pytest.skip("Evaluator not available")
        
        evaluator = CombinedEvaluator(use_llm_judge=False, headless=True)
        result = evaluator.evaluate(
            simple_html_response,
            "test_structure",
            "Create a simple HTML page"
        )
        
        # Verify complete structure
        assert 'test_name' in result
        assert 'functional' in result
        assert 'quality' in result
        assert 'overall_score' in result
        assert 'passed' in result
        
        # Verify functional results
        functional = result['functional']
        assert 'score' in functional
        assert 'renders' in functional
        assert 'errors' in functional
        assert 'screenshot' in functional
        assert 'feedback' in functional
        
        # Cleanup
        if functional['screenshot'] and os.path.exists(functional['screenshot']):
            os.remove(functional['screenshot'])
    
    def test_evaluation_scoring_logic(self, simple_html_response):
        """Test that scoring logic works correctly"""
        try:
            from praisonaibench.simple_evaluator import SimpleEvaluator
        except ImportError:
            pytest.skip("Evaluator not available")
        
        evaluator = SimpleEvaluator(headless=True)
        result = evaluator.evaluate(simple_html_response, "test_scoring")
        
        # Valid HTML should score well
        assert result['score'] >= 70
        assert result['passed'] is True
        assert result['renders'] is True
        assert len(result['errors']) == 0
        
        # Cleanup
        if result['screenshot'] and os.path.exists(result['screenshot']):
            os.remove(result['screenshot'])


class TestOutputGeneration:
    """Test output file generation"""
    
    def test_screenshot_directory_creation(self):
        """Test that screenshot directory is created"""
        try:
            from praisonaibench.simple_evaluator import SimpleEvaluator
        except ImportError:
            pytest.skip("Evaluator not available")
        
        # Remove screenshot dir if exists
        screenshot_dir = "output/screenshots"
        if os.path.exists(screenshot_dir):
            shutil.rmtree(screenshot_dir)
        
        evaluator = SimpleEvaluator(headless=True)
        html = "<!DOCTYPE html><html><head><title>Test</title></head><body><h1>Test</h1></body></html>"
        result = evaluator.evaluate(html, "test_dir_creation")
        
        # Directory should be created
        assert os.path.exists(screenshot_dir)
        
        # Screenshot should exist
        assert result['screenshot'] is not None
        assert os.path.exists(result['screenshot'])
        
        # Cleanup
        if os.path.exists(result['screenshot']):
            os.remove(result['screenshot'])
    
    def test_screenshot_file_format(self):
        """Test that screenshot is PNG format"""
        try:
            from praisonaibench.simple_evaluator import SimpleEvaluator
        except ImportError:
            pytest.skip("Evaluator not available")
        
        evaluator = SimpleEvaluator(headless=True)
        html = "<!DOCTYPE html><html><head><title>Test</title></head><body><h1>Test</h1></body></html>"
        result = evaluator.evaluate(html, "test_png_format")
        
        # Should be PNG file
        assert result['screenshot'].endswith('.png')
        assert os.path.exists(result['screenshot'])
        
        # Check file is not empty
        file_size = os.path.getsize(result['screenshot'])
        assert file_size > 0
        
        # Cleanup
        if os.path.exists(result['screenshot']):
            os.remove(result['screenshot'])


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_html_handling(self):
        """Test handling of invalid HTML"""
        try:
            from praisonaibench.simple_evaluator import SimpleEvaluator
        except ImportError:
            pytest.skip("Evaluator not available")
        
        evaluator = SimpleEvaluator(headless=True)
        invalid_html = "<html><head><title>Broken"  # Unclosed tags
        
        result = evaluator.evaluate(invalid_html, "test_invalid")
        
        # Should still attempt to evaluate
        assert 'score' in result
        assert 'renders' in result
        
        # Cleanup
        if result.get('screenshot') and os.path.exists(result['screenshot']):
            os.remove(result['screenshot'])
    
    def test_empty_html_handling(self):
        """Test handling of empty HTML"""
        try:
            from praisonaibench.simple_evaluator import SimpleEvaluator
        except ImportError:
            pytest.skip("Evaluator not available")
        
        evaluator = SimpleEvaluator(headless=True)
        empty_html = ""
        
        result = evaluator.evaluate(empty_html, "test_empty")
        
        # Should handle gracefully
        assert 'score' in result
        assert result['score'] >= 0
        
        # Cleanup
        if result.get('screenshot') and os.path.exists(result['screenshot']):
            os.remove(result['screenshot'])
    
    def test_javascript_error_detection(self):
        """Test that JavaScript errors are detected"""
        try:
            from praisonaibench.simple_evaluator import SimpleEvaluator
        except ImportError:
            pytest.skip("Evaluator not available")
        
        evaluator = SimpleEvaluator(headless=True)
        html_with_error = """<!DOCTYPE html>
<html>
<head><title>Error Test</title></head>
<body>
    <h1>Test</h1>
    <script>
        // This will cause an error
        nonExistentFunction();
    </script>
</body>
</html>"""
        
        result = evaluator.evaluate(html_with_error, "test_js_error")
        
        # Should detect errors
        assert len(result['errors']) > 0
        assert result['score'] < 100  # Score should be reduced
        
        # Cleanup
        if result.get('screenshot') and os.path.exists(result['screenshot']):
            os.remove(result['screenshot'])


class TestPerformance:
    """Test performance characteristics"""
    
    def test_evaluation_completes_quickly(self):
        """Test that evaluation completes in reasonable time"""
        import time
        
        try:
            from praisonaibench.simple_evaluator import SimpleEvaluator
        except ImportError:
            pytest.skip("Evaluator not available")
        
        evaluator = SimpleEvaluator(headless=True)
        html = "<!DOCTYPE html><html><head><title>Test</title></head><body><h1>Test</h1></body></html>"
        
        start = time.time()
        result = evaluator.evaluate(html, "test_performance")
        duration = time.time() - start
        
        # Should complete in under 10 seconds
        assert duration < 10.0
        
        # Cleanup
        if result.get('screenshot') and os.path.exists(result['screenshot']):
            os.remove(result['screenshot'])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
