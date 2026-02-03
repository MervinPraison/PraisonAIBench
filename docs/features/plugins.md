# Plugin System

Extensible evaluators for any language or task.

## Overview

The plugin system allows you to create custom evaluators for Python, TypeScript, Go, or any other language/task type. Each plugin is just one file.

## Creating a Plugin

### 1. Create Evaluator Class

```python
# my_evaluator.py
from praisonaibench import BaseEvaluator

class MyEvaluator(BaseEvaluator):
    def get_language(self):
        return 'mylang'  # e.g., 'python', 'typescript', 'go'
    
    def evaluate(self, code, test_name, prompt, expected=None):
        # Your evaluation logic here
        return {
            'score': 85,      # 0-100
            'passed': True,   # score >= 70
            'feedback': [{'level': 'success', 'message': '✅ Works!'}],
            'details': {}
        }
```

### 2. Configure Package

```toml
# pyproject.toml
[project]
name = "praisonaibench-mylang"
version = "0.1.0"
dependencies = ["praisonaibench>=0.1.0"]

[project.entry-points."praisonaibench.evaluators"]
mylang = "my_evaluator:MyEvaluator"
```

### 3. Install Plugin

```bash
pip install -e .
# or
uv pip install -e .
```

## Using Plugins

Specify the language in your test suite:

```yaml
# tests.yaml
tests:
  - name: "python_test"
    language: "python"  # Auto-discovered
    prompt: "Write Python hello world"
    expected: "Hello World"
```

Run the suite:

```bash
praisonaibench --suite tests.yaml
```

## Plugin Features

| Feature | Description |
|---------|-------------|
| ✅ One file | ~50 lines per plugin |
| ✅ Auto-discovery | No config needed |
| ✅ Backwards compatible | HTML evaluation unchanged |
| ✅ Language detection | Auto-detects from code blocks |
| ✅ Any task | Programming, text, translation, etc. |

## Example: Python Evaluator

```python
# examples/plugins/python_evaluator.py
from praisonaibench import BaseEvaluator
import subprocess
import tempfile
import os

class PythonEvaluator(BaseEvaluator):
    def get_language(self):
        return 'python'
    
    def evaluate(self, code, test_name, prompt, expected=None):
        # Write code to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = f.name
        
        try:
            # Run the code
            result = subprocess.run(
                ['python', temp_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Check output
            output = result.stdout.strip()
            score = 100 if expected and expected in output else 70
            
            return {
                'score': score,
                'passed': score >= 70,
                'feedback': [{'level': 'success', 'message': f'Output: {output}'}],
                'details': {'stdout': result.stdout, 'stderr': result.stderr}
            }
        finally:
            os.unlink(temp_path)
```

## Language Detection

Plugins auto-detect language from:
1. Explicit `language` field in test
2. Code block language identifier (```python)
3. File extension patterns
