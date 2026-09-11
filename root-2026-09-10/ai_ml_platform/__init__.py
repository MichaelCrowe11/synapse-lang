"""
Synapse Language - AI/ML Acceleration Platform
Quantum-Enhanced Machine Learning with Auto-GPU Scaling

This module provides:
- Neural network DSL with automatic GPU acceleration
- Quantum-classical hybrid model architectures
- AutoML hyperparameter optimization
- Multi-GPU distributed training orchestration
- Model deployment and serving infrastructure
- Integration with quantum computing primitives
"""

from .src.automl_optimizer import (
    AutoMLOptimizer,
    HyperparameterRange,
    HyperparameterSpace,
    create_neural_network_factory,
)
from .src.distributed_training import (
    DistributedTrainer,
    MultiGPUStrategy,
    TrainingJob,
    create_local_cluster,
    create_multi_node_cluster,
)
from .src.gpu_acceleration import GPUDevice, GPUManager, TensorAccelerator, create_gpu_manager
from .src.model_deployment import (
    CloudDeployment,
    InferenceRequest,
    InferenceResponse,
    ModelMetadata,
    ModelServer,
)
from .src.neural_network_dsl import LSTM, Attention, Conv2D, Dense, Layer, NeuralNetwork
from .src.quantum_neural_networks import (
    HybridQNN,
    QuantumAutoencoder,
    QuantumConvLayer,
    QuantumDense,
    QuantumLayer,
    QuantumLayerConfig,
)

__version__ = "3.0.0"
__author__ = "Synapse Language Team"

# Export main classes
__all__ = [
    # Neural Network DSL
    "NeuralNetwork", "Layer", "Dense", "Conv2D", "LSTM", "Attention",

    # Quantum-Neural Hybrids
    "QuantumLayer", "HybridQNN", "QuantumDense", "QuantumConvLayer", "QuantumAutoencoder", "QuantumLayerConfig",

    # AutoML
    "AutoMLOptimizer", "HyperparameterSpace", "HyperparameterRange", "create_neural_network_factory",

    # Distributed Training
    "DistributedTrainer", "MultiGPUStrategy", "TrainingJob", "create_local_cluster", "create_multi_node_cluster",

    # Deployment
    "ModelServer", "CloudDeployment", "InferenceRequest", "InferenceResponse", "ModelMetadata",

    # GPU Acceleration
    "GPUManager", "TensorAccelerator", "GPUDevice", "create_gpu_manager"
]

# AI/ML Platform constants
SUPPORTED_FRAMEWORKS = ["pytorch", "tensorflow", "jax", "quantum"]
GPU_BACKENDS = ["cuda", "rocm", "metal", "opencl"]
OPTIMIZATION_ALGORITHMS = ["adam", "adamw", "sgd", "quantum_natural_gradient"]

def create_hybrid_model(classical_layers: list, quantum_layers: list) -> NeuralNetwork:
    """
    Create a hybrid quantum-classical neural network.

    Args:
        classical_layers: List of classical neural network layers
        quantum_layers: List of quantum circuit layers

    Returns:
        Hybrid NeuralNetwork instance optimized for GPU execution
    """
    model = NeuralNetwork()

    # Add classical preprocessing layers
    for layer in classical_layers:
        model.add(layer)

    # Add quantum processing layers
    for qlayer in quantum_layers:
        model.add(qlayer)

    # Enable automatic GPU acceleration
    model.enable_gpu_acceleration()

    return model

def optimize_hyperparameters(model_factory: callable, search_space: dict,
                           dataset, trials: int = 100) -> dict:
    """
    Automatically optimize hyperparameters using advanced search algorithms.

    Args:
        model_factory: Function that creates model given hyperparameters
        search_space: Dictionary defining hyperparameter ranges
        dataset: Training/validation dataset
        trials: Number of optimization trials

    Returns:
        Best hyperparameters found
    """
    optimizer = AutoMLOptimizer(
        search_space=HyperparameterSpace(search_space),
        max_trials=trials,
        algorithm="bayesian_optimization"
    )

    return optimizer.optimize(model_factory, dataset)
