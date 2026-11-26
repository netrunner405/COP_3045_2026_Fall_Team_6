from pathlib import Path

import pandas as pd


DATE_COLUMNS = (
    "date",
    "firstPractice",
    "secondPractice",
    "thirdPractice",
    "qualifying",
    "sprint",
)
NUMERIC_COLUMNS = (
    "season",
    "round",
    "number",
    "position",
    "points",
    "grid",
    "laps",
    "fastestLapRank",
    "fastestLap_lap",
    "averageSpeed",
    "permanentNumber",
)
TEXT_COLUMNS = (
    "driverId",
    "driverName",
    "constructorId",
    "constructorName",
    "positionText",
    "status",
    "time",
    "fastestLapTime",
    "givenName",
    "familyName",
    "code",
    "nationality",
    "url",
    "raceName",
    "circuitId",
    "circuitName",
)


def inspect_data(data):
    print("Data shape:", data.shape)
    print("\nMissing values:\n", data.isnull().sum())
    print("\nDuplicate rows:", data.duplicated().sum())
    print("\nData types:\n", data.dtypes)


def remove_duplicate_rows(data):
    return data.drop_duplicates().reset_index(drop=True)


def handle_missing_values(data):
    data = data.copy()

    numeric_columns = data.select_dtypes(include=["number"]).columns
    for column in numeric_columns:
        if data[column].isnull().any():
            data[column] = data[column].fillna(data[column].median())

    string_columns = data.select_dtypes(exclude=["number"]).columns
    for column in string_columns:
        if data[column].isnull().any():
            data[column] = data[column].fillna("Unknown")

    return data


def clean_and_prepare_data(data):
    data = data.copy()

    # Keep only observations from the 2015-2016 season onward.
    if "season" in data.columns:
        data["season"] = pd.to_numeric(data["season"], errors="coerce")
        data = data[data["season"] >= 2015].copy()

    data = remove_duplicate_rows(data)
    data = handle_missing_values(data)

    for column in DATE_COLUMNS:
        if column in data.columns:
            data[column] = pd.to_datetime(data[column], errors="coerce")

    for column in NUMERIC_COLUMNS:
        if column in data.columns:
            data[column] = pd.to_numeric(data[column], errors="coerce")

    for column in TEXT_COLUMNS:
        if column in data.columns:
            data[column] = data[column].astype("string")

    validate_data_types(data)
    return data


def validate_data_types(data):
    invalid_columns = []

    for column in DATE_COLUMNS:
        if column in data.columns and not pd.api.types.is_datetime64_any_dtype(data[column]):
            invalid_columns.append(f"{column}: expected datetime, got {data[column].dtype}")

    for column in NUMERIC_COLUMNS:
        if column in data.columns and not pd.api.types.is_numeric_dtype(data[column]):
            invalid_columns.append(f"{column}: expected numeric, got {data[column].dtype}")

    for column in TEXT_COLUMNS:
        if column in data.columns and not pd.api.types.is_string_dtype(data[column].dtype):
            invalid_columns.append(f"{column}: expected string, got {data[column].dtype}")

    if invalid_columns:
        raise TypeError("Invalid data types:\n" + "\n".join(invalid_columns))


def main():
    try:
        root_dir = Path(__file__).resolve().parents[1]
        data_file = root_dir / "02-Database" / "consolidated_data_database.csv"
        data = pd.read_csv(data_file)

        inspect_data(data)
        cleaned_data = clean_and_prepare_data(data)

        output_file = Path(__file__).resolve().parent / "clean_data.csv"
        cleaned_data.to_csv(output_file, index=False)
        print("\nClean data saved to:", output_file)
    except NameError as error:
        print(f"Name error while processing data: {error}. Check variable and function names.")
        raise SystemExit(1) from error
    except TypeError as error:
        print(f"Data type error while validating data: {error}")
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
