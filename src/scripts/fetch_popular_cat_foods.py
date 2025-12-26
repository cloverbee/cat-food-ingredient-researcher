"""
Fetch popular cat foods from:
- CatFoodDB blog list (best dry cat foods)
- Petco search results

Then:
- Merge + dedupe
- Write a CSV compatible with `src/scripts/reset_and_import.py`
- Optionally run the reset+import command

CSV header (required by importer):
name,brand,price,age_group,food_type,description,full_ingredient_list,image_url,shopping_url
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple
from urllib.parse import parse_qs, urljoin, urlparse, urlunparse

import requests
from bs4 import BeautifulSoup

from src.scripts.fetch_cat_food_data import PetcoScraper

CATFOODDB_DEFAULT_URL = "https://catfooddb.com/blog/best-dry-cat-foods"
CATFOODDB_DEFAULT_URLS = [
    "https://catfooddb.com/blog/best-dry-cat-foods",
    "https://catfooddb.com/blog/best-wet-cat-foods",
    "https://catfooddb.com/blog/best-cat-food-brands",
]


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


def _parse_catfooddb_jsonld_best_dry(html: str) -> List[Row]:
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
                        items.append(
                            Row(
                                name=name,
                                brand=brand or "Unknown",
                                food_type="Dry",
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


def _parse_catfooddb_best_dry_from_dom(html: str, *, page_url: str) -> List[Row]:
    """
    CatFoodDB best-dry page renders the product list as images under /img/products/.
    This parser extracts:
    - name from image alt
    - image_url from image src
    - shopping_url from nearest link (decoded from pn?url=... when applicable)
    """
    base_url = "{uri.scheme}://{uri.netloc}".format(uri=urlparse(page_url))
    soup = BeautifulSoup(html, "html.parser")

    imgs = soup.select('img[src*="/img/products/"], img[data-src*="/img/products/"]')
    rows: List[Row] = []
    seen: set = set()
    for img in imgs:
        name = _clean_str(img.get("alt"))
        if not name:
            continue
        src = _clean_str(img.get("src") or img.get("data-src"))
        image_url = urljoin(base_url, src) if src else None

        a = img.find_parent("a")
        shopping_url = _extract_outbound_url_from_catfooddb_href(a.get("href") if a else None, base_url)

        brand = _infer_brand_from_name(name) or "Unknown"
        key = (_normalize_brand_for_dedupe(brand), _normalize_name_for_dedupe(name), _canonical_url(shopping_url) or "")
        if key in seen:
            continue
        seen.add(key)

        rows.append(
            Row(
                name=name,
                brand=brand,
                food_type="Dry",
                image_url=image_url,
                shopping_url=shopping_url,
            )
        )

    return rows


def fetch_catfooddb_best_dry(*, url: str, count: int, timeout_s: int = 20) -> List[Row]:
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
    rows = _parse_catfooddb_jsonld_best_dry(resp.text)
    if not rows:
        rows = _parse_catfooddb_best_dry_from_dom(resp.text, page_url=url)
    return rows[:count]


def fetch_catfooddb_from_urls(*, urls: List[str], count: int) -> List[Row]:
    """
    CatFoodDB blog pages tend to list < 50 items each. This helper aggregates across multiple pages
    until it reaches `count`.
    """
    out: List[Row] = []
    seen: set = set()
    for u in urls:
        if len(out) >= count:
            break
        try:
            # The parser is DOM-based and works for several CatFoodDB blog list pages.
            rows = fetch_catfooddb_best_dry(url=u, count=count)
        except Exception as e:
            print(f"⚠️ CatFoodDB fetch failed for {u}: {e}")
            continue
        for r in rows:
            key = (_normalize_brand_for_dedupe(r.brand), _normalize_name_for_dedupe(r.name))
            if key in seen:
                continue
            seen.add(key)
            out.append(r)
            if len(out) >= count:
                break
    return out[:count]


def fetch_petco_dry(*, count: int, delay_s: float) -> List[Row]:
    scraper = PetcoScraper(delay=delay_s)
    products = scraper.fetch("cat food", "dry", count)
    rows: List[Row] = []
    for p in products:
        name = _clean_str(p.name)
        brand = _clean_str(p.brand) or "Unknown"
        if not name:
            continue
        rows.append(
            Row(
                name=name,
                brand=brand,
                price=p.price,
                age_group=p.age_group,
                food_type=p.food_type,
                description=p.description,
                full_ingredient_list=p.full_ingredient_list,
                image_url=p.image_url,
                shopping_url=p.shopping_url,
            )
        )
    return rows


def read_rows_from_csv(path: str, *, count: int) -> List[Row]:
    """
    Read an existing CSV (same schema as importer) into Rows.
    Useful as a fallback when a site blocks scraping (e.g. Petco/Chewy).
    """
    rows: List[Row] = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            name = _clean_str(raw.get("name"))
            if not name:
                continue
            brand = _clean_str(raw.get("brand")) or _infer_brand_from_name(name) or "Unknown"
            price_val = _clean_str(raw.get("price"))
            price: Optional[float] = None
            if price_val:
                try:
                    price = float(price_val)
                except Exception:
                    price = None
            rows.append(
                Row(
                    name=name,
                    brand=brand,
                    price=price,
                    age_group=_clean_str(raw.get("age_group")),
                    food_type=_clean_str(raw.get("food_type")),
                    description=_clean_str(raw.get("description")),
                    full_ingredient_list=_clean_str(raw.get("full_ingredient_list")),
                    image_url=_clean_str(raw.get("image_url")),
                    shopping_url=_clean_str(raw.get("shopping_url")),
                )
            )
            if len(rows) >= count:
                break
    return rows


def merge_and_dedupe(rows: Iterable[Tuple[str, Row]]) -> Tuple[List[Row], Dict[str, int]]:
    """
    Dedupe order:
    - Prefer rows with an image_url + shopping_url.
    - Otherwise keep first.
    """
    by_key: Dict[str, Tuple[str, Row]] = {}
    stats = {"input": 0, "kept": 0, "dropped": 0}

    for source, r in rows:
        stats["input"] += 1
        canon_url = _canonical_url(r.shopping_url) or ""
        dedupe_key = ""
        if canon_url:
            dedupe_key = f"url::{canon_url}"
        else:
            dedupe_key = f"name::{_normalize_brand_for_dedupe(r.brand)}::{_normalize_name_for_dedupe(r.name)}"

        existing = by_key.get(dedupe_key)
        if existing is None:
            by_key[dedupe_key] = (source, r)
            continue

        _existing_source, existing_row = existing
        existing_score = int(bool(_clean_str(existing_row.image_url))) + int(
            bool(_clean_str(existing_row.shopping_url))
        )
        new_score = int(bool(_clean_str(r.image_url))) + int(bool(_clean_str(r.shopping_url)))

        if new_score > existing_score:
            by_key[dedupe_key] = (source, r)

    merged = [pair[1] for pair in by_key.values()]
    stats["kept"] = len(merged)
    stats["dropped"] = stats["input"] - stats["kept"]
    return merged, stats


def write_csv(rows: List[Row], output_path: str) -> None:
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
                    "name": r.name,
                    "brand": r.brand or "Unknown",
                    "price": r.price or "",
                    "age_group": r.age_group or "",
                    "food_type": r.food_type or "",
                    "description": r.description or "",
                    "full_ingredient_list": r.full_ingredient_list or "",
                    "image_url": r.image_url or "",
                    "shopping_url": r.shopping_url or "",
                }
            )


def _parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Fetch + merge popular cat foods from CatFoodDB + Petco.")
    p.add_argument(
        "--catfooddb-url",
        action="append",
        default=[],
        help="CatFoodDB blog URL to pull products from (can be specified multiple times).",
    )
    p.add_argument("--catfooddb-count", type=int, default=50)
    p.add_argument("--second-source", choices=["petco", "csv", "rainforest_api"], default="petco")
    p.add_argument("--petco-count", type=int, default=50, help="Used when --second-source=petco")
    p.add_argument("--second-csv", default="cat_food_rainforest.csv", help="Used when --second-source=csv")
    p.add_argument("--delay", type=float, default=2.0, help="Delay between Petco requests (seconds).")
    p.add_argument("--output", default="cat_food_popular_merged.csv")
    p.add_argument(
        "--max-output",
        type=int,
        default=100,
        help="Maximum number of rows to write to the merged CSV (default: 100).",
    )
    p.add_argument(
        "--run-import",
        action="store_true",
        help="After generating CSV, run `python -m src.scripts.reset_and_import --yes --csv <output>`.",
    )
    p.add_argument(
        "--yes",
        action="store_true",
        help="Required when using --run-import (confirms deletion of local DB data).",
    )
    return p.parse_args(list(argv) if argv is not None else None)


def main(argv: Optional[Iterable[str]] = None) -> int:
    args = _parse_args(argv)

    catfooddb_urls = args.catfooddb_url or list(CATFOODDB_DEFAULT_URLS)
    catfooddb_rows = fetch_catfooddb_from_urls(urls=catfooddb_urls, count=args.catfooddb_count)
    if len(catfooddb_rows) < args.catfooddb_count:
        print(f"⚠️ CatFoodDB returned {len(catfooddb_rows)} rows (< {args.catfooddb_count}).")

    second_rows: List[Row] = []
    if args.second_source == "petco":
        second_rows = fetch_petco_dry(count=args.petco_count, delay_s=args.delay)
        if not second_rows:
            print("⚠️ Second source (Petco) returned 0 rows. This is often due to anti-bot protections (403).")
            # Auto-fallback to CSV if it exists
            try:
                second_rows = read_rows_from_csv(args.second_csv, count=args.petco_count)
                if second_rows:
                    print(f"✅ Fallback: loaded {len(second_rows)} rows from CSV: {args.second_csv}")
            except Exception:
                pass
            if not second_rows:
                print("   Tip: try `--second-source csv --second-csv cat_food_rainforest.csv` as a fallback.")
    elif args.second_source == "rainforest_api":
        # Uses existing script logic; requires RAINFOREST_API_KEY env var.
        try:
            from src.scripts.rainforest_api_fetcher import fetch_cat_food, get_api_key  # type: ignore

            api_key = get_api_key()
            products = fetch_cat_food(api_key, "dry", args.petco_count)
            second_rows = [
                Row(
                    name=_clean_str(p.get("name")) or "",
                    brand=_clean_str(p.get("brand")) or "Unknown",
                    price=p.get("price"),
                    age_group=_clean_str(p.get("age_group")),
                    food_type=_clean_str(p.get("food_type")),
                    description=_clean_str(p.get("description")),
                    full_ingredient_list=_clean_str(p.get("full_ingredient_list")),
                    image_url=_clean_str(p.get("image_url")),
                    shopping_url=_clean_str(p.get("shopping_url")),
                )
                for p in products
                if _clean_str(p.get("name"))
            ]
        except Exception as e:
            print(f"❌ Rainforest API fetch failed: {e}")
            print("   Tip: set RAINFOREST_API_KEY or use `--second-source csv` with an existing CSV.")
            second_rows = []
    else:
        second_rows = read_rows_from_csv(args.second_csv, count=args.petco_count)

    merged, stats = merge_and_dedupe(
        [("catfooddb", r) for r in catfooddb_rows] + [(args.second_source, r) for r in second_rows]
    )

    if args.max_output and len(merged) > args.max_output:

        def _row_score(rr: Row) -> int:
            return int(bool(_clean_str(rr.image_url))) + int(bool(_clean_str(rr.shopping_url)))

        merged = sorted(merged, key=_row_score, reverse=True)[: args.max_output]

    write_csv(merged, args.output)
    print(
        f"✅ Wrote {len(merged)} rows to {args.output} "
        f"(input={stats['input']} kept={stats['kept']} dropped={stats['dropped']})"
    )

    if args.run_import:
        if not args.yes:
            print("Refusing to run import without --yes (this will DELETE local data).")
            return 2
        cmd = [sys.executable, "-m", "src.scripts.reset_and_import", "--yes", "--csv", args.output]
        print(f"▶ Running: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
