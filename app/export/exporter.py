"""Export matched parking lots to CSV or JSON."""

import csv
import json
import os
from pathlib import Path

from app.models import MatchedLot


def _lot_rows(matched_lots: list[MatchedLot]) -> list[dict]:
    rows = []
    for group in matched_lots:
        for entry in group.entries:
            rows.append(
                {
                    "canonical_name": group.canonical_name,
                    "canonical_address": group.canonical_address,
                    "provider": entry.provider,
                    "lot_id": entry.lot_id,
                    "name": entry.name,
                    "address": entry.address,
                    "city": entry.city,
                    "state": entry.state,
                    "zip_code": entry.zip_code,
                    "latitude": entry.latitude,
                    "longitude": entry.longitude,
                    "price_per_day": entry.price_per_day,
                    "amenities": "|".join(entry.amenities),
                }
            )
    return rows


def export_csv(matched_lots: list[MatchedLot], output_dir: str = "output") -> str:
    """Write matched lots to a CSV file and return the file path."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    path = os.path.join(output_dir, "matched_lots.csv")
    rows = _lot_rows(matched_lots)
    if not rows:
        return path
    fieldnames = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return path


def export_json(matched_lots: list[MatchedLot], output_dir: str = "output") -> str:
    """Write matched lots to a JSON file and return the file path."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    path = os.path.join(output_dir, "matched_lots.json")
    rows = _lot_rows(matched_lots)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2)
    return path


def export(matched_lots: list[MatchedLot], fmt: str = "csv", output_dir: str = "output") -> str:
    """Dispatch to the correct exporter based on *fmt*."""
    if fmt == "json":
        return export_json(matched_lots, output_dir)
    return export_csv(matched_lots, output_dir)
