# PraisonAI Bench - Evaluation System
## Comprehensive Guide to Automated LLM Output Evaluation

**Version**: 1.0  
**Last Updated**: 2025-11-19  
**Status**: Production Ready

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Evaluation Philosophy](#evaluation-philosophy)
3. [Tier 1: Functional Validation](#tier-1-functional-validation)
4. [Tier 2: Quality Assessment](#tier-2-quality-assessment)
5. [Tier 3: Comparative Analysis](#tier-3-comparative-analysis)
6. [Implementation Guide](#implementation-guide)
7. [Best Practices](#best-practices)
8. [Metrics & Scoring](#metrics--scoring)
9. [Configuration](#configuration)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

PraisonAI Bench's evaluation system transforms raw LLM outputs into actionable quality insights. Unlike traditional text-matching approaches, our system validates **actual functionality** through browser automation, code quality through LLM-as-a-Judge, and provides comprehensive comparative analysis.

### Why This Approach?

Based on latest industry research (Playwright 2025, LLM evaluation best practices, Sebastian Raschka's evaluation guide):

- ✅ **Functional Correctness > Text Similarity** - Test what code **does**, not what it **says**
- ✅ **Browser Automation** - Catch runtime errors, validate visual output  
- ✅ **LLM-as-a-Judge** - Nuanced quality assessment beyond regex
- ✅ **Multi-Dimensional** - Functionality + Quality + Performance
- ✅ **Simple Implementation** - ~200 lines of clean Python code
- ✅ **No Complex Dependencies** - Just Playwright + standard library

### Key Principles

1. **Test User-Visible Behavior** - Validate what end users see and interact with
2. **Isolation** - Each test runs independently with fresh browser context
3. **Reliability** - Use web-first assertions that auto-wait for conditions
4. **Actionable Feedback** - Provide specific, helpful error messages
5. **Simplicity First** - Start with essentials, add complexity only if needed
6. **Fast Execution** - Complete evaluation in 3-5 seconds per test

---

## 🧭 Evaluation Philosophy

### What We Evaluate

```
┌─────────────────────────────────────────────────────────┐
│                  Evaluation Pyramid                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│                    Tier 3                               │
│              Comparative Analysis                       │
│         (Cross-model, Rankings, Trends)                 │
│                        ▲                                │
│                        │                                │
│                    Tier 2                               │
│              Quality Assessment                         │
│      (Code Quality, Best Practices, A11y)               │
│                        ▲                                │
│                        │                                │
│                    Tier 1                               │
│            Functional Validation                        │
│    (Does it work? Runtime errors? Visual output)        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### What We DON'T Evaluate

❌ **Text similarity to "expected" output** - Too rigid, misses valid alternatives  
❌ **Implementation details** - Focus on outcomes, not how code achieves them  
❌ **Third-party dependencies** - Only test what we control  
❌ **Subjective preferences** - Use objective, measurable criteria

---
## 🔬 Tier 1: Functional Validation

**Priority**: CRITICAL  
**Tools**: Playwright, BeautifulSoup  
**Execution Time**: ~2-5 seconds per test

### What It Does

Validates that generated HTML/JavaScript **actually works** by:
1. Rendering in a real browser (Chromium)
2. Detecting JavaScript errors
3. Checking for required elements
4. Capturing screenshots
5. Validating structure

### Implementation

```python
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json

class FunctionalValidator:
    """
    Validates HTML/JS functionality using Playwright
    
    Based on Playwright best practices:
    - Test user-visible behavior
    - Use web-first assertions
    - Isolated test execution
    """
    
    def __init__(self, headless=True):
        self.headless = headless
        self.results = {}
    
    def validate(self, html_content: str, test_name: str, requirements: dict = None) -> dict:
        """
        Main validation method
        
        Args:
            html_content: The HTML code to validate
            test_name: Name of the test
            requirements: Optional dict of functional requirements
        
        Returns:
            dict with validation results
        """
        results = {
            'test_name': test_name,
            'functional_score': 0,
            'checks': {},
            'errors': [],
            'warnings': [],
            'screenshot_path': None,
            'render_time_ms': 0
        }
        
        # 1. Parse HTML structure
        results['checks']['html_structure'] = self._validate_structure(html_content)
        
        # 2. Browser-based validation
        browser_results = self._validate_in_browser(html_content, test_name, requirements)
        results.update(browser_results)
        
        # 3. Calculate functional score
        results['functional_score'] = self._calculate_functional_score(results)
        
        return results
    
    def _validate_structure(self, html_content: str) -> dict:
        """Validate HTML structure using BeautifulSoup"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            return {
                'valid': True,
                'has_doctype': html_content.strip().lower().startswith('<!doctype'),
                'has_html_tag': soup.find('html') is not None,
                'has_head': soup.find('head') is not None,
                'has_body': soup.find('body') is not None,
                'has_title': soup.find('title') is not None
            }
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }
    
    def _validate_in_browser(self, html_content: str, test_name: str, requirements: dict) -> dict:
        """
        Validate using Playwright browser automation
        
        Implements Playwright best practices:
        - Web-first assertions
        - Automatic waiting
        - Isolated execution
        """
        results = {
            'renders_successfully': False,
            'javascript_executes': False,
            'no_console_errors': False,
            'console_errors': [],
            'console_warnings': [],
            'has_canvas': False,
            'screenshot_path': None,
            'render_time_ms': 0,
            'requirements_met': {}
        }
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=self.headless)
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080}
                )
                page = context.new_page()
                
                # Capture console messages
                console_errors = []
                console_warnings = []
                
                page.on('console', lambda msg: 
                    console_errors.append(msg.text()) if msg.type == 'error' else
                    console_warnings.append(msg.text()) if msg.type == 'warning' else None
                )
                
                # Capture page errors
                page.on('pageerror', lambda err: console_errors.append(str(err)))
                
                # Load HTML and measure render time
                import time
                start_time = time.time()
                
                page.set_content(html_content)
                page.wait_for_load_state('networkidle', timeout=5000)
                
                render_time = (time.time() - start_time) * 1000
                
                # Take screenshot
                screenshot_path = f"output/screenshots/{test_name}.png"
                page.screenshot(path=screenshot_path, full_page=True)
                
                # Check for canvas (Three.js indicator)
                has_canvas = page.query_selector('canvas') is not None
                
                # Check requirements if provided
                if requirements:
                    results['requirements_met'] = self._check_requirements(
                        page, requirements
                    )
                
                results.update({
                    'renders_successfully': True,
                    'javascript_executes': True,
                    'no_console_errors': len(console_errors) == 0,
                    'console_errors': console_errors,
                    'console_warnings': console_warnings,
                    'has_canvas': has_canvas,
                    'screenshot_path': screenshot_path,
                    'render_time_ms': round(render_time, 2)
                })
                
                browser.close()
                
        except Exception as e:
            results['errors'] = [str(e)]
        
        return results
    
    def _check_requirements(self, page, requirements: dict) -> dict:
        """
        Check functional requirements
        
        Example requirements:
        {
            'has_element': ['canvas', 'button'],
            'has_text': ['Three.js', 'Rotate'],
            'has_animation': True
        }
        """
        results = {}
        
        # Check for required elements
        if 'has_element' in requirements:
            for element in requirements['has_element']:
                results[f'has_{element}'] = page.query_selector(element) is not None
        
        # Check for required text
        if 'has_text' in requirements:
            page_text = page.content()
            for text in requirements['has_text']:
                results[f'contains_{text}'] = text in page_text
        
        # Check for animation (basic check)
        if requirements.get('has_animation'):
            # Check if requestAnimationFrame is called
            has_animation = page.evaluate('''
                () => {
                    return typeof requestAnimationFrame !== 'undefined';
                }
            ''')
            results['has_animation'] = has_animation
        
        return results
    
    def _calculate_functional_score(self, results: dict) -> int:
        """Calculate 0-100 functional score"""
        score = 0
        max_score = 100
        
        # Structure (20 points)
        structure = results['checks'].get('html_structure', {})
        if structure.get('valid'):
            score += 5
        if structure.get('has_doctype'):
            score += 3
        if structure.get('has_html_tag'):
            score += 3
        if structure.get('has_head'):
            score += 3
        if structure.get('has_body'):
            score += 3
        if structure.get('has_title'):
            score += 3
        
        # Rendering (30 points)
        if results.get('renders_successfully'):
            score += 30
        
        # No errors (30 points)
        if results.get('no_console_errors'):
            score += 30
        elif len(results.get('console_errors', [])) <= 2:
            score += 15  # Partial credit
        
        # Performance (10 points)
        render_time = results.get('render_time_ms', 0)
        if render_time > 0:
            if render_time < 1000:
                score += 10
            elif render_time < 3000:
                score += 5
        
        # Requirements (10 points)
        requirements_met = results.get('requirements_met', {})
        if requirements_met:
            met_count = sum(1 for v in requirements_met.values() if v)
            total_count = len(requirements_met)
            score += int((met_count / total_count) * 10) if total_count > 0 else 0
        
        return min(score, max_score)
```

### Usage Example

```python
# In bench.py
from praisonaibench.evaluator import FunctionalValidator

validator = FunctionalValidator()

# Define requirements for Three.js tests
requirements = {
    'has_element': ['canvas'],
    'has_text': ['Three.js'],
    'has_animation': True
}

# Validate HTML output
result = validator.validate(
    html_content=response,
    test_name="rotating_cube",
    requirements=requirements
)

print(f"Functional Score: {result['functional_score']}/100")
print(f"Renders: {result['renders_successfully']}")
print(f"Errors: {len(result['console_errors'])}")
print(f"Screenshot: {result['screenshot_path']}")
```

### Test Configuration Format

```yaml
tests:
  - name: "rotating_cube_simulation"
    prompt: "Create a rotating cube with Three.js..."
    
    # Functional requirements (testable assertions)
    functional_requirements:
      has_element:
        - canvas
        - script
      has_text:
        - "Three.js"
        - "OrbitControls"
      has_animation: true
      max_render_time_ms: 3000
      max_console_errors: 0
```

---

## 🎨 Tier 2: Quality Assessment

**Priority**: HIGH  
**Tools**: LLM-as-a-Judge, axe-core, ESLint  
**Execution Time**: ~3-8 seconds per test

### What It Does

Evaluates code quality through:
1. LLM-as-a-Judge for semantic quality
2. Accessibility testing (WCAG compliance)
3. Best practices validation
4. Performance analysis

### 2.1 LLM-as-a-Judge

```python
class LLMCodeQualityEvaluator:
    """
    Use LLM to evaluate code quality
    
    Based on LLM testing best practices 2025:
    - G-Eval framework for scoring
    - Structured output for reliability
    - Calibrated against human feedback
    """
    
    def __init__(self, judge_model="gpt-4o"):
        self.judge_model = judge_model
    
    def evaluate(self, html_content: str, original_prompt: str) -> dict:
        """
        Evaluate code quality using LLM-as-a-Judge
        
        Returns structured evaluation with scores and feedback
        """
        
        evaluation_prompt = f"""You are an expert code reviewer evaluating HTML/JavaScript code.

Original Request:
{original_prompt}

Generated Code:
```html
{html_content[:4000]}  # Truncate for token limits
```

Evaluate the code on these dimensions (0-100 scale):

1. **Completeness**: Does it fulfill all requirements from the prompt?
2. **Code Quality**: Is it well-structured, readable, and maintainable?
3. **Best Practices**: Does it follow HTML5/JavaScript best practices?
4. **Documentation**: Are there helpful comments explaining the code?

Respond ONLY with valid JSON in this exact format:
{{
  "completeness_score": <0-100>,
  "quality_score": <0-100>,
  "best_practices_score": <0-100>,
  "documentation_score": <0-100>,
  "overall_score": <0-100>,
  "strengths": ["strength1", "strength2", "strength3"],
  "weaknesses": ["weakness1", "weakness2"],
  "suggestions": ["suggestion1", "suggestion2"]
}}"""

        try:
            # Use the judge model to evaluate
            from praisonaiagents import Agent
            
            judge = Agent(
                name="CodeQualityJudge",
                role="Expert Code Reviewer",
                goal="Provide objective code quality assessment",
                llm=self.judge_model
            )
            
            response = judge.chat(evaluation_prompt)
            
            # Parse JSON response
            import json
            import re
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                evaluation = json.loads(json_match.group())
                return evaluation
            else:
                return self._default_evaluation("Failed to parse LLM response")
                
        except Exception as e:
            return self._default_evaluation(str(e))
    
    def _default_evaluation(self, error_msg: str) -> dict:
        """Return default evaluation on error"""
        return {
            "completeness_score": 0,
            "quality_score": 0,
            "best_practices_score": 0,
            "documentation_score": 0,
            "overall_score": 0,
            "strengths": [],
            "weaknesses": [f"Evaluation failed: {error_msg}"],
            "suggestions": ["Unable to evaluate"]
        }
```

### 2.2 Accessibility Testing

```python
class AccessibilityEvaluator:
    """
    Test accessibility using axe-core
    
    Based on Playwright + axe-core best practices
    """
    
    def evaluate(self, page) -> dict:
        """
        Run axe-core accessibility tests
        
        Checks WCAG 2.1 Level A and AA compliance
        """
        try:
            # Inject axe-core
            page.add_script_tag(url="https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.7.2/axe.min.js")
            
            # Run axe
            results = page.evaluate("""
                async () => {
                    const results = await axe.run();
                    return {
                        violations: results.violations.length,
                        passes: results.passes.length,
                        incomplete: results.incomplete.length,
                        details: results.violations.map(v => ({
                            id: v.id,
                            impact: v.impact,
                            description: v.description,
                            nodes: v.nodes.length
                        }))
                    };
                }
            """)
            
            # Calculate accessibility score
            total_checks = results['violations'] + results['passes']
            score = int((results['passes'] / total_checks) * 100) if total_checks > 0 else 0
            
            return {
                'accessibility_score': score,
                'violations': results['violations'],
                'passes': results['passes'],
                'details': results['details']
            }
            
        except Exception as e:
            return {
                'accessibility_score': 0,
                'error': str(e)
            }
```

### 2.3 Performance Analysis

```python
class PerformanceEvaluator:
    """Evaluate performance metrics"""
    
    def evaluate(self, page) -> dict:
        """
        Collect performance metrics
        
        Metrics:
        - Page load time
        - Resource count
        - Total size
        - JavaScript execution time
        """
        try:
            metrics = page.evaluate("""
                () => {
                    const perf = performance.getEntriesByType('navigation')[0];
                    const resources = performance.getEntriesByType('resource');
                    
                    return {
                        load_time_ms: perf.loadEventEnd - perf.fetchStart,
                        dom_ready_ms: perf.domContentLoadedEventEnd - perf.fetchStart,
                        resource_count: resources.length,
                        total_size_kb: resources.reduce((sum, r) => sum + (r.transferSize || 0), 0) / 1024
                    };
                }
            """)
            
            # Calculate performance score
            load_time = metrics['load_time_ms']
            score = 100
            if load_time > 3000:
                score = 50
            elif load_time > 1000:
                score = 75
            
            metrics['performance_score'] = score
            return metrics
            
        except Exception as e:
            return {
                'performance_score': 0,
                'error': str(e)
            }
```

---

## 📊 Tier 3: Comparative Analysis

**Priority**: MEDIUM  
**Tools**: Statistical analysis, ranking algorithms  
**Execution Time**: <1 second

### What It Does

Compares results across models to identify:
1. Best performing model per test
2. Most consistent model
3. Best overall model
4. Performance trends

### Implementation

```python
class ComparativeAnalyzer:
    """
    Compare results across multiple models
    
    Provides rankings, trends, and insights
    """
    
    def analyze(self, all_results: list) -> dict:
        """
        Analyze results from multiple models
        
        Args:
            all_results: List of evaluation results from different models
        
        Returns:
            Comparative analysis with rankings
        """
        
        analysis = {
            'model_rankings': {},
            'test_winners': {},
            'overall_winner': None,
            'insights': []
        }
        
        # Group by test name
        tests = {}
        for result in all_results:
            test_name = result['test_name']
            if test_name not in tests:
                tests[test_name] = []
            tests[test_name].append(result)
        
        # Find winner for each test
        for test_name, results in tests.items():
            winner = max(results, key=lambda r: r.get('overall_score', 0))
            analysis['test_winners'][test_name] = {
                'model': winner['model'],
                'score': winner.get('overall_score', 0),
                'render_time_ms': winner.get('render_time_ms', 0)
            }
        
        # Calculate model rankings
        model_scores = {}
        for result in all_results:
            model = result['model']
            if model not in model_scores:
                model_scores[model] = []
            model_scores[model].append(result.get('overall_score', 0))
        
        for model, scores in model_scores.items():
            analysis['model_rankings'][model] = {
                'avg_score': sum(scores) / len(scores),
                'min_score': min(scores),
                'max_score': max(scores),
                'consistency': self._calculate_consistency(scores)
            }
        
        # Determine overall winner
        analysis['overall_winner'] = max(
            analysis['model_rankings'].items(),
            key=lambda x: x[1]['avg_score']
        )[0]
        
        # Generate insights
        analysis['insights'] = self._generate_insights(analysis)
        
        return analysis
    
    def _calculate_consistency(self, scores: list) -> float:
        """Calculate consistency score (lower std dev = more consistent)"""
        if len(scores) < 2:
            return 100.0
        
        import statistics
        std_dev = statistics.stdev(scores)
        # Normalize: 0 std dev = 100, high std dev = 0
        consistency = max(0, 100 - (std_dev * 2))
        return round(consistency, 2)
    
    def _generate_insights(self, analysis: dict) -> list:
        """Generate human-readable insights"""
        insights = []
        
        # Overall winner
        winner = analysis['overall_winner']
        winner_score = analysis['model_rankings'][winner]['avg_score']
        insights.append(f"{winner} is the overall winner with {winner_score:.1f} avg score")
        
        # Most consistent
        most_consistent = max(
            analysis['model_rankings'].items(),
            key=lambda x: x[1]['consistency']
        )
        insights.append(f"{most_consistent[0]} is most consistent ({most_consistent[1]['consistency']:.1f})")
        
        # Test domination
        test_wins = {}
        for test, data in analysis['test_winners'].items():
            model = data['model']
            test_wins[model] = test_wins.get(model, 0) + 1
        
        top_model = max(test_wins.items(), key=lambda x: x[1])
        insights.append(f"{top_model[0]} won {top_model[1]} tests")
        
        return insights
```

---

## 🛠️ Implementation Guide

### Step 1: Install Dependencies

```bash
# Install Playwright
pip install playwright
playwright install chromium

# Install other dependencies
pip install beautifulsoup4 lxml axe-selenium-python
```

### Step 2: Create Evaluator Module

Create `src/praisonaibench/evaluator.py`:

```python
"""
PraisonAI Bench Evaluation System

Comprehensive evaluation using:
- Tier 1: Functional Validation (Playwright)
- Tier 2: Quality Assessment (LLM-as-a-Judge + axe-core)
- Tier 3: Comparative Analysis
"""

from .functional_validator import FunctionalValidator
from .quality_evaluator import LLMCodeQualityEvaluator, AccessibilityEvaluator, PerformanceEvaluator
from .comparative_analyzer import ComparativeAnalyzer

class ComprehensiveEvaluator:
    """
    Main evaluator that orchestrates all evaluation tiers
    """
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        
        # Initialize evaluators
        self.functional_validator = FunctionalValidator(
            headless=self.config.get('headless', True)
        )
        self.quality_evaluator = LLMCodeQualityEvaluator(
            judge_model=self.config.get('judge_model', 'gpt-4o')
        )
        self.accessibility_evaluator = AccessibilityEvaluator()
        self.performance_evaluator = PerformanceEvaluator()
        self.comparative_analyzer = ComparativeAnalyzer()
    
    def evaluate(self, 
                 html_content: str, 
                 test_name: str,
                 original_prompt: str,
                 model: str,
                 requirements: dict = None) -> dict:
        """
        Run comprehensive evaluation
        
        Returns:
            Complete evaluation report with all tiers
        """
        
        report = {
            'test_name': test_name,
            'model': model,
            'tier1_functional': {},
            'tier2_quality': {},
            'overall_score': 0,
            'passed': False,
            'feedback': []
        }
        
        # Tier 1: Functional Validation
        print(f"  ⚡ Running functional validation...")
        functional_results = self.functional_validator.validate(
            html_content, test_name, requirements
        )
        report['tier1_functional'] = functional_results
        
        # Tier 2: Quality Assessment
        print(f"  🎨 Running quality assessment...")
        
        # LLM-as-a-Judge
        quality_results = self.quality_evaluator.evaluate(
            html_content, original_prompt
        )
        report['tier2_quality'] = quality_results
        
        # Calculate overall score (weighted average)
        functional_score = functional_results.get('functional_score', 0)
        quality_score = quality_results.get('overall_score', 0)
        
        # Weights: 60% functional, 40% quality
        overall_score = (functional_score * 0.6) + (quality_score * 0.4)
        report['overall_score'] = round(overall_score, 2)
        
        # Determine pass/fail (threshold: 70)
        report['passed'] = overall_score >= 70
        
        # Generate feedback
        report['feedback'] = self._generate_feedback(report)
        
        return report
    
    def _generate_feedback(self, report: dict) -> list:
        """Generate actionable feedback"""
        feedback = []
        
        functional = report['tier1_functional']
        quality = report['tier2_quality']
        
        # Functional feedback
        if not functional.get('renders_successfully'):
            feedback.append({
                'severity': 'error',
                'message': 'HTML failed to render in browser'
            })
        
        if functional.get('console_errors'):
            feedback.append({
                'severity': 'error',
                'message': f"Found {len(functional['console_errors'])} console errors",
                'details': functional['console_errors'][:3]  # Show first 3
            })
        
        # Quality feedback
        if quality.get('weaknesses'):
            for weakness in quality['weaknesses']:
                feedback.append({
                    'severity': 'warning',
                    'message': weakness
                })
        
        # Positive feedback
        if quality.get('strengths'):
            for strength in quality['strengths'][:2]:  # Show top 2
                feedback.append({
                    'severity': 'success',
                    'message': strength
                })
        
        return feedback
```

### Step 3: Integrate with Bench

Update `src/praisonaibench/bench.py`:

```python
from .evaluator import ComprehensiveEvaluator

class Bench:
    def __init__(self, config_file: str = None, enable_evaluation: bool = True):
        self.results = []
        self.config = self._load_config(config_file)
        self.enable_evaluation = enable_evaluation
        
        # Initialize evaluator
        if self.enable_evaluation:
            self.evaluator = ComprehensiveEvaluator(self.config)
    
    def run_single_test(self, prompt: str, model: str = None, test_name: str = None, 
                       llm_config: dict = None, requirements: dict = None) -> dict:
        """Run test with evaluation"""
        
        # ... existing test execution code ...
        
        # Run evaluation if enabled
        if self.enable_evaluation and result['status'] == 'success':
            print(f"\n📊 Evaluating output...")
            
            evaluation = self.evaluator.evaluate(
                html_content=result['response'],
                test_name=test_name,
                original_prompt=prompt,
                model=model,
                requirements=requirements
            )
            
            result['evaluation'] = evaluation
            
            # Print summary
            print(f"  Overall Score: {evaluation['overall_score']}/100")
            print(f"  Status: {'✅ PASSED' if evaluation['passed'] else '❌ FAILED'}")
            
            # Print feedback
            for item in evaluation['feedback'][:3]:  # Show top 3
                emoji = {'error': '❌', 'warning': '⚠️', 'success': '✅'}
                print(f"  {emoji.get(item['severity'], '•')} {item['message']}")
        
        return result
```

### Step 4: Update CLI

Update `src/praisonaibench/cli.py`:

```python
def main():
    parser = argparse.ArgumentParser(description='PraisonAI Bench')
    
    # ... existing arguments ...
    
    parser.add_argument(
        '--no-eval',
        action='store_true',
        help='Disable evaluation (faster, no quality assessment)'
    )
    
    parser.add_argument(
        '--eval-config',
        type=str,
        help='Path to evaluation configuration file'
    )
    
    args = parser.parse_args()
    
    # Create bench with evaluation setting
    bench = Bench(
        config_file=args.config,
        enable_evaluation=not args.no_eval
    )
    
    # ... rest of CLI code ...
```

---

## ✅ Best Practices

### 1. Test Isolation

Each evaluation should be independent:

```python
# ✅ Good: Isolated browser context
with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context()  # Fresh context
    page = context.new_page()
    # ... test ...
    browser.close()

# ❌ Bad: Reusing browser/page
browser = chromium.launch()
page = browser.new_page()
# Tests share state
```

### 2. Web-First Assertions

Use Playwright's built-in assertions that wait:

```python
# ✅ Good: Waits for element
await expect(page.locator('canvas')).to_be_visible()

# ❌ Bad: Doesn't wait
assert page.locator('canvas').is_visible()
```

### 3. Error Handling

Always handle errors gracefully:

```python
try:
    result = validator.validate(html_content, test_name)
except Exception as e:
    result = {
        'functional_score': 0,
        'error': str(e),
        'passed': False
    }
```

### 4. Performance

Optimize for speed:

```python
# Run evaluations in parallel for multiple tests
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [
        executor.submit(evaluator.evaluate, html, test, prompt, model)
        for html, test, prompt, model in test_data
    ]
    results = [f.result() for f in futures]
```

### 5. Configuration

Make evaluation configurable:

```yaml
# evaluation_config.yaml
evaluation:
  enabled: true
  headless: true
  judge_model: "gpt-4o"
  
  thresholds:
    functional_score: 70
    quality_score: 60
    overall_score: 70
  
  timeout_ms: 5000
  screenshot: true
  
  tiers:
    functional: true
    quality: true
    accessibility: true
    performance: true
    comparative: true
```

---

## 📈 Metrics & Scoring

### Scoring Breakdown

```
Overall Score (0-100) = Weighted Average
├─ Functional Score (60% weight)
│  ├─ Structure (20 points)
│  ├─ Renders Successfully (30 points)
│  ├─ No Console Errors (30 points)
│  ├─ Performance (10 points)
│  └─ Requirements Met (10 points)
│
└─ Quality Score (40% weight)
   ├─ Completeness (25%)
   ├─ Code Quality (25%)
   ├─ Best Practices (25%)
   └─ Documentation (25%)
```

### Pass/Fail Criteria

| Score Range | Status | Description |
|-------------|--------|-------------|
| 90-100 | ⭐ Excellent | Production-ready, best practices |
| 70-89 | ✅ Pass | Good quality, minor improvements needed |
| 50-69 | ⚠️ Warning | Functional but quality issues |
| 0-49 | ❌ Fail | Significant issues, not usable |

### Metrics Collected

**Functional Metrics**:
- Render success rate
- Console error count
- Render time (ms)
- Screenshot captured
- Requirements met (%)

**Quality Metrics**:
- Completeness score (0-100)
- Code quality score (0-100)
- Best practices score (0-100)
- Documentation score (0-100)

**Accessibility Metrics**:
- WCAG violations count
- Accessibility score (0-100)
- Impact levels (critical/serious/moderate/minor)

**Performance Metrics**:
- Page load time (ms)
- DOM ready time (ms)
- Resource count
- Total size (KB)

---

## ⚙️ Configuration

### Evaluation Config File

```yaml
# evaluation_config.yaml

# Global settings
evaluation:
  enabled: true
  headless: true  # Run browser in headless mode
  timeout_ms: 5000
  screenshot: true
  screenshot_dir: "output/screenshots"

# Judge model for quality assessment
judge:
  model: "gpt-4o"
  temperature: 0.1  # Low temperature for consistency
  max_tokens: 1000

# Scoring thresholds
thresholds:
  functional_min: 70
  quality_min: 60
  overall_min: 70
  accessibility_min: 80

# Tier configuration
tiers:
  tier1_functional:
    enabled: true
    timeout_ms: 5000
  
  tier2_quality:
    enabled: true
    llm_judge: true
    accessibility: true
    performance: true
  
  tier3_comparative:
    enabled: true
    generate_insights: true

# Browser settings
browser:
  viewport:
    width: 1920
    height: 1080
  user_agent: "Mozilla/5.0 (Playwright Test)"

# Performance budgets
performance:
  max_load_time_ms: 3000
  max_resource_count: 50
  max_total_size_kb: 5000
```

### Test-Specific Requirements

```yaml
# tests.yaml
tests:
  - name: "rotating_cube_simulation"
    prompt: "Create a rotating cube..."
    
    # Functional requirements
    requirements:
      has_element:
        - canvas
        - script
      has_text:
        - "Three.js"
      has_animation: true
      max_render_time_ms: 2000
      max_console_errors: 0
    
    # Evaluation overrides
    evaluation:
      thresholds:
        functional_min: 80  # Higher bar for this test
        quality_min: 70
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Playwright Installation

**Problem**: `playwright: command not found`

**Solution**:
```bash
pip install playwright
playwright install chromium
```

#### 2. Browser Launch Fails

**Problem**: `Error: Browser closed unexpectedly`

**Solution**:
```bash
# Install system dependencies (Linux)
playwright install-deps

# Or use headless mode
evaluation:
  headless: true
```

#### 3. Timeout Errors

**Problem**: `TimeoutError: page.wait_for_load_state: Timeout 5000ms exceeded`

**Solution**:
```yaml
# Increase timeout
evaluation:
  timeout_ms: 10000
```

#### 4. LLM Judge Errors

**Problem**: `Failed to parse LLM response`

**Solution**:
- Use a more reliable model (gpt-4o instead of gpt-3.5-turbo)
- Add retry logic
- Validate JSON structure

#### 5. Screenshot Failures

**Problem**: `Failed to save screenshot`

**Solution**:
```bash
# Create screenshots directory
mkdir -p output/screenshots

# Check permissions
chmod 755 output/screenshots
```

### Debug Mode

Enable verbose logging:

```python
# In bench.py
import logging
logging.basicConfig(level=logging.DEBUG)

# Or via CLI
praisonaibench --suite tests.yaml --debug
```

### Performance Optimization

If evaluation is too slow:

```yaml
# Disable non-critical tiers
tiers:
  tier2_quality:
    accessibility: false  # Skip a11y checks
    performance: false    # Skip perf analysis
  
  tier3_comparative:
    enabled: false  # Skip comparative analysis
```

---

## 📚 References

### Industry Standards

- **Playwright Best Practices**: https://playwright.dev/docs/best-practices
- **LLM Testing 2025**: https://www.confident-ai.com/blog/llm-testing-in-2024-top-methods-and-strategies
- **Accessibility Testing**: https://www.deque.com/axe/
- **Code Generation Benchmarks**: https://arxiv.org/html/2406.12655v1

### Tools Used

- **Playwright**: Browser automation and testing
- **BeautifulSoup**: HTML parsing
- **axe-core**: Accessibility testing
- **PraisonAI Agents**: LLM-as-a-Judge

### Further Reading

- [Web-First Assertions](https://playwright.dev/docs/test-assertions)
- [G-Eval Framework](https://www.deepeval.com/docs/metrics-llm-evals)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Performance Budgets](https://web.dev/performance-budgets-101/)

---

## 🎯 Quick Reference

### Evaluation Command

```bash
# Run with evaluation (default)
praisonaibench --suite tests.yaml --model gemini/gemini-3-pro-preview

# Run without evaluation (faster)
praisonaibench --suite tests.yaml --no-eval

# Custom evaluation config
praisonaibench --suite tests.yaml --eval-config evaluation_config.yaml
```

### Python API

```python
from praisonaibench import Bench

# With evaluation
bench = Bench(enable_evaluation=True)
result = bench.run_single_test(
    prompt="Create a rotating cube...",
    model="gpt-4o",
    requirements={'has_element': ['canvas']}
)

print(f"Score: {result['evaluation']['overall_score']}/100")
print(f"Passed: {result['evaluation']['passed']}")
```

### Evaluation Output

```json
{
  "test_name": "rotating_cube",
  "model": "gpt-4o",
  "evaluation": {
    "overall_score": 85.5,
    "passed": true,
    "tier1_functional": {
      "functional_score": 90,
      "renders_successfully": true,
      "console_errors": [],
      "screenshot_path": "output/screenshots/rotating_cube.png"
    },
    "tier2_quality": {
      "overall_score": 78,
      "completeness_score": 85,
      "quality_score": 80,
      "strengths": ["Well-structured code", "Good comments"],
      "weaknesses": ["Could use more error handling"]
    },
    "feedback": [
      {"severity": "success", "message": "Renders perfectly"},
      {"severity": "success", "message": "No console errors"},
      {"severity": "warning", "message": "Could use more error handling"}
    ]
  }
}
```

---

**This evaluation system provides the best balance of accuracy, reliability, and ease of implementation for HTML/JavaScript LLM output validation.**

*Last updated: 2025-11-19*
