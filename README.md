# OmniFold Publication Tools

Research-oriented utilities and documentation for preparing OmniFold weight outputs for publication and downstream reuse.

## Purpose

This repository provides:

- a structured gap analysis of available OmniFold HDF5 files,
- a machine-readable metadata schema (`metadata.yaml`),
- schema design rationale (`schema_design.md`),
- robust weighted-histogram utilities with uncertainty handling,
- tests covering numerical and data-quality edge cases.

The goal is to make event-level OmniFold outputs easier to validate, compare, and reuse by analysts who did not run the original training pipeline.

## Repository Structure

- `gap_analysis.md`: analysis of file-level differences and missing reproducibility metadata.
- `metadata.yaml`: scientific metadata description for dataset provenance and weight families.
- `schema_design.md`: schema design motivation, choices, and expected user workflow.
- `weighted_histogram.py`: weighted histogram computation and plotting helpers.
- `explore_h5.py`: helper script to inspect HDF5 structure and sample content.
- `tests/`: pytest suite for histogram logic and edge-case handling.
- `data/`: local OmniFold HDF5 files (ignored from git tracking).

## Setup

```bash
python3 -m pip install -r requirements.txt
```

The pinned minimum version constraints in `requirements.txt` improve
reproducibility across reviewer environments.

## Run Code

Example weighted histogram workflow:

```bash
python3 example_plot.py
```

This reads `data/multifold.h5`, computes a weighted `pT_ll` histogram using `weights_nominal`, and saves `example_histogram.png`.

## Example Usage

```bash
python example_plot.py
```

## Run Tests

```bash
pytest
```

The tests include core correctness checks and robustness checks for realistic physics-data issues (NaNs, shape mismatches, empty arrays).
