# F1 visualizations and automated report

From the repository root, create and activate the shared Conda environment:

```sh
conda env create -f environment.yml
conda activate cop3045
```

Then generate the cleaned input and report:

```sh
python3 03-Data_Cleaning/clean_data.py
python3 05-Visualizations/create_visualizations.py
```

The visualization script reads `03-Data_Cleaning/clean_data.csv` and automatically
creates `outputs/f1_visualizations.pdf`. The report includes the project goal,
dataset summary, preparation notes, numerical and categorical tables, four
charts, calculated findings, and limitations. Individual charts are saved as
PNGs. Report tables are calculated directly from the cleaned data and embedded
in the PDF. Exported summary CSVs belong in `04-EDA/outputs/`; the visualization
script does not export duplicate summaries. Rerunning replaces the PDF and PNGs.

Charts compare driver and constructor cumulative race points, starting versus
finishing position, and mean points by starting group. The grid charts match
the team's EDA filter: grid greater than zero and statuses `Finished`, `+1 Lap`,
or `+2 Laps`. This is a selected subset, not all classified finishers.

Before submission, the team must document the original external dataset source.
The shared environment.yml includes pandas, SQLAlchemy, and matplotlib.
This script runs the visualization/report stage; a team
entry point is still needed to automate the preceding preparation stages.
