"""Validation helpers for a minimal OmniFold publication package."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .reader import load_metadata


REQUIRED_METADATA_KEYS = ("observables", "weights", "publication")
REQUIRED_PUBLICATION_KEYS = ("format", "events_file", "event_count", "columns")
REQUIRED_WEIGHT_KEYS = ("nominal", "base_mc_weight")


def validate_package(path: str | Path) -> list[str]:
    """Return a list of validation errors for the package at ``path``."""

    package_dir = Path(path)
    metadata_path = package_dir / "metadata.yaml"
    events_path = package_dir / "events.parquet"
    errors: list[str] = []

    if not package_dir.exists():
        return [f"Package directory does not exist: {package_dir}"]
    if not metadata_path.exists():
        errors.append(f"Missing metadata file: {metadata_path}")
    if not events_path.exists():
        errors.append(f"Missing events file: {events_path}")
    if errors:
        return errors

    metadata = load_metadata(metadata_path)
    for key in REQUIRED_METADATA_KEYS:
        if key not in metadata:
            errors.append(f"Missing metadata key: {key}")

    publication = metadata.get("publication", {})
    weights = metadata.get("weights", {})

    for key in REQUIRED_PUBLICATION_KEYS:
        if key not in publication:
            errors.append(f"Missing publication key: {key}")
    for key in REQUIRED_WEIGHT_KEYS:
        if key not in weights:
            errors.append(f"Missing weights key: {key}")

    if errors:
        return errors

    if publication["format"] != "parquet":
        errors.append("publication.format must be 'parquet'.")

    df = pd.read_parquet(events_path)
    required_columns = set(publication["columns"])
    for observable in metadata["observables"]:
        if isinstance(observable, dict) and "name" in observable:
            required_columns.add(observable["name"])
    required_columns.add(weights["nominal"])
    required_columns.add(weights["base_mc_weight"])
    replica_column = weights.get("replica")
    if replica_column:
        required_columns.add(replica_column)

    missing_columns = sorted(required_columns - set(df.columns))
    if missing_columns:
        errors.append(
            "Missing required columns in events.parquet: "
            + ", ".join(missing_columns)
        )

    actual_event_count = int(len(df))
    if actual_event_count != int(publication["event_count"]):
        errors.append(
            "event_count mismatch: "
            f"metadata={publication['event_count']} actual={actual_event_count}"
        )

    return errors


def ensure_valid_package(path: str | Path) -> None:
    """Raise ``ValueError`` if the package is invalid."""

    errors = validate_package(path)
    if errors:
        raise ValueError("\n".join(errors))
