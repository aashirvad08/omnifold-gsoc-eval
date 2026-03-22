from __future__ import annotations

import numpy as np
import pandas as pd

from omnifold_publication import (
    ensure_valid_package,
    get_weights,
    load_events,
    load_metadata,
    write_package,
)
from omnifold_publication.writer import DEFAULT_EVENT_COUNT, DEFAULT_INPUT_PATH
from weighted_histogram import compute_weighted_histogram


def test_package_roundtrip_matches_direct_histogram(tmp_path):
    package_dir = write_package(output_dir=tmp_path / "demo_nominal")
    ensure_valid_package(package_dir)

    metadata = load_metadata(package_dir)
    packaged_df = load_events(package_dir)
    direct_df = pd.read_hdf(DEFAULT_INPUT_PATH, "df").iloc[:DEFAULT_EVENT_COUNT]

    observable = metadata["observables"][0]["name"]
    bins = np.linspace(0.0, 200.0, 26)

    packaged_result = compute_weighted_histogram(
        packaged_df[observable].to_numpy(),
        get_weights(packaged_df, metadata),
        bins=bins,
    )
    direct_result = compute_weighted_histogram(
        direct_df[observable].to_numpy(),
        direct_df[metadata["weights"]["nominal"]].to_numpy(),
        bins=bins,
    )

    np.testing.assert_allclose(packaged_result["hist"], direct_result["hist"])
    np.testing.assert_allclose(packaged_result["edges"], direct_result["edges"])
    np.testing.assert_allclose(
        packaged_result["uncertainty"],
        direct_result["uncertainty"],
    )
