from app.db import Database

# import your existing functions
from run import run_fetch, run_match, run_export


def run_pipeline_service(
    airports,
    start,
    end,
    db_path="parking_matching.db",
):
    db = Database(db_path)
    db.create_tables()

    try:
        # Run existing pipeline steps
        run_fetch(db, airports, start, end)
        run_match(db)

        # Instead of relying only on export files,
        # return data directly for API response
        parking_lots = db.fetch_all_parking_lots()
        parking_quotes = db.fetch_all_parking_quotes()
        matches = db.fetch_all_matches()

        # Optional: still export files
        run_export(db)

        return {
            "airports": airports,
            "total_lots": len(parking_lots),
            "total_quotes": len(parking_quotes),
            "total_matches": len(matches),
            "matches": matches,  # already structured from DB
        }

    finally:
        db.close()