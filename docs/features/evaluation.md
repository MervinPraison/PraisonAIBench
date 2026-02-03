# Evaluation System

Research-backed hybrid evaluation providing comprehensive quality assessment.

## Overview

PraisonAI Bench uses a multi-component evaluation system that combines static validation, functional testing, and AI-powered quality assessment.

## Evaluation Components

| Component | What It Does | Score Weight |
|-----------|--------------|--------------| 
| **📝 HTML Validation** | Static structure validation, DOCTYPE, required tags | 15% |
| **🌐 Functional** | Browser rendering, console errors, render time | 40% |
| **🎯 Expected Result** | Objective comparison (optional, for factual tasks) | 20%* |
| **🎨 Quality (LLM)** | Code quality, completeness, best practices | 25% |
| **📊 Overall** | Combined score (0-100) with pass/fail (≥70) | 100% |

*When `expected` field is not provided, weights are automatically normalized (HTML: 18.75%, Functional: 50%, LLM: 31.25%)

## Example Output

**With Expected Result:**
```
HTML Validation: 90/100 ✅ Valid structure
Functional: 85/100 (renders ✅, 1 error, <1s)
Expected: 95/100 (95% similarity with expected result)
Quality: 80/100 (good structure, minor issues)
Overall: 87/100 ✅ PASSED
```

**Without Expected Result:**
```
HTML Validation: 90/100 ✅ Valid structure
Functional: 85/100 (renders ✅, 1 error, <1s)
Expected: N/A (not provided)
Quality: 80/100 (good structure, minor issues)
Overall: 85/100 ✅ PASSED
```

## HTML Validation

Checks for:
- Valid DOCTYPE declaration
- Required HTML structure
- Proper tag nesting
- Semantic HTML usage

## Functional Testing

Browser-based testing that checks:
- Page renders without errors
- JavaScript executes correctly
- Console errors detected
- Render time measured

## LLM Quality Assessment

AI-powered code review evaluating:
- Code quality and cleanliness
- Feature completeness
- Best practices adherence
- Error handling

## Pass/Fail Threshold

- **Pass**: Overall score ≥ 70
- **Fail**: Overall score < 70

## Retry Logic

Each test includes automatic retry:
- Default: 3 attempts
- Configurable via settings
- Best result is used
