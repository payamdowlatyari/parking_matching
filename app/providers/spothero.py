from typing import Any

from app.providers.base import BaseProvider


class SpotHeroProvider(BaseProvider):
    """
    Mock SpotHero provider.

    TODO:
    Replace mocked responses with a real API integration after confirming
    endpoint shape, auth requirements, and request parameters.
    """

    provider_name = "spothero"

    def fetch_quotes(
        self, airport_code: str, start_dt: str, end_dt: str
    ) -> list[dict[str, Any]]:
        """
        Return mocked SpotHero-style raw records for the given airport and time range.
        """
        airport_code = airport_code.upper()

        mock_data: dict[str, list[dict[str, Any]]] = {
            "ORD": [
                {
                    "facility_id": "sh_ord_1",
                    "rate_id": "shq_ord_1",
                    "facility_name": "Joe's Airport Parking",
                    "street_address": "123 Main Street",
                    "municipality": "Chicago",
                    "region": "IL",
                    "zip": "60666",
                    "latitude": 41.9743,
                    "longitude": -87.9071,
                    "currency_code": "USD",
                    "price": 25.49,
                },
                {
                    "facility_id": "sh_ord_2",
                    "rate_id": "shq_ord_2",
                    "facility_name": "Skyline Valet",
                    "street_address": "500 Remote Road",
                    "municipality": "Chicago",
                    "region": "IL",
                    "zip": None,
                    "latitude": 41.9813,
                    "longitude": -87.9010,
                    "currency_code": "USD",
                    "price": 30.99,
                },
                {
                    "facility_id": "sh_ord_3",
                    "rate_id": "shq_ord_3",
                    "facility_name": "River North Event Parking",
                    "street_address": "10 Arena Blvd",
                    "municipality": "Chicago",
                    "region": "IL",
                    "zip": "60610",
                    "latitude": 41.9010,
                    "longitude": -87.6375,
                    "currency_code": "USD",
                    "price": 22.00,
                },
            ],
            "LAX": [
                {
                    "facility_id": "sh_lax_1",
                    "rate_id": "shq_lax_1",
                    "facility_name": "Sunset Airport Parking",
                    "street_address": "200 World Way Boulevard",
                    "municipality": "Los Angeles",
                    "region": "CA",
                    "zip": "90045",
                    "latitude": 33.9427,
                    "longitude": -118.4083,
                    "currency_code": "USD",
                    "price": 27.50,
                },
                {
                    "facility_id": "sh_lax_2",
                    "rate_id": "shq_lax_2",
                    "facility_name": "Pacific Park & Fly",
                    "street_address": "900 Sepulveda Boulevard",
                    "municipality": "Los Angeles",
                    "region": "CA",
                    "zip": "90045",
                    "latitude": 33.9499,
                    "longitude": -118.3960,
                    "currency_code": "USD",
                    "price": 33.95,
                },
                {
                    "facility_id": "sh_lax_3",
                    "rate_id": "shq_lax_3",
                    "facility_name": "Downtown LA Garage",
                    "street_address": "700 Flower St",
                    "municipality": "Los Angeles",
                    "region": "CA",
                    "zip": "90017",
                    "latitude": 34.0487,
                    "longitude": -118.2587,
                    "currency_code": "USD",
                    "price": 16.50,
                },
            ],
        }

        return mock_data.get(airport_code, [])