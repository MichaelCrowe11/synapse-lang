# Synapse Programming Language

<p align="left">
    <a href="https://pypi.org/project/synapse-lang/">
        <img alt="PyPI" src="https://img.shields.io/pypi/v/synapse-lang.svg?color=7A5CFF&label=PyPI&logo=pypi&logoColor=white" />
    </a>
    <a href="LICENSE">
        <img alt="License" src="https://img.shields.io/github/license/MichaelCrowe11/synapse-lang?color=43E5FF" />
    </a>
    <a href="https://pypistats.org/packages/synapse-lang">
        <img alt="Downloads" src="https://img.shields.io/pypi/dm/synapse-lang?color=2ECC71" />
    </a>
    <a href="#branding--assets"><img alt="Brand" src="https://img.shields.io/badge/brand-kit-0.1-dark?color=0B0F14" /></a>
</p>

**Created by Michael Benjamin Crowe**

A proprietary programming language designed for deep scientific reasoning and enhanced parallel thought processing pipelines.

> Dark / light adaptive inline logo example:
>
> ```html
> <picture>
>   <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/MichaelCrowe11/synapse-lang/master/branding/dark-inline.svg">
>   <img alt="Synapse-Lang" width="140" src="https://raw.githubusercontent.com/MichaelCrowe11/synapse-lang/master/branding/light-inline.svg" />
> </picture>
> ```

## Overview

Synapse is a domain-specific language that combines:
- **Parallel execution streams** for simultaneous hypothesis testing
- **Uncertainty quantification** built into the type system
- **Scientific reasoning chains** with formal logic constructs
- **Native tensor operations** for high-dimensional data
- **Hypothesis-driven programming** paradigm

## Key Features

### 1. Uncertainty-Aware Computing
```synapse
uncertain measurement = 42.3 ± 0.5
uncertain temperature = 300 ± 10
// Uncertainty propagates automatically through calculations
```

### 2. Parallel Thought Streams
```synapse
parallel {
    branch A: test_hypothesis_1()
    branch B: test_hypothesis_2()
    branch C: control_experiment()
}
```

### 3. Reasoning Chains
```synapse
reason chain ScientificMethod {
    premise P1: "Observable phenomenon exists"
    derive D1 from P1: "Hypothesis can be formed"
    conclude: D1 => "Experiment validates or refutes"
}
```

## Project Structure

```
synapse-lang/
├── LANGUAGE_SPEC.md          # Complete language specification
├── synapse_interpreter.py     # Core interpreter implementation
├── test_synapse.py           # Test suite
├── examples/
│   ├── quantum_simulation.syn    # Quantum mechanics example
│   ├── climate_model.syn        # Climate modeling example
│   └── drug_discovery.syn       # Drug discovery pipeline
└── README.md                 # This file
```

## Running Tests

```bash
cd synapse-lang
python test_synapse.py
```

## Example Programs

### Quantum Simulation
Demonstrates parallel evolution of quantum states with uncertainty:
```synapse
experiment DoubleSlitSimulation {
    parallel {
        branch slit_A: evolve_wavefunction(path="A")
        branch slit_B: evolve_wavefunction(path="B")
    }
    synthesize: compute_interference(slit_A, slit_B)
}
```

### Climate Modeling
Complex system analysis with ensemble runs:
```synapse
parallel {
    branch RCP2.6: model_pathway(emissions="low")
    branch RCP4.5: model_pathway(emissions="moderate")
    branch RCP8.5: model_pathway(emissions="high")
}
```

### Drug Discovery
Molecular simulation pipeline with parallel screening:
```synapse
pipeline DrugDiscovery {
    stage VirtualScreening parallel(64) {
        fork {
            path ligand_docking: autodock_vina
            path ml_prediction: graph_neural_network
        }
    }
}
```

## Implementation Status

✅ **Completed:**
- Basic lexer/tokenizer
- Token types for scientific operators
- Uncertain value arithmetic with error propagation
- Parallel execution framework
- Variable storage and retrieval
- Example scientific programs

🚧 **In Progress:**
- Full parser implementation
- Advanced reasoning chains
- Tensor operations
- Symbolic mathematics
- Pipeline execution

## Design Philosophy

Synapse is designed to express scientific thinking naturally:
1. **Hypothesis-first**: Start with assumptions, derive conclusions
2. **Parallel exploration**: Test multiple theories simultaneously  
3. **Uncertainty-native**: Propagate measurement errors automatically
4. **Reasoning chains**: Build formal logical arguments
5. **Pipeline-oriented**: Structure complex workflows

## Branding & Assets

The project now includes an initial logo/identity kit (v1) under `branding/LOGO_KIT.html` featuring:

- Synapse‑Lang horizontal + stacked lockups
- Icon-only badge (simplified path & nodes)
- Favicon simplification (no ± token for clarity at 16–32px)
- Seed marks for Qubit‑Flow and QNet (shared gradient family; QNet uses emerald accent)
- Palette & typography reference (Inter + JetBrains Mono)

### Quick Usage (Markdown badge / inline HTML)

```html
<!-- Inline SVG icon example -->
<svg width="20" height="20" viewBox="0 0 256 256" aria-hidden="true">
    <defs>
        <linearGradient id="synG" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#43E5FF"/>
            <stop offset="100%" stop-color="#7A5CFF"/>
        </linearGradient>
    </defs>
    <path d="M64 56 C128 56, 128 120, 192 120 C224 120, 224 160, 192 176 C160 192, 112 184, 88 208" fill="none" stroke="url(#synG)" stroke-width="18" stroke-linecap="round"/>
    <circle cx="64" cy="56" r="16" fill="#0B0F14"/>
    <circle cx="192" cy="120" r="16" fill="#0B0F14"/>
    <circle cx="88" cy="208" r="16" fill="#0B0F14"/>
</svg>
<span style="font:600 14px 'JetBrains Mono', monospace; vertical-align:middle;">Synapse‑Lang</span>
```

Guidelines: keep gradient stroke, avoid arbitrary recoloring of node fills except to invert for dark backgrounds; maintain minimum horizontal lockup width of 160px or switch to icon.

### Asset Inventory

- `branding/light-inline.svg` – Inline horizontal lockup (light / default)
- `branding/dark-inline.svg` – Inline horizontal lockup tuned for dark backgrounds
- `branding/LOGO_KIT.html` – Interactive reference + download kit
- `scripts/optimize_svgs.py` – Batch optimizer (uses `svgo` if available, else trims whitespace)

### Optimizing SVG Assets

Optional deep optimization via `svgo` (Node.js). Fallback lightweight trim always works.

Install (optional):
```
npm install -g svgo
```

Run optimization (auto-modifies files):
```
python -m synapse_lang.scripts.optimize_svgs
```

CI / check mode (fails if further optimization possible):
```
python -m synapse_lang.scripts.optimize_svgs --check
```

Output lists per-file bytes saved plus total.
