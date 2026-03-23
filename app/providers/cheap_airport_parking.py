from typing import Any

from app.providers.base import BaseProvider


class CheapAirportParkingProvider(BaseProvider):
    """
    Realistic CheapAirportParking-style provider mock.

    CheapAirportParking's public site clearly exposes airport/date search, lot
    comparison, reviews, shuttle intervals, and parking-type distinctions, but
    not a public API. These mocked records reflect a plausible internal search
    result shape derived from that website behavior.
    """

    provider_name = "cheap_airport_parking"

    def fetch_quotes(
        self, airport_code: str, start_dt: str, end_dt: str
    ) -> list[dict[str, Any]]:
        airport_code = airport_code.upper()

        mock_data: dict[str, list[dict[str, Any]]] = {
            "ORD": [
                {
                    "id": "cap_ord_1",
                    "quote_ref": "capq_ord_1",
                    "title": "Joe's Airport Parking",
                    "address_1": "9420 River St.",
                    "city_name": "Schiller Park",
                    "state_code": "IL",
                    "zip_code": "60176",
                    "geo": {"lat": 41.9738, "lng": -87.8696},
                    "pricing": {
                        "currency": "USD",
                        "total": 27.50,
                        "display_total": "$27.50",
                        "daily_from": 9.95,
                    },
                    "lot_type": "self",
                    "parking_type": "outdoor",
                    "airport_shuttle": {
                        "included": True,
                        "frequency_minutes": 15,
                        "hours": "24/7",
                    },
                    "reviews": {"rating": 4.5, "count": 205},
                    "free_cancellation": True,
                },
                {
                    "id": "cap_ord_2",
                    "quote_ref": "capq_ord_2",
                    "title": "Skyline Valet Garage",
                    "address_1": "10100 Mannheim Rd.",
                    "city_name": "Rosemont",
                    "state_code": "IL",
                    "zip_code": "60018",
                    "geo": {"lat": 41.9963, "lng": -87.8852},
                    "pricing": {
                        "currency": "USD",
                        "total": 34.00,
                        "display_total": "$34.00",
                        "daily_from": 11.50,
                    },
                    "lot_type": "valet",
                    "parking_type": "indoor",
                    "airport_shuttle": {
                        "included": True,
                        "frequency_minutes": 10,
                        "hours": "24/7",
                    },
                    "reviews": {"rating": 4.3, "count": 121},
                    "free_cancellation": True,
                },
                {
                    "id": "cap_ord_3",
                    "quote_ref": "capq_ord_3",
                    "title": "Rosemont Hotel Parking",
                    "address_1": "5440 N River Road",
                    "city_name": "Rosemont",
                    "state_code": "IL",
                    "zip_code": None,
                    "geo": {"lat": 41.9799, "lng": -87.8620},
                    "pricing": {
                        "currency": "USD",
                        "total": 22.10,
                        "display_total": "$22.10",
                        "daily_from": 8.75,
                    },
                    "lot_type": "self",
                    "parking_type": "outdoor",
                    "airport_shuttle": {
                        "included": True,
                        "frequency_minutes": 20,
                        "hours": "24/7",
                    },
                    "reviews": {"rating": 4.1, "count": 88},
                    "free_cancellation": True,
                },
            ],
            "LAX": [
                {
                    "id": "cap_lax_1",
                    "quote_ref": "capq_lax_1",
                    "title": "Sunset Airport Parking",
                    "address_1": "6151 W Century Blvd.",
                    "city_name": "Los Angeles",
                    "state_code": "CA",
                    "zip_code": "90045",
                    "geo": {"lat": 33.9454, "lng": -118.3896},
                    "pricing": {
                        "currency": "USD",
                        "total": 28.25,
                        "display_total": "$28.25",
                        "daily_from": 8.95,
                    },
                    "lot_type": "self",
                    "parking_type": "outdoor",
                    "airport_shuttle": {
                        "included": True,
                        "frequency_minutes": 10,
                        "hours": "24/7",
                    },
                    "reviews": {"rating": 4.6, "count": 301},
                    "free_cancellation": True,
                },
                {
                    "id": "cap_lax_2",
                    "quote_ref": "capq_lax_2",
                    "title": "Pacific Park and Fly",
                    "address_1": "5711 W Century Boulevard",
                    "city_name": "Los Angeles",
                    "state_code": "CA",
                    "zip_code": "90045",
                    "geo": {"lat": 33.9460, "lng": -118.3838},
                    "pricing": {
                        "currency": "USD",
                        "total": 35.50,
                        "display_total": "$35.50",
                        "daily_from": 10.95,
                    },
                    "lot_type": "self",
                    "parking_type": "indoor",
                    "airport_shuttle": {
                        "included": True,
                        "frequency_minutes": 15,
                        "hours": "24/7",
                    },
                    "reviews": {"rating": 4.4, "count": 198},
                    "free_cancellation": True,
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
                    "pricing": {
                        "currency": "USD",
                        "total": 16.25,
                        "display_total": "$16.25",
                        "daily_from": 7.95,
                    },
                    "lot_type": "self",
                    "parking_type": "outdoor",
                    "airport_shuttle": {
                        "included": False,
                        "frequency_minutes": None,
                        "hours": None,
                    },
                    "reviews": {"rating": 3.9, "count": 42},
                    "free_cancellation": False,
                },
            ],
        }

        return mock_data.get(airport_code, [])