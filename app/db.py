"""SQLite database helpers: connection, table creation, and CRUD utilities."""

import sqlite3
from contextlib import contextmanager
from typing import Generator

from app.config import DATABASE_URL
from app.models import ParkingLot


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
            CREATE TABLE IF NOT EXISTS parking_lots (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                provider    TEXT    NOT NULL,
                lot_id      TEXT    NOT NULL,
                name        TEXT    NOT NULL,
                address     TEXT    NOT NULL,
                city        TEXT    NOT NULL,
                state       TEXT    NOT NULL,
                zip_code    TEXT    NOT NULL,
                latitude    REAL,
                longitude   REAL,
                price_per_day REAL,
                amenities   TEXT,
                UNIQUE(provider, lot_id)
            );

            CREATE TABLE IF NOT EXISTS matched_lots (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                canonical_name   TEXT NOT NULL,
                canonical_address TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS matched_lot_entries (
                matched_lot_id  INTEGER NOT NULL REFERENCES matched_lots(id),
                parking_lot_id  INTEGER NOT NULL REFERENCES parking_lots(id),
                PRIMARY KEY (matched_lot_id, parking_lot_id)
            );
            """
        )


def insert_parking_lot(conn: sqlite3.Connection, lot: ParkingLot) -> int:
    """Insert a ParkingLot row (or ignore if duplicate). Returns the row id."""
    cursor = conn.execute(
        """
        INSERT OR IGNORE INTO parking_lots
            (provider, lot_id, name, address, city, state, zip_code,
             latitude, longitude, price_per_day, amenities)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            lot.provider,
            lot.lot_id,
            lot.name,
            lot.address,
            lot.city,
            lot.state,
            lot.zip_code,
            lot.latitude,
            lot.longitude,
            lot.price_per_day,
            ",".join(lot.amenities),
        ),
    )
    if cursor.lastrowid:
        return cursor.lastrowid
    # Row already existed – fetch existing id
    row = conn.execute(
        "SELECT id FROM parking_lots WHERE provider=? AND lot_id=?",
        (lot.provider, lot.lot_id),
    ).fetchone()
    return row["id"]
