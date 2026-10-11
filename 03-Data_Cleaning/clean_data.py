from pathlib import Path

import pandas as pd


# Step 1: Read Data
root_dir = Path(__file__).resolve().parents[1]
data_file = root_dir / "02-Database" / "consolidated_data_database.csv"
df = pd.read_csv(data_file)


# Step 2: Inspect Data
print("Data shape:", df.shape)
print("\nMissing values:\n", df.isnull().sum())
print("\nDuplicate rows:", df.duplicated().sum())
print("\nData types:\n", df.dtypes)


# Step 3: Clean and Prepare Data
# Keep only observations from the 2015-2016 season onward
if "season" in df.columns:
    df["season"] = pd.to_numeric(df["season"], errors="coerce")
    df = df[df["season"] >= 2015].copy()

# Remove duplicate rows
if df.duplicated().any():
    df = df.drop_duplicates().reset_index(drop=True)

# Handle missing values based on variable type
numeric_columns = df.select_dtypes(include=["number"]).columns
for col in numeric_columns:
    if df[col].isnull().any():
        df[col] = df[col].fillna(df[col].median())

string_columns = df.select_dtypes(exclude=["number"]).columns
for col in string_columns:
    if df[col].isnull().any():
        df[col] = df[col].fillna("Unknown")

# Convert selected columns to more useful data types
for col in ["date", "firstPractice", "secondPractice", "thirdPractice", "qualifying", "sprint"]:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")

for col in ["number", "position", "positionText", "points", "grid", "laps", "fastestLapRank", "fastestLap_lap", "averageSpeed"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")


# Step 4: Save Clean Data
output_file = Path(__file__).resolve().parent / "clean_data.csv"
df.to_csv(output_file, index=False)
print("\nClean data saved to:", output_file)
