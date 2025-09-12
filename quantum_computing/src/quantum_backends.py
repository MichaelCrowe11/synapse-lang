"""
Quantum Backends for Synapse Language

Provides interfaces to various quantum computing backends including
local simulation, IBM Quantum, Google Cirq, and AWS Braket.
"""

import numpy as np
from typing import Dict, List, Optional, Any, Union
from abc import ABC, abstractmethod
import json
from dataclasses import dataclass
from enum import Enum

class BackendType(Enum):
    """Enumeration of backend types."""
    SIMULATOR = "simulator"
    HARDWARE = "hardware"
    CLOUD = "cloud"

@dataclass 
class QuantumJob:
    """Represents a quantum job execution."""
    job_id: str
    circuit_name: str
    backend_name: str
    status: str
    shots: int
    created_at: str
    results: Optional[Dict] = None
    error_message: Optional[str] = None

class QuantumBackend(ABC):
    """Abstract base class for quantum backends."""
    
    def __init__(self, name: str, backend_type: BackendType):
        self.name = name
        self.backend_type = backend_type
        self.is_connected = False
        self.capabilities = {}
    
    @abstractmethod
    def connect(self, credentials: Dict = None) -> bool:
        """Connect to the backend."""
        pass
    
    @abstractmethod
    def submit_circuit(self, circuit, shots: int = 1024) -> QuantumJob:
        """Submit quantum circuit for execution."""
        pass
    
    @abstractmethod
    def get_job_status(self, job_id: str) -> str:
        """Get job execution status."""
        pass
    
    @abstractmethod
    def get_job_results(self, job_id: str) -> Dict:
        """Get job execution results."""
        pass
    
    @abstractmethod
    def get_backend_info(self) -> Dict:
        """Get backend information and capabilities."""
        pass

class LocalSimulator(QuantumBackend):
    """
    Local quantum circuit simulator using numpy.
    Suitable for small to medium circuits (up to ~20 qubits).
    """
    
    def __init__(self, name: str = "local_simulator"):
        super().__init__(name, BackendType.SIMULATOR)
        self.max_qubits = 25  # Practical limit for dense simulation
        self.max_shots = 1000000
        self.job_counter = 0
        self.jobs = {}
    
    def connect(self, credentials: Dict = None) -> bool:
        """Connect to local simulator (always available)."""
        self.is_connected = True
        self.capabilities = {
            'max_qubits': self.max_qubits,
            'max_shots': self.max_shots,
            'supports_midcircuit_measurement': True,
            'supports_reset': True,
            'supports_conditionals': True,
            'gate_set': ['H', 'X', 'Y', 'Z', 'CNOT', 'RX', 'RY', 'RZ', 'SWAP', 'TOFFOLI']
        }
        return True
    
    def submit_circuit(self, circuit, shots: int = 1024) -> QuantumJob:
        """Submit circuit to local simulator."""
        if not self.is_connected:
            raise RuntimeError("Backend not connected")
        
        if circuit.num_qubits > self.max_qubits:
            raise ValueError(f"Circuit has {circuit.num_qubits} qubits, max supported: {self.max_qubits}")
        
        # Generate job ID
        self.job_counter += 1
        job_id = f"local_sim_{self.job_counter:06d}"
        
        # Create job
        job = QuantumJob(
            job_id=job_id,
            circuit_name=getattr(circuit, 'name', 'unnamed_circuit'),
            backend_name=self.name,
            status='queued',
            shots=shots,
            created_at=self._current_timestamp()
        )
        
        # Execute immediately (local simulation)
        try:
            job.status = 'running'
            results = self._simulate_circuit(circuit, shots)
            job.results = results
            job.status = 'completed'
        except Exception as e:
            job.status = 'failed'
            job.error_message = str(e)
        
        self.jobs[job_id] = job
        return job
    
    def get_job_status(self, job_id: str) -> str:
        """Get job status."""
        if job_id not in self.jobs:
            return 'not_found'
        return self.jobs[job_id].status
    
    def get_job_results(self, job_id: str) -> Dict:
        """Get job results."""
        if job_id not in self.jobs:
            raise ValueError(f"Job {job_id} not found")
        
        job = self.jobs[job_id]
        if job.status != 'completed':
            raise ValueError(f"Job {job_id} not completed (status: {job.status})")
        
        return job.results
    
    def get_backend_info(self) -> Dict:
        """Get backend information."""
        return {
            'name': self.name,
            'type': self.backend_type.value,
            'version': '1.0.0',
            'capabilities': self.capabilities,
            'is_connected': self.is_connected
        }
    
    def _simulate_circuit(self, circuit, shots: int) -> Dict:
        """Simulate quantum circuit execution."""
        # Get final statevector
        statevector = circuit.get_statevector()
        if statevector is None:
            raise RuntimeError("Circuit simulation failed")
        
        # Get measurement probabilities
        probabilities = np.abs(statevector) ** 2
        
        # Simulate shot-based measurements
        num_states = len(probabilities)
        state_indices = np.arange(num_states)
        
        # Sample according to quantum probabilities
        measured_states = np.random.choice(
            state_indices, 
            size=shots,
            p=probabilities
        )
        
        # Count measurement outcomes
        counts = {}
        for state_idx in measured_states:
            # Convert state index to binary string
            binary_str = format(state_idx, f'0{circuit.num_qubits}b')
            counts[binary_str] = counts.get(binary_str, 0) + 1
        
        # Calculate success probability (for algorithms)
        success_states = [state for state, count in counts.items() if count > 0]
        
        return {
            'counts': counts,
            'shots': shots,
            'statevector': statevector.tolist(),
            'probabilities': probabilities.tolist(),
            'success_probability': max(probabilities),
            'measurement_fidelity': 1.0,  # Perfect for simulation
            'execution_time': 0.001  # Simulated execution time
        }
    
    def _current_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat()

class IBMBackend(QuantumBackend):
    """
    Interface to IBM Quantum hardware and cloud simulators.
    Requires qiskit and IBM Quantum account.
    """
    
    def __init__(self, device_name: str = "ibmq_qasm_simulator"):
        super().__init__(f"ibm_{device_name}", BackendType.HARDWARE)
        self.device_name = device_name
        self.provider = None
        self.backend = None
        self.api_token = None
    
    def connect(self, credentials: Dict = None) -> bool:
        """Connect to IBM Quantum."""
        try:
            # Import qiskit (optional dependency)
            from qiskit import IBMQ
            from qiskit.providers.ibmq import AccountCredentialsError
            
            if credentials and 'api_token' in credentials:
                self.api_token = credentials['api_token']
                IBMQ.save_account(self.api_token, overwrite=True)
            
            # Load account
            IBMQ.load_account()
            self.provider = IBMQ.get_provider()
            self.backend = self.provider.get_backend(self.device_name)
            
            # Get backend capabilities
            config = self.backend.configuration()
            self.capabilities = {
                'max_qubits': config.n_qubits,
                'max_shots': config.max_shots,
                'gate_set': list(config.basis_gates),
                'coupling_map': config.coupling_map,
                'gate_errors': getattr(config, 'gate_errors', {}),
                'readout_errors': getattr(config, 'readout_errors', {})
            }
            
            self.is_connected = True
            return True
            
        except ImportError:
            raise RuntimeError("IBM Quantum backend requires qiskit: pip install qiskit")
        except AccountCredentialsError:
            raise RuntimeError("Invalid IBM Quantum credentials")
        except Exception as e:
            raise RuntimeError(f"Failed to connect to IBM Quantum: {str(e)}")
    
    def submit_circuit(self, circuit, shots: int = 1024) -> QuantumJob:
        """Submit circuit to IBM Quantum."""
        if not self.is_connected:
            raise RuntimeError("Backend not connected")
        
        try:
            # Convert Synapse circuit to Qiskit circuit
            qiskit_circuit = self._convert_to_qiskit(circuit)
            
            # Submit job
            job = self.backend.run(qiskit_circuit, shots=shots)
            
            # Create Synapse job object
            synapse_job = QuantumJob(
                job_id=job.job_id(),
                circuit_name=getattr(circuit, 'name', 'unnamed_circuit'),
                backend_name=self.name,
                status='queued',
                shots=shots,
                created_at=self._current_timestamp()
            )
            
            return synapse_job
            
        except Exception as e:
            raise RuntimeError(f"Failed to submit circuit: {str(e)}")
    
    def get_job_status(self, job_id: str) -> str:
        """Get IBM Quantum job status."""
        if not self.is_connected:
            raise RuntimeError("Backend not connected")
        
        try:
            job = self.backend.retrieve_job(job_id)
            qiskit_status = job.status().name
            
            # Map Qiskit status to Synapse status
            status_mapping = {
                'INITIALIZING': 'queued',
                'QUEUED': 'queued',
                'VALIDATING': 'queued',
                'RUNNING': 'running',
                'CANCELLED': 'cancelled',
                'DONE': 'completed',
                'ERROR': 'failed'
            }
            
            return status_mapping.get(qiskit_status, 'unknown')
            
        except Exception as e:
            return 'error'
    
    def get_job_results(self, job_id: str) -> Dict:
        """Get IBM Quantum job results."""
        if not self.is_connected:
            raise RuntimeError("Backend not connected")
        
        try:
            job = self.backend.retrieve_job(job_id)
            result = job.result()
            
            # Extract measurement counts
            counts = result.get_counts()
            shots = sum(counts.values())
            
            # Calculate probabilities
            probabilities = {state: count/shots for state, count in counts.items()}
            
            return {
                'counts': counts,
                'shots': shots,
                'probabilities': probabilities,
                'success_probability': max(probabilities.values()),
                'execution_time': getattr(result, 'time_taken', 0),
                'backend_name': self.device_name
            }
            
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve results: {str(e)}")
    
    def get_backend_info(self) -> Dict:
        """Get IBM backend information."""
        if not self.is_connected:
            return {'error': 'Not connected'}
        
        status = self.backend.status()
        config = self.backend.configuration()
        
        return {
            'name': self.name,
            'type': self.backend_type.value,
            'device_name': self.device_name,
            'operational': status.operational,
            'pending_jobs': status.pending_jobs,
            'capabilities': self.capabilities,
            'description': config.description
        }
    
    def _convert_to_qiskit(self, circuit):
        """Convert Synapse circuit to Qiskit circuit."""
        try:
            from qiskit import QuantumCircuit as QiskitCircuit, ClassicalRegister as QiskitClassical
            
            # Create Qiskit circuit
            qc = QiskitCircuit(circuit.num_qubits, circuit.num_clbits)
            
            # Add gates
            for gate in circuit.gates:
                if gate.gate_type.value == 'H':
                    qc.h(gate.target_qubits[0])
                elif gate.gate_type.value == 'X':
                    qc.x(gate.target_qubits[0])
                elif gate.gate_type.value == 'Y':
                    qc.y(gate.target_qubits[0])
                elif gate.gate_type.value == 'Z':
                    qc.z(gate.target_qubits[0])
                elif gate.gate_type.value == 'CNOT':
                    qc.cx(gate.control_qubits[0], gate.target_qubits[0])
                elif gate.gate_type.value == 'RX':
                    qc.rx(gate.parameters[0], gate.target_qubits[0])
                elif gate.gate_type.value == 'RY':
                    qc.ry(gate.parameters[0], gate.target_qubits[0])
                elif gate.gate_type.value == 'RZ':
                    qc.rz(gate.parameters[0], gate.target_qubits[0])
                # Add more gate conversions as needed
            
            # Add measurements
            for qubit, clbit in circuit.measurements:
                qc.measure(qubit, clbit)
            
            return qc
            
        except ImportError:
            raise RuntimeError("Qiskit conversion requires qiskit installation")
    
    def _current_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat()

class GoogleBackend(QuantumBackend):
    """
    Interface to Google Quantum AI hardware via Cirq.
    Requires cirq and Google Cloud credentials.
    """
    
    def __init__(self, device_name: str = "simulator"):
        super().__init__(f"google_{device_name}", BackendType.HARDWARE)
        self.device_name = device_name
        self.processor = None
        self.project_id = None
    
    def connect(self, credentials: Dict = None) -> bool:
        """Connect to Google Quantum AI."""
        try:
            # Import cirq (optional dependency)
            import cirq
            import cirq_google
            
            if credentials:
                self.project_id = credentials.get('project_id')
            
            if self.device_name == "simulator":
                self.processor = cirq.Simulator()
                self.backend_type = BackendType.SIMULATOR
            else:
                if not self.project_id:
                    raise ValueError("project_id required for Google hardware")
                
                # Connect to Google Quantum hardware
                self.processor = cirq_google.get_engine(self.project_id).get_processor(self.device_name)
            
            self.capabilities = {
                'max_qubits': 70 if 'sycamore' in self.device_name.lower() else 12,
                'gate_set': ['X', 'Y', 'Z', 'CNOT', 'RX', 'RY', 'RZ', 'SQRT_X', 'SQRT_Y'],
                'native_gates': ['sqrt_x', 'sqrt_y', 'z', 'cz'],
                'supports_parametric': True
            }
            
            self.is_connected = True
            return True
            
        except ImportError:
            raise RuntimeError("Google backend requires cirq: pip install cirq cirq-google")
        except Exception as e:
            raise RuntimeError(f"Failed to connect to Google Quantum: {str(e)}")
    
    def submit_circuit(self, circuit, shots: int = 1024) -> QuantumJob:
        """Submit circuit to Google Quantum."""
        if not self.is_connected:
            raise RuntimeError("Backend not connected")
        
        # Placeholder implementation
        # Would convert Synapse circuit to Cirq and execute
        job_id = f"google_{self.device_name}_{shots}"
        
        return QuantumJob(
            job_id=job_id,
            circuit_name=getattr(circuit, 'name', 'unnamed_circuit'),
            backend_name=self.name,
            status='queued',
            shots=shots,
            created_at=self._current_timestamp()
        )
    
    def get_job_status(self, job_id: str) -> str:
        """Get Google job status."""
        return 'not_implemented'
    
    def get_job_results(self, job_id: str) -> Dict:
        """Get Google job results."""
        return {'error': 'Google backend not fully implemented'}
    
    def get_backend_info(self) -> Dict:
        """Get Google backend information."""
        return {
            'name': self.name,
            'type': self.backend_type.value,
            'device_name': self.device_name,
            'capabilities': self.capabilities,
            'status': 'experimental'
        }
    
    def _current_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat()

# Backend factory function
def get_backend(backend_name: str, **kwargs) -> QuantumBackend:
    """
    Factory function to create quantum backends.
    
    Args:
        backend_name: Name of backend ('local', 'ibm', 'google')
        **kwargs: Backend-specific configuration
        
    Returns:
        QuantumBackend instance
    """
    backend_name = backend_name.lower()
    
    if backend_name == 'local' or backend_name == 'simulator':
        return LocalSimulator(**kwargs)
    elif backend_name.startswith('ibm'):
        device = kwargs.get('device', 'ibmq_qasm_simulator')
        return IBMBackend(device)
    elif backend_name.startswith('google'):
        device = kwargs.get('device', 'simulator')
        return GoogleBackend(device)
    else:
        available = ['local', 'ibm', 'google']
        raise ValueError(f"Unknown backend '{backend_name}'. Available: {available}")

# Export backend classes
__all__ = [
    'QuantumBackend',
    'LocalSimulator',
    'IBMBackend', 
    'GoogleBackend',
    'QuantumJob',
    'BackendType',
    'get_backend'
]