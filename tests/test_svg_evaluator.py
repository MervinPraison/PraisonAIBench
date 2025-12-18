"""
Tests for SVG Evaluator

Test-Driven Development for the SVG evaluation system:
- SVGValidator
- SVGVisualEvaluator
- SVGSemanticEvaluator
- SVGCodeQualityEvaluator
- SVGEvaluator (main class)
"""

import pytest
import os


class TestSVGValidator:
    """Test the SVGValidator class"""

    @pytest.fixture
    def validator(self):
        """Create validator instance"""
        try:
            from praisonaibench.evaluators.svg_evaluator import SVGValidator
            return SVGValidator()
        except ImportError:
            pytest.skip("SVGValidator not available")

    @pytest.fixture
    def valid_svg(self):
        """Valid SVG with all required elements"""
        return '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">
    <rect x="10" y="10" width="80" height="80" fill="blue"/>
    <circle cx="50" cy="50" r="30" fill="red"/>
</svg>'''

    @pytest.fixture
    def svg_no_viewbox(self):
        """SVG without viewBox"""
        return '''<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
    <rect x="10" y="10" width="80" height="80" fill="blue"/>
</svg>'''

    @pytest.fixture
    def svg_in_markdown(self):
        """SVG wrapped in markdown code block"""
        return '''Here is the SVG:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
    <circle cx="50" cy="50" r="40" fill="green"/>
</svg>
```

This creates a green circle.'''

    def test_validator_initialization(self, validator):
        """Test that validator initializes correctly"""
        assert validator is not None

    def test_validate_valid_svg(self, validator, valid_svg):
        """Test validation of valid SVG"""
        result = validator.validate(valid_svg)

        # Check structure
        assert 'score' in result
        assert 'valid_structure' in result
        assert 'has_svg_tag' in result
        assert 'has_viewbox' in result
        assert 'issues' in result
        assert 'weight' in result

        # Check values
        assert result['score'] == 100
        assert result['valid_structure'] is True
        assert result['has_svg_tag'] is True
        assert result['has_viewbox'] is True
        assert len(result['issues']) == 0
        assert result['weight'] == 0.15

    def test_validate_svg_no_viewbox(self, validator, svg_no_viewbox):
        """Test validation of SVG without viewBox"""
        result = validator.validate(svg_no_viewbox)

        assert result['has_viewbox'] is False
        assert result['score'] < 100
        assert any('viewBox' in issue for issue in result['issues'])

    def test_validate_svg_in_markdown(self, validator, svg_in_markdown):
        """Test extraction and validation of SVG from markdown"""
        result = validator.validate(svg_in_markdown)

        assert result['has_svg_tag'] is True
        assert result['valid_structure'] is True
        assert result['score'] > 0

    def test_validate_no_svg(self, validator):
        """Test validation with no SVG content"""
        result = validator.validate("This is just plain text with no SVG.")

        assert result['score'] == 0
        assert result['has_svg_tag'] is False
        assert 'No SVG content found' in result['issues']

    def test_validate_invalid_xml(self, validator):
        """Test validation of invalid XML structure"""
        invalid_svg = '<svg><rect x="10" y="10"'  # Unclosed tags

        result = validator.validate(invalid_svg)

        assert result['valid_structure'] is False
        assert result['score'] < 100


class TestSVGVisualEvaluator:
    """Test the SVGVisualEvaluator class"""

    @pytest.fixture
    def evaluator(self):
        """Create evaluator instance"""
        try:
            from praisonaibench.evaluators.svg_evaluator import SVGVisualEvaluator
            return SVGVisualEvaluator(output_dir="output/svg_test")
        except ImportError:
            pytest.skip("SVGVisualEvaluator not available")

    @pytest.fixture
    def simple_svg(self):
        """Simple SVG for testing"""
        return '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">
    <rect x="0" y="0" width="100" height="100" fill="white"/>
    <circle cx="50" cy="50" r="40" fill="red"/>
</svg>'''

    def test_evaluator_initialization(self, evaluator):
        """Test that evaluator initializes correctly"""
        assert evaluator is not None
        assert os.path.exists(evaluator.output_dir)

    def test_evaluate_simple_svg(self, evaluator, simple_svg):
        """Test evaluation of simple SVG"""
        result = evaluator.evaluate(simple_svg, "test_simple")

        # Check structure
        assert 'score' in result
        assert 'renders' in result
        assert 'issues' in result
        assert 'weight' in result

        # Score should be > 0 even without rendering
        assert result['score'] > 0
        assert result['weight'] == 0.35

    def test_evaluate_no_svg(self, evaluator):
        """Test evaluation with no SVG content"""
        result = evaluator.evaluate("No SVG here", "test_no_svg")

        assert result['renders'] is False
        assert 'No SVG content' in str(result['issues'])


class TestSVGSemanticEvaluator:
    """Test the SVGSemanticEvaluator class"""

    @pytest.fixture
    def evaluator(self):
        """Create evaluator instance"""
        try:
            from praisonaibench.evaluators.svg_evaluator import SVGSemanticEvaluator
            return SVGSemanticEvaluator()
        except ImportError:
            pytest.skip("SVGSemanticEvaluator not available")

    @pytest.fixture
    def bridge_svg(self):
        """SVG with bridge-related content"""
        return '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">
    <!-- Golden Gate Bridge -->
    <g id="bridge">
        <rect id="tower1" x="200" y="100" width="20" height="300" fill="#C83C2C"/>
        <rect id="tower2" x="580" y="100" width="20" height="300" fill="#C83C2C"/>
        <!-- Cables -->
        <path id="cable" d="M 200 100 Q 400 50 600 100" stroke="#C83C2C" fill="none"/>
        <!-- Water -->
        <rect id="water" x="0" y="400" width="800" height="200" fill="#1E90FF"/>
    </g>
</svg>'''

    def test_evaluator_initialization(self, evaluator):
        """Test that evaluator initializes correctly"""
        assert evaluator is not None

    def test_keyword_matching(self, evaluator, bridge_svg):
        """Test keyword matching for bridge prompt"""
        prompt = "Generate an SVG of the Golden Gate Bridge"
        result = evaluator.evaluate(bridge_svg, prompt)

        # Check structure
        assert 'score' in result
        assert 'keyword_match' in result
        assert 'method' in result
        assert 'weight' in result

        # Should find bridge-related keywords
        assert result['score'] > 0
        assert result['method'] == 'keyword'
        assert result['weight'] == 0.25

    def test_no_match(self, evaluator):
        """Test with completely unrelated SVG"""
        svg = '<svg><circle cx="50" cy="50" r="10" fill="blue"/></svg>'
        prompt = "Generate an SVG of a detailed car with wheels and windows"

        result = evaluator.evaluate(svg, prompt)

        # Score should be lower for unrelated content
        assert result['score'] < 80


class TestSVGCodeQualityEvaluator:
    """Test the SVGCodeQualityEvaluator class"""

    @pytest.fixture
    def evaluator(self):
        """Create evaluator instance"""
        try:
            from praisonaibench.evaluators.svg_evaluator import SVGCodeQualityEvaluator
            return SVGCodeQualityEvaluator()
        except ImportError:
            pytest.skip("SVGCodeQualityEvaluator not available")

    @pytest.fixture
    def high_quality_svg(self):
        """High quality SVG with good practices"""
        return '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">
    <!-- Main content group -->
    <defs>
        <linearGradient id="grad1">
            <stop offset="0%" style="stop-color:rgb(255,255,0)"/>
            <stop offset="100%" style="stop-color:rgb(255,0,0)"/>
        </linearGradient>
    </defs>
    <g id="main-content">
        <rect x="10" y="10" width="80" height="80" fill="url(#grad1)"/>
        <circle cx="50" cy="50" r="30" fill="blue"/>
        <path d="M 20 80 L 50 20 L 80 80 Z" fill="green"/>
    </g>
</svg>'''

    @pytest.fixture
    def low_quality_svg(self):
        """Low quality SVG with minimal structure"""
        return '<svg><circle cx="50" cy="50" r="10"/></svg>'

    def test_evaluator_initialization(self, evaluator):
        """Test that evaluator initializes correctly"""
        assert evaluator is not None

    def test_high_quality_svg(self, evaluator, high_quality_svg):
        """Test evaluation of high quality SVG"""
        result = evaluator.evaluate(high_quality_svg)

        # Check structure
        assert 'score' in result
        assert 'has_comments' in result
        assert 'uses_groups' in result
        assert 'uses_defs' in result
        assert 'element_count' in result
        assert 'weight' in result

        # High quality should have good score
        assert result['score'] > 50
        assert result['has_comments'] is True
        assert result['uses_groups'] is True
        assert result['uses_defs'] is True
        assert result['element_count'] >= 3

    def test_low_quality_svg(self, evaluator, low_quality_svg):
        """Test evaluation of low quality SVG"""
        result = evaluator.evaluate(low_quality_svg)

        # Low quality should have lower score
        assert result['score'] < 50
        assert result['has_comments'] is False
        assert result['uses_groups'] is False
        assert result['uses_defs'] is False


class TestSVGEvaluator:
    """Test the main SVGEvaluator class"""

    @pytest.fixture
    def evaluator(self):
        """Create evaluator instance without LLM judge"""
        try:
            from praisonaibench.evaluators.svg_evaluator import SVGEvaluator
            return SVGEvaluator(use_llm_judge=False, output_dir="output/svg_test")
        except ImportError:
            pytest.skip("SVGEvaluator not available")

    @pytest.fixture
    def complete_svg(self):
        """Complete SVG for full evaluation"""
        return '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" width="800" height="600">
    <!-- Golden Gate Bridge at Sunset -->
    <defs>
        <linearGradient id="sunset" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#FF6B35"/>
            <stop offset="50%" style="stop-color:#F7931E"/>
            <stop offset="100%" style="stop-color:#FFD700"/>
        </linearGradient>
        <linearGradient id="water" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#1E90FF"/>
            <stop offset="100%" style="stop-color:#00008B"/>
        </linearGradient>
    </defs>

    <!-- Sky -->
    <rect x="0" y="0" width="800" height="400" fill="url(#sunset)"/>

    <!-- Water -->
    <rect x="0" y="400" width="800" height="200" fill="url(#water)"/>

    <!-- Bridge -->
    <g id="bridge" fill="#C83C2C">
        <!-- Left Tower -->
        <rect x="200" y="150" width="30" height="250"/>
        <!-- Right Tower -->
        <rect x="570" y="150" width="30" height="250"/>
        <!-- Road Deck -->
        <rect x="150" y="350" width="500" height="20"/>
        <!-- Main Cables -->
        <path d="M 150 200 Q 400 100 650 200" stroke="#C83C2C" stroke-width="8" fill="none"/>
        <!-- Suspension Cables -->
        <line x1="215" y1="200" x2="215" y2="350" stroke="#C83C2C" stroke-width="3"/>
        <line x1="585" y1="200" x2="585" y2="350" stroke="#C83C2C" stroke-width="3"/>
    </g>

    <!-- Sun -->
    <circle cx="650" cy="100" r="50" fill="#FFD700"/>
</svg>'''

    def test_evaluator_initialization(self, evaluator):
        """Test that evaluator initializes correctly"""
        assert evaluator is not None
        assert evaluator.validator is not None
        assert evaluator.visual is not None
        assert evaluator.semantic is not None
        assert evaluator.code_quality is not None
        assert evaluator.llm_judge is None  # Disabled

    def test_get_language(self, evaluator):
        """Test language identifier"""
        assert evaluator.get_language() == 'svg'

    def test_get_file_extension(self, evaluator):
        """Test file extension"""
        assert evaluator.get_file_extension() == 'svg'

    def test_full_evaluation(self, evaluator, complete_svg):
        """Test complete evaluation flow"""
        result = evaluator.evaluate(
            code=complete_svg,
            test_name="test_golden_gate",
            prompt="Generate an SVG of the Golden Gate Bridge at sunset"
        )

        # Check structure
        assert 'score' in result
        assert 'overall_score' in result
        assert 'passed' in result
        assert 'validity' in result
        assert 'visual' in result
        assert 'semantic' in result
        assert 'code_quality' in result
        assert 'feedback' in result
        assert 'breakdown' in result

        # Check component results
        assert result['validity'] is not None
        assert result['visual'] is not None
        assert result['semantic'] is not None
        assert result['code_quality'] is not None
        assert result['llm_judge'] is None  # Disabled

        # Check scores
        assert 0 <= result['overall_score'] <= 100
        assert result['passed'] in [True, False]

        # Should have good score for this complete SVG
        assert result['overall_score'] > 50

    def test_evaluation_with_markdown(self, evaluator):
        """Test evaluation of SVG in markdown"""
        markdown_svg = '''Here is the requested SVG:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
    <circle cx="50" cy="50" r="40" fill="red"/>
</svg>
```

This creates a simple red circle.'''

        result = evaluator.evaluate(
            code=markdown_svg,
            test_name="test_markdown",
            prompt="Create a red circle"
        )

        assert result['validity']['has_svg_tag'] is True
        assert result['overall_score'] > 0

    def test_feedback_generation(self, evaluator, complete_svg):
        """Test feedback generation"""
        result = evaluator.evaluate(
            code=complete_svg,
            test_name="test_feedback",
            prompt="Generate an SVG"
        )

        feedback = result['feedback']

        # Should have feedback from multiple components
        assert len(feedback) > 0

        # Each feedback item should have structure
        for item in feedback:
            assert 'level' in item
            assert 'component' in item
            assert 'message' in item
            assert item['level'] in ['success', 'warning', 'error', 'info']

    def test_breakdown_generation(self, evaluator, complete_svg):
        """Test score breakdown generation"""
        result = evaluator.evaluate(
            code=complete_svg,
            test_name="test_breakdown",
            prompt="Generate an SVG"
        )

        breakdown = result['breakdown']

        assert 'overall_score' in breakdown
        assert 'components' in breakdown
        assert 'validity' in breakdown['components']
        assert 'visual' in breakdown['components']
        assert 'semantic' in breakdown['components']
        assert 'code_quality' in breakdown['components']


class TestSVGBenchmarkIntegration:
    """Integration tests for SVG benchmark with Bench class"""

    @pytest.fixture
    def bench(self):
        """Create Bench instance"""
        try:
            from praisonaibench import Bench
            return Bench(enable_evaluation=True)
        except ImportError:
            pytest.skip("Bench not available")

    def test_svg_evaluator_registered(self, bench):
        """Test that SVG evaluator is registered in plugin manager"""
        if bench.plugin_manager is not None:
            svg_eval = bench.plugin_manager.get_evaluator('svg')
            assert svg_eval is not None
            assert 'svg' in bench.plugin_manager.list_languages()


# Pytest configuration
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "svg: marks tests for SVG evaluator"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
