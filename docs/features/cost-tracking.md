# Cost & Token Tracking

Automatic token usage and cost calculation for all LLM API calls.

## Overview

PraisonAI Bench automatically tracks token usage and calculates costs for all supported models, giving you full visibility into your benchmarking expenses.

## Per-Test Cost Tracking

Each test shows its individual cost:

```
Running test: rotating_cube_simulation
✅ PASSED (87/100)
💰 Cost: $0.002400 (1250 tokens)
```

## Summary Cost Report

After running a test suite, see cumulative costs:

```
📊 Summary:
   Total tests: 4
   Success rate: 100.0%
   Average time: 8.42s

💰 Cost Summary:
   Total tokens: 5,420
   Total cost: $0.0124

   By model:
     gpt-4o: $0.0124 (5,420 tokens)
```

## Supported Models

Accurate pricing for major providers:

| Provider | Models | Pricing |
|----------|--------|---------|
| OpenAI | GPT-4o, GPT-4, GPT-3.5, O1 | ✅ |
| Anthropic | Claude 3 family | ✅ |
| Google | Gemini 1.5 family | ✅ |
| XAI | Grok models | ✅ |
| Groq | Optimized models | ✅ |

## Token Extraction

Token usage is extracted from:
1. **API Response** - When available in response metadata
2. **Text Estimation** - Fallback based on text length

## Pricing Updates

Costs are calculated using official provider pricing, updated regularly.

## Cost by Model Breakdown

When using multiple models, see costs per model:

```
💰 Cost Summary:
   Total tokens: 12,450
   Total cost: $0.0325

   By model:
     gpt-4o: $0.0200 (4,000 tokens)
     claude-3-sonnet: $0.0075 (5,000 tokens)
     xai/grok-code-fast-1: $0.0050 (3,450 tokens)
```

## Budget Planning

Use cost tracking to:
- Estimate benchmark expenses before running
- Compare cost efficiency across models
- Set budget limits for test suites
- Optimize prompts for cost reduction
