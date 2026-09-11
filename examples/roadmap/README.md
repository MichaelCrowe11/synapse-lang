# Roadmap examples (not yet runnable)

These programs were written to illustrate where Synapse is headed. They use
syntax and constructs the current interpreter does **not** yet execute
(`import`, `for`/`if` statements, function definitions, f-strings, tensors,
reasoning chains, full quantum DSL, bra-ket notation, GPU annotations, and
more). They are kept here as design targets, not as working samples.

For examples that run today, see the parent `examples/` directory:

- `hello.syn` - printing, variables, arithmetic, built-in math
- `uncertainty.syn` - uncertain values and uncertainty propagation
- `parallel.syn` - parallel branches
- `quantum_bell.syn` - a quantum circuit on the built-in simulator

Two Qubit Flow programs also live here: `quantum_teleportation.qflow` and
`vqe_circuit.qflow`. They use a `circuit { ... }` block form and `rotation q: Ry(...)`
syntax that the current Qubit Flow parser rejects (`Unexpected character ':'`).
The form that runs today is one statement per line: `qubit a`, `H[a]`,
`CNOT[a,b]`, `measure a -> m`. See `qubit-flow-package/README.md`.
