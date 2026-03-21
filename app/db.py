"""SQLite database helpers: connection, table creation, and CRUD utilities."""

import sqlite3
from contextlib import contextmanager
from typing import Generator

from app.config import DATABASE_URL
from app.models import NormalizedFacility


def get_connection(db_path: str = DATABASE_URL) -> sqlite3.Connection:
    """Return a new SQLite connection with row_factory set."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def managed_connection(db_path: str = DATABASE_URL) -> Generator[sqlite3.Connection, None, None]:
    """Context manager that yields a connection and commits/closes on exit."""
    conn = get_connection(db_path)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db(db_path: str = DATABASE_URL) -> None:
    """Create database tables if they do not already exist."""
    with managed_connection(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS facilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            provider TEXT NOT NULL,
            provider_facility_id TEXT NOT NULL,
            airport_code TEXT NOT NULL,
            facility_name TEXT NOT NULL,
            address1 TEXT,
            city TEXT,
            state TEXT,
            postal_code TEXT,
            latitude REAL,
            longitude REAL,
            raw_payload TEXT NOT NULL,
            UNIQUE(provider, provider_facility_id)
            );

            CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            provider TEXT NOT NULL,
            provider_quote_id TEXT NOT NULL,
            provider_facility_id TEXT NOT NULL,
            airport_code TEXT NOT NULL,
            start_utc TEXT NOT NULL,
            end_utc TEXT NOT NULL,
            currency TEXT,
            price_total REAL,
            raw_payload TEXT NOT NULL,
            UNIQUE(provider, provider_quote_id)
            );

            CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            facility_id INTEGER NOT NULL,
            quote_id INTEGER NOT NULL,
            FOREIGN KEY(facility_id) REFERENCES facilities(id),
            FOREIGN KEY(quote_id) REFERENCES quotes(id)
            );
            """
        )


def insert_parking_lot(conn: sqlite3.Connection, lot: NormalizedFacility) -> int:
    """Insert a NormalizedFacility row (or ignore if duplicate). Returns the row id."""
    cursor = conn.execute(
        """
        INSERT OR IGNORE INTO facilities
        (provider, provider_facility_id, airport_code, facility_name, address1, city, state, postal_code, latitude, longitude, raw_payload)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            lot.provider,
            lot.provider_facility_id,
            lot.airport_code,
            lot.facility_name,
            lot.address1,
            lot.city,
            lot.state,
            lot.postal_code,
            lot.latitude,
            lot.longitude,
            str(lot.raw_payload),
        ),
    )
    if cursor.lastrowid:
        return cursor.lastrowid
    # Row already existed – fetch existing id
    row = conn.execute(
        "SELECT id FROM facilities WHERE provider=? AND provider_facility_id=?",
        (lot.provider, lot.provider_facility_id),
    ).fetchone()
    return row["id"]
