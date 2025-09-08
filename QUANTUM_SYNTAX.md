# Synapse Quantum Programming Syntax

This document describes the emerging native quantum programming constructs in Synapse.

## Quantum Circuit
```
quantum circuit bell(2) {
    h(0)
    cnot(0,1)
    measure(0,1)
}
```
- `quantum circuit <name>(<qubits>)` defines a circuit.
- Gates: `h, x, y, z, cnot/cx, rx(angle), ry(angle), rz(angle)`.
- `measure(q0, q1, ...)` records qubit states. If omitted, all qubits auto-measured.

## Quantum Backend
```
quantum backend simulator {
    shots: 1024
    noise_model: ideal
}
```
Defines execution configuration. Most recent backend becomes active.

## Quantum Algorithm Skeleton
```
quantum algorithm vqe {
    parameters: [theta1, theta2]
    ansatz: hardware_efficient
    cost_function: energy_expectation(H)
    optimize: gradient_descent(theta1, theta2)
}
```
Currently stored structurally for future execution / optimization phases.

## Mixed Classical + Quantum
```
shots = 512
quantum backend simulator { shots: shots }
quantum circuit ghz(3) {
    h(0)
    cnot(0,1)
    cnot(1,2)
    measure(0,1,2)
}
```

## Roadmap (Implemented vs Planned)
- [x] Circuit definition + basic gates
- [x] Measurement + auto-measure fallback
- [x] Backend config (shots)
- [x] Algorithm skeleton parsing
- [x] VS Code snippets
- [x] Additional gates (swap, cz, toffoli, iswap, cswap)
- [x] Semantic validation layer (error codes)
- [ ] Parameter binding from algorithm to circuit
- [ ] Measurement result variable binding
- [ ] Noise model simulation (currently only structural + depolarizing schema)
- [ ] Optimizer loop for VQE/QAOA

## Notes
- Rotation gates require one angle parameter.
- Non-numeric qubit indices are ignored with a warning.
- Active backend currently always uses in-process state vector simulator.

## Semantic Error Codes
| Code   | Description |
|--------|-------------|
| E1001  | Unknown gate name |
| E1002  | Qubit index out of circuit range |
| E1003  | Duplicate qubit provided to gate requiring distinct qubits |
| E1004  | Gate arity mismatch (wrong number of qubits) |
| E1005  | Gate parameter count mismatch |
| E1010  | Measurement index out of range |
| E1011  | Duplicate measurement of same qubit |
| E1101  | Non-integer qubit or measurement index |
| E1200  | Malformed noise model object/type |
| E1201  | Unknown or incomplete noise model specification |
| E1202  | Noise model probability parameter outside [0,1] |
| E1301  | Invalid backend shots value (must be positive int) |
| E1302  | Invalid total circuit qubit count |

These pre-execution semantic checks run before simulation to surface issues early.

## Example Output
Executing a Bell circuit returns counts approximately: `{ "00": ~500, "11": ~500 }` for 1000 shots.

---
This file will evolve as quantum features mature.
