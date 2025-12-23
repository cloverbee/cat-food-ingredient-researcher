"""
Combine multiple CSV files into one.

Usage:
    python -m src.scripts.combine_csv_files cat_food_dry.csv cat_food_wet.csv cat_food_dessert.csv --output combined.csv
"""

import argparse
import csv
from pathlib import Path


def combine_csv_files(input_files: list, output_file: str):
    """Combine multiple CSV files into one."""
    all_rows = []
    fieldnames = None

    for input_file in input_files:
        file_path = Path(input_file)
        if not file_path.exists():
            print(f"⚠️  Warning: {input_file} not found, skipping...")
            continue

        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if fieldnames is None:
                fieldnames = reader.fieldnames
            elif reader.fieldnames != fieldnames:
                print(f"⚠️  Warning: {input_file} has different columns, skipping...")
                continue

            for row in reader:
                all_rows.append(row)

        print(f"✅ Added {len([r for r in all_rows if r])} rows from {input_file}")

    if not all_rows:
        print("❌ No data to combine")
        return

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\n✅ Combined {len(all_rows)} rows into {output_file}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Combine multiple CSV files")
    parser.add_argument("input_files", nargs="+", help="Input CSV files to combine")
    parser.add_argument("--output", default="cat_food_combined.csv", help="Output CSV filename")

    args = parser.parse_args()
    combine_csv_files(args.input_files, args.output)


if __name__ == "__main__":
    main()
