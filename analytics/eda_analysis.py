from pathlib import Path

import pandas as pd


def load_data(data_file: Path) -> pd.DataFrame:
    """Load the cleaned F1 dataset from a CSV file."""
    try:
        return pd.read_csv(data_file, low_memory=False)
    except FileNotFoundError as error:
        raise FileNotFoundError(
            f"Cleaned dataset not found: {data_file}"
        ) from error
    except (pd.errors.EmptyDataError, pd.errors.ParserError) as error:
        raise ValueError(
            f"Unable to read dataset: {data_file}"
        ) from error


class RaceAnalysis:
    """Perform exploratory data analysis on F1 race results."""

    def __init__(self, data: pd.DataFrame):
        """Initialize and validate the race dataset."""
        required_columns = [
            "season", "driverId", "constructorId",
            "driverName", "constructorName", "points",
            "grid", "position", "laps", "nationality",
            "status"
        ]

        if not isinstance(data, pd.DataFrame):
            raise TypeError("Data must be a pandas DataFrame.")

        if data.empty:
            raise ValueError("The dataset is empty.")

        missing_columns = [
            column for column in required_columns
            if column not in data.columns
        ]

        if missing_columns:
            raise ValueError(
                f"Missing required columns: {missing_columns}"
            )

        for column in ["points", "grid", "position", "laps"]:
            if not pd.api.types.is_numeric_dtype(data[column]):
                raise ValueError(
                    f"Column '{column}' must contain numerical data."
                )

        self._data = data.copy()

    @property
    def data(self) -> pd.DataFrame:
        """Return a copy of the race dataset."""
        return self._data.copy()

    def inspect_data(self) -> None:
        """Display basic dataset information."""
        print("F1 Race Performance Analysis")
        print("=" * 40)

        print("\nDataset shape:", self._data.shape)
        print("\nColumn names:")
        print(self._data.columns.tolist())

        print("\nFirst 5 rows:")
        print(self._data.head())

        print("\nRemaining missing values:")
        print(self._data.isnull().sum())

        print("\nTotal race results:", len(self._data))
        print("Number of seasons:", self._data["season"].nunique())
        print("Number of drivers:", self._data["driverId"].nunique())
        print(
            "Number of constructors:",
            self._data["constructorId"].nunique()
        )

        print(
            "\nAverage points per race result:",
            round(self._data["points"].mean(), 2)
        )
        print(
            "Average starting grid position:",
            round(self._data["grid"].mean(), 2)
        )
        print(
            "Average recorded race position:",
            round(self._data["position"].mean(), 2)
        )

    def numerical_summary(self) -> pd.DataFrame:
        """Calculate descriptive statistics for numerical variables."""
        return self._data[
            ["points", "grid", "position", "laps"]
        ].describe().round(2)

    def performance_summary(self, column: str) -> pd.DataFrame:
        """Calculate performance statistics by driver or constructor."""
        if column not in ["driverName", "constructorName"]:
            raise ValueError(
                "Column must be driverName or constructorName."
            )

        summary = self._data.groupby(column).agg(
            race_entries=("points", "count"),
            total_points=("points", "sum"),
            average_points=("points", "mean"),
            average_starting_position=("grid", "mean")
        ).reset_index()

        return summary.sort_values(
            by="total_points",
            ascending=False
        ).round(2)

    def categorical_summary(self, column: str) -> pd.DataFrame:
        """Calculate frequency counts for a categorical variable."""
        if column not in self._data.columns:
            raise ValueError(f"Column not found: {column}")

        counts = self._data[column].value_counts()

        if column == "season":
            counts = counts.sort_index()

        return counts.rename_axis(column).reset_index(
            name="race_entries"
        )

    def categorical_percentages(self, column: str) -> pd.DataFrame:
        """Calculate percentage distributions for a variable."""
        if column not in self._data.columns:
            raise ValueError(f"Column not found: {column}")

        return (
            self._data[column]
            .value_counts(normalize=True)
            .mul(100)
            .round(2)
            .rename_axis(column)
            .reset_index(name="percentage")
        )

    def get_finishers(self) -> pd.DataFrame:
        """Select race finishers using the original status criteria."""
        return self._data[
            (self._data["grid"] > 0) &
            (self._data["status"].isin(
                ["Finished", "+1 Lap", "+2 Laps"]
            ))
        ].copy()

    def calculate_correlations(self) -> dict:
        """Calculate correlations between starting and race positions."""
        race_positions = self._data[
            (self._data["grid"] > 0) &
            (self._data["position"].notna())
        ]

        finishers = self.get_finishers()

        correlation = race_positions["grid"].corr(
            race_positions["position"]
        )

        finisher_correlation = finishers["grid"].corr(
            finishers["position"]
        )

        return {
            "overall_correlation": round(correlation, 3),
            "finisher_correlation": round(finisher_correlation, 3),
            "number_of_finishers": len(finishers)
        }

    def starting_position_summary(self) -> pd.DataFrame:
        """Compare race performance across starting-grid groups."""
        finishers = self.get_finishers()

        finishers["starting_group"] = pd.cut(
            finishers["grid"],
            bins=[0, 5, 10, 15, float("inf")],
            labels=["1-5", "6-10", "11-15", "16+"]
        )

        return finishers.groupby(
            "starting_group",
            observed=True
        ).agg(
            race_entries=("position", "count"),
            average_finishing_position=("position", "mean"),
            average_points=("points", "mean")
        ).round(2)

    def save_summary_tables(self, output_dir: Path) -> None:
        """Generate and save all nine EDA summary tables."""
        tables = {
            "numerical_summary.csv": self.numerical_summary(),
            "driver_summary.csv": self.performance_summary(
                "driverName"
            ),
            "constructor_summary.csv": self.performance_summary(
                "constructorName"
            ),
            "nationality_summary.csv": self.categorical_summary(
                "nationality"
            ),
            "status_summary.csv": self.categorical_summary("status"),
            "season_summary.csv": self.categorical_summary("season"),
            "nationality_percentages.csv": self.categorical_percentages(
                "nationality"
            ),
            "status_percentages.csv": self.categorical_percentages(
                "status"
            ),
            "starting_position_summary.csv":
                self.starting_position_summary()
        }

        indexed_tables = [
            "numerical_summary.csv",
            "starting_position_summary.csv"
        ]

        try:
            output_dir.mkdir(parents=True, exist_ok=True)

            for filename, table in tables.items():
                table.to_csv(
                    output_dir / filename,
                    index=filename in indexed_tables
                )

        except OSError as error:
            raise OSError(
                f"Unable to save EDA results to {output_dir}"
            ) from error

        print("\nEDA summary tables saved successfully!")
        print("Output folder:", output_dir)


def run_eda(data_file: Path, output_dir: Path) -> None:
    """Coordinate the complete exploratory data analysis workflow."""
    data = load_data(data_file)
    analysis = RaceAnalysis(data)

    analysis.inspect_data()

    print("\n--- Numerical Summary Statistics ---")
    print(analysis.numerical_summary())

    print("\n--- Top 10 Drivers by Total Points ---")
    print(
        analysis.performance_summary("driverName")
        .head(10).to_string(index=False)
    )

    print("\n--- Top 10 Constructors by Total Points ---")
    print(
        analysis.performance_summary("constructorName")
        .head(10).to_string(index=False)
    )

    print("\n--- Categorical Data Analysis ---")

    for column in ["nationality", "status", "season"]:
        print(f"\n{column.title()} Summary:")
        summary = analysis.categorical_summary(column)

        if column != "season":
            summary = summary.head(10)

        print(summary.to_string(index=False))

    print("\n--- Categorical Proportions ---")

    for column in ["nationality", "status"]:
        print(f"\n{column.title()} Percentages:")
        print(
            analysis.categorical_percentages(column)
            .head(10).to_string(index=False)
        )

    print("\n--- Starting Grid vs. Race Position ---")

    correlations = analysis.calculate_correlations()

    print(
        "Overall correlation:",
        correlations["overall_correlation"]
    )
    print(
        "Correlation for selected finishers:",
        correlations["finisher_correlation"]
    )
    print(
        "Number of finishers analyzed:",
        correlations["number_of_finishers"]
    )

    print("\n--- Starting Position Group Comparison ---")
    print(analysis.starting_position_summary())

    analysis.save_summary_tables(output_dir)


if __name__ == "__main__":
    root_dir = Path(__file__).resolve().parents[1]

    data_file = (
        root_dir / "03-Data_Cleaning" / "clean_data.csv"
    )

    output_dir = root_dir / "04-EDA" / "outputs"

    try:
        run_eda(data_file, output_dir)
    except (ValueError, TypeError, OSError) as error:
        raise SystemExit(f"EDA error: {error}") from error