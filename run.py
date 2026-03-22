import argparse

from app.db import Database
from app.export.exporter import (
    export_matched_lots,
    export_parking_lots,
    export_parking_quotes,
)
from app.normalize.facility import normalize_parking_lot
from app.normalize.quote import normalize_parking_quote
from app.providers.cheap_airport_parking import CheapAirportParkingProvider
from app.providers.parkwhiz import ParkWhizProvider
from app.providers.spothero import SpotHeroProvider
from app.matching.matcher import match_parking_lots


def get_providers():
    """
    Return all provider instances used by the pipeline.
    """
    return [
        ParkWhizProvider(),
        SpotHeroProvider(),
        CheapAirportParkingProvider(),
    ]


def run_fetch(db: Database, airports: list[str], start_dt: str, end_dt: str) -> None:
    """
    Fetch raw records from all providers, normalize them, and store them.
    """
    providers = get_providers()

    for airport_code in airports:
        airport_code = airport_code.upper()

        for provider in providers:
            raw_records = provider.fetch_quotes(airport_code, start_dt, end_dt)

            for raw_record in raw_records:
                lot = normalize_parking_lot(
                    provider=provider.provider_name,
                    raw_record=raw_record,
                    airport_code=airport_code,
                )
                quote = normalize_parking_quote(
                    provider=provider.provider_name,
                    raw_record=raw_record,
                    airport_code=airport_code,
                    start_dt=start_dt,
                    end_dt=end_dt,
                )

                db.upsert_parking_lot(lot)
                db.upsert_parking_quote(quote)

            print(
                f"Fetched {len(raw_records)} records from {provider.provider_name} for {airport_code}"
            )


def run_match(db: Database) -> None:
    """
    Load stored lots, run pairwise matching, and store match results.
    """
    parking_lots = db.fetch_all_parking_lots()
    matches = match_parking_lots(parking_lots)

    db.clear_matches()

    for match in matches:
        db.insert_matched_lot(match)

    print(f"Stored {len(matches)} match results")


def run_export(db: Database) -> None:
    """
    Export stored lots, quotes, and matches to JSON and CSV.
    """
    parking_lots = db.fetch_all_parking_lots()
    parking_quotes = db.fetch_all_parking_quotes()
    matched_lots = db.fetch_all_matches()

    lot_paths = export_parking_lots(parking_lots)
    quote_paths = export_parking_quotes(parking_quotes)
    match_paths = export_matched_lots(matched_lots)

    print("Exported parking lots to:")
    for path in lot_paths:
        print(f"  - {path}")

    print("Exported parking quotes to:")
    for path in quote_paths:
        print(f"  - {path}")

    print("Exported matched lots to:")
    for path in match_paths:
        print(f"  - {path}")


def build_parser() -> argparse.ArgumentParser:
    """
    Build the CLI parser. 
    """
    parser = argparse.ArgumentParser(
        description="Parking location quote matching pipeline"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_common_arguments(command_parser: argparse.ArgumentParser) -> None:
        command_parser.add_argument(
            "--db-path",
            default="parking_matching.db",
            help="Path to the SQLite database file",
        )

    fetch_parser = subparsers.add_parser(
        "fetch", help="Fetch provider data and store normalized records"
    )
    fetch_parser.add_argument(
        "--airports",
        nargs="+",
        required=True,
        help="Airport codes, e.g. ORD LAX",
    )
    fetch_parser.add_argument(
        "--start",
        required=True,
        help="Start datetime in ISO-like string format",
    )
    fetch_parser.add_argument(
        "--end",
        required=True,
        help="End datetime in ISO-like string format",
    )
    add_common_arguments(fetch_parser)

    match_parser = subparsers.add_parser(
        "match", help="Run matching using stored parking lots"
    )
    add_common_arguments(match_parser)

    export_parser = subparsers.add_parser(
        "export", help="Export stored records to JSON and CSV"
    )
    add_common_arguments(export_parser)

    pipeline_parser = subparsers.add_parser(
        "pipeline", help="Run fetch, match, and export in sequence"
    )
    pipeline_parser.add_argument(
        "--airports",
        nargs="+",
        required=True,
        help="Airport codes, e.g. ORD LAX",
    )
    pipeline_parser.add_argument(
        "--start",
        required=True,
        help="Start datetime in ISO-like string format",
    )
    pipeline_parser.add_argument(
        "--end",
        required=True,
        help="End datetime in ISO-like string format",
    )
    add_common_arguments(pipeline_parser)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    db = Database(args.db_path)
    db.create_tables()

    try:
        if args.command == "fetch":
            run_fetch(db, args.airports, args.start, args.end)

        elif args.command == "match":
            run_match(db)

        elif args.command == "export":
            run_export(db)

        elif args.command == "pipeline":
            run_fetch(db, args.airports, args.start, args.end)
            run_match(db)
            run_export(db)

    finally:
        db.close()


if __name__ == "__main__":
    main()