"""SpotHero provider – returns placeholder data until a real API is wired."""

from app.models import ParkingLot
from app.providers.base import BaseProvider


class SpotHeroProvider(BaseProvider):
    name = "spothero"

    def fetch(self) -> list[ParkingLot]:
        """Return hardcoded sample lots (no live API call)."""
        return [
            ParkingLot(
                provider=self.name,
                lot_id="sh-001",
                name="SpotHero – Downtown Garage",
                address="123 Main Street",
                city="Chicago",
                state="IL",
                zip_code="60601",
                latitude=41.8782,
                longitude=-87.6297,
                price_per_day=22.00,
                amenities=["covered"],
            ),
            ParkingLot(
                provider=self.name,
                lot_id="sh-002",
                name="Midway Airport Parking – SpotHero",
                address="5700 S Cicero Ave",
                city="Chicago",
                state="IL",
                zip_code="60638",
                latitude=41.7868,
                longitude=-87.7522,
                price_per_day=12.00,
                amenities=["shuttle", "outdoor"],
            ),
        ]
