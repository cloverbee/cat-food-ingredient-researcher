"""
Delete cat food products from the database by matching URL fields.

Why:
- We don't currently store a "source" column (Rainforest vs. CatFoodDB vs. etc).
- The most reliable way to delete a specific imported batch is to match by URL(s).

Supports:
- Substring matching in `shopping_url` / `image_url` (e.g. "rainforest", "amazon.com")
- Exact URL matching from one or more CSV files (reads `shopping_url` and `image_url` columns if present)

Safe defaults:
- Always prints a preview (count + sample rows)
- Refuses to delete unless --yes is provided

Examples:
  # Preview products whose URLs contain "rainforest"
  python -m src.scripts.delete_products_by_url --contains rainforest

  # Delete products whose URLs contain "rainforest"
  python -m src.scripts.delete_products_by_url --contains rainforest --yes

  # Delete products whose shopping/image URLs appear in a CSV (e.g. cat_food_rainforest.csv)
  python -m src.scripts.delete_products_by_url --csv cat_food_rainforest.csv --yes
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import io
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Set

from sqlalchemy import delete, func, or_, select, text

from src.core.database import AsyncSessionLocal
from src.domain.models.product import CatFoodProduct, product_ingredient_association


@dataclass(frozen=True)
class _MatchConfig:
    match_shopping_url: bool
    match_image_url: bool


def _parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Delete cat food products by matching shopping/image URL fields.")
    p.add_argument(
        "--contains",
        action="append",
        default=[],
        help="Substring to match (case-insensitive). Can be provided multiple times.",
    )
    p.add_argument(
        "--csv",
        action="append",
        default=[],
        help="CSV file to read URL(s) from (uses columns shopping_url and/or image_url if present). Can repeat.",
    )
    p.add_argument(
        "--field",
        choices=["both", "shopping", "image"],
        default="both",
        help="Which URL field(s) to match against (default: both).",
    )
    p.add_argument(
        "--sample",
        type=int,
        default=20,
        help="How many matching rows to print as a preview (default: 20).",
    )
    p.add_argument(
        "--delete-orphan-ingredients",
        action="store_true",
        help="Also delete ingredients that are no longer referenced by any product after deletion.",
    )
    p.add_argument(
        "--yes",
        action="store_true",
        help="Actually perform deletion. Without this flag, the command only prints a preview.",
    )
    return p.parse_args(list(argv) if argv is not None else None)


def _match_config(field: str) -> _MatchConfig:
    if field == "shopping":
        return _MatchConfig(match_shopping_url=True, match_image_url=False)
    if field == "image":
        return _MatchConfig(match_shopping_url=False, match_image_url=True)
    return _MatchConfig(match_shopping_url=True, match_image_url=True)


def _read_urls_from_csv(path: Path) -> Set[str]:
    """
    Read URL candidates from a CSV file.

    If the CSV has `shopping_url` and/or `image_url` columns, we read them.
    Otherwise, we do a best-effort scan of all fields and collect values that look like URLs.
    """
    text_data = path.read_text(encoding="utf-8")
    reader = csv.DictReader(io.StringIO(text_data))
    urls: Set[str] = set()

    for row in reader:
        # Preferred columns if present
        for k in ("shopping_url", "image_url"):
            v = (row.get(k) or "").strip()
            if v:
                urls.add(v)

        if "shopping_url" in (reader.fieldnames or []) or "image_url" in (reader.fieldnames or []):
            continue

        # Fallback: scan all values for something URL-like
        for v in row.values():
            s = (v or "").strip()
            if s.startswith("http://") or s.startswith("https://"):
                urls.add(s)

    return urls


def _build_filter(*, contains: Sequence[str], urls: Sequence[str], cfg: _MatchConfig):
    clauses = []

    # Substring matches (case-insensitive)
    for raw in contains:
        needle = (raw or "").strip().lower()
        if not needle:
            continue
        like_val = f"%{needle}%"
        if cfg.match_shopping_url:
            clauses.append(func.lower(func.coalesce(CatFoodProduct.shopping_url, "")).like(like_val))
        if cfg.match_image_url:
            clauses.append(func.lower(func.coalesce(CatFoodProduct.image_url, "")).like(like_val))

    # Exact URL matches
    if urls:
        if cfg.match_shopping_url:
            clauses.append(CatFoodProduct.shopping_url.in_(list(urls)))
        if cfg.match_image_url:
            clauses.append(CatFoodProduct.image_url.in_(list(urls)))

    if not clauses:
        return None
    return or_(*clauses)


async def _fetch_matching_ids(where_clause) -> List[int]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(CatFoodProduct.id).where(where_clause))
        return [row[0] for row in result.all()]


async def _preview(where_clause, *, sample: int) -> int:
    async with AsyncSessionLocal() as session:
        count_result = await session.execute(select(func.count()).select_from(CatFoodProduct).where(where_clause))
        total = int(count_result.scalar() or 0)

        if total == 0:
            print("Matched 0 products.")
            return 0

        print(f"Matched {total} products. Showing up to {sample} sample rows:\n")
        sample_stmt = (
            select(
                CatFoodProduct.id,
                CatFoodProduct.brand,
                CatFoodProduct.name,
                CatFoodProduct.shopping_url,
                CatFoodProduct.image_url,
            )
            .where(where_clause)
            .order_by(CatFoodProduct.id.asc())
            .limit(sample)
        )
        rows = (await session.execute(sample_stmt)).all()
        for r in rows:
            print(f"- id={r.id} brand={r.brand!r} name={r.name!r}")
            print(f"  shopping_url={r.shopping_url!r}")
            print(f"  image_url={r.image_url!r}")
        print("")
        return total


async def _delete_by_ids(
    ids: Sequence[int],
    *,
    delete_orphan_ingredients: bool,
) -> None:
    if not ids:
        print("Nothing to delete.")
        return

    async with AsyncSessionLocal() as session:
        # Order matters due to FK constraints
        await session.execute(
            delete(product_ingredient_association).where(product_ingredient_association.c.product_id.in_(list(ids)))
        )
        await session.execute(delete(CatFoodProduct).where(CatFoodProduct.id.in_(list(ids))))

        if delete_orphan_ingredients:
            # Remove any ingredients with no remaining associations.
            await session.execute(
                text(
                    """
                    DELETE FROM ingredient i
                    WHERE NOT EXISTS (
                      SELECT 1
                      FROM product_ingredient_association pia
                      WHERE pia.ingredient_id = i.id
                    )
                    """
                )
            )

        await session.commit()


async def main(argv: Optional[Iterable[str]] = None) -> int:
    args = _parse_args(argv)
    cfg = _match_config(args.field)

    csv_urls: Set[str] = set()
    for csv_path in args.csv:
        path = Path(csv_path).expanduser().resolve()
        if not path.exists():
            print(f"CSV not found: {path}")
            return 2
        csv_urls |= _read_urls_from_csv(path)

    where_clause = _build_filter(contains=args.contains, urls=sorted(csv_urls), cfg=cfg)
    if where_clause is None:
        print("No match criteria provided. Use --contains and/or --csv.")
        return 2

    await _preview(where_clause, sample=args.sample)

    if not args.yes:
        print("Refusing to delete without --yes. Re-run with --yes to apply.")
        return 2

    ids = await _fetch_matching_ids(where_clause)
    await _delete_by_ids(ids, delete_orphan_ingredients=args.delete_orphan_ingredients)
    print(f"✅ Deleted {len(ids)} products.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
