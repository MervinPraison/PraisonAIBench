# PraisonAI Bench - Agent Instructions

## Project Structure
```
PraisonAIBench/
├── pyproject.toml        # Version managed by hatch
├── src/praisonaibench/
│   └── version.py        # Version source
├── tests.yaml
└── docs/
```

## Version: `src/praisonaibench/version.py`

## CLI: `praisonaibench`

## Commands
```bash
praisonaibench run tests.yaml
praisonaibench --help
```

## Development
```bash
uv pip install -e ".[dev]"
pytest
```
