"""
PraisonAI Bench - Simple LLM Benchmarking Tool

A user-friendly benchmarking tool for Large Language Models using PraisonAI Agents.
"""

from .bench import Bench
from .agent import BenchAgent
from .version import __version__

__all__ = ['Bench', 'BenchAgent', '__version__']
