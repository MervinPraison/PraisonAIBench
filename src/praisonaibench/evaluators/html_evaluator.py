"""
HTML/JavaScript evaluator adapter.

Wraps the existing HybridEvaluator to match the BaseEvaluator interface.
"""

from ..base_evaluator import BaseEvaluator
from typing import Dict, Any, Optional


class HTMLEvaluator(BaseEvaluator):
    """
    Evaluator for HTML/JavaScript code.
    
    Adapter that wraps the existing HybridEvaluator system.
    """
    
    def __init__(self):
        """Initialize HTML evaluator."""
        # Lazy import to avoid circular dependencies
        from ..hybrid_evaluator import HybridEvaluator
        self.hybrid = HybridEvaluator()
    
    def get_language(self) -> str:
        """Return language identifier."""
        return 'html'
    
    def get_file_extension(self) -> str:
        """Return file extension."""
        return 'html'
    
    def evaluate(self, 
                 code: str, 
                 test_name: str,
                 prompt: str,
                 expected: Optional[str] = None) -> Dict[str, Any]:
        """
        Evaluate HTML/JavaScript code.
        
        Delegates to existing HybridEvaluator for backwards compatibility.
        """
        return self.hybrid.evaluate(
            html_content=code,
            test_name=test_name,
            prompt=prompt,
            expected=expected
        )
