# Roadmap examples (not parsed by the current grammar)

`backbone.qnet`, `qkd_demo.qnet` and `teleport_demo.qnet` describe where the
Quantum Net language is headed: typed nodes with memory parameters, protocol
blocks with per-node code, entanglement with repeaters, applications with trial
runs and reports. None of that is in the current lexer or parser, and none of it
executes. `synapse-qnet` rejects these files with a syntax error, and
`tests/test_examples_and_roadmap.py` asserts that it does; the day one of them
parses, that test fails so the file can be promoted deliberately.

Runnable today (grammar validation only, reported as `parse-only`): the files in
the parent `examples/` directory. Protocol execution, including BB84, E91,
teleportation, entanglement swapping and purification, is not implemented in
this package; the `qnet_runtime.protocols` modules say so explicitly.
