"""Generate the Formula 1 charts and PDF from a cleaned CSV."""

from argparse import ArgumentParser
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Read cleaned race results and run the standalone reporting stage."""
    # Direct script execution puts 05-Visualizations, rather than the repo, on sys.path.
    sys.path.insert(0, str(ROOT))
    from f1_analysis.report import ReportGenerator

    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", type=Path, default=ROOT / "03-Data_Cleaning" / "clean_data.csv",
        help="Path to the cleaned race results CSV.",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=Path(__file__).resolve().parent / "outputs",
        help="Directory for the PDF report and PNG charts.",
    )
    args = parser.parse_args()

    try:
        cleaned_data = pd.read_csv(args.input, low_memory=False)
    except FileNotFoundError:
        parser.exit(
            1, f"Cleaned CSV not found: {args.input}. Run 03-Data_Cleaning/clean_data.py "
            "or pass an existing file with --input.\n",
        )
    except (OSError, ValueError) as error:
        parser.exit(1, f"Could not read the cleaned CSV {args.input}: {error}\n")

    try:
        report = ReportGenerator(args.output_dir).generate(cleaned_data)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Report generation failed: {error}\n")

    print(f"Saved four PNG charts and {report.name} to {report.parent}")


if __name__ == "__main__":
    main()
