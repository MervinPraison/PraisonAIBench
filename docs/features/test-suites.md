# Test Suites

Run multiple tests from a YAML configuration file for comprehensive LLM benchmarking.

## Overview

Test suites allow you to define a collection of tests in a YAML file and run them all at once, with parallel execution support and comprehensive reporting.

## Creating a Test Suite

Create a YAML file with your tests:

```yaml
# tests.yaml
tests:
  - name: "math_test"
    prompt: "What is 15 * 23?"
    expected: "345"  # Optional: for objective comparison
  
  - name: "python_test"
    language: "python"  # Use plugin evaluator
    prompt: "Write Python factorial function"
    expected: "120"
  
  - name: "creative_test"
    prompt: "Write a short story about a robot"
    # No expected field - subjective task
  
  - name: "model_specific_test"
    prompt: "Explain quantum physics"
    model: "gpt-4o"
```

## Running Suites

### Basic Usage

```bash
# Run entire test suite
praisonaibench --suite tests.yaml

# Run specific test from suite
praisonaibench --suite tests.yaml --test-name "rotating_cube_simulation"

# Run suite with specific model (overrides individual test models)
praisonaibench --suite tests.yaml --model xai/grok-code-fast-1
```

### Parallel Execution

```bash
# Run tests in parallel (3 concurrent workers)
praisonaibench --suite tests.yaml --concurrent 3
```

## Global Configuration

Set global LLM configuration that applies to all tests:

```yaml
# Global LLM configuration
config:
  max_tokens: 4000
  temperature: 0.7
  top_p: 0.9
  frequency_penalty: 0.0
  presence_penalty: 0.0

tests:
  - name: "creative_writing"
    prompt: "Write a detailed sci-fi story"
    model: "gpt-4o"
```

## Using the Expected Field

| Use Case | Include Expected? |
|----------|-------------------|
| Factual questions | ✅ Yes |
| Math problems | ✅ Yes |
| Code output | ✅ Yes |
| Deterministic tasks | ✅ Yes |
| Creative tasks | ❌ No |
| Open-ended questions | ❌ No |
| Visual/interactive content | ❌ No |

**Scoring Impact:**
- When provided: Adds 20% objective scoring based on similarity
- When omitted: Weights automatically normalize (no penalty)
