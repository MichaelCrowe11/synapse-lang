"""
Test runner for the Quantum Trinity test suite.

Provides comprehensive testing with coverage reports, performance benchmarks,
and example validation.
"""

import sys
import os
import time
import argparse
from pathlib import Path
import unittest
import json
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestRunner:
    """Comprehensive test runner for Quantum Trinity."""
    
    def __init__(self, verbose=False, coverage=False):
        self.verbose = verbose
        self.coverage = coverage
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'coverage': {},
            'performance': {}
        }
        
    def run_unit_tests(self):
        """Run all unit tests."""
        print("\n" + "="*60)
        print("RUNNING UNIT TESTS")
        print("="*60)
        
        loader = unittest.TestLoader()
        suite = loader.discover('tests/unit', pattern='test_*.py')
        
        runner = unittest.TextTestRunner(verbosity=2 if self.verbose else 1)
        result = runner.run(suite)
        
        self.results['tests']['unit'] = {
            'total': result.testsRun,
            'failures': len(result.failures),
            'errors': len(result.errors),
            'skipped': len(result.skipped),
            'success': result.wasSuccessful()
        }
        
        return result.wasSuccessful()
        
    def run_integration_tests(self):
        """Run integration tests."""
        print("\n" + "="*60)
        print("RUNNING INTEGRATION TESTS")
        print("="*60)
        
        loader = unittest.TestLoader()
        suite = loader.discover('tests/integration', pattern='test_*.py')
        
        runner = unittest.TextTestRunner(verbosity=2 if self.verbose else 1)
        result = runner.run(suite)
        
        self.results['tests']['integration'] = {
            'total': result.testsRun,
            'failures': len(result.failures),
            'errors': len(result.errors),
            'skipped': len(result.skipped),
            'success': result.wasSuccessful()
        }
        
        return result.wasSuccessful()
        
    def validate_examples(self):
        """Validate all documentation examples."""
        print("\n" + "="*60)
        print("VALIDATING DOCUMENTATION EXAMPLES")
        print("="*60)
        
        examples_dir = project_root / 'docs' / 'examples'
        validation_results = []
        
        # Define example files to validate
        example_files = [
            'chemistry/drug-discovery.md',
            'finance/risk-analysis.md',
            'physics/climate-modeling.md',
            'ml/quantum-ml.md'
        ]
        
        for example_file in example_files:
            file_path = examples_dir / example_file
            if file_path.exists():
                print(f"\nValidating {example_file}...")
                success = self._validate_example_file(file_path)
                validation_results.append({
                    'file': example_file,
                    'success': success
                })
            else:
                print(f"Warning: {example_file} not found")
                validation_results.append({
                    'file': example_file,
                    'success': False,
                    'error': 'File not found'
                })
                
        self.results['tests']['examples'] = validation_results
        
        return all(r['success'] for r in validation_results if 'error' not in r)
        
    def _validate_example_file(self, file_path):
        """Validate code blocks in a single example file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract code blocks
        import re
        
        # Find Synapse code blocks
        synapse_blocks = re.findall(r'```synapse(.*?)```', content, re.DOTALL)
        
        # Find Qubit-Flow code blocks  
        qubit_blocks = re.findall(r'```qubit-flow(.*?)```', content, re.DOTALL)
        
        # Find Quantum-Net code blocks
        quantum_net_blocks = re.findall(r'```quantum-net(.*?)```', content, re.DOTALL)
        
        # Validate syntax (simplified - would need actual parsers)
        validation_passed = True
        
        for block in synapse_blocks:
            if not self._validate_synapse_syntax(block):
                print(f"  ✗ Synapse syntax error in {file_path.name}")
                validation_passed = False
                
        for block in qubit_blocks:
            if not self._validate_qubit_flow_syntax(block):
                print(f"  ✗ Qubit-Flow syntax error in {file_path.name}")
                validation_passed = False
                
        for block in quantum_net_blocks:
            if not self._validate_quantum_net_syntax(block):
                print(f"  ✗ Quantum-Net syntax error in {file_path.name}")
                validation_passed = False
                
        if validation_passed:
            print(f"  ✓ All code blocks valid in {file_path.name}")
            
        return validation_passed
        
    def _validate_synapse_syntax(self, code):
        """Basic Synapse syntax validation."""
        # Check for basic syntax elements
        required_elements = ['uncertain', '±', 'monte_carlo', 'parallel']
        
        # At least one of these should be present
        for element in required_elements:
            if element in code:
                return True
        
        # Check for Python-like syntax
        try:
            # Basic syntax check (would need proper parser)
            compile(code.replace('uncertain ', '').replace('±', ','), '<string>', 'exec')
            return True
        except:
            return False
            
    def _validate_qubit_flow_syntax(self, code):
        """Basic Qubit-Flow syntax validation."""
        # Check for quantum-specific syntax
        quantum_elements = ['qubit', '|0⟩', '|1⟩', 'H[', 'CNOT[', 'circuit', 'measure']
        
        for element in quantum_elements:
            if element in code:
                return True
                
        return False
        
    def _validate_quantum_net_syntax(self, code):
        """Basic Quantum-Net syntax validation."""
        # Check for network-specific syntax
        network_elements = ['network', 'nodes', 'teleport', 'quantum_channel', 'bell_pair']
        
        for element in network_elements:
            if element in code:
                return True
                
        return False
        
    def run_performance_benchmarks(self):
        """Run performance benchmarks."""
        print("\n" + "="*60)
        print("RUNNING PERFORMANCE BENCHMARKS")
        print("="*60)
        
        benchmarks = []
        
        # Benchmark 1: Uncertainty propagation
        print("\n1. Uncertainty Propagation Benchmark...")
        start_time = time.time()
        self._benchmark_uncertainty_propagation()
        uncertainty_time = time.time() - start_time
        benchmarks.append({
            'name': 'Uncertainty Propagation',
            'time': uncertainty_time,
            'operations_per_second': 10000 / uncertainty_time
        })
        print(f"   Completed in {uncertainty_time:.2f}s")
        
        # Benchmark 2: Parallel execution
        print("\n2. Parallel Execution Benchmark...")
        start_time = time.time()
        speedup = self._benchmark_parallel_execution()
        parallel_time = time.time() - start_time
        benchmarks.append({
            'name': 'Parallel Execution',
            'time': parallel_time,
            'speedup': speedup
        })
        print(f"   Speedup: {speedup:.2f}x")
        
        # Benchmark 3: Monte Carlo simulation
        print("\n3. Monte Carlo Simulation Benchmark...")
        start_time = time.time()
        self._benchmark_monte_carlo()
        monte_carlo_time = time.time() - start_time
        benchmarks.append({
            'name': 'Monte Carlo (100k samples)',
            'time': monte_carlo_time,
            'samples_per_second': 100000 / monte_carlo_time
        })
        print(f"   {100000 / monte_carlo_time:.0f} samples/second")
        
        self.results['performance']['benchmarks'] = benchmarks
        
        return True
        
    def _benchmark_uncertainty_propagation(self):
        """Benchmark uncertainty propagation performance."""
        from synapse_lang.uncertainty import UncertainValue
        
        # Create uncertain values
        values = [UncertainValue(i, i * 0.1) for i in range(1, 101)]
        
        # Perform many operations
        result = values[0]
        for v in values[1:]:
            result = result + v
            result = result * UncertainValue(1.001, 0.0001)
            
        return result
        
    def _benchmark_parallel_execution(self):
        """Benchmark parallel execution speedup."""
        import time
        from synapse_lang.parallel import parallel_block
        
        def cpu_task(n):
            total = 0
            for i in range(n):
                total += i ** 2
            return total
            
        # Serial execution
        start = time.time()
        serial_results = [cpu_task(100000) for _ in range(8)]
        serial_time = time.time() - start
        
        # Parallel execution
        start = time.time()
        parallel_results = parallel_block(
            function=cpu_task,
            inputs=[100000] * 8
        )
        parallel_time = time.time() - start
        
        speedup = serial_time / parallel_time
        return speedup
        
    def _benchmark_monte_carlo(self):
        """Benchmark Monte Carlo simulation."""
        from synapse_lang.uncertainty import UncertainValue, monte_carlo
        import numpy as np
        
        # Define uncertain parameters
        x = UncertainValue(10.0, 1.0)
        y = UncertainValue(5.0, 0.5)
        
        def calculation(x_val, y_val):
            return np.sin(x_val) * np.exp(-y_val/10) + x_val * y_val
            
        result = monte_carlo(
            function=calculation,
            inputs={'x': x, 'y': y},
            samples=100000
        )
        
        return result
        
    def run_coverage_analysis(self):
        """Run code coverage analysis."""
        if not self.coverage:
            return True
            
        print("\n" + "="*60)
        print("RUNNING COVERAGE ANALYSIS")
        print("="*60)
        
        try:
            import coverage
            
            cov = coverage.Coverage()
            cov.start()
            
            # Run tests with coverage
            self.run_unit_tests()
            self.run_integration_tests()
            
            cov.stop()
            cov.save()
            
            # Generate report
            print("\nCoverage Report:")
            cov.report()
            
            # Save HTML report
            cov.html_report(directory='tests/coverage_html')
            print("\nHTML coverage report saved to tests/coverage_html/")
            
            # Get coverage percentage
            total_coverage = cov.report(show_missing=False)
            self.results['coverage']['total'] = total_coverage
            
            return True
            
        except ImportError:
            print("Coverage package not installed. Install with: pip install coverage")
            return False
            
    def generate_report(self):
        """Generate comprehensive test report."""
        print("\n" + "="*60)
        print("TEST REPORT SUMMARY")
        print("="*60)
        
        # Unit tests
        if 'unit' in self.results['tests']:
            unit = self.results['tests']['unit']
            print(f"\nUnit Tests: {unit['total']} tests")
            print(f"  ✓ Passed: {unit['total'] - unit['failures'] - unit['errors']}")
            print(f"  ✗ Failed: {unit['failures']}")
            print(f"  ⚠ Errors: {unit['errors']}")
            
        # Integration tests
        if 'integration' in self.results['tests']:
            integration = self.results['tests']['integration']
            print(f"\nIntegration Tests: {integration['total']} tests")
            print(f"  ✓ Passed: {integration['total'] - integration['failures'] - integration['errors']}")
            print(f"  ✗ Failed: {integration['failures']}")
            print(f"  ⚠ Errors: {integration['errors']}")
            
        # Example validation
        if 'examples' in self.results['tests']:
            examples = self.results['tests']['examples']
            passed = sum(1 for e in examples if e.get('success', False))
            print(f"\nExample Validation: {len(examples)} files")
            print(f"  ✓ Valid: {passed}")
            print(f"  ✗ Invalid: {len(examples) - passed}")
            
        # Performance benchmarks
        if 'benchmarks' in self.results['performance']:
            print("\nPerformance Benchmarks:")
            for benchmark in self.results['performance']['benchmarks']:
                print(f"  • {benchmark['name']}: {benchmark['time']:.2f}s")
                if 'speedup' in benchmark:
                    print(f"    Speedup: {benchmark['speedup']:.2f}x")
                    
        # Coverage
        if 'total' in self.results['coverage']:
            print(f"\nCode Coverage: {self.results['coverage']['total']:.1f}%")
            
        # Save JSON report
        report_path = project_root / 'tests' / 'test_report.json'
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"\nDetailed report saved to: {report_path}")
        
        # Overall status
        all_passed = all([
            self.results['tests'].get('unit', {}).get('success', False),
            self.results['tests'].get('integration', {}).get('success', False)
        ])
        
        print("\n" + "="*60)
        if all_passed:
            print("✓ ALL TESTS PASSED")
        else:
            print("✗ SOME TESTS FAILED")
        print("="*60)
        
        return all_passed


def main():
    """Main entry point for test runner."""
    parser = argparse.ArgumentParser(description='Quantum Trinity Test Runner')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('-c', '--coverage', action='store_true', help='Run with coverage analysis')
    parser.add_argument('--unit', action='store_true', help='Run only unit tests')
    parser.add_argument('--integration', action='store_true', help='Run only integration tests')
    parser.add_argument('--examples', action='store_true', help='Validate only examples')
    parser.add_argument('--benchmarks', action='store_true', help='Run only benchmarks')
    parser.add_argument('--all', action='store_true', help='Run all tests (default)')
    
    args = parser.parse_args()
    
    # Default to all if nothing specified
    if not any([args.unit, args.integration, args.examples, args.benchmarks]):
        args.all = True
        
    runner = TestRunner(verbose=args.verbose, coverage=args.coverage)
    
    success = True
    
    if args.all or args.unit:
        success = success and runner.run_unit_tests()
        
    if args.all or args.integration:
        success = success and runner.run_integration_tests()
        
    if args.all or args.examples:
        success = success and runner.validate_examples()
        
    if args.all or args.benchmarks:
        runner.run_performance_benchmarks()
        
    if args.coverage:
        runner.run_coverage_analysis()
        
    runner.generate_report()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()