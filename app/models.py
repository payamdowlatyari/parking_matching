"""Data models for parking lots and matched results."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class NormalizedFacility:
    provider: str
    provider_facility_id: str
    airport_code: str
    facility_name: str
    address1: Optional[str]
    city: Optional[str]
    state: Optional[str]
    postal_code: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    raw_payload: dict


@dataclass
class NormalizedQuote:
    provider: str
    provider_quote_id: str
    provider_facility_id: str
    airport_code: str
    start_utc: str
    end_utc: str
    currency: str
    price_total: Optional[float]
    raw_payload: dict


@dataclass
class MatchedFacility:
    canonical_name: str
    canonical_address: str
    entries: list[NormalizedFacility] = field(default_factory=list)
    