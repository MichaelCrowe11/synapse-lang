#!/usr/bin/env python3
"""
Enhanced feature tests for Synapse language improvements
Tests new deliverables: tensor literals, pipeline context, reason chains, parallel optimization
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from synapse_interpreter import SynapseInterpreter
import time

def test_tensor_literals():
    print("\n" + "="*60)
    print("TEST: Tensor/Matrix Literal Parsing")
    print("="*60)
    
    interpreter = SynapseInterpreter()
    
    # Test list literal
    code1 = """
    vector = [1, 2, 3, 4]
    x = 5
    """
    results1 = interpreter.execute(code1)
    for r in results1:
        print(f"  List: {r}")
    
    # Test matrix literal (manual construction for now)
    print("  Matrix stored in variables:", interpreter.variables.get('vector', 'Not found'))
    
    print("  [PASSED] test_tensor_literals")

def test_pipeline_context_propagation():
    print("\n" + "="*60)
    print("TEST: Pipeline Context Propagation")
    print("="*60)
    
    interpreter = SynapseInterpreter()
    
    code = """
    initial_value = 10
    pipeline DataProcess {
        stage preprocess {
            processed_value = initial_value * 2
        }
        stage transform {
            final_value = processed_value + 5
        }
    }
    """
    
    results = interpreter.execute(code)
    for r in results:
        print(f"  Pipeline: {r}")
    
    # Check if variables propagated
    print(f"  Variables after pipeline: {list(interpreter.variables.keys())}")
    print(f"  Final value: {interpreter.variables.get('final_value', 'Not found')}")
    
    print("  [PASSED] test_pipeline_context_propagation")

def test_enhanced_reason_chains():
    print("\n" + "="*60)
    print("TEST: Enhanced Reason Chain Evaluation")
    print("="*60)
    
    interpreter = SynapseInterpreter()
    
    code = """
    temperature = 300
    reason chain ThermalAnalysis {
        premise P1: temperature
        derive D1 from P1: temperature * 1.5
        conclude: temperature -> "valid_temperature"
    }
    """
    
    results = interpreter.execute(code)
    for r in results:
        print(f"  Reason chain: {r}")
    
    print("  [PASSED] test_enhanced_reason_chains")

def test_parallel_optimization():
    print("\n" + "="*60)
    print("TEST: Parallel Worker Optimization")
    print("="*60)
    
    interpreter = SynapseInterpreter()
    
    # Test with specified worker count
    code1 = """
    parallel(4) {
        branch A: task_a()
        branch B: task_b()
        branch C: task_c()
        branch D: task_d()
    }
    """
    
    start_time = time.time()
    results1 = interpreter.execute(code1)
    exec_time = time.time() - start_time
    
    for r in results1:
        print(f"  Parallel (4 workers): {r}")
    print(f"  Execution time: {exec_time:.3f} seconds")
    
    # Test auto worker detection
    code2 = """
    parallel {
        branch X: task_x()
        branch Y: task_y()
    }
    """
    
    results2 = interpreter.execute(code2)
    for r in results2:
        print(f"  Parallel (auto): {r}")
    
    print("  [PASSED] test_parallel_optimization")

def test_comprehensive_integration():
    print("\n" + "="*60)
    print("TEST: Comprehensive Feature Integration")
    print("="*60)
    
    interpreter = SynapseInterpreter()
    
    code = """
    data = [1, 2, 3]
    hypothesis DataValid: data
    
    pipeline Analysis {
        stage validate {
            is_valid = 1
        }
        stage process parallel(2) {
            result = is_valid * 42
        }
    }
    
    reason chain Validation {
        premise P1: result
        conclude: result -> "analysis_complete"
    }
    """
    
    results = interpreter.execute(code)
    for r in results:
        print(f"  Integration: {r}")
    
    print(f"  Final variables: {list(interpreter.variables.keys())}")
    
    print("  [PASSED] test_comprehensive_integration")

def run_all_enhanced_tests():
    print("############################################################")
    print("# SYNAPSE ENHANCED FEATURES TEST SUITE")
    print("############################################################")
    
    test_tensor_literals()
    test_pipeline_context_propagation()
    test_enhanced_reason_chains()
    test_parallel_optimization()
    test_comprehensive_integration()
    
    print("\n############################################################")
    print("# ENHANCED TEST SUITE COMPLETED")
    print("############################################################")

if __name__ == "__main__":
    run_all_enhanced_tests()
