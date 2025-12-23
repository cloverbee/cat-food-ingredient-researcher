"""
Cat Food Data Fetcher

This script fetches cat food product data from various sources.
Supports multiple platforms: Amazon, Chewy, Petco

IMPORTANT LEGAL NOTICE:
- Web scraping may violate Terms of Service of some websites
- Always check robots.txt and respect rate limits
- Consider using official APIs when available
- This script is for educational/research purposes

Usage:
    python -m src.scripts.fetch_cat_food_data --source amazon --type dry --count 100
    python -m src.scripts.fetch_cat_food_data --source chewy --type wet --count 100
    python -m src.scripts.fetch_cat_food_data --source all --type dessert --count 100
"""

import argparse
import csv
import json
import re
import time
from dataclasses import dataclass
from typing import List, Optional
from urllib.parse import quote_plus, urljoin

import requests
from bs4 import BeautifulSoup


@dataclass
class CatFoodProduct:
    """Data class for cat food product information."""

    name: str
    brand: str
    price: Optional[float] = None
    age_group: Optional[str] = None
    food_type: Optional[str] = None
    description: Optional[str] = None
    full_ingredient_list: Optional[str] = None
    url: Optional[str] = None


class BaseScraper:
    """Base class for cat food scrapers."""

    def __init__(self, delay: float = 2.0):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
            }
        )

    def fetch(self, query: str, food_type: str, count: int) -> List[CatFoodProduct]:
        """Fetch products based on query and food type."""
        raise NotImplementedError

    def parse_price(self, price_text: str) -> Optional[float]:
        """Extract numeric price from text."""
        if not price_text:
            return None
        # Remove currency symbols and extract numbers
        price_match = re.search(r"[\d,]+\.?\d*", price_text.replace(",", ""))
        if price_match:
            try:
                return float(price_match.group())
            except ValueError:
                return None
        return None

    def normalize_age_group(self, text: str) -> Optional[str]:
        """Normalize age group text to standard values."""
        if not text:
            return None
        text_lower = text.lower()
        if "kitten" in text_lower or "young" in text_lower:
            return "Kitten"
        elif "senior" in text_lower or "mature" in text_lower:
            return "Senior"
        elif "adult" in text_lower or "all life" in text_lower:
            return "Adult"
        return None

    def normalize_food_type(self, food_type: str) -> str:
        """Normalize food type."""
        food_type_lower = food_type.lower()
        if "dessert" in food_type_lower or "treat" in food_type_lower:
            return "Dessert"
        elif "wet" in food_type_lower or "canned" in food_type_lower:
            return "Wet"
        elif "dry" in food_type_lower or "kibble" in food_type_lower:
            return "Dry"
        return food_type.capitalize()

    def sleep(self):
        """Sleep to respect rate limits."""
        time.sleep(self.delay)


class AmazonScraper(BaseScraper):
    """Scraper for Amazon cat food products."""

    BASE_URL = "https://www.amazon.com"

    def fetch(self, query: str, food_type: str, count: int) -> List[CatFoodProduct]:
        """Fetch products from Amazon."""
        products = []
        search_query = f"cat {food_type} food"
        search_url = f"{self.BASE_URL}/s?k={quote_plus(search_query)}&i=pets"

        print(f"Fetching from Amazon: {search_query}")

        try:
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            # Amazon product containers
            product_divs = soup.find_all("div", {"data-component-type": "s-search-result"})

            for div in product_divs[:count]:
                try:
                    product = self._parse_product(div)
                    if product:
                        products.append(product)
                        if len(products) >= count:
                            break
                except Exception as e:
                    print(f"Error parsing product: {e}")
                    continue

                self.sleep()

        except Exception as e:
            print(f"Error fetching from Amazon: {e}")

        return products

    def _parse_product(self, div) -> Optional[CatFoodProduct]:
        """Parse a single product from Amazon search result."""
        # Product name
        name_elem = div.find("h2", class_="a-size-mini")
        if not name_elem:
            name_elem = div.find("h2")
        if not name_elem:
            return None

        name = name_elem.get_text(strip=True)

        # Brand (usually first word or in name)
        brand = name.split()[0] if name else "Unknown"

        # Price
        price_elem = div.find("span", class_="a-price-whole")
        price = None
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            price = self.parse_price(price_text)

        # URL
        link_elem = div.find("a", class_="a-link-normal")
        url = None
        if link_elem and link_elem.get("href"):
            url = urljoin(self.BASE_URL, link_elem["href"])

        # Description (limited in search results)
        description = None

        return CatFoodProduct(
            name=name,
            brand=brand,
            price=price,
            food_type=self.normalize_food_type("dry"),  # Will be set by caller
            description=description,
            url=url,
        )


class ChewyScraper(BaseScraper):
    """Scraper for Chewy cat food products."""

    BASE_URL = "https://www.chewy.com"

    def fetch(self, query: str, food_type: str, count: int) -> List[CatFoodProduct]:
        """Fetch products from Chewy."""
        products = []
        search_query = f"cat {food_type} food"
        search_url = f"{self.BASE_URL}/s?query={quote_plus(search_query)}"

        print(f"Fetching from Chewy: {search_query}")

        try:
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            # Chewy product containers
            product_divs = soup.find_all("article", class_="kib-product-card") or soup.find_all("div", class_="product")

            for div in product_divs[:count]:
                try:
                    product = self._parse_product(div)
                    if product:
                        products.append(product)
                        if len(products) >= count:
                            break
                except Exception as e:
                    print(f"Error parsing product: {e}")
                    continue

                self.sleep()

        except Exception as e:
            print(f"Error fetching from Chewy: {e}")

        return products

    def _parse_product(self, div) -> Optional[CatFoodProduct]:
        """Parse a single product from Chewy search result."""
        # Product name
        name_elem = div.find("h3") or div.find("a", class_="kib-product-title")
        if not name_elem:
            return None

        name = name_elem.get_text(strip=True)

        # Brand
        brand_elem = div.find("span", class_="kib-product-brand") or div.find("p", class_="brand")
        brand = brand_elem.get_text(strip=True) if brand_elem else name.split()[0]

        # Price
        price_elem = div.find("span", class_="kib-product-price") or div.find("span", class_="price")
        price = None
        if price_elem:
            price = self.parse_price(price_elem.get_text(strip=True))

        # URL
        link_elem = div.find("a")
        url = None
        if link_elem and link_elem.get("href"):
            url = urljoin(self.BASE_URL, link_elem["href"])

        return CatFoodProduct(
            name=name,
            brand=brand,
            price=price,
            food_type=self.normalize_food_type("dry"),  # Will be set by caller
            url=url,
        )


class PetcoScraper(BaseScraper):
    """Scraper for Petco cat food products."""

    BASE_URL = "https://www.petco.com"

    def fetch(self, query: str, food_type: str, count: int) -> List[CatFoodProduct]:
        """Fetch products from Petco."""
        products = []
        search_query = f"cat {food_type} food"
        search_url = f"{self.BASE_URL}/shop/en/petcostore/search/{quote_plus(search_query)}"

        print(f"Fetching from Petco: {search_query}")

        try:
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            # Petco product containers
            product_divs = soup.find_all("div", class_="product-tile") or soup.find_all("div", class_="product")

            for div in product_divs[:count]:
                try:
                    product = self._parse_product(div)
                    if product:
                        products.append(product)
                        if len(products) >= count:
                            break
                except Exception as e:
                    print(f"Error parsing product: {e}")
                    continue

                self.sleep()

        except Exception as e:
            print(f"Error fetching from Petco: {e}")

        return products

    def _parse_product(self, div) -> Optional[CatFoodProduct]:
        """Parse a single product from Petco search result."""
        # Product name
        name_elem = div.find("h3") or div.find("a", class_="product-name")
        if not name_elem:
            return None

        name = name_elem.get_text(strip=True)

        # Brand
        brand_elem = div.find("span", class_="brand") or div.find("p", class_="brand-name")
        brand = brand_elem.get_text(strip=True) if brand_elem else name.split()[0]

        # Price
        price_elem = div.find("span", class_="price") or div.find("div", class_="product-price")
        price = None
        if price_elem:
            price = self.parse_price(price_elem.get_text(strip=True))

        # URL
        link_elem = div.find("a")
        url = None
        if link_elem and link_elem.get("href"):
            url = urljoin(self.BASE_URL, link_elem["href"])

        return CatFoodProduct(
            name=name,
            brand=brand,
            price=price,
            food_type=self.normalize_food_type("dry"),  # Will be set by caller
            url=url,
        )


def save_to_csv(products: List[CatFoodProduct], filename: str):
    """Save products to CSV file."""
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["name", "brand", "price", "age_group", "food_type", "description", "full_ingredient_list"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for product in products:
            writer.writerow(
                {
                    "name": product.name,
                    "brand": product.brand,
                    "price": product.price or "",
                    "age_group": product.age_group or "",
                    "food_type": product.food_type or "",
                    "description": product.description or "",
                    "full_ingredient_list": product.full_ingredient_list or "",
                }
            )

    print(f"Saved {len(products)} products to {filename}")


def main():
    """Main function to fetch cat food data."""
    parser = argparse.ArgumentParser(description="Fetch cat food product data from various sources")
    parser.add_argument("--source", choices=["amazon", "chewy", "petco", "all"], default="amazon", help="Data source")
    parser.add_argument("--type", choices=["dry", "wet", "dessert"], required=True, help="Food type")
    parser.add_argument("--count", type=int, default=100, help="Number of products to fetch")
    parser.add_argument("--output", default="cat_food_data.csv", help="Output CSV filename")
    parser.add_argument("--delay", type=float, default=2.0, help="Delay between requests (seconds)")

    args = parser.parse_args()

    print("=" * 60)
    print("Cat Food Data Fetcher")
    print("=" * 60)
    print(f"Source: {args.source}")
    print(f"Type: {args.type}")
    print(f"Count: {args.count}")
    print("=" * 60)
    print("\n⚠️  LEGAL NOTICE:")
    print("Web scraping may violate Terms of Service.")
    print("Use responsibly and consider official APIs when available.")
    print("=" * 60)
    print()

    all_products = []

    sources = []
    if args.source == "all":
        sources = ["amazon", "chewy", "petco"]
    else:
        sources = [args.source]

    for source in sources:
        scraper = None
        if source == "amazon":
            scraper = AmazonScraper(delay=args.delay)
        elif source == "chewy":
            scraper = ChewyScraper(delay=args.delay)
        elif source == "petco":
            scraper = PetcoScraper(delay=args.delay)

        if scraper:
            products = scraper.fetch("cat food", args.type, args.count)
            # Set food type for all products
            for product in products:
                product.food_type = scraper.normalize_food_type(args.type)
            all_products.extend(products)
            print(f"Fetched {len(products)} products from {source}")

    if all_products:
        save_to_csv(all_products, args.output)
        print(f"\n✅ Successfully fetched {len(all_products)} products total")
    else:
        print("\n❌ No products were fetched. Please check your connection and try again.")


if __name__ == "__main__":
    main()
