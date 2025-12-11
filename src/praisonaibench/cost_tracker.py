"""
Cost Tracker - Token usage and cost calculation for LLM benchmarking

Pricing data based on official provider pricing (as of December 2024).
Prices are per 1M tokens (input/output).
"""

from typing import Dict, Any, Optional, Tuple


# Model pricing database (USD per 1M tokens)
# Format: "provider/model": {"input": price, "output": price}
MODEL_PRICING = {
    # OpenAI Models
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.150, "output": 0.600},
    "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    "gpt-4": {"input": 30.00, "output": 60.00},
    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    "gpt-3.5-turbo-16k": {"input": 3.00, "output": 4.00},
    
    # OpenAI O1 Models
    "o1": {"input": 15.00, "output": 60.00},
    "o1-mini": {"input": 3.00, "output": 12.00},
    "o1-preview": {"input": 15.00, "output": 60.00},
    
    # Anthropic Claude Models
    "claude-3-opus-20240229": {"input": 15.00, "output": 75.00},
    "claude-3-sonnet-20240229": {"input": 3.00, "output": 15.00},
    "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
    "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
    
    # Google Gemini Models
    "gemini/gemini-1.5-pro": {"input": 1.25, "output": 5.00},
    "gemini/gemini-1.5-flash": {"input": 0.075, "output": 0.30},
    "gemini/gemini-1.5-flash-8b": {"input": 0.0375, "output": 0.15},
    "gemini/gemini-pro": {"input": 0.50, "output": 1.50},
    
    # XAI Grok Models
    "xai/grok-beta": {"input": 5.00, "output": 15.00},
    "xai/grok-code-fast-1": {"input": 2.00, "output": 6.00},
    
    # Groq Models (highly optimized pricing)
    "groq/llama-3.1-70b-versatile": {"input": 0.59, "output": 0.79},
    "groq/llama-3.1-8b-instant": {"input": 0.05, "output": 0.08},
    "groq/mixtral-8x7b-32768": {"input": 0.24, "output": 0.24},
    
    # Default fallback pricing (for unknown models)
    "default": {"input": 1.00, "output": 3.00}
}


class CostTracker:
    """Track token usage and calculate costs for LLM API calls."""
    
    def __init__(self):
        """Initialize cost tracker."""
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
        self.model_costs = {}
    
    @staticmethod
    def normalize_model_name(model: str) -> str:
        """
        Normalize model name for pricing lookup.
        
        Args:
            model: Model identifier (e.g., "gpt-4o", "openai/gpt-4o")
            
        Returns:
            Normalized model name
        """
        if not model:
            return "default"
        
        # Remove "openai/" prefix if present
        if model.startswith("openai/"):
            model = model.replace("openai/", "")
        
        # Remove "anthropic/" prefix if present
        if model.startswith("anthropic/"):
            model = model.replace("anthropic/", "")
        
        return model
    
    @staticmethod
    def get_model_pricing(model: str) -> Dict[str, float]:
        """
        Get pricing for a specific model.
        
        Args:
            model: Model identifier
            
        Returns:
            Dictionary with input and output prices per 1M tokens
        """
        normalized = CostTracker.normalize_model_name(model)
        
        # Try exact match
        if normalized in MODEL_PRICING:
            return MODEL_PRICING[normalized]
        
        # Try partial match (for versioned models)
        for key in MODEL_PRICING:
            if key in normalized or normalized in key:
                return MODEL_PRICING[key]
        
        # Return default pricing
        return MODEL_PRICING["default"]
    
    @staticmethod
    def calculate_cost(input_tokens: int, 
                      output_tokens: int, 
                      model: str) -> float:
        """
        Calculate cost for token usage.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model: Model identifier
            
        Returns:
            Total cost in USD
        """
        pricing = CostTracker.get_model_pricing(model)
        
        # Convert from per-1M-tokens to per-token, then multiply
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        
        return input_cost + output_cost
    
    @staticmethod
    def extract_token_usage(response_data: Any) -> Tuple[int, int]:
        """
        Extract token usage from LiteLLM response.
        
        Args:
            response_data: Response from LiteLLM (can be dict, object, or string)
            
        Returns:
            Tuple of (input_tokens, output_tokens)
        """
        input_tokens = 0
        output_tokens = 0
        
        try:
            # If response is a dict with usage info
            if isinstance(response_data, dict):
                if "usage" in response_data:
                    usage = response_data["usage"]
                    input_tokens = usage.get("prompt_tokens", 0)
                    output_tokens = usage.get("completion_tokens", 0)
                elif "token_usage" in response_data:
                    usage = response_data["token_usage"]
                    input_tokens = usage.get("input_tokens", 0)
                    output_tokens = usage.get("output_tokens", 0)
            
            # If response has attributes (object)
            elif hasattr(response_data, "usage"):
                usage = response_data.usage
                if hasattr(usage, "prompt_tokens"):
                    input_tokens = usage.prompt_tokens
                    output_tokens = usage.completion_tokens
                elif hasattr(usage, "input_tokens"):
                    input_tokens = usage.input_tokens
                    output_tokens = usage.output_tokens
            
            # If response has _hidden_params (LiteLLM specific)
            elif hasattr(response_data, "_hidden_params"):
                hidden = response_data._hidden_params
                if "response_cost" in hidden:
                    # Try to extract from additional_kwargs
                    if "additional_kwargs" in hidden:
                        kwargs = hidden["additional_kwargs"]
                        if "usage" in kwargs:
                            usage = kwargs["usage"]
                            input_tokens = usage.get("prompt_tokens", 0)
                            output_tokens = usage.get("completion_tokens", 0)
        
        except Exception:
            # If extraction fails, return 0s
            pass
        
        return input_tokens, output_tokens
    
    @staticmethod
    def estimate_tokens(text: str) -> int:
        """
        Rough estimation of tokens from text.
        Uses approximation: 1 token ≈ 4 characters.
        
        Args:
            text: Input text
            
        Returns:
            Estimated token count
        """
        if not text:
            return 0
        return len(text) // 4
    
    def add_usage(self, input_tokens: int, output_tokens: int, 
                  model: str, cost: Optional[float] = None):
        """
        Add token usage to tracker.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model: Model identifier
            cost: Pre-calculated cost (optional)
        """
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        
        if cost is None:
            cost = self.calculate_cost(input_tokens, output_tokens, model)
        
        self.total_cost += cost
        
        # Track per-model costs
        if model not in self.model_costs:
            self.model_costs[model] = {
                "input_tokens": 0,
                "output_tokens": 0,
                "cost": 0.0
            }
        
        self.model_costs[model]["input_tokens"] += input_tokens
        self.model_costs[model]["output_tokens"] += output_tokens
        self.model_costs[model]["cost"] += cost
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get cost tracking summary.
        
        Returns:
            Dictionary with totals and per-model breakdown
        """
        return {
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "total_cost_usd": round(self.total_cost, 4),
            "by_model": self.model_costs
        }
