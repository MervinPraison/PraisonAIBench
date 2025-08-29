"""
BenchAgent - Core agent for running benchmarks using PraisonAI Agents
"""

from praisonaiagents import Agent
from typing import Dict, List, Any, Optional
import json
import time


class BenchAgent:
    """
    A simple agent wrapper for running LLM benchmarks.
    
    This class provides an easy-to-use interface for creating and managing
    benchmark agents using PraisonAI Agents framework.
    """
    
    def __init__(self, 
                 name: str = "BenchAgent",
                 llm: str = "gpt-4o",
                 instructions: str = None):
        """
        Initialize a benchmark agent.
        
        Args:
            name: Name of the agent
            llm: LLM model to use (supports OpenAI, Ollama, Anthropic, etc.)
            instructions: Custom instructions for the agent
        """
        self.name = name
        self.llm = llm
        
        # Default instructions for benchmarking
        default_instructions = """
        You are a helpful AI assistant designed for benchmarking tasks.
        Provide clear, accurate, and detailed responses.
        Follow instructions precisely and maintain consistency in your responses.
        """
        
        self.instructions = instructions or default_instructions
        
        # Initialize the PraisonAI Agent with simple parameters
        self.agent = Agent(
            instructions=self.instructions,
            llm=self.llm
        )
    
    def run_test(self, prompt: str, test_name: str = None) -> Dict[str, Any]:
        """
        Run a single benchmark test.
        
        Args:
            prompt: The test prompt to send to the agent
            test_name: Optional name for the test
            
        Returns:
            Dictionary containing test results
        """
        start_time = time.time()
        
        try:
            response = self.agent.start(prompt)
            end_time = time.time()
            
            return {
                "test_name": test_name or "unnamed_test",
                "prompt": prompt,
                "response": response,
                "model": self.llm,
                "agent_name": self.name,
                "execution_time": end_time - start_time,
                "status": "success",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            end_time = time.time()
            return {
                "test_name": test_name or "unnamed_test",
                "prompt": prompt,
                "response": None,
                "model": self.llm,
                "agent_name": self.name,
                "execution_time": end_time - start_time,
                "status": "error",
                "error": str(e),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def run_multiple_tests(self, tests: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Run multiple benchmark tests.
        
        Args:
            tests: List of test dictionaries with 'prompt' and optional 'name' keys
            
        Returns:
            List of test results
        """
        results = []
        
        for test in tests:
            prompt = test.get("prompt", "")
            test_name = test.get("name", f"test_{len(results) + 1}")
            
            result = self.run_test(prompt, test_name)
            results.append(result)
            
        return results
