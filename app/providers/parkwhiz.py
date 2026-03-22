from typing import Any

from app.providers.base import BaseProvider


class ParkWhizProvider(BaseProvider):
    """
    Mock ParkWhiz provider.

    TODO:
    Replace mocked responses with a real API integration once the endpoint,
    authentication requirements, and payload shape are confirmed.
    """

    provider_name = "parkwhiz"

    def fetch_quotes(
        self, airport_code: str, start_dt: str, end_dt: str
    ) -> list[dict[str, Any]]:
        """
        Return mocked ParkWhiz-style raw records for the given airport and time range.
        """
        airport_code = airport_code.upper()

        mock_data: dict[str, list[dict[str, Any]]] = {
            "ORD": [
                {
                    "listing_id": "pw_ord_1",
                    "quote_id": "pwq_ord_1",
                    "location_name": "Joes Airport Parking",
                    "address": "123 Main St",
                    "city": "Chicago",
                    "state": "IL",
                    "postal_code": "60666",
                    "lat": 41.9742,
                    "lng": -87.9073,
                    "currency": "USD",
                    "total_price": 24.99,
                },
                {
                    "listing_id": "pw_ord_2",
                    "quote_id": "pwq_ord_2",
                    "location_name": "Skyline Valet Garage",
                    "address": "500 Remote Rd",
                    "city": "Chicago",
                    "state": "IL",
                    "postal_code": "60666",
                    "lat": 41.9815,
                    "lng": -87.9012,
                    "currency": "USD",
                    "total_price": 31.50,
                },
                {
                    "listing_id": "pw_ord_3",
                    "quote_id": "pwq_ord_3",
                    "location_name": "Hotel Blue Self Park",
                    "address": "800 Traveler Ave",
                    "city": "Rosemont",
                    "state": "IL",
                    "postal_code": "60018",
                    "lat": 41.9931,
                    "lng": -87.8845,
                    "currency": "USD",
                    "total_price": 18.75,
                },
            ],
            "LAX": [
                {
                    "listing_id": "pw_lax_1",
                    "quote_id": "pwq_lax_1",
                    "location_name": "Sunset Airport Parking",
                    "address": "200 World Way Blvd",
                    "city": "Los Angeles",
                    "state": "CA",
                    "postal_code": "90045",
                    "lat": 33.9428,
                    "lng": -118.4085,
                    "currency": "USD",
                    "total_price": 27.00,
                },
                {
                    "listing_id": "pw_lax_2",
                    "quote_id": "pwq_lax_2",
                    "location_name": "Pacific Park and Fly",
                    "address": "900 Sepulveda Blvd",
                    "city": "Los Angeles",
                    "state": "CA",
                    "postal_code": "90045",
                    "lat": 33.9498,
                    "lng": -118.3961,
                    "currency": "USD",
                    "total_price": 34.25,
                },
                {
                    "listing_id": "pw_lax_3",
                    "quote_id": "pwq_lax_3",
                    "location_name": "Airport Center Garage",
                    "address": "615 Aviation Ave",
                    "city": "El Segundo",
                    "state": "CA",
                    "postal_code": "90245",
                    "lat": 33.9201,
                    "lng": -118.3875,
                    "currency": "USD",
                    "total_price": 19.95,
                },
            ],
        }

        return mock_data.get(airport_code, [])