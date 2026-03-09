# OmniFold HDF5 Gap Analysis

## Central Finding: Strong Asymmetry in Weight Information

The dominant gap across the three files is not in observables but in **available weight information**.

| File | Events | Approx. weight columns | Weight coverage summary |
|---|---:|---:|---|
| `multifold.h5` | 418,014 | ~175 | Full OmniFold-style weight content (`weights_nominal`, `weights_ensemble_*`, `weights_bootstrap_mc_*`, `weights_bootstrap_data_*`, plus many detector/theory/background/lumi weights). |
| `multifold_sherpa.h5` | 326,430 | ~27 | Reduced set (`weight_mc`, `weights_nominal`, `weights_bootstrap_mc_*`), missing ensemble replicas and data bootstraps. |
| `multifold_nonDY.h5` | 433,397 | 2 | Only `weight_mc` and `weights_nominal`. |

This asymmetry is the key publication risk: the files are **not equivalent for uncertainty workflows**.

## Why This Matters for Uncertainty Estimation

OmniFold uncertainty studies typically require repeated weight realizations (ensemble and/or bootstrap replicas) to propagate model and statistical uncertainty through derived observables.

- With `multifold.h5`, users can run replica-based uncertainty propagation directly.
- With `multifold_sherpa.h5`, users can only do limited uncertainty studies (MC bootstrap only).
- With `multifold_nonDY.h5`, users cannot run replica-based uncertainty estimation from this file alone.

In practice, a user relying only on Sherpa or nonDY inputs cannot reproduce the same uncertainty treatment available with `multifold.h5`.

## Observable Coverage Is Consistent

All files share the same core event-level observables (24 columns), including:
`pT_ll`, lepton kinematics (`pT_l1`, `pT_l2`, `eta_*`, `phi_*`), track-jet features (`pT_trackj*`, `y_trackj*`, `phi_trackj*`, `m_trackj*`, `tau*`), and track multiplicities (`Ntracks_trackj1`, `Ntracks_trackj2`).

So the primary compatibility issue is **weight completeness**, not feature schema.

## Note on `target_dd`

The column `target_dd` appears in `multifold.h5` but is absent from the reduced files.

Most likely interpretation: it is a **data-driven target label/value used during OmniFold training or calibration** (paired with `weights_dd`).

Current limitation: the semantic meaning and intended downstream use of `target_dd` are not documented in-file. For publication-grade reproducibility, this should be explicitly defined in metadata (e.g., domain meaning, valid range, and whether it is training-only or analysis-usable).

## Practical Recommendation

Treat `multifold.h5` as the reference file for full uncertainty propagation.
Use `multifold_sherpa.h5` and `multifold_nonDY.h5` as specialized inputs unless accompanying metadata or auxiliary files provide missing replica/systematic weights.
