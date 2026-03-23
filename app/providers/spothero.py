from typing import Any

from app.providers.base import BaseProvider


class SpotHeroProvider(BaseProvider):
    """
    Realistic SpotHero-style provider mock.

    SpotHero publicly advertises a developer platform / parking API, but public
    endpoint docs and response schemas are not exposed on the public developer page.
    These mocked records are shaped to resemble a marketplace search result with
    facility, pricing, amenities, and airport-travel attributes.
    """

    provider_name = "spothero"

    def fetch_quotes(
        self, airport_code: str, start_dt: str, end_dt: str
    ) -> list[dict[str, Any]]:
        airport_code = airport_code.upper()

        mock_data: dict[str, list[dict[str, Any]]] = {
            "ORD": [
                {
                    "facility_id": "sh_ord_1",
                    "rate_id": "shr_ord_1",
                    "facility_name": "Joes Airport Parking",
                    "street_address": "9420 River Street",
                    "municipality": "Schiller Park",
                    "region": "IL",
                    "zip": "60176",
                    "latitude": 41.9741,
                    "longitude": -87.8692,
                    "currency_code": "USD",
                    "price": 28.49,
                    "display_price": "$28.49",
                    "review_score": 4.6,
                    "review_count": 318,
                    "amenities": ["self_park", "shuttle", "covered_available"],
                    "shuttle_frequency_minutes": 15,
                    "distance_to_airport_miles": 2.4,
                    "is_refundable": True,
                    "inventory_status": "available",
                },
                {
                    "facility_id": "sh_ord_2",
                    "rate_id": "shr_ord_2",
                    "facility_name": "Skyline Valet",
                    "street_address": "10100 Mannheim Road",
                    "municipality": "Rosemont",
                    "region": "IL",
                    "zip": None,
                    "latitude": 41.9960,
                    "longitude": -87.8853,
                    "currency_code": "USD",
                    "price": 34.95,
                    "display_price": "$34.95",
                    "review_score": 4.4,
                    "review_count": 190,
                    "amenities": ["valet", "shuttle"],
                    "shuttle_frequency_minutes": 10,
                    "distance_to_airport_miles": 2.9,
                    "is_refundable": True,
                    "inventory_status": "available",
                },
                {
                    "facility_id": "sh_ord_3",
                    "rate_id": "shr_ord_3",
                    "facility_name": "River North Event Parking",
                    "street_address": "10 Arena Boulevard",
                    "municipality": "Chicago",
                    "region": "IL",
                    "zip": "60610",
                    "latitude": 41.9010,
                    "longitude": -87.6375,
                    "currency_code": "USD",
                    "price": 22.00,
                    "display_price": "$22.00",
                    "review_score": 4.1,
                    "review_count": 74,
                    "amenities": ["self_park"],
                    "shuttle_frequency_minutes": None,
                    "distance_to_airport_miles": 16.8,
                    "is_refundable": False,
                    "inventory_status": "available",
                },
            ],
            "LAX": [
                {
                    "facility_id": "sh_lax_1",
                    "rate_id": "shr_lax_1",
                    "facility_name": "Sunset Airport Parking",
                    "street_address": "6151 W Century Boulevard",
                    "municipality": "Los Angeles",
                    "region": "CA",
                    "zip": "90045",
                    "latitude": 33.9456,
                    "longitude": -118.3894,
                    "currency_code": "USD",
                    "price": 29.10,
                    "display_price": "$29.10",
                    "review_score": 4.7,
                    "review_count": 412,
                    "amenities": ["self_park", "shuttle", "ev_charging"],
                    "shuttle_frequency_minutes": 12,
                    "distance_to_airport_miles": 1.8,
                    "is_refundable": True,
                    "inventory_status": "available",
                },
                {
                    "facility_id": "sh_lax_2",
                    "rate_id": "shr_lax_2",
                    "facility_name": "Pacific Park & Fly",
                    "street_address": "5711 W Century Blvd",
                    "municipality": "Los Angeles",
                    "region": "CA",
                    "zip": "90045",
                    "latitude": 33.9462,
                    "longitude": -118.3835,
                    "currency_code": "USD",
                    "price": 35.95,
                    "display_price": "$35.95",
                    "review_score": 4.5,
                    "review_count": 265,
                    "amenities": ["self_park", "shuttle", "covered_available"],
                    "shuttle_frequency_minutes": 15,
                    "distance_to_airport_miles": 1.5,
                    "is_refundable": True,
                    "inventory_status": "available",
                },
                {
                    "facility_id": "sh_lax_3",
                    "rate_id": "shr_lax_3",
                    "facility_name": "Downtown LA Garage",
                    "street_address": "700 Flower St",
                    "municipality": "Los Angeles",
                    "region": "CA",
                    "zip": "90017",
                    "latitude": 34.0487,
                    "longitude": -118.2587,
                    "currency_code": "USD",
                    "price": 16.50,
                    "display_price": "$16.50",
                    "review_score": 4.0,
                    "review_count": 86,
                    "amenities": ["self_park"],
                    "shuttle_frequency_minutes": None,
                    "distance_to_airport_miles": 16.1,
                    "is_refundable": False,
                    "inventory_status": "available",
                },
            ],
        }

        return mock_data.get(airport_code, [])