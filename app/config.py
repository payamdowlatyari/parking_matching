import os
from dataclasses import dataclass


@dataclass
class Settings:
    parkwhiz_api_token: str | None
    parkwhiz_base_url: str
    parkwhiz_use_mock_fallback: bool


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def get_settings() -> Settings:
    """
    Return a Settings object with the following environment variables populated:
    - PARKWHIZ_API_TOKEN: API token for ParkWhiz (required for real API calls)
    - PARKWHIZ_BASE_URL: Base URL for ParkWhiz API (default: https://api.parkwhiz.com/v4)
    - PARKWHIZ_USE_MOCK_FALLBACK: Use mock data for local development (default: True)
    """
    return Settings(
        parkwhiz_api_token=os.getenv("PARKWHIZ_API_TOKEN"),
        parkwhiz_base_url=os.getenv("PARKWHIZ_BASE_URL", "https://api.parkwhiz.com/v4"),
        parkwhiz_use_mock_fallback=_get_bool("PARKWHIZ_USE_MOCK_FALLBACK", True),
    )