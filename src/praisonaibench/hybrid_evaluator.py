"""
PraisonAI Bench - Hybrid Evaluator
Research-backed multi-metric evaluation system

Components:
1. HTML Structure Validator (15%) - Static validation
2. Functional Evaluator (40%) - Browser testing
3. Expected Result Evaluator (20%) - Objective comparison
4. LLM Judge (25%) - Semantic quality

Based on:
- ArXiv 2404.09135: "Unveiling LLM Evaluation Focused on Metrics"
- Nature Scientific Reports: "Evaluation metrics for ML"
- ArXiv 2506.13832: "FrontendBench"
- GoCodeo: "Measuring AI Code Generation Quality"
"""

from difflib import SequenceMatcher
from html.parser import HTMLParser
from typing import Any, Dict, Optional

from .simple_evaluator import LLMJudge, SimpleEvaluator


class HTMLStructureValidator:
    """
    Static HTML structure validation (15% weight)
    Pre-flight validation before browser testing
    """
    
    def validate(self, html_content: str) -> Dict[str, Any]:
        """
        Validate HTML structure statically
        
        Args:
            html_content: The HTML code to validate
            
        Returns:
            {
                'score': 0-100,
                'valid_structure': bool,
                'has_doctype': bool,
                'has_required_tags': bool,
                'issues': list
            }
        """
        score = 0
        issues = []
        
        # DOCTYPE check (25 points)
        has_doctype = '<!DOCTYPE' in html_content.upper()
        if has_doctype:
            score += 25
        else:
            issues.append("Missing DOCTYPE declaration")
        
        # Required tags check (25 points)
        required_tags = ['<html', '<head', '<body']
        found_tags = sum(1 for tag in required_tags if tag in html_content.lower())
        tag_score = (found_tags / len(required_tags)) * 25
        score += tag_score
        
        if found_tags < len(required_tags):
            missing = [tag for tag in required_tags if tag not in html_content.lower()]
            issues.append(f"Missing required tags: {', '.join(missing)}")
        
        # Valid HTML structure (50 points)
        try:
            parser = HTMLParser()
            parser.feed(html_content)
            score += 50
            valid_structure = True
        except Exception as e:
            issues.append(f"Invalid HTML structure: {str(e)}")
            valid_structure = False
        
        return {
            'score': int(score),
            'valid_structure': valid_structure,
            'has_doctype': has_doctype,
            'has_required_tags': found_tags == len(required_tags),
            'issues': issues,
            'weight': 0.15
        }


class ExpectedResultEvaluator:
    """
    Expected result comparison (20% weight)
    Objective measurement using similarity scoring
    """
    
    def evaluate(self, response: str, expected: str) -> Dict[str, Any]:
        """
        Compare response against expected result
        
        Args:
            response: The actual response/output (can be HTML or plain text)
            expected: The expected result
            
        Returns:
            {
                'score': 0-100,
                'similarity': 0-1,
                'keyword_match': 0-1,
                'exact_match': bool
            }
        """
        if not expected:
            return None
        
        # Extract text content from HTML if response contains HTML
        # This allows comparing the visible output, not the HTML structure
        from html.parser import HTMLParser
        
        class TextExtractor(HTMLParser):
            def __init__(self):
                super().__init__()
                self.text = []
            
            def handle_data(self, data):
                self.text.append(data)
            
            def get_text(self):
                return ' '.join(self.text)
        
        # Try to extract text from HTML, fallback to original if not HTML
        if '<html' in response.lower() or '<!doctype' in response.lower():
            try:
                extractor = TextExtractor()
                extractor.feed(response)
                response_text = extractor.get_text()
            except Exception:
                # Fallback to original if HTML parsing fails
                response_text = response
        else:
            response_text = response
        
        # Normalize strings
        response_norm = response_text.strip().lower()
        expected_norm = expected.strip().lower()
        
        # Exact match (100 points)
        if response_norm == expected_norm:
            return {
                'score': 100,
                'similarity': 1.0,
                'keyword_match': 1.0,
                'exact_match': True,
                'weight': 0.20
            }
        
        # Similarity scoring (70% weight)
        similarity = SequenceMatcher(None, response_norm, expected_norm).ratio()
        
        # Keyword matching (30% weight)
        keywords = expected_norm.split()
        if keywords:
            keyword_score = sum(1 for kw in keywords if kw in response_norm) / len(keywords)
        else:
            keyword_score = 0.0
        
        # Combined score
        combined_score = (similarity * 0.7 + keyword_score * 0.3)
        score = int(combined_score * 100)
        
        return {
            'score': score,
            'similarity': round(similarity, 3),
            'keyword_match': round(keyword_score, 3),
            'exact_match': False,
            'weight': 0.20
        }


class HybridEvaluator:
    """
    Hybrid evaluation system combining multiple metrics
    
    Weights (research-backed):
    - HTML Validation: 15%
    - Functional: 40%
    - Expected: 20% (optional)
    - LLM Judge: 25%
    
    When expected is missing, weights are normalized:
    - HTML: 18.75%
    - Functional: 50%
    - LLM Judge: 31.25%
    """
    
    def __init__(self, 
                 use_llm_judge: bool = True,
                 judge_model: str = "gpt-5.1",
                 headless: bool = True):
        """
        Initialize hybrid evaluator
        
        Args:
            use_llm_judge: Enable LLM-as-a-Judge quality scoring
            judge_model: Model to use for judging (default: gpt-5.1)
            headless: Run browser in headless mode
        """
        self.html_validator = HTMLStructureValidator()
        self.functional = SimpleEvaluator(headless=headless)
        self.expected_evaluator = ExpectedResultEvaluator()
        self.llm_judge = LLMJudge(judge_model) if use_llm_judge else None
    
    def evaluate(self, 
                 html_content: str, 
                 test_name: str,
                 prompt: str,
                 expected: Optional[str] = None) -> Dict[str, Any]:
        """
        Comprehensive evaluation with multiple metrics
        
        Args:
            html_content: The HTML code to evaluate
            test_name: Name of the test
            prompt: Original prompt/requirement
            expected: Optional expected result for objective comparison
            
        Returns:
            Complete evaluation results with all metrics
        """
        results = {}
        
        # 1. HTML Structure Validation (15%) - Fast pre-flight check
        results['html_validation'] = self.html_validator.validate(html_content)
        
        # 2. Functional Evaluation (40%) - Browser testing
        results['functional'] = self.functional.evaluate(html_content, test_name)
        
        # 3. Expected Result (20%) - Optional objective comparison
        if expected:
            results['expected'] = self.expected_evaluator.evaluate(html_content, expected)
        else:
            results['expected'] = None
        
        # 4. LLM Judge (25%) - Semantic quality assessment
        if self.llm_judge:
            results['llm_judge'] = self.llm_judge.evaluate(html_content, prompt)
        else:
            results['llm_judge'] = None
        
        # Calculate overall score with dynamic weighting
        overall_score = self._calculate_overall(results)
        
        return {
            'html_validation': results['html_validation'],
            'functional': results['functional'],
            'expected': results['expected'],
            'llm_judge': results['llm_judge'],
            'overall_score': overall_score,
            'passed': overall_score >= 70,
            'breakdown': self._generate_breakdown(results, overall_score)
        }
    
    def _calculate_overall(self, results: Dict[str, Any]) -> int:
        """
        Calculate overall score with dynamic weight normalization
        
        When expected is missing, weights are automatically normalized:
        - HTML: 15% → 18.75%
        - Functional: 40% → 50%
        - LLM: 25% → 31.25%
        """
        score = 0.0
        total_weight = 0.0
        
        # HTML Validation (15%)
        if results.get('html_validation'):
            weight = 0.15
            score += results['html_validation']['score'] * weight
            total_weight += weight
        
        # Functional (40%)
        if results.get('functional'):
            weight = 0.40
            score += results['functional']['score'] * weight
            total_weight += weight
        
        # Expected (20%) - Optional
        if results.get('expected'):
            weight = 0.20
            score += results['expected']['score'] * weight
            total_weight += weight
        
        # LLM Judge (25%) - uses 'quality_score' instead of 'score'
        if results.get('llm_judge'):
            weight = 0.25
            llm_result = results['llm_judge']
            llm_score = llm_result.get('quality_score', llm_result.get('score', 0))
            score += llm_score * weight
            total_weight += weight
        
        # Normalize if expected is missing
        if total_weight > 0 and total_weight < 1.0:
            score = score / total_weight
        
        return int(score)
    
    def _generate_breakdown(self, results: Dict[str, Any], overall: int) -> Dict[str, Any]:
        """
        Generate detailed score breakdown for transparency
        """
        breakdown = {
            'overall_score': overall,
            'components': {}
        }
        
        # Calculate actual weights used
        has_expected = results.get('expected') is not None
        
        if has_expected:
            weights = {
                'html_validation': 0.15,
                'functional': 0.40,
                'expected': 0.20,
                'llm_judge': 0.25
            }
        else:
            # Normalized weights when expected is missing
            weights = {
                'html_validation': 0.1875,
                'functional': 0.50,
                'expected': 0.0,
                'llm_judge': 0.3125
            }
        
        # Add component details
        for component, weight in weights.items():
            if results.get(component):
                comp_result = results[component]
                # Handle llm_judge which uses 'quality_score' instead of 'score'
                if component == 'llm_judge':
                    comp_score = comp_result.get('quality_score', comp_result.get('score', 0))
                else:
                    comp_score = comp_result.get('score', 0)
                breakdown['components'][component] = {
                    'score': comp_score,
                    'weight': f"{weight * 100:.2f}%",
                    'contribution': f"{comp_score * weight:.2f}"
                }
            elif component == 'expected' and not has_expected:
                breakdown['components'][component] = {
                    'score': 'N/A',
                    'weight': '0%',
                    'contribution': 'Not provided'
                }
        
        return breakdown
    
    def get_feedback(self, results: Dict[str, Any]) -> list:
        """
        Generate comprehensive feedback from all evaluation components
        """
        feedback = []
        
        # HTML Validation feedback
        if results.get('html_validation'):
            html_result = results['html_validation']
            if html_result['issues']:
                feedback.append({
                    'level': 'warning',
                    'component': 'HTML Validation',
                    'message': f"⚠️  {len(html_result['issues'])} HTML structure issue(s)",
                    'details': html_result['issues']
                })
            else:
                feedback.append({
                    'level': 'success',
                    'component': 'HTML Validation',
                    'message': '✅ Valid HTML structure'
                })
        
        # Functional feedback
        if results.get('functional'):
            func_result = results['functional']
            if func_result.get('feedback'):
                for item in func_result['feedback']:
                    item['component'] = 'Functional'
                    feedback.append(item)
        
        # Expected result feedback
        if results.get('expected'):
            exp_result = results['expected']
            if exp_result['exact_match']:
                feedback.append({
                    'level': 'success',
                    'component': 'Expected Result',
                    'message': '✅ Exact match with expected result'
                })
            elif exp_result['score'] >= 80:
                feedback.append({
                    'level': 'success',
                    'component': 'Expected Result',
                    'message': f"✅ High similarity ({exp_result['similarity']:.1%}) with expected result"
                })
            else:
                feedback.append({
                    'level': 'warning',
                    'component': 'Expected Result',
                    'message': f"⚠️  Low similarity ({exp_result['similarity']:.1%}) with expected result"
                })
        
        # LLM Judge feedback - uses 'quality_score' instead of 'score'
        if results.get('llm_judge'):
            llm_result = results['llm_judge']
            llm_score = llm_result.get('quality_score', llm_result.get('score', 0))
            feedback.append({
                'level': 'info',
                'component': 'LLM Judge',
                'message': f"🤖 Quality Score: {llm_score}/100",
                'reasoning': llm_result.get('reasoning', ''),
                'strengths': llm_result.get('strengths', ''),
                'weaknesses': llm_result.get('weaknesses', [])
            })
        
        return feedback
