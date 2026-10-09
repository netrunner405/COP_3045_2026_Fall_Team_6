# Create SQLite Database

Create a SQLite database using **pandas and SQLAlchemy**.

## Source Files

Use these files from `00-Raw_data`:

* `races.csv`
* `drivers.csv`
* `race_results.csv`

## Output

After I approve the plan:

1. Create the folder `02-Database`.
2. Create `02-Database/instantiate_database.py`.
3. Do not execute the Python file. I will run it manually.

When executed, `instantiate_database.py` should create `02-Database/project.db`.

Do not include code in `instantiate_database.py` to create the `02-Database`
folder. Copilot should create the folder before creating the Python file.

## Python Script

Organize `instantiate_database.py` into four steps:

### 1. Instantiate Database

* Create a SQLite engine using SQLAlchemy.
* Connect to `project.db`.

### 2. Read Data

Read the three CSV files into pandas DataFrames.

### 3. Create Tables

Create these tables using `DataFrame.to_sql()`:

* `races`
* `drivers`
* `race_results`

Use:

* `if_exists="replace"`
* `index=False`

### 4. Close Connection

Close the database connection.

Keep the code simple.