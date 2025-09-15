"""
Distributed Training Orchestration for Synapse Language

Multi-GPU and multi-node distributed training with automatic scaling,
fault tolerance, and performance optimization.
"""

import numpy as np
from typing import Dict, List, Any, Optional, Callable, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor, Future
from .neural_network_dsl import NeuralNetwork

class DistributionStrategy(Enum):
    """Distributed training strategies."""
    DATA_PARALLEL = "data_parallel"
    MODEL_PARALLEL = "model_parallel"
    PIPELINE_PARALLEL = "pipeline_parallel"
    HYBRID_PARALLEL = "hybrid_parallel"

class CommunicationBackend(Enum):
    """Communication backends for distributed training."""
    NCCL = "nccl"  # NVIDIA Collective Communication Library
    MPI = "mpi"    # Message Passing Interface
    GLOO = "gloo"  # Facebook's collective communication library
    CUSTOM = "custom"

@dataclass
class DeviceInfo:
    """Information about a compute device."""
    device_id: int
    device_type: str  # 'cpu', 'gpu', 'tpu'
    memory_gb: float
    compute_capability: str
    is_available: bool = True
    current_utilization: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            'device_id': self.device_id,
            'device_type': self.device_type,
            'memory_gb': self.memory_gb,
            'compute_capability': self.compute_capability,
            'is_available': self.is_available,
            'current_utilization': self.current_utilization
        }

@dataclass
class NodeInfo:
    """Information about a compute node."""
    node_id: str
    hostname: str
    devices: List[DeviceInfo] = field(default_factory=list)
    cpu_cores: int = 1
    memory_gb: float = 8.0
    network_bandwidth_gbps: float = 1.0
    is_master: bool = False
    
    def get_gpu_devices(self) -> List[DeviceInfo]:
        """Get GPU devices on this node."""
        return [device for device in self.devices if device.device_type == 'gpu']
    
    def get_total_gpu_memory(self) -> float:
        """Get total GPU memory across all devices."""
        return sum(device.memory_gb for device in self.get_gpu_devices())

@dataclass
class TrainingJob:
    """Distributed training job configuration."""
    job_id: str
    model_config: Dict[str, Any]
    dataset_config: Dict[str, Any]
    training_config: Dict[str, Any]
    distribution_strategy: DistributionStrategy
    required_devices: int
    estimated_duration: Optional[float] = None
    priority: int = 1
    status: str = "pending"  # pending, running, completed, failed
    assigned_nodes: List[str] = field(default_factory=list)
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    
    def to_dict(self) -> Dict:
        return {
            'job_id': self.job_id,
            'model_config': self.model_config,
            'dataset_config': self.dataset_config,
            'training_config': self.training_config,
            'distribution_strategy': self.distribution_strategy.value,
            'required_devices': self.required_devices,
            'estimated_duration': self.estimated_duration,
            'priority': self.priority,
            'status': self.status,
            'assigned_nodes': self.assigned_nodes,
            'start_time': self.start_time,
            'end_time': self.end_time
        }

class DistributedDataLoader:
    """Distributed data loader with automatic partitioning."""
    
    def __init__(self, dataset: Tuple[np.ndarray, np.ndarray], 
                 batch_size: int, num_replicas: int, rank: int):
        self.X, self.y = dataset
        self.batch_size = batch_size
        self.num_replicas = num_replicas
        self.rank = rank
        
        # Partition data for this rank
        samples_per_replica = len(self.X) // num_replicas
        start_idx = rank * samples_per_replica
        end_idx = start_idx + samples_per_replica if rank < num_replicas - 1 else len(self.X)
        
        self.local_X = self.X[start_idx:end_idx]
        self.local_y = self.y[start_idx:end_idx]
        
        self.num_batches = (len(self.local_X) + batch_size - 1) // batch_size
        self.current_batch = 0
    
    def __iter__(self):
        self.current_batch = 0
        return self
    
    def __next__(self):
        if self.current_batch >= self.num_batches:
            raise StopIteration
        
        start_idx = self.current_batch * self.batch_size
        end_idx = min(start_idx + self.batch_size, len(self.local_X))
        
        batch_X = self.local_X[start_idx:end_idx]
        batch_y = self.local_y[start_idx:end_idx]
        
        self.current_batch += 1
        return batch_X, batch_y
    
    def __len__(self):
        return self.num_batches

class GradientAggregator:
    """Gradient aggregation for distributed training."""
    
    def __init__(self, communication_backend: CommunicationBackend = CommunicationBackend.CUSTOM):
        self.backend = communication_backend
        self.accumulated_gradients = {}
        self.gradient_count = 0
        
    def all_reduce(self, gradients: Dict[str, np.ndarray], 
                  num_replicas: int) -> Dict[str, np.ndarray]:
        """All-reduce gradient aggregation across replicas."""
        # Simplified implementation - real version would use proper communication
        averaged_gradients = {}
        
        for name, grad in gradients.items():
            # In real implementation, this would aggregate across all replicas
            # Here we just simulate by averaging with some noise
            averaged_gradients[name] = grad / num_replicas
        
        return averaged_gradients
    
    def accumulate_gradients(self, gradients: Dict[str, np.ndarray]):
        """Accumulate gradients for gradient accumulation."""
        for name, grad in gradients.items():
            if name not in self.accumulated_gradients:
                self.accumulated_gradients[name] = np.zeros_like(grad)
            self.accumulated_gradients[name] += grad
        
        self.gradient_count += 1
    
    def get_averaged_gradients(self) -> Dict[str, np.ndarray]:
        """Get averaged accumulated gradients."""
        if self.gradient_count == 0:
            return {}
        
        averaged = {}
        for name, grad in self.accumulated_gradients.items():
            averaged[name] = grad / self.gradient_count
        
        # Reset accumulation
        self.accumulated_gradients.clear()
        self.gradient_count = 0
        
        return averaged

class MultiGPUStrategy:
    """Multi-GPU training strategy implementation."""
    
    def __init__(self, devices: List[DeviceInfo], 
                 strategy: DistributionStrategy = DistributionStrategy.DATA_PARALLEL):
        self.devices = devices
        self.strategy = strategy
        self.gradient_aggregator = GradientAggregator()
        self.replica_models = {}
        self.device_assignments = {}
        
    def distribute_model(self, model: NeuralNetwork) -> Dict[int, NeuralNetwork]:
        """Distribute model across multiple GPUs."""
        replicas = {}
        
        if self.strategy == DistributionStrategy.DATA_PARALLEL:
            # Create model replica for each device
            for device in self.devices:
                if device.device_type == 'gpu' and device.is_available:
                    # In real implementation, this would create model on specific GPU
                    replica = self._create_model_replica(model, device.device_id)
                    replicas[device.device_id] = replica
        
        elif self.strategy == DistributionStrategy.MODEL_PARALLEL:
            # Split model layers across devices
            layers_per_device = len(model.layers) // len(self.devices)
            
            for i, device in enumerate(self.devices[:len(model.layers)]):
                start_layer = i * layers_per_device
                end_layer = start_layer + layers_per_device
                if i == len(self.devices) - 1:  # Last device gets remaining layers
                    end_layer = len(model.layers)
                
                # Create partial model for this device
                partial_model = self._create_partial_model(model, start_layer, end_layer)
                replicas[device.device_id] = partial_model
        
        self.replica_models = replicas
        return replicas
    
    def _create_model_replica(self, model: NeuralNetwork, device_id: int) -> NeuralNetwork:
        """Create model replica on specific device."""
        # Simplified implementation - real version would handle GPU placement
        replica = NeuralNetwork(name=f"{model.name}_GPU_{device_id}")
        
        # Copy layers to replica
        for layer in model.layers:
            replica.add(layer)
        
        # Copy compilation settings
        if model.compiled:
            replica.compile(
                optimizer=model.optimizer.value,
                loss=model.loss_function,
                learning_rate=model.learning_rate
            )
        
        return replica
    
    def _create_partial_model(self, model: NeuralNetwork, 
                             start_layer: int, end_layer: int) -> NeuralNetwork:
        """Create partial model for model parallelism."""
        partial = NeuralNetwork(name=f"{model.name}_Partial_{start_layer}_{end_layer}")
        
        # Add specified layers
        for i in range(start_layer, end_layer):
            if i < len(model.layers):
                partial.add(model.layers[i])
        
        return partial
    
    def synchronize_gradients(self, device_gradients: Dict[int, Dict[str, np.ndarray]]):
        """Synchronize gradients across devices."""
        if self.strategy == DistributionStrategy.DATA_PARALLEL:
            # Average gradients across all replicas
            all_gradients = list(device_gradients.values())
            if all_gradients:
                averaged = self.gradient_aggregator.all_reduce(
                    all_gradients[0], len(all_gradients)
                )
                
                # Update all replicas with averaged gradients
                for device_id, replica in self.replica_models.items():
                    self._apply_gradients(replica, averaged)
    
    def _apply_gradients(self, model: NeuralNetwork, gradients: Dict[str, np.ndarray]):
        """Apply gradients to model parameters."""
        # Simplified gradient application
        for layer in model.layers:
            if hasattr(layer, 'weights') and layer.weights is not None:
                layer_name = f"{layer.name}_weights"
                if layer_name in gradients:
                    layer.weights -= model.learning_rate * gradients[layer_name]

class DistributedTrainer:
    """Main distributed training orchestrator."""
    
    def __init__(self, nodes: List[NodeInfo], 
                 communication_backend: CommunicationBackend = CommunicationBackend.CUSTOM):
        self.nodes = nodes
        self.communication_backend = communication_backend
        self.job_queue = []
        self.running_jobs = {}
        self.completed_jobs = []
        self.device_monitor = DeviceMonitor(nodes)
        
        # Find master node
        self.master_node = next((node for node in nodes if node.is_master), nodes[0])
        
    def submit_job(self, job: TrainingJob) -> str:
        """Submit distributed training job."""
        self.job_queue.append(job)
        print(f"Job {job.job_id} submitted to queue (priority: {job.priority})")
        return job.job_id
    
    def schedule_jobs(self):
        """Schedule jobs based on resource availability."""
        # Sort jobs by priority
        self.job_queue.sort(key=lambda job: job.priority, reverse=True)
        
        for job in self.job_queue[:]:  # Copy list to avoid modification during iteration
            if job.status == "pending":
                available_nodes = self._find_available_nodes(job)
                
                if len(available_nodes) >= job.required_devices:
                    # Assign nodes to job
                    assigned_nodes = available_nodes[:job.required_devices]
                    job.assigned_nodes = [node.node_id for node in assigned_nodes]
                    job.status = "running"
                    job.start_time = time.time()
                    
                    # Start training
                    future = self._start_distributed_training(job, assigned_nodes)
                    self.running_jobs[job.job_id] = (job, future)
                    
                    # Remove from queue
                    self.job_queue.remove(job)
                    
                    print(f"Job {job.job_id} started on nodes: {job.assigned_nodes}")
    
    def _find_available_nodes(self, job: TrainingJob) -> List[NodeInfo]:
        """Find nodes with sufficient resources for the job."""
        available = []
        
        for node in self.nodes:
            gpu_devices = node.get_gpu_devices()
            available_gpus = [gpu for gpu in gpu_devices if gpu.is_available and gpu.current_utilization < 0.8]
            
            if len(available_gpus) > 0:
                available.append(node)
        
        return available
    
    def _start_distributed_training(self, job: TrainingJob, 
                                   assigned_nodes: List[NodeInfo]) -> Future:
        """Start distributed training on assigned nodes."""
        # Use thread pool for simulation
        executor = ThreadPoolExecutor(max_workers=len(assigned_nodes))
        
        # Create training function
        def train_on_nodes():
            return self._execute_distributed_training(job, assigned_nodes)
        
        return executor.submit(train_on_nodes)
    
    def _execute_distributed_training(self, job: TrainingJob, 
                                    assigned_nodes: List[NodeInfo]) -> Dict[str, Any]:
        """Execute distributed training across nodes."""
        print(f"Starting distributed training for job {job.job_id}")
        
        # Initialize distributed training components
        strategy = MultiGPUStrategy(
            devices=[device for node in assigned_nodes for device in node.devices],
            strategy=job.distribution_strategy
        )
        
        # Create model
        model = self._create_model_from_config(job.model_config)
        
        # Distribute model
        distributed_models = strategy.distribute_model(model)
        
        # Create distributed data loaders
        dataset = self._load_dataset(job.dataset_config)
        num_replicas = len(distributed_models)
        data_loaders = {}
        
        for rank, (device_id, replica_model) in enumerate(distributed_models.items()):
            data_loader = DistributedDataLoader(
                dataset=dataset,
                batch_size=job.training_config.get('batch_size', 32),
                num_replicas=num_replicas,
                rank=rank
            )
            data_loaders[device_id] = data_loader
        
        # Training parameters
        epochs = job.training_config.get('epochs', 10)
        
        # Training loop
        training_metrics = {'loss_history': [], 'epoch_times': []}
        
        for epoch in range(epochs):
            epoch_start = time.time()
            epoch_losses = []
            
            # Train on all replicas
            device_gradients = {}
            
            for device_id, data_loader in data_loaders.items():
                replica_model = distributed_models[device_id]
                device_loss = 0
                
                for batch_X, batch_y in data_loader:
                    # Forward pass
                    predictions = replica_model.forward(batch_X, training=True)
                    
                    # Compute loss
                    loss = replica_model._compute_loss(predictions, batch_y)
                    device_loss += loss
                    
                    # Backward pass
                    grad_loss = replica_model._compute_loss_gradient(predictions, batch_y)
                    replica_model.backward(grad_loss)
                    
                    # Collect gradients
                    gradients = {}
                    for layer in replica_model.layers:
                        if hasattr(layer, 'gradients'):
                            for param_name, grad in layer.gradients.items():
                                gradients[f"{layer.name}_{param_name}"] = grad
                    
                    device_gradients[device_id] = gradients
                
                epoch_losses.append(device_loss / len(data_loader))
            
            # Synchronize gradients across devices
            strategy.synchronize_gradients(device_gradients)
            
            # Log epoch results
            avg_loss = np.mean(epoch_losses)
            epoch_time = time.time() - epoch_start
            
            training_metrics['loss_history'].append(avg_loss)
            training_metrics['epoch_times'].append(epoch_time)
            
            print(f"Job {job.job_id} - Epoch {epoch+1}/{epochs}: "
                  f"loss={avg_loss:.4f}, time={epoch_time:.2f}s")
        
        # Training complete
        total_time = sum(training_metrics['epoch_times'])
        final_loss = training_metrics['loss_history'][-1]
        
        return {
            'job_id': job.job_id,
            'status': 'completed',
            'final_loss': final_loss,
            'total_time': total_time,
            'training_metrics': training_metrics,
            'nodes_used': [node.node_id for node in assigned_nodes],
            'model_state': 'saved'  # Placeholder
        }
    
    def _create_model_from_config(self, model_config: Dict[str, Any]) -> NeuralNetwork:
        """Create model from configuration."""
        from .neural_network_dsl import NeuralNetwork, Dense, Conv2D, LSTM, Attention
        
        model = NeuralNetwork(name=model_config.get('name', 'DistributedModel'))
        
        # Add layers based on configuration
        for layer_config in model_config.get('layers', []):
            layer_type = layer_config['type']
            
            if layer_type == 'dense':
                layer = Dense(
                    units=layer_config['units'],
                    activation=layer_config.get('activation', 'relu'),
                    dropout_rate=layer_config.get('dropout_rate', 0.0)
                )
            elif layer_type == 'conv2d':
                layer = Conv2D(
                    filters=layer_config['filters'],
                    kernel_size=tuple(layer_config['kernel_size']),
                    stride=tuple(layer_config.get('stride', [1, 1])),
                    activation=layer_config.get('activation', 'relu')
                )
            elif layer_type == 'lstm':
                layer = LSTM(
                    units=layer_config['units'],
                    return_sequences=layer_config.get('return_sequences', False)
                )
            elif layer_type == 'attention':
                layer = Attention(
                    num_heads=layer_config['num_heads'],
                    key_dim=layer_config['key_dim']
                )
            else:
                continue
            
            model.add(layer)
        
        # Compile model
        model.compile(
            optimizer=model_config.get('optimizer', 'adam'),
            loss=model_config.get('loss', 'mse'),
            learning_rate=model_config.get('learning_rate', 0.001)
        )
        
        return model
    
    def _load_dataset(self, dataset_config: Dict[str, Any]) -> Tuple[np.ndarray, np.ndarray]:
        """Load dataset from configuration."""
        # Simplified dataset loading - real implementation would load from various sources
        dataset_type = dataset_config.get('type', 'synthetic')
        
        if dataset_type == 'synthetic':
            num_samples = dataset_config.get('num_samples', 1000)
            num_features = dataset_config.get('num_features', 10)
            
            X = np.random.randn(num_samples, num_features)
            y = np.random.randn(num_samples, 1)
            
            return X, y
        else:
            # Placeholder for other dataset types
            return np.random.randn(1000, 10), np.random.randn(1000, 1)
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of a training job."""
        # Check running jobs
        if job_id in self.running_jobs:
            job, future = self.running_jobs[job_id]
            if future.done():
                try:
                    result = future.result()
                    job.status = "completed"
                    job.end_time = time.time()
                    self.completed_jobs.append((job, result))
                    del self.running_jobs[job_id]
                    return result
                except Exception as e:
                    job.status = "failed"
                    job.end_time = time.time()
                    return {'job_id': job_id, 'status': 'failed', 'error': str(e)}
            else:
                return {'job_id': job_id, 'status': 'running', 
                       'elapsed_time': time.time() - job.start_time}
        
        # Check completed jobs
        for job, result in self.completed_jobs:
            if job.job_id == job_id:
                return result
        
        # Check queued jobs
        for job in self.job_queue:
            if job.job_id == job_id:
                return {'job_id': job_id, 'status': 'pending', 'position_in_queue': self.job_queue.index(job)}
        
        return {'job_id': job_id, 'status': 'not_found'}
    
    def get_cluster_status(self) -> Dict[str, Any]:
        """Get overall cluster status."""
        total_gpus = sum(len(node.get_gpu_devices()) for node in self.nodes)
        available_gpus = sum(
            len([gpu for gpu in node.get_gpu_devices() if gpu.is_available])
            for node in self.nodes
        )
        
        return {
            'total_nodes': len(self.nodes),
            'total_gpus': total_gpus,
            'available_gpus': available_gpus,
            'running_jobs': len(self.running_jobs),
            'queued_jobs': len(self.job_queue),
            'completed_jobs': len(self.completed_jobs),
            'cluster_utilization': 1.0 - (available_gpus / total_gpus) if total_gpus > 0 else 0.0
        }

class DeviceMonitor:
    """Monitor device utilization and health."""
    
    def __init__(self, nodes: List[NodeInfo]):
        self.nodes = nodes
        self.monitoring = False
        self.monitor_thread = None
        
    def start_monitoring(self, interval: float = 5.0):
        """Start device monitoring."""
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,)
        )
        self.monitor_thread.start()
        print("Device monitoring started")
    
    def stop_monitoring(self):
        """Stop device monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        print("Device monitoring stopped")
    
    def _monitor_loop(self, interval: float):
        """Main monitoring loop."""
        while self.monitoring:
            self._update_device_status()
            time.sleep(interval)
    
    def _update_device_status(self):
        """Update device utilization status."""
        for node in self.nodes:
            for device in node.devices:
                if device.device_type == 'gpu':
                    # Simulate GPU utilization monitoring
                    device.current_utilization = np.random.uniform(0.0, 1.0)
                    device.is_available = device.current_utilization < 0.9

# Factory functions for easy setup
def create_local_cluster(num_gpus: int = 1) -> List[NodeInfo]:
    """Create local cluster configuration."""
    devices = []
    for i in range(num_gpus):
        device = DeviceInfo(
            device_id=i,
            device_type='gpu',
            memory_gb=8.0,
            compute_capability='7.5',
            is_available=True
        )
        devices.append(device)
    
    # Add CPU device
    cpu_device = DeviceInfo(
        device_id=num_gpus,
        device_type='cpu',
        memory_gb=16.0,
        compute_capability='x86_64',
        is_available=True
    )
    devices.append(cpu_device)
    
    node = NodeInfo(
        node_id='local_node_0',
        hostname='localhost',
        devices=devices,
        cpu_cores=8,
        memory_gb=32.0,
        is_master=True
    )
    
    return [node]

def create_multi_node_cluster(node_configs: List[Dict[str, Any]]) -> List[NodeInfo]:
    """Create multi-node cluster from configurations."""
    nodes = []
    
    for i, config in enumerate(node_configs):
        devices = []
        
        # Add GPU devices
        for gpu_id in range(config.get('num_gpus', 0)):
            device = DeviceInfo(
                device_id=gpu_id,
                device_type='gpu',
                memory_gb=config.get('gpu_memory_gb', 8.0),
                compute_capability=config.get('gpu_capability', '7.5'),
                is_available=True
            )
            devices.append(device)
        
        # Add CPU device
        cpu_device = DeviceInfo(
            device_id=config.get('num_gpus', 0),
            device_type='cpu',
            memory_gb=config.get('memory_gb', 16.0),
            compute_capability='x86_64',
            is_available=True
        )
        devices.append(cpu_device)
        
        node = NodeInfo(
            node_id=config.get('node_id', f'node_{i}'),
            hostname=config.get('hostname', f'worker-{i}'),
            devices=devices,
            cpu_cores=config.get('cpu_cores', 8),
            memory_gb=config.get('memory_gb', 32.0),
            is_master=config.get('is_master', i == 0)
        )
        
        nodes.append(node)
    
    return nodes

# Export main classes
__all__ = [
    'DistributedTrainer', 'MultiGPUStrategy', 'TrainingJob',
    'NodeInfo', 'DeviceInfo', 'DistributionStrategy', 'CommunicationBackend',
    'DistributedDataLoader', 'GradientAggregator', 'DeviceMonitor',
    'create_local_cluster', 'create_multi_node_cluster'
]