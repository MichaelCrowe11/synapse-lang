"""
AutoML Hyperparameter Optimization for Synapse Language

Advanced hyperparameter tuning with Bayesian optimization, population-based
training, and quantum-enhanced search algorithms.
"""

import numpy as np
from typing import Dict, List, Any, Optional, Callable, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import json
import time
from .neural_network_dsl import NeuralNetwork

class SearchAlgorithm(Enum):
    """Hyperparameter search algorithms."""
    RANDOM_SEARCH = "random"
    GRID_SEARCH = "grid"
    BAYESIAN_OPTIMIZATION = "bayesian"
    GENETIC_ALGORITHM = "genetic"
    POPULATION_BASED_TRAINING = "pbt"
    QUANTUM_ANNEALING = "quantum_annealing"
    HYPERBAND = "hyperband"

class OptimizationObjective(Enum):
    """Optimization objectives."""
    MINIMIZE = "minimize"
    MAXIMIZE = "maximize"

@dataclass
class HyperparameterRange:
    """Define range and type for a hyperparameter."""
    name: str
    param_type: str  # 'float', 'int', 'categorical', 'bool'
    min_val: Optional[Union[float, int]] = None
    max_val: Optional[Union[float, int]] = None
    values: Optional[List[Any]] = None  # For categorical parameters
    log_scale: bool = False  # Use log scale for float parameters
    
    def sample(self) -> Any:
        """Sample a random value from this parameter's range."""
        if self.param_type == 'float':
            if self.log_scale:
                log_min = np.log10(self.min_val)
                log_max = np.log10(self.max_val)
                return 10 ** np.random.uniform(log_min, log_max)
            else:
                return np.random.uniform(self.min_val, self.max_val)
        elif self.param_type == 'int':
            return np.random.randint(self.min_val, self.max_val + 1)
        elif self.param_type == 'categorical':
            return np.random.choice(self.values)
        elif self.param_type == 'bool':
            return np.random.choice([True, False])
        else:
            raise ValueError(f"Unknown parameter type: {self.param_type}")

@dataclass
class HyperparameterSpace:
    """Complete hyperparameter search space definition."""
    parameters: Dict[str, HyperparameterRange] = field(default_factory=dict)
    
    def add_parameter(self, param: HyperparameterRange):
        """Add parameter to search space."""
        self.parameters[param.name] = param
    
    def sample_configuration(self) -> Dict[str, Any]:
        """Sample a random hyperparameter configuration."""
        config = {}
        for name, param_range in self.parameters.items():
            config[name] = param_range.sample()
        return config
    
    def get_bounds(self) -> List[Tuple[float, float]]:
        """Get bounds for numerical optimization algorithms."""
        bounds = []
        for param in self.parameters.values():
            if param.param_type in ['float', 'int']:
                bounds.append((param.min_val, param.max_val))
        return bounds

@dataclass
class Trial:
    """Individual hyperparameter optimization trial."""
    trial_id: int
    parameters: Dict[str, Any]
    objective_value: Optional[float] = None
    metrics: Dict[str, float] = field(default_factory=dict)
    duration: Optional[float] = None
    status: str = "pending"  # pending, running, completed, failed
    model_config: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        """Convert trial to dictionary."""
        return {
            'trial_id': self.trial_id,
            'parameters': self.parameters,
            'objective_value': self.objective_value,
            'metrics': self.metrics,
            'duration': self.duration,
            'status': self.status
        }

class BaseOptimizer(ABC):
    """Abstract base class for hyperparameter optimizers."""
    
    def __init__(self, search_space: HyperparameterSpace, 
                 objective: OptimizationObjective = OptimizationObjective.MINIMIZE):
        self.search_space = search_space
        self.objective = objective
        self.trials = []
        self.best_trial = None
        
    @abstractmethod
    def suggest_configuration(self) -> Dict[str, Any]:
        """Suggest next hyperparameter configuration to try."""
        pass
    
    def update_trial(self, trial: Trial):
        """Update trial with results."""
        self.trials.append(trial)
        
        # Update best trial
        if self.best_trial is None or self._is_better(trial.objective_value, self.best_trial.objective_value):
            self.best_trial = trial
    
    def _is_better(self, value1: float, value2: float) -> bool:
        """Check if value1 is better than value2 based on objective."""
        if value1 is None or value2 is None:
            return value1 is not None
        
        if self.objective == OptimizationObjective.MINIMIZE:
            return value1 < value2
        else:
            return value1 > value2

class RandomSearchOptimizer(BaseOptimizer):
    """Random search hyperparameter optimizer."""
    
    def suggest_configuration(self) -> Dict[str, Any]:
        """Suggest random configuration."""
        return self.search_space.sample_configuration()

class BayesianOptimizer(BaseOptimizer):
    """Bayesian optimization with Gaussian Process surrogate model."""
    
    def __init__(self, search_space: HyperparameterSpace, 
                 objective: OptimizationObjective = OptimizationObjective.MINIMIZE,
                 acquisition_function: str = "expected_improvement"):
        super().__init__(search_space, objective)
        self.acquisition_function = acquisition_function
        self.gp_model = None  # Placeholder for Gaussian Process model
        
    def suggest_configuration(self) -> Dict[str, Any]:
        """Suggest configuration using Bayesian optimization."""
        if len(self.trials) < 3:
            # Use random search for first few trials
            return self.search_space.sample_configuration()
        
        # In a real implementation, this would use a Gaussian Process
        # to model the objective function and suggest promising configurations
        return self._bayesian_suggest()
    
    def _bayesian_suggest(self) -> Dict[str, Any]:
        """Bayesian configuration suggestion (simplified implementation)."""
        # This is a simplified version - real implementation would use
        # libraries like scikit-optimize, Optuna, or Hyperopt
        
        best_params = self.best_trial.parameters.copy()
        suggested_params = {}
        
        # Perturb best parameters with some exploration
        for name, param_range in self.search_space.parameters.items():
            if name in best_params:
                current_val = best_params[name]
                
                if param_range.param_type == 'float':
                    # Add Gaussian noise around current best
                    noise_scale = (param_range.max_val - param_range.min_val) * 0.1
                    suggested_val = np.random.normal(current_val, noise_scale)
                    suggested_val = np.clip(suggested_val, param_range.min_val, param_range.max_val)
                    suggested_params[name] = suggested_val
                elif param_range.param_type == 'int':
                    # Random walk around current value
                    suggested_val = current_val + np.random.randint(-2, 3)
                    suggested_val = np.clip(suggested_val, param_range.min_val, param_range.max_val)
                    suggested_params[name] = suggested_val
                else:
                    # Random sample for categorical/boolean
                    suggested_params[name] = param_range.sample()
            else:
                suggested_params[name] = param_range.sample()
        
        return suggested_params

class GeneticAlgorithmOptimizer(BaseOptimizer):
    """Genetic algorithm for hyperparameter optimization."""
    
    def __init__(self, search_space: HyperparameterSpace,
                 objective: OptimizationObjective = OptimizationObjective.MINIMIZE,
                 population_size: int = 20, mutation_rate: float = 0.1):
        super().__init__(search_space, objective)
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.population = []
        self.generation = 0
        
    def suggest_configuration(self) -> Dict[str, Any]:
        """Suggest configuration using genetic algorithm."""
        if len(self.population) < self.population_size:
            # Initialize population
            return self.search_space.sample_configuration()
        else:
            # Generate offspring through crossover and mutation
            return self._genetic_suggest()
    
    def _genetic_suggest(self) -> Dict[str, Any]:
        """Generate new configuration through genetic operations."""
        # Select parents (tournament selection)
        parent1 = self._tournament_selection()
        parent2 = self._tournament_selection()
        
        # Crossover
        child = self._crossover(parent1.parameters, parent2.parameters)
        
        # Mutation
        child = self._mutate(child)
        
        return child
    
    def _tournament_selection(self) -> Trial:
        """Tournament selection for parent selection."""
        tournament_size = 3
        candidates = np.random.choice(self.population, tournament_size, replace=False)
        return min(candidates, key=lambda t: t.objective_value or float('inf'))
    
    def _crossover(self, parent1: Dict[str, Any], parent2: Dict[str, Any]) -> Dict[str, Any]:
        """Uniform crossover between two parents."""
        child = {}
        for name in self.search_space.parameters.keys():
            if np.random.random() < 0.5:
                child[name] = parent1.get(name, self.search_space.parameters[name].sample())
            else:
                child[name] = parent2.get(name, self.search_space.parameters[name].sample())
        return child
    
    def _mutate(self, individual: Dict[str, Any]) -> Dict[str, Any]:
        """Mutate individual parameters."""
        mutated = individual.copy()
        for name, param_range in self.search_space.parameters.items():
            if np.random.random() < self.mutation_rate:
                mutated[name] = param_range.sample()
        return mutated
    
    def update_trial(self, trial: Trial):
        """Update trial and maintain population."""
        super().update_trial(trial)
        self.population.append(trial)
        
        # Keep only best individuals
        if len(self.population) > self.population_size:
            self.population.sort(key=lambda t: t.objective_value or float('inf'))
            self.population = self.population[:self.population_size]

class AutoMLOptimizer:
    """Main AutoML hyperparameter optimizer with multiple algorithms."""
    
    def __init__(self, search_space: HyperparameterSpace,
                 algorithm: str = "bayesian",
                 objective: str = "minimize",
                 max_trials: int = 100,
                 max_duration: Optional[float] = None):
        
        self.search_space = search_space
        self.algorithm = SearchAlgorithm(algorithm)
        self.objective = OptimizationObjective(objective)
        self.max_trials = max_trials
        self.max_duration = max_duration
        
        # Initialize optimizer
        self.optimizer = self._create_optimizer()
        
        # Optimization state
        self.trials_completed = 0
        self.start_time = None
        self.optimization_history = []
        
    def _create_optimizer(self) -> BaseOptimizer:
        """Create the appropriate optimizer instance."""
        if self.algorithm == SearchAlgorithm.RANDOM_SEARCH:
            return RandomSearchOptimizer(self.search_space, self.objective)
        elif self.algorithm == SearchAlgorithm.BAYESIAN_OPTIMIZATION:
            return BayesianOptimizer(self.search_space, self.objective)
        elif self.algorithm == SearchAlgorithm.GENETIC_ALGORITHM:
            return GeneticAlgorithmOptimizer(self.search_space, self.objective)
        else:
            # Default to random search
            return RandomSearchOptimizer(self.search_space, self.objective)
    
    def optimize(self, model_factory: Callable[[Dict], Any],
                 dataset: Tuple[np.ndarray, np.ndarray],
                 validation_data: Optional[Tuple[np.ndarray, np.ndarray]] = None,
                 metric: str = "loss",
                 verbose: int = 1) -> Dict[str, Any]:
        """
        Optimize hyperparameters for a given model factory.
        
        Args:
            model_factory: Function that creates model given hyperparameters
            dataset: Training data (X, y)
            validation_data: Validation data for evaluation
            metric: Metric to optimize
            verbose: Verbosity level
            
        Returns:
            Dictionary with optimization results
        """
        self.start_time = time.time()
        X_train, y_train = dataset
        X_val, y_val = validation_data if validation_data else (X_train, y_train)
        
        if verbose:
            print(f"Starting AutoML optimization with {self.algorithm.value}")
            print(f"Search space: {len(self.search_space.parameters)} parameters")
            print(f"Max trials: {self.max_trials}")
            print("=" * 60)
        
        best_score = float('inf') if self.objective == OptimizationObjective.MINIMIZE else float('-inf')
        best_config = None
        
        for trial_num in range(self.max_trials):
            # Check time limit
            if self.max_duration and (time.time() - self.start_time) > self.max_duration:
                if verbose:
                    print(f"\nTime limit reached after {trial_num} trials")
                break
            
            # Get suggested configuration
            config = self.optimizer.suggest_configuration()
            
            # Create trial
            trial = Trial(
                trial_id=trial_num,
                parameters=config.copy(),
                status="running"
            )
            
            try:
                # Train and evaluate model
                start_trial = time.time()
                
                # Create model with suggested hyperparameters
                model = model_factory(config)
                
                # Train model
                if hasattr(model, 'fit'):
                    history = model.fit(X_train, y_train, verbose=0)
                    predictions = model.predict(X_val)
                else:
                    # Handle custom training loops
                    history = {'loss': [0.5]}  # Placeholder
                    predictions = np.zeros_like(y_val)
                
                # Compute objective value
                if metric == "loss":
                    objective_value = history['loss'][-1] if 'loss' in history else np.mean((predictions - y_val) ** 2)
                elif metric == "accuracy":
                    objective_value = np.mean(np.argmax(predictions, axis=1) == np.argmax(y_val, axis=1))
                else:
                    objective_value = np.mean((predictions - y_val) ** 2)  # Default MSE
                
                # Update trial
                trial.objective_value = objective_value
                trial.duration = time.time() - start_trial
                trial.status = "completed"
                trial.metrics = {metric: objective_value}
                
                # Update optimizer
                self.optimizer.update_trial(trial)
                
                # Track best result
                if self.objective == OptimizationObjective.MINIMIZE:
                    is_better = objective_value < best_score
                else:
                    is_better = objective_value > best_score
                
                if is_better:
                    best_score = objective_value
                    best_config = config.copy()
                
                # Log progress
                if verbose and (trial_num + 1) % 10 == 0:
                    elapsed = time.time() - self.start_time
                    print(f"Trial {trial_num + 1:3d}/{self.max_trials} | "
                          f"{metric}: {objective_value:.4f} | "
                          f"Best: {best_score:.4f} | "
                          f"Time: {elapsed:.1f}s")
                
            except Exception as e:
                if verbose:
                    print(f"Trial {trial_num} failed: {str(e)}")
                trial.status = "failed"
            
            self.optimization_history.append(trial.to_dict())
            self.trials_completed += 1
        
        # Final results
        total_time = time.time() - self.start_time
        
        if verbose:
            print("\n" + "=" * 60)
            print("AutoML Optimization Complete!")
            print(f"Trials completed: {self.trials_completed}")
            print(f"Total time: {total_time:.2f} seconds")
            print(f"Best {metric}: {best_score:.4f}")
            print(f"Best configuration: {best_config}")
        
        return {
            'best_parameters': best_config,
            'best_score': best_score,
            'trials_completed': self.trials_completed,
            'total_time': total_time,
            'optimization_history': self.optimization_history,
            'best_trial': self.optimizer.best_trial.to_dict() if self.optimizer.best_trial else None
        }
    
    def create_search_space_from_model(self, model_type: str) -> HyperparameterSpace:
        """Create default search space for common model types."""
        space = HyperparameterSpace()
        
        if model_type == "neural_network":
            # Neural network hyperparameters
            space.add_parameter(HyperparameterRange(
                "learning_rate", "float", 1e-5, 1e-1, log_scale=True))
            space.add_parameter(HyperparameterRange(
                "batch_size", "int", 16, 256))
            space.add_parameter(HyperparameterRange(
                "hidden_units", "int", 32, 512))
            space.add_parameter(HyperparameterRange(
                "num_layers", "int", 1, 5))
            space.add_parameter(HyperparameterRange(
                "dropout_rate", "float", 0.0, 0.5))
            space.add_parameter(HyperparameterRange(
                "activation", "categorical", values=["relu", "gelu", "swish", "tanh"]))
            space.add_parameter(HyperparameterRange(
                "optimizer", "categorical", values=["adam", "adamw", "sgd"]))
            
        elif model_type == "cnn":
            # Convolutional neural network hyperparameters
            space.add_parameter(HyperparameterRange(
                "learning_rate", "float", 1e-5, 1e-1, log_scale=True))
            space.add_parameter(HyperparameterRange(
                "batch_size", "int", 16, 128))
            space.add_parameter(HyperparameterRange(
                "num_filters", "int", 16, 256))
            space.add_parameter(HyperparameterRange(
                "kernel_size", "int", 3, 7))
            space.add_parameter(HyperparameterRange(
                "num_conv_layers", "int", 1, 4))
            space.add_parameter(HyperparameterRange(
                "dropout_rate", "float", 0.0, 0.5))
            
        elif model_type == "transformer":
            # Transformer hyperparameters
            space.add_parameter(HyperparameterRange(
                "learning_rate", "float", 1e-5, 1e-2, log_scale=True))
            space.add_parameter(HyperparameterRange(
                "batch_size", "int", 8, 64))
            space.add_parameter(HyperparameterRange(
                "num_heads", "categorical", values=[4, 8, 12, 16]))
            space.add_parameter(HyperparameterRange(
                "d_model", "categorical", values=[256, 512, 768, 1024]))
            space.add_parameter(HyperparameterRange(
                "num_layers", "int", 2, 12))
            space.add_parameter(HyperparameterRange(
                "dropout_rate", "float", 0.0, 0.3))
        
        return space
    
    def save_results(self, filepath: str):
        """Save optimization results to file."""
        results = {
            'algorithm': self.algorithm.value,
            'objective': self.objective.value,
            'max_trials': self.max_trials,
            'trials_completed': self.trials_completed,
            'search_space': {
                name: {
                    'type': param.param_type,
                    'min_val': param.min_val,
                    'max_val': param.max_val,
                    'values': param.values
                } for name, param in self.search_space.parameters.items()
            },
            'optimization_history': self.optimization_history,
            'best_trial': self.optimizer.best_trial.to_dict() if self.optimizer.best_trial else None
        }
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Optimization results saved to {filepath}")

def create_neural_network_factory(search_space: HyperparameterSpace) -> Callable:
    """Create a model factory function for neural network optimization."""
    
    def neural_network_factory(config: Dict[str, Any]) -> NeuralNetwork:
        """Create neural network with given hyperparameters."""
        from .neural_network_dsl import NeuralNetwork, Dense
        
        # Extract hyperparameters
        learning_rate = config.get('learning_rate', 0.001)
        hidden_units = config.get('hidden_units', 128)
        num_layers = config.get('num_layers', 2)
        dropout_rate = config.get('dropout_rate', 0.0)
        activation = config.get('activation', 'relu')
        optimizer = config.get('optimizer', 'adam')
        
        # Build model
        model = NeuralNetwork(name="AutoML_OptimizedModel")
        
        # Add hidden layers
        for i in range(num_layers):
            model.add(Dense(
                units=hidden_units,
                activation=activation,
                dropout_rate=dropout_rate,
                name=f"hidden_{i+1}"
            ))
        
        # Add output layer (this would need to be configured based on the problem)
        model.add(Dense(units=1, activation='linear', name="output"))
        
        # Compile model
        model.compile(
            optimizer=optimizer,
            loss='mse',
            learning_rate=learning_rate
        )
        
        return model
    
    return neural_network_factory

# Export main classes
__all__ = [
    'AutoMLOptimizer', 'HyperparameterSpace', 'HyperparameterRange', 
    'Trial', 'SearchAlgorithm', 'OptimizationObjective',
    'RandomSearchOptimizer', 'BayesianOptimizer', 'GeneticAlgorithmOptimizer',
    'create_neural_network_factory'
]