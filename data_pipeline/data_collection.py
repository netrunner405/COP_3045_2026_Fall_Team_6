from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / "00-Raw_data"


def load_datasets(raw_data_dir: Path) -> dict[str, pd.DataFrame]:
    """Load the original Formula 1 CSV datasets."""
    datasets = {}

    for name in ["races", "drivers", "race_results"]:
        file_path = raw_data_dir / f"{name}.csv"

        try:
            datasets[name] = pd.read_csv(file_path)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Required dataset not found: {file_path}"
            )
        except (pd.errors.EmptyDataError, pd.errors.ParserError) as error:
            raise ValueError(
                f"Unable to read dataset: {file_path}"
            ) from error

    return datasets


def combine_datasets(
    race_results: pd.DataFrame,
    drivers: pd.DataFrame,
    races: pd.DataFrame
) -> pd.DataFrame:
    """Combine race results, driver information, and race details."""

    if not {"driverId", "season", "round"}.issubset(race_results.columns):
        raise ValueError("Race results are missing required columns.")

    if "driverId" not in drivers.columns:
        raise ValueError("Drivers dataset is missing driverId.")

    if not {"season", "round"}.issubset(races.columns):
        raise ValueError("Races dataset is missing season or round.")

    consolidated = race_results.merge(
        drivers,
        on="driverId",
        how="left"
    )

    race_extra_columns = [
        col for col in races.columns
        if col not in consolidated.columns
    ]

    consolidated = consolidated.merge(
        races[["season", "round"] + race_extra_columns],
        on=["season", "round"],
        how="left"
    )

    return consolidated


def save_dataset(dataset: pd.DataFrame, output_file: Path) -> None:
    """Save a DataFrame to a CSV file without its index."""
    try:
        dataset.to_csv(output_file, index=False)
    except OSError as error:
        raise OSError(
            f"Unable to save dataset to: {output_file}"
        ) from error


def main() -> None:
    """Run the data collection and consolidation process."""
    datasets = load_datasets(RAW_DATA_DIR)

    consolidated = combine_datasets(
        datasets["race_results"],
        datasets["drivers"],
        datasets["races"]
    )

    output_file = RAW_DATA_DIR / "consolidated_data.csv"
    save_dataset(consolidated, output_file)

    print("Consolidated file created:", output_file)
    print("Consolidated head():")
    print(consolidated.head())


if __name__ == "__main__":
    main()