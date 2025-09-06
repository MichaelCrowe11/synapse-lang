"""
Scientific Computing Integration for Synapse
Bridges Synapse with NumPy, SciPy, and other scientific libraries
"""

import numpy as np
import scipy
from scipy import stats, optimize, signal, fft
from scipy.integrate import odeint, solve_ivp
from typing import Any, Dict, List, Optional, Union, Callable
import matplotlib.pyplot as plt
from dataclasses import dataclass
import warnings

# Import quantum ML capabilities
from synapse_quantum_ml import (
    QuantumNeuralNetwork, 
    QuantumEnsemble, 
    ContinuousQuantumLearner,
    create_quantum_neural_network,
    start_continuous_learning,
    quantum_ensemble_predict
)

@dataclass
class SynapseArray:
    """Synapse wrapper for NumPy arrays with uncertainty support"""
    data: np.ndarray
    uncertainty: Optional[np.ndarray] = None
    
    def __repr__(self):
        if self.uncertainty is not None:
            return f"SynapseArray({self.data} ± {self.uncertainty})"
        return f"SynapseArray({self.data})"
    
    def propagate_uncertainty(self, func: Callable, *args, **kwargs):
        """Propagate uncertainty through a function using linear approximation"""
        result = func(self.data, *args, **kwargs)
        
        if self.uncertainty is not None:
            # Use numerical differentiation for uncertainty propagation
            epsilon = 1e-8
            grad = np.zeros_like(self.data)
            
            for i in np.ndindex(self.data.shape):
                data_plus = self.data.copy()
                data_plus[i] += epsilon
                grad[i] = (func(data_plus, *args, **kwargs) - result) / epsilon
            
            # Propagate uncertainty: σ_f = |∂f/∂x| * σ_x
            uncertainty_out = np.abs(grad) * self.uncertainty
            return SynapseArray(result, uncertainty_out)
        
        return SynapseArray(result)

class ScientificFunctions:
    """Built-in scientific functions for Synapse"""
    
    @staticmethod
    def tensor(*shape, dtype=np.float64):
        """Create a tensor with specified shape"""
        if len(shape) == 1 and isinstance(shape[0], (list, tuple)):
            shape = shape[0]
        return np.zeros(shape, dtype=dtype)
    
    @staticmethod
    def random_tensor(*shape, distribution='normal', **params):
        """Create random tensor with specified distribution"""
        if len(shape) == 1 and isinstance(shape[0], (list, tuple)):
            shape = shape[0]
        
        if distribution == 'normal':
            mu = params.get('mu', 0)
            sigma = params.get('sigma', 1)
            return np.random.normal(mu, sigma, shape)
        elif distribution == 'uniform':
            low = params.get('low', 0)
            high = params.get('high', 1)
            return np.random.uniform(low, high, shape)
        elif distribution == 'poisson':
            lam = params.get('lambda', 1)
            return np.random.poisson(lam, shape)
        else:
            return np.random.random(shape)
    
    @staticmethod
    def solve_ode(dydt, y0, t, args=()):
        """Solve ordinary differential equation"""
        return odeint(dydt, y0, t, args=args)
    
    @staticmethod
    def optimize_function(func, x0, method='BFGS', bounds=None):
        """Optimize a function"""
        result = optimize.minimize(func, x0, method=method, bounds=bounds)
        return result.x, result.fun
    
    @staticmethod
    def fft_transform(signal_data):
        """Fast Fourier Transform"""
        return fft.fft(signal_data)
    
    @staticmethod
    def inverse_fft(freq_data):
        """Inverse Fast Fourier Transform"""
        return fft.ifft(freq_data)
    
    @staticmethod
    def convolve(signal1, signal2, mode='same'):
        """Convolution of two signals"""
        return signal.convolve(signal1, signal2, mode=mode)
    
    @staticmethod
    def create_quantum_neural_network(input_size: int, hidden_size: int, output_size: int):
        """Create a quantum neural network for advanced machine learning"""
        return create_quantum_neural_network(input_size, hidden_size, output_size)
    
    @staticmethod
    def start_continuous_quantum_learning(data_generator: Callable, max_iterations: int = 100):
        """Start continuous quantum learning with auto-adjustment"""
        return start_continuous_learning(data_generator, max_iterations)
    
    @staticmethod
    def quantum_ensemble_predict(ensemble: QuantumEnsemble, X: np.ndarray):
        """Make predictions using a quantum ensemble"""
        return quantum_ensemble_predict(ensemble, X)
    
    @staticmethod
    def create_quantum_ensemble(num_models: int = 5):
        """Create an ensemble of quantum models"""
        return QuantumEnsemble(num_models)
    
    @staticmethod
    def quantum_state_preparation(num_qubits: int):
        """Prepare a quantum state for computation"""
        from synapse_quantum_ml import QuantumState
        return QuantumState(num_qubits)
    
    @staticmethod
    def quantum_circuit_optimization(target_function: Callable, initial_circuit):
        """Optimize quantum circuits automatically"""
        from synapse_quantum_ml import AutoQuantumOptimizer
        optimizer = AutoQuantumOptimizer()
        return optimizer.optimize_circuit(target_function, initial_circuit)
    
    @staticmethod
    def correlate(signal1, signal2, mode='same'):
        """Cross-correlation of two signals"""
        return signal.correlate(signal1, signal2, mode=mode)
    
    @staticmethod
    def statistical_test(data1, data2=None, test='ttest'):
        """Perform statistical hypothesis test"""
        if test == 'ttest':
            if data2 is None:
                return stats.ttest_1samp(data1, 0)
            return stats.ttest_ind(data1, data2)
        elif test == 'ks':
            if data2 is None:
                return stats.kstest(data1, 'norm')
            return stats.ks_2samp(data1, data2)
        elif test == 'wilcoxon':
            if data2 is None:
                return stats.wilcoxon(data1)
            return stats.wilcoxon(data1, data2)
        elif test == 'mannwhitney':
            return stats.mannwhitneyu(data1, data2)
    
    @staticmethod
    def fit_distribution(data, distribution='normal'):
        """Fit a probability distribution to data"""
        if distribution == 'normal':
            params = stats.norm.fit(data)
            return {'mu': params[0], 'sigma': params[1]}
        elif distribution == 'exponential':
            params = stats.expon.fit(data)
            return {'loc': params[0], 'scale': params[1]}
        elif distribution == 'gamma':
            params = stats.gamma.fit(data)
            return {'a': params[0], 'loc': params[1], 'scale': params[2]}
        else:
            return {}
    
    @staticmethod
    def monte_carlo(func, n_samples=10000, **param_distributions):
        """Monte Carlo simulation"""
        results = []
        
        for _ in range(n_samples):
            params = {}
            for param_name, dist_info in param_distributions.items():
                if isinstance(dist_info, tuple):
                    # Assume normal distribution (mean, std)
                    params[param_name] = np.random.normal(dist_info[0], dist_info[1])
                elif isinstance(dist_info, dict):
                    # Distribution with parameters
                    dist_type = dist_info.get('type', 'normal')
                    if dist_type == 'normal':
                        params[param_name] = np.random.normal(
                            dist_info.get('mu', 0), 
                            dist_info.get('sigma', 1)
                        )
                    elif dist_type == 'uniform':
                        params[param_name] = np.random.uniform(
                            dist_info.get('low', 0),
                            dist_info.get('high', 1)
                        )
                else:
                    params[param_name] = dist_info
            
            results.append(func(**params))
        
        results = np.array(results)
        return {
            'mean': np.mean(results),
            'std': np.std(results),
            'percentiles': np.percentile(results, [5, 25, 50, 75, 95]),
            'samples': results
        }
    
    @staticmethod
    def parallel_map(func, data, n_workers=None):
        """Parallel map operation on data"""
        from concurrent.futures import ProcessPoolExecutor
        
        if n_workers is None:
            import multiprocessing
            n_workers = multiprocessing.cpu_count()
        
        with ProcessPoolExecutor(max_workers=n_workers) as executor:
            results = list(executor.map(func, data))
        
        return results
    
    @staticmethod
    def eigenanalysis(matrix):
        """Compute eigenvalues and eigenvectors"""
        eigenvalues, eigenvectors = np.linalg.eig(matrix)
        return {
            'eigenvalues': eigenvalues,
            'eigenvectors': eigenvectors,
            'condition_number': np.linalg.cond(matrix)
        }
    
    @staticmethod
    def svd_decomposition(matrix):
        """Singular Value Decomposition"""
        U, S, Vt = np.linalg.svd(matrix)
        return {
            'U': U,
            'singular_values': S,
            'Vt': Vt,
            'rank': np.linalg.matrix_rank(matrix)
        }

class QuantumSimulator:
    """Quantum computing simulation capabilities"""
    
    @staticmethod
    def create_qubit(alpha=1.0, beta=0.0):
        """Create a qubit state |ψ⟩ = α|0⟩ + β|1⟩"""
        # Normalize
        norm = np.sqrt(abs(alpha)**2 + abs(beta)**2)
        return np.array([alpha/norm, beta/norm], dtype=complex)
    
    @staticmethod
    def hadamard_gate():
        """Hadamard gate matrix"""
        return np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
    
    @staticmethod
    def pauli_x():
        """Pauli-X (NOT) gate"""
        return np.array([[0, 1], [1, 0]], dtype=complex)
    
    @staticmethod
    def pauli_y():
        """Pauli-Y gate"""
        return np.array([[0, -1j], [1j, 0]], dtype=complex)
    
    @staticmethod
    def pauli_z():
        """Pauli-Z gate"""
        return np.array([[1, 0], [0, -1]], dtype=complex)
    
    @staticmethod
    def cnot():
        """Controlled-NOT gate"""
        return np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0]
        ], dtype=complex)
    
    @staticmethod
    def measure(state, n_measurements=1000):
        """Simulate quantum measurement"""
        probabilities = np.abs(state)**2
        outcomes = np.random.choice(len(state), size=n_measurements, p=probabilities)
        counts = np.bincount(outcomes, minlength=len(state))
        return counts / n_measurements
    
    @staticmethod
    def entangle(qubit1, qubit2):
        """Create entangled state from two qubits"""
        return np.kron(qubit1, qubit2)

class ClimateModeling:
    """Climate and Earth system modeling functions"""
    
    @staticmethod
    def radiative_forcing(co2_ppm, co2_baseline=280):
        """Calculate radiative forcing from CO2"""
        return 5.35 * np.log(co2_ppm / co2_baseline)
    
    @staticmethod
    def temperature_response(forcing, sensitivity=3.0, time_constant=10):
        """Calculate temperature response to forcing"""
        def response(t):
            return sensitivity * forcing * (1 - np.exp(-t/time_constant))
        return response
    
    @staticmethod
    def carbon_cycle(emissions, ocean_uptake=0.25, land_uptake=0.25):
        """Simple carbon cycle model"""
        atmospheric_fraction = 1 - ocean_uptake - land_uptake
        return emissions * atmospheric_fraction
    
    @staticmethod
    def sea_ice_albedo(temperature, threshold=-2):
        """Calculate albedo feedback from sea ice"""
        ice_fraction = np.clip(1 - (temperature - threshold) / 10, 0, 1)
        albedo_ice = 0.6
        albedo_ocean = 0.06
        return ice_fraction * albedo_ice + (1 - ice_fraction) * albedo_ocean

class DrugDiscovery:
    """Molecular simulation and drug discovery functions"""
    
    @staticmethod
    def binding_affinity(distance, epsilon=1.0, sigma=3.5):
        """Lennard-Jones potential for binding affinity"""
        return 4 * epsilon * ((sigma/distance)**12 - (sigma/distance)**6)
    
    @staticmethod
    def michaelis_menten(substrate, vmax, km):
        """Michaelis-Menten enzyme kinetics"""
        return vmax * substrate / (km + substrate)
    
    @staticmethod
    def hill_equation(ligand, ec50, n=1):
        """Hill equation for dose-response"""
        return ligand**n / (ec50**n + ligand**n)
    
    @staticmethod
    def admet_score(logp, mw, hbd, hba, tpsa):
        """Calculate ADMET score based on Lipinski's rule of five"""
        score = 0
        if logp <= 5:
            score += 20
        if mw <= 500:
            score += 20
        if hbd <= 5:
            score += 20
        if hba <= 10:
            score += 20
        if tpsa <= 140:
            score += 20
        return score

# Enhanced interpreter integration
def integrate_scientific_functions(interpreter):
    """Integrate scientific functions into Synapse interpreter"""
    
    # Add NumPy functions
    interpreter.variables['np'] = np
    interpreter.variables['scipy'] = scipy
    
    # Add custom scientific functions
    sci_funcs = ScientificFunctions()
    interpreter.variables['tensor'] = sci_funcs.tensor
    interpreter.variables['random_tensor'] = sci_funcs.random_tensor
    interpreter.variables['solve_ode'] = sci_funcs.solve_ode
    interpreter.variables['optimize'] = sci_funcs.optimize_function
    interpreter.variables['fft'] = sci_funcs.fft_transform
    interpreter.variables['ifft'] = sci_funcs.inverse_fft
    interpreter.variables['convolve'] = sci_funcs.convolve
    interpreter.variables['correlate'] = sci_funcs.correlate
    interpreter.variables['stat_test'] = sci_funcs.statistical_test
    interpreter.variables['fit_dist'] = sci_funcs.fit_distribution
    interpreter.variables['monte_carlo'] = sci_funcs.monte_carlo
    interpreter.variables['parallel_map'] = sci_funcs.parallel_map
    interpreter.variables['eigen'] = sci_funcs.eigenanalysis
    interpreter.variables['svd'] = sci_funcs.svd_decomposition
    
    # Add quantum functions
    quantum = QuantumSimulator()
    interpreter.variables['qubit'] = quantum.create_qubit
    interpreter.variables['hadamard'] = quantum.hadamard_gate
    interpreter.variables['pauli_x'] = quantum.pauli_x
    interpreter.variables['pauli_y'] = quantum.pauli_y
    interpreter.variables['pauli_z'] = quantum.pauli_z
    interpreter.variables['cnot'] = quantum.cnot
    interpreter.variables['measure'] = quantum.measure
    interpreter.variables['entangle'] = quantum.entangle
    
    # Add climate functions
    climate = ClimateModeling()
    interpreter.variables['radiative_forcing'] = climate.radiative_forcing
    interpreter.variables['temp_response'] = climate.temperature_response
    interpreter.variables['carbon_cycle'] = climate.carbon_cycle
    interpreter.variables['sea_ice_albedo'] = climate.sea_ice_albedo
    
    # Add drug discovery functions
    drug = DrugDiscovery()
    interpreter.variables['binding_affinity'] = drug.binding_affinity
    interpreter.variables['michaelis_menten'] = drug.michaelis_menten
    interpreter.variables['hill_equation'] = drug.hill_equation
    interpreter.variables['admet_score'] = drug.admet_score
    
    # Mathematical constants
    interpreter.variables['pi'] = np.pi
    interpreter.variables['e'] = np.e
    interpreter.variables['golden_ratio'] = (1 + np.sqrt(5)) / 2
    interpreter.variables['avogadro'] = 6.02214076e23
    interpreter.variables['boltzmann'] = 1.380649e-23
    interpreter.variables['planck'] = 6.62607015e-34
    interpreter.variables['light_speed'] = 299792458  # m/s
    
    return interpreter