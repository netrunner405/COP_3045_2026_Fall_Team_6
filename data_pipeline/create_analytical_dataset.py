from pathlib import Path

from .data_collection import combine_datasets, save_dataset
from .instantiate_database import F1Database, DATABASE_PATH


OUTPUT_FILE = DATABASE_PATH.parent / "consolidated_data_database.csv"


def create_analytical_dataset(
    database: F1Database,
    output_file: Path
) -> None:
    """Combine database tables and export the analytical dataset."""

    datasets = database.read_tables()

    consolidated = combine_datasets(
        datasets["race_results"],
        datasets["drivers"],
        datasets["races"]
    )

    save_dataset(consolidated, output_file)

    print("Analytical dataset created:", output_file)


def main() -> None:
    """Generate the analytical dataset from the Formula 1 database."""
    database = F1Database(DATABASE_PATH)

    try:
        create_analytical_dataset(database, OUTPUT_FILE)
    finally:
        database.close()


if __name__ == "__main__":
    main()
