from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

from .data_collection import BASE_DIR, RAW_DATA_DIR, load_datasets


DATABASE_PATH = BASE_DIR / "02-Database" / "project.db"


class F1Database:
    """Manage the Formula 1 SQLite database and its tables."""

    def __init__(self, database_path: Path) -> None:
        """Initialize the database path and SQLAlchemy engine."""
        self._database_path = database_path
        self._engine = create_engine(
            f"sqlite:///{self._database_path}"
        )

    def create_tables(
        self, datasets: dict[str, pd.DataFrame]
    ) -> None:
        """Create or replace database tables using the supplied datasets."""

        required_tables = ["races", "drivers", "race_results"]

        for name in required_tables:
            if name not in datasets:
                raise ValueError(f"Missing required dataset: {name}")

        try:
            with self._engine.begin() as connection:
                for name in required_tables:
                    datasets[name].to_sql(
                        name,
                        con=connection,
                        if_exists="replace",
                        index=False
                    )

        except SQLAlchemyError as error:
            raise RuntimeError(
                f"Unable to create database tables: {error}"
            ) from error

    def read_tables(self) -> dict[str, pd.DataFrame]:
        """Retrieve the Formula 1 tables as Pandas DataFrames."""

        if not self._database_path.is_file():
            raise FileNotFoundError(
                f"Database not found: {self._database_path}"
            )

        datasets = {}

        try:
            with self._engine.connect() as connection:
                for name in ["races", "drivers", "race_results"]:
                    datasets[name] = pd.read_sql_table(
                        name,
                        con=connection
                    )

        except (SQLAlchemyError, ValueError) as error:
            raise RuntimeError(
                f"Unable to read database tables: {error}"
            ) from error

        return datasets

    def close(self) -> None:
        """Release database engine resources."""
        self._engine.dispose()


def main() -> None:
    """Load raw datasets and create the Formula 1 database."""
    datasets = load_datasets(RAW_DATA_DIR)
    database = F1Database(DATABASE_PATH)

    try:
        database.create_tables(datasets)
        print("Database tables created successfully.")
    finally:
        database.close()


if __name__ == "__main__":
    main()
