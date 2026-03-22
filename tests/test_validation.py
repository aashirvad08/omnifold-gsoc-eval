from __future__ import annotations

from pathlib import Path

import yaml

from omnifold_publication import validate_package, write_package


def test_validation_detects_event_count_mismatch(tmp_path):
    package_dir = write_package(output_dir=tmp_path / "demo_nominal")
    metadata_path = Path(package_dir) / "metadata.yaml"

    with metadata_path.open("r", encoding="utf-8") as stream:
        metadata = yaml.safe_load(stream)

    metadata["publication"]["event_count"] += 1
    with metadata_path.open("w", encoding="utf-8") as stream:
        yaml.safe_dump(metadata, stream, sort_keys=False)

    errors = validate_package(package_dir)
    assert any("event_count mismatch" in error for error in errors)


def test_validation_detects_missing_events_file(tmp_path):
    package_dir = write_package(output_dir=tmp_path / "demo_nominal")
    events_path = Path(package_dir) / "events.parquet"
    events_path.unlink()

    errors = validate_package(package_dir)
    assert any("Missing events file" in error for error in errors)
