"""
Tests for Cost & Token Usage Tracking Feature

Tests the cost tracking functionality added in v0.0.9
"""

import pytest
from unittest.mock import Mock, patch


class TestCostTracker:
    """Test the CostTracker class"""
    
    @pytest.fixture
    def tracker(self):
        """Create CostTracker instance"""
        try:
            from praisonaibench import CostTracker
            return CostTracker()
        except ImportError:
            pytest.skip("CostTracker not available")
    
    def test_tracker_initialization(self, tracker):
        """Test that tracker initializes correctly"""
        assert tracker.total_input_tokens == 0
        assert tracker.total_output_tokens == 0
        assert tracker.total_cost == 0.0
        assert tracker.model_costs == {}
    
    def test_model_pricing_lookup(self):
        """Test model pricing lookup"""
        from praisonaibench import CostTracker
        
        # Test known models
        pricing = CostTracker.get_model_pricing("gpt-4o")
        assert pricing["input"] > 0
        assert pricing["output"] > 0
        
        pricing = CostTracker.get_model_pricing("claude-3-sonnet-20240229")
        assert pricing["input"] > 0
        assert pricing["output"] > 0
        
        # Test default for unknown model
        pricing = CostTracker.get_model_pricing("unknown-model-xyz")
        assert pricing["input"] > 0
        assert pricing["output"] > 0
    
    def test_model_name_normalization(self):
        """Test model name normalization"""
        from praisonaibench import CostTracker
        
        # Test with provider prefix
        normalized = CostTracker.normalize_model_name("openai/gpt-4o")
        assert normalized == "gpt-4o"
        
        normalized = CostTracker.normalize_model_name("anthropic/claude-3-sonnet")
        assert "claude" in normalized.lower()
        
        # Test without prefix
        normalized = CostTracker.normalize_model_name("gpt-4o")
        assert normalized == "gpt-4o"
    
    def test_cost_calculation(self):
        """Test cost calculation"""
        from praisonaibench import CostTracker
        
        # Test with known model
        cost = CostTracker.calculate_cost(1000, 500, "gpt-4o")
        assert cost > 0
        assert isinstance(cost, float)
        
        # Test with zero tokens
        cost = CostTracker.calculate_cost(0, 0, "gpt-4o")
        assert cost == 0.0
        
        # Test with large token count
        cost = CostTracker.calculate_cost(1000000, 500000, "gpt-4o")
        assert cost > 0
    
    def test_token_estimation(self):
        """Test token estimation from text"""
        from praisonaibench import CostTracker
        
        # Test short text
        tokens = CostTracker.estimate_tokens("Hello")
        assert tokens > 0
        
        # Test longer text
        tokens = CostTracker.estimate_tokens("A" * 400)
        assert tokens == 100  # 400 chars / 4 = 100 tokens
        
        # Test empty text
        tokens = CostTracker.estimate_tokens("")
        assert tokens == 0
        
        # Test None
        tokens = CostTracker.estimate_tokens(None)
        assert tokens == 0
    
    def test_add_usage(self, tracker):
        """Test adding token usage"""
        tracker.add_usage(1000, 500, "gpt-4o")
        
        assert tracker.total_input_tokens == 1000
        assert tracker.total_output_tokens == 500
        assert tracker.total_cost > 0
        assert "gpt-4o" in tracker.model_costs
    
    def test_cumulative_tracking(self, tracker):
        """Test cumulative tracking across multiple calls"""
        tracker.add_usage(1000, 500, "gpt-4o")
        tracker.add_usage(2000, 1000, "gpt-4o")
        tracker.add_usage(5000, 2000, "claude-3-haiku-20240307")
        
        assert tracker.total_input_tokens == 8000
        assert tracker.total_output_tokens == 3500
        assert tracker.total_cost > 0
        assert len(tracker.model_costs) == 2
    
    def test_get_summary(self, tracker):
        """Test summary generation"""
        tracker.add_usage(1000, 500, "gpt-4o")
        tracker.add_usage(2000, 1000, "claude-3-haiku-20240307")
        
        summary = tracker.get_summary()
        
        assert "total_input_tokens" in summary
        assert "total_output_tokens" in summary
        assert "total_tokens" in summary
        assert "total_cost_usd" in summary
        assert "by_model" in summary
        
        assert summary["total_tokens"] == 4500
        assert summary["total_cost_usd"] > 0
        assert len(summary["by_model"]) == 2
    
    def test_extract_token_usage_from_dict(self):
        """Test token extraction from dict response"""
        from praisonaibench import CostTracker
        
        # Test with usage dict
        response = {
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50
            }
        }
        
        input_tokens, output_tokens = CostTracker.extract_token_usage(response)
        assert input_tokens == 100
        assert output_tokens == 50
    
    def test_extract_token_usage_from_object(self):
        """Test token extraction from object response"""
        from praisonaibench import CostTracker
        
        # Create mock object with usage attribute
        class MockUsage:
            def __init__(self):
                self.prompt_tokens = 200
                self.completion_tokens = 100
        
        class MockResponse:
            def __init__(self):
                self.usage = MockUsage()
        
        response = MockResponse()
        input_tokens, output_tokens = CostTracker.extract_token_usage(response)
        assert input_tokens == 200
        assert output_tokens == 100
    
    def test_extract_token_usage_fallback(self):
        """Test token extraction fallback to estimation"""
        from praisonaibench import CostTracker
        
        # Test with string (no usage info)
        response = "Some text response"
        input_tokens, output_tokens = CostTracker.extract_token_usage(response)
        # Should return 0, 0 (estimation happens elsewhere)
        assert input_tokens == 0
        assert output_tokens == 0


class TestBenchCostTracking:
    """Test cost tracking integration with Bench"""
    
    @pytest.fixture
    def bench(self):
        """Create Bench instance"""
        try:
            from praisonaibench import Bench
            return Bench(enable_evaluation=False)
        except ImportError:
            pytest.skip("Bench not available")
    
    def test_bench_has_cost_tracker(self, bench):
        """Test that Bench has cost tracker"""
        assert hasattr(bench, 'cost_tracker')
        assert bench.cost_tracker is not None
    
    def test_cost_tracking_in_results(self, bench):
        """Test that results include cost information"""
        # Mock the agent to return a result with token usage
        with patch('praisonaibench.bench.BenchAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.run_test = Mock(return_value={
                'test_name': 'test_1',
                'prompt': 'Test prompt',
                'response': 'Test response',
                'model': 'gpt-4o',
                'agent_name': 'BenchAgent',
                'execution_time': 1.0,
                'status': 'success',
                'timestamp': '2024-01-01 00:00:00',
                'token_usage': {
                    'input_tokens': 100,
                    'output_tokens': 50,
                    'total_tokens': 150,
                    'method': 'estimated'
                },
                'cost': {
                    'total_usd': 0.0005,
                    'input_cost_usd': 0.00025,
                    'output_cost_usd': 0.0005,
                    'model': 'gpt-4o'
                }
            })
            mock_agent_class.return_value = mock_agent
            
            result = bench.run_single_test("Test prompt", model="gpt-4o")
            
            # Check that cost was tracked
            assert (bench.cost_tracker.total_input_tokens + bench.cost_tracker.total_output_tokens) > 0
            assert bench.cost_tracker.total_cost > 0
    
    def test_cost_summary_in_get_summary(self, bench):
        """Test that get_summary includes cost information"""
        # Add a mock result and usage
        bench.results.append({
            'test_name': 'test_1',
            'status': 'success',
            'token_usage': {'input_tokens': 1000, 'output_tokens': 500, 'total_tokens': 1500},
            'cost': {'total_usd': 0.005}
        })
        bench.cost_tracker.add_usage(1000, 500, "gpt-4o")
        
        summary = bench.get_summary()
        
        # Should include cost summary if tokens were used
        total_tokens = bench.cost_tracker.total_input_tokens + bench.cost_tracker.total_output_tokens
        if total_tokens > 0:
            assert "cost_summary" in summary
            assert "total_tokens" in summary["cost_summary"]
            assert "total_cost_usd" in summary["cost_summary"]


class TestAgentCostTracking:
    """Test cost tracking in BenchAgent"""
    
    @pytest.fixture
    def agent(self):
        """Create BenchAgent instance"""
        try:
            from praisonaibench import BenchAgent
            return BenchAgent(name="TestAgent", llm="gpt-4o")
        except ImportError:
            pytest.skip("BenchAgent not available")
    
    def test_extract_usage_and_cost(self, agent):
        """Test token usage and cost extraction"""
        prompt = "What is 2+2?"
        response = "The answer is 4."
        
        token_usage, cost_info = agent._extract_usage_and_cost(prompt, response)
        
        assert "input_tokens" in token_usage
        assert "output_tokens" in token_usage
        assert "total_tokens" in token_usage
        assert "method" in token_usage
        
        assert "total_usd" in cost_info
        assert "input_cost_usd" in cost_info
        assert "output_cost_usd" in cost_info
        assert "model" in cost_info
        
        assert token_usage["total_tokens"] > 0
        assert cost_info["total_usd"] >= 0


class TestCostTrackingCLI:
    """Test CLI cost display"""
    
    def test_cost_display_format(self):
        """Test that cost is displayed in correct format"""
        # This tests the format, not actual CLI execution
        cost_usd = 0.0024
        tokens = 1250
        
        # Format should be: $0.002400 (1250 tokens)
        formatted = f"${cost_usd:.6f} ({tokens} tokens)"
        assert "$0.002400" in formatted
        assert "1250" in formatted


class TestModelPricingDatabase:
    """Test the model pricing database"""
    
    def test_pricing_for_major_models(self):
        """Test that pricing exists for major models"""
        from praisonaibench import CostTracker
        
        models = [
            "gpt-4o",
            "gpt-4o-mini",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "gemini/gemini-1.5-flash",
            "xai/grok-beta"
        ]
        
        for model in models:
            pricing = CostTracker.get_model_pricing(model)
            assert pricing["input"] > 0
            assert pricing["output"] > 0
    
    def test_pricing_consistency(self):
        """Test that pricing is consistent"""
        from praisonaibench import CostTracker
        
        # Same model should return same pricing
        pricing1 = CostTracker.get_model_pricing("gpt-4o")
        pricing2 = CostTracker.get_model_pricing("gpt-4o")
        
        assert pricing1 == pricing2
    
    def test_default_pricing_for_unknown(self):
        """Test that unknown models get default pricing"""
        from praisonaibench import CostTracker
        
        pricing = CostTracker.get_model_pricing("completely-unknown-model-xyz-123")
        
        # Should return default pricing
        assert pricing["input"] > 0
        assert pricing["output"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
