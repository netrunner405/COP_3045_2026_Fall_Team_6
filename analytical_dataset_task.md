# Create Analytical Dataset

Create a pandas DataFrame for analysis using the three tables in
`02-Database/project.db`:

* `races`
* `drivers`
* `race_results`

## Output

After I approve the plan:

1. Create `02-Database/create_analytical_dataset.py`.
2. Do not execute the Python file. I will run it manually.

## Python Script

Organize the script into four steps:

### 1. Connect to Database

* Create a SQLAlchemy engine.
* Connect to `02-Database/project.db`.

### 2. Read Tables

Read the three tables into pandas DataFrames.

### 3. Create Analytical DataFrame

Create a single DataFrame named `df`:

1. Left join `race_results` with `drivers` using `driverId`.
2. Left join the result with `races` using `season` and `round`.
3. From `races`, add only columns that are not already present in the DataFrame to avoid duplicate columns.
4. Save the final DataFrame as:
   `02-Database/consolidated_data_database.csv`

Do not save the resulting DataFrame as a new table in the database.

### 4. Close Connection

Close the database connection.

Keep the implementation simple.