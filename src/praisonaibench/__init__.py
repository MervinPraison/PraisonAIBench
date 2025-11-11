"""
PraisonAI Bench - Simple LLM Benchmarking Tool

A user-friendly benchmarking tool for Large Language Models using PraisonAI Agents.
Includes automated evaluation for quality, correctness, and expected result comparison.
"""

from .bench import Bench
from .agent import BenchAgent
from .evaluator import (
    CompositeEvaluator,
    ExpectedResultEvaluator,
    HTMLCodeEvaluator,
    QualityEvaluator,
    EvaluationResult
)
from .version import __version__

__all__ = [
    'Bench',
    'BenchAgent',
    'CompositeEvaluator',
    'ExpectedResultEvaluator',
    'HTMLCodeEvaluator',
    'QualityEvaluator',
    'EvaluationResult',
    '__version__'
]
