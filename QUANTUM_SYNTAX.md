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
- [ ] Additional gates (swap, cz, toffoli)
- [ ] Parameter binding from algorithm to circuit
- [ ] Measurement result variable binding
- [ ] Noise model simulation
- [ ] Optimizer loop for VQE/QAOA

## Notes
- Rotation gates require one angle parameter.
- Non-numeric qubit indices are ignored with a warning.
- Active backend currently always uses in-process state vector simulator.

## Example Output
Executing a Bell circuit returns counts approximately: `{ "00": ~500, "11": ~500 }` for 1000 shots.

---
This file will evolve as quantum features mature.
