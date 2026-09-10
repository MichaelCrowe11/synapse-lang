"""Trusted local interoperability; no quantum advantage or calibration claims."""
import math

from .qubit_flow_interpreter import QubitFlowInterpreter


class SynapseQubitBridge:
    def __init__(self):
        from synapse_lang import Interpreter
        self.synapse_interpreter = Interpreter()
        self.qubit_interpreter = QubitFlowInterpreter()
        self.shared_variables = {}

    def execute_hybrid(self, synapse_code, qubit_code):
        synapse_result = self.synapse_interpreter.execute(synapse_code)
        from synapse_lang import UncertainValue
        for name, value in self.synapse_interpreter.variables.items():
            if isinstance(value, (int, float, UncertainValue)):
                self.qubit_interpreter.variables[name] = (
                    value.nominal if isinstance(value, UncertainValue) else value
                )
                self.shared_variables[name] = value
        quantum_result = self.qubit_interpreter.execute(qubit_code)
        if any(message.startswith("Error:") for message in quantum_result):
            raise ValueError("; ".join(quantum_result))
        for name in self.qubit_interpreter.qubits:
            p = self.qubit_interpreter.probability_one(name)
            # Bernoulli outcome spread, not uncertainty of an estimated mean.
            value = UncertainValue(p, math.sqrt(max(0, p * (1 - p))))
            self.shared_variables[f"quantum_{name}"] = value
            self.synapse_interpreter.variables[f"quantum_{name}"] = value
        return {"synapse_results": synapse_result, "qubit_results": quantum_result,
                "shared_context": dict(self.shared_variables)}

    def quantum_measurement_feedback(self, qubit_name, measurement_basis="Z"):
        if measurement_basis != "Z":
            raise NotImplementedError("Only computational-basis feedback is supported")
        from synapse_lang import UncertainValue
        p = self.qubit_interpreter.probability_one(qubit_name)
        result = self.qubit_interpreter.measure_qubit(qubit_name)
        value = UncertainValue(result, math.sqrt(max(0, p * (1 - p))))
        self.shared_variables[f"{qubit_name}_measurement"] = value
        self.synapse_interpreter.variables[f"{qubit_name}_measurement"] = value
        return value


def create_hybrid_interpreter():
    return SynapseQubitBridge()
