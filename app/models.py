"""Data models for parking lots and matched results."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ParkingLot:
    """Represents a single parking lot entry from a provider."""

    provider: str
    lot_id: str
    name: str
    address: str
    city: str
    state: str
    zip_code: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    price_per_day: Optional[float] = None
    amenities: list[str] = field(default_factory=list)


@dataclass
class MatchedLot:
    """A group of ParkingLot entries that refer to the same physical lot."""

    canonical_name: str
    canonical_address: str
    entries: list[ParkingLot] = field(default_factory=list)
