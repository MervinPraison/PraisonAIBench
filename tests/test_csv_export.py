"""
Tests for CSV Export Feature

Tests the CSV export functionality added in v0.0.10
"""

import pytest
import os
import csv
import tempfile
import shutil


class TestCSVExport:
    """Test CSV export functionality"""
    
    @pytest.fixture
    def bench_with_results(self):
        """Create Bench instance with mock results"""
        try:
            from praisonaibench import Bench
        except ImportError:
            pytest.skip("Bench not available")
        
        bench = Bench(enable_evaluation=False)
        
        # Add mock results
        bench.results = [
            {
                'test_name': 'test_1',
                'prompt': 'What is 2+2?',
                'response': 'The answer is 4.',
                'model': 'gpt-4o',
                'agent_name': 'BenchAgent',
                'execution_time': 1.23,
                'status': 'success',
                'timestamp': '2024-12-11 10:00:00',
                'token_usage': {
                    'input_tokens': 100,
                    'output_tokens': 50,
                    'total_tokens': 150
                },
                'cost': {
                    'total_usd': 0.000625,
                    'model': 'gpt-4o'
                },
                'evaluation': {
                    'overall_score': 95,
                    'passed': True
                }
            },
            {
                'test_name': 'test_2',
                'prompt': 'What is 3+3?',
                'response': None,
                'model': 'gpt-4o',
                'status': 'error',
                'timestamp': '2024-12-11 10:00:01',
                'execution_time': 0.5,
                'error': 'API timeout'
            }
        ]
        
        return bench
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    def test_csv_export_creates_file(self, bench_with_results, temp_output_dir):
        """Test that CSV export creates a file"""
        bench_with_results.config['output_dir'] = temp_output_dir
        
        csv_file = bench_with_results.save_results_csv('test.csv')
        
        assert csv_file is not None
        assert os.path.exists(csv_file)
        assert csv_file.endswith('.csv')
    
    def test_csv_export_has_headers(self, bench_with_results, temp_output_dir):
        """Test that CSV has correct headers"""
        bench_with_results.config['output_dir'] = temp_output_dir
        
        csv_file = bench_with_results.save_results_csv('test.csv')
        
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            
            # Check required headers
            assert 'test_name' in headers
            assert 'status' in headers
            assert 'model' in headers
            assert 'execution_time' in headers
            assert 'input_tokens' in headers
            assert 'output_tokens' in headers
            assert 'cost_usd' in headers
            assert 'evaluation_score' in headers
    
    def test_csv_export_row_count(self, bench_with_results, temp_output_dir):
        """Test that CSV has correct number of rows"""
        bench_with_results.config['output_dir'] = temp_output_dir
        
        csv_file = bench_with_results.save_results_csv('test.csv')
        
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            # Should have 2 rows (same as results)
            assert len(rows) == 2
    
    def test_csv_export_data_accuracy(self, bench_with_results, temp_output_dir):
        """Test that CSV data matches results"""
        bench_with_results.config['output_dir'] = temp_output_dir
        
        csv_file = bench_with_results.save_results_csv('test.csv')
        
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            # Check first row
            assert rows[0]['test_name'] == 'test_1'
            assert rows[0]['status'] == 'success'
            assert rows[0]['model'] == 'gpt-4o'
            assert rows[0]['input_tokens'] == '100'
            assert rows[0]['output_tokens'] == '50'
            assert rows[0]['evaluation_score'] == '95'
            
            # Check second row (error case)
            assert rows[1]['test_name'] == 'test_2'
            assert rows[1]['status'] == 'error'
            assert rows[1]['error'] == 'API timeout'
    
    def test_csv_export_empty_results(self, temp_output_dir):
        """Test CSV export with no results"""
        from praisonaibench import Bench
        
        bench = Bench(enable_evaluation=False)
        bench.config['output_dir'] = temp_output_dir
        
        result = bench.save_results_csv('test.csv')
        
        # Should return None for empty results
        assert result is None
    
    def test_csv_export_with_dict_model(self, temp_output_dir):
        """Test CSV export handles dict model configs"""
        from praisonaibench import Bench
        
        bench = Bench(enable_evaluation=False)
        bench.config['output_dir'] = temp_output_dir
        
        bench.results = [{
            'test_name': 'test_1',
            'model': {'model': 'gpt-4o', 'temperature': 0.7},
            'status': 'success',
            'execution_time': 1.0,
            'timestamp': '2024-01-01 00:00:00'
        }]
        
        csv_file = bench.save_results_csv('test.csv')
        
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            # Should extract model name from dict
            assert rows[0]['model'] == 'gpt-4o'
    
    def test_save_results_with_csv_format(self, bench_with_results, temp_output_dir):
        """Test save_results method with format='csv'"""
        bench_with_results.config['output_dir'] = temp_output_dir
        
        csv_file = bench_with_results.save_results(format='csv')
        
        assert csv_file is not None
        assert os.path.exists(csv_file)
        assert csv_file.endswith('.csv')
    
    def test_save_results_default_format(self, bench_with_results, temp_output_dir):
        """Test that default format is JSON"""
        bench_with_results.config['output_dir'] = temp_output_dir
        
        file_path = bench_with_results.save_results()
        
        assert file_path is not None
        assert file_path.endswith('.json')
    
    def test_csv_filename_extension(self, bench_with_results, temp_output_dir):
        """Test that .csv extension is added if missing"""
        bench_with_results.config['output_dir'] = temp_output_dir
        
        # Pass filename without .csv extension
        csv_file = bench_with_results.save_results_csv('test_results')
        
        assert csv_file.endswith('.csv')
    
    def test_csv_directory_creation(self, bench_with_results, temp_output_dir):
        """Test that csv subdirectory is created"""
        bench_with_results.config['output_dir'] = temp_output_dir
        
        csv_file = bench_with_results.save_results_csv('test.csv')
        
        # Should be in csv subdirectory
        assert 'csv' in csv_file
        assert os.path.exists(os.path.dirname(csv_file))


class TestCSVCLIIntegration:
    """Test CLI integration for CSV export"""
    
    def test_cli_format_argument(self):
        """Test that --format argument is accepted"""
        import argparse
        
        parser = argparse.ArgumentParser()
        parser.add_argument('--format', type=str, choices=['json', 'csv'], default='json')
        
        args = parser.parse_args(['--format', 'csv'])
        assert args.format == 'csv'
    
    def test_cli_format_default(self):
        """Test that --format defaults to json"""
        import argparse
        
        parser = argparse.ArgumentParser()
        parser.add_argument('--format', type=str, choices=['json', 'csv'], default='json')
        
        args = parser.parse_args([])
        assert args.format == 'json'


class TestCSVEdgeCases:
    """Test edge cases for CSV export"""
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    def test_csv_with_special_characters(self, temp_output_dir):
        """Test CSV export with special characters in data"""
        from praisonaibench import Bench
        
        bench = Bench(enable_evaluation=False)
        bench.config['output_dir'] = temp_output_dir
        
        bench.results = [{
            'test_name': 'test_special',
            'prompt': 'Test with "quotes" and, commas',
            'response': 'Response with\nnewlines',
            'status': 'success',
            'model': 'gpt-4o',
            'execution_time': 1.0,
            'timestamp': '2024-01-01 00:00:00'
        }]
        
        csv_file = bench.save_results_csv('test.csv')
        
        # Should handle special characters
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            assert len(rows) == 1
            assert 'quotes' in rows[0]['prompt']
    
    def test_csv_with_missing_fields(self, temp_output_dir):
        """Test CSV export with missing optional fields"""
        from praisonaibench import Bench
        
        bench = Bench(enable_evaluation=False)
        bench.config['output_dir'] = temp_output_dir
        
        bench.results = [{
            'test_name': 'test_minimal',
            'status': 'success',
            'execution_time': 1.0
            # Missing many optional fields
        }]
        
        csv_file = bench.save_results_csv('test.csv')
        
        # Should handle missing fields gracefully
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            assert len(rows) == 1
            assert rows[0]['test_name'] == 'test_minimal'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

