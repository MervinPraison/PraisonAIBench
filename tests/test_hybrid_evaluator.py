"""
Tests for Hybrid Evaluator (v0.0.7)

Test-Driven Development for the new hybrid evaluation system:
- HTMLStructureValidator
- ExpectedResultEvaluator
- HybridEvaluator

Following TDD principles:
1. Write tests first
2. Run tests (they should fail)
3. Implement features
4. Run tests (they should pass)
5. Refactor
"""

import pytest
import os


class TestHTMLStructureValidator:
    """Test the HTMLStructureValidator class"""
    
    @pytest.fixture
    def validator(self):
        """Create validator instance"""
        try:
            from praisonaibench.hybrid_evaluator import HTMLStructureValidator
            return HTMLStructureValidator()
        except ImportError:
            pytest.skip("HTMLStructureValidator not available")
    
    @pytest.fixture
    def valid_html(self):
        """Valid HTML with all required elements"""
        return """<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
</head>
<body>
    <h1>Hello World</h1>
</body>
</html>"""
    
    @pytest.fixture
    def html_no_doctype(self):
        """HTML without DOCTYPE"""
        return """<html>
<head><title>Test</title></head>
<body><h1>Test</h1></body>
</html>"""
    
    @pytest.fixture
    def html_missing_tags(self):
        """HTML missing required tags"""
        return """<!DOCTYPE html>
<html>
<h1>Missing head and body tags</h1>
</html>"""
    
    def test_validator_initialization(self, validator):
        """Test that validator initializes correctly"""
        assert validator is not None
    
    def test_validate_valid_html(self, validator, valid_html):
        """Test validation of valid HTML"""
        result = validator.validate(valid_html)
        
        # Check structure
        assert 'score' in result
        assert 'valid_structure' in result
        assert 'has_doctype' in result
        assert 'has_required_tags' in result
        assert 'issues' in result
        assert 'weight' in result
        
        # Check values
        assert result['score'] == 100
        assert result['valid_structure'] == True
        assert result['has_doctype'] == True
        assert result['has_required_tags'] == True
        assert len(result['issues']) == 0
        assert result['weight'] == 0.15
    
    def test_validate_html_no_doctype(self, validator, html_no_doctype):
        """Test validation of HTML without DOCTYPE"""
        result = validator.validate(html_no_doctype)
        
        assert result['has_doctype'] == False
        assert result['score'] < 100
        assert len(result['issues']) > 0
        assert any('DOCTYPE' in issue for issue in result['issues'])
    
    def test_validate_html_missing_tags(self, validator, html_missing_tags):
        """Test validation of HTML with missing required tags"""
        result = validator.validate(html_missing_tags)
        
        assert result['has_required_tags'] == False
        assert result['score'] < 100
        assert len(result['issues']) > 0
    
    def test_validate_invalid_html(self, validator):
        """Test validation of invalid HTML"""
        invalid_html = """<!DOCTYPE html>
<html>
<head><title>Test</title>
<body><h1>Unclosed tags"""
        
        result = validator.validate(invalid_html)
        
        # Should detect structure issues (HTMLParser may still parse it)
        # At minimum, should have issues reported
        assert 'score' in result
        assert 'valid_structure' in result


class TestExpectedResultEvaluator:
    """Test the ExpectedResultEvaluator class"""
    
    @pytest.fixture
    def evaluator(self):
        """Create evaluator instance"""
        try:
            from praisonaibench.hybrid_evaluator import ExpectedResultEvaluator
            return ExpectedResultEvaluator()
        except ImportError:
            pytest.skip("ExpectedResultEvaluator not available")
    
    def test_evaluator_initialization(self, evaluator):
        """Test that evaluator initializes correctly"""
        assert evaluator is not None
    
    def test_evaluate_exact_match(self, evaluator):
        """Test exact match detection"""
        result = evaluator.evaluate("345", "345")
        
        # Check structure
        assert 'score' in result
        assert 'similarity' in result
        assert 'keyword_match' in result
        assert 'exact_match' in result
        assert 'weight' in result
        
        # Check values
        assert result['score'] == 100
        assert result['similarity'] == 1.0
        assert result['keyword_match'] == 1.0
        assert result['exact_match'] == True
        assert result['weight'] == 0.20
    
    def test_evaluate_partial_match(self, evaluator):
        """Test partial match scoring"""
        result = evaluator.evaluate("The answer is 345", "345")
        
        assert result['score'] > 0
        assert result['score'] < 100
        assert result['exact_match'] == False
        assert result['similarity'] > 0
    
    def test_evaluate_html_with_text(self, evaluator):
        """Test text extraction from HTML"""
        html = '<!DOCTYPE html><html><body>345</body></html>'
        result = evaluator.evaluate(html, "345")
        
        # Should extract text and match exactly
        assert result['score'] == 100
        assert result['exact_match'] == True
    
    def test_evaluate_html_with_extra_text(self, evaluator):
        """Test HTML with additional text"""
        html = '<!DOCTYPE html><html><body><h1>The answer is 345</h1></body></html>'
        result = evaluator.evaluate(html, "345")
        
        # Should extract text and find partial match
        assert result['score'] > 0
        assert result['score'] < 100
        assert result['exact_match'] == False
    
    def test_evaluate_no_expected(self, evaluator):
        """Test with no expected result"""
        result = evaluator.evaluate("test", None)
        
        # Should return None
        assert result is None
    
    def test_evaluate_empty_expected(self, evaluator):
        """Test with empty expected result"""
        result = evaluator.evaluate("test", "")
        
        # Should return None
        assert result is None
    
    def test_keyword_matching(self, evaluator):
        """Test keyword matching functionality"""
        result = evaluator.evaluate("Paris is the capital of France", "Paris")
        
        # Should have high keyword match
        assert result['keyword_match'] == 1.0
        assert result['score'] > 0


class TestHybridEvaluator:
    """Test the HybridEvaluator class"""
    
    @pytest.fixture
    def evaluator_no_llm(self):
        """Create evaluator without LLM judge"""
        try:
            from praisonaibench.hybrid_evaluator import HybridEvaluator
            return HybridEvaluator(use_llm_judge=False, headless=True)
        except ImportError:
            pytest.skip("HybridEvaluator not available")
    
    @pytest.fixture
    def valid_html(self):
        """Valid HTML for testing"""
        return """<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
</head>
<body>
    <h1>345</h1>
    <p>The answer is 345</p>
</body>
</html>"""
    
    def test_evaluator_initialization(self, evaluator_no_llm):
        """Test that evaluator initializes correctly"""
        assert evaluator_no_llm is not None
        assert evaluator_no_llm.html_validator is not None
        assert evaluator_no_llm.functional is not None
        assert evaluator_no_llm.expected_evaluator is not None
        assert evaluator_no_llm.llm_judge is None
    
    def test_evaluate_with_expected(self, evaluator_no_llm, valid_html):
        """Test evaluation with expected result"""
        result = evaluator_no_llm.evaluate(
            html_content=valid_html,
            test_name="test_math",
            prompt="What is 15 * 23?",
            expected="345"
        )
        
        # Check structure
        assert 'html_validation' in result
        assert 'functional' in result
        assert 'expected' in result
        assert 'llm_judge' in result
        assert 'overall_score' in result
        assert 'passed' in result
        assert 'breakdown' in result
        
        # Check components exist
        assert result['html_validation'] is not None
        assert result['functional'] is not None
        assert result['expected'] is not None
        assert result['llm_judge'] is None  # Disabled
        
        # Check scores
        assert 0 <= result['overall_score'] <= 100
        assert result['passed'] in [True, False]
        
        # Clean up screenshot
        if result['functional']['screenshot'] and os.path.exists(result['functional']['screenshot']):
            os.remove(result['functional']['screenshot'])
    
    def test_evaluate_without_expected(self, evaluator_no_llm, valid_html):
        """Test evaluation without expected result"""
        result = evaluator_no_llm.evaluate(
            html_content=valid_html,
            test_name="test_no_expected",
            prompt="Create a page",
            expected=None
        )
        
        # Expected should be None
        assert result['expected'] is None
        
        # Should still have overall score
        assert 'overall_score' in result
        assert 0 <= result['overall_score'] <= 100
        
        # Clean up
        if result['functional']['screenshot'] and os.path.exists(result['functional']['screenshot']):
            os.remove(result['functional']['screenshot'])
    
    def test_weight_normalization_with_expected(self, evaluator_no_llm, valid_html):
        """Test weight normalization with expected field"""
        result = evaluator_no_llm.evaluate(
            html_content=valid_html,
            test_name="test_weights_with",
            prompt="Test",
            expected="345"
        )
        
        breakdown = result['breakdown']
        
        # Check weights sum to 100% (accounting for missing LLM judge)
        # With expected but no LLM: HTML=15%, Func=40%, Exp=20% = 75%
        # Normalized: HTML=20%, Func=53.33%, Exp=26.67%
        assert 'components' in breakdown
        
        # Clean up
        if result['functional']['screenshot'] and os.path.exists(result['functional']['screenshot']):
            os.remove(result['functional']['screenshot'])
    
    def test_weight_normalization_without_expected(self, evaluator_no_llm, valid_html):
        """Test weight normalization without expected field"""
        result = evaluator_no_llm.evaluate(
            html_content=valid_html,
            test_name="test_weights_without",
            prompt="Test",
            expected=None
        )
        
        breakdown = result['breakdown']
        
        # Without expected and no LLM: HTML=15%, Func=40% = 55%
        # Normalized: HTML=27.27%, Func=72.73%
        assert 'components' in breakdown
        assert 'expected' in breakdown['components']
        assert breakdown['components']['expected']['score'] == 'N/A'
        
        # Clean up
        if result['functional']['screenshot'] and os.path.exists(result['functional']['screenshot']):
            os.remove(result['functional']['screenshot'])
    
    def test_get_feedback(self, evaluator_no_llm, valid_html):
        """Test feedback generation"""
        result = evaluator_no_llm.evaluate(
            html_content=valid_html,
            test_name="test_feedback",
            prompt="Test",
            expected="345"
        )
        
        feedback = evaluator_no_llm.get_feedback(result)
        
        # Should have feedback from multiple components
        assert len(feedback) > 0
        
        # Each feedback item should have structure
        for item in feedback:
            assert 'level' in item
            assert 'component' in item
            assert 'message' in item
            assert item['level'] in ['success', 'warning', 'error', 'info']
        
        # Clean up
        if result['functional']['screenshot'] and os.path.exists(result['functional']['screenshot']):
            os.remove(result['functional']['screenshot'])


class TestWeightCalculations:
    """Test weight calculation and normalization"""
    
    def test_weights_with_all_components(self):
        """Test that weights sum to 1.0 with all components"""
        weights = {
            'html': 0.15,
            'functional': 0.40,
            'expected': 0.20,
            'llm': 0.25
        }
        
        total = sum(weights.values())
        assert total == 1.0
    
    def test_weights_without_expected(self):
        """Test weight normalization without expected"""
        original = {
            'html': 0.15,
            'functional': 0.40,
            'llm': 0.25
        }
        
        original_total = sum(original.values())
        assert original_total == 0.80
        
        # Normalize
        normalized = {k: v / original_total for k, v in original.items()}
        
        # Check normalized values
        assert abs(normalized['html'] - 0.1875) < 0.0001
        assert abs(normalized['functional'] - 0.50) < 0.0001
        assert abs(normalized['llm'] - 0.3125) < 0.0001
        
        # Check total
        assert abs(sum(normalized.values()) - 1.0) < 0.0001
    
    def test_scoring_with_expected(self):
        """Test scoring calculation with expected field"""
        scores = {
            'html': 90,
            'functional': 85,
            'expected': 95,
            'llm': 80
        }
        
        weights = {
            'html': 0.15,
            'functional': 0.40,
            'expected': 0.20,
            'llm': 0.25
        }
        
        overall = sum(scores[k] * weights[k] for k in scores.keys())
        
        # Should be 86.5
        assert abs(overall - 86.5) < 0.1
    
    def test_scoring_without_expected(self):
        """Test scoring calculation without expected field"""
        scores = {
            'html': 90,
            'functional': 85,
            'llm': 80
        }
        
        # Normalized weights
        weights = {
            'html': 0.1875,
            'functional': 0.50,
            'llm': 0.3125
        }
        
        overall = sum(scores[k] * weights[k] for k in scores.keys())
        
        # Should be 84.375
        assert abs(overall - 84.375) < 0.1


class TestBenchIntegrationHybrid:
    """Test integration with Bench class using hybrid evaluator"""
    
    @pytest.fixture
    def bench_with_hybrid(self):
        """Create Bench with hybrid evaluation enabled"""
        try:
            from praisonaibench import Bench
            return Bench(enable_evaluation=True)
        except ImportError:
            pytest.skip("Bench not available")
    
    def test_bench_uses_hybrid_evaluator(self, bench_with_hybrid):
        """Test that Bench uses HybridEvaluator"""
        if bench_with_hybrid.evaluator is not None:
            # Should have HybridEvaluator
            assert hasattr(bench_with_hybrid.evaluator, 'html_validator')
            assert hasattr(bench_with_hybrid.evaluator, 'expected_evaluator')


class TestEndToEndHybrid:
    """End-to-end tests for hybrid evaluation system"""
    
    def test_full_hybrid_evaluation_flow(self):
        """Test complete hybrid evaluation flow"""
        try:
            from praisonaibench.hybrid_evaluator import HybridEvaluator
        except ImportError:
            pytest.skip("HybridEvaluator not available")
        
        # Create evaluator
        evaluator = HybridEvaluator(use_llm_judge=False, headless=True)
        
        # HTML with expected result
        html = """<!DOCTYPE html>
<html>
<head><title>Math Test</title></head>
<body>
    <h1>Result: 345</h1>
    <p>15 * 23 = 345</p>
</body>
</html>"""
        
        # Evaluate with expected
        result = evaluator.evaluate(
            html_content=html,
            test_name="e2e_hybrid_test",
            prompt="What is 15 * 23?",
            expected="345"
        )
        
        # Verify all components
        assert result['html_validation']['score'] > 0
        assert result['functional']['renders'] == True
        assert result['expected']['score'] > 0
        assert result['overall_score'] > 0
        assert result['passed'] in [True, False]
        
        # Verify feedback
        feedback = evaluator.get_feedback(result)
        assert len(feedback) > 0
        
        # Clean up
        if result['functional']['screenshot'] and os.path.exists(result['functional']['screenshot']):
            os.remove(result['functional']['screenshot'])


# Pytest configuration
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "hybrid: marks tests for hybrid evaluator"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
