# Automated Evaluation System

PraisonAI Bench now includes a comprehensive automated evaluation system that assesses response quality, correctness, and adherence to expected results.

## Features

### ✅ **Expected Result Comparison**
- Compares LLM responses against expected results using similarity metrics
- Calculates similarity scores using sequence matching
- Identifies keyword presence for partial matching
- Supports both exact and fuzzy matching

### ✅ **HTML/JavaScript Code Validation**
- Validates HTML document structure
- Checks for required elements (DOCTYPE, head, body, title)
- Analyzes JavaScript code quality
- Detects syntax errors and mismatched tags
- Scores based on best practices

### ✅ **Quality Assessment**
- Evaluates response completeness
- Checks for truncation
- Analyzes response structure
- Measures appropriate length

### ✅ **Comprehensive Scoring**
- Individual scores for each evaluation metric
- Overall weighted score
- Pass/fail status
- Detailed feedback messages

## Usage

### Enable/Disable Evaluation

Evaluation is **enabled by default**. To disable:

```bash
# Disable evaluation
praisonaibench --suite tests.yaml --no-eval
```

### Python API

```python
from praisonaibench import Bench

# With evaluation (default)
bench = Bench(enable_evaluation=True)

# Without evaluation
bench = Bench(enable_evaluation=False)

# Run tests
result = bench.run_single_test("What is 2+2?")

# Check evaluation results
if 'evaluation' in result:
    print(f"Score: {result['evaluation']['overall_score']}%")
    print(f"Passed: {result['evaluation']['overall_passed']}")
```

## Test Configuration with Expected Results

Add `expected` field to your test YAML files:

```yaml
tests:
  - name: "math_test"
    prompt: "What is 15 * 23?"
    expected: "345"
  
  - name: "capital_test"
    prompt: "What is the capital of France?"
    expected: "Paris"
  
  - name: "code_generation"
    prompt: "Create an HTML page with a red heading"
    # HTML tests are automatically validated for structure and correctness
```

## Evaluation Results

### Console Output

```
📊 Evaluation Results for math_test:
   Overall Score: 95.5%
   Status: ✅ PASSED

   Expected Result:
     - Similarity: 98.0%
     - Keyword Match: 100.0%

   Quality:
     - Response Length: 85.0%
     - Completeness: 100.0%
     - Structure: 75.0%
```

### JSON Output

Results are saved to JSON with evaluation data:

```json
{
  "test_name": "math_test",
  "prompt": "What is 15 * 23?",
  "response": "345",
  "status": "success",
  "execution_time": 1.23,
  "evaluation": {
    "evaluated_at": "2025-11-11T10:30:00",
    "overall_passed": true,
    "overall_score": 95.5,
    "evaluations": {
      "expected_result": {
        "passed": true,
        "overall_score": 99.0,
        "scores": {
          "similarity": {
            "value": 100,
            "max": 100,
            "percentage": 100.0
          },
          "keyword_match": {
            "value": 100,
            "max": 100,
            "percentage": 100.0
          }
        },
        "feedback": [
          {
            "message": "✅ Exact match with expected result",
            "severity": "success"
          }
        ],
        "metrics": {
          "exact_match": true,
          "keywords_found": "1/1"
        }
      }
    }
  }
}
```

## Evaluation Metrics

### 1. Expected Result Evaluator

**Metrics:**
- **Similarity Score** (0-100%): Sequence matching between response and expected
- **Keyword Match** (0-100%): Percentage of important keywords found
- **Exact Match**: Boolean indicating perfect match

**Pass Criteria:**
- Similarity > 80%: High similarity (Pass)
- Similarity 50-80%: Moderate similarity (Warning)
- Similarity < 50%: Low similarity (Fail)

### 2. HTML Code Evaluator

**Metrics:**
- **HTML Structure** (0-100%): DOCTYPE, html, head, body, title tags
- **Required Elements** (0-100%): Proper closing tags, meta charset
- **JavaScript Quality** (0-100%): Code quality, modern practices
- **Best Practices** (0-100%): Semantic HTML, CDN usage, avoiding inline styles

**Pass Criteria:**
- Overall score ≥ 60%: Pass
- Overall score < 60%: Fail

### 3. Quality Evaluator

**Metrics:**
- **Response Length** (0-100%): Appropriate length for the query
- **Completeness** (0-100%): Response appears complete
- **Structure** (0-100%): Well-organized with paragraphs, lists, etc.

**Pass Criteria:**
- Not truncated
- Completeness score ≥ 50%

## Summary Statistics

The benchmark summary includes evaluation metrics:

```
📊 Summary:
   Total tests: 10
   Success rate: 100.0%
   Average time: 3.45s

📋 Evaluation Summary:
   Evaluated tests: 10
   Average score: 87.5%
   Pass rate: 90.0%
   Passed: 9 | Failed: 1
```

## Advanced Usage

### Custom Evaluators

You can create custom evaluators by extending the `BaseEvaluator` class:

```python
from praisonaibench.evaluator import BaseEvaluator, EvaluationResult

class CustomEvaluator(BaseEvaluator):
    def evaluate(self, response: str, test_config: dict) -> EvaluationResult:
        result = EvaluationResult()
        
        # Your custom evaluation logic
        if "important_keyword" in response.lower():
            result.add_score("keyword_check", 100, 100)
            result.add_feedback("✅ Keyword found", "success")
        else:
            result.add_score("keyword_check", 0, 100)
            result.add_feedback("❌ Keyword missing", "error")
            result.set_passed(False)
        
        return result
```

### Using Individual Evaluators

```python
from praisonaibench import (
    ExpectedResultEvaluator,
    HTMLCodeEvaluator,
    QualityEvaluator
)

# Use specific evaluators
expected_eval = ExpectedResultEvaluator()
result = expected_eval.evaluate(
    response="Paris",
    test_config={"expected": "Paris"}
)

print(f"Score: {result.get_overall_score()}%")
print(f"Passed: {result.passed}")
```

## Examples

### Example 1: Math Test with Expected Result

```bash
# Create test file
cat > math_tests.yaml << EOF
tests:
  - name: "multiplication"
    prompt: "What is 12 * 8?"
    expected: "96"
  
  - name: "division"
    prompt: "What is 144 / 12?"
    expected: "12"
EOF

# Run with evaluation
praisonaibench --suite math_tests.yaml
```

### Example 2: HTML Code Generation

```bash
# Create test file
cat > html_tests.yaml << EOF
tests:
  - name: "simple_page"
    prompt: |
      Create a complete HTML5 page with:
      - Proper DOCTYPE
      - A title "My Page"
      - A heading "Hello World"
      - A paragraph with some text
      - Include meta charset UTF-8
EOF

# Run and see HTML validation results
praisonaibench --suite html_tests.yaml
```

### Example 3: Disable Evaluation for Speed

```bash
# Run without evaluation for faster benchmarking
praisonaibench --suite large_suite.yaml --no-eval
```

## Best Practices

1. **Use Expected Results**: Always provide `expected` field for factual questions
2. **Clear Prompts**: Write specific prompts for better evaluation
3. **HTML Tests**: Let the system automatically validate HTML structure
4. **Review Scores**: Check evaluation feedback to improve prompts
5. **Threshold Setting**: Adjust pass/fail thresholds based on use case

## Limitations

- **Expected result matching**: Works best with factual, short answers
- **HTML validation**: Basic syntax checking, not browser compatibility
- **JavaScript validation**: Static analysis only, no runtime testing
- **Semantic understanding**: Limited to similarity and keyword matching

## Future Enhancements

Planned features:
- [ ] Custom scoring weights
- [ ] Configurable pass/fail thresholds
- [ ] More sophisticated code execution testing
- [ ] Semantic similarity using embeddings
- [ ] Integration with automated testing frameworks
- [ ] HTML rendering and screenshot comparison
- [ ] JavaScript runtime validation

## Troubleshooting

### Evaluation Not Running

```bash
# Check if evaluation is enabled
praisonaibench --suite tests.yaml
# Should show "📊 Automated evaluation: ENABLED"

# If disabled, remove --no-eval flag
```

### Low Scores Despite Good Responses

- Check that `expected` results are realistic
- Review the similarity threshold (50-80-100%)
- Ensure response completeness
- Verify HTML structure if applicable

### Missing Evaluation in Results

- Evaluation only runs for successful responses
- Check that test status is "success"
- Verify `enable_evaluation=True` in code

## Support

For issues, feature requests, or questions about the evaluation system:
- GitHub Issues: [PraisonAI Bench Issues](https://github.com/MervinPraison/praisonaibench/issues)
- Documentation: [README.md](README.md)

---

**The automated evaluation system makes PraisonAI Bench more than just a benchmarking tool—it's a comprehensive quality assurance system for LLM outputs!** 🎯

