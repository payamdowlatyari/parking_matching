"""Data models for parking lots and matched results."""

from dataclasses import dataclass
from typing import Any


@dataclass
class ParkingLot:
    """
    Normalized representation of a parking facility across providers.
    """
    provider: str
    provider_lot_id: str
    airport_code: str
    name: str
    address1: str | None
    city: str | None
    state: str | None
    postal_code: str | None
    latitude: float | None
    longitude: float | None
    raw_payload: dict[str, Any]


@dataclass
class ParkingQuote:
    """
    Normalized representation of a parking quote tied to a parking lot.
    """
    provider: str
    provider_quote_id: str
    provider_lot_id: str
    airport_code: str
    start_utc: str
    end_utc: str
    currency: str
    price_total: float | None
    raw_payload: dict[str, Any]


@dataclass
class MatchedLot:
    """
    Pairwise match result between two parking lots from different providers.
    """
    airport_code: str
    left_provider: str
    left_lot_id: str
    right_provider: str
    right_lot_id: str
    score: float
    decision: str
    reason: str
    