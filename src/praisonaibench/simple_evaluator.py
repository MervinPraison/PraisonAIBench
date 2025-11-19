"""
PraisonAI Bench - Simplified Evaluator
~150 lines of production-ready evaluation code

Based on:
- Playwright best practices 2025
- LLM evaluation best practices
- Sebastian Raschka's evaluation guide
"""

from playwright.sync_api import sync_playwright
import time
import os
import json
import re


class SimpleEvaluator:
    """
    Minimal but effective HTML/JS evaluator
    
    What it does:
    1. Renders HTML in real browser (Chromium)
    2. Detects console errors
    3. Takes screenshot
    4. Scores 0-100
    
    What it doesn't do:
    - Complex accessibility testing
    - Detailed performance profiling
    - Text similarity matching
    """
    
    def __init__(self, headless=True):
        self.headless = headless
    
    def evaluate(self, html_content: str, test_name: str) -> dict:
        """
        Main evaluation method
        
        Args:
            html_content: The HTML code to validate
            test_name: Name of the test
        
        Returns:
            {
                'score': 0-100,
                'passed': bool,
                'renders': bool,
                'errors': list,
                'screenshot': str,
                'render_time_ms': float,
                'feedback': list
            }
        """
        result = {
            'score': 0,
            'passed': False,
            'renders': False,
            'errors': [],
            'warnings': [],
            'screenshot': None,
            'render_time_ms': 0,
            'feedback': []
        }
        
        try:
            with sync_playwright() as p:
                # Launch browser
                browser = p.chromium.launch(headless=self.headless)
                page = browser.new_page()
                
                # Capture console messages
                errors = []
                warnings = []
                page.on('console', lambda msg: 
                    errors.append(msg.text) if msg.type == 'error' else
                    warnings.append(msg.text) if msg.type == 'warning' else None
                )
                page.on('pageerror', lambda err: errors.append(str(err)))
                
                # Load HTML and measure time
                start = time.time()
                page.set_content(html_content)
                page.wait_for_load_state('networkidle', timeout=5000)
                render_time = (time.time() - start) * 1000
                
                # Take screenshot
                os.makedirs('output/screenshots', exist_ok=True)
                screenshot_path = f'output/screenshots/{test_name}.png'
                page.screenshot(path=screenshot_path, full_page=True)
                
                # Update results
                result.update({
                    'renders': True,
                    'errors': errors,
                    'warnings': warnings,
                    'screenshot': screenshot_path,
                    'render_time_ms': round(render_time, 2)
                })
                
                browser.close()
                
        except Exception as e:
            result['errors'].append(f"Browser error: {str(e)}")
        
        # Calculate score
        result['score'] = self._calculate_score(result)
        result['passed'] = result['score'] >= 70
        result['feedback'] = self._generate_feedback(result)
        
        return result
    
    def _calculate_score(self, result: dict) -> int:
        """
        Simple scoring: 0-100
        
        - Renders successfully: 50 points
        - No console errors: 30 points
        - Fast render (<3s): 20 points
        """
        score = 0
        
        # Renders successfully
        if result['renders']:
            score += 50
        
        # No console errors
        if len(result['errors']) == 0:
            score += 30
        elif len(result['errors']) <= 2:
            score += 15  # Partial credit
        
        # Performance
        render_time = result['render_time_ms']
        if render_time > 0:
            if render_time < 1000:
                score += 20
            elif render_time < 3000:
                score += 10
        
        return min(score, 100)
    
    def _generate_feedback(self, result: dict) -> list:
        """Generate simple, actionable feedback"""
        feedback = []
        
        if result['renders']:
            feedback.append({
                'level': 'success',
                'message': f"✅ Renders successfully in {result['render_time_ms']}ms"
            })
        else:
            feedback.append({
                'level': 'error',
                'message': '❌ Failed to render'
            })
        
        if len(result['errors']) == 0:
            feedback.append({
                'level': 'success',
                'message': '✅ No console errors'
            })
        else:
            feedback.append({
                'level': 'error',
                'message': f"❌ {len(result['errors'])} console error(s)",
                'details': result['errors'][:3]  # Show first 3
            })
        
        if len(result['warnings']) > 0:
            feedback.append({
                'level': 'warning',
                'message': f"⚠️  {len(result['warnings'])} warning(s)"
            })
        
        return feedback


class LLMJudge:
    """
    Optional: Simple LLM-as-a-Judge
    Uses your existing LLM setup
    """
    
    def __init__(self, model="gpt-4o"):
        self.model = model
    
    def evaluate(self, html_content: str, prompt: str) -> dict:
        """
        Simple quality check using LLM
        
        Args:
            html_content: The HTML code to evaluate
            prompt: Original prompt/request
        
        Returns:
            {
                'quality_score': 0-100,
                'feedback': str
            }
        """
        
        # Simple prompt for LLM
        judge_prompt = f"""Rate this HTML/JS code quality (0-100):

Original request: {prompt}

Code (first 2000 chars):
{html_content[:2000]}

Respond with JSON only:
{{
  "score": <0-100>,
  "feedback": "<one sentence feedback>"
}}"""

        try:
            from praisonaiagents import Agent
            
            judge = Agent(
                name="CodeJudge",
                role="Code Quality Reviewer",
                goal="Provide objective code quality assessment",
                llm=self.model
            )
            
            response = judge.chat(judge_prompt)
            
            # Parse JSON response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return {
                    'quality_score': result.get('score', 0),
                    'feedback': result.get('feedback', 'No feedback')
                }
        except Exception as e:
            print(f"  ⚠️  LLM judge failed: {str(e)}")
        
        return {'quality_score': 0, 'feedback': 'Evaluation failed'}


class CombinedEvaluator:
    """
    Combines functional + quality evaluation
    
    This is the main evaluator you should use.
    """
    
    def __init__(self, use_llm_judge=True, judge_model="gpt-4o", headless=True):
        """
        Initialize combined evaluator
        
        Args:
            use_llm_judge: Enable LLM-as-a-Judge quality scoring
            judge_model: Model to use for judging (default: gpt-4o)
            headless: Run browser in headless mode
        """
        self.functional = SimpleEvaluator(headless=headless)
        self.llm_judge = LLMJudge(judge_model) if use_llm_judge else None
    
    def evaluate(self, html_content: str, test_name: str, prompt: str = "") -> dict:
        """
        Run complete evaluation
        
        Args:
            html_content: The HTML code to evaluate
            test_name: Name of the test
            prompt: Original prompt (needed for LLM judge)
        
        Returns:
            Complete evaluation results with overall score
        """
        # Functional evaluation
        print(f"  ⚡ Running functional validation...")
        functional_result = self.functional.evaluate(html_content, test_name)
        
        result = {
            'test_name': test_name,
            'functional': functional_result,
            'quality': None,
            'overall_score': functional_result['score'],
            'passed': functional_result['passed']
        }
        
        # Optional: LLM judge
        if self.llm_judge and prompt:
            print(f"  🎨 Running LLM quality assessment...")
            quality_result = self.llm_judge.evaluate(html_content, prompt)
            result['quality'] = quality_result
            
            # Combined score: 70% functional, 30% quality
            result['overall_score'] = int(
                functional_result['score'] * 0.7 + 
                quality_result['quality_score'] * 0.3
            )
            result['passed'] = result['overall_score'] >= 70
        
        return result
