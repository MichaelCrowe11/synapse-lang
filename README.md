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
Synapse 2.4.1
```

```bash
printf 'x = 3 ± 0.2\nprint(x * 2)\n' > first.syn
synapse first.syn
```

```
6.0
```

Both outputs were captured on 2026-09-10 from a fresh virtual environment with
the package installed from PyPI. Release 2.4.1 drops the uncertainty on a bare
`x = 3 ± 0.2` literal; the fix is on the `master` branch and ships in the next
release. Until then, install from the repository:

```bash
pip install git+https://github.com/MichaelCrowe11/synapse-lang.git
synapse --version
synapse first.syn
```

```
Synapse 2.4.2
6.0 ± 0.4
```

Captured on 2026-09-10 from a fresh virtual environment installed from the
repository at the commit this README ships with.

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
`cos`, `tan`, `floor`, `ceil`, `mean`, `std`, `nominal`, `sigma`, `covariance`,
`correlation`, and the constants `pi` and `e`. The math builtins keep the
uncertainty when given an uncertain value.

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

Uncertain values remember their sources. A variable used twice in one formula
is one variable, so `t - t` is exactly zero and a formula such as
`t * b / (t + c)` carries the exact first-order derivative instead of counting
the two `t` as independent. `covariance` and `correlation` read how two
results move together through the sources they share.

```synapse
t = 21.0 ± 0.46
b = 17.27
c = 237.3
exponent = t * b / (t + c)
print("exponent =", exponent)
print("t - t =", t - t)
print("sqrt(t) =", sqrt(t))
a = 2 ± 0.1
s = a + t
d = a - t
print("covariance(s, d) =", covariance(s, d))
print("correlation(s, a) =", correlation(s, a))
```

```
exponent = 1.4040650406504065 ± 0.028255246152926107
t - t = 0.0 ± 0.0
sqrt(t) = 4.58257569495584 ± 0.05019011475427825
covariance(s, d) = -0.2016
correlation(s, a) = 0.2124296443310437
```

The exponent's uncertainty is `b * c / (t + c)^2 * 0.46`, the exact first-order
value. Treating the two `t` as independent would report about nine percent more.
The telemetry validation harness (`scripts/validate_uncertainty_telemetry.py`)
gates this form against an independent analytic reference at one part in 1e9.

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
