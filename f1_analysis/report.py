"""Generate the team's Formula 1 PDF report and companion PNG charts."""

from collections.abc import Iterator, Sequence
from pathlib import Path
from tempfile import TemporaryDirectory
from textwrap import fill, wrap

import pandas as pd
from matplotlib import rc_context
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.figure import Figure
from pandas.api.types import is_any_real_numeric_dtype

from .visualizations import (
    add_chart_caption,
    plot_points_by_starting_group,
    plot_points_ranking,
    plot_starting_vs_finishing,
)

PDF_NAME = "f1_visualizations.pdf"
NUMERICAL_COLUMNS = ("points", "grid", "position", "laps")
REQUIRED_COLUMNS = {
    *NUMERICAL_COLUMNS, "season", "round", "driverId", "driverName",
    "constructorId", "constructorName", "status",
}
FINISHER_STATUSES = ("Finished", "+1 Lap", "+2 Laps")


class ReportGenerator:
    """Render cleaned Formula 1 race results to a PDF and four PNGs."""

    def __init__(self, output_dir: Path) -> None:
        """Set the directory where the report and companion graphics are saved."""
        self._output_dir = output_dir

    def generate(self, cleaned_data: pd.DataFrame) -> Path:
        """Write the report and charts and return the path to the PDF."""
        _validate_results(cleaned_data)
        output = self._output_dir
        try:
            output.mkdir(parents=True, exist_ok=True)
            # A failed render leaves the previously generated files available.
            with TemporaryDirectory(dir=output, prefix=".f1-report-") as temporary:
                staging = Path(temporary)
                with rc_context({
                    "font.size": 11,
                    "axes.spines.top": False,
                    "axes.spines.right": False,
                    "figure.dpi": 150,
                }):
                    self._render(cleaned_data, staging)
                artifacts = sorted(staging.iterdir())
                for artifact in artifacts:
                    if (output / artifact.name).is_dir():
                        raise IsADirectoryError(f"{output / artifact.name} is a directory")
                for artifact in artifacts:
                    artifact.replace(output / artifact.name)
        except OSError as error:
            raise OSError(f"Could not save report and charts to {output}: {error}") from error

        return output / PDF_NAME

    def _render(self, results: pd.DataFrame, output: Path) -> None:
        years = f"{int(results['season'].min())}–{int(results['season'].max())}"
        finishers = results.loc[
            (results["grid"] > 0)
            & results["position"].notna()
            & results["status"].isin(FINISHER_STATUSES)
        ]
        starting_groups = _summarize_starting_groups(finishers)
        numerical = results[list(NUMERICAL_COLUMNS)].describe().round(2)
        statuses = results["status"].value_counts().rename_axis("Status").reset_index(name="Entries")
        statuses["Percent"] = (statuses["Entries"] / len(results) * 100).round(2)
        driver_points = results.groupby("driverName")["points"].sum()
        constructor_points = results.groupby("constructorName")["points"].sum()

        with PdfPages(output / PDF_NAME, metadata={
            "Title": "F1 Race Performance Analysis",
            "Subject": "Dataset summary, EDA, visualizations and findings",
        }) as report:
            self._write_text_page(
                report, "F1 Race Performance Analysis", _overview(results, years)
            )
            self._write_table_page(
                report, "Numerical Summary Statistics",
                numerical.rename_axis("Statistic").reset_index(),
                "All cleaned entries. Grid 0 denotes a non-standard start and is excluded "
                "from the grid charts. Recorded position includes non-finishers.",
            )
            self._write_table_page(
                report, "Most Frequent Result Statuses", statuses.head(10),
                "Top 10 statuses only; percentages use all cleaned driver-race entries "
                "as the denominator.",
            )
            for name, figure, caption in _chart_pages(
                years, driver_points, constructor_points, finishers, starting_groups
            ):
                add_chart_caption(figure, caption)
                figure.savefig(output / f"{name}.png", bbox_inches="tight", backend="agg")
                report.savefig(figure, bbox_inches="tight")

            self._write_text_page(
                report, "Key Findings and Interpretation",
                _findings(driver_points, constructor_points, finishers, starting_groups, statuses),
            )

    @staticmethod
    def _write_text_page(report: PdfPages, title: str, paragraphs: Sequence[str]) -> None:
        figure = Figure(figsize=(11.7, 8.3))
        figure.text(0.07, 0.91, title, fontsize=21, weight="bold", color="#173b73")
        y = 0.82
        for paragraph in paragraphs:
            lines = wrap(paragraph, width=105)
            figure.text(0.07, y, "\n".join(lines), fontsize=11, va="top", linespacing=1.6)
            y -= 0.032 * len(lines) + 0.035
        report.savefig(figure)

    @staticmethod
    def _write_table_page(report: PdfPages, title: str, frame: pd.DataFrame, note: str) -> None:
        figure = Figure(figsize=(11.7, 8.3))
        axes = figure.subplots()
        axes.axis("off")
        figure.text(0.07, 0.91, title, fontsize=21, weight="bold", color="#173b73")
        table = axes.table(
            cellText=frame.astype(str).values, colLabels=frame.columns,
            cellLoc="center", bbox=[0, 0.16, 1, 0.68],
        )
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        for (row, _), cell in table.get_celld().items():
            cell.set_edgecolor("#ffffff")
            if row == 0:
                cell.set_facecolor("#173b73")
                cell.set_text_props(color="white", weight="bold")
            else:
                cell.set_facecolor("#eaf0f8" if row % 2 else "#f7f9fc")
        figure.text(0.07, 0.08, fill(note, width=105), fontsize=10)
        report.savefig(figure)


def _validate_results(results: pd.DataFrame) -> None:
    if results.empty:
        raise ValueError("Cleaned race results must contain at least one entry.")
    missing = REQUIRED_COLUMNS.difference(results.columns)
    if missing:
        raise ValueError(f"Missing required race-result columns: {', '.join(sorted(missing))}.")
    if not results.columns.is_unique:
        raise ValueError("Cleaned race results must have unique column names.")
    invalid_numeric = [
        column for column in ("season", *NUMERICAL_COLUMNS)
        if not is_any_real_numeric_dtype(results[column])
        or results[column].isin([float("inf"), float("-inf")]).any()
    ]
    if invalid_numeric:
        raise ValueError(
            f"Expected finite numeric values in: {', '.join(invalid_numeric)}."
        )
    empty_columns = [
        column for column in ("season", "driverName", "constructorName", "status")
        if not results[column].notna().any()
    ]
    if empty_columns:
        raise ValueError(f"No values available in required columns: {', '.join(empty_columns)}.")


def _summarize_starting_groups(finishers: pd.DataFrame) -> pd.DataFrame:
    groups = pd.cut(
        finishers["grid"], bins=[0, 5, 10, 15, float("inf")],
        labels=["1–5", "6–10", "11–15", "16+"],
    )
    return finishers.groupby(groups, observed=True).agg(
        average_points=("points", "mean"), race_entries=("points", "count")
    )


def _chart_pages(
    years: str,
    driver_points: pd.Series,
    constructor_points: pd.Series,
    finishers: pd.DataFrame,
    starting_groups: pd.DataFrame,
) -> Iterator[tuple[str, Figure, str]]:
    driver_count = min(10, len(driver_points))
    constructor_count = min(10, len(constructor_points))
    driver_label = "ten drivers" if driver_count == 10 else f"{driver_count} drivers"
    constructor_label = (
        "ten constructors" if constructor_count == 10 else f"{constructor_count} constructors"
    )
    yield "top_drivers", plot_points_ranking(driver_points, "Drivers", years), (
        f"This chart ranks the {driver_label} with the most accumulated race points in the {years} dataset. "
        "Longer bars indicate higher totals. These totals reflect both performance and the number of "
        "races entered, so they do not measure driver skill alone."
    )
    yield "top_constructors", plot_points_ranking(constructor_points, "Constructors", years), (
        f"This chart ranks the {constructor_label} with the most accumulated race points in the {years} dataset. "
        "Each total combines the team's driver entries across seasons. Longer bars indicate more points, "
        "with participation and performance both contributing to the totals."
    )
    yield (
        "starting_vs_finishing",
        plot_starting_vs_finishing(finishers, years),
        _density_caption(finishers),
    )
    yield (
        "points_by_starting_group",
        plot_points_by_starting_group(starting_groups, years),
        _starting_group_caption(starting_groups),
    )


def _density_caption(finishers: pd.DataFrame) -> str:
    if finishers.empty:
        return (
            "This comparison requires a positive starting grid, a recorded finishing position, "
            "and a status of Finished, +1 Lap, or +2 Laps."
        )
    caption = (
        "This density plot compares starting grid position on the horizontal axis with finishing position on "
        "the vertical axis. Darker hexagons represent more race entries. The dashed diagonal marks unchanged "
        "positions; entries below it gained positions, while those above it lost positions. "
    )
    front_starters = finishers.loc[finishers["grid"] <= 5, "position"]
    if not front_starters.empty and (front_starters <= 5).mean() > 0.5:
        caption += "The dark bottom-left region shows that front starters frequently finished near the front. "
    return (
        caption + "Only entries with grid greater than zero and statuses Finished, +1 Lap, or +2 Laps are included."
    )


def _starting_group_caption(summary: pd.DataFrame) -> str:
    caption = (
        "This chart compares average race points for four starting-grid groups among the same selected finishers "
        "(grid > 0; statuses Finished, +1 Lap, or +2 Laps). "
    )
    averages = summary["average_points"].dropna()
    if {"1–5", "16+"}.issubset(averages.index):
        caption += (
            f"Drivers starting 1–5 averaged {averages['1–5']:.2f} points per entry, compared with "
            f"{averages['16+']:.2f} for those starting 16 or farther back. "
        )
    if averages.empty:
        return caption + "No groups have a recorded points value."
    caption += "The n labels show the number of entries in each group. "
    if len(averages) < 4:
        caption += "Groups without recorded points are omitted. "
    if averages.is_monotonic_decreasing and averages.nunique() > 1:
        caption += (
            "Better starting positions are associated with higher average points in this subset; "
            "the chart does not establish causation."
        )
    return caption.rstrip()


def _overview(results: pd.DataFrame, years: str) -> list[str]:
    race_count = len(results[["season", "round"]].drop_duplicates())
    return [
        "Goal: compare driver and constructor performance and explore how starting grid position "
        "relates to finishing position and race points.",
        f"Dataset: {len(results):,} driver-race entries across {results['season'].nunique()} seasons ({years}), "
        f"{race_count} races, {results['driverId'].nunique()} drivers and "
        f"{results['constructorId'].nunique()} constructors. "
        "One row represents one driver's result in one race.",
        "Inputs: races.csv, drivers.csv and race_results.csv in 00-Raw_data. Results are joined to drivers "
        "on driverId and to races on season and round. The original external dataset source is not documented "
        "in the repository; the team must add its attribution before submission.",
        "Numerical variables: points, grid, position and laps. Categorical variables: driver, constructor, "
        "nationality and result status. Analysis uses the team's cleaned CSV.",
        "Preparation: the existing cleaning script keeps seasons from 2015 onward, removes duplicate rows, "
        "fills missing numeric values with medians and missing text with Unknown, and converts selected dates "
        "and numbers. Some date conversions may still produce missing values.",
        "Scope: totals describe this dataset, not a complete official championship ranking. Cumulative points "
        "depend on participation. Grid analyses use the same selected statuses as the team EDA, exclude grid 0, "
        "and show associations rather than causal effects.",
    ]


def _findings(
    driver_points: pd.Series,
    constructor_points: pd.Series,
    finishers: pd.DataFrame,
    starting_groups: pd.DataFrame,
    statuses: pd.DataFrame,
) -> list[str]:
    best_driver = driver_points.idxmax()
    best_constructor = constructor_points.idxmax()
    status = statuses.iloc[0]
    return [
        f"Driver comparison: {best_driver} has the highest total in this dataset with "
        f"{driver_points[best_driver]:,.1f} race points. The chart ranks cumulative points, "
        "so longer participation can increase a driver's total.",
        f"Constructor comparison: {best_constructor} leads with {constructor_points[best_constructor]:,.1f} "
        "race points. Totals combine entries across seasons and should not be interpreted as performance "
        "in a single season.",
        _correlation_finding(finishers),
        _starting_group_finding(starting_groups),
        f"Categorical finding: {status['Status']} is the most frequent status, accounting for "
        f"{status['Percent']:.2f}% of all cleaned entries.",
        "Limitations: the grid charts include only Finished, +1 Lap and +2 Laps with grid > 0. Finishers "
        "further behind and non-finishers are excluded. Filtering can affect the relationship observed. "
        "Median-filled lap measurements are not used in these charts. Dataset completeness and original "
        "source attribution should be confirmed by the team.",
    ]


def _correlation_finding(finishers: pd.DataFrame) -> str:
    if finishers["grid"].nunique() < 2 or finishers["position"].nunique() < 2:
        return (
            "Starting versus finishing: too few distinct grid and finish positions are available "
            "to calculate a Pearson correlation."
        )
    correlation = finishers["grid"].corr(finishers["position"])
    return (
        f"Starting versus finishing: Pearson correlation is {correlation:.3f} across "
        f"{len(finishers):,} selected entries. Both axes use lower numbers for better positions. "
        "Darker hexagons indicate more entries; entries below the diagonal finished in a better "
        "position than they started."
    )


def _starting_group_finding(summary: pd.DataFrame) -> str:
    groups = summary.dropna(subset=["average_points"])
    if groups.empty:
        return "Average points by starting group: no race points are available for the selected finishers."
    averages = "; ".join(
        f"grid {group}: {row.average_points:.2f} points ({int(row.race_entries):,} entries)"
        for group, row in groups.iterrows()
    )
    return (
        f"Average points by starting group: {averages}. "
        "These averages apply to the selected result statuses."
    )
