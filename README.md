# parking_matching

A pipeline that aggregates parking-lot listings from multiple providers,
normalises the data, matches duplicate lots across providers, and exports
the results to CSV or JSON.

## Folder structure

```
parking_matching/
├── run.py                          # Pipeline entry-point
├── requirements.txt
├── .env.example                    # Copy to .env and set your values
├── app/
│   ├── config.py                   # Settings loaded from .env
│   ├── db.py                       # SQLite helpers + table init
│   ├── models.py                   # ParkingLot / MatchedLot dataclasses
│   ├── providers/
│   │   ├── base.py                 # Abstract BaseProvider
│   │   ├── parkwhiz.py             # ParkWhiz provider (placeholder)
│   │   ├── spothero.py             # SpotHero provider (placeholder)
│   │   └── cheap_airport_parking.py
│   ├── normalize/
│   │   └── text.py                 # Text normalisation helpers
│   ├── matching/
│   │   └── matcher.py              # Lot-matching / clustering logic
│   └── export/
│       └── exporter.py             # CSV / JSON export
└── tests/
    ├── test_text_normalization.py
    └── test_matching.py
```

## Quick start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. (Optional) configure environment
cp .env.example .env
# edit .env as needed

# 3. Run the pipeline
python run.py

# Export as JSON instead of CSV
python run.py --format json

# Custom output directory and database path
python run.py --output results --db my.db
```

## Running tests

```bash
pytest
```

## Architecture notes

- **Providers** fetch lot data (placeholder data now; real API calls in future steps).
- **Normalizer** cleans names and addresses for reliable comparison.
- **Matcher** clusters lots that represent the same physical location (same
  normalised address or geographic proximity within ~200 m).
- **Exporter** writes matched clusters to `output/matched_lots.{csv,json}`.
- All raw lots and match results are also persisted in a local SQLite database.