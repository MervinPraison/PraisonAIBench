"""
SVG Benchmark Report Generator

Generates visual comparison reports for SVG generation benchmarks.
Displays side-by-side model comparisons with:
- Rendered SVG images
- Token counts
- Execution times
- Thinking/output phases
- SVG code preview

Based on the UI design from Gemini 3 Flash vs Gemini 2.5 Pro comparison.
"""

import os
import json
import base64
from datetime import datetime
from typing import Dict, List, Any, Optional


class SVGReportGenerator:
    """
    Generate HTML reports for SVG benchmark results.
    
    Creates a visual comparison interface similar to the Gemini benchmark UI.
    """
    
    @staticmethod
    def generate(results: List[Dict[str, Any]], 
                 summary: Dict[str, Any] = None,
                 output_path: str = None,
                 title: str = "SVG Generation Benchmark") -> str:
        """
        Generate HTML report from SVG benchmark results.
        
        Args:
            results: List of test results
            summary: Optional summary statistics
            output_path: Optional output file path
            title: Report title
            
        Returns:
            Path to generated report
        """
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = "output/reports"
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"svg_benchmark_{timestamp}.html")
        
        # Group results by test name for comparison
        grouped = SVGReportGenerator._group_by_test(results)
        
        # Generate HTML
        html = SVGReportGenerator._generate_html(grouped, summary, title)
        
        # Write to file
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"📊 SVG Benchmark Report: {output_path}")
        return output_path
    
    @staticmethod
    def _group_by_test(results: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """Group results by test name for comparison."""
        grouped = {}
        for result in results:
            test_name = result.get('test_name', 'unknown')
            if test_name not in grouped:
                grouped[test_name] = []
            grouped[test_name].append(result)
        return grouped
    
    @staticmethod
    def _generate_html(grouped: Dict[str, List[Dict]], 
                       summary: Dict[str, Any],
                       title: str) -> str:
        """Generate the complete HTML report."""
        
        # Calculate summary if not provided
        if not summary:
            all_results = [r for results in grouped.values() for r in results]
            summary = SVGReportGenerator._calculate_summary(all_results)
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        {SVGReportGenerator._get_styles()}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>{title}</h1>
            <p class="subtitle">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </header>
        
        {SVGReportGenerator._generate_summary_section(summary)}
        
        <div class="tests-container">
            {SVGReportGenerator._generate_test_sections(grouped)}
        </div>
    </div>
    
    <script>
        {SVGReportGenerator._get_scripts()}
    </script>
</body>
</html>'''
        return html
    
    @staticmethod
    def _get_styles() -> str:
        """Return CSS styles for the report."""
        return '''
        :root {
            --bg-primary: #0f0f0f;
            --bg-secondary: #1a1a1a;
            --bg-card: #242424;
            --text-primary: #ffffff;
            --text-secondary: #a0a0a0;
            --accent-blue: #3b82f6;
            --accent-green: #22c55e;
            --accent-orange: #f97316;
            --accent-purple: #a855f7;
            --border-color: #333;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
        }
        
        .container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            padding: 40px 0;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5rem;
            font-weight: 600;
            margin-bottom: 10px;
        }
        
        .subtitle {
            color: var(--text-secondary);
        }
        
        /* Summary Section */
        .summary-section {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .summary-card {
            background: var(--bg-card);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        }
        
        .summary-card .value {
            font-size: 2rem;
            font-weight: 700;
            color: var(--accent-blue);
        }
        
        .summary-card .label {
            color: var(--text-secondary);
            font-size: 0.9rem;
            margin-top: 5px;
        }
        
        /* Test Section */
        .test-section {
            background: var(--bg-secondary);
            border-radius: 16px;
            margin-bottom: 30px;
            overflow: hidden;
        }
        
        .test-header {
            background: var(--bg-card);
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
        }
        
        .test-header:hover {
            background: #2a2a2a;
        }
        
        .test-title {
            font-size: 1.2rem;
            font-weight: 600;
        }
        
        .test-prompt {
            color: var(--text-secondary);
            font-size: 0.9rem;
            margin-top: 5px;
            max-width: 600px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        .test-badge {
            background: var(--accent-blue);
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
        }
        
        .test-content {
            padding: 20px;
        }
        
        /* Model Comparison Grid */
        .model-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
        }
        
        .model-card {
            background: var(--bg-card);
            border-radius: 12px;
            overflow: hidden;
        }
        
        .model-header {
            padding: 15px 20px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .model-name {
            font-weight: 600;
            font-size: 1.1rem;
        }
        
        .token-badge {
            background: var(--accent-purple);
            color: white;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 0.8rem;
        }
        
        /* SVG Preview */
        .svg-preview {
            background: white;
            aspect-ratio: 4/3;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            position: relative;
        }
        
        .svg-preview img {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }
        
        .svg-preview svg {
            max-width: 100%;
            max-height: 100%;
        }
        
        .svg-placeholder {
            color: #666;
            text-align: center;
            padding: 40px;
        }
        
        /* Metrics Bar */
        .metrics-bar {
            display: flex;
            padding: 15px 20px;
            gap: 20px;
            border-top: 1px solid var(--border-color);
            flex-wrap: wrap;
        }
        
        .metric {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .metric-icon {
            width: 20px;
            height: 20px;
        }
        
        .metric-value {
            font-weight: 600;
        }
        
        .metric-label {
            color: var(--text-secondary);
            font-size: 0.85rem;
        }
        
        .status-success {
            color: var(--accent-green);
        }
        
        .status-pending {
            color: var(--accent-orange);
        }
        
        /* Progress Indicators */
        .progress-bar {
            height: 4px;
            background: var(--border-color);
            border-radius: 2px;
            overflow: hidden;
            margin-top: 10px;
        }
        
        .progress-fill {
            height: 100%;
            background: var(--accent-blue);
            transition: width 0.3s ease;
        }
        
        /* Phases */
        .phases {
            display: flex;
            gap: 10px;
            padding: 10px 20px;
            border-top: 1px solid var(--border-color);
            font-size: 0.85rem;
        }
        
        .phase {
            padding: 4px 10px;
            border-radius: 4px;
            background: var(--bg-secondary);
        }
        
        .phase.active {
            background: var(--accent-blue);
            color: white;
        }
        
        /* Code Preview */
        .code-preview {
            background: #1e1e1e;
            padding: 15px;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.8rem;
            max-height: 200px;
            overflow: auto;
            border-top: 1px solid var(--border-color);
        }
        
        .code-preview code {
            color: #d4d4d4;
            white-space: pre-wrap;
            word-break: break-all;
        }
        
        /* Toggle Button */
        .toggle-code {
            background: none;
            border: 1px solid var(--border-color);
            color: var(--text-secondary);
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.85rem;
            margin: 10px 20px;
        }
        
        .toggle-code:hover {
            background: var(--bg-secondary);
            color: var(--text-primary);
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .model-grid {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 1.8rem;
            }
        }
        '''
    
    @staticmethod
    def _get_scripts() -> str:
        """Return JavaScript for interactivity."""
        return '''
        // Toggle code preview
        function toggleCode(id) {
            const el = document.getElementById(id);
            if (el) {
                el.style.display = el.style.display === 'none' ? 'block' : 'none';
            }
        }
        
        // Toggle test section
        function toggleTest(id) {
            const el = document.getElementById(id);
            if (el) {
                el.style.display = el.style.display === 'none' ? 'block' : 'none';
            }
        }
        
        // Copy SVG code
        function copyCode(id) {
            const el = document.getElementById(id);
            if (el) {
                navigator.clipboard.writeText(el.textContent);
                alert('Code copied to clipboard!');
            }
        }
        '''
    
    @staticmethod
    def _calculate_summary(results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary statistics from results."""
        total = len(results)
        successful = sum(1 for r in results if r.get('status') == 'success')
        
        total_time = sum(r.get('execution_time', 0) for r in results)
        avg_time = total_time / total if total > 0 else 0
        
        total_tokens = sum(
            r.get('token_usage', {}).get('total_tokens', 0) 
            for r in results
        )
        
        avg_score = 0
        score_count = 0
        for r in results:
            eval_result = r.get('evaluation', {})
            if eval_result and 'overall_score' in eval_result:
                avg_score += eval_result['overall_score']
                score_count += 1
        avg_score = avg_score / score_count if score_count > 0 else 0
        
        return {
            'total_tests': total,
            'successful_tests': successful,
            'failed_tests': total - successful,
            'success_rate': f"{(successful/total*100):.1f}%" if total > 0 else "0%",
            'total_execution_time': f"{total_time:.1f}s",
            'average_execution_time': f"{avg_time:.2f}s",
            'total_tokens': total_tokens,
            'average_score': f"{avg_score:.1f}"
        }
    
    @staticmethod
    def _generate_summary_section(summary: Dict[str, Any]) -> str:
        """Generate the summary cards section."""
        return f'''
        <div class="summary-section">
            <div class="summary-card">
                <div class="value">{summary.get('total_tests', 0)}</div>
                <div class="label">Total Tests</div>
            </div>
            <div class="summary-card">
                <div class="value" style="color: var(--accent-green);">{summary.get('successful_tests', 0)}</div>
                <div class="label">Successful</div>
            </div>
            <div class="summary-card">
                <div class="value">{summary.get('average_execution_time', '0s')}</div>
                <div class="label">Avg Time</div>
            </div>
            <div class="summary-card">
                <div class="value">{summary.get('total_tokens', 0):,}</div>
                <div class="label">Total Tokens</div>
            </div>
            <div class="summary-card">
                <div class="value">{summary.get('average_score', '0')}</div>
                <div class="label">Avg Score</div>
            </div>
        </div>
        '''
    
    @staticmethod
    def _generate_test_sections(grouped: Dict[str, List[Dict]]) -> str:
        """Generate test comparison sections."""
        sections = []
        
        for test_name, results in grouped.items():
            prompt = results[0].get('prompt', '')[:100] + '...' if results else ''
            
            section = f'''
            <div class="test-section">
                <div class="test-header" onclick="toggleTest('test-{test_name}')">
                    <div>
                        <div class="test-title">📊 {test_name}</div>
                        <div class="test-prompt">{prompt}</div>
                    </div>
                    <span class="test-badge">{len(results)} run(s)</span>
                </div>
                <div class="test-content" id="test-{test_name}">
                    <div class="model-grid">
                        {SVGReportGenerator._generate_model_cards(results, test_name)}
                    </div>
                </div>
            </div>
            '''
            sections.append(section)
        
        return '\n'.join(sections)
    
    @staticmethod
    def _generate_model_cards(results: List[Dict], test_name: str) -> str:
        """Generate model comparison cards."""
        cards = []
        
        for i, result in enumerate(results):
            model = result.get('model', 'unknown')
            if isinstance(model, dict):
                model_name = model.get('model', str(model))
            else:
                model_name = str(model)
            
            status = result.get('status', 'unknown')
            exec_time = result.get('execution_time', 0)
            token_usage = result.get('token_usage', {})
            total_tokens = token_usage.get('total_tokens', 0)
            input_tokens = token_usage.get('input_tokens', 0)
            output_tokens = token_usage.get('output_tokens', 0)
            
            # Get evaluation results
            evaluation = result.get('evaluation', {})
            score = evaluation.get('overall_score', evaluation.get('score', 0))
            
            # Get render path
            render_path = None
            if evaluation:
                render_path = evaluation.get('render_path') or \
                             evaluation.get('visual', {}).get('render_path')
            
            # Generate SVG preview
            svg_preview = SVGReportGenerator._generate_svg_preview(
                result.get('response', ''),
                render_path,
                test_name,
                i
            )
            
            # Status indicator
            status_class = 'status-success' if status == 'success' else 'status-pending'
            status_icon = '✅' if status == 'success' else '⏳'
            
            card = f'''
            <div class="model-card">
                <div class="model-header">
                    <span class="model-name">{model_name}</span>
                    <span class="token-badge">{total_tokens:,} tokens</span>
                </div>
                
                <div class="svg-preview">
                    {svg_preview}
                </div>
                
                <div class="metrics-bar">
                    <div class="metric">
                        <span class="metric-value {status_class}">{status_icon}</span>
                        <span class="metric-label">{exec_time:.2f}s</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Input</span>
                        <span class="metric-value">{input_tokens:,}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Output</span>
                        <span class="metric-value">{output_tokens:,}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Score</span>
                        <span class="metric-value">{score}/100</span>
                    </div>
                </div>
                
                <div class="phases">
                    <span class="phase active">Input</span>
                    <span class="phase active">Thinking</span>
                    <span class="phase {'active' if status == 'success' else ''}">Output</span>
                </div>
                
                <button class="toggle-code" onclick="toggleCode('code-{test_name}-{i}')">
                    Show/Hide Code
                </button>
                
                <div class="code-preview" id="code-{test_name}-{i}" style="display: none;">
                    <code>{SVGReportGenerator._escape_html(result.get('response', '')[:2000])}</code>
                </div>
            </div>
            '''
            cards.append(card)
        
        return '\n'.join(cards)
    
    @staticmethod
    def _generate_svg_preview(response: str, render_path: str, 
                              test_name: str, index: int) -> str:
        """Generate SVG preview HTML."""
        # Try to use rendered PNG if available
        if render_path and os.path.exists(render_path):
            try:
                with open(render_path, 'rb') as f:
                    img_data = base64.b64encode(f.read()).decode('utf-8')
                return f'<img src="data:image/png;base64,{img_data}" alt="{test_name}">'
            except Exception:
                pass
        
        # Try to extract and embed SVG directly
        svg_content = SVGReportGenerator._extract_svg(response)
        if svg_content:
            # Sanitize SVG for embedding
            svg_safe = svg_content.replace('<script', '<!-- script')
            svg_safe = svg_safe.replace('</script>', 'script -->')
            return svg_safe
        
        # Fallback placeholder
        return '''
        <div class="svg-placeholder">
            <p>⏳ SVG Preview</p>
            <p style="font-size: 0.8rem;">Rendering...</p>
        </div>
        '''
    
    @staticmethod
    def _extract_svg(content: str) -> Optional[str]:
        """Extract SVG from response."""
        import re
        
        # Try code blocks first
        svg_block = re.search(r'```(?:svg|xml)?\s*\n(.*?)\n```', content, re.DOTALL)
        if svg_block:
            svg = svg_block.group(1)
            if '<svg' in svg.lower():
                return svg
        
        # Try raw SVG
        svg_match = re.search(r'(<svg[^>]*>.*?</svg>)', content, re.DOTALL | re.IGNORECASE)
        if svg_match:
            return svg_match.group(1)
        
        return None
    
    @staticmethod
    def _escape_html(text: str) -> str:
        """Escape HTML special characters."""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))


class SVGComparisonReport:
    """
    Generate side-by-side model comparison reports.
    
    Similar to the Gemini 3 Flash vs Gemini 2.5 Pro comparison UI.
    """
    
    @staticmethod
    def generate(model_results: Dict[str, List[Dict[str, Any]]],
                 output_path: str = None,
                 title: str = "Model Comparison") -> str:
        """
        Generate comparison report for multiple models.
        
        Args:
            model_results: Dict mapping model names to their results
            output_path: Optional output file path
            title: Report title
            
        Returns:
            Path to generated report
        """
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = "output/reports"
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"model_comparison_{timestamp}.html")
        
        # Flatten results for the main generator
        all_results = []
        for model_name, results in model_results.items():
            for result in results:
                result['model'] = model_name
                all_results.append(result)
        
        return SVGReportGenerator.generate(all_results, None, output_path, title)
