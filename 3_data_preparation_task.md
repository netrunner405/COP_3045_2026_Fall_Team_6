# Clean and Prepare Data

Clean and prepare `02-Database/consolidated_data_database.csv` for analysis.

## Output

After I approve the plan:

1. Create the folder `03-Data cleaning`.
2. Create `03-Data cleaning/clean_data.py`.
3. Do not execute the Python file. I will run it manually.

## Python Script

Organize the script into four steps:

### 1. Read Data

Read `02-Database/consolidated_data_database.csv` into a pandas DataFrame named `df`.

### 2. Inspect Data

Inspect the DataFrame to identify:

* Missing values
* Duplicate rows
* Data types

### 3. Clean and Prepare Data

* Keep only observations from the 2015-2016 season onward.
* Remove duplicate rows.
* Handle missing values appropriately based on the variable and data type.
* Convert columns to appropriate data types when necessary.
* Keep the implementation simple.

### 4. Save Clean Data

Save the cleaned DataFrame as:

`03-Data cleaning/clean_data.csv`

Do not include the DataFrame index.

Keep the code simple and clearly identify the four steps with comments.
