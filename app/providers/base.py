from abc import ABC, abstractmethod
from typing import Any


class BaseProvider(ABC):
    """
    Abstract base class for parking data providers.
    """

    provider_name: str

    @abstractmethod
    def fetch_quotes(
        self, airport_code: str, start_dt: str, end_dt: str
    ) -> list[dict[str, Any]]:
        """
        Fetch raw parking quote/location records for an airport and time range.

        Returns provider-specific raw records. Normalization into the shared
        internal schema happens outside the provider class.
        """
        raise NotImplementedError