"""
Report Generator - Create HTML dashboard from benchmark results
Simple, standalone report generation with charts and metrics
"""

from typing import List, Dict, Any
from datetime import datetime
import json
import os


class ReportGenerator:
    """Generate HTML reports from benchmark results"""
    
    @staticmethod
    def generate_html_report(results: List[Dict[str, Any]], 
                            summary: Dict[str, Any],
                            output_path: str = None) -> str:
        """
        Generate HTML report with charts and metrics
        
        Args:
            results: List of benchmark results
            summary: Summary dictionary from Bench.get_summary()
            output_path: Optional path for output file
            
        Returns:
            Path to generated HTML file
        """
        if not results:
            print("No results to generate report from")
            return None
        
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"output/reports/benchmark_report_{timestamp}.html"
        
        # Ensure directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir:  # Only if there's a directory component
            os.makedirs(output_dir, exist_ok=True)
        else:
            # If just a filename, put it in output/reports/
            output_path = f"output/reports/{output_path}"
            os.makedirs("output/reports", exist_ok=True)
        
        # Generate HTML content
        html_content = ReportGenerator._generate_html(results, summary)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"📊 Report generated: {output_path}")
        return output_path
    
    @staticmethod
    def _generate_html(results: List[Dict[str, Any]], summary: Dict[str, Any]) -> str:
        """Generate HTML content"""
        
        # Prepare data for charts
        test_names = [r.get('test_name', 'Unknown') for r in results]
        execution_times = [r.get('execution_time', 0) for r in results]
        statuses = [r.get('status', 'unknown') for r in results]
        
        # Token usage data
        token_data = []
        cost_data = []
        eval_scores = []
        
        for r in results:
            token_usage = r.get('token_usage', {})
            token_data.append(token_usage.get('total_tokens', 0))
            
            cost = r.get('cost', {})
            cost_data.append(cost.get('total_usd', 0))
            
            evaluation = r.get('evaluation', {})
            eval_scores.append(evaluation.get('overall_score', 0) if evaluation else 0)
        
        # Count by status
        status_counts = {'success': 0, 'error': 0, 'other': 0}
        for status in statuses:
            if status == 'success':
                status_counts['success'] += 1
            elif status == 'error':
                status_counts['error'] += 1
            else:
                status_counts['other'] += 1
        
        # Model breakdown
        model_stats = {}
        for r in results:
            model = r.get('model')
            if isinstance(model, dict):
                model_name = model.get('model', 'unknown')
            else:
                model_name = str(model) if model else 'unknown'
            
            if model_name not in model_stats:
                model_stats[model_name] = {'count': 0, 'success': 0, 'total_time': 0}
            
            model_stats[model_name]['count'] += 1
            if r.get('status') == 'success':
                model_stats[model_name]['success'] += 1
            model_stats[model_name]['total_time'] += r.get('execution_time', 0)
        
        # Cost summary
        cost_summary = summary.get('cost_summary', {})
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PraisonAI Bench Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; background: #f5f7fa; color: #2c3e50; line-height: 1.6; }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
        header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 20px; text-align: center; border-radius: 10px; margin-bottom: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .subtitle {{ opacity: 0.9; font-size: 1.1em; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .stat-card {{ background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 4px solid #667eea; }}
        .stat-value {{ font-size: 2em; font-weight: bold; color: #667eea; margin: 10px 0; }}
        .stat-label {{ color: #7f8c8d; text-transform: uppercase; font-size: 0.85em; letter-spacing: 0.5px; }}
        .charts-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(500px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .chart-container {{ background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .chart-container h3 {{ margin-bottom: 20px; color: #2c3e50; }}
        canvas {{ max-height: 300px; }}
        .results-table {{ background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 30px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        thead {{ background: #667eea; color: white; }}
        th, td {{ padding: 15px; text-align: left; border-bottom: 1px solid #ecf0f1; }}
        tbody tr:hover {{ background: #f8f9fa; }}
        .status-badge {{ padding: 5px 10px; border-radius: 5px; font-size: 0.85em; font-weight: 600; }}
        .status-success {{ background: #d4edda; color: #155724; }}
        .status-error {{ background: #f8d7da; color: #721c24; }}
        .model-stats {{ background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .model-item {{ padding: 15px; border-bottom: 1px solid #ecf0f1; display: flex; justify-content: space-between; align-items: center; }}
        .model-name {{ font-weight: 600; color: #2c3e50; }}
        .model-metrics {{ display: flex; gap: 20px; }}
        .metric {{ text-align: center; }}
        .metric-value {{ font-size: 1.2em; font-weight: bold; color: #667eea; }}
        .metric-label {{ font-size: 0.85em; color: #7f8c8d; }}
        footer {{ text-align: center; padding: 20px; color: #7f8c8d; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 PraisonAI Bench Report</h1>
            <p class="subtitle">Generated on {datetime.now().strftime("%B %d, %Y at %H:%M:%S")}</p>
        </header>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Tests</div>
                <div class="stat-value">{summary.get('total_tests', 0)}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Success Rate</div>
                <div class="stat-value">{summary.get('success_rate', '0%')}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Avg Time</div>
                <div class="stat-value">{summary.get('average_execution_time', '0s')}</div>
            </div>
            {f'''<div class="stat-card">
                <div class="stat-label">Total Cost</div>
                <div class="stat-value">${cost_summary.get('total_cost_usd', 0):.4f}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Tokens</div>
                <div class="stat-value">{cost_summary.get('total_tokens', 0):,}</div>
            </div>''' if cost_summary else ''}
        </div>

        <div class="charts-grid">
            <div class="chart-container">
                <h3>📊 Test Status Distribution</h3>
                <canvas id="statusChart"></canvas>
            </div>
            <div class="chart-container">
                <h3>⏱️ Execution Time by Test</h3>
                <canvas id="timeChart"></canvas>
            </div>
            {f'''<div class="chart-container">
                <h3>🪙 Token Usage by Test</h3>
                <canvas id="tokenChart"></canvas>
            </div>
            <div class="chart-container">
                <h3>💰 Cost by Test</h3>
                <canvas id="costChart"></canvas>
            </div>''' if any(token_data) or any(cost_data) else ''}
            {f'''<div class="chart-container">
                <h3>📈 Evaluation Scores</h3>
                <canvas id="evalChart"></canvas>
            </div>''' if any(eval_scores) else ''}
        </div>

        <div class="model-stats">
            <h3 style="margin-bottom: 20px;">🤖 Model Performance</h3>
            {ReportGenerator._generate_model_stats_html(model_stats)}
        </div>

        <div class="results-table">
            <table>
                <thead>
                    <tr>
                        <th>Test Name</th>
                        <th>Status</th>
                        <th>Model</th>
                        <th>Time (s)</th>
                        <th>Tokens</th>
                        <th>Cost</th>
                        <th>Score</th>
                    </tr>
                </thead>
                <tbody>
                    {ReportGenerator._generate_table_rows(results)}
                </tbody>
            </table>
        </div>

        <footer>
            <p>Generated by PraisonAI Bench v0.0.12 | <a href="https://github.com/MervinPraison/praisonaibench" target="_blank">GitHub</a></p>
        </footer>
    </div>

    <script>
        // Status Chart
        new Chart(document.getElementById('statusChart'), {{
            type: 'doughnut',
            data: {{
                labels: ['Success', 'Error', 'Other'],
                datasets: [{{
                    data: [{status_counts['success']}, {status_counts['error']}, {status_counts['other']}],
                    backgroundColor: ['#4ade80', '#f87171', '#94a3b8']
                }}]
            }},
            options: {{ responsive: true, maintainAspectRatio: true }}
        }});

        // Execution Time Chart
        new Chart(document.getElementById('timeChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(test_names)},
                datasets: [{{
                    label: 'Execution Time (s)',
                    data: {json.dumps(execution_times)},
                    backgroundColor: '#667eea'
                }}]
            }},
            options: {{ responsive: true, maintainAspectRatio: true, scales: {{ y: {{ beginAtZero: true }} }} }}
        }});

        {f'''// Token Chart
        new Chart(document.getElementById('tokenChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(test_names)},
                datasets: [{{
                    label: 'Tokens',
                    data: {json.dumps(token_data)},
                    backgroundColor: '#f59e0b'
                }}]
            }},
            options: {{ responsive: true, maintainAspectRatio: true, scales: {{ y: {{ beginAtZero: true }} }} }}
        }});

        // Cost Chart
        new Chart(document.getElementById('costChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(test_names)},
                datasets: [{{
                    label: 'Cost (USD)',
                    data: {json.dumps(cost_data)},
                    backgroundColor: '#10b981'
                }}]
            }},
            options: {{ responsive: true, maintainAspectRatio: true, scales: {{ y: {{ beginAtZero: true }} }} }}
        }});''' if any(token_data) or any(cost_data) else ''}

        {f'''// Evaluation Chart
        new Chart(document.getElementById('evalChart'), {{
            type: 'line',
            data: {{
                labels: {json.dumps(test_names)},
                datasets: [{{
                    label: 'Evaluation Score',
                    data: {json.dumps(eval_scores)},
                    borderColor: '#8b5cf6',
                    backgroundColor: 'rgba(139, 92, 246, 0.1)',
                    tension: 0.4,
                    fill: true
                }}]
            }},
            options: {{ 
                responsive: true, 
                maintainAspectRatio: true,
                scales: {{ y: {{ beginAtZero: true, max: 100 }} }} 
            }}
        }});''' if any(eval_scores) else ''}
    </script>
</body>
</html>'''
        
        return html
    
    @staticmethod
    def _generate_model_stats_html(model_stats: Dict[str, Dict]) -> str:
        """Generate HTML for model statistics"""
        html = ""
        for model_name, stats in model_stats.items():
            success_rate = (stats['success'] / stats['count'] * 100) if stats['count'] > 0 else 0
            avg_time = stats['total_time'] / stats['count'] if stats['count'] > 0 else 0
            
            html += f'''
            <div class="model-item">
                <div class="model-name">{model_name}</div>
                <div class="model-metrics">
                    <div class="metric">
                        <div class="metric-value">{stats['count']}</div>
                        <div class="metric-label">Tests</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{success_rate:.0f}%</div>
                        <div class="metric-label">Success</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{avg_time:.2f}s</div>
                        <div class="metric-label">Avg Time</div>
                    </div>
                </div>
            </div>'''
        
        return html
    
    @staticmethod
    def _generate_table_rows(results: List[Dict[str, Any]]) -> str:
        """Generate HTML table rows for results"""
        rows = ""
        for r in results:
            status = r.get('status', 'unknown')
            status_class = f"status-{status}" if status in ['success', 'error'] else "status-other"
            
            model = r.get('model')
            if isinstance(model, dict):
                model_name = model.get('model', 'unknown')
            else:
                model_name = str(model) if model else 'unknown'
            
            token_usage = r.get('token_usage', {})
            tokens = token_usage.get('total_tokens', '-')
            
            cost = r.get('cost', {})
            cost_usd = f"${cost.get('total_usd', 0):.6f}" if cost.get('total_usd') else '-'
            
            evaluation = r.get('evaluation', {})
            score = evaluation.get('overall_score', '-') if evaluation else '-'
            
            rows += f'''
            <tr>
                <td>{r.get('test_name', 'Unknown')}</td>
                <td><span class="status-badge {status_class}">{status.upper()}</span></td>
                <td>{model_name}</td>
                <td>{r.get('execution_time', 0):.2f}</td>
                <td>{tokens}</td>
                <td>{cost_usd}</td>
                <td>{score}</td>
            </tr>'''
        
        return rows
    
    @staticmethod
    def generate_comparison_report(runs: List[Dict[str, Any]], output_path: str = None) -> str:
        """
        Generate comparison report from multiple test runs.
        
        Args:
            runs: List of run data (each with 'results', 'summary', 'file')
            output_path: Optional path for output file
            
        Returns:
            Path to generated HTML file
        """
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"output/reports/comparison_report_{timestamp}.html"
        
        # Ensure directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        else:
            output_path = f"output/reports/{output_path}"
            os.makedirs("output/reports", exist_ok=True)
        
        # Build comparison data
        run_labels = [run['file'] for run in runs]
        
        # Aggregate metrics per run
        metrics_by_run = []
        for run in runs:
            results = run['results']
            total = len(results)
            success = sum(1 for r in results if r.get('status') == 'success')
            avg_time = sum(r.get('execution_time', 0) for r in results) / total if total > 0 else 0
            total_tokens = sum(r.get('token_usage', {}).get('total_tokens', 0) for r in results)
            total_cost = sum(r.get('cost', {}).get('total_usd', 0) for r in results)
            
            metrics_by_run.append({
                'total': total,
                'success': success,
                'success_rate': (success/total*100) if total > 0 else 0,
                'avg_time': avg_time,
                'total_tokens': total_tokens,
                'total_cost': total_cost
            })
        
        # Generate HTML
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PraisonAI Bench Comparison</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f7fa; color: #2c3e50; line-height: 1.6; }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
        header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 20px; text-align: center; border-radius: 10px; margin-bottom: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .subtitle {{ opacity: 0.9; font-size: 1.1em; }}
        .comparison-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .run-card {{ background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .run-title {{ font-size: 1.2em; font-weight: bold; margin-bottom: 15px; color: #667eea; }}
        .metric-row {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #ecf0f1; }}
        .metric-label {{ color: #7f8c8d; }}
        .metric-value {{ font-weight: bold; }}
        .charts-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(500px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .chart-container {{ background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .chart-container h3 {{ margin-bottom: 20px; color: #2c3e50; }}
        canvas {{ max-height: 300px; }}
        footer {{ text-align: center; padding: 20px; color: #7f8c8d; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 PraisonAI Bench Comparison</h1>
            <p class="subtitle">Comparing {len(runs)} test runs - Generated on {datetime.now().strftime("%B %d, %Y at %H:%M:%S")}</p>
        </header>

        <div class="comparison-grid">
            {ReportGenerator._generate_comparison_cards(runs, metrics_by_run)}
        </div>

        <div class="charts-grid">
            <div class="chart-container">
                <h3>📈 Success Rate Comparison</h3>
                <canvas id="successChart"></canvas>
            </div>
            <div class="chart-container">
                <h3>⏱️ Average Execution Time</h3>
                <canvas id="timeChart"></canvas>
            </div>
            <div class="chart-container">
                <h3>🪙 Total Tokens Used</h3>
                <canvas id="tokenChart"></canvas>
            </div>
            <div class="chart-container">
                <h3>💰 Total Cost</h3>
                <canvas id="costChart"></canvas>
            </div>
        </div>

        <footer>
            <p>Generated by PraisonAI Bench v0.0.11 | <a href="https://github.com/MervinPraison/praisonaibench" target="_blank">GitHub</a></p>
        </footer>
    </div>

    <script>
        const labels = {json.dumps(run_labels)};
        
        // Success Rate Chart
        new Chart(document.getElementById('successChart'), {{
            type: 'bar',
            data: {{
                labels: labels,
                datasets: [{{
                    label: 'Success Rate (%)',
                    data: {json.dumps([m['success_rate'] for m in metrics_by_run])},
                    backgroundColor: '#4ade80'
                }}]
            }},
            options: {{ 
                responsive: true, 
                maintainAspectRatio: true,
                scales: {{ y: {{ beginAtZero: true, max: 100 }} }} 
            }}
        }});

        // Execution Time Chart
        new Chart(document.getElementById('timeChart'), {{
            type: 'bar',
            data: {{
                labels: labels,
                datasets: [{{
                    label: 'Avg Time (seconds)',
                    data: {json.dumps([round(m['avg_time'], 2) for m in metrics_by_run])},
                    backgroundColor: '#667eea'
                }}]
            }},
            options: {{ 
                responsive: true, 
                maintainAspectRatio: true,
                scales: {{ y: {{ beginAtZero: true }} }} 
            }}
        }});

        // Token Chart
        new Chart(document.getElementById('tokenChart'), {{
            type: 'bar',
            data: {{
                labels: labels,
                datasets: [{{
                    label: 'Total Tokens',
                    data: {json.dumps([m['total_tokens'] for m in metrics_by_run])},
                    backgroundColor: '#f59e0b'
                }}]
            }},
            options: {{ 
                responsive: true, 
                maintainAspectRatio: true,
                scales: {{ y: {{ beginAtZero: true }} }} 
            }}
        }});

        // Cost Chart
        new Chart(document.getElementById('costChart'), {{
            type: 'bar',
            data: {{
                labels: labels,
                datasets: [{{
                    label: 'Total Cost (USD)',
                    data: {json.dumps([round(m['total_cost'], 4) for m in metrics_by_run])},
                    backgroundColor: '#10b981'
                }}]
            }},
            options: {{ 
                responsive: true, 
                maintainAspectRatio: true,
                scales: {{ y: {{ beginAtZero: true }} }} 
            }}
        }});
    </script>
</body>
</html>'''
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"📊 Comparison report generated: {output_path}")
        return output_path
    
    @staticmethod
    def _generate_comparison_cards(runs: List[Dict], metrics: List[Dict]) -> str:
        """Generate HTML cards for each run"""
        html = ""
        for i, (run, metric) in enumerate(zip(runs, metrics)):
            html += f'''
            <div class="run-card">
                <div class="run-title">Run {i+1}: {run['file']}</div>
                <div class="metric-row">
                    <span class="metric-label">Total Tests</span>
                    <span class="metric-value">{metric['total']}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Successful</span>
                    <span class="metric-value">{metric['success']}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Success Rate</span>
                    <span class="metric-value">{metric['success_rate']:.1f}%</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Avg Time</span>
                    <span class="metric-value">{metric['avg_time']:.2f}s</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Total Tokens</span>
                    <span class="metric-value">{metric['total_tokens']:,}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Total Cost</span>
                    <span class="metric-value">${metric['total_cost']:.4f}</span>
                </div>
            </div>'''
        
        return html

