# PraisonAI Bench

🚀 **A simple, powerful LLM benchmarking tool built with PraisonAI Agents**

Benchmark any LiteLLM-compatible model with automatic HTML extraction, model-specific output organization, and flexible test suite management.

## ✨ Key Features

- 🎯 **Any LLM Model** - OpenAI, Anthropic, Google, XAI, local models via LiteLLM
- 🔄 **Single Agent Design** - Your prompt becomes the instruction (no complex configs)
- 💾 **Auto HTML Extraction** - Automatically saves HTML code from responses
- 📁 **Smart Organization** - Model-specific output folders (`output/gpt-4o/`, `output/xai/grok-code-fast-1/`)
- 🎛️ **Flexible Testing** - Run single tests, full suites, or filter specific tests
- ⚡ **Modern Tooling** - Built with `pyproject.toml` and `uv` package manager
- 📊 **Comprehensive Results** - JSON metrics with timing, success rates, and metadata

## 🚀 Quick Start

### 1. Install with uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/MervinPraison/praisonaibench
cd praisonaibench

# Install with uv
uv sync

# Or install in development mode
uv pip install -e .
```

### 2. Alternative: Install with pip

```bash
pip install -e .
```

### 3. Set Your API Keys

```bash
# OpenAI
export OPENAI_API_KEY=your_openai_key

# XAI (Grok)
export XAI_API_KEY=your_xai_key

# Anthropic
export ANTHROPIC_API_KEY=your_anthropic_key

# Google
export GOOGLE_API_KEY=your_google_key
```

### 4. Run Your First Benchmark

```python
from praisonaibench import Bench

# Create benchmark suite
bench = Bench()

# Run a simple test
result = bench.run_single_test("What is 2+2?")
print(result['response'])

# Run with specific model
result = bench.run_single_test(
    "Create a rotating cube HTML file", 
    model="xai/grok-code-fast-1"
)

# Get summary
summary = bench.get_summary()
print(summary)
```

## 📁 Project Structure

```
praisonaibench/
├── pyproject.toml           # Modern Python packaging
├── src/praisonaibench/      # Source code
│   ├── __init__.py          # Main imports
│   ├── bench.py             # Core benchmarking engine
│   ├── agent.py             # LLM agent wrapper
│   ├── cli.py               # Command line interface
│   └── version.py           # Version info
├── examples/                # Example configurations
│   ├── threejs_simulation_suite.yaml
│   └── config_example.yaml
└── output/                  # Generated results
    ├── gpt-4o/             # Model-specific HTML files
    ├── xai/grok-code-fast-1/
    └── benchmark_results_*.json
```

## 💻 CLI Usage

### Basic Commands

```bash
# Single test with default model
praisonaibench --test "Explain quantum computing"

# Single test with specific model
praisonaibench --test "Write a poem" --model gpt-4o

# Use any LiteLLM-compatible model
praisonaibench --test "Create HTML" --model xai/grok-code-fast-1
praisonaibench --test "Write code" --model gemini/gemini-1.5-flash-8b
praisonaibench --test "Analyze data" --model claude-3-sonnet-20240229
```

### Test Suites

```bash
# Run entire test suite
praisonaibench --suite examples/threejs_simulation_suite.yaml

# Run specific test from suite
praisonaibench --suite examples/threejs_simulation_suite.yaml --test-name "rotating_cube_simulation"

# Run suite with specific model (overrides individual test models)
praisonaibench --suite tests.yaml --model xai/grok-code-fast-1
```

### Cross-Model Comparison

```bash
# Compare across multiple models
praisonaibench --cross-model "Write a poem" --models gpt-4o,gpt-3.5-turbo,xai/grok-code-fast-1
```

### Extract HTML from Results

```bash
# Extract HTML from existing benchmark results
praisonaibench --extract output/benchmark_results_20250829_160426.json
# → Processes JSON file and saves any HTML content to .html files

# Works with any benchmark results JSON file
praisonaibench --extract my_results.json
```

### HTML Generation Examples

```bash
# Generate Three.js simulation (auto-saves HTML)
praisonaibench --test "Create a rotating cube HTML with Three.js" --model gpt-4o
# → Saves to: output/gpt-4o/test_cube.html

# Run Three.js test suite
praisonaibench --suite examples/threejs_simulation_suite.yaml --model xai/grok-code-fast-1
# → Saves to: output/xai/grok-code-fast-1/rotating_cube_simulation.html
```

## 📋 Test Suite Format

### Basic Test Suite (`tests.yaml`)

```yaml
tests:
  - name: "math_test"
    prompt: "What is 15 * 23?"
  
  - name: "creative_test"
    prompt: "Write a short story about a robot"
  
  - name: "model_specific_test"
    prompt: "Explain quantum physics"
    model: "gpt-4o"
```

### Advanced Test Suite with Full Config Support

```yaml
# Global LLM configuration (applies to all tests)
config:
  max_tokens: 4000
  temperature: 0.7
  top_p: 0.9
  frequency_penalty: 0.0
  presence_penalty: 0.0
  # Any LiteLLM-compatible parameter is supported!

tests:
  - name: "creative_writing"
    prompt: "Write a detailed sci-fi story"
    model: "gpt-4o"
  
  - name: "code_generation"
    prompt: "Create a Python web scraper"
    model: "xai/grok-code-fast-1"
```

### Three.js HTML Generation Suite

```yaml
# examples/threejs_simulation_suite.yaml
tests:
  - name: "rotating_cube_simulation"
    prompt: |
      Create a complete HTML file with Three.js that displays a rotating 3D cube.
      The cube should have different colored faces, rotate continuously, and include proper lighting.
      The HTML file should be self-contained with Three.js loaded from CDN.
      Include camera controls for user interaction.
      Save the output as 'rotating_cube.html'.
    
  - name: "particle_system"
    prompt: |
      Create an HTML file with Three.js showing an animated particle system.
      Include 1000+ particles with random colors, movement, and physics.
      Add mouse interaction to influence particle behavior.
      
  - name: "terrain_simulation"
    prompt: |
      Create a Three.js HTML file with a procedurally generated terrain landscape.
      Include realistic textures, lighting, and a first-person camera.
      Add fog effects and animated elements.
      
  - name: "solar_system"
    prompt: |
      Create a Three.js solar system simulation in HTML.
      Include the sun, planets with realistic orbits, textures, and lighting.
      Add controls to speed up/slow down time.
```

## 🔧 Configuration

### Basic Configuration (`config.yaml`)

```yaml
# Default model (can be overridden per test)
default_model: "gpt-4o"

# Output settings
output_format: "json"
save_results: true
output_dir: "output"

# Performance settings
max_retries: 3
timeout: 60
```

### Supported Models

PraisonAI Bench supports **any LiteLLM-compatible model**:

```yaml
# OpenAI Models
- gpt-4o
- gpt-4o-mini
- gpt-3.5-turbo

# Anthropic Models
- claude-3-opus-20240229
- claude-3-sonnet-20240229
- claude-3-haiku-20240307

# Google Models
- gemini/gemini-1.5-pro
- gemini/gemini-1.5-flash
- gemini/gemini-1.5-flash-8b

# XAI Models
- xai/grok-beta
- xai/grok-code-fast-1

# Local Models (via LM Studio, Ollama, etc.)
- ollama/llama2
- openai/gpt-3.5-turbo  # with OPENAI_API_BASE set
```

## 📊 Results & Output

### Automatic HTML Extraction

When LLM responses contain HTML code blocks, they're automatically extracted and saved:

```
output/
├── gpt-4o/
│   ├── rotating_cube_simulation.html
│   └── particle_system.html
├── xai/
│   └── grok-code-fast-1/
│       ├── terrain_simulation.html
│       └── solar_system.html
└── benchmark_results_20250829_160426.json
```

### JSON Results Format

```json
[
  {
    "test_name": "rotating_cube_simulation",
    "prompt": "Create a complete HTML file with Three.js...",
    "response": "<!DOCTYPE html>\n<html>\n...",
    "model": "xai/grok-code-fast-1",
    "agent_name": "BenchAgent",
    "execution_time": 8.24,
    "status": "success",
    "timestamp": "2025-08-29 16:04:26"
  }
]
```

### Summary Statistics

```bash
📊 Summary:
   Total tests: 4
   Success rate: 100.0%
   Average time: 12.34s
Results saved to: output/benchmark_results_20250829_160426.json
```

## 🎯 Advanced Features

### 🔄 **Universal Model Support**
- Works with **any LiteLLM-compatible model**
- No hardcoded model restrictions
- Automatic API key detection

### 💾 **Smart HTML Handling**
- Auto-detects HTML in multiple formats:
  - Markdown-wrapped HTML (```html...```)
  - Truncated HTML blocks (incomplete responses)
  - Raw HTML content (direct HTML responses)
- Extracts and saves as `.html` files automatically
- Organizes by model in separate folders
- Extract HTML from existing benchmark results with `--extract`
- Perfect for Three.js, React, or any web development benchmarks

### 🎛️ **Flexible Test Management**
- Run entire suites or filter specific tests
- Override models per test or globally
- Cross-model comparisons with detailed metrics

### ⚡ **Modern Development**
- Built with `pyproject.toml` (no legacy `setup.py`)
- Optimized for `uv` package manager
- Fast dependency resolution and installation

### 🏗️ **Simple Architecture**
- **Single Agent Design** - Your prompt becomes the instruction
- **No Complex Configs** - Just write your test prompts
- **Minimal Dependencies** - Only what you need

## 🚀 Use Cases

### Web Development Benchmarking
```bash
# Test HTML/CSS/JS generation across models
praisonaibench --suite web_dev_suite.yaml --model gpt-4o
```

### Code Generation Comparison
```bash
# Compare coding abilities
praisonaibench --cross-model "Write a Python web scraper" --models gpt-4o,claude-3-sonnet-20240229,xai/grok-code-fast-1
```

### Creative Content Testing
```bash
# Test creative writing
praisonaibench --test "Write a sci-fi short story" --model gemini/gemini-1.5-pro
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Install dependencies: `uv sync`
4. Make your changes
5. Run tests: `uv run pytest`
6. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

---

**Perfect for developers who need powerful, flexible LLM benchmarking with zero complexity!** 🚀
