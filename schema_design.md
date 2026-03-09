# Schema Design for OmniFold Publication Metadata

## Purpose

The metadata schema is designed to make OmniFold weight files publication-ready by documenting:

- which files are available,
- which observables are present,
- which weight families exist per file,
- and what uncertainty workflows are reproducible from each file.

This avoids hidden assumptions when analysts use reduced files (`multifold_sherpa.h5`, `multifold_nonDY.h5`) that do not carry the full weight content of `multifold.h5`.

## Core Schema Blocks

- `files`: per-file event counts and weight-family availability.
- `observables`: canonical observable names expected in OmniFold outputs.
- `weights.required_core`: baseline weights needed for central-value histograms.
- `weights.uncertainty_families`: replica-based weight families used for uncertainty propagation.
- `weights.detector_theory_families`: detector, theory, and normalization weights used for systematic variations.

### Explicit Systematic Weight Families

The schema explicitly lists weight families such as:

- `weights_ensemble_*`
- `weights_bootstrap_mc_*`
- `weights_bootstrap_data_*`

These map directly to uncertainty estimation procedures commonly used in OmniFold analyses:

- **ensemble weights** capture variation across reweighting models/replicas,
- **MC bootstrap weights** capture MC statistical uncertainty,
- **data bootstrap weights** capture data statistical uncertainty.

Making these families explicit in metadata allows downstream users to:

- detect whether a given file supports full uncertainty propagation,
- automate replica loops without hard-coded column guesses,
- reproduce uncertainty bands in a transparent and auditable way.

## How Users Interact with `metadata.yaml`

A typical workflow is:

1. Read `metadata.yaml` and pick an input file under `files`.
2. Validate `event_count`, required observables, and `weights.required_core`.
3. Use `weights.uncertainty_families` to discover replica columns (wildcard/prefix based).
4. Use `weights.detector_theory_families` for detector/theory normalization studies.
5. If replica families are missing, restrict the analysis scope or switch to `multifold.h5`.

In short, metadata drives both data loading and uncertainty capability checks before physics plotting.
