import matplotlib

matplotlib.use("Agg")

import numpy as np
import pytest

from weighted_histogram import compute_weighted_histogram, plot_weighted_histogram


def test_compute_weighted_histogram_matches_numpy():
    values = np.array([0.2, 0.7, 1.2, 1.9])
    weights = np.array([1.0, 2.0, 3.0, 4.0])
    bins = np.array([0.0, 1.0, 2.0])

    hist, edges, errors = compute_weighted_histogram(values, weights, bins=bins)

    expected_hist, expected_edges = np.histogram(values, bins=bins, weights=weights)
    expected_sumw2, _ = np.histogram(values, bins=bins, weights=weights**2)

    np.testing.assert_allclose(hist, expected_hist)
    np.testing.assert_allclose(edges, expected_edges)
    np.testing.assert_allclose(errors, np.sqrt(expected_sumw2))


def test_compute_weighted_histogram_density_integrates_to_one():
    values = np.array([0.1, 0.2, 0.8, 1.2, 1.8])
    weights = np.array([1.0, 2.0, 1.0, 1.0, 3.0])

    hist, edges, _ = compute_weighted_histogram(
        values,
        weights,
        bins=np.array([0.0, 1.0, 2.0]),
        density=True,
    )

    integral = np.sum(hist * np.diff(edges))
    assert np.isclose(integral, 1.0)


def test_compute_weighted_histogram_rejects_shape_mismatch():
    values = np.array([0.1, 0.2, 0.3])
    weights = np.array([1.0, 2.0])

    with pytest.raises(ValueError, match="same shape"):
        compute_weighted_histogram(values, weights, bins=2)


def test_compute_weighted_histogram_drops_nonfinite_entries():
    values = np.array([0.1, 0.3, np.nan, 0.7])
    weights = np.array([1.0, 2.0, 3.0, np.inf])

    hist, edges, errors = compute_weighted_histogram(
        values,
        weights,
        bins=np.array([0.0, 0.5, 1.0]),
    )

    np.testing.assert_allclose(hist, np.array([3.0, 0.0]))
    np.testing.assert_allclose(edges, np.array([0.0, 0.5, 1.0]))
    np.testing.assert_allclose(errors, np.array([np.sqrt(5.0), 0.0]))


def test_compute_weighted_histogram_raises_when_all_entries_filtered():
    values = np.array([np.nan, np.nan])
    weights = np.array([1.0, 2.0])

    with pytest.raises(ValueError, match="No finite entries"):
        compute_weighted_histogram(values, weights, bins=2)


def test_plot_weighted_histogram_returns_objects():
    values = np.array([0.2, 0.4, 0.6, 1.2])
    weights = np.array([1.0, 1.5, 0.5, 2.0])

    fig, ax, hist, edges, errors = plot_weighted_histogram(
        values,
        weights,
        bins=np.array([0.0, 1.0, 2.0]),
        density=False,
        label="nominal",
    )

    assert fig is ax.figure
    assert hist.shape == (2,)
    assert edges.shape == (3,)
    assert errors.shape == (2,)
    assert len(ax.patches) >= 1

    fig.clf()
