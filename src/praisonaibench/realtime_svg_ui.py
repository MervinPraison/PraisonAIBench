"""
Real-time SVG Comparison UI
Watch models generate SVGs side-by-side with live streaming
"""

import json
import os
import re
import time
import webbrowser
from typing import List, Dict, Any, Optional


class RealtimeSVGComparison:
    """Real-time SVG generation comparison with live UI"""
    
    def __init__(self, models: List[str], prompt: str, port: int = 8765):
        self.models = models
        self.prompt = prompt
        self.port = port
        self.results = {model: {"status": "pending", "svg": None, "time": 0, "tokens": 0} for model in models}
        self.start_time = None
        self.output_dir = "output/realtime_svg"
        os.makedirs(self.output_dir, exist_ok=True)
        
    def generate_html(self) -> str:
        """Generate the real-time comparison HTML page"""
        model_cards = ""
        for i, model in enumerate(self.models):
            model_short = model.split('/')[-1] if '/' in model else model
            model_cards += f'''
            <div class="model-card" id="card-{i}">
                <div class="model-header">
                    <span class="model-name">{model_short}</span>
                    <span class="model-status" id="status-{i}">⏳ Waiting</span>
                </div>
                <div class="svg-container" id="svg-{i}">
                    <div class="placeholder">
                        <div class="pulse-ring"></div>
                        <span>Ready to generate</span>
                    </div>
                </div>
                <div class="metrics">
                    <div class="metric">
                        <span class="metric-label">Time</span>
                        <span class="metric-value" id="time-{i}">--</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Tokens</span>
                        <span class="metric-value" id="tokens-{i}">--</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Score</span>
                        <span class="metric-value" id="score-{i}">--</span>
                    </div>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" id="progress-{i}"></div>
                </div>
            </div>
            '''
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎬 Real-time SVG Comparison</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            color: #fff;
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            padding: 30px 20px;
            margin-bottom: 30px;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #667eea, #764ba2, #f093fb);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .prompt-display {{
            background: rgba(255,255,255,0.1);
            padding: 15px 25px;
            border-radius: 10px;
            max-width: 800px;
            margin: 20px auto;
            font-style: italic;
            color: #a0a0a0;
        }}
        
        .controls {{
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-bottom: 40px;
        }}
        
        .btn {{
            padding: 15px 40px;
            font-size: 1.2em;
            border: none;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .btn-play {{
            background: linear-gradient(135deg, #4ade80, #22c55e);
            color: white;
            box-shadow: 0 4px 15px rgba(74, 222, 128, 0.4);
        }}
        
        .btn-play:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(74, 222, 128, 0.5);
        }}
        
        .btn-play:disabled {{
            background: #666;
            cursor: not-allowed;
            box-shadow: none;
        }}
        
        .btn-reset {{
            background: rgba(255,255,255,0.1);
            color: white;
            border: 1px solid rgba(255,255,255,0.2);
        }}
        
        .btn-reset:hover {{
            background: rgba(255,255,255,0.2);
        }}
        
        .models-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 25px;
            max-width: 1600px;
            margin: 0 auto;
        }}
        
        .model-card {{
            background: rgba(255,255,255,0.05);
            border-radius: 20px;
            padding: 25px;
            border: 1px solid rgba(255,255,255,0.1);
            transition: all 0.3s ease;
        }}
        
        .model-card.generating {{
            border-color: #667eea;
            box-shadow: 0 0 30px rgba(102, 126, 234, 0.3);
        }}
        
        .model-card.complete {{
            border-color: #4ade80;
        }}
        
        .model-card.winner {{
            border-color: #fbbf24;
            box-shadow: 0 0 40px rgba(251, 191, 36, 0.4);
        }}
        
        .model-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }}
        
        .model-name {{
            font-size: 1.3em;
            font-weight: 600;
        }}
        
        .model-status {{
            font-size: 0.9em;
            padding: 5px 12px;
            border-radius: 20px;
            background: rgba(255,255,255,0.1);
        }}
        
        .model-status.generating {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            animation: pulse 1.5s infinite;
        }}
        
        .model-status.complete {{
            background: linear-gradient(135deg, #4ade80, #22c55e);
        }}
        
        .model-status.winner {{
            background: linear-gradient(135deg, #fbbf24, #f59e0b);
        }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
        }}
        
        .svg-container {{
            background: white;
            border-radius: 15px;
            height: 250px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 20px;
            overflow: hidden;
            position: relative;
        }}
        
        .svg-container svg {{
            max-width: 100%;
            max-height: 100%;
        }}
        
        .placeholder {{
            text-align: center;
            color: #999;
        }}
        
        .pulse-ring {{
            width: 60px;
            height: 60px;
            border: 3px solid #ddd;
            border-radius: 50%;
            margin: 0 auto 15px;
        }}
        
        .generating .pulse-ring {{
            border-color: #667eea;
            border-top-color: transparent;
            animation: spin 1s linear infinite;
        }}
        
        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}
        
        .metrics {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-bottom: 15px;
        }}
        
        .metric {{
            text-align: center;
            padding: 10px;
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
        }}
        
        .metric-label {{
            display: block;
            font-size: 0.8em;
            color: #888;
            margin-bottom: 5px;
        }}
        
        .metric-value {{
            font-size: 1.2em;
            font-weight: 600;
            color: #fff;
        }}
        
        .progress-bar {{
            height: 4px;
            background: rgba(255,255,255,0.1);
            border-radius: 2px;
            overflow: hidden;
        }}
        
        .progress-fill {{
            height: 100%;
            width: 0%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            transition: width 0.3s ease;
        }}
        
        .timer {{
            text-align: center;
            font-size: 3em;
            font-weight: 300;
            margin-bottom: 30px;
            font-family: 'Courier New', monospace;
            color: #667eea;
        }}
        
        .winner-badge {{
            position: absolute;
            top: 10px;
            right: 10px;
            background: linear-gradient(135deg, #fbbf24, #f59e0b);
            color: #000;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.9em;
            display: none;
        }}
        
        .model-card.winner .winner-badge {{
            display: block;
        }}
        
        .race-line {{
            position: absolute;
            bottom: 0;
            left: 0;
            height: 3px;
            background: linear-gradient(90deg, #667eea, #764ba2);
            transition: width 0.1s linear;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎬 Real-time SVG Generation Race</h1>
        <p style="color: #888; margin-top: 10px;">Watch models compete to generate SVGs in real-time</p>
        <div class="prompt-display">
            "{self.prompt}"
        </div>
    </div>
    
    <div class="controls">
        <button class="btn btn-play" id="playBtn" onclick="startRace()">
            ▶️ Start Race
        </button>
        <button class="btn btn-reset" onclick="resetRace()">
            🔄 Reset
        </button>
    </div>
    
    <div class="timer" id="timer">00:00.000</div>
    
    <div class="models-grid">
        {model_cards}
    </div>
    
    <script>
        const models = {json.dumps(self.models)};
        let raceStarted = false;
        let startTime = null;
        let timerInterval = null;
        let eventSource = null;
        
        function updateTimer() {{
            if (!startTime) return;
            const elapsed = Date.now() - startTime;
            const mins = Math.floor(elapsed / 60000);
            const secs = Math.floor((elapsed % 60000) / 1000);
            const ms = elapsed % 1000;
            document.getElementById('timer').textContent = 
                String(mins).padStart(2, '0') + ':' + 
                String(secs).padStart(2, '0') + '.' + 
                String(ms).padStart(3, '0');
        }}
        
        function startRace() {{
            if (raceStarted) return;
            raceStarted = true;
            startTime = Date.now();
            
            document.getElementById('playBtn').disabled = true;
            document.getElementById('playBtn').innerHTML = '⏳ Running...';
            
            timerInterval = setInterval(updateTimer, 50);
            
            // Start all models
            models.forEach((model, i) => {{
                const card = document.getElementById('card-' + i);
                const status = document.getElementById('status-' + i);
                const svg = document.getElementById('svg-' + i);
                
                card.classList.add('generating');
                status.classList.add('generating');
                status.textContent = '🔄 Generating...';
                svg.innerHTML = '<div class="placeholder"><div class="pulse-ring"></div><span>Generating...</span></div>';
                
                // Simulate progress
                simulateProgress(i);
            }});
            
            // Connect to SSE for real updates
            eventSource = new EventSource('/api/race/stream');
            eventSource.onmessage = function(event) {{
                const data = JSON.parse(event.data);
                handleUpdate(data);
            }};
            eventSource.onerror = function() {{
                // Fallback: poll for updates
                pollForUpdates();
            }};
            
            // Start the actual race
            fetch('/api/race/start', {{ method: 'POST' }});
        }}
        
        function simulateProgress(index) {{
            let progress = 0;
            const interval = setInterval(() => {{
                if (!raceStarted) {{
                    clearInterval(interval);
                    return;
                }}
                progress += Math.random() * 5;
                if (progress > 95) progress = 95;
                document.getElementById('progress-' + index).style.width = progress + '%';
            }}, 200);
        }}
        
        function handleUpdate(data) {{
            const index = models.indexOf(data.model);
            if (index === -1) return;
            
            const card = document.getElementById('card-' + index);
            const status = document.getElementById('status-' + index);
            const svg = document.getElementById('svg-' + index);
            const time = document.getElementById('time-' + index);
            const tokens = document.getElementById('tokens-' + index);
            const score = document.getElementById('score-' + index);
            const progress = document.getElementById('progress-' + index);
            
            if (data.status === 'complete') {{
                card.classList.remove('generating');
                card.classList.add('complete');
                status.classList.remove('generating');
                status.classList.add('complete');
                status.textContent = '✅ Complete';
                progress.style.width = '100%';
                
                if (data.svg) {{
                    svg.innerHTML = data.svg;
                }}
                
                time.textContent = data.time.toFixed(2) + 's';
                tokens.textContent = data.tokens || '--';
                score.textContent = data.score || '--';
                
                if (data.winner) {{
                    card.classList.add('winner');
                    status.classList.add('winner');
                    status.textContent = '🏆 Winner!';
                }}
            }} else if (data.status === 'streaming') {{
                // Show partial SVG
                if (data.partial_svg) {{
                    svg.innerHTML = data.partial_svg;
                }}
            }}
            
            // Check if all complete
            checkRaceComplete();
        }}
        
        function checkRaceComplete() {{
            const allComplete = models.every((_, i) => {{
                return document.getElementById('card-' + i).classList.contains('complete');
            }});
            
            if (allComplete) {{
                clearInterval(timerInterval);
                document.getElementById('playBtn').innerHTML = '✅ Complete';
                if (eventSource) eventSource.close();
            }}
        }}
        
        function pollForUpdates() {{
            if (!raceStarted) return;
            
            fetch('/api/race/status')
                .then(r => r.json())
                .then(data => {{
                    data.results.forEach(result => handleUpdate(result));
                    if (!data.complete) {{
                        setTimeout(pollForUpdates, 500);
                    }}
                }})
                .catch(() => setTimeout(pollForUpdates, 1000));
        }}
        
        function resetRace() {{
            raceStarted = false;
            startTime = null;
            clearInterval(timerInterval);
            if (eventSource) eventSource.close();
            
            document.getElementById('timer').textContent = '00:00.000';
            document.getElementById('playBtn').disabled = false;
            document.getElementById('playBtn').innerHTML = '▶️ Start Race';
            
            models.forEach((_, i) => {{
                const card = document.getElementById('card-' + i);
                const status = document.getElementById('status-' + i);
                const svg = document.getElementById('svg-' + i);
                
                card.classList.remove('generating', 'complete', 'winner');
                status.classList.remove('generating', 'complete', 'winner');
                status.textContent = '⏳ Waiting';
                svg.innerHTML = '<div class="placeholder"><div class="pulse-ring"></div><span>Ready to generate</span></div>';
                
                document.getElementById('time-' + i).textContent = '--';
                document.getElementById('tokens-' + i).textContent = '--';
                document.getElementById('score-' + i).textContent = '--';
                document.getElementById('progress-' + i).style.width = '0%';
            }});
        }}
    </script>
</body>
</html>'''
        return html
    
    def save_html(self) -> str:
        """Save the HTML file"""
        html = self.generate_html()
        filepath = os.path.join(self.output_dir, "realtime_comparison.html")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        return filepath


class RealtimeSVGServer:
    """HTTP server for real-time SVG comparison"""
    
    def __init__(self, models: List[str], prompt: str, port: int = 8765):
        self.models = models
        self.prompt = prompt
        self.port = port
        self.results = {}
        self.race_complete = False
        self.winner = None
        self.start_time = None
        
    def run_race(self):
        """Run the SVG generation race"""
        from praisonaibench import Bench
        import concurrent.futures
        
        bench = Bench()
        self.start_time = time.time()
        self.results = {model: {"status": "generating"} for model in self.models}
        
        def generate_for_model(model: str) -> Dict[str, Any]:
            start = time.time()
            result = bench.run_single_test(
                prompt=self.prompt,
                model=model,
                test_name=f"race_{model.replace('/', '_')}"
            )
            elapsed = time.time() - start
            
            # Extract SVG
            svg = self._extract_svg(result.get('response', ''))
            
            return {
                "model": model,
                "status": "complete",
                "svg": svg,
                "time": elapsed,
                "tokens": result.get('token_usage', {}).get('total_tokens', 0),
                "score": result.get('evaluation', {}).get('overall_score', 0),
                "winner": False
            }
        
        # Run all models concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.models)) as executor:
            futures = {executor.submit(generate_for_model, model): model for model in self.models}
            
            for future in concurrent.futures.as_completed(futures):
                model = futures[future]
                try:
                    result = future.result()
                    self.results[model] = result
                    
                    # First to complete is winner
                    if self.winner is None:
                        self.winner = model
                        result["winner"] = True
                        
                except Exception as e:
                    self.results[model] = {
                        "model": model,
                        "status": "error",
                        "error": str(e)
                    }
        
        self.race_complete = True
        return self.results
    
    def _extract_svg(self, content: str) -> Optional[str]:
        """Extract SVG from response"""
        if not content:
            return None
            
        # Try code blocks
        match = re.search(r'```(?:svg|xml)?\s*\n(.*?)\n```', content, re.DOTALL)
        if match:
            svg = match.group(1)
            if '<svg' in svg.lower():
                return svg
        
        # Try raw SVG
        match = re.search(r'(<svg[^>]*>.*?</svg>)', content, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1)
        
        return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get current race status"""
        return {
            "complete": self.race_complete,
            "results": list(self.results.values()),
            "winner": self.winner
        }


def run_realtime_comparison(models: List[str], prompt: str, port: int = 8765, open_browser: bool = True):
    """
    Run a real-time SVG comparison between models.
    
    Args:
        models: List of model names to compare
        prompt: SVG generation prompt
        port: Port for the web server
        open_browser: Whether to open browser automatically
    """
    from praisonaibench import Bench
    import concurrent.futures
    
    # Generate HTML
    comparison = RealtimeSVGComparison(models, prompt, port)
    html_path = comparison.save_html()
    
    print(f"🎬 Real-time SVG Comparison")
    print(f"   Models: {', '.join(models)}")
    print(f"   Prompt: {prompt[:50]}...")
    print(f"   UI: file://{os.path.abspath(html_path)}")
    print()
    
    # Run the race
    print("🏁 Starting race...")
    bench = Bench()
    results = {}
    winner = None
    start_time = time.time()
    
    def generate_for_model(model: str) -> Dict[str, Any]:
        model_start = time.time()
        result = bench.run_single_test(
            prompt=prompt,
            model=model,
            test_name=f"race_{model.replace('/', '_')}"
        )
        elapsed = time.time() - model_start
        return {
            "model": model,
            "time": elapsed,
            "tokens": result.get('token_usage', {}).get('total_tokens', 0),
            "score": result.get('evaluation', {}).get('overall_score', 0),
            "response": result.get('response', '')
        }
    
    # Run concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(models)) as executor:
        futures = {executor.submit(generate_for_model, model): model for model in models}
        
        for future in concurrent.futures.as_completed(futures):
            model = futures[future]
            try:
                result = future.result()
                results[model] = result
                
                if winner is None:
                    winner = model
                    print(f"🏆 {model} finished first in {result['time']:.2f}s!")
                else:
                    print(f"✅ {model} finished in {result['time']:.2f}s")
                    
            except Exception as e:
                print(f"❌ {model} failed: {e}")
    
    total_time = time.time() - start_time
    
    # Print summary
    print()
    print("=" * 60)
    print("                    RACE RESULTS")
    print("=" * 60)
    print(f"| {'Model':<20} | {'Time':>8} | {'Tokens':>8} | {'Score':>6} |")
    print(f"|{'-'*22}|{'-'*10}|{'-'*10}|{'-'*8}|")
    
    for model in sorted(results.keys(), key=lambda m: results[m]['time']):
        r = results[model]
        badge = "🏆" if model == winner else "  "
        print(f"| {badge} {model:<18} | {r['time']:>6.2f}s | {r['tokens']:>8} | {r['score']:>6} |")
    
    print()
    print(f"Total race time: {total_time:.2f}s")
    print(f"Winner: {winner}")
    
    # Open browser if requested
    if open_browser:
        webbrowser.open(f"file://{os.path.abspath(html_path)}")
    
    return results


if __name__ == "__main__":
    # Example usage
    run_realtime_comparison(
        models=["gpt-4o-mini", "gpt-4o"],
        prompt="Generate an SVG of a simple red heart icon with proper xmlns and viewBox.",
        open_browser=True
    )
