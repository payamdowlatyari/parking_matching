import json
import sqlite3
from pathlib import Path

from app.models import MatchedLot, ParkingLot, ParkingQuote


class Database:
    """
    Small SQLite helper for storing normalized parking lots, quotes, and matches.
    """
    def __init__(self, db_path: str = "parking_matching.db") -> None:
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def close(self) -> None:
        """Close the database connection."""
        self.conn.close()

    def create_tables(self) -> None:
        """Create all tables required for the project."""
        cursor = self.conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS parking_lots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider TEXT NOT NULL,
                provider_lot_id TEXT NOT NULL,
                airport_code TEXT NOT NULL,
                name TEXT NOT NULL,
                address1 TEXT,
                city TEXT,
                state TEXT,
                postal_code TEXT,
                latitude REAL,
                longitude REAL,
                raw_payload TEXT NOT NULL,
                UNIQUE(provider, provider_lot_id)
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS parking_quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider TEXT NOT NULL,
                provider_quote_id TEXT NOT NULL,
                provider_lot_id TEXT NOT NULL,
                airport_code TEXT NOT NULL,
                start_utc TEXT NOT NULL,
                end_utc TEXT NOT NULL,
                currency TEXT NOT NULL,
                price_total REAL,
                raw_payload TEXT NOT NULL,
                UNIQUE(provider, provider_quote_id)
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS matched_lots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                airport_code TEXT NOT NULL,
                left_provider TEXT NOT NULL,
                left_lot_id TEXT NOT NULL,
                right_provider TEXT NOT NULL,
                right_lot_id TEXT NOT NULL,
                score REAL NOT NULL,
                decision TEXT NOT NULL,
                reason TEXT NOT NULL
            )
            """
        )

        self.conn.commit()

    def upsert_parking_lot(self, lot: ParkingLot) -> None:
        """Insert or update a normalized parking lot."""
        self.conn.execute(
            """
            INSERT INTO parking_lots (
                provider,
                provider_lot_id,
                airport_code,
                name,
                address1,
                city,
                state,
                postal_code,
                latitude,
                longitude,
                raw_payload
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(provider, provider_lot_id)
            DO UPDATE SET
                airport_code = excluded.airport_code,
                name = excluded.name,
                address1 = excluded.address1,
                city = excluded.city,
                state = excluded.state,
                postal_code = excluded.postal_code,
                latitude = excluded.latitude,
                longitude = excluded.longitude,
                raw_payload = excluded.raw_payload
            """,
            (
                lot.provider,
                lot.provider_lot_id,
                lot.airport_code,
                lot.name,
                lot.address1,
                lot.city,
                lot.state,
                lot.postal_code,
                lot.latitude,
                lot.longitude,
                json.dumps(lot.raw_payload),
            ),
        )
        self.conn.commit()

    def upsert_parking_quote(self, quote: ParkingQuote) -> None:
        """Insert or update a normalized parking quote."""
        self.conn.execute(
            """
            INSERT INTO parking_quotes (
                provider,
                provider_quote_id,
                provider_lot_id,
                airport_code,
                start_utc,
                end_utc,
                currency,
                price_total,
                raw_payload
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(provider, provider_quote_id)
            DO UPDATE SET
                provider_lot_id = excluded.provider_lot_id,
                airport_code = excluded.airport_code,
                start_utc = excluded.start_utc,
                end_utc = excluded.end_utc,
                currency = excluded.currency,
                price_total = excluded.price_total,
                raw_payload = excluded.raw_payload
            """,
            (
                quote.provider,
                quote.provider_quote_id,
                quote.provider_lot_id,
                quote.airport_code,
                quote.start_utc,
                quote.end_utc,
                quote.currency,
                quote.price_total,
                json.dumps(quote.raw_payload),
            ),
        )
        self.conn.commit()

    def insert_matched_lot(self, match: MatchedLot) -> None:
        """Insert a parking lot match result."""
        self.conn.execute(
            """
            INSERT INTO matched_lots (
                airport_code,
                left_provider,
                left_lot_id,
                right_provider,
                right_lot_id,
                score,
                decision,
                reason
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                match.airport_code,
                match.left_provider,
                match.left_lot_id,
                match.right_provider,
                match.right_lot_id,
                match.score,
                match.decision,
                match.reason,
            ),
        )
        self.conn.commit()

    def clear_matches(self) -> None:
        """Remove all stored match results."""
        self.conn.execute("DELETE FROM matched_lots")
        self.conn.commit()

    def fetch_all_parking_lots(self) -> list[ParkingLot]:
        """Return all stored parking lots as dataclass instances."""
        rows = self.conn.execute("SELECT * FROM parking_lots").fetchall()
        return [self._row_to_parking_lot(row) for row in rows]

    def fetch_all_parking_quotes(self) -> list[ParkingQuote]:
        """Return all stored parking quotes as dataclass instances."""
        rows = self.conn.execute("SELECT * FROM parking_quotes").fetchall()
        return [self._row_to_parking_quote(row) for row in rows]

    def fetch_all_matches(self) -> list[MatchedLot]:
        """Return all stored match results as dataclass instances."""
        rows = self.conn.execute("SELECT * FROM matched_lots").fetchall()
        return [self._row_to_matched_lot(row) for row in rows]

    def fetch_parking_lots_by_airport(self, airport_code: str) -> list[ParkingLot]:
        """Return all stored parking lots for a specific airport."""
        rows = self.conn.execute(
            "SELECT * FROM parking_lots WHERE airport_code = ?",
            (airport_code,),
        ).fetchall()
        return [self._row_to_parking_lot(row) for row in rows]

    @staticmethod
    def _row_to_parking_lot(row: sqlite3.Row) -> ParkingLot:
        return ParkingLot(
            provider=row["provider"],
            provider_lot_id=row["provider_lot_id"],
            airport_code=row["airport_code"],
            name=row["name"],
            address1=row["address1"],
            city=row["city"],
            state=row["state"],
            postal_code=row["postal_code"],
            latitude=row["latitude"],
            longitude=row["longitude"],
            raw_payload=json.loads(row["raw_payload"]),
        )

    @staticmethod
    def _row_to_parking_quote(row: sqlite3.Row) -> ParkingQuote:
        return ParkingQuote(
            provider=row["provider"],
            provider_quote_id=row["provider_quote_id"],
            provider_lot_id=row["provider_lot_id"],
            airport_code=row["airport_code"],
            start_utc=row["start_utc"],
            end_utc=row["end_utc"],
            currency=row["currency"],
            price_total=row["price_total"],
            raw_payload=json.loads(row["raw_payload"]),
        )

    @staticmethod
    def _row_to_matched_lot(row: sqlite3.Row) -> MatchedLot:
        return MatchedLot(
            airport_code=row["airport_code"],
            left_provider=row["left_provider"],
            left_lot_id=row["left_lot_id"],
            right_provider=row["right_provider"],
            right_lot_id=row["right_lot_id"],
            score=row["score"],
            decision=row["decision"],
            reason=row["reason"],
        )