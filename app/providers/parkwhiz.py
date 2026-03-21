"""ParkWhiz provider – returns placeholder data until a real API is wired."""

from app.models import NormalizedFacility
from app.providers.base import BaseProvider


class ParkWhizProvider(BaseProvider):
    name = "parkwhiz"

    def fetch(self) -> list[NormalizedFacility]:
        """Return hardcoded sample lots (no live API call)."""
        return [
            NormalizedFacility(
                provider=self.name,
                provider_facility_id="pw-001",
                airport_code="ORD",
                facility_name="O'Hare Airport Parking – ParkWhiz",
                address1="10000 W O'Hare Ave",
                city="Chicago",
                state="IL",
                postal_code="60666",
                latitude=41.9742,
                longitude=-87.9073,
                raw_payload={"price_per_day": 15.00, "amenities": ["shuttle", "outdoor"]},
            ),
            NormalizedFacility(
                provider=self.name,
                provider_facility_id="pw-002",
                airport_code="ORD",
                facility_name="O'Hare Valet Parking – ParkWhiz",
                address1="10000 W O'Hare Ave",
                city="Chicago",
                state="IL",
                postal_code="60666",
                latitude=41.9742,
                longitude=-87.9073,
                raw_payload={"price_per_day": 25.00, "amenities": ["shuttle", "valet"]},
            ),
        ]
