import csv
import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any


OUTPUT_DIR = Path("data/output")


def _ensure_output_dir() -> None:
    """Create the output directory if it does not already exist."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _serialize_record(record: Any) -> dict[str, Any]:
    """
    Convert a dataclass instance into a JSON/CSV-friendly dictionary.
    """
    if is_dataclass(record):
        data = asdict(record)
    elif isinstance(record, dict):
        data = record
    else:
        raise TypeError(f"Unsupported record type: {type(record)}")

    return data


def _prepare_rows(records: list[Any]) -> list[dict[str, Any]]:
    """
    Convert records to dictionaries and JSON-encode nested dict/list values
    so they can be safely written to CSV.
    """
    rows: list[dict[str, Any]] = []

    for record in records:
        row = _serialize_record(record)
        normalized_row: dict[str, Any] = {}

        for key, value in row.items():
            if isinstance(value, (dict, list)):
                normalized_row[key] = json.dumps(value)
            else:
                normalized_row[key] = value

        rows.append(normalized_row)

    return rows


def export_json(records: list[Any], filename: str) -> Path:
    """
    Export records to a JSON file under data/output/.
    """
    _ensure_output_dir()
    output_path = OUTPUT_DIR / filename

    payload = [_serialize_record(record) for record in records]

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)

    return output_path


def export_csv(records: list[Any], filename: str) -> Path:
    """
    Export records to a CSV file under data/output/.
    """
    _ensure_output_dir()
    output_path = OUTPUT_DIR / filename

    rows = _prepare_rows(records)

    if not rows:
        with output_path.open("w", encoding="utf-8", newline="") as file:
            file.write("")
        return output_path

    fieldnames = list(rows[0].keys())

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return output_path


def export_parking_lots(parking_lots: list[Any]) -> tuple[Path, Path]:
    """
    Export parking lots to both JSON and CSV.
    """
    json_path = export_json(parking_lots, "parking_lots.json")
    csv_path = export_csv(parking_lots, "parking_lots.csv")
    return json_path, csv_path


def export_parking_quotes(parking_quotes: list[Any]) -> tuple[Path, Path]:
    """
    Export parking quotes to both JSON and CSV.
    """
    json_path = export_json(parking_quotes, "parking_quotes.json")
    csv_path = export_csv(parking_quotes, "parking_quotes.csv")
    return json_path, csv_path


def export_matched_lots(matched_lots: list[Any]) -> tuple[Path, Path]:
    """
    Export matched lots to both JSON and CSV.
    """
    json_path = export_json(matched_lots, "matched_lots.json")
    csv_path = export_csv(matched_lots, "matched_lots.csv")
    return json_path, csv_path