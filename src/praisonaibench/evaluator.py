"""
Evaluator - Automated evaluation system for PraisonAI Bench

This module provides comprehensive evaluation capabilities including:
- Expected result comparison
- Code validation (HTML, JavaScript)
- Quality scoring
- Semantic similarity analysis
"""

import re
from typing import Dict, Any, Optional, List
from difflib import SequenceMatcher
import json
import os
import subprocess
import tempfile
from datetime import datetime


class EvaluationResult:
    """Container for evaluation results."""
    
    def __init__(self):
        self.scores = {}
        self.passed = True
        self.feedback = []
        self.metrics = {}
    
    def add_score(self, name: str, value: float, max_value: float = 100.0):
        """Add a score metric."""
        self.scores[name] = {
            "value": value,
            "max": max_value,
            "percentage": (value / max_value * 100) if max_value > 0 else 0
        }
    
    def add_feedback(self, message: str, severity: str = "info"):
        """Add evaluation feedback."""
        self.feedback.append({
            "message": message,
            "severity": severity,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_metric(self, name: str, value: Any):
        """Add a custom metric."""
        self.metrics[name] = value
    
    def set_passed(self, passed: bool):
        """Set overall pass/fail status."""
        self.passed = passed
    
    def get_overall_score(self) -> float:
        """Calculate weighted average of all scores."""
        if not self.scores:
            return 0.0
        
        total = sum(score["percentage"] for score in self.scores.values())
        return total / len(self.scores)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "passed": self.passed,
            "overall_score": round(self.get_overall_score(), 2),
            "scores": self.scores,
            "feedback": self.feedback,
            "metrics": self.metrics
        }


class BaseEvaluator:
    """Base class for all evaluators."""
    
    def evaluate(self, response: str, test_config: Dict[str, Any]) -> EvaluationResult:
        """
        Evaluate a response.
        
        Args:
            response: The LLM response to evaluate
            test_config: Test configuration containing expected results, etc.
            
        Returns:
            EvaluationResult object
        """
        raise NotImplementedError("Subclasses must implement evaluate()")


class ExpectedResultEvaluator(BaseEvaluator):
    """Evaluates responses against expected results."""
    
    def evaluate(self, response: str, test_config: Dict[str, Any]) -> EvaluationResult:
        """Compare response with expected result."""
        result = EvaluationResult()
        
        expected = test_config.get("expected")
        if not expected:
            result.add_feedback("No expected result provided, skipping comparison", "info")
            return result
        
        # Clean and normalize strings
        response_clean = self._normalize_text(response)
        expected_clean = self._normalize_text(expected)
        
        # Calculate similarity score
        similarity = self._calculate_similarity(response_clean, expected_clean)
        result.add_score("similarity", similarity * 100, 100.0)
        
        # Exact match check
        if response_clean == expected_clean:
            result.add_feedback("✅ Exact match with expected result", "success")
            result.add_metric("exact_match", True)
        elif similarity > 0.8:
            result.add_feedback(f"✓ High similarity ({similarity*100:.1f}%) with expected result", "success")
            result.add_metric("exact_match", False)
        elif similarity > 0.5:
            result.add_feedback(f"⚠ Moderate similarity ({similarity*100:.1f}%) with expected result", "warning")
            result.add_metric("exact_match", False)
        else:
            result.add_feedback(f"❌ Low similarity ({similarity*100:.1f}%) with expected result", "error")
            result.set_passed(False)
            result.add_metric("exact_match", False)
        
        # Check if expected keywords are present
        keywords = self._extract_keywords(expected_clean)
        if keywords:
            found_keywords = sum(1 for kw in keywords if kw in response_clean)
            keyword_score = (found_keywords / len(keywords)) * 100
            result.add_score("keyword_match", keyword_score, 100.0)
            result.add_metric("keywords_found", f"{found_keywords}/{len(keywords)}")
        
        return result
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison."""
        # Convert to lowercase
        text = text.lower()
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove punctuation for better matching
        text = re.sub(r'[^\w\s]', '', text)
        return text.strip()
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity ratio between two strings."""
        return SequenceMatcher(None, str1, str2).ratio()
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text."""
        # Simple keyword extraction - words longer than 3 characters
        words = text.split()
        keywords = [w for w in words if len(w) > 3]
        return list(set(keywords))  # Unique keywords


class HTMLCodeEvaluator(BaseEvaluator):
    """Evaluates HTML/JavaScript code for correctness and quality."""
    
    def evaluate(self, response: str, test_config: Dict[str, Any]) -> EvaluationResult:
        """Evaluate HTML/JavaScript code quality."""
        result = EvaluationResult()
        
        # Extract HTML code from response
        html_content = self._extract_html(response)
        
        if not html_content:
            result.add_feedback("No HTML code found in response", "info")
            return result
        
        # Check HTML structure
        structure_score = self._check_html_structure(html_content)
        result.add_score("html_structure", structure_score, 100.0)
        
        # Check for required elements
        required_elements = self._check_required_elements(html_content)
        result.add_score("required_elements", required_elements, 100.0)
        
        # Check JavaScript validity
        js_score = self._check_javascript(html_content)
        result.add_score("javascript_quality", js_score, 100.0)
        
        # Check for best practices
        best_practices_score = self._check_best_practices(html_content)
        result.add_score("best_practices", best_practices_score, 100.0)
        
        # Validate HTML syntax
        is_valid, validation_errors = self._validate_html_syntax(html_content)
        result.add_metric("html_valid", is_valid)
        
        if is_valid:
            result.add_feedback("✅ HTML syntax is valid", "success")
        else:
            result.add_feedback(f"⚠ HTML validation issues found: {len(validation_errors)}", "warning")
            for error in validation_errors[:3]:  # Show first 3 errors
                result.add_feedback(f"  - {error}", "warning")
        
        # Overall pass/fail
        overall_score = result.get_overall_score()
        if overall_score < 60:
            result.set_passed(False)
            result.add_feedback(f"❌ Code quality below threshold ({overall_score:.1f}%)", "error")
        else:
            result.add_feedback(f"✅ Code quality acceptable ({overall_score:.1f}%)", "success")
        
        return result
    
    def _extract_html(self, response: str) -> Optional[str]:
        """Extract HTML code from response."""
        # Try markdown code blocks first
        html_pattern = r'```html\s*\n(.*?)\n```'
        matches = re.findall(html_pattern, response, re.DOTALL | re.IGNORECASE)
        
        if matches:
            return matches[0].strip()
        
        # Check for truncated blocks
        truncated_pattern = r'```html\s*\n(.*)'
        truncated_matches = re.findall(truncated_pattern, response, re.DOTALL | re.IGNORECASE)
        
        if truncated_matches:
            return truncated_matches[0].strip()
        
        # Check if entire response is HTML
        response_stripped = response.strip()
        if (response_stripped.lower().startswith('<!doctype') or 
            response_stripped.lower().startswith('<html')):
            return response_stripped
        
        return None
    
    def _check_html_structure(self, html: str) -> float:
        """Check HTML document structure."""
        score = 0.0
        checks = [
            (r'<!DOCTYPE\s+html>', 20),  # DOCTYPE declaration
            (r'<html[^>]*>', 15),         # HTML tag
            (r'<head[^>]*>', 15),         # HEAD tag
            (r'<body[^>]*>', 15),         # BODY tag
            (r'<title[^>]*>.*?</title>', 15),  # TITLE tag
            (r'</html>', 20),             # Closing HTML tag
        ]
        
        for pattern, points in checks:
            if re.search(pattern, html, re.IGNORECASE | re.DOTALL):
                score += points
        
        return score
    
    def _check_required_elements(self, html: str) -> float:
        """Check for common required elements."""
        score = 100.0  # Start with full score
        
        # Check meta charset
        if not re.search(r'<meta[^>]*charset[^>]*>', html, re.IGNORECASE):
            score -= 20
        
        # Check for proper closing tags
        opening_tags = re.findall(r'<(\w+)[^>]*>', html)
        closing_tags = re.findall(r'</(\w+)>', html)
        
        self_closing = ['meta', 'link', 'img', 'br', 'hr', 'input']
        for tag in opening_tags:
            if tag.lower() not in self_closing and tag.lower() not in [t.lower() for t in closing_tags]:
                score -= 5  # Deduct for unclosed tags
        
        return max(0, score)
    
    def _check_javascript(self, html: str) -> float:
        """Check JavaScript code quality."""
        score = 100.0
        
        # Extract JavaScript code
        js_pattern = r'<script[^>]*>(.*?)</script>'
        js_blocks = re.findall(js_pattern, html, re.DOTALL | re.IGNORECASE)
        
        if not js_blocks:
            return score  # No JS to evaluate
        
        js_code = '\n'.join(js_blocks)
        
        # Check for common errors
        error_patterns = [
            (r'console\.log\((?![^)]*//)', -5, "Console.log statements found"),  # Console logs
            (r'debugger', -10, "Debugger statements found"),
            (r'alert\(', -5, "Alert statements found"),
        ]
        
        for pattern, deduction, message in error_patterns:
            matches = re.findall(pattern, js_code, re.IGNORECASE)
            if matches:
                score += deduction * min(len(matches), 3)  # Cap deduction
        
        # Check for best practices
        if re.search(r'(const|let)\s+\w+', js_code):
            score += 5  # Using modern variable declarations
        
        if re.search(r'=>', js_code):
            score += 5  # Using arrow functions
        
        return max(0, min(100, score))
    
    def _check_best_practices(self, html: str) -> float:
        """Check for HTML/CSS best practices."""
        score = 100.0
        
        # Check for inline styles (should be avoided)
        inline_styles = re.findall(r'style=', html, re.IGNORECASE)
        if inline_styles:
            score -= min(len(inline_styles) * 2, 20)
        
        # Check for CDN usage (good practice)
        if re.search(r'https?://cdn', html, re.IGNORECASE):
            score += 10
        
        # Check for semantic HTML5 tags
        semantic_tags = ['header', 'footer', 'nav', 'section', 'article', 'aside']
        for tag in semantic_tags:
            if re.search(f'<{tag}[^>]*>', html, re.IGNORECASE):
                score += 2
        
        return min(100, score)
    
    def _validate_html_syntax(self, html: str) -> tuple[bool, List[str]]:
        """Validate HTML syntax (basic validation)."""
        errors = []
        
        # Check for mismatched tags
        tag_pattern = r'<(/?)(\w+)[^>]*>'
        tag_stack = []
        
        for match in re.finditer(tag_pattern, html):
            is_closing = match.group(1) == '/'
            tag_name = match.group(2).lower()
            
            # Skip self-closing tags
            self_closing = ['meta', 'link', 'img', 'br', 'hr', 'input', 'source']
            if tag_name in self_closing:
                continue
            
            if is_closing:
                if not tag_stack:
                    errors.append(f"Closing tag </{tag_name}> without opening tag")
                elif tag_stack[-1] != tag_name:
                    errors.append(f"Mismatched tags: expected </{tag_stack[-1]}>, found </{tag_name}>")
                    tag_stack.pop()
                else:
                    tag_stack.pop()
            else:
                tag_stack.append(tag_name)
        
        # Check for unclosed tags
        if tag_stack:
            errors.append(f"Unclosed tags: {', '.join(tag_stack)}")
        
        return len(errors) == 0, errors


class QualityEvaluator(BaseEvaluator):
    """Evaluates overall response quality."""
    
    def evaluate(self, response: str, test_config: Dict[str, Any]) -> EvaluationResult:
        """Evaluate response quality metrics."""
        result = EvaluationResult()
        
        # Length check
        length_score = self._evaluate_length(response)
        result.add_score("response_length", length_score, 100.0)
        result.add_metric("character_count", len(response))
        result.add_metric("word_count", len(response.split()))
        
        # Completeness check
        completeness_score = self._evaluate_completeness(response)
        result.add_score("completeness", completeness_score, 100.0)
        
        # Structure check
        structure_score = self._evaluate_structure(response)
        result.add_score("structure", structure_score, 100.0)
        
        # Check for truncation
        if self._is_truncated(response):
            result.add_feedback("⚠ Response appears to be truncated", "warning")
            result.add_metric("truncated", True)
            result.set_passed(False)
        else:
            result.add_feedback("✅ Response appears complete", "success")
            result.add_metric("truncated", False)
        
        return result
    
    def _evaluate_length(self, response: str) -> float:
        """Evaluate if response length is appropriate."""
        length = len(response)
        
        if length < 10:
            return 0.0  # Too short
        elif length < 50:
            return 30.0  # Very short but acceptable for simple queries
        elif length < 200:
            return 70.0  # Reasonable length
        elif length < 5000:
            return 100.0  # Good length
        elif length < 10000:
            return 90.0  # Quite long
        else:
            return 80.0  # Very long
    
    def _evaluate_completeness(self, response: str) -> float:
        """Check if response seems complete."""
        # Check for common completion indicators
        completion_indicators = [
            (r'[.!?]$', 30),  # Ends with proper punctuation
            (r'</html>\s*$', 30),  # Ends with closing HTML tag
            (r'```\s*$', 30),  # Ends with code block closure
            (r'\bconclu(sion|de)\b', 20),  # Contains conclusion
            (r'\bsummary\b', 15),  # Contains summary
        ]
        
        score = 40  # Base score
        for pattern, points in completion_indicators:
            if re.search(pattern, response, re.IGNORECASE | re.MULTILINE):
                score += points
                break  # Only add once
        
        return min(100, score)
    
    def _evaluate_structure(self, response: str) -> float:
        """Evaluate response structure."""
        score = 50  # Base score
        
        # Check for paragraphs
        paragraphs = response.split('\n\n')
        if len(paragraphs) > 1:
            score += 15
        
        # Check for code blocks
        if '```' in response:
            score += 15
        
        # Check for lists
        if re.search(r'^[\-\*\d]+[\.\)]\s', response, re.MULTILINE):
            score += 10
        
        # Check for headers (markdown)
        if re.search(r'^#+\s', response, re.MULTILINE):
            score += 10
        
        return min(100, score)
    
    def _is_truncated(self, response: str) -> bool:
        """Check if response appears to be truncated."""
        # Check for incomplete code blocks
        if response.count('```') % 2 != 0:
            return True
        
        # Check for incomplete HTML
        if '<html' in response.lower() and '</html>' not in response.lower():
            return True
        
        # Check for abrupt ending (no punctuation in last 50 chars)
        last_chars = response[-50:] if len(response) > 50 else response
        if not re.search(r'[.!?>\}]', last_chars):
            return True
        
        return False


class CompositeEvaluator:
    """Combines multiple evaluators for comprehensive evaluation."""
    
    def __init__(self):
        self.evaluators = {
            "expected_result": ExpectedResultEvaluator(),
            "html_code": HTMLCodeEvaluator(),
            "quality": QualityEvaluator()
        }
    
    def evaluate(self, response: str, test_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run all applicable evaluators and combine results.
        
        Args:
            response: The LLM response to evaluate
            test_config: Test configuration
            
        Returns:
            Combined evaluation results dictionary
        """
        combined_results = {
            "evaluated_at": datetime.now().isoformat(),
            "overall_passed": True,
            "overall_score": 0.0,
            "evaluations": {},
            "summary": {
                "total_scores": 0,
                "passed_evaluations": 0,
                "failed_evaluations": 0
            }
        }
        
        total_score = 0.0
        score_count = 0
        
        # Run all evaluators
        for name, evaluator in self.evaluators.items():
            eval_result = evaluator.evaluate(response, test_config)
            combined_results["evaluations"][name] = eval_result.to_dict()
            
            # Update overall status
            if not eval_result.passed:
                combined_results["overall_passed"] = False
                combined_results["summary"]["failed_evaluations"] += 1
            else:
                combined_results["summary"]["passed_evaluations"] += 1
            
            # Accumulate scores
            if eval_result.scores:
                total_score += eval_result.get_overall_score()
                score_count += 1
                combined_results["summary"]["total_scores"] += 1
        
        # Calculate overall score
        if score_count > 0:
            combined_results["overall_score"] = round(total_score / score_count, 2)
        
        return combined_results

