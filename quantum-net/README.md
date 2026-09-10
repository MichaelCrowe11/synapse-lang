## Current executable scope

`synapse-qnet examples/validated-flat.qnet` validates the flat network grammar.
The CLI reports `parse-only`; it does not execute a networking protocol.
The older backbone, teleportation and QKD examples are roadmap material, not
installed-wheel acceptance examples. See `../docs/trinity-implementation-blueprint.md`.

1# Quantum-Net (QNet)

A third language that complements **Synapse-Lang** (scientific reasoning/hypotheses) and **Qubit-Flow** (circuit construction/execution) by providing *network-level* abstractions for quantum links, routing, repeaters, and distributed algorithms. Essential for building next-generation quantum software spanning the *quantum internet*.

This repository contains the language specification, simulator, and examples for QNet.

## Getting Started

1.  **Install dependencies:**
    ```bash
    pip install -e .
    ```

2.  **Run an example:**
    ```bash
    qnet run examples/teleport_demo.qnet
    ```

3.  **Run tests:**
    ```bash
    pytest
    ```
