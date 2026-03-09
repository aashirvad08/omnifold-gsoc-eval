"""Weighted histogram helpers for OmniFold event-level analysis."""

from __future__ import annotations

from typing import Sequence

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from numpy.typing import ArrayLike


def compute_weighted_histogram(
    values: ArrayLike,
    weights: ArrayLike | None = None,
    bins: int | Sequence[float] = 50,
    hist_range: tuple[float, float] | None = None,
    density: bool = False,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute a weighted histogram and per-bin statistical uncertainty.

    Parameters
    ----------
    values:
        Observable values for each event.
    weights:
        Event weights. If ``None``, unit weights are used.
    bins:
        Number of bins or explicit bin edges, passed to ``numpy.histogram``.
    hist_range:
        Optional ``(min, max)`` range used when ``bins`` is an integer.
    density:
        If ``True``, return a normalized density histogram.

    Returns
    -------
    hist, bin_edges, errors:
        Weighted bin contents, bin edges, and per-bin uncertainty
        ``sqrt(sum w^2)`` (also density-normalized if ``density=True``).

    Notes
    -----
    Non-finite values/weights are dropped before histogramming.
    """

    values_arr = np.asarray(values, dtype=float).ravel()

    if weights is None:
        weights_arr = np.ones_like(values_arr, dtype=float)
    else:
        weights_arr = np.asarray(weights, dtype=float).ravel()
        if values_arr.shape != weights_arr.shape:
            raise ValueError("`values` and `weights` must have the same shape.")

    finite_mask = np.isfinite(values_arr) & np.isfinite(weights_arr)
    values_arr = values_arr[finite_mask]
    weights_arr = weights_arr[finite_mask]

    if values_arr.size == 0:
        raise ValueError("No finite entries remain after filtering values/weights.")

    hist, bin_edges = np.histogram(
        values_arr,
        bins=bins,
        range=hist_range,
        weights=weights_arr,
        density=False,
    )
    sumw2, _ = np.histogram(
        values_arr,
        bins=bins,
        range=hist_range,
        weights=weights_arr * weights_arr,
        density=False,
    )
    errors = np.sqrt(sumw2)

    if density:
        total_weight = float(np.sum(hist))
        if total_weight <= 0.0:
            raise ValueError(
                "Cannot build a density histogram with non-positive total weight."
            )
        widths = np.diff(bin_edges)
        hist = hist / (total_weight * widths)
        errors = errors / (total_weight * widths)

    return hist.astype(float), bin_edges.astype(float), errors.astype(float)


def plot_weighted_histogram(
    values: ArrayLike,
    weights: ArrayLike | None = None,
    bins: int | Sequence[float] = 50,
    hist_range: tuple[float, float] | None = None,
    density: bool = False,
    ax: Axes | None = None,
    label: str | None = None,
    color: str = "C0",
    show_errors: bool = True,
    xlabel: str = "Observable",
) -> tuple[Figure, Axes, np.ndarray, np.ndarray, np.ndarray]:
    """Compute and plot a weighted histogram with optional error bars.

    Returns the matplotlib figure/axes and the histogram arrays so calling
    code can reuse the computed values in tests or downstream analysis.
    """

    hist, bin_edges, errors = compute_weighted_histogram(
        values=values,
        weights=weights,
        bins=bins,
        hist_range=hist_range,
        density=density,
    )

    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.figure

    ax.stairs(hist, bin_edges, color=color, label=label, linewidth=1.8)

    if show_errors:
        centers = 0.5 * (bin_edges[1:] + bin_edges[:-1])
        ax.errorbar(
            centers,
            hist,
            yerr=errors,
            fmt="none",
            ecolor=color,
            elinewidth=1.0,
            capsize=2.0,
        )

    ax.set_xlabel(xlabel)
    ax.set_ylabel("Density" if density else "Weighted events")
    if label:
        ax.legend(frameon=False)

    return fig, ax, hist, bin_edges, errors
