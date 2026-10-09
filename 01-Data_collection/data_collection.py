from pathlib import Path
import pandas as pd

# Go up from 01-Data_collection to the project folder
BASE_DIR = Path(__file__).resolve().parent.parent

# Raw data folder
RAW_DATA_DIR = BASE_DIR / "00-Raw_data"

# Load the CSV files
races = pd.read_csv(RAW_DATA_DIR / "races.csv")
drivers = pd.read_csv(RAW_DATA_DIR / "drivers.csv")
race_results = pd.read_csv(RAW_DATA_DIR / "race_results.csv")

# Merge race results with driver information
consolidated = race_results.merge(
    drivers,
    on="driverId",
    how="left"
)

# Only bring in race columns that are not already in consolidated
race_extra_columns = [
    col for col in races.columns
    if col not in consolidated.columns
]

# Merge in race information
consolidated = consolidated.merge(
    races[["season", "round"] + race_extra_columns],
    on=["season", "round"],
    how="left"
)

# Save the consolidated dataset
output_file = RAW_DATA_DIR / "consolidated_data.csv"
consolidated.to_csv(output_file, index=False)

print("Consolidated file created:", output_file)

# Optional: show the first few rows of the consolidated dataset
print("Consolidated head():")
print(consolidated.head())