#!/usr/bin/env python3
"""
Inspect selected HDF5 files and compare their structure.

Requirements:
- h5py
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import h5py


FILES = [
    Path("data/multifold.h5"),
    Path("data/multifold_sherpa.h5"),
    Path("data/multifold_nonDY.h5"),
]


def preview_dataset(ds: h5py.Dataset, nrows: int = 5) -> Any:
    """Return the first nrows from a dataset in a shape-safe way."""
    if ds.shape == ():
        return ds[()]
    if len(ds.shape) == 0:
        return ds[()]
    return ds[: min(nrows, ds.shape[0])]


def print_group_details(group: h5py.Group, indent: int = 0) -> None:
    """Recursively print datasets/groups with metadata and sample rows."""
    pad = " " * indent
    for key in group.keys():
        obj = group[key]
        obj_path = obj.name
        if isinstance(obj, h5py.Dataset):
            print(f"{pad}- Dataset: {obj_path}")
            print(f"{pad}  shape: {obj.shape}")
            print(f"{pad}  dtype: {obj.dtype}")
            try:
                sample = preview_dataset(obj, nrows=5)
                print(f"{pad}  first 5 rows:\n{sample}")
            except Exception as exc:  # pragma: no cover - defensive
                print(f"{pad}  first 5 rows: <error reading dataset: {exc}>")
        elif isinstance(obj, h5py.Group):
            print(f"{pad}- Group: {obj_path}")
            print_group_details(obj, indent=indent + 2)
        else:  # pragma: no cover - uncommon in typical h5py usage
            print(f"{pad}- Other object: {obj_path} ({type(obj).__name__})")


def collect_structure(group: h5py.Group, structure: dict[str, tuple[str, Any, Any]]) -> None:
    """Collect recursive structural signature for comparison."""
    for key in group.keys():
        obj = group[key]
        if isinstance(obj, h5py.Dataset):
            structure[obj.name] = ("dataset", obj.shape, str(obj.dtype))
        elif isinstance(obj, h5py.Group):
            structure[obj.name] = ("group", None, None)
            collect_structure(obj, structure)
        else:
            structure[obj.name] = (type(obj).__name__, None, None)


def compare_structures(paths: list[Path]) -> None:
    """Compare all files to the first file as the baseline."""
    signatures: dict[Path, dict[str, tuple[str, Any, Any]]] = {}

    for path in paths:
        with h5py.File(path, "r") as f:
            sig: dict[str, tuple[str, Any, Any]] = {}
            collect_structure(f, sig)
            signatures[path] = sig

    baseline_path = paths[0]
    baseline = signatures[baseline_path]

    print("\n=== Structure Comparison ===")
    all_identical = True

    for path in paths[1:]:
        current = signatures[path]
        if current == baseline:
            print(f"[MATCH] {path} has identical structure to {baseline_path}")
            continue

        all_identical = False
        print(f"[DIFF ] {path} differs from {baseline_path}")

        baseline_keys = set(baseline.keys())
        current_keys = set(current.keys())

        only_in_baseline = sorted(baseline_keys - current_keys)
        only_in_current = sorted(current_keys - baseline_keys)
        shared = baseline_keys & current_keys
        metadata_diff = sorted(k for k in shared if baseline[k] != current[k])

        if only_in_baseline:
            print(f"  - Present only in {baseline_path}:")
            for k in only_in_baseline:
                print(f"    {k} -> {baseline[k]}")
        if only_in_current:
            print(f"  - Present only in {path}:")
            for k in only_in_current:
                print(f"    {k} -> {current[k]}")
        if metadata_diff:
            print("  - Shared paths with different metadata:")
            for k in metadata_diff:
                print(f"    {k}")
                print(f"      {baseline_path}: {baseline[k]}")
                print(f"      {path}: {current[k]}")

    if all_identical:
        print("All three files have identical structure.")
    else:
        print("The three files do not all share identical structure.")


def main() -> None:
    for path in FILES:
        print(f"\n=== Inspecting: {path} ===")
        if not path.exists():
            print(f"File not found: {path}")
            continue

        with h5py.File(path, "r") as f:
            top_keys = list(f.keys())
            print(f"Top-level keys: {top_keys}")
            print_group_details(f)

    existing = [p for p in FILES if p.exists()]
    if len(existing) >= 2:
        compare_structures(existing)
    else:
        print("\nNot enough existing files to run structure comparison.")


if __name__ == "__main__":
    main()
