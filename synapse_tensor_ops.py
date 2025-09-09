"""
Tensor operations for Synapse language
Implements tensor arithmetic, manipulation, and scientific computing operations
"""

import numpy as np
from typing import Union, List, Tuple, Optional, Any
from dataclasses import dataclass
import scipy.linalg as la
import scipy.sparse as sp

@dataclass
class SynapseTensor:
    """Tensor with uncertainty propagation support"""
    data: np.ndarray
    uncertainty: Optional[np.ndarray] = None
    name: Optional[str] = None
    
    def __post_init__(self):
        """Ensure data is numpy array"""
        if not isinstance(self.data, np.ndarray):
            self.data = np.array(self.data)
        
        if self.uncertainty is not None and not isinstance(self.uncertainty, np.ndarray):
            self.uncertainty = np.array(self.uncertainty)
    
    @property
    def shape(self) -> Tuple[int, ...]:
        return self.data.shape
    
    @property
    def ndim(self) -> int:
        return self.data.ndim
    
    @property
    def size(self) -> int:
        return self.data.size
    
    @property
    def dtype(self):
        return self.data.dtype
    
    def __str__(self) -> str:
        if self.uncertainty is not None:
            return f"Tensor({self.data} ± {self.uncertainty})"
        return f"Tensor({self.data})"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __add__(self, other: Union['SynapseTensor', np.ndarray, float]) -> 'SynapseTensor':
        """Addition with uncertainty propagation"""
        if isinstance(other, SynapseTensor):
            result_data = self.data + other.data
            
            # Propagate uncertainty
            if self.uncertainty is not None or other.uncertainty is not None:
                self_unc = self.uncertainty if self.uncertainty is not None else np.zeros_like(self.data)
                other_unc = other.uncertainty if other.uncertainty is not None else np.zeros_like(other.data)
                result_uncertainty = np.sqrt(self_unc**2 + other_unc**2)
            else:
                result_uncertainty = None
            
            return SynapseTensor(result_data, result_uncertainty)
        else:
            # Scalar or array addition
            result_data = self.data + other
            return SynapseTensor(result_data, self.uncertainty)
    
    def __sub__(self, other: Union['SynapseTensor', np.ndarray, float]) -> 'SynapseTensor':
        """Subtraction with uncertainty propagation"""
        if isinstance(other, SynapseTensor):
            result_data = self.data - other.data
            
            # Propagate uncertainty
            if self.uncertainty is not None or other.uncertainty is not None:
                self_unc = self.uncertainty if self.uncertainty is not None else np.zeros_like(self.data)
                other_unc = other.uncertainty if other.uncertainty is not None else np.zeros_like(other.data)
                result_uncertainty = np.sqrt(self_unc**2 + other_unc**2)
            else:
                result_uncertainty = None
            
            return SynapseTensor(result_data, result_uncertainty)
        else:
            result_data = self.data - other
            return SynapseTensor(result_data, self.uncertainty)
    
    def __mul__(self, other: Union['SynapseTensor', np.ndarray, float]) -> 'SynapseTensor':
        """Element-wise multiplication with uncertainty propagation"""
        if isinstance(other, SynapseTensor):
            result_data = self.data * other.data
            
            # Propagate uncertainty (relative uncertainties add in quadrature)
            if self.uncertainty is not None or other.uncertainty is not None:
                self_unc = self.uncertainty if self.uncertainty is not None else np.zeros_like(self.data)
                other_unc = other.uncertainty if other.uncertainty is not None else np.zeros_like(other.data)
                
                # Avoid division by zero
                with np.errstate(divide='ignore', invalid='ignore'):
                    rel_unc_self = np.where(self.data != 0, self_unc / np.abs(self.data), 0)
                    rel_unc_other = np.where(other.data != 0, other_unc / np.abs(other.data), 0)
                
                rel_unc_total = np.sqrt(rel_unc_self**2 + rel_unc_other**2)
                result_uncertainty = np.abs(result_data) * rel_unc_total
            else:
                result_uncertainty = None
            
            return SynapseTensor(result_data, result_uncertainty)
        else:
            result_data = self.data * other
            if self.uncertainty is not None:
                result_uncertainty = np.abs(other) * self.uncertainty
            else:
                result_uncertainty = None
            return SynapseTensor(result_data, result_uncertainty)
    
    def __truediv__(self, other: Union['SynapseTensor', np.ndarray, float]) -> 'SynapseTensor':
        """Element-wise division with uncertainty propagation"""
        if isinstance(other, SynapseTensor):
            result_data = self.data / other.data
            
            # Propagate uncertainty
            if self.uncertainty is not None or other.uncertainty is not None:
                self_unc = self.uncertainty if self.uncertainty is not None else np.zeros_like(self.data)
                other_unc = other.uncertainty if other.uncertainty is not None else np.zeros_like(other.data)
                
                with np.errstate(divide='ignore', invalid='ignore'):
                    rel_unc_self = np.where(self.data != 0, self_unc / np.abs(self.data), 0)
                    rel_unc_other = np.where(other.data != 0, other_unc / np.abs(other.data), 0)
                
                rel_unc_total = np.sqrt(rel_unc_self**2 + rel_unc_other**2)
                result_uncertainty = np.abs(result_data) * rel_unc_total
            else:
                result_uncertainty = None
            
            return SynapseTensor(result_data, result_uncertainty)
        else:
            result_data = self.data / other
            if self.uncertainty is not None:
                result_uncertainty = self.uncertainty / np.abs(other)
            else:
                result_uncertainty = None
            return SynapseTensor(result_data, result_uncertainty)
    
    def __matmul__(self, other: 'SynapseTensor') -> 'SynapseTensor':
        """Matrix multiplication with uncertainty propagation"""
        if not isinstance(other, SynapseTensor):
            other = SynapseTensor(other)
        
        result_data = self.data @ other.data
        
        # Simplified uncertainty propagation for matrix multiplication
        if self.uncertainty is not None or other.uncertainty is not None:
            # This is a simplified approach - full error propagation would be more complex
            self_unc = self.uncertainty if self.uncertainty is not None else np.zeros_like(self.data)
            other_unc = other.uncertainty if other.uncertainty is not None else np.zeros_like(other.data)
            
            # Approximate uncertainty propagation
            unc_term1 = np.abs(self_unc @ other.data)
            unc_term2 = np.abs(self.data @ other_unc)
            result_uncertainty = np.sqrt(unc_term1**2 + unc_term2**2)
        else:
            result_uncertainty = None
        
        return SynapseTensor(result_data, result_uncertainty)
    
    def __pow__(self, power: float) -> 'SynapseTensor':
        """Power operation with uncertainty propagation"""
        result_data = self.data ** power
        
        if self.uncertainty is not None:
            # Propagate uncertainty: δ(x^n) = |n * x^(n-1) * δx|
            with np.errstate(divide='ignore', invalid='ignore'):
                result_uncertainty = np.abs(power * self.data**(power-1) * self.uncertainty)
        else:
            result_uncertainty = None
        
        return SynapseTensor(result_data, result_uncertainty)
    
    def __getitem__(self, key) -> 'SynapseTensor':
        """Tensor indexing"""
        result_data = self.data[key]
        
        if self.uncertainty is not None:
            result_uncertainty = self.uncertainty[key]
        else:
            result_uncertainty = None
        
        if isinstance(result_data, np.ndarray):
            return SynapseTensor(result_data, result_uncertainty)
        else:
            # Scalar result
            return result_data if result_uncertainty is None else (result_data, result_uncertainty)
    
    def __setitem__(self, key, value):
        """Tensor assignment"""
        if isinstance(value, SynapseTensor):
            self.data[key] = value.data
            if value.uncertainty is not None:
                if self.uncertainty is None:
                    self.uncertainty = np.zeros_like(self.data)
                self.uncertainty[key] = value.uncertainty
        else:
            self.data[key] = value
    
    def reshape(self, *shape) -> 'SynapseTensor':
        """Reshape tensor"""
        result_data = self.data.reshape(*shape)
        
        if self.uncertainty is not None:
            result_uncertainty = self.uncertainty.reshape(*shape)
        else:
            result_uncertainty = None
        
        return SynapseTensor(result_data, result_uncertainty)
    
    def transpose(self, axes: Optional[List[int]] = None) -> 'SynapseTensor':
        """Transpose tensor"""
        result_data = np.transpose(self.data, axes)
        
        if self.uncertainty is not None:
            result_uncertainty = np.transpose(self.uncertainty, axes)
        else:
            result_uncertainty = None
        
        return SynapseTensor(result_data, result_uncertainty)
    
    def sum(self, axis: Optional[Union[int, Tuple[int, ...]]] = None) -> 'SynapseTensor':
        """Sum with uncertainty propagation"""
        result_data = np.sum(self.data, axis=axis)
        
        if self.uncertainty is not None:
            # Uncertainties add in quadrature
            result_uncertainty = np.sqrt(np.sum(self.uncertainty**2, axis=axis))
        else:
            result_uncertainty = None
        
        return SynapseTensor(result_data, result_uncertainty)
    
    def mean(self, axis: Optional[Union[int, Tuple[int, ...]]] = None) -> 'SynapseTensor':
        """Mean with uncertainty propagation"""
        result_data = np.mean(self.data, axis=axis)
        
        if self.uncertainty is not None:
            # Standard error of the mean
            n = self.data.shape[axis] if axis is not None else self.data.size
            result_uncertainty = np.sqrt(np.sum(self.uncertainty**2, axis=axis)) / n
        else:
            result_uncertainty = None
        
        return SynapseTensor(result_data, result_uncertainty)
    
    def std(self, axis: Optional[Union[int, Tuple[int, ...]]] = None) -> 'SynapseTensor':
        """Standard deviation"""
        result_data = np.std(self.data, axis=axis)
        return SynapseTensor(result_data)
    
    def normalize(self, axis: Optional[int] = None) -> 'SynapseTensor':
        """Normalize tensor"""
        norm = np.linalg.norm(self.data, axis=axis, keepdims=True)
        result_data = self.data / norm
        
        if self.uncertainty is not None:
            # Propagate uncertainty through normalization
            result_uncertainty = self.uncertainty / norm
        else:
            result_uncertainty = None
        
        return SynapseTensor(result_data, result_uncertainty)


class TensorOperations:
    """Static methods for tensor operations"""
    
    @staticmethod
    def zeros(shape: Union[int, Tuple[int, ...]], dtype=np.float64) -> SynapseTensor:
        """Create zero tensor"""
        return SynapseTensor(np.zeros(shape, dtype=dtype))
    
    @staticmethod
    def ones(shape: Union[int, Tuple[int, ...]], dtype=np.float64) -> SynapseTensor:
        """Create ones tensor"""
        return SynapseTensor(np.ones(shape, dtype=dtype))
    
    @staticmethod
    def random(shape: Union[int, Tuple[int, ...]], 
               distribution: str = 'uniform',
               **kwargs) -> SynapseTensor:
        """Create random tensor"""
        if distribution == 'uniform':
            low = kwargs.get('low', 0.0)
            high = kwargs.get('high', 1.0)
            data = np.random.uniform(low, high, shape)
        elif distribution == 'normal':
            mean = kwargs.get('mean', 0.0)
            std = kwargs.get('std', 1.0)
            data = np.random.normal(mean, std, shape)
        elif distribution == 'poisson':
            lam = kwargs.get('lam', 1.0)
            data = np.random.poisson(lam, shape)
        else:
            raise ValueError(f"Unknown distribution: {distribution}")
        
        return SynapseTensor(data)
    
    @staticmethod
    def eye(n: int, m: Optional[int] = None, dtype=np.float64) -> SynapseTensor:
        """Create identity matrix"""
        return SynapseTensor(np.eye(n, m, dtype=dtype))
    
    @staticmethod
    def linspace(start: float, stop: float, num: int = 50) -> SynapseTensor:
        """Create linearly spaced tensor"""
        return SynapseTensor(np.linspace(start, stop, num))
    
    @staticmethod
    def logspace(start: float, stop: float, num: int = 50, base: float = 10.0) -> SynapseTensor:
        """Create logarithmically spaced tensor"""
        return SynapseTensor(np.logspace(start, stop, num, base=base))
    
    @staticmethod
    def concatenate(tensors: List[SynapseTensor], axis: int = 0) -> SynapseTensor:
        """Concatenate tensors"""
        data_list = [t.data for t in tensors]
        result_data = np.concatenate(data_list, axis=axis)
        
        # Handle uncertainty
        if any(t.uncertainty is not None for t in tensors):
            unc_list = []
            for t in tensors:
                if t.uncertainty is not None:
                    unc_list.append(t.uncertainty)
                else:
                    unc_list.append(np.zeros_like(t.data))
            result_uncertainty = np.concatenate(unc_list, axis=axis)
        else:
            result_uncertainty = None
        
        return SynapseTensor(result_data, result_uncertainty)
    
    @staticmethod
    def stack(tensors: List[SynapseTensor], axis: int = 0) -> SynapseTensor:
        """Stack tensors"""
        data_list = [t.data for t in tensors]
        result_data = np.stack(data_list, axis=axis)
        
        # Handle uncertainty
        if any(t.uncertainty is not None for t in tensors):
            unc_list = []
            for t in tensors:
                if t.uncertainty is not None:
                    unc_list.append(t.uncertainty)
                else:
                    unc_list.append(np.zeros_like(t.data))
            result_uncertainty = np.stack(unc_list, axis=axis)
        else:
            result_uncertainty = None
        
        return SynapseTensor(result_data, result_uncertainty)
    
    @staticmethod
    def dot(a: SynapseTensor, b: SynapseTensor) -> SynapseTensor:
        """Dot product"""
        return a @ b
    
    @staticmethod
    def cross(a: SynapseTensor, b: SynapseTensor, axis: int = -1) -> SynapseTensor:
        """Cross product"""
        result_data = np.cross(a.data, b.data, axis=axis)
        
        # Simplified uncertainty propagation for cross product
        if a.uncertainty is not None or b.uncertainty is not None:
            # This is an approximation
            a_unc = a.uncertainty if a.uncertainty is not None else np.zeros_like(a.data)
            b_unc = b.uncertainty if b.uncertainty is not None else np.zeros_like(b.data)
            
            # Propagate through cross product (simplified)
            result_uncertainty = np.sqrt(
                np.cross(a_unc, b.data, axis=axis)**2 + 
                np.cross(a.data, b_unc, axis=axis)**2
            )
        else:
            result_uncertainty = None
        
        return SynapseTensor(result_data, result_uncertainty)
    
    @staticmethod
    def eigenvalues(tensor: SynapseTensor) -> SynapseTensor:
        """Compute eigenvalues"""
        if tensor.ndim != 2:
            raise ValueError("Eigenvalues require 2D tensor")
        
        eigenvals = np.linalg.eigvals(tensor.data)
        return SynapseTensor(eigenvals)
    
    @staticmethod
    def eigenvectors(tensor: SynapseTensor) -> Tuple[SynapseTensor, SynapseTensor]:
        """Compute eigenvalues and eigenvectors"""
        if tensor.ndim != 2:
            raise ValueError("Eigenvectors require 2D tensor")
        
        eigenvals, eigenvecs = np.linalg.eig(tensor.data)
        return SynapseTensor(eigenvals), SynapseTensor(eigenvecs)
    
    @staticmethod
    def svd(tensor: SynapseTensor) -> Tuple[SynapseTensor, SynapseTensor, SynapseTensor]:
        """Singular value decomposition"""
        if tensor.ndim != 2:
            raise ValueError("SVD requires 2D tensor")
        
        u, s, vh = np.linalg.svd(tensor.data)
        return SynapseTensor(u), SynapseTensor(s), SynapseTensor(vh)
    
    @staticmethod
    def inv(tensor: SynapseTensor) -> SynapseTensor:
        """Matrix inverse"""
        if tensor.ndim != 2:
            raise ValueError("Inverse requires 2D tensor")
        
        result_data = np.linalg.inv(tensor.data)
        
        # Propagate uncertainty (simplified)
        if tensor.uncertainty is not None:
            # This is a first-order approximation
            result_uncertainty = np.abs(result_data @ tensor.uncertainty @ result_data)
        else:
            result_uncertainty = None
        
        return SynapseTensor(result_data, result_uncertainty)
    
    @staticmethod
    def solve(a: SynapseTensor, b: SynapseTensor) -> SynapseTensor:
        """Solve linear system Ax = b"""
        result_data = np.linalg.solve(a.data, b.data)
        
        # Simplified uncertainty propagation
        if a.uncertainty is not None or b.uncertainty is not None:
            # This is an approximation
            a_inv = np.linalg.inv(a.data)
            
            result_uncertainty = None
            if b.uncertainty is not None:
                result_uncertainty = np.abs(a_inv @ b.uncertainty)
            
            if a.uncertainty is not None:
                term = np.abs(a_inv @ a.uncertainty @ a_inv @ b.data)
                if result_uncertainty is not None:
                    result_uncertainty = np.sqrt(result_uncertainty**2 + term**2)
                else:
                    result_uncertainty = term
        else:
            result_uncertainty = None
        
        return SynapseTensor(result_data, result_uncertainty)
    
    @staticmethod
    def fft(tensor: SynapseTensor, axis: int = -1) -> SynapseTensor:
        """Fast Fourier Transform"""
        result_data = np.fft.fft(tensor.data, axis=axis)
        
        # FFT preserves uncertainty magnitude
        if tensor.uncertainty is not None:
            result_uncertainty = np.fft.fft(tensor.uncertainty, axis=axis)
        else:
            result_uncertainty = None
        
        return SynapseTensor(result_data, result_uncertainty)
    
    @staticmethod
    def ifft(tensor: SynapseTensor, axis: int = -1) -> SynapseTensor:
        """Inverse Fast Fourier Transform"""
        result_data = np.fft.ifft(tensor.data, axis=axis)
        
        if tensor.uncertainty is not None:
            result_uncertainty = np.fft.ifft(tensor.uncertainty, axis=axis)
        else:
            result_uncertainty = None
        
        return SynapseTensor(result_data, result_uncertainty)
    
    @staticmethod
    def convolve(a: SynapseTensor, b: SynapseTensor, mode: str = 'full') -> SynapseTensor:
        """Convolution"""
        result_data = np.convolve(a.data.flatten(), b.data.flatten(), mode=mode)
        
        # Propagate uncertainty
        if a.uncertainty is not None or b.uncertainty is not None:
            a_unc = a.uncertainty.flatten() if a.uncertainty is not None else np.zeros_like(a.data.flatten())
            b_unc = b.uncertainty.flatten() if b.uncertainty is not None else np.zeros_like(b.data.flatten())
            
            # Uncertainty propagation through convolution
            unc_term1 = np.convolve(a_unc, np.abs(b.data.flatten()), mode=mode)
            unc_term2 = np.convolve(np.abs(a.data.flatten()), b_unc, mode=mode)
            result_uncertainty = np.sqrt(unc_term1**2 + unc_term2**2)
        else:
            result_uncertainty = None
        
        return SynapseTensor(result_data, result_uncertainty)
    
    @staticmethod
    def gradient(tensor: SynapseTensor, axis: Optional[int] = None) -> SynapseTensor:
        """Compute gradient"""
        if axis is None:
            result_data = np.gradient(tensor.data)
        else:
            result_data = np.gradient(tensor.data, axis=axis)
        
        # Propagate uncertainty through gradient
        if tensor.uncertainty is not None:
            if axis is None:
                result_uncertainty = np.gradient(tensor.uncertainty)
            else:
                result_uncertainty = np.gradient(tensor.uncertainty, axis=axis)
        else:
            result_uncertainty = None
        
        return SynapseTensor(result_data, result_uncertainty)
    
    @staticmethod
    def apply_function(tensor: SynapseTensor, func: callable, 
                      deriv_func: Optional[callable] = None) -> SynapseTensor:
        """Apply arbitrary function with optional uncertainty propagation"""
        result_data = func(tensor.data)
        
        # Propagate uncertainty if derivative is provided
        if tensor.uncertainty is not None and deriv_func is not None:
            # δf(x) = |f'(x)| * δx
            result_uncertainty = np.abs(deriv_func(tensor.data)) * tensor.uncertainty
        else:
            result_uncertainty = None
        
        return SynapseTensor(result_data, result_uncertainty)


# Convenience functions for common operations
def sin(tensor: SynapseTensor) -> SynapseTensor:
    """Sine with uncertainty propagation"""
    return TensorOperations.apply_function(tensor, np.sin, np.cos)

def cos(tensor: SynapseTensor) -> SynapseTensor:
    """Cosine with uncertainty propagation"""
    return TensorOperations.apply_function(tensor, np.cos, lambda x: -np.sin(x))

def exp(tensor: SynapseTensor) -> SynapseTensor:
    """Exponential with uncertainty propagation"""
    return TensorOperations.apply_function(tensor, np.exp, np.exp)

def log(tensor: SynapseTensor) -> SynapseTensor:
    """Natural logarithm with uncertainty propagation"""
    return TensorOperations.apply_function(tensor, np.log, lambda x: 1/x)

def sqrt(tensor: SynapseTensor) -> SynapseTensor:
    """Square root with uncertainty propagation"""
    return TensorOperations.apply_function(tensor, np.sqrt, lambda x: 0.5/np.sqrt(x))

def abs(tensor: SynapseTensor) -> SynapseTensor:
    """Absolute value"""
    return TensorOperations.apply_function(tensor, np.abs, lambda x: np.sign(x))