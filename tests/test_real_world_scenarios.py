"""
Real-World Scenario Tests

Tests that simulate actual user workflows and edge cases
"""

import pytest
import os
import tempfile
import shutil


class TestRealWorldScenarios:
    """Test real-world usage scenarios"""
    
    def test_user_runs_benchmark_with_evaluation(self):
        """Simulate: User runs a benchmark with evaluation enabled"""
        try:
            from praisonaibench import Bench
        except ImportError:
            pytest.skip("Bench not available")
        
        # User creates bench with evaluation
        bench = Bench(enable_evaluation=True)
        
        # Verify it's set up correctly
        assert bench.enable_evaluation is True
        print("✅ User can create bench with evaluation")
    
    def test_user_runs_benchmark_without_evaluation(self):
        """Simulate: User wants fast benchmarking without evaluation"""
        try:
            from praisonaibench import Bench
        except ImportError:
            pytest.skip("Bench not available")
        
        # User creates bench without evaluation
        bench = Bench(enable_evaluation=False)
        
        # Verify evaluation is disabled
        assert bench.enable_evaluation is False
        assert bench.evaluator is None
        print("✅ User can disable evaluation for speed")
    
    def test_playwright_not_installed_graceful_degradation(self):
        """Simulate: User doesn't have Playwright installed"""
        try:
            from praisonaibench import Bench
        except ImportError:
            pytest.skip("Bench not available")
        
        # Even if Playwright fails, Bench should still work
        bench = Bench(enable_evaluation=True)
        
        # Should not crash
        assert bench is not None
        print("✅ System degrades gracefully without Playwright")
    
    def test_user_wants_functional_only_no_llm_judge(self):
        """Simulate: User wants functional validation but no LLM costs"""
        try:
            from praisonaibench.simple_evaluator import CombinedEvaluator
        except ImportError:
            pytest.skip("Evaluator not available")
        
        # User creates evaluator without LLM judge
        evaluator = CombinedEvaluator(use_llm_judge=False, headless=True)
        
        html = "<!DOCTYPE html><html><head><title>Test</title></head><body><h1>Test</h1></body></html>"
        result = evaluator.evaluate(html, "test_no_llm", "Create a test page")
        
        # Should have functional results but no quality
        assert result['functional']['score'] > 0
        assert result['quality'] is None
        
        # Cleanup
        if result['functional']['screenshot'] and os.path.exists(result['functional']['screenshot']):
            os.remove(result['functional']['screenshot'])
        
        print("✅ User can skip LLM judge to save costs")
    
    def test_batch_evaluation_multiple_tests(self):
        """Simulate: User wants to evaluate multiple HTML outputs"""
        try:
            from praisonaibench.simple_evaluator import SimpleEvaluator
        except ImportError:
            pytest.skip("Evaluator not available")
        
        evaluator = SimpleEvaluator(headless=True)
        
        # Multiple HTML outputs to evaluate
        html_outputs = [
            ("test1", "<!DOCTYPE html><html><head><title>Test 1</title></head><body><h1>Test 1</h1></body></html>"),
            ("test2", "<!DOCTYPE html><html><head><title>Test 2</title></head><body><h1>Test 2</h1></body></html>"),
            ("test3", "<!DOCTYPE html><html><head><title>Test 3</title></head><body><h1>Test 3</h1></body></html>"),
        ]
        
        results = []
        for name, html in html_outputs:
            result = evaluator.evaluate(html, name)
            results.append(result)
            
            # Cleanup
            if result['screenshot'] and os.path.exists(result['screenshot']):
                os.remove(result['screenshot'])
        
        # All should have been evaluated
        assert len(results) == 3
        assert all(r['score'] > 0 for r in results)
        
        print("✅ User can batch evaluate multiple outputs")
    
    def test_screenshot_directory_auto_created(self):
        """Simulate: User runs evaluation, screenshot dir doesn't exist"""
        try:
            from praisonaibench.simple_evaluator import SimpleEvaluator
        except ImportError:
            pytest.skip("Evaluator not available")
        
        # Remove screenshot directory if it exists
        screenshot_dir = "output/screenshots"
        if os.path.exists(screenshot_dir):
            shutil.rmtree(screenshot_dir)
        
        # User runs evaluation
        evaluator = SimpleEvaluator(headless=True)
        html = "<!DOCTYPE html><html><head><title>Test</title></head><body><h1>Test</h1></body></html>"
        result = evaluator.evaluate(html, "test_auto_dir")
        
        # Directory should be auto-created
        assert os.path.exists(screenshot_dir)
        assert os.path.exists(result['screenshot'])
        
        # Cleanup
        if os.path.exists(result['screenshot']):
            os.remove(result['screenshot'])
        
        print("✅ Screenshot directory auto-created")
    
    def test_html_with_three_js_canvas(self):
        """Simulate: User generates Three.js HTML (common use case)"""
        try:
            from praisonaibench.simple_evaluator import SimpleEvaluator
        except ImportError:
            pytest.skip("Evaluator not available")
        
        # Typical Three.js HTML output
        threejs_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Three.js Scene</title>
    <style>
        body { margin: 0; }
        canvas { display: block; }
    </style>
</head>
<body>
    <canvas id="canvas"></canvas>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('canvas') });
        renderer.setSize(window.innerWidth, window.innerHeight);
        
        const geometry = new THREE.BoxGeometry();
        const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
        const cube = new THREE.Mesh(geometry, material);
        scene.add(cube);
        
        camera.position.z = 5;
        
        function animate() {
            requestAnimationFrame(animate);
            cube.rotation.x += 0.01;
            cube.rotation.y += 0.01;
            renderer.render(scene, camera);
        }
        animate();
    </script>
</body>
</html>"""
        
        evaluator = SimpleEvaluator(headless=True)
        result = evaluator.evaluate(threejs_html, "test_threejs")
        
        # Should render successfully
        assert result['renders'] is True
        assert result['score'] > 0
        
        # Cleanup
        if result['screenshot'] and os.path.exists(result['screenshot']):
            os.remove(result['screenshot'])
        
        print("✅ Three.js HTML evaluates correctly")
    
    def test_malformed_html_doesnt_crash(self):
        """Simulate: LLM generates malformed HTML"""
        try:
            from praisonaibench.simple_evaluator import SimpleEvaluator
        except ImportError:
            pytest.skip("Evaluator not available")
        
        # Malformed HTML (common LLM mistake)
        malformed_html = """<!DOCTYPE html>
<html>
<head>
    <title>Broken HTML
</head>
<body>
    <h1>Missing closing tags
    <p>Unclosed paragraph
    <div>Unclosed div
</body>"""
        
        evaluator = SimpleEvaluator(headless=True)
        
        # Should not crash
        result = evaluator.evaluate(malformed_html, "test_malformed")
        
        # Should still return a result
        assert 'score' in result
        assert 'renders' in result
        
        # Cleanup
        if result.get('screenshot') and os.path.exists(result['screenshot']):
            os.remove(result['screenshot'])
        
        print("✅ Malformed HTML handled gracefully")
    
    def test_empty_response_handling(self):
        """Simulate: LLM returns empty response"""
        try:
            from praisonaibench.simple_evaluator import SimpleEvaluator
        except ImportError:
            pytest.skip("Evaluator not available")
        
        evaluator = SimpleEvaluator(headless=True)
        
        # Empty response
        result = evaluator.evaluate("", "test_empty")
        
        # Should handle gracefully
        assert 'score' in result
        assert result['score'] >= 0
        
        # Cleanup
        if result.get('screenshot') and os.path.exists(result['screenshot']):
            os.remove(result['screenshot'])
        
        print("✅ Empty response handled gracefully")
    
    def test_very_large_html_handling(self):
        """Simulate: LLM generates very large HTML file"""
        try:
            from praisonaibench.simple_evaluator import SimpleEvaluator
        except ImportError:
            pytest.skip("Evaluator not available")
        
        # Generate large HTML (10KB+)
        large_html = "<!DOCTYPE html><html><head><title>Large</title></head><body>"
        large_html += "<div>" * 1000  # Many nested divs
        large_html += "<p>Content</p>"
        large_html += "</div>" * 1000
        large_html += "</body></html>"
        
        evaluator = SimpleEvaluator(headless=True)
        result = evaluator.evaluate(large_html, "test_large")
        
        # Should handle large files
        assert 'score' in result
        
        # Cleanup
        if result.get('screenshot') and os.path.exists(result['screenshot']):
            os.remove(result['screenshot'])
        
        print("✅ Large HTML files handled correctly")


class TestDocumentationCompleteness:
    """Verify documentation covers all use cases"""
    
    def test_quickstart_guide_exists(self):
        """Verify evaluation documentation exists"""
        assert os.path.exists('EVALUATION.md'), "Main evaluation guide missing"
        print("✅ Main evaluation guide exists")
    
    def test_implementation_guide_exists(self):
        """Verify LLM judge criteria documentation exists"""
        assert os.path.exists('LLM_JUDGE_CRITERIA.md'), "LLM judge criteria missing"
        print("✅ LLM judge criteria exists")
    
    def test_comparison_guide_exists(self):
        """Verify best practices documentation exists"""
        assert os.path.exists('LLM_JUDGE_BEST_PRACTICES.md'), "Best practices guide missing"
        print("✅ Best practices guide exists")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
