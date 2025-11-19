# LLM-as-a-Judge Evaluation Criteria

## Overview

The LLM Judge uses **detailed, structured evaluation criteria** with a clear scoring rubric to provide objective, consistent code quality assessment.

---

## 🎯 Evaluation Criteria (Total: 100 points)

### 1. COMPLETENESS (25 points)

**What it evaluates:**
- Does the code fulfill the original request?
- Are all required features implemented?
- Is anything missing or incomplete?

**Examples:**
- ✅ **25 pts**: All features from prompt implemented perfectly
- ✅ **20 pts**: Most features present, minor omissions
- ⚠️ **15 pts**: Some key features missing
- ❌ **10 pts**: Many features incomplete
- ❌ **0 pts**: Barely addresses the request

---

### 2. CODE QUALITY (25 points)

**What it evaluates:**
- Clean, readable code structure?
- Proper HTML/CSS/JS organization?
- Good naming conventions?
- Appropriate use of libraries?

**Examples:**
- ✅ **25 pts**: Professional, clean, well-organized
- ✅ **20 pts**: Good structure, minor style issues
- ⚠️ **15 pts**: Acceptable but messy in places
- ❌ **10 pts**: Poor organization, hard to read
- ❌ **0 pts**: Chaotic, unreadable code

---

### 3. BEST PRACTICES (25 points)

**What it evaluates:**
- Follows HTML5/ES6+ standards?
- Proper error handling?
- Security considerations?
- Performance optimizations?

**Examples:**
- ✅ **25 pts**: Modern standards, secure, optimized
- ✅ **20 pts**: Good practices, minor issues
- ⚠️ **15 pts**: Some outdated patterns
- ❌ **10 pts**: Many poor practices
- ❌ **0 pts**: Ignores best practices entirely

---

### 4. FUNCTIONALITY (25 points)

**What it evaluates:**
- Code appears logically correct?
- Proper event handling?
- Good user experience?
- Appropriate comments/documentation?

**Examples:**
- ✅ **25 pts**: Logic sound, good UX, well-documented
- ✅ **20 pts**: Mostly correct, minor logic issues
- ⚠️ **15 pts**: Some logical problems
- ❌ **10 pts**: Multiple functional issues
- ❌ **0 pts**: Logic fundamentally broken

---

## 📊 Scoring Guide

### Score Ranges

| Score | Rating | Description |
|-------|--------|-------------|
| **90-100** | Excellent | Professional quality, all criteria met excellently |
| **80-89** | Good | High quality, minor improvements possible |
| **70-79** | Acceptable | Functional with some issues, meets basic standards |
| **60-69** | Fair | Multiple issues, needs significant work |
| **Below 60** | Poor | Significant problems, major rework needed |

### Pass/Fail Threshold

- **Pass**: Score ≥ 70 (Acceptable or better)
- **Fail**: Score < 70 (Fair or poor)

---

## 🔍 Example Evaluation

### Sample Code
```html
<!DOCTYPE html>
<html>
<head>
    <title>Rotating Cube</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>
    <script>
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer();
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);
        
        const geometry = new THREE.BoxGeometry();
        const material = new THREE.MeshBasicMaterial({color: 0x00ff00});
        const cube = new THREE.Mesh(geometry, material);
        scene.add(cube);
        
        camera.position.z = 5;
        
        function animate() {
            requestAnimationFrame(animate);
            cube.rotation.x += 0.01;
            cube.rotation.y += 0.01;
            renderer.render(scene, camera);
        }
        animate();
    </script>
</body>
</html>
```

### LLM Judge Evaluation

**Prompt**: "Create a rotating green cube using Three.js"

**Evaluation Result**:
```json
{
  "score": 85,
  "feedback": "Clean Three.js implementation with proper animation loop. Could add window resize handling and better error checking.",
  "strengths": "Correct Three.js setup, smooth animation, fulfills all requirements, clean code structure",
  "improvements": "Add window resize listener, error handling for WebGL support, consider using newer Three.js version"
}
```

**Breakdown**:
- **Completeness**: 25/25 - All features present (rotating cube, green color, Three.js)
- **Code Quality**: 22/25 - Clean and readable, minor improvements possible
- **Best Practices**: 20/25 - Good but could add error handling and responsiveness
- **Functionality**: 18/25 - Works well but lacks resize handling

**Total**: 85/100 (Good)

---

## 🎨 Structured Feedback

The LLM Judge provides three types of feedback:

### 1. Overall Feedback
Short, actionable summary (1-2 sentences)

**Example**: "Clean Three.js implementation with proper animation loop. Could add window resize handling and better error checking."

### 2. Strengths
What the code does well

**Example**: "Correct Three.js setup, smooth animation, fulfills all requirements, clean code structure"

### 3. Improvements
Specific suggestions for enhancement

**Example**: "Add window resize listener, error handling for WebGL support, consider using newer Three.js version"

---

## 🔧 Implementation Details

### Prompt Structure

The LLM Judge receives:
1. **Original Request** - What was asked for
2. **Code Sample** - First 2000 chars of generated code
3. **Evaluation Criteria** - Detailed scoring rubric (4 categories × 25 points)
4. **Scoring Guide** - Clear ranges and descriptions
5. **Response Format** - Structured JSON output

### Response Format

```json
{
  "score": 85,
  "feedback": "Short actionable summary",
  "strengths": "What was done well",
  "improvements": "What could be better"
}
```

---

## 📈 Combined Scoring

When used with functional validation, scores are combined:

**Overall Score** = (Functional × 70%) + (Quality × 30%)

**Example**:
- Functional Score: 90/100 (renders, no errors, fast)
- Quality Score: 85/100 (LLM judge)
- **Overall**: (90 × 0.7) + (85 × 0.3) = 63 + 25.5 = **88.5/100**

**Rationale**:
- **70% Functional** - Code must work (most important)
- **30% Quality** - Code should be good (important but secondary)

---

## ✅ Why This Approach Works

### 1. Objective Criteria
- Clear, measurable factors
- Consistent evaluation
- No arbitrary scoring

### 2. Comprehensive Coverage
- Completeness (does it work?)
- Quality (is it good code?)
- Best practices (is it professional?)
- Functionality (is it correct?)

### 3. Actionable Feedback
- Specific strengths identified
- Clear improvement suggestions
- Helps developers learn

### 4. Industry-Aligned
- Based on code review best practices
- Follows modern web standards
- Considers real-world requirements

---

## 🎓 Comparison: Before vs After

### Before (Simple Prompt)
```
"Rate this HTML/JS code quality (0-100)"
```

**Problems**:
- ❌ No clear criteria
- ❌ Inconsistent scoring
- ❌ Vague feedback
- ❌ Hard to reproduce

### After (Detailed Criteria)
```
"Evaluate using 4 criteria (25 pts each):
1. Completeness - fulfills request?
2. Code Quality - clean, readable?
3. Best Practices - modern standards?
4. Functionality - logically correct?"
```

**Benefits**:
- ✅ Clear, objective criteria
- ✅ Consistent scoring
- ✅ Specific feedback
- ✅ Reproducible results

---

## 🔍 Example Scenarios

### Scenario 1: Perfect Implementation

**Code**: Professional Three.js app with all features, error handling, responsive design

**Score**: 95/100
- Completeness: 25/25
- Code Quality: 25/25
- Best Practices: 23/25 (minor optimization possible)
- Functionality: 22/25 (excellent but room for docs)

### Scenario 2: Good but Incomplete

**Code**: Working Three.js cube but missing requested lighting

**Score**: 72/100
- Completeness: 18/25 (missing feature)
- Code Quality: 20/25 (good structure)
- Best Practices: 17/25 (acceptable)
- Functionality: 17/25 (works but incomplete)

### Scenario 3: Poor Quality

**Code**: Messy code with errors, doesn't fully work

**Score**: 45/100
- Completeness: 10/25 (barely works)
- Code Quality: 8/25 (very messy)
- Best Practices: 12/25 (poor practices)
- Functionality: 15/25 (multiple issues)

---

## 📚 References

This evaluation approach is based on:

1. **Code Review Best Practices**
   - Google's Code Review Guidelines
   - Microsoft's Code Review Standards

2. **LLM Evaluation Research**
   - Sebastian Raschka's LLM Evaluation Guide
   - LLM-as-a-Judge papers (2024)

3. **Web Development Standards**
   - HTML5/ES6+ specifications
   - MDN Web Docs best practices
   - Three.js documentation

4. **Industry Benchmarks**
   - HumanEval code generation benchmark
   - CodeBERT evaluation methodology

---

## 🎯 Summary

The LLM Judge provides:

✅ **Objective** - 4 clear criteria, 25 points each
✅ **Comprehensive** - Covers completeness, quality, practices, functionality
✅ **Actionable** - Specific strengths and improvements
✅ **Consistent** - Clear scoring guide, reproducible
✅ **Professional** - Based on industry standards

**Not random** - Every score is backed by detailed criteria and clear reasoning.

---

*This evaluation system ensures fair, consistent, and helpful code quality assessment.*
