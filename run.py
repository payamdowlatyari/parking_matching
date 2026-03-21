"""Pipeline entry-point.

Usage:
    python run.py [--format csv|json] [--output <dir>] [--db <path>]

Steps:
1. Initialise the SQLite database.
2. Fetch placeholder lots from all providers.
3. Persist raw lots to the database.
4. Run the matcher to group identical physical lots.
5. Export the results to CSV or JSON.
"""

import argparse
import sys

from app.config import DATABASE_URL, EXPORT_FORMAT, EXPORT_PATH
from app.db import init_db, insert_parking_lot, managed_connection
from app.export.exporter import export
from app.matching.matcher import match
from app.providers.cheap_airport_parking import CheapAirportParkingProvider
from app.providers.parkwhiz import ParkWhizProvider
from app.providers.spothero import SpotHeroProvider


def run(db_path: str = DATABASE_URL, fmt: str = EXPORT_FORMAT, output_dir: str = EXPORT_PATH) -> None:
    print(f"[1/5] Initialising database at '{db_path}' …")
    init_db(db_path)

    print("[2/5] Fetching lots from providers …")
    providers = [ParkWhizProvider(), SpotHeroProvider(), CheapAirportParkingProvider()]
    all_lots = []
    for provider in providers:
        lots = provider.fetch()
        print(f"      {provider.name}: {len(lots)} lot(s)")
        all_lots.extend(lots)

    print(f"[3/5] Persisting {len(all_lots)} raw lots to database …")
    with managed_connection(db_path) as conn:
        for lot in all_lots:
            insert_parking_lot(conn, lot)

    print("[4/5] Running matcher …")
    matched = match(all_lots)
    print(f"      {len(matched)} cluster(s) found from {len(all_lots)} lot(s)")

    print(f"[5/5] Exporting results as {fmt.upper()} to '{output_dir}/' …")
    path = export(matched, fmt=fmt, output_dir=output_dir)
    print(f"      Written to {path}")

    print("Done.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Parking lot matching pipeline")
    parser.add_argument("--format", default=EXPORT_FORMAT, choices=["csv", "json"], help="Export format")
    parser.add_argument("--output", default=EXPORT_PATH, help="Output directory")
    parser.add_argument("--db", default=DATABASE_URL, help="SQLite database path")
    args = parser.parse_args()

    run(db_path=args.db, fmt=args.format, output_dir=args.output)


if __name__ == "__main__":
    sys.exit(main())
