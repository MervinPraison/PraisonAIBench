# Plugin System

PraisonAI Bench now supports **plugin-based evaluators** for any programming language!

## 🎯 Overview

Volunteers can create evaluators for **any language** (Python, TypeScript, Go, Rust, etc.) in just **one .py file**.

## 🚀 Quick Start

### For Plugin Creators

1. **Create your evaluator** (one file):

```python
from praisonaibench import BaseEvaluator

class MyEvaluator(BaseEvaluator):
    def get_language(self):
        return 'mylang'  # e.g., 'python', 'rust', 'go'
    
    def evaluate(self, code, test_name, prompt, expected=None):
        # Your evaluation logic
        return {
            'score': 85,      # 0-100
            'passed': True,   # score >= 70
            'feedback': [{'level': 'success', 'message': '✅ Works!'}],
            'details': {}
        }
```

2. **Create pyproject.toml**:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "praisonaibench-mylang"
version = "0.1.0"
dependencies = ["praisonaibench>=0.1.0"]

[project.entry-points."praisonaibench.evaluators"]
mylang = "my_evaluator:MyEvaluator"
```

3. **Install**: `pip install -e .` or `uv pip install -e .`

Done! Your plugin is now active.

### For Users

1. **Install plugin**: `pip install praisonaibench-python`
2. **Use in tests.yaml**:

```yaml
tests:
  - name: "python_test"
    language: "python"  # Plugin auto-discovered
    prompt: "Write Python hello world"
    expected: "Hello World"
```

3. **Run**: `praisonaibench --suite tests.yaml`

## 📁 Implementation Files

**Core System** (created):
- `src/praisonaibench/base_evaluator.py` - Base class for plugins
- `src/praisonaibench/plugin_manager.py` - Plugin discovery & loading
- `src/praisonaibench/evaluators/html_evaluator.py` - HTML adapter (backwards compatible)
- Modified: `src/praisonaibench/bench.py` - Language detection & plugin integration
- Modified: `src/praisonaibench/__init__.py` - Export BaseEvaluator

**Examples**:
- `examples/plugins/python_evaluator.py` - Complete Python plugin example
- `examples/plugins/setup.py.example` - Setup file template

## ✅ Testing

Run the test script:

```bash
python test_plugin_system.py
```

## 🎯 Key Features

- **One file per plugin** - Simple to create
- **Auto-discovery** - No config needed
- **Backwards compatible** - HTML evaluation unchanged
- **Language detection** - Auto-detects from code blocks
- **Zero maintenance** - Plugins maintained by community

## 📚 Example Plugin

See `examples/plugins/python_evaluator.py` for a complete working example that:
- Checks Python syntax
- Executes code safely
- Compares output with expected
- Returns structured evaluation

## 🔧 Architecture

```
Bench → PluginManager → {html: HTMLEvaluator, python: PythonEvaluator, ...}
```

- **PluginManager**: Discovers & loads plugins via entry points
- **BaseEvaluator**: Interface all plugins implement
- **Language detection**: Auto-detects from ````lang` or config
- **Backwards compatible**: HTML evaluation works exactly as before

## 📖 API

### BaseEvaluator (Plugin Interface)

```python
class BaseEvaluator(ABC):
    @abstractmethod
    def get_language(self) -> str:
        """Return language identifier (lowercase)"""
        pass
    
    @abstractmethod
    def evaluate(self, code, test_name, prompt, expected=None) -> dict:
        """
        Evaluate code and return:
        {
            'score': 0-100,
            'passed': bool,
            'feedback': [...],
            'details': {}
        }
        """
        pass
```

## 🎉 Benefits

- **For Volunteers**: One file (~50 lines), 2 methods, 45 minutes
- **For Users**: One command install, zero config
- **For Core**: Unlimited languages, zero maintenance

## 📝 Test Suite Format

```yaml
tests:
  - name: "test_python"
    language: "python"  # Explicit
    prompt: "Write Python code"
  
  - name: "test_auto"
    # Auto-detects from ```python in response
    prompt: "Write Python code"
```

## 🚀 Status

✅ **Implemented & Tested**
- Plugin manager with auto-discovery
- HTML evaluator (backwards compatible)
- Language detection (code blocks + explicit)
- All tests passing

**Ready for community plugins!**
