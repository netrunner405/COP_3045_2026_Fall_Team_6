from pathlib import Path

import pandas as pd

from data_pipeline.pipeline import run_pipeline
from data_pipeline.clean_data import main as clean_data
from analytics import run_eda
from f1_analysis.report import ReportGenerator


BASE_DIR = Path(__file__).resolve().parent

CLEANED_DATA_FILE = BASE_DIR / "03-Data_Cleaning" / "clean_data.csv"
EDA_OUTPUT_DIR = BASE_DIR / "04-EDA" / "outputs"
REPORT_OUTPUT_DIR = BASE_DIR / "05-Visualizations" / "outputs"


def main() -> None:
    """Execute the complete Formula 1 data analysis application."""

    print("\n========== DATA COLLECTION AND DATABASE ==========")
    run_pipeline()

    print("\n========== DATA CLEANING ==========")
    clean_data()

    print("\n========== EXPLORATORY DATA ANALYSIS ==========")
    run_eda(CLEANED_DATA_FILE, EDA_OUTPUT_DIR)

    print("\n========== VISUALIZATIONS AND REPORT ==========")
    cleaned_data = pd.read_csv(CLEANED_DATA_FILE, low_memory=False)

    report_generator = ReportGenerator(REPORT_OUTPUT_DIR)
    report_file = report_generator.generate(cleaned_data)

    print("\n========== APPLICATION COMPLETED ==========")
    print("Final PDF report:", report_file)


if __name__ == "__main__":
    main()
