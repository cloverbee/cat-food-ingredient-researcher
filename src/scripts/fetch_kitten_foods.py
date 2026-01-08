"""
Fetch the most popular 10 kitten cat foods from CatFoodDB.

This script fetches kitten-specific cat foods from:
- CatFoodDB blog: best-kitten-food page

Then writes a CSV compatible with the ingestion system.

CSV header (required by importer):
name,brand,price,age_group,food_type,description,full_ingredient_list,image_url,shopping_url
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass
from typing import List, Optional
from urllib.parse import parse_qs, urljoin, urlparse, urlunparse

import requests
from bs4 import BeautifulSoup

CATFOODDB_KITTEN_URL = "https://catfooddb.com/blog/best-kitten-food"


@dataclass(frozen=True)
class Row:
    name: str
    brand: str
    price: Optional[float] = None
    age_group: Optional[str] = None
    food_type: Optional[str] = None
    description: Optional[str] = None
    full_ingredient_list: Optional[str] = None
    image_url: Optional[str] = None
    shopping_url: Optional[str] = None


def _clean_str(val: Optional[str]) -> Optional[str]:
    if val is None:
        return None
    v = str(val).strip()
    if not v:
        return None
    v = re.sub(r"\s+", " ", v)
    return v


def _canonical_url(url: Optional[str]) -> Optional[str]:
    """Drop query+fragment, normalize host casing."""
    url = _clean_str(url)
    if not url:
        return None
    try:
        parsed = urlparse(url)
    except Exception:
        return url
    if not parsed.scheme or not parsed.netloc:
        return url
    # Keep scheme/host/path only (strip query/fragment)
    canon = parsed._replace(netloc=parsed.netloc.lower(), query="", fragment="")
    return urlunparse(canon)


_SIZE_RE = re.compile(
    r"\b(\d+(\.\d+)?)\s*(lb|lbs|pound|pounds|oz|ounce|ounces|kg|g|ct|count)\b",
    re.IGNORECASE,
)


def _normalize_name_for_dedupe(name: str) -> str:
    n = name.lower()
    n = re.sub(r"[^\w\s]", " ", n)
    n = _SIZE_RE.sub(" ", n)
    n = re.sub(r"\b(dry|wet|canned|kibble|cat|food|foods)\b", " ", n)
    n = re.sub(r"\s+", " ", n).strip()
    return n


def _normalize_brand_for_dedupe(brand: str) -> str:
    b = brand.lower()
    b = re.sub(r"[^\w\s]", " ", b)
    b = re.sub(r"\s+", " ", b).strip()
    return b


def _infer_brand_from_name(name: str) -> str:
    """
    CatFoodDB blog lists often contain brand in the product name but not split out.
    This is a heuristic only; importer requires `brand` to be non-empty.
    """
    n = _clean_str(name) or ""
    # "Brand: Product Name"
    if ":" in n:
        left = n.split(":", 1)[0].strip()
        if 1 <= len(left) <= 40:
            return left
    # "Brand - Product Name"
    if " - " in n:
        left = n.split(" - ", 1)[0].strip()
        if 1 <= len(left) <= 40:
            return left
    # Fallback: first token
    toks = [t for t in re.split(r"\s+", n) if t]
    if toks:
        return toks[0]
    return "Unknown"


def _infer_food_type_from_name(name: str) -> str:
    """Infer food type from product name."""
    n = _clean_str(name) or ""
    n_lower = n.lower()
    if "wet" in n_lower or "canned" in n_lower or "pate" in n_lower or "mousse" in n_lower or "pouch" in n_lower:
        return "Wet"
    elif "dry" in n_lower or "kibble" in n_lower:
        return "Dry"
    return "Wet"  # Default to wet for kitten foods


def _parse_catfooddb_jsonld_kitten(html: str) -> List[Row]:
    soup = BeautifulSoup(html, "html.parser")
    scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
    items: List[Row] = []

    def handle_item(obj: dict) -> None:
        # Common pattern: ItemList with itemListElement
        if obj.get("@type") == "ItemList" and isinstance(obj.get("itemListElement"), list):
            for el in obj["itemListElement"]:
                if isinstance(el, dict):
                    item = el.get("item") if isinstance(el.get("item"), dict) else el
                    name = _clean_str(item.get("name"))
                    url = _clean_str(item.get("url"))
                    image = item.get("image")
                    if isinstance(image, list) and image:
                        image_url = _clean_str(image[0])
                    else:
                        image_url = _clean_str(image)
                    desc = _clean_str(item.get("description"))
                    if name:
                        brand = _infer_brand_from_name(name)
                        food_type = _infer_food_type_from_name(name)
                        items.append(
                            Row(
                                name=name,
                                brand=brand or "Unknown",
                                age_group="Kitten",
                                food_type=food_type,
                                description=desc,
                                image_url=image_url,
                                shopping_url=url,
                            )
                        )

        # Some pages embed a list in mainEntity
        if isinstance(obj.get("mainEntity"), dict):
            handle_item(obj["mainEntity"])

    for s in scripts:
        raw = s.get_text(strip=True)
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except Exception:
            continue
        if isinstance(data, list):
            for el in data:
                if isinstance(el, dict):
                    handle_item(el)
        elif isinstance(data, dict):
            handle_item(data)

    return items


def _extract_outbound_url_from_catfooddb_href(href: Optional[str], base_url: str) -> Optional[str]:
    """
    CatFoodDB uses internal redirect links like:
      pn?url=https://www.chewy.com/...
    Prefer the decoded outbound url when present.
    """
    href = _clean_str(href)
    if not href:
        return None
    full = urljoin(base_url, href)
    parsed = urlparse(full)
    qs = parse_qs(parsed.query or "")
    for key in ("url", "u"):
        if key in qs and qs[key]:
            return _clean_str(qs[key][0])
    return full


def _parse_catfooddb_kitten_from_dom(html: str, *, page_url: str) -> List[Row]:
    """
    CatFoodDB best-kitten-food page renders the product list.
    This parser extracts:
    - name from image alt or product links
    - image_url from image src
    - shopping_url from nearest link (decoded from pn?url=... when applicable)
    """
    base_url = "{uri.scheme}://{uri.netloc}".format(uri=urlparse(page_url))
    soup = BeautifulSoup(html, "html.parser")

    rows: List[Row] = []
    seen: set = set()

    # Try to find product images
    imgs = soup.select('img[src*="/img/products/"], img[data-src*="/img/products/"]')
    for img in imgs:
        name = _clean_str(img.get("alt"))
        if not name:
            continue
        src = _clean_str(img.get("src") or img.get("data-src"))
        image_url = urljoin(base_url, src) if src else None

        a = img.find_parent("a")
        shopping_url = _extract_outbound_url_from_catfooddb_href(a.get("href") if a else None, base_url)

        brand = _infer_brand_from_name(name) or "Unknown"
        food_type = _infer_food_type_from_name(name)
        key = (_normalize_brand_for_dedupe(brand), _normalize_name_for_dedupe(name), _canonical_url(shopping_url) or "")
        if key in seen:
            continue
        seen.add(key)

        rows.append(
            Row(
                name=name,
                brand=brand,
                age_group="Kitten",
                food_type=food_type,
                image_url=image_url,
                shopping_url=shopping_url,
            )
        )

    # Also try to find product links/headings if images didn't work
    if not rows:
        # Look for product links or headings
        product_links = soup.select('a[href*="/product/"], h2, h3')
        for elem in product_links:
            name = _clean_str(elem.get_text())
            if not name or len(name) < 5:
                continue
            # Skip if it's clearly not a product name
            if name.lower() in ["best kitten food", "kitten food", "products", "related articles"]:
                continue

            href = elem.get("href") if elem.name == "a" else None
            shopping_url = _extract_outbound_url_from_catfooddb_href(href, base_url) if href else None

            # Try to find associated image
            img = elem.find("img") or (elem.find_parent() and elem.find_parent().find("img"))
            image_url = None
            if img:
                src = _clean_str(img.get("src") or img.get("data-src"))
                if src:
                    image_url = urljoin(base_url, src)

            brand = _infer_brand_from_name(name) or "Unknown"
            food_type = _infer_food_type_from_name(name)
            key = (
                _normalize_brand_for_dedupe(brand),
                _normalize_name_for_dedupe(name),
                _canonical_url(shopping_url) or "",
            )
            if key in seen:
                continue
            seen.add(key)

            rows.append(
                Row(
                    name=name,
                    brand=brand,
                    age_group="Kitten",
                    food_type=food_type,
                    image_url=image_url,
                    shopping_url=shopping_url,
                )
            )

    return rows


def fetch_catfooddb_kitten_foods(*, url: str, count: int, timeout_s: int = 20) -> List[Row]:
    """Fetch kitten foods from CatFoodDB."""
    resp = requests.get(
        url,
        timeout=timeout_s,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        },
    )
    resp.raise_for_status()
    rows = _parse_catfooddb_jsonld_kitten(resp.text)
    if not rows:
        rows = _parse_catfooddb_kitten_from_dom(resp.text, page_url=url)

    # Filter to ensure we only get kitten-related products
    filtered_rows = []
    for r in rows:
        name_lower = (r.name or "").lower()
        if (
            "kitten" in name_lower
            or "kitten" in (r.brand or "").lower()
            or (r.age_group and "kitten" in r.age_group.lower())
        ):
            filtered_rows.append(r)

    # If we don't have enough filtered results, include all rows (they're from kitten page anyway)
    if len(filtered_rows) < count:
        filtered_rows = rows

    return filtered_rows[:count]


def write_csv(rows: List[Row], output_path: str) -> None:
    """Write rows to CSV file."""
    fieldnames = [
        "name",
        "brand",
        "price",
        "age_group",
        "food_type",
        "description",
        "full_ingredient_list",
        "image_url",
        "shopping_url",
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(
                {
                    "name": r.name or "",
                    "brand": r.brand or "Unknown",
                    "price": r.price or "",
                    "age_group": r.age_group or "Kitten",
                    "food_type": r.food_type or "",
                    "description": r.description or "",
                    "full_ingredient_list": r.full_ingredient_list or "",
                    "image_url": r.image_url or "",
                    "shopping_url": r.shopping_url or "",
                }
            )


def _parse_args(argv: Optional[list] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Fetch popular kitten cat foods from CatFoodDB.")
    p.add_argument(
        "--url",
        default=CATFOODDB_KITTEN_URL,
        help=f"CatFoodDB kitten food page URL (default: {CATFOODDB_KITTEN_URL})",
    )
    p.add_argument("--count", type=int, default=10, help="Number of products to fetch (default: 10)")
    p.add_argument("--output", default="kitten_foods.csv", help="Output CSV filename (default: kitten_foods.csv)")
    return p.parse_args(list(argv) if argv is not None else None)


def main(argv: Optional[list] = None) -> int:
    args = _parse_args(argv)

    print("=" * 60)
    print("Fetching Popular Kitten Cat Foods")
    print("=" * 60)
    print("Source: CatFoodDB")
    print(f"URL: {args.url}")
    print(f"Count: {args.count}")
    print("=" * 60)
    print()

    try:
        rows = fetch_catfooddb_kitten_foods(url=args.url, count=args.count)

        if not rows:
            print("❌ No kitten foods found. The page structure may have changed.")
            return 1

        # Ensure all rows have age_group set to Kitten
        rows = [
            Row(
                name=r.name,
                brand=r.brand,
                price=r.price,
                age_group="Kitten",
                food_type=r.food_type,
                description=r.description,
                full_ingredient_list=r.full_ingredient_list,
                image_url=r.image_url,
                shopping_url=r.shopping_url,
            )
            for r in rows
        ]

        write_csv(rows, args.output)
        print(f"✅ Successfully fetched {len(rows)} kitten food products")
        print(f"✅ Saved to: {args.output}")
        print()
        print("Top kitten foods:")
        for i, row in enumerate(rows, 1):
            print(f"  {i}. {row.name} ({row.brand}) - {row.food_type or 'Unknown type'}")

        return 0
    except Exception as e:
        print(f"❌ Error fetching kitten foods: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
