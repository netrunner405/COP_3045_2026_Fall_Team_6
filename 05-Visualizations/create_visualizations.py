"""Create report charts from the team's cleaned F1 race results."""

from pathlib import Path
import textwrap

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = Path(__file__).resolve().parent / "outputs"


def text_page(report, title, paragraphs):
    fig = plt.figure(figsize=(11.7, 8.3))
    fig.text(0.07, 0.91, title, fontsize=21, weight="bold", color="#173b73")
    y = 0.82
    for paragraph in paragraphs:
        lines = textwrap.wrap(paragraph, width=105)
        fig.text(0.07, y, "\n".join(lines), fontsize=11, va="top", linespacing=1.6)
        y -= 0.032 * len(lines) + 0.035
    report.savefig(fig)
    plt.close(fig)


def table_page(report, title, frame, note):
    fig, ax = plt.subplots(figsize=(11.7, 8.3))
    ax.axis("off")
    fig.text(0.07, 0.91, title, fontsize=21, weight="bold", color="#173b73")
    table = ax.table(cellText=frame.astype(str).values, colLabels=frame.columns,
                     cellLoc="center", bbox=[0, 0.16, 1, 0.68])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("#ffffff")
        cell.set_facecolor("#173b73" if row == 0 else "#eaf0f8" if row % 2 else "#f7f9fc")
        if row == 0:
            cell.set_text_props(color="white", weight="bold")
    fig.text(0.07, 0.08, "\n".join(textwrap.wrap(note, 105)), fontsize=10)
    report.savefig(fig)
    plt.close(fig)


def main():
    data_file = ROOT / "03-Data_Cleaning" / "clean_data.csv"
    if not data_file.exists():
        raise FileNotFoundError("Run python3 03-Data_Cleaning/clean_data.py first.")
    df = pd.read_csv(data_file, low_memory=False)
    required = {"season", "round", "driverId", "driverName", "constructorId",
                "constructorName", "points", "grid", "position", "laps", "status"}
    if df.empty or required.difference(df.columns):
        raise ValueError(f"Input must contain race results and columns: {sorted(required)}")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    years = f"{int(df.season.min())}–{int(df.season.max())}"
    plt.rcParams.update({"font.size": 11, "axes.spines.top": False,
                         "axes.spines.right": False, "figure.dpi": 150})

    with PdfPages(OUTPUT / "f1_visualizations.pdf") as report:
        report.infodict()["Title"] = "F1 Race Performance Analysis"
        report.infodict()["Subject"] = "Dataset summary, EDA, visualizations and findings"
        text_page(report, "F1 Race Performance Analysis", [
            "Goal: compare driver and constructor performance and explore how starting grid position relates to finishing position and race points.",
            f"Dataset: {len(df):,} driver-race entries across {df.season.nunique()} seasons ({years}), "
            f"{df[['season', 'round']].drop_duplicates().shape[0]} races, "
            f"{df.driverId.nunique()} drivers and {df.constructorId.nunique()} constructors. "
            "One row represents one driver's result in one race.",
            "Inputs: races.csv, drivers.csv and race_results.csv in 00-Raw_data. Results are joined to drivers on driverId and to races on season and round. The original external dataset source is not documented in the repository; the team must add its attribution before submission.",
            "Numerical variables: points, grid, position and laps. Categorical variables: driver, constructor, nationality and result status. Analysis uses the team's cleaned CSV.",
            "Preparation: the existing cleaning script keeps seasons from 2015 onward, removes duplicate rows, fills missing numeric values with medians and missing text with Unknown, and converts selected dates and numbers. Some date conversions may still produce missing values.",
            "Scope: totals describe this dataset, not a complete official championship ranking. Cumulative points depend on participation. Grid analyses use the same selected statuses as the team EDA, exclude grid 0, and show associations rather than causal effects.",
        ])
        numerical = df[["points", "grid", "position", "laps"]].describe().round(2)
        table_page(report, "Numerical Summary Statistics", numerical.reset_index().rename(
            columns={"index": "Statistic"}),
            "All cleaned entries. Grid 0 denotes a non-standard start and is excluded from the grid charts. Recorded position includes non-finishers.")
        statuses = df.status.value_counts().rename_axis("Status").reset_index(name="Entries")
        statuses["Percent"] = (statuses.Entries / len(df) * 100).round(2)
        table_page(report, "Most Frequent Result Statuses", statuses.head(10),
                   "Top 10 statuses only; percentages use all cleaned driver-race entries as the denominator.")
        def save(fig, name):
            fig.tight_layout()
            fig.savefig(OUTPUT / f"{name}.png", bbox_inches="tight")
            report.savefig(fig, bbox_inches="tight")
            plt.close(fig)

        for column, label, name in [
            ("driverName", "Drivers", "top_drivers"),
            ("constructorName", "Constructors", "top_constructors"),
        ]:
            totals = df.groupby(column)["points"].sum().nlargest(10).sort_values()
            fig, ax = plt.subplots(figsize=(10, 6))
            bars = ax.barh(totals.index, totals.values, color="#2563eb")
            ax.bar_label(bars, fmt="%.1f", padding=4)
            ax.set_xlim(0, totals.max() * 1.18)
            ax.set_xlabel("Total race points")
            ax.set_title(f"Top 10 {label} by Total Race Points ({years})", loc="left")
            ax.text(0, -0.16, "Cumulative totals reflect both performance and number of race entries.",
                    transform=ax.transAxes, fontsize=9, color="#555555")
            save(fig, name)

        # Match the finisher definition used in the team's EDA.
        finishers = df[(df.grid > 0) & df.position.notna()
                       & df.status.isin(["Finished", "+1 Lap", "+2 Laps"])].copy()
        fig, ax = plt.subplots(figsize=(9, 6))
        counts = ax.hexbin(finishers.grid, finishers.position, gridsize=20,
                           mincnt=1, cmap="Blues")
        maximum = max(finishers.grid.max(), finishers.position.max())
        ax.plot([1, maximum], [1, maximum], "--", color="#ef4444",
                linewidth=1.5, label="Same starting and finishing position")
        fig.colorbar(counts, ax=ax, label="Race entries per bin")
        ax.set_xlabel("Starting grid position (1 = pole)")
        ax.set_ylabel("Finishing position (1 = winner)")
        ax.set_title(f"Starting vs. Finishing Position ({years})", loc="left")
        ax.legend(fontsize=8)
        ax.text(0, -0.18, f"{len(finishers):,} entries; statuses: Finished, +1 Lap, +2 Laps; grid > 0.",
                transform=ax.transAxes, fontsize=9, color="#555555")
        save(fig, "starting_vs_finishing")

        finishers["starting_group"] = pd.cut(
            finishers.grid, bins=[0, 5, 10, 15, float("inf")],
            labels=["1–5", "6–10", "11–15", "16+"])
        summary = finishers.groupby("starting_group", observed=True).agg(
            average_points=("points", "mean"), race_entries=("points", "count"))
        fig, ax = plt.subplots(figsize=(9, 6))
        bars = ax.bar(summary.index.astype(str), summary.average_points, color="#2563eb")
        ax.bar_label(bars, labels=[f"{row.average_points:.2f}\n(n={int(row.race_entries):,})"
                                   for row in summary.itertuples()], padding=5)
        ax.set_ylim(0, summary.average_points.max() * 1.25)
        ax.set_xlabel("Starting grid position group")
        ax.set_ylabel("Average race points per entry")
        ax.set_title(f"Average Points by Starting Position ({years})", loc="left")
        ax.text(0, -0.16, "Statuses: Finished, +1 Lap, +2 Laps; grid > 0. Association does not establish causation.",
                transform=ax.transAxes, fontsize=9, color="#555555")
        save(fig, "points_by_starting_group")
        driver_points = df.groupby("driverName").points.sum().sort_values(ascending=False)
        team_points = df.groupby("constructorName").points.sum().sort_values(ascending=False)
        correlation = finishers.grid.corr(finishers.position)
        text_page(report, "Key Findings and Interpretation", [
            f"Driver comparison: {driver_points.index[0]} has the highest total in this dataset with {driver_points.iloc[0]:,.1f} race points. The chart ranks cumulative points, so longer participation can increase a driver's total.",
            f"Constructor comparison: {team_points.index[0]} leads with {team_points.iloc[0]:,.1f} race points. Totals combine entries across seasons and should not be interpreted as performance in a single season.",
            f"Starting versus finishing: Pearson correlation is {correlation:.3f} across {len(finishers):,} selected entries. Both axes use lower numbers for better positions. Darker hexagons indicate more entries; entries below the diagonal finished in a better position than they started.",
            "Average points by starting group: " + "; ".join(
                f"grid {group}: {row.average_points:.2f} points ({int(row.race_entries):,} entries)"
                for group, row in summary.iterrows()) + ". These averages apply to the selected result statuses.",
            f"Categorical finding: {statuses.iloc[0]['Status']} is the most frequent status, accounting for {statuses.iloc[0]['Percent']:.2f}% of all cleaned entries.",
            "Limitations: the grid charts include only Finished, +1 Lap and +2 Laps with grid > 0. Finishers further behind and non-finishers are excluded. Filtering can affect the relationship observed. Median-filled lap measurements are not used in these charts. Dataset completeness and original source attribution should be confirmed by the team.",
        ])
    print(f"Saved four PNG charts and f1_visualizations.pdf to {OUTPUT}")


if __name__ == "__main__":
    main()
