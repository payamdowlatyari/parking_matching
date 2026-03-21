"""CheapAirportParking provider – returns placeholder data until a real API is wired."""

from app.models import NormalizedFacility
from app.providers.base import BaseProvider


class CheapAirportParkingProvider(BaseProvider):
    name = "cheap_airport_parking"

    def fetch(self) -> list[NormalizedFacility]:
        """Return hardcoded sample lots (no live API call)."""
        return [
            NormalizedFacility(
                provider=self.name,
                provider_facility_id="cap-001",
                airport_code="ORD",
                facility_name="Midway Economy Lot",
                address1="5700 S. Cicero Avenue",
                city="Chicago",
                state="IL",
                postal_code="60638",
                latitude=41.7869,
                longitude=-87.7521,
                raw_payload={"price_per_day": 10.00, "amenities": ["shuttle", "outdoor"]},
            ),
            NormalizedFacility(
                provider=self.name,
                provider_facility_id="cap-002",
                airport_code="ORD",
                facility_name="Midway Valet Lot",
                address1="5700 S. Cicero Avenue",
                city="Chicago",
                state="IL",
                postal_code="60638",
                latitude=41.7869,
                longitude=-87.7521,
                raw_payload={"price_per_day": 20.00, "amenities": ["shuttle", "valet"]},
            ),
        ]
