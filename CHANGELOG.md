# Changelog

All notable changes to PraisonAI Bench will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.9] - 2024-12-11

### Added
- **Cost & Token Usage Tracking** - Automatic tracking of token usage and costs
  - `CostTracker` class for managing token and cost data
  - Token usage extracted from LiteLLM responses (or estimated from text)
  - Cost calculation for 30+ models across OpenAI, Anthropic, Google, XAI, Groq
  - Per-test cost display: `💰 Cost: $0.002400 (1250 tokens)`
  - Cumulative cost summary in benchmark results
  - Per-model cost breakdown for multi-model tests
  - Token usage included in JSON results: `token_usage` and `cost` fields

### Changed
- Results JSON now includes `token_usage` and `cost` fields
- Summary output includes cost information when available
- `get_summary()` returns cost summary with token counts and costs by model

## [0.0.8] - 2024-12-11

### Added
- **Parallel Test Execution** - Run tests concurrently for faster benchmarking
  - `--concurrent N` CLI flag to specify number of workers
  - Thread-safe result collection with progress tracking
  - Uses `ThreadPoolExecutor` for I/O-bound LLM API calls
  - Results sorted by test name for consistent ordering

### Changed
- `run_test_suite` now accepts `concurrent` parameter (default: 1 = sequential)
- Internal refactoring: sequential and parallel execution separated into `_run_tests_sequential` and `_run_tests_parallel` methods

## [0.0.7] - 2024-11-20

### Added
- **Hybrid Evaluation System** - Research-backed multi-metric evaluation
  - `HTMLStructureValidator` (15% weight) - Static HTML validation
  - `ExpectedResultEvaluator` (20% weight) - Objective comparison with expected results
  - `HybridEvaluator` - Combines all 4 evaluation components
- **Expected Field Support** - Optional `expected` field in test YAML for objective comparison
  - Automatic weight normalization when expected field is not provided
  - Similarity scoring using difflib.SequenceMatcher
  - Keyword matching for partial credit
- **Dynamic Weight Calculation** - Weights automatically adjust based on available metrics
- **Comprehensive Feedback System** - Detailed feedback from all evaluation components
- **Research Validation** - Scoring system validated against 5 research papers

### Changed
- **Evaluation Weights** (research-backed):
  - HTML Validation: 15% (new)
  - Functional: 40% (reduced from 70%)
  - Expected: 20% (new, optional)
  - LLM Judge: 25% (reduced from 30%)
- **LLM Judge Model** - Changed default from `gpt-4o` to `gpt-5.1`
- **README** - Updated with hybrid evaluation details and expected field usage

### Technical Details
- Based on ArXiv 2404.09135, Nature Scientific Reports, ArXiv 2506.13832, GoCodeo, EvidentlyAI
- Objective metrics (75%) > Subjective (25%)
- Deterministic (75%) > Variable (25%)
- Runtime validation (40%) > Static validation (15%)

## [0.0.6] - 2024-11-19

### Changed
- Changed LLM judge model from `gpt-4o` to `gpt-5.1`
- Removed all output truncation (error details, response display)
- Updated README with PyPI installation instructions and testing modes table

### Fixed
- Error details now show all errors instead of truncating to first 3
- Response display shows length instead of truncated content

## [0.0.5] - 2024-11-18

### Added
- Retry logic with exponential backoff (3 attempts)
- Empty response detection for silent API failures
- Retry attempt tracking in results

### Fixed
- Silent authentication failures now properly detected and reported
- Better error messages for API key issues

## [0.0.4] - 2024-11-17

### Added
- Initial evaluation system with functional testing and LLM judge
- Browser-based validation using Playwright
- Console error/warning detection
- Screenshot capture
- Combined scoring (70% functional + 30% quality)

### Changed
- Improved HTML extraction from responses
- Model-specific output directories

## [0.0.3] - 2024-11-16

### Added
- Test suite support with YAML files
- Cross-model comparison
- HTML extraction from responses

## [0.0.2] - 2024-11-15

### Added
- Single test execution
- LiteLLM integration
- Basic CLI interface

## [0.0.1] - 2024-11-14

### Added
- Initial release
- Basic benchmarking functionality
- PraisonAI Agents integration
