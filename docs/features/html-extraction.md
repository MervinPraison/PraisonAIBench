# HTML Extraction

Automatic HTML code extraction from LLM responses.

## Overview

When LLM responses contain HTML code blocks, PraisonAI Bench automatically extracts and saves them as `.html` files, organized by model.

## How It Works

```
┌─────────────────┐
│  LLM Response   │  Contains ```html ... ```
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Auto-Detection │  Detects HTML blocks
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Extraction     │  Extracts clean HTML
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Save to File   │  output/{model}/{test}.html
└─────────────────┘
```

## Supported Formats

PraisonAI Bench auto-detects HTML in multiple formats:

| Format | Example |
|--------|---------|
| Markdown-wrapped | ````html ... ```` |
| Truncated blocks | Incomplete responses |
| Raw HTML | Direct HTML content |

## Output Organization

HTML files are organized by model:

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

## Extract from Existing Results

Extract HTML from previously saved benchmark results:

```bash
# Extract HTML from existing benchmark results
praisonaibench --extract output/benchmark_results_20250829_160426.json

# Works with any benchmark results JSON file
praisonaibench --extract my_results.json
```

## Use Cases

Perfect for benchmarking:
- **Three.js Visualizations** - 3D graphics and animations
- **React Components** - UI component generation
- **Interactive Demos** - Web applications
- **Charts & Graphs** - Data visualization
- **Game Development** - Browser games
