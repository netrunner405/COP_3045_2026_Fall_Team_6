from .data_collection import (
    RAW_DATA_DIR,
    load_datasets,
    combine_datasets,
    save_dataset
)
from .instantiate_database import F1Database, DATABASE_PATH
from .create_analytical_dataset import (
    create_analytical_dataset,
    OUTPUT_FILE
)


def run_pipeline() -> None:
    """Execute the complete Formula 1 data integration pipeline."""

    # Load the original datasets
    datasets = load_datasets(RAW_DATA_DIR)

    # Combine and export the raw datasets
    consolidated = combine_datasets(
        datasets["race_results"],
        datasets["drivers"],
        datasets["races"]
    )

    output_file = RAW_DATA_DIR / "consolidated_data.csv"
    save_dataset(consolidated, output_file)
    print("Consolidated file created:", output_file)

    # Create and populate the database
    database = F1Database(DATABASE_PATH)

    try:
        database.create_tables(datasets)
        print("Database tables created successfully.")

        # Generate the analytical dataset
        create_analytical_dataset(database, OUTPUT_FILE)

    finally:
        database.close()

    print("Data pipeline completed successfully.")


if __name__ == "__main__":
    run_pipeline()