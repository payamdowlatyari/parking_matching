"""Abstract base class that every parking provider must implement."""

from abc import ABC, abstractmethod

from app.models import NormalizedFacility


class BaseProvider(ABC):
    """Fetch and return a list of ParkingLot records."""

    name: str = "base"

    @abstractmethod
    def fetch(self) -> list[NormalizedFacility]:
        """Return parking lots from this provider."""
