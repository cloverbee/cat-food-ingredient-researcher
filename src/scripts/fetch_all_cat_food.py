"""
Convenience script to fetch all cat food categories at once.

This script fetches:
- 100 dry food products
- 100 wet food products
- 100 dessert/treat products

Usage:
    python -m src.scripts.fetch_all_cat_food
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Fetch all cat food categories."""
    script_dir = Path(__file__).parent
    base_script = script_dir / "fetch_cat_food_data.py"

    categories = [
        ("dry", "cat_food_dry.csv"),
        ("wet", "cat_food_wet.csv"),
        ("dessert", "cat_food_dessert.csv"),
    ]

    print("=" * 60)
    print("Fetching All Cat Food Categories")
    print("=" * 60)
    print()

    all_files = []

    for food_type, output_file in categories:
        print(f"\n📦 Fetching {food_type} food products...")
        print("-" * 60)

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "src.scripts.fetch_cat_food_data",
                    "--source",
                    "amazon",
                    "--type",
                    food_type,
                    "--count",
                    "100",
                    "--output",
                    output_file,
                    "--delay",
                    "2.0",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            print(result.stdout)
            all_files.append(output_file)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error fetching {food_type} food: {e.stderr}")
            continue

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Generated files: {', '.join(all_files)}")
    print("\nTo combine all files into one CSV, you can use:")
    print("  python -m src.scripts.combine_csv_files")


if __name__ == "__main__":
    main()
