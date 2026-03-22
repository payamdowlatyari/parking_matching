"""Export matched parking lots to CSV or JSON."""

import csv
import json
import os
from pathlib import Path
from typing import Any

def _rows(matched_lots: list[Any]) -> list[dict]:
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


def export_csv(matched_facility: list[Any], output_dir: str = "output") -> str:
        """Write matched lots to a CSV file and return the file path."""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        path = os.path.join(output_dir, "matched_facility.csv")
        rows = _rows(matched_facility)
        with open(path, "w", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=rows[0].keys() if rows else [])
            writer.writeheader()
            writer.writerows(rows)
        return path


def export_json(matched_facility: list[Any], output_dir: str = "output") -> str:
    """Write matched lots to a JSON file and return the file path."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    path = os.path.join(output_dir, "matched_facility.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(matched_facility, fh, indent=2, separators=(",", ": "))
    return path


def export(matched_facility: list[Any], fmt: str = "csv", output_dir: str = "output") -> str:
    """Dispatch to the correct exporter based on *fmt*."""
    if fmt == "json":
        return export_json(matched_facility, output_dir)
    return export_csv(matched_facility, output_dir)

