"""ParkWhiz provider – returns placeholder data until a real API is wired."""

from app.models import ParkingLot
from app.providers.base import BaseProvider


class ParkWhizProvider(BaseProvider):
    name = "parkwhiz"

    def fetch(self) -> list[ParkingLot]:
        """Return hardcoded sample lots (no live API call)."""
        return [
            ParkingLot(
                provider=self.name,
                lot_id="pw-001",
                name="ParkWhiz Downtown Garage",
                address="123 Main St",
                city="Chicago",
                state="IL",
                zip_code="60601",
                latitude=41.8781,
                longitude=-87.6298,
                price_per_day=25.00,
                amenities=["covered", "24/7"],
            ),
            ParkingLot(
                provider=self.name,
                lot_id="pw-002",
                name="O'Hare Airport Parking – ParkWhiz",
                address="10000 W O'Hare Ave",
                city="Chicago",
                state="IL",
                zip_code="60666",
                latitude=41.9742,
                longitude=-87.9073,
                price_per_day=18.00,
                amenities=["shuttle", "outdoor"],
            ),
        ]
