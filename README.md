# COP_3045_2026_Fall_Team_6
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