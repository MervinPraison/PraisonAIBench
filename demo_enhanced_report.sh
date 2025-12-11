#!/bin/bash
# Demo: Generate enhanced HTML reports with all UI features

echo "🚀 PraisonAI Bench - Enhanced Report Demo"
echo "=========================================="
echo ""

# Find a recent test result with evaluation data
RESULT_FILE=$(find output/json -name "*.json" -type f | head -1)

if [ -z "$RESULT_FILE" ]; then
    echo "❌ No test results found"
    echo "Run some tests first:"
    echo "  praisonaibench --suite tests.yaml"
    exit 1
fi

echo "📂 Using test results: $RESULT_FILE"
echo ""
echo "🎨 Generating enhanced HTML report..."
echo ""

# Generate enhanced report
praisonaibench --report-from "$RESULT_FILE"

echo ""
echo "✅ Done! Enhanced report includes:"
echo ""
echo "  📊 Dashboard Tab:"
echo "     - Summary cards (tests, models, success rate, time, cost, tokens)"
echo "     - Interactive charts (status, execution time, scores, errors/warnings)"
echo ""
echo "  🏆 Leaderboard Tab:"
echo "     - Model rankings with multiple criteria"
echo "     - Top 3 medals 🥇🥈🥉"
echo "     - Dynamic re-ranking by criteria"
echo ""
echo "  ⚖️ Comparison Tab:"
echo "     - Side-by-side model comparison"
echo "     - Detailed metrics table"
echo ""
echo "  📋 Results Tab:"
echo "     - All test results with details"
echo ""
echo "📂 Location: output/reports/"
echo "🌐 Open the HTML file in any browser"
