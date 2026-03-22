# OmniFold Publication Tools

Research-oriented utilities and documentation for preparing OmniFold weight
outputs for publication and downstream reuse.

## Purpose

This repository provides:
- a structured gap analysis of available OmniFold HDF5 files,
- a machine-readable metadata schema (`metadata.yaml`),
- schema design rationale (`schema_design.md`),
- robust weighted-histogram utilities with uncertainty handling,
- tests covering numerical and data-quality edge cases,
- a minimal working prototype of a publication package API.

The goal is to make event-level OmniFold outputs easier to validate, compare,
and reuse by analysts who did not run the original training pipeline.

---

## Repository Structure

| File / Directory | Description |
|---|---|
| `gap_analysis.md` | Analysis of file-level differences and missing reproducibility metadata |
| `metadata.yaml` | Scientific metadata for dataset provenance and weight families |
| `schema_design.md` | Schema design motivation, choices, and expected user workflow |
| `weighted_histogram.py` | Weighted histogram computation and plotting helpers |
| `explore_h5.py` | Helper script to inspect HDF5 structure and sample content |
| `example_plot.py` | End-to-end example: load data, compute histogram, save plot |
| `example_histogram.png` | Output of `example_plot.py` on the provided pseudo-data |
| `omnifold_publication/` | Prototype publication package API (writer, reader, validator) |
| `examples/` | Roundtrip example: write package → reload → verify histogram equivalence |
| `tests/` | pytest suite for histogram logic, roundtrip correctness, and validation |
| `data/` | Local OmniFold HDF5 files (ignored from git tracking) |

---

## Setup
```bash
python3 -m pip install -r requirements.txt
```

The pinned minimum version constraints in `requirements.txt` improve
reproducibility across reviewer environments.

---

## Run Code

**Weighted histogram example:**
```bash
python3 example_plot.py
```

Reads `data/multifold.h5`, computes a weighted `pT_ll` histogram using
`weights_nominal`, and saves `example_histogram.png`.

**Publication package roundtrip:**
```bash
python3 examples/package_roundtrip.py
```

Reads `data/multifold.h5`, writes a minimal publication package to
`artifacts/demo_nominal/` (Parquet + metadata), reloads it, and verifies
that the reloaded histogram matches the original to numerical precision.

---

## Prototype: `omnifold_publication`

The `omnifold_publication` package is a minimal proof-of-concept for the
publication API proposed in the GSoC project.

**Modules:**

| Module | Description |
|---|---|
| `writer.py` | Reads OmniFold HDF5 output and writes a publication package (Parquet + metadata YAML) |
| `reader.py` | Loads metadata and event data from a publication package; selects weight families by name |
| `validation.py` | Checks schema compliance, required columns, event count consistency, and file integrity |

**Package layout written by `writer.py`:**
```
artifacts/demo_nominal/
    events.parquet       # observables + weights (columnar, partitioned)
    package_metadata.yaml  # provenance, weight families, normalization
```

**Key design decisions:**
- Parquet is used as the primary storage format: columnar layout enables
  efficient per-observable and per-weight-family access without loading the
  full event record.
- The writer selects a canonical nominal weight (`weights_nominal`) and one
  replica column (`weights_ensemble_0`) to demonstrate the minimal/full
  package split described in the proposal.
- Validation is decoupled from reading, so packages can be checked
  independently of the analysis workflow.

This prototype covers the nominal package tier. The full GSoC implementation
would extend it to all systematic weight families, configurable event
selection, iteration metadata, and HEPData-compatible derived outputs.

---

## Run Tests
```bash
pytest
```

The test suite includes:
- core histogram correctness and uncertainty propagation,
- robustness checks for realistic physics-data issues (NaNs, negative weights,
  shape mismatches, empty arrays),
- roundtrip correctness (write package → reload → compare histograms),
- validation failure cases (missing files, missing columns, wrong event counts).
