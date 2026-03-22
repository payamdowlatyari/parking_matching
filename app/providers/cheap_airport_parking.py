from typing import Any

from app.providers.base import BaseProvider


class CheapAirportParkingProvider(BaseProvider):
    """
    Mock Cheap Airport Parking provider.

    TODO:
    Replace mocked responses with a real API integration after discovering
    the public endpoint shape, request params, and any auth/session needs.
    """

    provider_name = "cheap_airport_parking"

    def fetch_quotes(
        self, airport_code: str, start_dt: str, end_dt: str
    ) -> list[dict[str, Any]]:
        """
        Return mocked Cheap Airport Parking-style raw records for the given
        airport and time range.
        """
        airport_code = airport_code.upper()

        mock_data: dict[str, list[dict[str, Any]]] = {
            "ORD": [
                {
                    "id": "cap_ord_1",
                    "quote_ref": "capq_ord_1",
                    "title": "Joes Apt Parking",
                    "address_1": "123 Main St.",
                    "city_name": "Chicago",
                    "state_code": "IL",
                    "zip_code": "60666",
                    "geo": {"lat": 41.9741, "lng": -87.9074},
                    "pricing": {"currency": "USD", "total": 24.50},
                },
                {
                    "id": "cap_ord_2",
                    "quote_ref": "capq_ord_2",
                    "title": "Skyline Valet Garage",
                    "address_1": "500 Remote Rd.",
                    "city_name": "Chicago",
                    "state_code": "IL",
                    "zip_code": "60666",
                    "geo": {"lat": 41.9816, "lng": -87.9013},
                    "pricing": {"currency": "USD", "total": 31.00},
                },
                {
                    "id": "cap_ord_3",
                    "quote_ref": "capq_ord_3",
                    "title": "Rosemont Hotel Parking",
                    "address_1": "810 Traveler Avenue",
                    "city_name": "Rosemont",
                    "state_code": "IL",
                    "zip_code": None,
                    "geo": {"lat": 41.9930, "lng": -87.8844},
                    "pricing": {"currency": "USD", "total": 19.25},
                },
            ],
            "LAX": [
                {
                    "id": "cap_lax_1",
                    "quote_ref": "capq_lax_1",
                    "title": "Sunset Apt Parking",
                    "address_1": "200 World Way Blvd.",
                    "city_name": "Los Angeles",
                    "state_code": "CA",
                    "zip_code": "90045",
                    "geo": {"lat": 33.9429, "lng": -118.4086},
                    "pricing": {"currency": "USD", "total": 26.75},
                },
                {
                    "id": "cap_lax_2",
                    "quote_ref": "capq_lax_2",
                    "title": "Pacific Park and Fly",
                    "address_1": "900 Sepulveda Blvd",
                    "city_name": "Los Angeles",
                    "state_code": "CA",
                    "zip_code": "90045",
                    "geo": {"lat": 33.9497, "lng": -118.3962},
                    "pricing": {"currency": "USD", "total": 34.10},
                },
                {
                    "id": "cap_lax_3",
                    "quote_ref": "capq_lax_3",
                    "title": "Marina Traveler Parking",
                    "address_1": "1200 Lincoln Blvd",
                    "city_name": "Santa Monica",
                    "state_code": "CA",
                    "zip_code": "90401",
                    "geo": {"lat": 34.0195, "lng": -118.4912},
                    "pricing": {"currency": "USD", "total": 15.75},
                },
            ],
        }

        return mock_data.get(airport_code, [])