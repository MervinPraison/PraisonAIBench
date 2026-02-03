# PraisonAI Bench

Simple LLM Benchmarking Tool using PraisonAI Agents.

```mermaid
graph LR
    A[📄 YAML Tests] --> B[🔌 PraisonAI]
    B --> C[📊 Benchmark Results]
    
    style A fill:#14B8A6,stroke:#7C90A0,color:#fff
    style B fill:#6366F1,stroke:#7C90A0,color:#fff
    style C fill:#F59E0B,stroke:#7C90A0,color:#fff
```

## Quick Start

```bash
pip install praisonaibench
praisonaibench run tests.yaml
```

## Features

| Feature | Description |
|---------|-------------|
| 📊 YAML Tests | Define tests in YAML |
| 🔌 Plugin System | Extensible plugins |
| 📈 Reports | Detailed benchmark reports |

## Next Steps

- [Installation](getting-started/installation.md)
- [Quick Start](getting-started/quick-start.md)
