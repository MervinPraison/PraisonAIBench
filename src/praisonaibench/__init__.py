"""
PraisonAI Bench - Simple LLM Benchmarking Tool

A user-friendly benchmarking tool for Large Language Models using PraisonAI Agents.
"""

from .version import __version__
from .bench import Bench, BenchAgent
from .plugin_manager import PluginManager
from .cost_tracker import CostTracker
from .report_generator import ReportGenerator
from .svg_report import SVGReportGenerator
from .realtime_svg_ui import run_realtime_comparison

__all__ = [
    'Bench',
    'BenchAgent',
    'PluginManager',
    'CostTracker',
    'ReportGenerator',
    'SVGReportGenerator',
    'run_realtime_comparison',
    '__version__'
]
