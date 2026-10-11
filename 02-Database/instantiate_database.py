from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine


# 1. Instantiate Database
PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_DIR / "00-Raw_data"
DATABASE_PATH = Path(__file__).resolve().parent / "project.db"

engine = create_engine(f"sqlite:///{DATABASE_PATH}")
connection = engine.connect()


# 2. Read Data
races_df = pd.read_csv(RAW_DATA_DIR / "races.csv")
drivers_df = pd.read_csv(RAW_DATA_DIR / "drivers.csv")
race_results_df = pd.read_csv(RAW_DATA_DIR / "race_results.csv")


# 3. Create Tables
races_df.to_sql(
    "races",
    con=connection,
    if_exists="replace",
    index=False
)

drivers_df.to_sql(
    "drivers",
    con=connection,
    if_exists="replace",
    index=False
)

race_results_df.to_sql(
    "race_results",
    con=connection,
    if_exists="replace",
    index=False
)


# 4. Close Connection
connection.close()
engine.dispose()