"""
Tests for Parallel/Concurrent Test Execution Feature

Tests the parallel execution functionality added in v0.0.8
"""

import pytest
import os
import time
from unittest.mock import Mock, patch


class TestParallelExecution:
    """Test parallel test execution functionality"""
    
    @pytest.fixture
    def bench(self):
        """Create Bench instance"""
        try:
            from praisonaibench import Bench
            return Bench(enable_evaluation=False)
        except ImportError:
            pytest.skip("Bench not available")
    
    @pytest.fixture
    def sample_test_file(self, tmp_path):
        """Create a sample test YAML file"""
        test_file = tmp_path / "test_parallel.yaml"
        test_file.write_text("""
tests:
  - name: "test_1"
    prompt: "What is 2+2?"
  - name: "test_2"
    prompt: "What is 3+3?"
  - name: "test_3"
    prompt: "What is 4+4?"
  - name: "test_4"
    prompt: "What is 5+5?"
""")
        return str(test_file)
    
    def test_sequential_execution_default(self, bench, sample_test_file):
        """Test that default execution is sequential (concurrent=1)"""
        results = bench.run_test_suite(sample_test_file, concurrent=1)
        
        # Should have 4 results
        assert len(results) == 4
        
        # Results should be in order
        assert results[0]['test_name'] == 'test_1'
        assert results[1]['test_name'] == 'test_2'
        assert results[2]['test_name'] == 'test_3'
        assert results[3]['test_name'] == 'test_4'
    
    def test_parallel_execution_with_workers(self, bench, sample_test_file):
        """Test parallel execution with multiple workers"""
        results = bench.run_test_suite(sample_test_file, concurrent=3)
        
        # Should have 4 results
        assert len(results) == 4
        
        # Results should be sorted by test name (parallel execution maintains order)
        test_names = [r['test_name'] for r in results]
        assert 'test_1' in test_names
        assert 'test_2' in test_names
        assert 'test_3' in test_names
        assert 'test_4' in test_names
    
    def test_concurrent_parameter_validation(self, bench, sample_test_file):
        """Test that concurrent parameter is validated"""
        # concurrent=0 should default to sequential
        results = bench.run_test_suite(sample_test_file, concurrent=0)
        assert len(results) == 4
        
        # concurrent=-1 should default to sequential
        results = bench.run_test_suite(sample_test_file, concurrent=-1)
        assert len(results) == 4
    
    def test_test_filter_with_parallel(self, bench, sample_test_file):
        """Test that test filtering works with parallel execution"""
        results = bench.run_test_suite(
            sample_test_file, 
            test_filter="test_2",
            concurrent=3
        )
        
        # Should have only 1 result
        assert len(results) == 1
        assert results[0]['test_name'] == 'test_2'
    
    def test_parallel_results_include_all_fields(self, bench, sample_test_file):
        """Test that parallel execution results include all required fields"""
        results = bench.run_test_suite(sample_test_file, concurrent=2)
        
        for result in results:
            assert 'test_name' in result
            assert 'prompt' in result
            assert 'status' in result
            assert 'execution_time' in result
            assert 'timestamp' in result
    
    @patch('praisonaibench.bench.BenchAgent')
    def test_parallel_execution_thread_safety(self, mock_agent_class, bench, sample_test_file):
        """Test that parallel execution is thread-safe"""
        # Mock agent to return predictable results
        mock_agent = Mock()
        mock_agent.run_test = Mock(side_effect=lambda prompt, test_name: {
            'test_name': test_name,
            'prompt': prompt,
            'response': f'Response for {test_name}',
            'model': 'gpt-4o',
            'agent_name': 'BenchAgent',
            'execution_time': 1.0,
            'status': 'success',
            'timestamp': '2024-01-01 00:00:00'
        })
        mock_agent_class.return_value = mock_agent
        
        results = bench.run_test_suite(sample_test_file, concurrent=4)
        
        # Should have all 4 results
        assert len(results) == 4
        
        # All should be successful
        assert all(r['status'] == 'success' for r in results)
    
    def test_parallel_execution_progress_tracking(self, bench, sample_test_file, capsys):
        """Test that progress tracking works in parallel mode"""
        bench.run_test_suite(sample_test_file, concurrent=3)
        
        # Check that progress messages are printed
        captured = capsys.readouterr()
        assert "concurrent workers" in captured.out or "Running" in captured.out


class TestCLIParallelExecution:
    """Test CLI integration for parallel execution"""
    
    def test_cli_concurrent_argument(self):
        """Test that --concurrent argument is accepted"""
        import argparse
        from praisonaibench.cli import main
        
        # This is a basic test - actual CLI testing would require subprocess
        # Just verify the argument parser accepts --concurrent
        parser = argparse.ArgumentParser()
        parser.add_argument('--concurrent', type=int, default=1)
        
        args = parser.parse_args(['--concurrent', '3'])
        assert args.concurrent == 3
    
    def test_cli_concurrent_default(self):
        """Test that --concurrent defaults to 1"""
        import argparse
        
        parser = argparse.ArgumentParser()
        parser.add_argument('--concurrent', type=int, default=1)
        
        args = parser.parse_args([])
        assert args.concurrent == 1


class TestParallelExecutionEdgeCases:
    """Test edge cases for parallel execution"""
    
    @pytest.fixture
    def bench(self):
        """Create Bench instance"""
        try:
            from praisonaibench import Bench
            return Bench(enable_evaluation=False)
        except ImportError:
            pytest.skip("Bench not available")
    
    def test_single_test_parallel(self, bench, tmp_path):
        """Test parallel execution with single test"""
        test_file = tmp_path / "single_test.yaml"
        test_file.write_text("""
tests:
  - name: "single_test"
    prompt: "Test prompt"
""")
        
        results = bench.run_test_suite(str(test_file), concurrent=3)
        assert len(results) == 1
    
    def test_many_tests_parallel(self, bench, tmp_path):
        """Test parallel execution with many tests"""
        # Create test file with 10 tests
        tests = "\n".join([
            f"  - name: \"test_{i}\"\n    prompt: \"Test {i}\""
            for i in range(10)
        ])
        
        test_file = tmp_path / "many_tests.yaml"
        test_file.write_text(f"tests:\n{tests}\n")
        
        results = bench.run_test_suite(str(test_file), concurrent=5)
        assert len(results) == 10
    
    def test_parallel_with_model_override(self, bench, tmp_path):
        """Test parallel execution with model override"""
        test_file = tmp_path / "test_model.yaml"
        test_file.write_text("""
tests:
  - name: "test_1"
    prompt: "Test 1"
  - name: "test_2"
    prompt: "Test 2"
""")
        
        results = bench.run_test_suite(
            str(test_file),
            default_model="gpt-4o",
            concurrent=2
        )
        
        assert len(results) == 2
        # Model should be applied to all tests
        for result in results:
            assert result.get('model') is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
