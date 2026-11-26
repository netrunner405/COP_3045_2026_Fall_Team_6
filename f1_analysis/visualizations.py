"""Build Matplotlib figures from Formula 1 results and summaries."""

from textwrap import fill

import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure


def plot_points_ranking(totals: pd.Series, label: str, years: str) -> Figure:
    """Plot up to ten drivers or constructors by cumulative race points."""
    top = totals.nlargest(10).sort_values()
    figure = Figure(figsize=(10, 6))
    axes = figure.subplots()
    bars = axes.barh(top.index, top.values, color="#2563eb")
    axes.bar_label(bars, fmt="%.1f", padding=4)
    if top.max() > 0 and top.min() >= 0:
        axes.set_xlim(0, top.max() * 1.18)
    axes.set_xlabel("Total race points")
    axes.set_title(f"Top 10 {label} by Total Race Points ({years})", loc="left")
    return figure


def plot_starting_vs_finishing(finishers: pd.DataFrame, years: str) -> Figure:
    """Plot the density of positions for the selected finisher entries."""
    figure = Figure(figsize=(9, 6))
    axes = figure.subplots()
    axes.set_xlabel("Starting grid position (1 = pole)")
    axes.set_ylabel("Finishing position (1 = winner)")
    axes.set_title(f"Starting vs. Finishing Position ({years})", loc="left")
    if finishers.empty:
        _show_no_data(axes, "No entries meet the finisher criteria.")
        return figure

    counts = axes.hexbin(
        finishers["grid"], finishers["position"], gridsize=20, mincnt=1, cmap="Blues"
    )
    maximum = max(finishers["grid"].max(), finishers["position"].max())
    axes.plot(
        [1, maximum], [1, maximum], "--", color="#ef4444", linewidth=1.5,
        label="Same starting and finishing position",
    )
    figure.colorbar(counts, ax=axes, label="Race entries per bin")
    axes.legend(fontsize=8)
    return figure


def plot_points_by_starting_group(summary: pd.DataFrame, years: str) -> Figure:
    """Plot average race points and sample size for each available grid group."""
    figure = Figure(figsize=(9, 6))
    axes = figure.subplots()
    axes.set_xlabel("Starting grid position group")
    axes.set_ylabel("Average race points per entry")
    axes.set_title(f"Average Points by Starting Position ({years})", loc="left")
    groups = summary.dropna(subset=["average_points"])
    if groups.empty:
        _show_no_data(axes, "No race points are available for the selected finishers.")
        return figure

    bars = axes.bar(groups.index.astype(str), groups["average_points"], color="#2563eb")
    axes.bar_label(
        bars,
        labels=[
            f"{row.average_points:.2f}\n(n={int(row.race_entries):,})"
            for row in groups.itertuples()
        ],
        padding=5,
    )
    if groups["average_points"].max() > 0 and groups["average_points"].min() >= 0:
        axes.set_ylim(0, groups["average_points"].max() * 1.25)
    return figure


def add_chart_caption(figure: Figure, caption: str) -> None:
    """Reserve caption space and prepare a chart for PNG and PDF export."""
    figure.tight_layout(rect=(0, 0.28, 1, 1))
    figure.text(
        0.07, 0.04, fill(caption, width=110), fontsize=9, color="#555555",
        va="bottom", linespacing=1.5,
    )


def _show_no_data(axes: Axes, message: str) -> None:
    axes.set_xticks([])
    axes.set_yticks([])
    axes.text(0.5, 0.5, message, transform=axes.transAxes, ha="center", va="center")
