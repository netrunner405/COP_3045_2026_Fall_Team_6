from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine


# 1. Connect to Database
DATABASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = DATABASE_DIR / "project.db"

engine = create_engine(f"sqlite:///{DATABASE_PATH}")
connection = engine.connect()


# 2. Read Tables
race_results = pd.read_sql_table("race_results", con=connection)
drivers = pd.read_sql_table("drivers", con=connection)
races = pd.read_sql_table("races", con=connection)


# 3. Create Analytical DataFrame

# Add driver information to race results
df = race_results.merge(
    drivers,
    on="driverId",
    how="left"
)

# Only add race columns that are not already in df
race_extra_columns = [
    column for column in races.columns
    if column not in df.columns
]

# Add race information
df = df.merge(
    races[["season", "round"] + race_extra_columns],
    on=["season", "round"],
    how="left"
)

# Save analytical dataset
output_file = DATABASE_DIR / "consolidated_data_database.csv"
df.to_csv(output_file, index=False)


# 4. Close Connection
connection.close()