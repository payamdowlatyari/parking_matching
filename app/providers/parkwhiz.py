from __future__ import annotations

from typing import Any

import requests

from app.config import get_settings
from app.providers.base import BaseProvider


class ParkWhizProvider(BaseProvider):
    """
    ParkWhiz provider.

    Real integration is attempted first using the documented v4 quotes endpoint.
    If credentials are unavailable or the call fails, the provider falls back to
    realistic mocked records shaped to resemble ParkWhiz location/quote data.

    Notes from official docs:
    - v4 base URL is https://api.parkwhiz.com/v4
    - GET /quotes exists and requires authorization
    - GET /quotes supports option_types for bookable/non-bookable quotes
    """

    provider_name = "parkwhiz"

    def __init__(self) -> None:
        self.settings = get_settings()

    def fetch_quotes(
        self, airport_code: str, start_dt: str, end_dt: str
    ) -> list[dict[str, Any]]:
        airport_code = airport_code.upper()

        try:
            records = self._fetch_quotes_real(airport_code, start_dt, end_dt)
            if records:
                return records
        except Exception as exc:
            print(f"[parkwhiz] Real API attempt failed for {airport_code}: {exc}")

        if self.settings.parkwhiz_use_mock_fallback:
            print(f"[parkwhiz] Using mock fallback for {airport_code}")
            return self._fetch_quotes_mock(airport_code)

        return []

    def _fetch_quotes_real(
        self, airport_code: str, start_dt: str, end_dt: str
    ) -> list[dict[str, Any]]:
        if not self.settings.parkwhiz_api_token:
            raise ValueError("PARKWHIZ_API_TOKEN is not set")

        url = f"{self.settings.parkwhiz_base_url}/quotes"
        headers = {
            "Authorization": f"Bearer {self.settings.parkwhiz_api_token}",
            "Accept": "application/json",
        }
        params = {
            "q": airport_code,
            "start_time": start_dt,
            "end_time": end_dt,
            "option_types": "bookable,non_bookable",
        }

        response = requests.get(url, headers=headers, params=params, timeout=20)
        if response.status_code != 200:
            raise RuntimeError(
                f"ParkWhiz quotes request failed: {response.status_code} {response.text[:300]}"
            )

        payload = response.json()
        if not isinstance(payload, list):
            raise RuntimeError(
                f"Unexpected ParkWhiz payload type: {type(payload).__name__}"
            )

        results: list[dict[str, Any]] = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            mapped = self._map_quote_item(item)
            if mapped:
                results.append(mapped)

        return results

    def _map_quote_item(self, item: dict[str, Any]) -> dict[str, Any] | None:
        location_id = item.get("location_id") or item.get("id")
        if location_id is None:
            return None

        quote_id = (
            item.get("quote_id")
            or item.get("purchase_option_id")
            or f"pwq_{location_id}"
        )

        price_obj = item.get("price") if isinstance(item.get("price"), dict) else {}
        total_price = (
            price_obj.get("total")
            or item.get("total_price")
            or item.get("price")
            or item.get("price_total")
        )
        currency = price_obj.get("currency") or item.get("currency") or "USD"

        return {
            "listing_id": str(location_id),
            "quote_id": str(quote_id),
            "location_name": item.get("name") or item.get("location_name") or "",
            "address": (
                item.get("address1")
                or item.get("address")
                or item.get("street_address")
            ),
            "city": item.get("city"),
            "state": item.get("state"),
            "postal_code": item.get("postal_code") or item.get("zip"),
            "lat": item.get("lat") or item.get("latitude"),
            "lng": item.get("lng") or item.get("longitude"),
            "currency": currency,
            "total_price": total_price,
            "is_bookable": item.get("is_bookable"),
            "site_url": item.get("site_url"),
            "phone": item.get("phone"),
            "capacity": item.get("capacity"),
            "hours": item.get("hours"),
            "operating_hours": item.get("operating_hours"),
            "non_bookable_rates": item.get("non_bookable_rates"),
            "raw_source": item,
        }

    def _fetch_quotes_mock(self, airport_code: str) -> list[dict[str, Any]]:
        mock_data: dict[str, list[dict[str, Any]]] = {
            "ORD": [
                {
                    "listing_id": "pw_ord_1",
                    "quote_id": "pwq_ord_1",
                    "location_name": "Joe's Airport Parking",
                    "address": "9420 River St",
                    "city": "Schiller Park",
                    "state": "IL",
                    "postal_code": "60176",
                    "lat": 41.9739,
                    "lng": -87.8694,
                    "currency": "USD",
                    "total_price": 27.99,
                    "is_bookable": True,
                    "site_url": "https://www.parkwhiz.com/p/chicago-parking/joes-airport-parking/",
                    "phone": "(773) 555-0101",
                    "capacity": 180,
                    "hours": "24/7",
                    "operating_hours": {"open": "00:00", "close": "23:59"},
                    "non_bookable_rates": [],
                },
                {
                    "listing_id": "pw_ord_2",
                    "quote_id": "pwq_ord_2",
                    "location_name": "Skyline Valet Garage",
                    "address": "10100 Mannheim Rd",
                    "city": "Rosemont",
                    "state": "IL",
                    "postal_code": "60018",
                    "lat": 41.9962,
                    "lng": -87.8854,
                    "currency": "USD",
                    "total_price": 34.50,
                    "is_bookable": True,
                    "site_url": "https://www.parkwhiz.com/p/chicago-parking/skyline-valet-garage/",
                    "phone": "(773) 555-0102",
                    "capacity": 120,
                    "hours": "24/7",
                    "operating_hours": {"open": "00:00", "close": "23:59"},
                    "non_bookable_rates": [],
                },
                {
                    "listing_id": "pw_ord_3",
                    "quote_id": "pwq_ord_3",
                    "location_name": "Hotel Blue Self Park",
                    "address": "5440 N River Rd",
                    "city": "Rosemont",
                    "state": "IL",
                    "postal_code": "60018",
                    "lat": 41.9798,
                    "lng": -87.8621,
                    "currency": "USD",
                    "total_price": 21.25,
                    "is_bookable": True,
                    "site_url": "https://www.parkwhiz.com/p/chicago-parking/hotel-blue-self-park/",
                    "phone": "(773) 555-0103",
                    "capacity": 90,
                    "hours": "24/7",
                    "operating_hours": {"open": "00:00", "close": "23:59"},
                    "non_bookable_rates": [],
                },
            ],
            "LAX": [
                {
                    "listing_id": "pw_lax_1",
                    "quote_id": "pwq_lax_1",
                    "location_name": "Sunset Airport Parking",
                    "address": "6151 W Century Blvd",
                    "city": "Los Angeles",
                    "state": "CA",
                    "postal_code": "90045",
                    "lat": 33.9455,
                    "lng": -118.3895,
                    "currency": "USD",
                    "total_price": 28.75,
                    "is_bookable": True,
                    "site_url": "https://www.parkwhiz.com/p/los-angeles-parking/sunset-airport-parking/",
                    "phone": "(310) 555-0101",
                    "capacity": 260,
                    "hours": "24/7",
                    "operating_hours": {"open": "00:00", "close": "23:59"},
                    "non_bookable_rates": [],
                },
                {
                    "listing_id": "pw_lax_2",
                    "quote_id": "pwq_lax_2",
                    "location_name": "Pacific Park and Fly",
                    "address": "5711 W Century Blvd",
                    "city": "Los Angeles",
                    "state": "CA",
                    "postal_code": "90045",
                    "lat": 33.9461,
                    "lng": -118.3837,
                    "currency": "USD",
                    "total_price": 36.10,
                    "is_bookable": True,
                    "site_url": "https://www.parkwhiz.com/p/los-angeles-parking/pacific-park-and-fly/",
                    "phone": "(310) 555-0102",
                    "capacity": 200,
                    "hours": "24/7",
                    "operating_hours": {"open": "00:00", "close": "23:59"},
                    "non_bookable_rates": [],
                },
                {
                    "listing_id": "pw_lax_3",
                    "quote_id": "pwq_lax_3",
                    "location_name": "Airport Center Garage",
                    "address": "210 E Imperial Ave",
                    "city": "El Segundo",
                    "state": "CA",
                    "postal_code": "90245",
                    "lat": 33.9314,
                    "lng": -118.4018,
                    "currency": "USD",
                    "total_price": 22.40,
                    "is_bookable": True,
                    "site_url": "https://www.parkwhiz.com/p/los-angeles-parking/airport-center-garage/",
                    "phone": "(310) 555-0103",
                    "capacity": 110,
                    "hours": "24/7",
                    "operating_hours": {"open": "00:00", "close": "23:59"},
                    "non_bookable_rates": [],
                },
            ],
        }

        return mock_data.get(airport_code, [])