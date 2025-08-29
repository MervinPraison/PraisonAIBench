# Product Requirements Document: PraisonAI Bench

## Executive Summary

PraisonAI Bench is an open-source benchmarking tool that enables developers to evaluate and compare different Large Language Models (LLMs) with minimal setup. Built as a Python package using PraisonAI Agents, it provides a simple CLI interface for running standardised tests against various LLM providers and generating structured, reproducible results.

## Product Vision

To become the go-to tool for developers who need quick, reliable, and standardised LLM benchmarking with zero configuration complexity.

## Target Users

### Primary Users
- **AI/ML Developers**: Testing model performance for specific use cases
- **Product Engineers**: Evaluating LLMs for integration decisions
- **Researchers**: Comparing model capabilities across different tasks
- **DevOps Engineers**: Performance testing in CI/CD pipelines

### Secondary Users
- **Technical Writers**: Documenting model comparisons
- **Solution Architects**: Making informed model selection decisions

## Core User Journey

1. **Install**: `pip install praisonaibench`
2. **Configure**: Set up API keys via environment variables
3. **Prepare**: Create or use existing `tests.yaml` file
4. **Execute**: Run `praisonaibench --model openai/gpt-4o`
5. **Review**: Examine results in timestamped output folder

## Functional Requirements

### 1. Python Package Distribution

**FR-1.1**: Package Structure
- Distribute via PyPI as `praisonaibench`
- Use modern Python packaging with `pyproject.toml`
- Use uv package manager
- Support Python 3.8+
- Include console script entry point

**FR-1.2**: Dependencies
- Core: `praisonaiagents`, `pyyaml`, `click`
- Optional: Provider-specific SDKs as needed
- Minimal dependency footprint

### 2. Command Line Interface

**FR-2.1**: Primary Command Structure
```bash
praisonaibench --model <model_identifier> [options]
```

**FR-2.2**: Required Parameters
- `--model`: Model identifier (e.g., `openai/gpt-4o`, `anthropic/claude-3-sonnet`)

**FR-2.3**: Optional Parameters
- `--tests`: Path to test file (default: `./tests.yaml`)
- `--output`: Output directory (default: `./output/`)
- `--verbose`: Enable detailed logging
- `--concurrent`: Number of concurrent requests (default: 1)

**FR-2.4**: Help and Version
- `--help`: Display usage information
- `--version`: Show package version

### 3. Test Configuration Format

**FR-3.1**: YAML Structure
```yaml
tests:
  - title: "Summarise Shakespeare"
    prompt: "Summarise Hamlet in 3 sentences."
    category: "summarisation"
  - title: "Mathematical Reasoning"
    prompt: "Solve 128 * 47 and explain your method."
    category: "mathematics"
  - title: "Creative Writing"
    prompt: "Write a haiku about artificial intelligence."
    category: "creativity"
```

**FR-3.2**: Test Properties
- `title`: Human-readable test identifier (required)
- `prompt`: The actual prompt to send to the model (required)
- `category`: Optional grouping for results analysis
- `expected`: Optional expected response for validation
- `timeout`: Optional per-test timeout in seconds

### 4. Model Provider Support

**FR-4.1**: Supported Providers (via PraisonAI Agents)
- OpenAI (GPT-4, GPT-3.5, etc.)
- Anthropic (Claude family)
- Google (Gemini family)
- Ollama (local models)
- Groq
- Any LiteLLM-compatible provider

**FR-4.2**: Model Identifier Format
- Use LiteLLM naming convention: `provider/model-name`
- Examples: `openai/gpt-4o`, `anthropic/claude-3-sonnet`, `ollama/llama2`

### 5. Execution Engine

**FR-5.1**: Sequential Processing
- Execute tests in order defined in YAML
- Handle API rate limits gracefully
- Implement exponential backoff for retries

**FR-5.2**: Error Handling
- Continue execution on individual test failures
- Log errors with context
- Include error details in results

**FR-5.3**: Progress Reporting
- Display progress during execution
- Show current test being processed
- Estimate completion time

### 6. Output Format and Storage

**FR-6.1**: Directory Structure
```
output/
└── run_2025-01-20_143052_openai_gpt-4o/
    ├── tests.yaml           # Copy of test configuration used
    ├── results.json         # Structured results
    └── metadata.json        # Run metadata
```

**FR-6.2**: Results JSON Format
```json
{
  "model": "openai/gpt-4o",
  "run_timestamp": "2025-01-20T14:30:52Z",
  "run_id": "run_2025-01-20_143052_openai_gpt-4o",
  "total_tests": 3,
  "successful_tests": 2,
  "failed_tests": 1,
  "total_duration_seconds": 45.2,
  "results": [
    {
      "title": "Summarise Shakespeare",
      "prompt": "Summarise Hamlet in 3 sentences.",
      "category": "summarisation",
      "response": "Hamlet is a tragedy about...",
      "status": "success",
      "duration_seconds": 2.1,
      "timestamp": "2025-01-20T14:30:54Z",
      "token_usage": {
        "prompt_tokens": 12,
        "completion_tokens": 45,
        "total_tokens": 57
      }
    },
    {
      "title": "Mathematical Reasoning",
      "prompt": "Solve 128 * 47 and explain your method.",
      "category": "mathematics",
      "response": null,
      "status": "error",
      "error": "API rate limit exceeded",
      "duration_seconds": 0,
      "timestamp": "2025-01-20T14:30:56Z"
    }
  ]
}
```

**FR-6.3**: Metadata JSON Format
```json
{
  "tool_version": "1.0.0",
  "python_version": "3.9.7",
  "platform": "darwin",
  "environment_variables": {
    "OPENAI_API_KEY": "***masked***"
  },
  "command_line": "praisonaibench --model openai/gpt-4o --tests custom_tests.yaml"
}
```

### 7. Python API (Stretch Goal)

**FR-7.1**: Programmatic Interface
```python
from praisonaibench import Bench

# Basic usage
bench = Bench(model="openai/gpt-4o", tests="tests.yaml")
results = bench.run()

# Advanced usage
bench = Bench(
    model="anthropic/claude-3-sonnet",
    tests="custom_tests.yaml",
    output_dir="./my_results/",
    concurrent=3
)
results = bench.run()
print(f"Completed {results.successful_tests}/{results.total_tests} tests")
```

## Non-Functional Requirements

### 1. Performance

**NFR-1.1**: Startup Time
- CLI should start within 2 seconds
- Package import should complete within 1 second

**NFR-1.2**: Memory Usage
- Base memory footprint under 100MB
- Efficient handling of large result sets

**NFR-1.3**: Concurrent Execution
- Support up to 10 concurrent requests (configurable)
- Respect provider rate limits

### 2. Reliability

**NFR-2.1**: Error Recovery
- Graceful handling of network failures
- Automatic retry with exponential backoff
- Continue execution despite individual test failures

**NFR-2.2**: Data Integrity
- Ensure all results are saved even on interruption
- Atomic writes for result files
- Backup partial results during long runs

### 3. Usability

**NFR-3.1**: Documentation
- Comprehensive README with examples
- CLI help text for all commands
- Error messages with actionable guidance

**NFR-3.2**: Cross-Platform Compatibility
- Support Windows, macOS, and Linux
- Handle path separators correctly
- Respect platform-specific conventions

### 4. Security

**NFR-4.1**: API Key Management
- Never log or save API keys
- Support environment variable configuration
- Mask sensitive information in outputs

**NFR-4.2**: Input Validation
- Validate YAML syntax before execution
- Sanitise file paths
- Prevent directory traversal attacks

### 5. Maintainability

**NFR-5.1**: Code Quality
- Type hints throughout codebase
- Comprehensive test coverage (>90%)
- Follow PEP 8 style guidelines

**NFR-5.2**: Extensibility
- Plugin architecture for new providers
- Configurable output formats
- Modular design for easy feature additions

## Technical Architecture

### Core Components

1. **CLI Interface** (`cli.py`)
   - Argument parsing with Click
   - Command validation and help

2. **Test Loader** (`loader.py`)
   - YAML parsing and validation
   - Test configuration management

3. **Execution Engine** (`executor.py`)
   - Model communication via PraisonAI Agents
   - Concurrent execution management
   - Error handling and retries

4. **Results Manager** (`results.py`)
   - Output formatting and serialisation
   - File system operations
   - Progress tracking

5. **Model Providers** (`providers/`)
   - Abstract base class for providers
   - Provider-specific implementations
   - Rate limiting and authentication

### Dependencies

- **Core**: `praisonaiagents>=1.0.0`, `pyyaml>=6.0`, `click>=8.0`
- **Development**: `pytest`, `black`, `mypy`, `pre-commit`
- **Optional**: Provider SDKs as needed

## Success Metrics

### Primary Metrics
- **Installation Success Rate**: >95% successful pip installs
- **First Run Success**: >90% of users complete first benchmark within 5 minutes
- **Command Completion**: >99% of valid commands complete successfully

### Secondary Metrics
- **GitHub Stars**: Target 1,000+ within 6 months
- **PyPI Downloads**: 10,000+ monthly downloads within 1 year
- **Community Contributions**: 20+ contributors within 1 year

### Quality Metrics
- **Test Coverage**: >90%
- **Documentation Coverage**: 100% of public APIs documented
- **Performance**: <5 seconds for 10-test benchmark

## Release Strategy

### Phase 1: MVP (v0.1.0)
- Core CLI functionality
- OpenAI and Anthropic support
- Basic YAML test format
- JSON output format

### Phase 2: Enhanced (v0.2.0)
- Additional model providers
- Concurrent execution
- Enhanced error handling
- Progress reporting

### Phase 3: Advanced (v0.3.0)
- Python API
- Plugin architecture
- CSV export
- Performance metrics (latency, tokens)

### Phase 4: Enterprise (v1.0.0)
- Multi-model comparison
- Advanced analytics
- CI/CD integration
- Enterprise features

## Risk Analysis

### Technical Risks
- **API Rate Limits**: Mitigated by exponential backoff and concurrent request management
- **Provider API Changes**: Mitigated by using PraisonAI Agents abstraction layer
- **Large Result Sets**: Mitigated by streaming writes and efficient memory management

### Business Risks
- **Competition**: Differentiate through simplicity and PraisonAI integration
- **Provider Costs**: Document usage costs and provide cost estimation features
- **Adoption**: Focus on developer experience and comprehensive documentation

## Appendix

### Example Usage Scenarios

**Scenario 1: Model Comparison**
```bash
# Compare different models on the same test suite
praisonaibench --model openai/gpt-4o --tests comparison_tests.yaml
praisonaibench --model anthropic/claude-3-sonnet --tests comparison_tests.yaml
praisonaibench --model google/gemini-pro --tests comparison_tests.yaml
```

**Scenario 2: CI/CD Integration**
```bash
# Automated testing in pipeline
praisonaibench --model $MODEL_UNDER_TEST --tests regression_tests.yaml --output ./ci_results/
```

**Scenario 3: Local Development**
```bash
# Quick local testing with Ollama
praisonaibench --model ollama/llama2 --tests dev_tests.yaml
```

### Sample Test Files

**Basic Tests** (`tests.yaml`):
```yaml
tests:
  - title: "Text Summarisation"
    prompt: "Summarise this article in 2 sentences: [article content]"
    category: "summarisation"
  
  - title: "Code Generation"
    prompt: "Write a Python function to calculate fibonacci numbers"
    category: "coding"
  
  - title: "Reasoning"
    prompt: "If all roses are flowers and some flowers fade quickly, can we conclude that some roses fade quickly?"
    category: "logic"
```

**Advanced Tests** (`advanced_tests.yaml`):
```yaml
tests:
  - title: "Complex Reasoning"
    prompt: "A train travels 120km in 2 hours, then 180km in 3 hours. What's the average speed?"
    category: "mathematics"
    expected: "60 km/h"
    timeout: 30
  
  - title: "Creative Writing"
    prompt: "Write a short story about AI and humans collaborating"
    category: "creativity"
    timeout: 60
```

This PRD provides a comprehensive foundation for building PraisonAI Bench as a robust, user-friendly LLM benchmarking tool that leverages the PraisonAI Agents framework for maximum compatibility and ease of use. Aim is to build benchmark framework, not agentic framework. So aim is to test various prompts against same model and compare results. 

# 📦 PraisonAI Agents Docs 

## 1. Install Package

```bash
pip install praisonaiagents
```

Optional (for tools like web search) - This is just an example on how to use tools with agents:

```bash
pip install praisonaiagents duckduckgo-search
```

## 2. Configure Environment

```bash
export OPENAI_API_KEY=your_openai_key
```

* Supports **OpenAI**, **Ollama**, **Anthropic**, **Groq**, **Google**, and other providers.
* For alternative models, see LiteLLM-compatible usage below.

---

## 3. Basic Agent Usage

### 🔹 Single Agent

```python
from praisonaiagents import Agent

agent = Agent(instructions="You are a helpful AI assistant")
print(agent.start("Write a movie script about a robot in Mars"))
```

---

## 4. Agents with Tools

```python
from praisonaiagents import Agent
from duckduckgo_search import DDGS

# 1. Define the tool
def internet_search_tool(query: str):
    results = []
    ddgs = DDGS()
    for result in ddgs.text(keywords=query, max_results=5):
        results.append({
            "title": result.get("title", ""),
            "url": result.get("href", ""),
            "snippet": result.get("body", "")
        })
    return results

# 2. Assign the tool to an agent
search_agent = Agent(
    instructions="Perform internet searches to collect relevant information.",
    tools=[internet_search_tool]  # <--- Tool assignment
)

# 3. Run Agent
print(search_agent.start("Search about AI job trends in 2025"))
```

---

## 5. LiteLLM Compatible Models

Install with extras:

```bash
pip install "praisonaiagents[llm]"
```

Use alternative model providers (via LiteLLM naming convention):

```python
from praisonaiagents import Agent

agent = Agent(
    instructions="You are a helpful assistant",
    llm="gemini/gemini-1.5-flash-8b",  # LiteLLM-compatible model name
)

print(agent.start("Why is the sky blue?"))
```

---

## 6. Run Script

```bash
python app.py
```

---

✅ This **one doc** includes:

* Install (with and without extras).
* Env setup.
* Single Agent.
* Multi-Agent.
* Agent + Tools.
* LiteLLM (other model providers).
* Running script.

