# Synapse Language

An interpreted language for uncertainty-aware scientific computing, with
built-in quantum circuit simulation and parallel blocks.

[![PyPI](https://img.shields.io/pypi/v/synapse-lang.svg?label=PyPI)](https://pypi.org/project/synapse-lang/)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-Proprietary-red.svg)

Synapse is a small language focused on a few ideas that are awkward in
general-purpose languages: values that carry uncertainty and propagate it
through arithmetic, simple parallel branches, and quantum circuits that run on
a built-in simulator.

This is an early-stage language. The sections below describe what runs today.
Larger aspirational programs (imports, control flow, functions, tensors,
reasoning chains, a full quantum DSL) are kept under `examples/roadmap/` as
design targets and do not execute yet.

## Install

```bash
pip install synapse-lang
```

Requires Python 3.10+. Core dependencies: numpy, scipy, sympy, matplotlib,
networkx, pandas, colorama.

## First run

```bash
synapse --version
```

```
Synapse 2.4.2
```

```bash
printf 'x = 3 ± 0.2\nprint(x * 2)\n' > first.syn
synapse first.syn
```

```
6.0 ± 0.4
```

Both outputs were captured on 2026-09-10 from a fresh virtual environment with
the package installed from PyPI. Before 2.4.2 the first program printed `6.0`
and silently dropped the uncertainty unless the line began with `uncertain`.

## Runtime safety

Execution is trusted and in-process, not an operating-system security sandbox.
Do not run untrusted source or context callables without external isolation.
`execute(..., sandbox=True)`, `execute_program(..., sandbox=True)`, and
`--sandbox` fail explicitly rather than silently executing without isolation.
The default is now `sandbox=False`; `--no-sandbox` remains a compatibility flag.
The older security helper classes now refuse execution. An opt-in
[external Docker runner](docs/isolation.md) is available, with tested resource
and OS restrictions; it is separate from the ordinary interpreter API.

See [runtime optimization and verification](docs/runtime-optimization.md) for
AST reuse, parallel semantics, benchmark commands, and verification limits.

## Usage

```bash
synapse path/to/program.syn      # run a file
synapse -c 'print(1 + 2)'        # run a snippet
synapse --repl                   # interactive REPL
synapse --version
```

## What works today

### Printing, variables, and built-in math

```synapse
print("Hello from Synapse!")
x = 21
y = 21
print("x + y =", x + y)
print("sqrt(144) =", sqrt(144))
print("pi =", pi)
```

```
Hello from Synapse!
x + y = 42.0
sqrt(144) = 12.0
pi = 3.141592653589793
```

Built-ins include `print`, `str`, `int`, `float`, `bool`, `len`, `range`,
`abs`, `round`, `min`, `max`, `sum`, `sqrt`, `exp`, `log`, `log10`, `sin`,
`cos`, `tan`, `floor`, `ceil`, `mean`, `std`, and the constants `pi` and `e`.

### Uncertainty propagation

A value declared `uncertain` carries an uncertainty that propagates
automatically through arithmetic.

```synapse
uncertain measurement = 42.3 ± 0.5
uncertain temperature = 300 ± 10
energy = measurement * temperature
print("energy =", energy)
```

```
energy = 12690.0 ± 448.808422380864
```

### Parallel branches

```synapse
parallel {
    branch dataset_1: {
        print("Processing dataset 1...")
        result_1 = 100
    }
    branch dataset_2: {
        print("Processing dataset 2...")
        result_2 = 200
    }
}
print("Combined result:", result_1 + result_2)
```

```
Processing dataset 1...
Processing dataset 2...
Combined result: 300.0
```

### Quantum circuits on the built-in simulator

```synapse
quantum circuit bell(2) {
    h(0)
    cnot(0,1)
}
run bell { shots: 256 }
```

```
{'circuit': 'bell', 'backend': None, 'shots': 256, 'counts': {'11': 124, '00': 132}, 'noise': None}
```

A Bell state is entangled, so measurements only ever come out `00` or `11`.

## Examples

Runnable examples live in [`examples/`](examples/): `hello.syn`,
`uncertainty.syn`, `parallel.syn`, `quantum_bell.syn`. Each is covered by the
test suite. Aspirational examples are under
[`examples/roadmap/`](examples/roadmap/).

## License

Proprietary software. All rights reserved. Use, copying, modification, or
distribution requires a separate written license from the copyright holder; see
[LICENSE](LICENSE). Earlier copies distributed under MIT retain their granted
rights, and third-party components retain their own licenses.

## Citation

```bibtex
@software{synapse_lang,
    title = {Synapse: an interpreted language for uncertainty-aware scientific computing},
    author = {Michael Benjamin Crowe},
    year = {2026},
    version = {2.4.1}
}
```
