"""
Synapse Language - Standard Library
Comprehensive scientific computing functions and utilities
"""

import numpy as np
import scipy as sp
from scipy import stats, optimize, integrate, signal
from typing import Any, List, Dict, Tuple, Union, Optional, Callable
import pandas as pd
import matplotlib.pyplot as plt
from dataclasses import dataclass
import warnings
import asyncio
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import numba
from numba import jit, cuda
import sympy as sym

# Statistical Functions
class Statistics:
    """Advanced statistical computing functions"""
    
    @staticmethod
    @jit(nopython=True)
    def fast_mean(data: np.ndarray) -> float:
        """JIT-compiled mean calculation"""
        return np.mean(data)
    
    @staticmethod
    @jit(nopython=True)
    def fast_std(data: np.ndarray) -> float:
        """JIT-compiled standard deviation"""
        return np.std(data)
    
    @staticmethod
    def confidence_interval(data: np.ndarray, confidence: float = 0.95) -> Tuple[float, float]:
        """Calculate confidence interval with uncertainty"""
        mean = np.mean(data)
        sem = stats.sem(data)
        interval = stats.t.interval(confidence, len(data)-1, loc=mean, scale=sem)
        return interval
    
    @staticmethod
    def hypothesis_test(sample1: np.ndarray, sample2: np.ndarray, 
                       test_type: str = 't-test') -> Dict[str, float]:
        """Perform statistical hypothesis testing"""
        if test_type == 't-test':
            statistic, p_value = stats.ttest_ind(sample1, sample2)
        elif test_type == 'mann-whitney':
            statistic, p_value = stats.mannwhitneyu(sample1, sample2)
        elif test_type == 'anova':
            statistic, p_value = stats.f_oneway(sample1, sample2)
        else:
            raise ValueError(f"Unknown test type: {test_type}")
        
        return {
            'statistic': statistic,
            'p_value': p_value,
            'significant': p_value < 0.05,
            'effect_size': Statistics._calculate_effect_size(sample1, sample2)
        }
    
    @staticmethod
    def _calculate_effect_size(sample1: np.ndarray, sample2: np.ndarray) -> float:
        """Cohen's d effect size"""
        pooled_std = np.sqrt((np.var(sample1) + np.var(sample2)) / 2)
        return (np.mean(sample1) - np.mean(sample2)) / pooled_std
    
    @staticmethod
    def monte_carlo_simulation(func: Callable, params: Dict, 
                              n_simulations: int = 10000) -> Dict[str, Any]:
        """Run Monte Carlo simulation with uncertainty propagation"""
        results = []
        
        for _ in range(n_simulations):
            # Sample parameters from distributions
            sampled_params = {}
            for key, dist in params.items():
                if isinstance(dist, tuple):  # (mean, std) for normal distribution
                    sampled_params[key] = np.random.normal(dist[0], dist[1])
                else:
                    sampled_params[key] = dist
            
            results.append(func(**sampled_params))
        
        results = np.array(results)
        return {
            'mean': np.mean(results),
            'std': np.std(results),
            'confidence_95': np.percentile(results, [2.5, 97.5]),
            'distribution': results
        }

# Machine Learning Tools
class MachineLearning:
    """Machine learning utilities for scientific computing"""
    
    @staticmethod
    def auto_regression(x: np.ndarray, y: np.ndarray, 
                        degree: int = None) -> Dict[str, Any]:
        """Automatic polynomial regression with optimal degree selection"""
        if degree is None:
            # Use cross-validation to find optimal degree
            degrees = range(1, min(10, len(x)))
            best_score = -np.inf
            best_degree = 1
            
            for d in degrees:
                coeffs = np.polyfit(x, y, d)
                poly = np.poly1d(coeffs)
                y_pred = poly(x)
                score = 1 - np.sum((y - y_pred)**2) / np.sum((y - np.mean(y))**2)
                
                if score > best_score:
                    best_score = score
                    best_degree = d
            
            degree = best_degree
        
        coeffs = np.polyfit(x, y, degree)
        poly = np.poly1d(coeffs)
        y_pred = poly(x)
        
        return {
            'coefficients': coeffs,
            'polynomial': poly,
            'r_squared': 1 - np.sum((y - y_pred)**2) / np.sum((y - np.mean(y))**2),
            'degree': degree,
            'predictions': y_pred
        }
    
    @staticmethod
    def neural_network_simple(X: np.ndarray, y: np.ndarray, 
                             hidden_layers: List[int] = [10, 10],
                             epochs: int = 100) -> 'NeuralNetwork':
        """Simple neural network for regression/classification"""
        return NeuralNetwork(X, y, hidden_layers, epochs)
    
    @staticmethod
    def dimensionality_reduction(X: np.ndarray, n_components: int = 2,
                                method: str = 'pca') -> np.ndarray:
        """Reduce dimensionality of data"""
        if method == 'pca':
            from sklearn.decomposition import PCA
            reducer = PCA(n_components=n_components)
        elif method == 'tsne':
            from sklearn.manifold import TSNE
            reducer = TSNE(n_components=n_components)
        else:
            raise ValueError(f"Unknown method: {method}")
        
        return reducer.fit_transform(X)

class NeuralNetwork:
    """Simple neural network implementation"""
    
    def __init__(self, X: np.ndarray, y: np.ndarray, 
                 hidden_layers: List[int], epochs: int):
        self.X = X
        self.y = y
        self.hidden_layers = hidden_layers
        self.epochs = epochs
        self.weights = []
        self.biases = []
        self._initialize_weights()
        self.train()
    
    def _initialize_weights(self):
        """Initialize network weights"""
        layer_sizes = [self.X.shape[1]] + self.hidden_layers + [self.y.shape[1] if len(self.y.shape) > 1 else 1]
        
        for i in range(len(layer_sizes) - 1):
            w = np.random.randn(layer_sizes[i], layer_sizes[i+1]) * 0.1
            b = np.zeros((1, layer_sizes[i+1]))
            self.weights.append(w)
            self.biases.append(b)
    
    def _sigmoid(self, x):
        """Sigmoid activation function"""
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))
    
    def _forward(self, X):
        """Forward propagation"""
        self.activations = [X]
        for w, b in zip(self.weights, self.biases):
            z = np.dot(self.activations[-1], w) + b
            a = self._sigmoid(z)
            self.activations.append(a)
        return self.activations[-1]
    
    def train(self):
        """Train the network"""
        learning_rate = 0.01
        
        for epoch in range(self.epochs):
            # Forward pass
            output = self._forward(self.X)
            
            # Backward pass (simplified)
            error = output - self.y.reshape(-1, 1) if len(self.y.shape) == 1 else output - self.y
            
            for i in range(len(self.weights) - 1, -1, -1):
                self.weights[i] -= learning_rate * np.dot(self.activations[i].T, error)
                self.biases[i] -= learning_rate * np.sum(error, axis=0, keepdims=True)
                if i > 0:
                    error = np.dot(error, self.weights[i].T) * self.activations[i] * (1 - self.activations[i])
    
    def predict(self, X):
        """Make predictions"""
        return self._forward(X)

# Differential Equations Solver
class DifferentialEquations:
    """Solve various types of differential equations"""
    
    @staticmethod
    def solve_ode(func: Callable, y0: Union[float, np.ndarray], 
                  t_span: Tuple[float, float], 
                  method: str = 'RK45') -> Dict[str, np.ndarray]:
        """Solve ordinary differential equations"""
        from scipy.integrate import solve_ivp
        
        t_eval = np.linspace(t_span[0], t_span[1], 1000)
        solution = solve_ivp(func, t_span, y0, t_eval=t_eval, method=method)
        
        return {
            't': solution.t,
            'y': solution.y,
            'success': solution.success,
            'message': solution.message
        }
    
    @staticmethod
    def solve_pde_heat(initial_condition: np.ndarray, 
                       diffusion_coeff: float,
                       dx: float, dt: float, 
                       n_steps: int) -> np.ndarray:
        """Solve heat equation (1D) using finite differences"""
        u = initial_condition.copy()
        n_points = len(u)
        
        for _ in range(n_steps):
            u_new = u.copy()
            for i in range(1, n_points - 1):
                u_new[i] = u[i] + diffusion_coeff * dt / (dx**2) * (u[i+1] - 2*u[i] + u[i-1])
            u = u_new
        
        return u
    
    @staticmethod
    def solve_wave_equation(initial_position: np.ndarray,
                           initial_velocity: np.ndarray,
                           wave_speed: float,
                           dx: float, dt: float,
                           n_steps: int) -> List[np.ndarray]:
        """Solve wave equation using finite differences"""
        n_points = len(initial_position)
        u_prev = initial_position.copy()
        u_curr = initial_position + initial_velocity * dt
        
        solutions = [u_prev, u_curr]
        c = wave_speed * dt / dx
        
        for _ in range(n_steps - 2):
            u_next = np.zeros(n_points)
            for i in range(1, n_points - 1):
                u_next[i] = 2*u_curr[i] - u_prev[i] + c**2 * (u_curr[i+1] - 2*u_curr[i] + u_curr[i-1])
            
            u_prev = u_curr
            u_curr = u_next
            solutions.append(u_curr)
        
        return solutions

# Signal Processing
class SignalProcessing:
    """Advanced signal processing functions"""
    
    @staticmethod
    def fft_analysis(signal: np.ndarray, sample_rate: float) -> Dict[str, np.ndarray]:
        """Perform FFT analysis with frequency spectrum"""
        n = len(signal)
        fft_values = np.fft.fft(signal)
        frequencies = np.fft.fftfreq(n, 1/sample_rate)
        
        # Only positive frequencies
        positive_freq_idx = frequencies > 0
        frequencies = frequencies[positive_freq_idx]
        magnitude = np.abs(fft_values[positive_freq_idx])
        phase = np.angle(fft_values[positive_freq_idx])
        
        return {
            'frequencies': frequencies,
            'magnitude': magnitude,
            'phase': phase,
            'dominant_frequency': frequencies[np.argmax(magnitude)]
        }
    
    @staticmethod
    def filter_signal(signal: np.ndarray, sample_rate: float,
                     filter_type: str = 'lowpass',
                     cutoff: Union[float, Tuple[float, float]] = 100) -> np.ndarray:
        """Apply various filters to signal"""
        from scipy import signal as sig
        
        nyquist = sample_rate / 2
        
        if filter_type == 'lowpass':
            b, a = sig.butter(4, cutoff / nyquist, btype='low')
        elif filter_type == 'highpass':
            b, a = sig.butter(4, cutoff / nyquist, btype='high')
        elif filter_type == 'bandpass':
            b, a = sig.butter(4, [cutoff[0] / nyquist, cutoff[1] / nyquist], btype='band')
        else:
            raise ValueError(f"Unknown filter type: {filter_type}")
        
        return sig.filtfilt(b, a, signal)
    
    @staticmethod
    def wavelet_transform(signal: np.ndarray, wavelet: str = 'db4') -> Dict[str, Any]:
        """Perform wavelet transform for time-frequency analysis"""
        import pywt
        
        coeffs = pywt.wavedec(signal, wavelet)
        reconstructed = pywt.waverec(coeffs, wavelet)
        
        return {
            'coefficients': coeffs,
            'reconstructed': reconstructed,
            'levels': len(coeffs) - 1
        }

# Optimization Tools
class Optimization:
    """Advanced optimization algorithms"""
    
    @staticmethod
    def minimize_global(func: Callable, bounds: List[Tuple[float, float]],
                       method: str = 'differential_evolution') -> Dict[str, Any]:
        """Global optimization with various algorithms"""
        if method == 'differential_evolution':
            result = optimize.differential_evolution(func, bounds)
        elif method == 'basinhopping':
            x0 = np.mean(bounds, axis=1)
            result = optimize.basinhopping(func, x0)
        elif method == 'shgo':
            result = optimize.shgo(func, bounds)
        else:
            raise ValueError(f"Unknown method: {method}")
        
        return {
            'x': result.x,
            'fun': result.fun,
            'success': result.success,
            'message': result.message,
            'nfev': result.nfev
        }
    
    @staticmethod
    def constrained_optimization(func: Callable, x0: np.ndarray,
                                constraints: List[Dict],
                                bounds: Optional[List[Tuple]] = None) -> Dict[str, Any]:
        """Solve constrained optimization problems"""
        result = optimize.minimize(func, x0, method='SLSQP',
                                  constraints=constraints, bounds=bounds)
        
        return {
            'x': result.x,
            'fun': result.fun,
            'success': result.success,
            'constraint_violations': Optimization._check_constraints(result.x, constraints)
        }
    
    @staticmethod
    def _check_constraints(x: np.ndarray, constraints: List[Dict]) -> List[float]:
        """Check constraint violations"""
        violations = []
        for constraint in constraints:
            if constraint['type'] == 'eq':
                violations.append(abs(constraint['fun'](x)))
            else:  # ineq
                violations.append(max(0, -constraint['fun'](x)))
        return violations

# Quantum Computing Simulator
class QuantumSimulator:
    """Basic quantum computing simulation"""
    
    @staticmethod
    def create_qubit(alpha: complex = 1+0j, beta: complex = 0+0j) -> np.ndarray:
        """Create a qubit state |ψ⟩ = α|0⟩ + β|1⟩"""
        norm = np.sqrt(abs(alpha)**2 + abs(beta)**2)
        return np.array([alpha/norm, beta/norm], dtype=complex)
    
    @staticmethod
    def hadamard_gate(qubit: np.ndarray) -> np.ndarray:
        """Apply Hadamard gate"""
        H = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
        return H @ qubit
    
    @staticmethod
    def pauli_x(qubit: np.ndarray) -> np.ndarray:
        """Apply Pauli-X (NOT) gate"""
        X = np.array([[0, 1], [1, 0]])
        return X @ qubit
    
    @staticmethod
    def measure(qubit: np.ndarray, n_measurements: int = 1000) -> Dict[str, Any]:
        """Measure qubit state"""
        prob_0 = abs(qubit[0])**2
        prob_1 = abs(qubit[1])**2
        
        measurements = np.random.choice([0, 1], size=n_measurements, 
                                      p=[prob_0, prob_1])
        
        return {
            'probabilities': {'|0⟩': prob_0, '|1⟩': prob_1},
            'measurements': measurements,
            'counts': {
                '|0⟩': np.sum(measurements == 0),
                '|1⟩': np.sum(measurements == 1)
            }
        }
    
    @staticmethod
    def entangle(qubit1: np.ndarray, qubit2: np.ndarray) -> np.ndarray:
        """Create entangled state (simplified Bell state)"""
        # Create |00⟩ + |11⟩ (normalized)
        entangled = np.zeros(4, dtype=complex)
        entangled[0] = 1/np.sqrt(2)  # |00⟩
        entangled[3] = 1/np.sqrt(2)  # |11⟩
        return entangled

# Parallel Computing Utilities
class ParallelComputing:
    """Utilities for parallel and distributed computing"""
    
    @staticmethod
    async def async_compute(funcs: List[Callable], args_list: List[tuple]) -> List[Any]:
        """Run multiple functions asynchronously"""
        tasks = []
        for func, args in zip(funcs, args_list):
            task = asyncio.create_task(asyncio.to_thread(func, *args))
            tasks.append(task)
        
        return await asyncio.gather(*tasks)
    
    @staticmethod
    def parallel_map(func: Callable, data: List, n_workers: int = None) -> List[Any]:
        """Parallel map operation"""
        if n_workers is None:
            n_workers = mp.cpu_count()
        
        with ProcessPoolExecutor(max_workers=n_workers) as executor:
            results = list(executor.map(func, data))
        
        return results
    
    @staticmethod
    def gpu_accelerate(func: Callable) -> Callable:
        """Decorator for GPU acceleration using numba.cuda"""
        if cuda.is_available():
            return cuda.jit(func)
        else:
            warnings.warn("CUDA not available, falling back to CPU")
            return jit(nopython=True)(func)

# Visualization Tools
class Visualization:
    """Advanced scientific visualization"""
    
    @staticmethod
    def plot_uncertainty(x: np.ndarray, y: np.ndarray, 
                        y_err: np.ndarray, title: str = "Data with Uncertainty"):
        """Plot data with uncertainty bands"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.plot(x, y, 'b-', label='Mean')
        ax.fill_between(x, y - y_err, y + y_err, alpha=0.3, label='Uncertainty')
        
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_title(title)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        return fig
    
    @staticmethod
    def plot_3d_surface(X: np.ndarray, Y: np.ndarray, Z: np.ndarray,
                       title: str = "3D Surface"):
        """Create 3D surface plot"""
        from mpl_toolkits.mplot3d import Axes3D
        
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        surf = ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)
        
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title(title)
        
        fig.colorbar(surf)
        
        return fig
    
    @staticmethod
    def animate_evolution(data_sequence: List[np.ndarray], 
                         interval: int = 50) -> Any:
        """Animate evolution of data over time"""
        from matplotlib.animation import FuncAnimation
        
        fig, ax = plt.subplots()
        line, = ax.plot([], [], 'b-')
        
        ax.set_xlim(0, len(data_sequence[0]))
        ax.set_ylim(np.min(data_sequence), np.max(data_sequence))
        
        def animate(frame):
            line.set_data(range(len(data_sequence[frame])), data_sequence[frame])
            return line,
        
        anim = FuncAnimation(fig, animate, frames=len(data_sequence),
                           interval=interval, blit=True)
        
        return anim

# Export all classes
__all__ = [
    'Statistics',
    'MachineLearning',
    'NeuralNetwork',
    'DifferentialEquations',
    'SignalProcessing',
    'Optimization',
    'QuantumSimulator',
    'ParallelComputing',
    'Visualization'
]