# F1 Race Performance Analysis

COP 3045 — Fall 2026 — Team 6

This Python project combines Formula 1 race results, driver information, and
race information to explore driver and constructor performance and the
relationship between starting position, finishing position, and race points.
It includes data preparation, a SQLite database, exploratory data analysis
(EDA), four visualizations, and an automatically generated PDF report.

## Datasets

The input CSV files are included in `00-Raw_data/`.

| Dataset | Information | Join key |
| --- | --- | --- |
| `race_results.csv` | Driver-race results, points, starting grid, finishing position, laps, constructor, and result status | `driverId`; `season` and `round` |
| `drivers.csv` | Driver identity, name, nationality, and other driver attributes | `driverId` |
| `races.csv` | Race, season, round, circuit, and date information | `season` and `round` |

The analytical dataset uses left joins from race results to drivers and races.
Each row represents one driver's result in one race. Numerical variables
include `points`, `grid`, `position`, and `laps`. Categorical variables include
driver, constructor, nationality, and result status.

The current cleaned dataset covers 2015–2024 and contains 4,219 driver-race
entries across 209 races, 53 drivers, and 18 constructors. These figures
describe the included files and may change if the inputs are updated.

**Source attribution:** The original external dataset provider, download links,
and licensing information still need to be confirmed and added by the team.
The included CSV filenames alone do not establish their source.

## Repository structure

```text
00-Raw_data/          Source CSVs and a consolidated CSV
01-Data_collection/   Script to read and combine the source CSVs
02-Database/          SQLite creation, analytical dataset script, and outputs
03-Data_Cleaning/     Cleaning script and locally generated clean_data.csv
04-EDA/               EDA script and summary CSVs
05-Visualizations/    Chart/report script, instructions, and generated outputs
environment.yml      Portable Conda environment specification
```

## Environment setup

The application requires Python, pandas, SQLAlchemy, and matplotlib. Charts
use a noninteractive rendering backend, so no graphical desktop is required.

Create and activate the shared environment from the repository root:

```sh
conda env create -f environment.yml
conda activate cop3045
```

## Run the project

Run the following commands from the repository root, in order:

```sh
python 02-Database/instantiate_database.py
python 02-Database/create_analytical_dataset.py
python 03-Data_Cleaning/clean_data.py
python 04-EDA/eda_analysis.py
python 05-Visualizations/create_visualizations.py
```

The database script replaces the three SQLite tables using the input CSVs.
The analytical dataset script combines those tables into a CSV. Cleaning
creates `03-Data_Cleaning/clean_data.csv`; that generated file is not currently
tracked in Git and must be created before EDA or visualization runs. EDA saves
summary tables, and the final script automatically writes the PDF and charts.
Rerunning replaces the corresponding generated outputs.

The optional `01-Data_collection/data_collection.py` also combines the raw CSVs
directly into `00-Raw_data/consolidated_data.csv`. The database workflow above
reads the three source CSVs independently and does not require that extra step.

Each stage currently runs separately. A single application entry point to
automate all stages remains an integration task.

## Data preparation and EDA

The cleaning script keeps seasons from 2015 onward, removes duplicate rows,
fills missing numerical values with medians and missing text with `Unknown`,
and converts selected date and numerical columns. Invalid date or numerical
conversions can still yield missing values. These are the implemented rules;
the team should validate join keys, dataset completeness, and whether each
imputation is appropriate before final submission.

EDA generates numerical descriptive statistics, driver and constructor
performance summaries, nationality and result-status counts and percentages,
season counts, and a starting-position group comparison.

## Exploratory Data Analysis (EDA)

**Contributor:** Sarah Singh

### Purpose
The goal of the exploratory data analysis was to examine Formula 1 driver and race performance and investigate whether drivers who start closer to the front of the grid generally achieve better finishing positions.

### Dataset
The analysis uses 4,219 Formula 1 race-result records from the 2015–2024 seasons. The dataset includes numerical variables such as starting grid position, recorded finishing position, points earned, and laps completed, along with categorical variables such as driver nationality, constructor, and race status.

### Analysis Performed

- Calculated descriptive statistics for numerical variables using Pandas.
- Analyzed categorical variables using frequency counts and percentages.
- Compared driver and constructor performance using grouped summary tables.
- Calculated correlations between starting grid position and recorded finishing position.
- Compared average finishing positions and points across starting-grid groups.
- Exported nine CSV summary tables for use in visualizations and automated reporting.

### Key Findings

- The correlation between starting grid position and recorded race position was **0.618** across the analyzed race results.
- For 3,416 selected finisher records, the correlation increased to **0.761**, indicating a strong positive relationship.
- Drivers starting in positions **1–5** had an average recorded finishing position of **3.67** and earned **14.94 points** on average.
- Drivers starting in positions **16 or farther back** had an average recorded finishing position of **13.55** and earned **0.92 points** on average.

These results suggest that drivers starting closer to the front generally achieve better race results. However, correlation does not establish causation, and factors such as car performance and driver skill may also influence the results.

### Files

- `04-EDA/eda_analysis.py` — Python script for numerical, categorical, and correlation analysis.
- `04-EDA/outputs/` — Exported CSV summary tables containing the analysis results.

## Visualizations and report

Open the [generated PDF report](05-Visualizations/outputs/f1_visualizations.pdf).
It contains the project goal, dataset summary, preparation notes, numerical
and categorical tables, four charts, calculated findings, and limitations.

| Chart | Analytical purpose |
| --- | --- |
| Top 10 drivers by total race points | Compare cumulative driver performance |
| Top 10 constructors by total race points | Compare cumulative constructor performance |
| Starting versus finishing position | Explore the relationship using a density plot |
| Average points by starting-position group | Compare mean points across grid groups |

Individual PNG charts and the PDF are saved in `05-Visualizations/outputs/`.
The report calculates its tables directly from the cleaned input; exported
summary CSVs are maintained by EDA in `04-EDA/outputs/`.
See the [visualization instructions](05-Visualizations/README.md) for details.

The grid analyses match the EDA filter: `grid > 0` and statuses `Finished`,
`+1 Lap`, or `+2 Laps`. This excludes other finishers and non-finishers, so
findings apply to that selected subset. Lower starting and finishing position
numbers indicate better placements. Cumulative point rankings reflect both
performance and participation and are not official championship standings.
Observed relationships do not establish causation.

## Team contributions and GitHub workflow

| Team member | Contributions evidenced by the current repository |
| --- | --- |
| Alain Nammur (`netrunner405`) | Initial project setup, dataset consolidation, SQLite database, and analytical dataset pipeline |
| Sarah Singh | EDA, summary tables, and starting-versus-finishing position analysis |
| Drishti Sharma (`drishti8005-wq`) | Four visualizations, automated PDF report, report validation, and visualization documentation |
| Cleaning contributor — name to confirm | Data cleaning script; the original commit currently uses the placeholder author `Your Name` |

The team should confirm this table and update it as remaining work is completed.
Original commits and PRs provide contribution evidence even when a commit email
is not linked to a GitHub account.

Develop changes on feature branches, commit and push them, and open pull
requests for team review before merging into `main`. Configure commit names
and emails so contributions are attributed correctly. A branch based on a
teammate's branch includes that teammate's commits; review the complete PR
scope before merging.

## Submission checklist

- Confirm dataset sources and licensing, join correctness, and cleaning rules.
- Verify a fresh Conda setup using `environment.yml` on the team's machines.
- Add and verify a single command for the complete workflow.
- Review the report and merge approved changes through pull requests.
- Record the approximately 10-minute presentation with all members explaining
  their contributions and a live demonstration of PDF generation.
- Submit an accessible YouTube link; a slide deck is recommended.
- Each member submits their own peer-review form.
