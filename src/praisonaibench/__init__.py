"""
PraisonAI Bench - Simple LLM Benchmarking Tool

A user-friendly benchmarking tool for Large Language Models using PraisonAI Agents.
"""

from .bench import Bench
from .agent import BenchAgent
from .base_evaluator import BaseEvaluator
from .plugin_manager import PluginManager
from .cost_tracker import CostTracker
from .report_generator import ReportGenerator
from .svg_report import SVGReportGenerator, SVGComparisonReport
from .version import __version__

__all__ = [
    'Bench',
    'BenchAgent',
    'BaseEvaluator',
    'PluginManager',
    'CostTracker',
    'ReportGenerator',
    'SVGReportGenerator',
    'SVGComparisonReport',
    '__version__'
]
