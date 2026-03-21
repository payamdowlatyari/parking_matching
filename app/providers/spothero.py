"""SpotHero provider – returns placeholder data until a real API is wired."""

from app.models import NormalizedFacility
from app.providers.base import BaseProvider


class SpotHeroProvider(BaseProvider):
    name = "spothero"

    def fetch(self) -> list[NormalizedFacility]:
        """Return hardcoded sample lots (no live API call)."""
        return [
            NormalizedFacility(
                provider=self.name,
                provider_facility_id="sh-001",
                airport_code="ORD",
                facility_name="SpotHero – Downtown Garage",
                address1="123 Main Street",
                city="Chicago",
                state="IL",
                postal_code="60601",
                latitude=41.8782,
                longitude=-87.6297,
                raw_payload={"price_per_day": 22.00, "amenities": ["covered"]},
            ),
            NormalizedFacility(
                provider=self.name,
                provider_facility_id="sh-002",
                airport_code="ORD",
                facility_name="Midway Airport Parking – SpotHero",
                address1="5700 S Cicero Ave",
                city="Chicago",
                state="IL",
                postal_code="60638",
                latitude=41.7868,
                longitude=-87.7522,
                raw_payload={"price_per_day": 12.00, "amenities": ["shuttle", "outdoor"]},
            ),
        ]
