"""
Generate mock data for all cat food categories.

Usage:
    python -m src.scripts.generate_all_mock_data
"""

import subprocess
import sys

categories = [
    ("dry", "cat_food_dry_mock.csv"),
    ("wet", "cat_food_wet_mock.csv"),
    ("dessert", "cat_food_dessert_mock.csv"),
]

print("=" * 60)
print("Generating Mock Cat Food Data")
print("=" * 60)
print()

for food_type, output_file in categories:
    print(f"📦 Generating {food_type} food products...")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "src.scripts.generate_mock_cat_food_data",
            "--type",
            food_type,
            "--count",
            "100",
            "--output",
            output_file,
        ],
        check=True,
    )

print("\n" + "=" * 60)
print("✅ All mock data generated!")
print("=" * 60)
print("\nFiles created:")
for _, output_file in categories:
    print(f"  - {output_file}")
