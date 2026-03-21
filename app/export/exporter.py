"""Export matched parking lots to CSV or JSON."""

import csv
import json
import os
from pathlib import Path

from app.models import MatchedFacility


def export_json(matched_facility: list[MatchedFacility], output_dir: str = "output") -> str:
    """Write matched lots to a JSON file and return the file path."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_file = os.path.join(output_dir, "matched_lots.json")
    with open(output_file, "w") as f:
        json.dump(matched_facility, f, indent=2, separators=(",", ": "))
    return output_file


def export_csv(matched_facility: list[MatchedFacility], output_dir: str = "output") -> str:
    """Write matched lots to a CSV file and return the file path."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_file = os.path.join(output_dir, "matched_lots.csv")
    with open(output_file, "w") as f:
        writer = csv.DictWriter(f, fieldnames=MatchedFacility.__annotations__.keys())
        writer.writeheader()
        writer.writerows(matched_facility)
    return output_file


def export(matched_facility: list[MatchedFacility], fmt: str = "csv", output_dir: str = "output") -> str:
    """Dispatch to the correct exporter based on *fmt*."""
    if fmt == "json":
        return export_json(matched_facility, output_dir)
    return export_csv(matched_facility, output_dir)

