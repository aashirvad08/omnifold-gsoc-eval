"""Read a minimal OmniFold publication package."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import yaml


def _resolve_metadata_path(path: str | Path) -> Path:
    path = Path(path)
    return path / "metadata.yaml" if path.is_dir() else path


def load_metadata(path: str | Path) -> dict[str, Any]:
    """Load package metadata from a package directory or metadata file path."""

    metadata_path = _resolve_metadata_path(path)
    with metadata_path.open("r", encoding="utf-8") as stream:
        metadata = yaml.safe_load(stream) or {}
    if not isinstance(metadata, dict):
        raise ValueError("Package metadata must be a mapping.")
    return metadata


def load_events(path: str | Path, columns: list[str] | None = None) -> pd.DataFrame:
    """Load the Parquet event table from a package directory or file path."""

    path = Path(path)
    if path.is_dir():
        metadata = load_metadata(path)
        events_file = metadata["publication"]["events_file"]
        events_path = path / events_file
    else:
        events_path = path
    return pd.read_parquet(events_path, columns=columns)


def get_weights(
    df: pd.DataFrame,
    metadata: dict[str, Any],
    variation: str = "nominal",
):
    """Return the requested weight array from the loaded event table."""

    weights = metadata.get("weights", {})
    if variation == "nominal":
        column = weights["nominal"]
    elif variation == "replica":
        column = weights.get("replica")
        if column is None:
            raise KeyError("Replica weight column is not defined in metadata.")
    elif variation in df.columns:
        column = variation
    else:
        raise KeyError(f"Unknown weight variation: {variation}")

    if column not in df.columns:
        raise KeyError(f"Weight column {column!r} is not present in the event table.")
    return df[column].to_numpy()
