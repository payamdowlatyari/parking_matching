import os
from dataclasses import dataclass


@dataclass
class Settings:
    parkwhiz_api_token: str | None
    parkwhiz_base_url: str


def get_settings() -> Settings:
    """
    Return a Settings object with the following environment variables populated:
    - PARKWHIZ_API_TOKEN: API token for ParkWhiz (required for real API calls)
    - PARKWHIZ_BASE_URL: Base URL for ParkWhiz API (default: https://api.parkwhiz.com/v4)
    """
    return Settings(
        parkwhiz_api_token=os.getenv("PARKWHIZ_API_TOKEN"),
        parkwhiz_base_url=os.getenv("PARKWHIZ_BASE_URL", "https://api.parkwhiz.com/v4"),
    )