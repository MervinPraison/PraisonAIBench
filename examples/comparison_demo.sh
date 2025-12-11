#!/bin/bash
# Demo: Compare multiple benchmark results

echo "📊 PraisonAI Bench - Comparison Demo"
echo "===================================="
echo ""

# Find JSON result files
FILES=($(find output/json -name "*.json" -type f | head -3))

if [ ${#FILES[@]} -lt 2 ]; then
    echo "❌ Need at least 2 result files to compare"
    echo "Run some tests first:"
    echo "  praisonaibench --suite tests.yaml"
    exit 1
fi

echo "Found ${#FILES[@]} result files:"
for i in "${!FILES[@]}"; do
    echo "  [$((i+1))] ${FILES[$i]}"
done
echo ""

echo "🎨 Generating comparison report..."
praisonaibench --compare "${FILES[@]}"

echo ""
echo "✅ Done! Check output/reports/ for the comparison report"
