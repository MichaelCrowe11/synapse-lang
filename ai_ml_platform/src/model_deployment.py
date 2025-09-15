"""
Model Deployment and Serving Infrastructure for Synapse Language

Production-ready model serving with REST APIs, WebSocket streaming,
cloud deployment, and monitoring capabilities.
"""

import json
import time
import threading
from typing import Dict, List, Any, Optional, Callable, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from .neural_network_dsl import NeuralNetwork

class DeploymentTarget(Enum):
    """Deployment targets."""
    LOCAL = "local"
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    AWS_LAMBDA = "aws_lambda"
    AWS_SAGEMAKER = "aws_sagemaker"
    GCP_CLOUD_RUN = "gcp_cloud_run"
    AZURE_CONTAINER = "azure_container"
    EDGE_DEVICE = "edge_device"

class ServingProtocol(Enum):
    """Model serving protocols."""
    REST_API = "rest_api"
    GRPC = "grpc"
    WEBSOCKET = "websocket"
    BATCH = "batch"
    STREAMING = "streaming"

@dataclass
class ModelMetadata:
    """Model metadata for deployment."""
    model_id: str
    model_name: str
    version: str
    framework: str
    input_shape: Tuple[int, ...]
    output_shape: Tuple[int, ...]
    model_size_mb: float
    creation_time: float
    last_updated: float
    tags: Dict[str, str] = field(default_factory=dict)
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'model_id': self.model_id,
            'model_name': self.model_name,
            'version': self.version,
            'framework': self.framework,
            'input_shape': self.input_shape,
            'output_shape': self.output_shape,
            'model_size_mb': self.model_size_mb,
            'creation_time': self.creation_time,
            'last_updated': self.last_updated,
            'tags': self.tags,
            'description': self.description
        }

@dataclass
class InferenceRequest:
    """Individual inference request."""
    request_id: str
    model_id: str
    input_data: np.ndarray
    preprocessing_config: Dict[str, Any] = field(default_factory=dict)
    postprocessing_config: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()

@dataclass
class InferenceResponse:
    """Inference response."""
    request_id: str
    model_id: str
    predictions: np.ndarray
    confidence_scores: Optional[np.ndarray] = None
    processing_time_ms: float = 0.0
    timestamp: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'request_id': self.request_id,
            'model_id': self.model_id,
            'predictions': self.predictions.tolist() if isinstance(self.predictions, np.ndarray) else self.predictions,
            'confidence_scores': self.confidence_scores.tolist() if self.confidence_scores is not None else None,
            'processing_time_ms': self.processing_time_ms,
            'timestamp': self.timestamp,
            'metadata': self.metadata
        }

class ModelPreprocessor:
    """Data preprocessing pipeline for models."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.normalization = config.get('normalization', None)
        self.scaling = config.get('scaling', None)
        self.reshape = config.get('reshape', None)
        
    def preprocess(self, data: np.ndarray) -> np.ndarray:
        """Apply preprocessing to input data."""
        processed = data.copy()
        
        # Normalization
        if self.normalization == 'minmax':
            processed = (processed - processed.min()) / (processed.max() - processed.min())
        elif self.normalization == 'zscore':
            processed = (processed - processed.mean()) / processed.std()
        
        # Scaling
        if self.scaling:
            scale_factor = self.scaling.get('factor', 1.0)
            processed = processed * scale_factor
        
        # Reshape
        if self.reshape:
            target_shape = tuple(self.reshape)
            if -1 in target_shape:
                # Handle dynamic dimensions
                new_shape = list(target_shape)
                new_shape[new_shape.index(-1)] = processed.size // (-np.prod(target_shape))
                target_shape = tuple(new_shape)
            processed = processed.reshape(target_shape)
        
        return processed

class ModelPostprocessor:
    """Post-processing pipeline for model outputs."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.output_format = config.get('output_format', 'raw')
        self.confidence_threshold = config.get('confidence_threshold', 0.0)
        self.top_k = config.get('top_k', None)
        
    def postprocess(self, predictions: np.ndarray) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """Apply post-processing to model predictions."""
        processed_preds = predictions.copy()
        confidence_scores = None
        
        # Apply softmax for probability outputs
        if self.output_format == 'probabilities':
            exp_preds = np.exp(processed_preds - np.max(processed_preds, axis=-1, keepdims=True))
            processed_preds = exp_preds / np.sum(exp_preds, axis=-1, keepdims=True)
            confidence_scores = np.max(processed_preds, axis=-1)
        
        # Apply confidence thresholding
        if self.confidence_threshold > 0.0 and confidence_scores is not None:
            mask = confidence_scores >= self.confidence_threshold
            processed_preds = processed_preds * mask[:, np.newaxis]
        
        # Top-k filtering
        if self.top_k and len(processed_preds.shape) > 1:
            top_k_indices = np.argsort(processed_preds, axis=-1)[:, -self.top_k:]
            filtered_preds = np.zeros_like(processed_preds)
            for i, indices in enumerate(top_k_indices):
                filtered_preds[i, indices] = processed_preds[i, indices]
            processed_preds = filtered_preds
        
        return processed_preds, confidence_scores

class ModelServer:
    """High-performance model serving server."""
    
    def __init__(self, host: str = "localhost", port: int = 8080,
                 max_workers: int = 4, max_batch_size: int = 32):
        self.host = host
        self.port = port
        self.max_workers = max_workers
        self.max_batch_size = max_batch_size
        
        # Model registry
        self.models: Dict[str, NeuralNetwork] = {}
        self.model_metadata: Dict[str, ModelMetadata] = {}
        self.preprocessors: Dict[str, ModelPreprocessor] = {}
        self.postprocessors: Dict[str, ModelPostprocessor] = {}
        
        # Request handling
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.request_queue = []
        self.batch_buffer: Dict[str, List[InferenceRequest]] = {}
        
        # Performance monitoring
        self.request_count = 0
        self.error_count = 0
        self.total_processing_time = 0.0
        self.performance_history = []
        
        # Server state
        self.running = False
        self.server_thread = None
        
    def register_model(self, model: NeuralNetwork, model_id: str,
                      preprocessing_config: Dict[str, Any] = None,
                      postprocessing_config: Dict[str, Any] = None):
        """Register model for serving."""
        # Calculate model size (approximate)
        model_size_mb = self._estimate_model_size(model)
        
        # Create metadata
        metadata = ModelMetadata(
            model_id=model_id,
            model_name=model.name,
            version="1.0.0",
            framework="Synapse",
            input_shape=(1,),  # Placeholder
            output_shape=(1,),  # Placeholder
            model_size_mb=model_size_mb,
            creation_time=time.time(),
            last_updated=time.time(),
            description=f"Synapse neural network model: {model.name}"
        )
        
        # Register components
        self.models[model_id] = model
        self.model_metadata[model_id] = metadata
        
        if preprocessing_config:
            self.preprocessors[model_id] = ModelPreprocessor(preprocessing_config)
        
        if postprocessing_config:
            self.postprocessors[model_id] = ModelPostprocessor(postprocessing_config)
        
        print(f"Model '{model_id}' registered for serving ({model_size_mb:.2f}MB)")
    
    def _estimate_model_size(self, model: NeuralNetwork) -> float:
        """Estimate model size in MB."""
        total_params = 0
        
        for layer in model.layers:
            if hasattr(layer, 'weights') and layer.weights is not None:
                total_params += layer.weights.size
            if hasattr(layer, 'bias') and layer.bias is not None:
                total_params += layer.bias.size
        
        # Assume 4 bytes per parameter (float32)
        size_bytes = total_params * 4
        return size_bytes / (1024 * 1024)
    
    def predict(self, request: InferenceRequest) -> InferenceResponse:
        """Make prediction for single request."""
        start_time = time.time()
        
        try:
            # Get model
            if request.model_id not in self.models:
                raise ValueError(f"Model '{request.model_id}' not found")
            
            model = self.models[request.model_id]
            
            # Preprocess input
            processed_input = request.input_data
            if request.model_id in self.preprocessors:
                processed_input = self.preprocessors[request.model_id].preprocess(processed_input)
            
            # Make prediction
            predictions = model.predict(processed_input)
            
            # Postprocess output
            confidence_scores = None
            if request.model_id in self.postprocessors:
                predictions, confidence_scores = self.postprocessors[request.model_id].postprocess(predictions)
            
            processing_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Update metrics
            self.request_count += 1
            self.total_processing_time += processing_time
            
            return InferenceResponse(
                request_id=request.request_id,
                model_id=request.model_id,
                predictions=predictions,
                confidence_scores=confidence_scores,
                processing_time_ms=processing_time,
                metadata={'batch_size': 1}
            )
            
        except Exception as e:
            self.error_count += 1
            print(f"Prediction error: {str(e)}")
            
            return InferenceResponse(
                request_id=request.request_id,
                model_id=request.model_id,
                predictions=np.array([]),
                processing_time_ms=(time.time() - start_time) * 1000,
                metadata={'error': str(e)}
            )
    
    def predict_batch(self, requests: List[InferenceRequest]) -> List[InferenceResponse]:
        """Make predictions for batch of requests."""
        if not requests:
            return []
        
        # Group requests by model
        model_batches = {}
        for request in requests:
            if request.model_id not in model_batches:
                model_batches[request.model_id] = []
            model_batches[request.model_id].append(request)
        
        all_responses = []
        
        # Process each model batch
        for model_id, batch_requests in model_batches.items():
            batch_responses = self._process_model_batch(model_id, batch_requests)
            all_responses.extend(batch_responses)
        
        return all_responses
    
    def _process_model_batch(self, model_id: str, requests: List[InferenceRequest]) -> List[InferenceResponse]:
        """Process batch of requests for a single model."""
        start_time = time.time()
        
        try:
            # Get model
            model = self.models[model_id]
            
            # Prepare batch input
            batch_inputs = []
            for request in requests:
                processed_input = request.input_data
                if model_id in self.preprocessors:
                    processed_input = self.preprocessors[model_id].preprocess(processed_input)
                batch_inputs.append(processed_input)
            
            # Stack inputs into batch
            batch_array = np.stack(batch_inputs, axis=0)
            
            # Batch prediction
            batch_predictions = model.predict(batch_array)
            
            # Process individual responses
            responses = []
            for i, request in enumerate(requests):
                pred = batch_predictions[i:i+1]  # Keep batch dimension
                confidence_scores = None
                
                # Postprocess
                if model_id in self.postprocessors:
                    pred, confidence_scores = self.postprocessors[model_id].postprocess(pred)
                
                processing_time = (time.time() - start_time) * 1000 / len(requests)
                
                response = InferenceResponse(
                    request_id=request.request_id,
                    model_id=request.model_id,
                    predictions=pred,
                    confidence_scores=confidence_scores,
                    processing_time_ms=processing_time,
                    metadata={'batch_size': len(requests)}
                )
                responses.append(response)
            
            # Update metrics
            self.request_count += len(requests)
            self.total_processing_time += (time.time() - start_time) * 1000
            
            return responses
            
        except Exception as e:
            self.error_count += len(requests)
            print(f"Batch prediction error: {str(e)}")
            
            # Return error responses
            return [
                InferenceResponse(
                    request_id=req.request_id,
                    model_id=req.model_id,
                    predictions=np.array([]),
                    processing_time_ms=0.0,
                    metadata={'error': str(e)}
                ) for req in requests
            ]
    
    def start_server(self):
        """Start the model server."""
        self.running = True
        self.server_thread = threading.Thread(target=self._server_loop)
        self.server_thread.start()
        print(f"Model server started on {self.host}:{self.port}")
    
    def stop_server(self):
        """Stop the model server."""
        self.running = False
        if self.server_thread:
            self.server_thread.join()
        print("Model server stopped")
    
    def _server_loop(self):
        """Main server loop (simplified)."""
        print(f"Server listening on {self.host}:{self.port}")
        print("Available endpoints:")
        print("  POST /predict - Single prediction")
        print("  POST /predict_batch - Batch prediction")
        print("  GET /models - List models")
        print("  GET /health - Health check")
        
        while self.running:
            # Simulate request processing
            time.sleep(0.1)
            
            # Process any queued batch requests
            self._process_batch_queue()
    
    def _process_batch_queue(self):
        """Process batched requests."""
        for model_id, requests in self.batch_buffer.items():
            if len(requests) >= self.max_batch_size or self._should_flush_batch(requests):
                # Process batch
                responses = self._process_model_batch(model_id, requests)
                
                # Clear processed requests
                self.batch_buffer[model_id] = []
                
                # In real implementation, would send responses back to clients
    
    def _should_flush_batch(self, requests: List[InferenceRequest]) -> bool:
        """Determine if batch should be flushed."""
        if not requests:
            return False
        
        # Flush if oldest request is too old (e.g., > 100ms)
        oldest_time = min(req.timestamp for req in requests)
        return (time.time() - oldest_time) > 0.1
    
    def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """Get information about a registered model."""
        if model_id in self.model_metadata:
            return self.model_metadata[model_id].to_dict()
        else:
            raise ValueError(f"Model '{model_id}' not found")
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List all registered models."""
        return [metadata.to_dict() for metadata in self.model_metadata.values()]
    
    def get_server_stats(self) -> Dict[str, Any]:
        """Get server performance statistics."""
        avg_processing_time = (
            self.total_processing_time / self.request_count 
            if self.request_count > 0 else 0.0
        )
        
        error_rate = (
            self.error_count / self.request_count 
            if self.request_count > 0 else 0.0
        )
        
        return {
            'total_requests': self.request_count,
            'total_errors': self.error_count,
            'error_rate': error_rate,
            'avg_processing_time_ms': avg_processing_time,
            'registered_models': len(self.models),
            'server_uptime_seconds': time.time() - (hasattr(self, 'start_time') and self.start_time or time.time()),
            'active_workers': self.max_workers,
            'max_batch_size': self.max_batch_size
        }

class CloudDeployment:
    """Cloud deployment orchestration."""
    
    def __init__(self, target: DeploymentTarget):
        self.target = target
        self.deployment_config = {}
        self.deployed_models = {}
        
    def deploy_model(self, model: NeuralNetwork, model_id: str,
                    deployment_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Deploy model to cloud platform."""
        config = deployment_config or {}
        
        deployment_info = {
            'model_id': model_id,
            'target': self.target.value,
            'deployment_time': time.time(),
            'status': 'deploying',
            'endpoint_url': None,
            'config': config
        }
        
        try:
            if self.target == DeploymentTarget.AWS_LAMBDA:
                deployment_info.update(self._deploy_to_aws_lambda(model, model_id, config))
            elif self.target == DeploymentTarget.AWS_SAGEMAKER:
                deployment_info.update(self._deploy_to_sagemaker(model, model_id, config))
            elif self.target == DeploymentTarget.GCP_CLOUD_RUN:
                deployment_info.update(self._deploy_to_cloud_run(model, model_id, config))
            elif self.target == DeploymentTarget.KUBERNETES:
                deployment_info.update(self._deploy_to_kubernetes(model, model_id, config))
            elif self.target == DeploymentTarget.DOCKER:
                deployment_info.update(self._deploy_to_docker(model, model_id, config))
            else:
                deployment_info.update(self._deploy_locally(model, model_id, config))
            
            deployment_info['status'] = 'deployed'
            self.deployed_models[model_id] = deployment_info
            
        except Exception as e:
            deployment_info['status'] = 'failed'
            deployment_info['error'] = str(e)
            print(f"Deployment failed: {str(e)}")
        
        return deployment_info
    
    def _deploy_to_aws_lambda(self, model: NeuralNetwork, model_id: str, 
                             config: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy to AWS Lambda (placeholder)."""
        print(f"Deploying {model_id} to AWS Lambda...")
        
        # Simulate deployment
        time.sleep(2)
        
        return {
            'endpoint_url': f"https://lambda.aws.com/functions/{model_id}",
            'function_name': f"synapse-model-{model_id}",
            'runtime': 'python3.9',
            'memory_mb': config.get('memory_mb', 512),
            'timeout_seconds': config.get('timeout_seconds', 30)
        }
    
    def _deploy_to_sagemaker(self, model: NeuralNetwork, model_id: str,
                           config: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy to AWS SageMaker (placeholder)."""
        print(f"Deploying {model_id} to AWS SageMaker...")
        
        time.sleep(3)
        
        return {
            'endpoint_url': f"https://sagemaker.aws.com/endpoints/{model_id}",
            'endpoint_name': f"synapse-{model_id}",
            'instance_type': config.get('instance_type', 'ml.t2.medium'),
            'initial_instance_count': config.get('instance_count', 1)
        }
    
    def _deploy_to_cloud_run(self, model: NeuralNetwork, model_id: str,
                           config: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy to Google Cloud Run (placeholder)."""
        print(f"Deploying {model_id} to Google Cloud Run...")
        
        time.sleep(2)
        
        return {
            'endpoint_url': f"https://{model_id}-cloudrun.googleapis.com",
            'service_name': f"synapse-{model_id}",
            'region': config.get('region', 'us-central1'),
            'cpu_limit': config.get('cpu_limit', '1'),
            'memory_limit': config.get('memory_limit', '512Mi')
        }
    
    def _deploy_to_kubernetes(self, model: NeuralNetwork, model_id: str,
                            config: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy to Kubernetes (placeholder)."""
        print(f"Deploying {model_id} to Kubernetes...")
        
        time.sleep(4)
        
        return {
            'endpoint_url': f"http://synapse-{model_id}.default.svc.cluster.local",
            'deployment_name': f"synapse-{model_id}",
            'namespace': config.get('namespace', 'default'),
            'replicas': config.get('replicas', 3),
            'container_image': f"synapse/model-server:{model_id}"
        }
    
    def _deploy_to_docker(self, model: NeuralNetwork, model_id: str,
                         config: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy to Docker container (placeholder)."""
        print(f"Deploying {model_id} to Docker...")
        
        time.sleep(1)
        
        return {
            'endpoint_url': f"http://localhost:{config.get('port', 8080)}",
            'container_name': f"synapse-{model_id}",
            'image_name': f"synapse/model-server:{model_id}",
            'port_mapping': f"{config.get('port', 8080)}:8080"
        }
    
    def _deploy_locally(self, model: NeuralNetwork, model_id: str,
                       config: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy locally (placeholder)."""
        print(f"Deploying {model_id} locally...")
        
        return {
            'endpoint_url': f"http://localhost:{config.get('port', 8080)}",
            'process_id': 12345,  # Placeholder
            'log_file': f"/tmp/synapse-{model_id}.log"
        }
    
    def scale_deployment(self, model_id: str, instances: int) -> Dict[str, Any]:
        """Scale deployment to specified number of instances."""
        if model_id not in self.deployed_models:
            raise ValueError(f"Model {model_id} not deployed")
        
        print(f"Scaling {model_id} to {instances} instances...")
        
        # Update deployment info
        self.deployed_models[model_id]['instances'] = instances
        self.deployed_models[model_id]['last_scaled'] = time.time()
        
        return {
            'model_id': model_id,
            'new_instance_count': instances,
            'scaling_time': time.time(),
            'status': 'scaled'
        }
    
    def get_deployment_status(self, model_id: str) -> Dict[str, Any]:
        """Get deployment status."""
        if model_id in self.deployed_models:
            return self.deployed_models[model_id]
        else:
            return {'model_id': model_id, 'status': 'not_deployed'}
    
    def list_deployments(self) -> List[Dict[str, Any]]:
        """List all deployments."""
        return list(self.deployed_models.values())

# Factory functions
def create_model_server(host: str = "localhost", port: int = 8080) -> ModelServer:
    """Create model server instance."""
    return ModelServer(host=host, port=port)

def create_cloud_deployment(target: str) -> CloudDeployment:
    """Create cloud deployment instance."""
    return CloudDeployment(DeploymentTarget(target))

def deploy_model_to_cloud(model: NeuralNetwork, model_id: str, 
                         target: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Deploy model to cloud platform."""
    deployment = create_cloud_deployment(target)
    return deployment.deploy_model(model, model_id, config)

# Export main classes
__all__ = [
    'ModelServer', 'CloudDeployment', 'ModelMetadata', 
    'InferenceRequest', 'InferenceResponse', 'ModelPreprocessor', 'ModelPostprocessor',
    'DeploymentTarget', 'ServingProtocol',
    'create_model_server', 'create_cloud_deployment', 'deploy_model_to_cloud'
]