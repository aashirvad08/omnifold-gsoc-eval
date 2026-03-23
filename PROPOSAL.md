# GSoC 2026 — Project Proposal: OmniFold Publication Tools

**by Aashirvad**

---

## Why Me?

My work in Scikit-HEP Awkward Array has focused on solving core challenges in schema stability,
backend-agnostic data representation, and reproducible serialization across CPU/GPU environments.
I have implemented byte-order handling across NumPy, CuPy, and JAX, ensured schema-consistent
round-trip guarantees, and extended GPU interoperability with cuDF while enforcing explicit buffer
ownership. This experience with iteration-aware serialization directly informs how I would handle
OmniFold's per-iteration weight semantics and step metadata in the publication schema.

I approach this problem from a data systems perspective, with a strong focus on how scientific
outputs can be structured for long-term reuse and reinterpretation. My experience working with
Arrow-backed columnar models and zero-copy semantics is particularly relevant for designing
scalable storage formats for OmniFold weights that remain interoperable across scientific Python
ecosystems.

I also have research experience as a co-author at IEEE MoSICom 2025, with ongoing work under
review at the IEEE Open Journal of the Computer Society. Through this, I have developed an
understanding of how to structure, document, and communicate complex systems for a broader
scientific audience, which is directly relevant to defining publication standards for OmniFold
outputs.

I see this project not just as an implementation task, but as an opportunity to define a standard
for publishing ML-based scientific results, and my experience in data systems, scientific
serialization, and research-driven development positions me to contribute effectively to this goal.

---

## Abstract

OmniFold outputs have no publication standard. The per-event weights, iteration metadata, and
systematic variations produced by the algorithm are stored in ad-hoc formats that cannot be reused
without the original analysis environment. This project defines a framework combining structured
metadata (YAML/JSON), a Parquet-based storage format for per-event weights, and a lightweight
Python API for loading data, applying weights, and computing observables. The outcome is a
reproducible and interoperable standard for publishing ML-based unfolding results, enabling broader
reuse across the scientific community.

This proposal prioritizes a minimal, working standard first — a fully usable publication package
with nominal weights and one uncertainty family — with extensibility as a secondary goal.

**Project Duration:** 175 hours (Medium) · **Project Difficulty:** Intermediate

---

## Problem Statement

OmniFold produces event-level weights, not fixed histograms, making the publishable result a
combination of weights, observables, and metadata across iterations and uncertainties.

Current outputs (NumPy arrays, HDF5) lack:

- a canonical published weight
- clear iteration/step semantics
- structured uncertainty representation
- sufficient metadata for reuse

The core problem is to convert these into a self-describing, versioned package that can be reused
without the original analysis.

---

## Why This Matters

- Enables reuse without retraining
- Makes uncertainties and normalization explicit
- Preserves results beyond original environments
- Bridges OmniFold outputs with HEPData workflows

---

## Technical Objectives

- Define a versioned metadata schema
- Define a standard storage format for weights and systematics
- Build reader + writer APIs
- Implement validation tools (schema, normalization, closure)
- Support minimal (reuse) and full (reproducibility) packages
- Provide end-to-end example workflow

The existing OmniFold package (`omnifold/multifold.py`) produces weights but provides no writer
or serialization layer — this project adds that layer without modifying the core training pipeline.

---

## Proposed Architecture

**Package structure:**
```
manifest.yaml        → version, files, checksums
observables.yaml     → definitions, bins
samples/             → event data
weights/             → nominal, iterations, systematics
validation/          → checks + summaries
reproducibility/     → training + models (optional)
```

---

## Publication Tiers

**Minimal:**
- final truth-level weights
- observables
- metadata + uncertainties
- validation

**Full:**
- all minimal
- iteration + detector weights
- training + preprocessing
- optional model artifacts

---

## Metadata Schema Design

**Top-level blocks:**
`format_version`, `analysis`, `datasets`, `samples`, `observables`,
`weights`, `systematics`, `normalization`, `validation`, `provenance`

**Required fields:**
- canonical weight: `w_final = w_mc × w_omnifold_final`
- explicit weight formula and MC-weight handling
- event alignment contract (IDs or ordering)
- iteration index + step (detector/truth)
- uncertainty type + combination rule
- dataset provenance (generator, tune, simulation, selection)
- schema version + compatibility policy
- file hashes + software versions
  
**Example manifest:**
```yaml
format_version: "0.1"

analysis:
  name: "ATLAS Z+jets OmniFold example"
  process: "pp -> Z/gamma* + jets -> l+l- + jets"
  sqrt_s: "13 TeV"
  dataset: "Run 2 pseudodata"
  observable: "pT_ll"

storage:
  events_file: "events.parquet"
  event_count: 418014

weights:
  nominal:
    column: "weights_nominal"
    formula: "weight_mc * weights_nominal"
    iteration: 4
    step: "truth"
  generator_choice:
    column: "weights_generator_choice"
    reference: "Sherpa"

normalization:
  mode: "shape"
  base_weight_column: "weight_mc"
  nominal_sumw: 418014.0

provenance:
  generator: "Pythia8"
  tune: "CP5"
  software:
    omnifold_version: "0.3"
    python: "3.11"
```

**Rules:**
- final truth-level nominal weight = required publication object
- iteration weights = optional, but must include iteration + step metadata
- missing metadata must be explicitly `unknown` (never inferred)

---

## Storage Choice

| Format | Role |
|---|---|
| Parquet | Canonical |
| Arrow | In-memory |
| HDF5 | Legacy (optional) |

**Justification:**
- columnar → efficient observable + weight selection
- partitioned → scalable for large uncertainty families
- supports lazy loading + Python interoperability
- HDF5 is not used as the primary format due to limited support for partitioned, schema-driven
  datasets.
- HEPData expects binned histograms and covariance tables, not per-event weights; Parquet is
  therefore the appropriate format for the raw publication artifact, with HEPData integration
  handled through derived histogram outputs.

---

## Why Not Existing Approaches?

- **ROOT-based publication** — ROOT files are widely used but lack native schema versioning, and
  per-event weight storage in TTree format has no standard column contract for OmniFold outputs.
- **Extended HDF5** — HDF5 supports large arrays but has limited support for partitioned,
  schema-driven datasets and no standard metadata layer for weight semantics or provenance.
- **HEPData formats** — HEPData expects binned histograms and covariance tables, not per-event
  weights. It is appropriate for derived outputs but not for the raw publication artifact.

Parquet with a versioned YAML metadata sidecar addresses all three gaps: columnar access, schema
versioning, and interoperability with the scientific Python ecosystem.

---

## Systematics and Iterations

**Systematics types:**
- event-aligned weights
- statistical replicas
- model ensembles
- alternative samples (non-aligned)

**Systematics usage example:**
```python
import numpy as np
from omnifold_publication import load_package
from weighted_histogram import weighted_histogram

pkg = load_package("artifacts/zjets_nominal")
pkg.validate()

df = pkg.load_events(columns=["pT_ll"])
bins = np.linspace(0.0, 150.0, 31)

nominal = weighted_histogram(df["pT_ll"], pkg.get_weights("nominal"), bins=bins)
generator_choice = weighted_histogram(df["pT_ll"], pkg.get_weights("generator_choice"), bins=bins)

uncertainty_band = np.abs(generator_choice["hist"] - nominal["hist"])
```

**Rules:**
- aligned variations → one-to-one event mapping
- non-aligned samples → separate datasets (not weight columns)
- each family must define type, indexing, and combination rule

**Iterations:**
- final truth-level weight = required
- step-1/step-2 weights = optional but standardized

---

## HEPData Integration Strategy

- HEPData stores derived histograms + covariance tables
- OmniFold package stored as external DOI resource
- manifest defines how to reproduce published tables

---

## Implementation Plan

**Specification**
- define schema + weight semantics
- define systematics rules

**Format**
- implement writer + reader (Parquet)
- support nominal + one uncertainty family

**API**
- load package
- select weights
- compute observables + histograms

**Validation**
- schema compliance
- alignment + integrity checks
- normalization + closure
  
**Validation example:**
```python
from omnifold_publication import load_package

pkg = load_package("artifacts/zjets_nominal")
pkg.validate()  # raises with descriptive message if schema, alignment, or normalization fails

df = pkg.load_events(columns=["pT_ll"])
w = pkg.get_weights(variation="nominal")

print(f"Loaded {len(df)} events — weight sum: {w.sum():.2f}")
```

**Workflow**
- end-to-end example (export → reload → reproduce results)
- generate HEPData-compatible outputs

---

## Deliverables

**Required:**
- Versioned metadata schema (required + optional fields)
- Canonical publication package format (datasets, weights, validation, provenance)
- Python reader/writer API to:
  - write packages from OmniFold outputs
  - load metadata and weight families
  - apply weights to observables
- Validation tools (schema, integrity, alignment, completeness)
- One reference publication package
- Documentation + tutorial workflow

**Stretch:**
- HEPData export templates
- Support for multiple uncertainty families
- HDF5 → package conversion utilities
- Optional model/training artifact support

---

## Success Criteria

A user can:
- open a published package and inspect metadata
- list observables, datasets, and weight families
- load final truth-level nominal weights
- compute a reference unfolded histogram
- propagate at least one uncertainty family
- validate schema + data integrity
- reproduce a reference observable from the example

The core success criterion is a minimal, fully usable publication package with nominal weights
and one uncertainty family. Everything beyond that is extensibility.

---

## Timeline (175 hours)

**Community Bonding**
- finalize scope + publication boundaries
- collect representative OmniFold outputs

**Weeks 1–2**
- Produce the requirements summary and gap analysis
- Draft schema v1 for package metadata and weight semantics
- Define the canonical package layout and minimal/full package split
- *Artifact: schema draft and package-format document + tests for schema validation logic*

**Weeks 3–4**
- Implement the package writer for nominal outputs
- Implement the package reader for metadata and nominal weights
- Add schema validation and package inventory checks
- *Artifact: working nominal package reader/writer with schema validation + pytest coverage*

**Weeks 5–6**
- Add support for iteration metadata and one uncertainty family
- Implement dataset alignment, integrity, and normalization checks
- Compare Parquet-based access against the current HDF5-style workflow
- *Artifact: package support for iterations plus one uncertainty family + alignment tests*

**Weeks 7–8**
- Implement the user-facing API for loading weights and applying them to observables
- Add reference histogram and uncertainty-summary utilities
- Document weight semantics and uncertainty handling
- *Artifact: reusable analysis API with documented reference workflow + integration tests*

**Weeks 9–10**
- Build the end-to-end publication example
- Reproduce at least one reference observable from the published package
- Finalize tests, tutorial documentation, and package examples
- *Artifact: complete end-to-end example package and reproducible tutorial + full test suite*

**Final Phase**
- Incorporate mentor feedback, finalize documentation, and prepare final report
- HEPData integration pursued as stretch if time permits
- *Artifact: final package, documentation, and HEPData integration prototype*

---

## Risks and Mitigation

| Risk | Mitigation |
|---|---|
| Ambiguous definition of "published weight" | Define one canonical required weight; make others optional but typed |
| Systematics are heterogeneous across analyses | Use a taxonomy-based schema rather than hardcoding column prefixes |
| HEPData may not be a suitable raw backend | Integrate via derived products and external package references |
| Scope creep into full retraining reproducibility | Keep minimal package mandatory, full package optional |

---

## Prior Contributions

### Scikit-HEP / awkward-array

**Merged**
- [#3796](https://github.com/scikit-hep/awkward/pull/3796) — Fixed `ArrayBuilder.show()`
  incorrectly wrapping the `formatter` argument causing a `TypeError`. Added regression tests.
- [#3823](https://github.com/scikit-hep/awkward/pull/3823) — Updated `axis` parameter
  docstrings across 33 high-level operations to document named-axis support with links to the
  user guide. 
- [#3813](https://github.com/scikit-hep/awkward/pull/3813) — Documented GPU backend and cuDF
  compatibility limitations based on direct debugging experience.

**Open / Under Active Review**
- [#3845](https://github.com/scikit-hep/awkward/pull/3845) — Implementing backend-specific
  `byteswap` across NumPy, CuPy, and JAX nplikes with lazy virtual array handling and
  per-backend test coverage.
- [#3878](https://github.com/scikit-hep/awkward/pull/3878) — Adding `ak.str.uniques` and
  `ak.str.distinct_counts` backed by PyArrow, operating per nested string axis via
  `recursively_apply`.
- [#3801](https://github.com/scikit-hep/awkward/pull/3801) — Updating `ak.to_cudf` for
  cuDF ≥ 24.12 column API changes. Core fix complete; blocked on CI environment.

**Issue Contributions**
- [#3721](https://github.com/scikit-hep/awkward/issues/3721) — Diagnosed `ak.to_json` float64
  precision loss as a C++ `strtod` issue, not Python. Maintainers confirmed and escalated to a
  Ryū/Dragonbox fix.

### PODIO (AIDASoft) — Open

- [#941](https://github.com/AIDASoft/podio/pull/941) — Adding unit tests for JSON
  serialization, covering struct members, range matchers, and null reference handling. Under
  active review by tmadlener and andresailer.
- [#938](https://github.com/AIDASoft/podio/pull/938) — Draft prototype of a
  `TransportFrameData` backend to validate frame-level transport at the `FrameData` layer
  without modifying `Frame`. Round-trip confirmed with maintainer tmadlener.
- [#946](https://github.com/AIDASoft/podio/pull/946) — Diagnosed CI failure root cause:
  `MiscHelpers.h` leaking into ROOT dictionary generation via a `clang` macro. Proposed the
  header split fix; maintainer implemented it.

### OmniFold (hep-lbdl) — Open

- [#11](https://github.com/hep-lbdl/OmniFold/pull/11) — Fixed TensorFlow/Keras compatibility
  in `GaussianExample_minimal` and `omnifold.py` for modern TF versions. Tested locally with
  finite weights confirmed.
- [#12](https://github.com/hep-lbdl/OmniFold/pull/12) — Fixed README typo in the efficiency
  factors section.

---

## Evaluation Task Prototype

During the evaluation task I built `omnifold_publication`, a working prototype implementing the
write/read/validate pipeline on the provided pseudo-data. It writes Parquet-based publication
packages, validates schema compliance and event-count integrity, and passes 15 tests covering
roundtrip correctness and validation failures. A key finding was the undocumented asymmetry
across the three files — 175 weight columns in the nominal file versus 2 in the nonDY variation
— which directly motivated the systematic weight taxonomy proposed here.
```python
# Example of the proposed user-facing API
from omnifold_publication import load_package
from weighted_histogram import weighted_histogram

pkg = load_package("artifacts/demo_nominal/")
df = pkg.load_events(columns=["pT_ll"])
weights = pkg.get_weights(variation="nominal")

hist, edges = weighted_histogram(df["pT_ll"], weights, bins=50)
```

Code available at: https://github.com/X0708a/omnifold-gsoc-eval

---

## Progress Monitoring

I will maintain a structured work log and provide regular progress updates through GitHub issues,
pull requests, and mentor communication channels. I will schedule check-ins at least 2–3 times
per week to review progress, discuss blockers, and validate design decisions. Major milestones,
including the schema, package format, API, validation tools, and example workflow, will be tracked
through GitHub to ensure transparency and steady delivery. Key technical decisions and results
will be documented through concise design notes and periodic technical write-ups.

---

## Future Scope

This project establishes a foundation for standardized publication of OmniFold results and
supports continued development beyond the GSoC period. Follow-up work includes extending support
to additional uncertainty families, improving HEPData integration tooling, refining the schema
and API based on community feedback, and supporting adoption in realistic analysis workflows.

---

## Benefits to the Community

This project addresses a clear gap in modern HEP software by making ML-based unfolding results
publishable in a reusable and standardized form. Published OmniFold weights will become easier
to interpret, validate, preserve, and reuse for new observables without retraining. The proposed
format also provides a practical interface to existing publication infrastructure, including
HEPData, while establishing a common foundation that can be reused across analyses.

The gap analysis and metadata schema in this proposal are grounded in direct inspection of the
provided pseudo-data files, including the asymmetric weight structure across the three HDF5
files — 175 weight columns in the nominal file versus 2 in the nonDY variation — which informed
the systematic weight taxonomy proposed here.

---

## Conclusion

This project delivers a concrete publication standard for OmniFold results: a versioned package
format, an explicit metadata schema, and a reference Python API for loading, validating, and
reusing published weights. It transforms event-level unfolding outputs into self-describing
scientific artifacts that enable reinterpretation, long-term preservation, and reproducible
analysis beyond the original training environment.

By defining a practical integration path with HEPData through derived products and external
package references, it establishes a scalable and interoperable framework for publishing
ML-based unfolding results in high-energy physics.

---

I confirm that I will be fully available during the GSoC 2026 coding period (June–September 2026)
and will dedicate a minimum of 40 hours per week to this project.
