#!/usr/bin/env python3
"""
Synapse Language - Complete AI/ML Platform Demo

Comprehensive demonstration of the AI/ML acceleration platform including:
- Neural network DSL with custom architectures
- AutoML hyperparameter optimization
- Multi-GPU distributed training
- Quantum-classical hybrid models
- GPU acceleration and performance optimization
- Model deployment and serving
"""

import sys
import os
import numpy as np
import time

# Add platform to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.neural_network_dsl import NeuralNetwork, Dense, Conv2D, LSTM, Attention
from src.automl_optimizer import AutoMLOptimizer, HyperparameterSpace, HyperparameterRange, create_neural_network_factory
from src.distributed_training import DistributedTrainer, TrainingJob, DistributionStrategy, create_local_cluster
from src.quantum_neural_networks import HybridQNN, QuantumDense, QuantumLayerConfig, create_quantum_classifier
from src.gpu_acceleration import GPUManager, create_gpu_manager
from src.model_deployment import ModelServer, CloudDeployment, DeploymentTarget, create_model_server

def demo_neural_network_dsl():
    """Demonstrate neural network DSL capabilities."""
    print("=" * 70)
    print("NEURAL NETWORK DSL DEMONSTRATION")
    print("=" * 70)
    
    # Create custom neural network architecture
    print("\n1. Building Custom Neural Network Architecture")
    print("-" * 50)
    
    model = NeuralNetwork("CustomImageClassifier")
    
    # Dense layers for demonstration (CNN integration would need flattening layer)
    model.add(Dense(units=128, activation='gelu', dropout_rate=0.3, name='dense1'))
    model.add(Dense(units=64, activation='swish', dropout_rate=0.2, name='dense2'))
    
    # Output layer
    model.add(Dense(units=10, activation='softmax', name='output'))
    
    # Compile model
    model.compile(optimizer='adamw', loss='categorical_crossentropy', learning_rate=0.001)
    
    # Print model summary
    model.summary()
    
    # Generate synthetic data for demo
    print("\n2. Training on Synthetic Data")
    print("-" * 50)
    
    X_train = np.random.randn(1000, 128)  # 1000 samples with 128 features
    y_train = np.eye(10)[np.random.randint(0, 10, 1000)]  # One-hot encoded labels
    
    # Train model
    history = model.fit(X_train, y_train, epochs=5, batch_size=32, validation_split=0.2)
    
    # Make predictions
    X_test = np.random.randn(100, 128)
    predictions = model.predict(X_test)
    
    print(f"Predictions shape: {predictions.shape}")
    print(f"Sample prediction: {predictions[0]}")
    
    # Save model
    model.save("custom_image_classifier.json")
    print("Model saved successfully!")
    
    return model

def demo_automl_optimization():
    """Demonstrate AutoML hyperparameter optimization."""
    print("\n" + "=" * 70)
    print("AUTOML HYPERPARAMETER OPTIMIZATION DEMONSTRATION")
    print("=" * 70)
    
    # Define hyperparameter search space
    print("\n1. Setting Up Hyperparameter Search Space")
    print("-" * 50)
    
    search_space = HyperparameterSpace()
    
    # Add hyperparameters
    search_space.add_parameter(HyperparameterRange(
        "learning_rate", "float", 1e-4, 1e-2, log_scale=True))
    search_space.add_parameter(HyperparameterRange(
        "batch_size", "int", 16, 128))
    search_space.add_parameter(HyperparameterRange(
        "hidden_units", "int", 64, 256))
    search_space.add_parameter(HyperparameterRange(
        "num_layers", "int", 2, 4))
    search_space.add_parameter(HyperparameterRange(
        "dropout_rate", "float", 0.1, 0.5))
    search_space.add_parameter(HyperparameterRange(
        "activation", "categorical", values=["relu", "gelu", "swish"]))
    
    print(f"Search space defined with {len(search_space.parameters)} parameters:")
    for name, param in search_space.parameters.items():
        print(f"  {name}: {param.param_type} {param.min_val}-{param.max_val if param.max_val else param.values}")
    
    # Create AutoML optimizer
    print("\n2. Running Bayesian Optimization")
    print("-" * 50)
    
    optimizer = AutoMLOptimizer(
        search_space=search_space,
        algorithm="bayesian",
        max_trials=20,
        objective="minimize"
    )
    
    # Create model factory
    model_factory = create_neural_network_factory(search_space)
    
    # Generate synthetic dataset
    X_data = np.random.randn(500, 20)
    y_data = np.random.randn(500, 1)
    dataset = (X_data, y_data)
    
    # Run optimization
    results = optimizer.optimize(
        model_factory=model_factory,
        dataset=dataset,
        metric="loss",
        verbose=1
    )
    
    # Print results
    print("\n3. Optimization Results")
    print("-" * 50)
    print(f"Best parameters: {results['best_parameters']}")
    print(f"Best score: {results['best_score']:.4f}")
    print(f"Total trials: {results['trials_completed']}")
    print(f"Total time: {results['total_time']:.2f} seconds")
    
    # Save results
    optimizer.save_results("automl_results.json")
    
    return results

def demo_distributed_training():
    """Demonstrate distributed training capabilities."""
    print("\n" + "=" * 70)
    print("DISTRIBUTED TRAINING DEMONSTRATION")
    print("=" * 70)
    
    # Create local cluster
    print("\n1. Setting Up Local Cluster")
    print("-" * 50)
    
    nodes = create_local_cluster(num_gpus=2)
    print(f"Created cluster with {len(nodes)} nodes:")
    for node in nodes:
        print(f"  Node {node.node_id}: {len(node.get_gpu_devices())} GPUs, {node.memory_gb}GB RAM")
    
    # Create distributed trainer
    trainer = DistributedTrainer(nodes)
    
    # Define training job
    print("\n2. Creating Distributed Training Job")
    print("-" * 50)
    
    job_config = TrainingJob(
        job_id="demo_distributed_job",
        model_config={
            "name": "DistributedDemoModel",
            "layers": [
                {"type": "dense", "units": 128, "activation": "relu"},
                {"type": "dense", "units": 64, "activation": "relu"},
                {"type": "dense", "units": 1, "activation": "linear"}
            ],
            "optimizer": "adam",
            "loss": "mse",
            "learning_rate": 0.001
        },
        dataset_config={
            "type": "synthetic",
            "num_samples": 5000,
            "num_features": 50
        },
        training_config={
            "epochs": 10,
            "batch_size": 64
        },
        distribution_strategy=DistributionStrategy.DATA_PARALLEL,
        required_devices=2,
        priority=1
    )
    
    # Submit job
    job_id = trainer.submit_job(job_config)
    print(f"Job submitted with ID: {job_id}")
    
    # Schedule and monitor job
    print("\n3. Running Distributed Training")
    print("-" * 50)
    
    trainer.schedule_jobs()
    
    # Monitor progress
    for i in range(15):
        status = trainer.get_job_status(job_id)
        print(f"Job status: {status.get('status', 'unknown')}")
        
        if status.get('status') == 'completed':
            print(f"Training completed! Final loss: {status.get('final_loss', 'N/A'):.4f}")
            print(f"Total time: {status.get('total_time', 0):.2f} seconds")
            break
        elif status.get('status') == 'failed':
            print(f"Training failed: {status.get('error', 'Unknown error')}")
            break
        
        time.sleep(2)
    
    # Get cluster status
    cluster_status = trainer.get_cluster_status()
    print(f"\nCluster utilization: {cluster_status['cluster_utilization']:.1%}")
    
    return trainer

def demo_quantum_neural_networks():
    """Demonstrate quantum-classical hybrid neural networks."""
    print("\n" + "=" * 70)
    print("QUANTUM-CLASSICAL HYBRID NEURAL NETWORKS DEMONSTRATION")
    print("=" * 70)
    
    # Create quantum classifier
    print("\n1. Building Quantum-Classical Hybrid Classifier")
    print("-" * 50)
    
    quantum_model = create_quantum_classifier(
        input_dim=4,
        num_classes=3,
        num_qubits=4,
        num_layers=2
    )
    
    # Compile hybrid model
    quantum_model.compile_hybrid(
        quantum_optimizer="parameter_shift",
        classical_optimizer="adam",
        loss="categorical_crossentropy",
        learning_rate=0.01
    )
    
    # Print quantum circuit summary
    quantum_model.quantum_circuit_summary()
    
    # Create synthetic quantum dataset
    print("\n2. Training Hybrid Model")
    print("-" * 50)
    
    X_quantum = np.random.randn(200, 4)  # 4 features
    y_quantum = np.random.randint(0, 3, (200, 3))  # 3 classes (one-hot)
    
    # Train hybrid model
    hybrid_history = quantum_model.fit_hybrid(
        X_quantum, y_quantum,
        epochs=5,
        batch_size=16,
        quantum_shots=1000,
        verbose=1
    )
    
    # Test quantum predictions
    X_test_quantum = np.random.randn(20, 4)
    quantum_predictions = quantum_model.predict(X_test_quantum)
    
    print(f"\nQuantum predictions shape: {quantum_predictions.shape}")
    print(f"Sample quantum prediction: {quantum_predictions[0]}")
    
    # Manual quantum layer demo
    print("\n3. Manual Quantum Layer Construction")
    print("-" * 50)
    
    from src.quantum_neural_networks import QuantumDense, QuantumLayerConfig
    
    # Create quantum layer configuration
    config = QuantumLayerConfig(
        num_qubits=3,
        num_layers=2,
        entanglement="circular",
        shots=500
    )
    
    # Create quantum dense layer
    quantum_layer = QuantumDense(units=5, config=config, activation="quantum")
    
    # Test quantum layer
    test_input = np.random.randn(10, 6)  # 10 samples, 6 features
    quantum_output = quantum_layer.forward(test_input)
    
    print(f"Quantum layer output shape: {quantum_output.shape}")
    print(f"Quantum layer parameters: {len(quantum_layer.parameters)}")
    
    return quantum_model

def demo_gpu_acceleration():
    """Demonstrate GPU acceleration capabilities."""
    print("\n" + "=" * 70)
    print("GPU ACCELERATION DEMONSTRATION")
    print("=" * 70)
    
    # Create GPU manager
    print("\n1. Initializing GPU Manager")
    print("-" * 50)
    
    gpu_manager = create_gpu_manager(auto_detect=True)
    
    # Display GPU information
    gpu_info = gpu_manager.get_device_info()
    print("Available GPUs:")
    for device_info in gpu_info:
        print(f"  Device {device_info['device_id']}: {device_info['name']}")
        print(f"    Memory: {device_info['memory_total_gb']:.1f}GB")
        print(f"    Backend: {device_info['backend']}")
    
    # Benchmark GPU performance
    print("\n2. GPU Performance Benchmarking")
    print("-" * 50)
    
    if gpu_manager.devices:
        device_id = 0
        benchmark_results = gpu_manager.benchmark_device(
            device_id=device_id,
            matrix_sizes=[512, 1024]
        )
        
        print(f"\nBenchmark results for Device {device_id}:")
        for test_name, results in benchmark_results.items():
            print(f"  {test_name}: {results['speedup']:.1f}x speedup")
    
    # Test tensor operations
    print("\n3. Accelerated Tensor Operations")
    print("-" * 50)
    
    if gpu_manager.devices:
        # Create test matrices
        A = np.random.randn(1000, 1000).astype(np.float32)
        B = np.random.randn(1000, 1000).astype(np.float32)
        
        # Move to GPU
        A_gpu = gpu_manager.accelerate_tensor(A)
        B_gpu = gpu_manager.accelerate_tensor(B)
        
        print("Tensors moved to GPU successfully")
        
        # Perform GPU matrix multiplication
        start_time = time.time()
        result_gpu_id = gpu_manager.execute_on_gpu("matmul", [A_gpu, B_gpu])
        gpu_time = time.time() - start_time
        
        # CPU comparison
        start_time = time.time()
        cpu_result = np.dot(A, B)
        cpu_time = time.time() - start_time
        
        print(f"GPU matmul time: {gpu_time*1000:.2f}ms")
        print(f"CPU matmul time: {cpu_time*1000:.2f}ms")
        print(f"Speedup: {cpu_time/gpu_time:.1f}x")
        
        # Get memory statistics
        memory_stats = gpu_manager.tensor_accelerators[0].get_memory_stats()
        print(f"GPU memory usage: {memory_stats['utilization_percent']:.1f}%")
    
    # Enable model GPU acceleration
    print("\n4. Model GPU Acceleration")
    print("-" * 50)
    
    # Create model and enable GPU acceleration
    gpu_model = NeuralNetwork("GPUAcceleratedModel")
    gpu_model.add(Dense(units=256, activation='relu'))
    gpu_model.add(Dense(units=128, activation='relu'))
    gpu_model.add(Dense(units=1, activation='linear'))
    
    gpu_model.compile(optimizer='adam', loss='mse')
    gpu_model.enable_gpu_acceleration()
    
    print("Model GPU acceleration enabled")
    
    return gpu_manager

def demo_model_deployment():
    """Demonstrate model deployment and serving."""
    print("\n" + "=" * 70)
    print("MODEL DEPLOYMENT AND SERVING DEMONSTRATION")
    print("=" * 70)
    
    # Create model for deployment
    print("\n1. Preparing Model for Deployment")
    print("-" * 50)
    
    deployment_model = NeuralNetwork("ProductionModel")
    deployment_model.add(Dense(units=64, activation='relu', name='input_layer'))
    deployment_model.add(Dense(units=32, activation='relu', name='hidden_layer'))
    deployment_model.add(Dense(units=3, activation='softmax', name='output_layer'))
    
    deployment_model.compile(optimizer='adam', loss='categorical_crossentropy')
    
    # Train model briefly
    X_deploy = np.random.randn(100, 10)
    y_deploy = np.random.randint(0, 3, (100, 3))
    deployment_model.fit(X_deploy, y_deploy, epochs=3, verbose=0)
    
    print("Model trained and ready for deployment")
    
    # Create model server
    print("\n2. Setting Up Model Server")
    print("-" * 50)
    
    server = create_model_server(host="localhost", port=8080)
    
    # Register model with preprocessing/postprocessing
    preprocessing_config = {
        'normalization': 'zscore',
        'reshape': [-1, 10]
    }
    
    postprocessing_config = {
        'output_format': 'probabilities',
        'confidence_threshold': 0.5,
        'top_k': 2
    }
    
    server.register_model(
        model=deployment_model,
        model_id="production_classifier",
        preprocessing_config=preprocessing_config,
        postprocessing_config=postprocessing_config
    )
    
    print("Model registered with server")
    
    # Test single prediction
    print("\n3. Testing Model Serving")
    print("-" * 50)
    
    from src.model_deployment import InferenceRequest
    
    test_request = InferenceRequest(
        request_id="test_001",
        model_id="production_classifier",
        input_data=np.random.randn(1, 10)
    )
    
    response = server.predict(test_request)
    
    print(f"Prediction successful!")
    print(f"Request ID: {response.request_id}")
    print(f"Processing time: {response.processing_time_ms:.2f}ms")
    print(f"Predictions: {response.predictions}")
    if response.confidence_scores is not None:
        print(f"Confidence: {response.confidence_scores}")
    
    # Test batch prediction
    batch_requests = [
        InferenceRequest(
            request_id=f"batch_{i}",
            model_id="production_classifier",
            input_data=np.random.randn(1, 10)
        ) for i in range(5)
    ]
    
    batch_responses = server.predict_batch(batch_requests)
    
    print(f"\nBatch prediction completed!")
    print(f"Processed {len(batch_responses)} requests")
    avg_time = np.mean([r.processing_time_ms for r in batch_responses])
    print(f"Average processing time: {avg_time:.2f}ms")
    
    # Get server statistics
    stats = server.get_server_stats()
    print(f"\nServer Statistics:")
    print(f"  Total requests: {stats['total_requests']}")
    print(f"  Error rate: {stats['error_rate']:.2%}")
    print(f"  Avg processing time: {stats['avg_processing_time_ms']:.2f}ms")
    
    # Cloud deployment demo
    print("\n4. Cloud Deployment Simulation")
    print("-" * 50)
    
    cloud_deployment = CloudDeployment(DeploymentTarget.AWS_LAMBDA)
    
    deployment_config = {
        'memory_mb': 1024,
        'timeout_seconds': 60
    }
    
    deployment_result = cloud_deployment.deploy_model(
        model=deployment_model,
        model_id="production_classifier",
        deployment_config=deployment_config
    )
    
    print(f"Cloud deployment result:")
    print(f"  Status: {deployment_result['status']}")
    print(f"  Endpoint: {deployment_result['endpoint_url']}")
    
    return server

def main():
    """Main demonstration function."""
    print("SYNAPSE LANGUAGE - AI/ML ACCELERATION PLATFORM")
    print("Complete Platform Demonstration")
    print("=" * 70)
    
    try:
        # Demo 1: Neural Network DSL
        model = demo_neural_network_dsl()
        
        # Demo 2: AutoML Optimization
        automl_results = demo_automl_optimization()
        
        # Demo 3: Distributed Training
        distributed_trainer = demo_distributed_training()
        
        # Demo 4: Quantum-Classical Hybrid Networks
        quantum_model = demo_quantum_neural_networks()
        
        # Demo 5: GPU Acceleration
        gpu_manager = demo_gpu_acceleration()
        
        # Demo 6: Model Deployment
        model_server = demo_model_deployment()
        
        # Final summary
        print("\n" + "=" * 70)
        print("PLATFORM DEMONSTRATION COMPLETE!")
        print("=" * 70)
        print("\nSuccessfully demonstrated:")
        print("  ✓ Neural Network DSL with custom architectures")
        print("  ✓ AutoML hyperparameter optimization")
        print("  ✓ Multi-GPU distributed training")
        print("  ✓ Quantum-classical hybrid models")
        print("  ✓ GPU acceleration and performance optimization")
        print("  ✓ Model deployment and serving")
        print("\nThe Synapse Language AI/ML platform is ready for")
        print("quantum-enhanced machine learning at scale!")
        
        return 0
        
    except Exception as e:
        print(f"\n[ERROR] Platform demonstration failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)