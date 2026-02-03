# Reports & Export

Generate beautiful HTML reports and export results in multiple formats.

## HTML Dashboard Reports

Generate interactive reports with comprehensive visualizations:

```bash
# Generate report after running tests
praisonaibench --suite tests.yaml --report

# Generate report from existing results
praisonaibench --report-from output/json/benchmark_results_20241211_123456.json

# Compare multiple test results
praisonaibench --compare result1.json result2.json result3.json
```

## Report Features

### 📊 Dashboard Tab

- Summary cards with key metrics
- Interactive charts:
  - Status distribution (success/failure)
  - Execution time by model
  - Evaluation scores (radar chart)
  - Errors & warnings

### 🏆 Leaderboard Tab

- Model rankings with multiple criteria:
  - Overall Score (default)
  - Functional Score
  - Quality Score
  - Pass Rate
  - Speed (fastest first)
- Top 3 models highlighted with medals
- Click criteria to re-rank dynamically

### ⚖️ Comparison Tab

- Side-by-side model comparison
- Comprehensive metrics table:
  - Overall score, functional score, quality score
  - Pass rate with color coding
  - Average execution time
  - Total errors and warnings count

### 📋 Results Tab

- Complete test results table
- Individual test status, scores, time, tokens, cost
- Sortable columns
- Status indicators

## Report Benefits

| Feature | Benefit |
|---------|---------|
| 🎨 Modern UI | Gradient headers, smooth transitions |
| 📱 Responsive | Works on all devices |
| ⚡ Lightweight | No external dependencies |
| 📊 Interactive | Chart.js powered |
| 💾 Standalone | Works offline |
| 📧 Shareable | Single HTML file |

## CSV Export

Export results for spreadsheet analysis:

```bash
# Export to CSV format
praisonaibench --suite tests.yaml --format csv

# Results saved to: output/csv/benchmark_results_20241211_123456.csv
```

### CSV Columns

- Test names and status
- Model information
- Execution times
- Token usage (input/output/total)
- Costs per test
- Evaluation scores
- Prompts and response lengths
- Error messages (if any)

### CSV Use Cases

- Spreadsheet analysis (Excel/Google Sheets)
- Data visualization tools
- Statistical analysis
- Sharing with non-technical stakeholders

## Comparison Reports

Multi-run comparison shows:
- Side-by-side success rates
- Performance trends
- Cost and token usage evolution
- Model improvements over time
