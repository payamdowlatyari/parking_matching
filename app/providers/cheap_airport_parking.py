"""CheapAirportParking provider – returns placeholder data until a real API is wired."""

from app.models import ParkingLot
from app.providers.base import BaseProvider


class CheapAirportParkingProvider(BaseProvider):
    name = "cheap_airport_parking"

    def fetch(self) -> list[ParkingLot]:
        """Return hardcoded sample lots (no live API call)."""
        return [
            ParkingLot(
                provider=self.name,
                lot_id="cap-001",
                name="O'Hare Airport Parking – Cheap Airport Parking",
                address="10000 W Ohare Ave",
                city="Chicago",
                state="IL",
                zip_code="60666",
                latitude=41.9741,
                longitude=-87.9074,
                price_per_day=15.00,
                amenities=["shuttle"],
            ),
            ParkingLot(
                provider=self.name,
                lot_id="cap-002",
                name="Midway Economy Lot",
                address="5700 S. Cicero Avenue",
                city="Chicago",
                state="IL",
                zip_code="60638",
                latitude=41.7869,
                longitude=-87.7521,
                price_per_day=10.00,
                amenities=["shuttle", "outdoor"],
            ),
        ]
