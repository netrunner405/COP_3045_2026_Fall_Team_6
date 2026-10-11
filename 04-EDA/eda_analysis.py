
from pathlib import Path
import pandas as pd


# ============================================================
# 1. LOAD AND INSPECT DATA


# Locate the cleaned F1 dataset
root_dir = Path(__file__).resolve().parents[1]
data_file = root_dir / "03-Data_Cleaning" / "clean_data.csv"

# Read the dataset
df = pd.read_csv(data_file, low_memory=False)

print("F1 Race Performance Analysis")
print("=" * 40)

print("\nDataset shape:", df.shape)
print("\nColumn names:")
print(df.columns.tolist())

print("\nFirst 5 rows:")
print(df.head())

print("\nRemaining missing values:")
print(df.isnull().sum())


# ============================================================
# 2. NUMERICAL SUMMARY STATISTICS


print("\n--- Numerical Summary Statistics ---")

# Basic dataset information
print("\nTotal race results:", len(df))
print("Number of seasons:", df["season"].nunique())
print("Number of drivers:", df["driverId"].nunique())
print("Number of constructors:", df["constructorId"].nunique())

# Average performance measurements
print("\nAverage points per race result:", round(df["points"].mean(), 2))
print("Average starting grid position:", round(df["grid"].mean(), 2))
print("Average recorded race position:", round(df["position"].mean(), 2))

# Detailed statistics for numerical variables
numeric_summary = df[
    ["points", "grid", "position", "laps"]
].describe().round(2)

print("\nNumerical Variables Summary:")
print(numeric_summary)


# ============================================================
# 3. DRIVER PERFORMANCE ANALYSIS


print("\n--- Top 10 Drivers by Total Points ---")

# Group race results by driver
driver_stats = df.groupby("driverName").agg(
    race_entries=("points", "count"),
    total_points=("points", "sum"),
    average_points=("points", "mean"),
    average_starting_position=("grid", "mean")
).reset_index()

# Rank drivers by total points
driver_stats = driver_stats.sort_values(
    by="total_points",
    ascending=False
).round(2)

print(driver_stats.head(10).to_string(index=False))


# ============================================================
# 4. CONSTRUCTOR PERFORMANCE ANALYSIS


print("\n--- Top 10 Constructors by Total Points ---")

# Group race results by racing team
constructor_stats = df.groupby("constructorName").agg(
    race_entries=("points", "count"),
    total_points=("points", "sum"),
    average_points=("points", "mean"),
    average_starting_position=("grid", "mean")
).reset_index()

# Rank constructors by total points
constructor_stats = constructor_stats.sort_values(
    by="total_points",
    ascending=False
).round(2)

print(constructor_stats.head(10).to_string(index=False))


# ============================================================
# 5. CATEGORICAL DATA ANALYSIS


print("\n--- Categorical Data Analysis ---")

# Count race entries by driver nationality
nationality_summary = (
    df["nationality"]
    .value_counts()
    .rename_axis("nationality")
    .reset_index(name="race_entries")
)

print("\nTop 10 Nationalities by Race Entries:")
print(nationality_summary.head(10).to_string(index=False))

# Count race entries by race-result status
status_summary = (
    df["status"]
    .value_counts()
    .rename_axis("status")
    .reset_index(name="race_entries")
)

print("\nTop 10 Race Result Statuses:")
print(status_summary.head(10).to_string(index=False))

# Count race entries by season
season_summary = (
    df["season"]
    .value_counts()
    .sort_index()
    .rename_axis("season")
    .reset_index(name="race_entries")
)

print("\nRace Results by Season:")
print(season_summary.to_string(index=False))


# ============================================================
# 6. CATEGORICAL PROPORTIONS


print("\n--- Categorical Proportions ---")

# Percentage of race entries by nationality
nationality_percent = (
    df["nationality"]
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
    .rename_axis("nationality")
    .reset_index(name="percentage")
)

print("\nTop 10 Nationalities (%):")
print(nationality_percent.head(10).to_string(index=False))

# Percentage of race entries by race-result status
status_percent = (
    df["status"]
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
    .rename_axis("status")
    .reset_index(name="percentage")
)

print("\nTop 10 Race Result Statuses (%):")
print(status_percent.head(10).to_string(index=False))


# ============================================================
# 7. SAVE EDA SUMMARY TABLES


# Create an output folder for all summary tables
output_dir = Path(__file__).resolve().parent / "outputs"
output_dir.mkdir(exist_ok=True)

# Save numerical statistics
numeric_summary.to_csv(output_dir / "numerical_summary.csv")

# Save driver and constructor statistics
driver_stats.to_csv(output_dir / "driver_summary.csv", index=False)
constructor_stats.to_csv(output_dir / "constructor_summary.csv", index=False)

# Save categorical frequency tables
nationality_summary.to_csv(output_dir / "nationality_summary.csv", index=False)
status_summary.to_csv(output_dir / "status_summary.csv", index=False)
season_summary.to_csv(output_dir / "season_summary.csv", index=False)

# Save categorical percentage tables
nationality_percent.to_csv(
    output_dir / "nationality_percentages.csv", index=False
)
status_percent.to_csv(
    output_dir / "status_percentages.csv", index=False
)

print("\nEDA summary tables saved successfully!")
print("Output folder:", output_dir)

print("Output folder:", output_dir)

# ============================================================
# 8. STARTING GRID VS. RACE POSITION
# ============================================================

print("\n--- Starting Grid vs. Race Position ---")

# Exclude non-standard starting positions (grid = 0)
race_positions = df[
    (df["grid"] > 0) &
    (df["position"].notna())
].copy()

# Calculate the correlation between starting and race position
correlation = race_positions["grid"].corr(
    race_positions["position"]
)

print("Correlation between starting and race position:",
      round(correlation, 3))


# Compare starting and finishing positions for race finishers
finishers = df[
    (df["grid"] > 0) &
    (df["status"].isin(["Finished", "+1 Lap", "+2 Laps"]))
].copy()

finisher_correlation = finishers["grid"].corr(
    finishers["position"]
)

print("\nCorrelation for classified finishers:",
      round(finisher_correlation, 3))

print("Number of finishers analyzed:", len(finishers))

# ============================================================
# 9. STARTING POSITION GROUP COMPARISON
# ============================================================

print("\n--- Starting Position Group Comparison ---")

# Divide drivers into starting-grid groups
finishers["starting_group"] = pd.cut(
    finishers["grid"],
    bins=[0, 5, 10, 15, float("inf")],
    labels=["1-5", "6-10", "11-15", "16+"]
)

# Calculate average recorded finishing position for each group
grid_summary = finishers.groupby(
    "starting_group",
    observed=True
).agg(
    race_entries=("position", "count"),
    average_finishing_position=("position", "mean"),
    average_points=("points", "mean")
).round(2)

print(grid_summary)

# Save the results for graphs and the PDF report
grid_summary.to_csv(
    output_dir / "starting_position_summary.csv"
)
