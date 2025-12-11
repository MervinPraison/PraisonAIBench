"""
Python Evaluator Plugin Example for PraisonAI Bench

This is a minimal example showing how to create a plugin.

Installation:
1. Create pyproject.toml in the same directory:
   
   [build-system]
   requires = ["hatchling"]
   build-backend = "hatchling.build"
   
   [project]
   name = "praisonaibench-python"
   version = "0.1.0"
   dependencies = ["praisonaibench>=0.1.0"]
   
   [project.entry-points."praisonaibench.evaluators"]
   python = "python_evaluator:PythonEvaluator"

2. Install: pip install -e .  (or: uv pip install -e .)

3. Use in tests.yaml:
   tests:
     - name: "python_test"
       language: "python"
       prompt: "Write Python code that prints Hello World"
       expected: "Hello World"
"""

from praisonaibench import BaseEvaluator
import subprocess
import tempfile
import os


class PythonEvaluator(BaseEvaluator):
    """Minimal Python code evaluator"""
    
    def get_language(self):
        return 'python'
    
    def get_file_extension(self):
        return 'py'
    
    def evaluate(self, code, test_name, prompt, expected=None):
        """
        Evaluate Python code:
        1. Check syntax (30 points)
        2. Execute code (50 points)
        3. Compare output (20 points if expected provided)
        """
        score = 0
        feedback = []
        
        # Extract code from markdown if present
        code = self._extract_code(code)
        
        # 1. Syntax Check
        syntax_ok, syntax_error = self._check_syntax(code)
        if syntax_ok:
            score += 30
            feedback.append({'level': 'success', 'message': '✅ Valid Python syntax'})
        else:
            feedback.append({'level': 'error', 'message': f'❌ Syntax error: {syntax_error}'})
            return {'score': score, 'passed': False, 'feedback': feedback, 'details': {}}
        
        # 2. Execution
        executed, output, error = self._execute_code(code)
        if executed:
            score += 50
            feedback.append({'level': 'success', 'message': '✅ Code executed successfully'})
        else:
            feedback.append({'level': 'error', 'message': f'❌ Runtime error: {error}'})
        
        # 3. Output comparison
        if expected and executed:
            if output.strip() == expected.strip():
                score += 20
                feedback.append({'level': 'success', 'message': '✅ Output matches expected'})
            else:
                feedback.append({'level': 'warning', 'message': '⚠️  Output differs from expected'})
        
        return {
            'score': min(score, 100),
            'passed': score >= 70,
            'feedback': feedback,
            'details': {'output': output if executed else None}
        }
    
    def _extract_code(self, response):
        """Extract Python code from markdown blocks"""
        import re
        patterns = [
            r'```python\s*\n(.*?)\n```',
            r'```py\s*\n(.*?)\n```',
            r'```\s*\n(.*?)\n```'
        ]
        for pattern in patterns:
            match = re.search(pattern, response, re.DOTALL)
            if match:
                return match.group(1).strip()
        return response.strip()
    
    def _check_syntax(self, code):
        """Check Python syntax"""
        try:
            compile(code, '<string>', 'exec')
            return True, None
        except SyntaxError as e:
            return False, str(e)
    
    def _execute_code(self, code, timeout=5):
        """Execute Python code safely"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            result = subprocess.run(
                ['python', temp_file],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            os.unlink(temp_file)
            
            if result.returncode == 0:
                return True, result.stdout.strip(), None
            else:
                return False, result.stdout.strip(), result.stderr.strip()
                
        except subprocess.TimeoutExpired:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
            return False, None, f"Timeout after {timeout}s"
        except Exception as e:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
            return False, None, str(e)
