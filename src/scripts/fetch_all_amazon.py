"""
Convenience script to fetch all cat food categories from Amazon API.

Fetches:
- 100 dry food products
- 100 wet food products
- 100 dessert/treat products

Usage:
    python -m src.scripts.fetch_all_amazon
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Fetch all cat food categories from Amazon API."""
    script_dir = Path(__file__).parent

    categories = [
        ("dry", "cat_food_dry_amazon.csv"),
        ("wet", "cat_food_wet_amazon.csv"),
        ("dessert", "cat_food_dessert_amazon.csv"),
    ]

    print("=" * 60)
    print("Amazon Product Advertising API - Fetch All Categories")
    print("=" * 60)
    print()

    all_files = []

    for food_type, output_file in categories:
        print(f"\n📦 Fetching {food_type} food products from Amazon...")
        print("-" * 60)

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "src.scripts.amazon_api_fetcher",
                    "--type",
                    food_type,
                    "--count",
                    "100",
                    "--output",
                    output_file,
                ],
                check=True,
                capture_output=False,  # Show output in real-time
            )
            all_files.append(output_file)
            print(f"✅ Successfully fetched {food_type} food products")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error fetching {food_type} food")
            print(f"   Exit code: {e.returncode}")
            continue
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
            break

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    if all_files:
        print(f"✅ Generated {len(all_files)} files:")
        for file in all_files:
            print(f"   - {file}")

        print("\n📝 To combine all files into one CSV:")
        print("   python -m src.scripts.combine_csv_files \\")
        print("     cat_food_dry_amazon.csv \\")
        print("     cat_food_wet_amazon.csv \\")
        print("     cat_food_dessert_amazon.csv \\")
        print("     --output cat_food_all_amazon.csv")
    else:
        print("❌ No files were generated. Please check your API credentials and try again.")


if __name__ == "__main__":
    main()
