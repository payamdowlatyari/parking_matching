"""Application configuration loaded from environment / .env file."""

import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL: str = os.getenv("DATABASE_URL", "parking.db")

PARKWHIZ_API_KEY: str = os.getenv("PARKWHIZ_API_KEY", "")
SPOTHERO_API_KEY: str = os.getenv("SPOTHERO_API_KEY", "")
CHEAP_AIRPORT_PARKING_API_KEY: str = os.getenv("CHEAP_AIRPORT_PARKING_API_KEY", "")

EXPORT_FORMAT: str = os.getenv("EXPORT_FORMAT", "csv")
EXPORT_PATH: str = os.getenv("EXPORT_PATH", "output")
