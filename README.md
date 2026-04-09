# Turbine Blade Design Optimization

A framework for optimizing gas turbine blade material properties and cooling conditions to minimize maximum von Mises stress, subject to a displacement feasibility constraint and operational uncertainties.

## Overview

Gas turbine blades operate under extreme thermal and mechanical loads. This project uses a finite-element model (FEM) simulator to find optimal material and cooling parameters that minimize blade stress while satisfying displacement constraints.

**Key results:**
- **41% reduction** in maximum von Mises stress
- GP surrogate models with 10-fold CV R² > 0.994
- 100% displacement feasibility under operational uncertainty with a 45% safety margin

## Input Variables

| Variable | Description | Range | Type |
|:---------|:-----------|:------|:-----|
| x₁ | Young's Modulus | [2×10¹¹, 3×10¹¹] Pa | Material |
| x₂ | Poisson's Ratio | [0.1, 0.49] | Material |
| x₃ | CTE (Coefficient of Thermal Expansion) | [5×10⁻⁶, 1.5×10⁻⁵] K⁻¹ | Material |
| x₄ | Thermal Conductivity | [5, 15] W/m/K | Material |
| x₅ | Cooling Air Temperature | [50, 350] °C | Operational (±2°C) |
| x₆ | Pressure Load | [10⁵, 4.8×10⁵] Pa | Operational (±10⁴ Pa) |

## Methodology

The 300-run evaluation budget is allocated as:

1. **100 runs** — Latin Hypercube Design (initial space-filling)
2. **150 runs** — Sequential Expected Improvement with Constraints (Bayesian optimization)
3. **27 runs** — Robust grid validation (3×3×3 perturbation grid)
4. **23 runs** — Final validation runs

## Project Structure

```
├── Blade.stl              # Turbine blade 3D geometry
├── simulator.p            # FEM simulator (pickled)
├── inputs/                # Parameter configurations (LHD + sequential)
├── scripts/               # MATLAB scripts for simulation
│   ├── gen_inputs.m       # Generate Latin Hypercube input designs
│   ├── batch_run.m        # Run simulations via SLURM array jobs
│   ├── collect_results.m  # Aggregate results from individual runs
│   └── single_test.m      # Run a single test simulation
├── slurm/                 # SLURM job submission scripts
├── results/               # Per-run simulation output CSVs
├── data/                  # Aggregated dataset (all_results.csv)
├── analysis/              # Python analysis & figure generation
│   └── run_analysis.py    # GP fitting, optimization, and plotting
├── figures/               # Generated figures for the report
├── sim_outputs/           # Simulation output plots per run
├── log/                   # SLURM job logs
├── report.qmd             # Quarto report source
└── report.pdf             # Final report
```

## Usage

### Running Simulations (HPC with SLURM)

```bash
# Generate input parameter designs
sbatch slurm/gen_inputs.sh

# Run batch simulations
sbatch --array=1-N slurm/batch_run.sh

# Collect results into a single CSV
sbatch slurm/collect_results.sh
```

### Running Analysis

```bash
python3 analysis/run_analysis.py
```

This fits Gaussian Process surrogates, performs Bayesian optimization, and generates all figures.

## Presentation

[Slides (Google Slides)](https://docs.google.com/presentation/d/1UdqcVesdaxPZP7XjMTsK-71AJsDyVhCkq49wHoZOTS4/edit#slide=id.g38b44dc6cea_2_75)

## Authors

Yuan Lei, Yuan Shan, Daisy Xu
