#!/usr/bin/env python3
"""
Quantum Machine Learning Example
Demonstrates quantum-enhanced pattern recognition with hybrid execution
"""

def run_quantum_ml_example():
    """Run quantum machine learning example with hybrid approach"""
    
    try:
        from synapse_qubit_bridge import create_hybrid_interpreter
        import time
        
        print("=" * 60)
        print("QUANTUM MACHINE LEARNING HYBRID SYSTEM")
        print("=" * 60)
        
        # Create hybrid interpreter
        bridge = create_hybrid_interpreter()
        
        # Synapse-Lang: Scientific hypothesis about quantum advantage in ML
        synapse_code = '''
        # Training data uncertainty
        uncertain accuracy_classical = 85.2 ± 2.1
        uncertain accuracy_quantum = 92.7 ± 1.8
        uncertain training_time = 45.3 ± 5.2
        
        # Hypothesis about quantum machine learning advantage
        hypothesis quantum_ml_advantage {
            assume: superposition_enables_parallel_processing
            assume: entanglement_captures_feature_correlations
            predict: exponential_speedup_for_certain_problems
            validate: comparative_performance_analysis
        }
        
        # Parallel model evaluation
        parallel {
            branch classical_svm: support_vector_machine
            branch classical_nn: neural_network
            branch quantum_svm: quantum_support_vector_machine
            branch quantum_nn: quantum_neural_network
            branch hybrid_ensemble: classical_quantum_ensemble
        }
        '''
        
        # Qubit-Flow: Quantum feature encoding and processing
        qubit_code = '''
        # Feature encoding qubits (4 features -> 2 qubits)
        qubit feature1 = |0⟩
        qubit feature2 = |0⟩
        
        # Feature encoding circuit
        circuit feature_encoding(feature1, feature2) {
            # Amplitude encoding of classical features
            RY(1.2)[feature1]
            RY(0.8)[feature2]
            
            # Feature correlation through entanglement
            CNOT[feature1, feature2]
            
            # Quantum interference for pattern recognition
            H[feature1]
            CZ[feature1, feature2]
        }
        
        # Quantum Support Vector Machine circuit
        circuit quantum_svm(feature1, feature2) {
            # Kernel computation through quantum interference
            H[feature1]
            H[feature2]
            
            # Non-linear feature mapping
            RZ(0.5)[feature1]
            RZ(0.3)[feature2]
            
            # Classification measurement
            measure feature1 -> class_bit1
            measure feature2 -> class_bit2
        }
        
        # Variational quantum classifier
        circuit variational_classifier(feature1, feature2) {
            RY(0.7)[feature1]
            RY(1.1)[feature2]
            CNOT[feature1, feature2]
            RY(0.4)[feature1]
            RY(0.9)[feature2]
        }
        '''
        
        print("Initializing quantum machine learning system...")
        print("\nSynapse-Lang (Scientific Framework):")
        print("- Hypothesis: Quantum advantage in ML")
        print("- Uncertainty in performance metrics")
        print("- Parallel model comparison")
        
        print("\nQubit-Flow (Quantum Processing):")
        print("- Quantum feature encoding")
        print("- Quantum SVM implementation")
        print("- Variational quantum classifier")
        
        # Execute hybrid ML system
        start_time = time.time()
        results = bridge.execute_hybrid(synapse_code, qubit_code)
        execution_time = time.time() - start_time
        
        print(f"\nExecution completed in {execution_time:.2f} seconds")
        
        print("\n" + "-" * 50)
        print("QUANTUM ML RESULTS")
        print("-" * 50)
        
        # Display results
        print("\nScientific Hypothesis Analysis:")
        for i, result in enumerate(results.get('synapse_results', [])[:4]):
            print(f"  {i+1}. {result}")
        
        print("\nQuantum Circuit Execution:")
        for i, result in enumerate(results.get('qubit_results', [])[:4]):
            print(f"  {i+1}. {result}")
        
        # Quantum-enhanced metrics
        if results.get('quantum_enhanced'):
            print("\nQuantum-Enhanced Performance Metrics:")
            for var, value in results.get('quantum_enhanced', {}).items():
                print(f"  {var}: {value}")
        
        # Simulate quantum advantage analysis
        print("\n" + "=" * 60)
        print("QUANTUM ADVANTAGE ANALYSIS")
        print("=" * 60)
        
        print("Quantum Feature Encoding:")
        print("✓ Superposition allows parallel feature processing")
        print("✓ Entanglement captures feature correlations")
        print("✓ Quantum interference enables non-linear mappings")
        
        print("\nPerformance Comparison (Simulated):")
        print("  Classical SVM:     85.2% ± 2.1% accuracy")
        print("  Quantum SVM:       92.7% ± 1.8% accuracy") 
        print("  Quantum Advantage: 7.5% improvement")
        
        print("\nKey Insights:")
        print("- Quantum encoding reduces feature dimensionality")
        print("- Entanglement captures non-local correlations")
        print("- Variational circuits adapt to training data")
        print("- Hybrid approach leverages both paradigms")
        
        # Create quantum-enhanced uncertainty for ML metrics
        if 'accuracy_quantum' in bridge.synapse_interpreter.variables:
            quantum_accuracy = bridge.quantum_enhance_uncertainty('accuracy_quantum', 'computational')
            print(f"\nQuantum-Enhanced Accuracy: {quantum_accuracy}")
        
        return results
        
    except Exception as e:
        print(f"Error in quantum ML simulation: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    run_quantum_ml_example()