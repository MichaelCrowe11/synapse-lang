"""
Machine Learning Integration for Synapse Language
Provides uncertainty-aware ML capabilities for scientific computing
"""

import numpy as np
import pandas as pd
from typing import Union, List, Dict, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
import warnings

# Core ML imports
try:
    import sklearn
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.linear_model import LinearRegression, BayesianRidge, ARDRegression
    from sklearn.gaussian_process import GaussianProcessRegressor
    from sklearn.gaussian_process.kernels import RBF, Matern, WhiteKernel
    from sklearn.model_selection import cross_val_score, train_test_split
    from sklearn.preprocessing import StandardScaler, MinMaxScaler
    from sklearn.metrics import mean_squared_error, r2_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# Neural networks
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, TensorDataset
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

# Bayesian ML
try:
    import pymc as pm
    import arviz as az
    BAYESIAN_AVAILABLE = True
except ImportError:
    BAYESIAN_AVAILABLE = False

from .uncertainty import UncertainValue, UncertaintyPropagator


@dataclass
class MLResult:
    """Container for ML model results with uncertainty quantification"""
    predictions: np.ndarray
    uncertainties: Optional[np.ndarray] = None
    model: Any = None
    metrics: Dict[str, float] = field(default_factory=dict)
    feature_importance: Optional[np.ndarray] = None
    cross_val_scores: Optional[np.ndarray] = None


class UncertaintyAwareML:
    """
    Machine learning models that account for input uncertainty and provide
    prediction uncertainty estimates
    """
    
    def __init__(self, model_type: str = "gaussian_process"):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.is_fitted = False
        
    def _prepare_uncertain_data(self, X: Union[np.ndarray, List[UncertainValue]], 
                               y: Union[np.ndarray, List[UncertainValue]] = None,
                               n_samples: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        """Convert uncertain data to Monte Carlo samples for training"""
        if isinstance(X[0], UncertainValue):
            # Convert uncertain inputs to samples
            X_samples = []
            for _ in range(n_samples):
                sample = []
                for uncertain_val in X:
                    if isinstance(uncertain_val, UncertainValue):
                        sample.append(np.random.choice(uncertain_val.samples))
                    else:
                        sample.append(uncertain_val)
                X_samples.append(sample)
            X_array = np.array(X_samples)
        else:
            X_array = np.array(X)
            
        if y is not None:
            if isinstance(y[0], UncertainValue):
                y_samples = []
                for _ in range(n_samples):
                    sample = []
                    for uncertain_val in y:
                        if isinstance(uncertain_val, UncertainValue):
                            sample.append(np.random.choice(uncertain_val.samples))
                        else:
                            sample.append(uncertain_val)
                    y_samples.append(sample)
                y_array = np.array(y_samples)
            else:
                y_array = np.array(y)
            return X_array, y_array
        
        return X_array, None
    
    def fit(self, X: Union[np.ndarray, List[UncertainValue]], 
            y: Union[np.ndarray, List[UncertainValue]], **kwargs) -> 'UncertaintyAwareML':
        """Fit the model with uncertainty-aware training"""
        
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn is required for ML functionality")
        
        # Prepare data
        X_train, y_train = self._prepare_uncertain_data(X, y)
        
        # Flatten if needed
        if y_train.ndim > 1 and y_train.shape[1] == 1:
            y_train = y_train.flatten()
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X_train)
        
        # Initialize model based on type
        if self.model_type == "gaussian_process":
            kernel = RBF(1.0) + WhiteKernel(1e-6)
            self.model = GaussianProcessRegressor(kernel=kernel, alpha=1e-6, 
                                                normalize_y=True, **kwargs)
        elif self.model_type == "bayesian_ridge":
            self.model = BayesianRidge(**kwargs)
        elif self.model_type == "random_forest":
            self.model = RandomForestRegressor(n_estimators=100, **kwargs)
        elif self.model_type == "gradient_boosting":
            self.model = GradientBoostingRegressor(**kwargs)
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")
        
        # Fit model
        self.model.fit(X_scaled, y_train)
        self.is_fitted = True
        
        return self
    
    def predict_with_uncertainty(self, X: Union[np.ndarray, List[UncertainValue]], 
                                return_std: bool = True) -> MLResult:
        """Make predictions with uncertainty estimates"""
        
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before making predictions")
        
        # Prepare input data
        X_test, _ = self._prepare_uncertain_data(X)
        X_scaled = self.scaler.transform(X_test)
        
        # Make predictions with uncertainty
        if self.model_type == "gaussian_process":
            predictions, std = self.model.predict(X_scaled, return_std=True)
            uncertainties = std if return_std else None
            
        elif self.model_type == "bayesian_ridge":
            predictions, std = self.model.predict(X_scaled, return_std=True)
            uncertainties = std if return_std else None
            
        elif self.model_type in ["random_forest", "gradient_boosting"]:
            predictions = self.model.predict(X_scaled)
            
            if return_std and hasattr(self.model, 'estimators_'):
                # Bootstrap uncertainty estimation for ensemble methods
                estimator_predictions = []
                for estimator in self.model.estimators_:
                    if hasattr(estimator, 'predict'):
                        pred = estimator.predict(X_scaled)
                        estimator_predictions.append(pred)
                
                estimator_predictions = np.array(estimator_predictions)
                uncertainties = np.std(estimator_predictions, axis=0)
            else:
                uncertainties = None
        else:
            predictions = self.model.predict(X_scaled)
            uncertainties = None
        
        # Calculate feature importance if available
        feature_importance = None
        if hasattr(self.model, 'feature_importances_'):
            feature_importance = self.model.feature_importances_
        
        return MLResult(
            predictions=predictions,
            uncertainties=uncertainties,
            model=self.model,
            feature_importance=feature_importance
        )
    
    def cross_validate(self, X: Union[np.ndarray, List[UncertainValue]], 
                      y: Union[np.ndarray, List[UncertainValue]], 
                      cv_folds: int = 5) -> Dict[str, float]:
        """Perform cross-validation with uncertainty propagation"""
        
        X_data, y_data = self._prepare_uncertain_data(X, y)
        X_scaled = self.scaler.fit_transform(X_data)
        
        if y_data.ndim > 1 and y_data.shape[1] == 1:
            y_data = y_data.flatten()
        
        # Cross-validation scores
        cv_scores = cross_val_score(self.model, X_scaled, y_data, cv=cv_folds, 
                                   scoring='r2')
        
        return {
            'mean_cv_score': np.mean(cv_scores),
            'std_cv_score': np.std(cv_scores),
            'cv_scores': cv_scores
        }


class BayesianNeuralNetwork:
    """Bayesian Neural Network with uncertainty quantification using PyTorch"""
    
    def __init__(self, input_dim: int, hidden_dims: List[int] = [50, 25], 
                 output_dim: int = 1):
        
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch is required for Bayesian Neural Networks")
        
        self.input_dim = input_dim
        self.hidden_dims = hidden_dims
        self.output_dim = output_dim
        
        # Build network
        layers = []
        prev_dim = input_dim
        
        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(prev_dim, hidden_dim))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(0.1))  # Dropout for uncertainty
            prev_dim = hidden_dim
        
        layers.append(nn.Linear(prev_dim, output_dim * 2))  # Mean and variance
        
        self.network = nn.Sequential(*layers)
        self.optimizer = None
        self.is_fitted = False
    
    def _gaussian_nll_loss(self, predictions: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        """Gaussian negative log-likelihood loss for uncertainty estimation"""
        mean, log_var = torch.chunk(predictions, 2, dim=1)
        var = torch.exp(log_var)
        
        # Negative log likelihood
        nll = 0.5 * torch.log(2 * np.pi * var) + 0.5 * ((targets - mean) ** 2) / var
        return torch.mean(nll)
    
    def fit(self, X: np.ndarray, y: np.ndarray, epochs: int = 1000, 
            learning_rate: float = 0.01, batch_size: int = 32):
        """Train the Bayesian neural network"""
        
        # Convert to tensors
        X_tensor = torch.FloatTensor(X)
        y_tensor = torch.FloatTensor(y.reshape(-1, 1))
        
        # Create data loader
        dataset = TensorDataset(X_tensor, y_tensor)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        # Initialize optimizer
        self.optimizer = optim.Adam(self.network.parameters(), lr=learning_rate)
        
        # Training loop
        self.network.train()
        for epoch in range(epochs):
            epoch_loss = 0
            for batch_x, batch_y in dataloader:
                self.optimizer.zero_grad()
                
                # Forward pass
                predictions = self.network(batch_x)
                loss = self._gaussian_nll_loss(predictions, batch_y)
                
                # Backward pass
                loss.backward()
                self.optimizer.step()
                
                epoch_loss += loss.item()
            
            if epoch % 100 == 0:
                print(f"Epoch {epoch}, Loss: {epoch_loss/len(dataloader):.6f}")
        
        self.is_fitted = True
    
    def predict_with_uncertainty(self, X: np.ndarray, n_samples: int = 100) -> MLResult:
        """Make predictions with epistemic uncertainty using dropout"""
        
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before making predictions")
        
        X_tensor = torch.FloatTensor(X)
        
        # Enable dropout for uncertainty estimation
        self.network.train()
        
        predictions = []
        for _ in range(n_samples):
            with torch.no_grad():
                pred = self.network(X_tensor)
                mean_pred, log_var_pred = torch.chunk(pred, 2, dim=1)
                predictions.append(mean_pred.numpy())
        
        predictions = np.array(predictions)
        
        # Calculate epistemic uncertainty (uncertainty in model parameters)
        mean_predictions = np.mean(predictions, axis=0).flatten()
        epistemic_uncertainty = np.std(predictions, axis=0).flatten()
        
        # Calculate aleatoric uncertainty (inherent data uncertainty)
        self.network.eval()
        with torch.no_grad():
            final_pred = self.network(X_tensor)
            _, log_var = torch.chunk(final_pred, 2, dim=1)
            aleatoric_uncertainty = np.sqrt(torch.exp(log_var).numpy()).flatten()
        
        # Total uncertainty
        total_uncertainty = np.sqrt(epistemic_uncertainty**2 + aleatoric_uncertainty**2)
        
        return MLResult(
            predictions=mean_predictions,
            uncertainties=total_uncertainty,
            model=self.network
        )


class ScientificMLPipeline:
    """Complete ML pipeline for scientific applications with uncertainty"""
    
    def __init__(self):
        self.models: Dict[str, UncertaintyAwareML] = {}
        self.data_preprocessor = None
        self.results: Dict[str, MLResult] = {}
    
    def add_model(self, name: str, model_type: str, **kwargs):
        """Add a model to the pipeline"""
        self.models[name] = UncertaintyAwareML(model_type, **kwargs)
    
    def fit_all_models(self, X: Union[np.ndarray, List[UncertainValue]], 
                      y: Union[np.ndarray, List[UncertainValue]]):
        """Fit all models in the pipeline"""
        for name, model in self.models.items():
            print(f"Fitting {name}...")
            try:
                model.fit(X, y)
                print(f"✅ {name} fitted successfully")
            except Exception as e:
                print(f"❌ Failed to fit {name}: {e}")
    
    def compare_models(self, X_test: Union[np.ndarray, List[UncertainValue]], 
                      y_test: Union[np.ndarray, List[UncertainValue]]) -> pd.DataFrame:
        """Compare all models and return performance metrics"""
        
        results = []
        
        for name, model in self.models.items():
            if not model.is_fitted:
                continue
            
            try:
                # Make predictions
                ml_result = model.predict_with_uncertainty(X_test)
                
                # Calculate metrics if ground truth is available
                if y_test is not None:
                    y_true = np.array([v.value if isinstance(v, UncertainValue) else v 
                                     for v in y_test])
                    
                    mse = mean_squared_error(y_true, ml_result.predictions)
                    r2 = r2_score(y_true, ml_result.predictions)
                    
                    # Uncertainty calibration (if uncertainties available)
                    calibration_score = None
                    if ml_result.uncertainties is not None:
                        # Simple calibration check: fraction of predictions within 1-sigma
                        residuals = np.abs(y_true - ml_result.predictions)
                        within_one_sigma = np.mean(residuals <= ml_result.uncertainties)
                        calibration_score = within_one_sigma
                    
                    results.append({
                        'model': name,
                        'mse': mse,
                        'rmse': np.sqrt(mse),
                        'r2_score': r2,
                        'mean_uncertainty': np.mean(ml_result.uncertainties) if ml_result.uncertainties is not None else np.nan,
                        'calibration_score': calibration_score
                    })
            
            except Exception as e:
                print(f"Error evaluating {name}: {e}")
        
        return pd.DataFrame(results)
    
    def ensemble_predict(self, X: Union[np.ndarray, List[UncertainValue]], 
                        weights: Optional[Dict[str, float]] = None) -> MLResult:
        """Create ensemble predictions from multiple models"""
        
        if weights is None:
            weights = {name: 1.0 for name in self.models.keys()}
        
        predictions_list = []
        uncertainties_list = []
        
        total_weight = sum(weights.values())
        
        for name, model in self.models.items():
            if not model.is_fitted:
                continue
            
            weight = weights.get(name, 0) / total_weight
            result = model.predict_with_uncertainty(X)
            
            predictions_list.append(weight * result.predictions)
            
            if result.uncertainties is not None:
                # Uncertainty combination for ensemble
                uncertainties_list.append((weight**2) * (result.uncertainties**2))
        
        # Combine predictions and uncertainties
        ensemble_predictions = np.sum(predictions_list, axis=0)
        
        if uncertainties_list:
            ensemble_uncertainties = np.sqrt(np.sum(uncertainties_list, axis=0))
        else:
            ensemble_uncertainties = None
        
        return MLResult(
            predictions=ensemble_predictions,
            uncertainties=ensemble_uncertainties
        )


# Integration with Synapse language constructs
class MLIntegration:
    """Integration layer for ML capabilities in Synapse language"""
    
    @staticmethod
    def create_ml_model(model_type: str, **config) -> UncertaintyAwareML:
        """Create ML model from Synapse syntax"""
        return UncertaintyAwareML(model_type, **config)
    
    @staticmethod
    def train_with_uncertain_data(model: UncertaintyAwareML, 
                                 X_uncertain: List[UncertainValue],
                                 y_uncertain: List[UncertainValue]) -> UncertaintyAwareML:
        """Train model with uncertain training data"""
        return model.fit(X_uncertain, y_uncertain)
    
    @staticmethod
    def predict_with_propagation(model: UncertaintyAwareML,
                               X_uncertain: List[UncertainValue]) -> List[UncertainValue]:
        """Make predictions that preserve input uncertainty"""
        result = model.predict_with_uncertainty(X_uncertain)
        
        # Convert to UncertainValue objects
        uncertain_predictions = []
        for i, pred in enumerate(result.predictions):
            uncertainty = result.uncertainties[i] if result.uncertainties is not None else 0.0
            uncertain_predictions.append(UncertainValue(pred, uncertainty))
        
        return uncertain_predictions
    
    @staticmethod
    def scientific_cross_validation(X: List[UncertainValue], y: List[UncertainValue],
                                  model_types: List[str]) -> Dict[str, Dict[str, float]]:
        """Perform scientific cross-validation with multiple model types"""
        results = {}
        
        for model_type in model_types:
            model = UncertaintyAwareML(model_type)
            cv_results = model.cross_validate(X, y)
            results[model_type] = cv_results
        
        return results


class GaussianProcessUncertainty:
    """Gaussian Process for uncertainty quantification in ML models."""
    
    def __init__(self, kernel: str = "rbf", length_scale: float = 1.0):
        self.kernel = kernel
        self.length_scale = length_scale
        self.X_train = None
        self.y_train = None
        self.fitted = False
        self.gp = None
        
        if SKLEARN_AVAILABLE:
            # Use sklearn GP if available
            if kernel == "rbf":
                kernel_obj = RBF(length_scale=length_scale) + WhiteKernel()
            elif kernel == "matern":
                kernel_obj = Matern(length_scale=length_scale) + WhiteKernel()
            else:
                kernel_obj = RBF(length_scale=length_scale) + WhiteKernel()
            
            self.gp = GaussianProcessRegressor(kernel=kernel_obj, alpha=1e-6)
    
    def fit(self, X: np.ndarray, y: np.ndarray):
        """Fit the Gaussian Process model."""
        self.X_train = np.array(X)
        
        # Handle UncertainValue objects in y
        if hasattr(y[0], 'value') and hasattr(y[0], 'uncertainty'):
            # Extract values and uncertainties from UncertainValue objects
            from .uncertainty import UncertainValue
            values = np.array([yi.value if isinstance(yi, UncertainValue) else yi for yi in y])
            uncertainties = np.array([yi.uncertainty if isinstance(yi, UncertainValue) else 0.0 for yi in y])
            self.y_train = values
            self.y_uncertainties = uncertainties
            
            # Incorporate uncertainties into GP alpha parameter (noise level)
            if self.gp is not None:
                avg_uncertainty = np.mean(uncertainties[uncertainties > 0])
                if avg_uncertainty > 0:
                    self.gp.alpha = avg_uncertainty ** 2
        else:
            self.y_train = np.array(y)
            self.y_uncertainties = None
        
        if self.gp is not None:
            self.gp.fit(self.X_train, self.y_train)
        
        self.fitted = True
        return self
    
    def predict(self, X: np.ndarray, return_std: bool = None, return_uncertain: bool = None):
        """Predict with uncertainty estimates."""
        if not self.fitted:
            raise ValueError("Model must be fitted before prediction")
        
        X = np.array(X)
        
        # Default behavior: if trained with UncertainValue objects, return UncertainValue objects
        if return_uncertain is None:
            return_uncertain = hasattr(self, 'y_uncertainties') and self.y_uncertainties is not None
        
        if return_std is None:
            return_std = not return_uncertain
        
        if self.gp is not None:
            # Use sklearn GP
            mean, std = self.gp.predict(X, return_std=True)
            
            if return_uncertain:
                # Return UncertainValue objects
                from .uncertainty import UncertainValue
                predictions = [UncertainValue(m, s) for m, s in zip(mean, std)]
                return predictions
            elif return_std:
                return mean, std
            return mean, None
        else:
            # Simple fallback implementation
            mean = np.mean(self.y_train) * np.ones(len(X))
            std = np.std(self.y_train) * np.ones(len(X))
            
            if return_uncertain:
                from .uncertainty import UncertainValue
                predictions = [UncertainValue(m, s) for m, s in zip(mean, std)]
                return predictions
            elif return_std:
                return mean, std
            return mean, None
    
    def sample(self, X: np.ndarray, n_samples: int = 10) -> np.ndarray:
        """Sample from the posterior distribution."""
        mean, std = self.predict(X, return_std=True, return_uncertain=False)
        
        if self.gp is not None and hasattr(self.gp, 'sample_y'):
            # Use sklearn's sampling if available
            return self.gp.sample_y(X, n_samples=n_samples).T
        else:
            # Fallback to normal sampling
            samples = np.random.normal(mean[:, None], std[:, None], (len(X), n_samples))
            return samples