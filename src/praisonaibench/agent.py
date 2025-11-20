"""
BenchAgent - Core agent for running benchmarks using PraisonAI Agents
"""

from praisonaiagents import Agent
from typing import Dict, List, Any, Optional
import json
import time
import logging


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
    
    def run_test(self, prompt: str, test_name: str = None, max_retries: int = 3) -> Dict[str, Any]:
        """
        Run a single benchmark test with retry logic.
        
        Args:
            prompt: The test prompt to send to the agent
            test_name: Optional name for the test
            max_retries: Maximum number of retry attempts (default: 3)
            
        Returns:
            Dictionary containing test results
        """
        start_time = time.time()
        last_error = None
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    # Exponential backoff: 2^attempt seconds
                    wait_time = 2 ** attempt
                    logging.info(f"🔄 Retry attempt {attempt + 1}/{max_retries} after {wait_time}s...")
                    time.sleep(wait_time)
                
                response = self.agent.start(prompt)
                end_time = time.time()
                
                # Check if response is empty or None (indicates silent failure)
                if not response or (isinstance(response, str) and len(response.strip()) == 0):
                    model_name = self.llm.get("model", str(self.llm)) if isinstance(self.llm, dict) else self.llm
                    error_msg = f"Agent returned empty response. This usually indicates an API authentication error or model unavailability. Please check your API keys for model '{model_name}'."
                    
                    if attempt < max_retries - 1:
                        logging.warning(f"⚠️  {error_msg} - Retrying...")
                        last_error = error_msg
                        continue
                    else:
                        logging.error(f"❌ {error_msg}")
                        return {
                            "test_name": test_name or "unnamed_test",
                            "prompt": prompt,
                            "response": None,
                            "model": self.llm,
                            "agent_name": self.name,
                            "execution_time": end_time - start_time,
                            "status": "error",
                            "error": error_msg,
                            "retry_attempts": attempt + 1,
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                        }
                
                # Success!
                result = {
                    "test_name": test_name or "unnamed_test",
                    "prompt": prompt,
                    "response": response,
                    "model": self.llm,
                    "agent_name": self.name,
                    "execution_time": end_time - start_time,
                    "status": "success",
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                
                if attempt > 0:
                    result["retry_attempts"] = attempt + 1
                    logging.info(f"✅ Succeeded after {attempt + 1} attempt(s)")
                
                return result
                
            except Exception as e:
                end_time = time.time()
                model_name = self.llm.get("model", str(self.llm)) if isinstance(self.llm, dict) else self.llm
                error_msg = f"Agent '{self.name}' failed with model '{model_name}': {str(e)}"
                
                if attempt < max_retries - 1:
                    logging.warning(f"⚠️  {error_msg} - Retrying...")
                    last_error = error_msg
                    continue
                else:
                    logging.error(f"❌ {error_msg}", exc_info=True)
                    return {
                        "test_name": test_name or "unnamed_test",
                        "prompt": prompt,
                        "response": None,
                        "model": self.llm,
                        "agent_name": self.name,
                        "execution_time": end_time - start_time,
                        "status": "error",
                        "error": error_msg,
                        "retry_attempts": attempt + 1,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                    }
        
        # Should never reach here, but just in case
        return {
            "test_name": test_name or "unnamed_test",
            "prompt": prompt,
            "response": None,
            "model": self.llm,
            "agent_name": self.name,
            "execution_time": time.time() - start_time,
            "status": "error",
            "error": last_error or "Unknown error after retries",
            "retry_attempts": max_retries,
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
