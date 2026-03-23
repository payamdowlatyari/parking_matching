from __future__ import annotations

from typing import Any

import requests

from app.config import get_settings
from app.providers.base import BaseProvider


class ParkWhizProvider(BaseProvider):
    """
    ParkWhiz provider.

    Real integration is attempted first using the documented v4 quotes endpoint.
    If configuration is missing or the request fails, this provider can fall
    back to mocked data for local development and take-home demo purposes.

    Docs used:
    - GET /quotes
    - GET /locations/{location_id}

    Notes:
    - ParkWhiz documents that /quotes requires an Authorization header.
    - The /quotes response is described as an array of Location models.
    - Payload shape may vary depending on token scope / response expansion, so
      field extraction is defensive.
    """

    provider_name = "parkwhiz"

    def __init__(self) -> None:
        self.settings = get_settings()

    def fetch_quotes(
        self, airport_code: str, start_dt: str, end_dt: str
    ) -> list[dict[str, Any]]:
        airport_code = airport_code.upper()

        try:
            real_records = self._fetch_quotes_real(airport_code, start_dt, end_dt)
            if real_records:
                return real_records
        except Exception as exc:
            print(f"[parkwhiz] Real API attempt failed for {airport_code}: {exc}")

        if self.settings.parkwhiz_use_mock_fallback:
            print(f"[parkwhiz] Using mock fallback for {airport_code}")
            return self._fetch_quotes_mock(airport_code, start_dt, end_dt)

        return []

    def _fetch_quotes_real(
        self, airport_code: str, start_dt: str, end_dt: str
    ) -> list[dict[str, Any]]:
        if not self.settings.parkwhiz_api_token:
            raise ValueError("PARKWHIZ_API_TOKEN is not set")

        url = f"{self.settings.parkwhiz_base_url}/quotes"

        # ParkWhiz documents a required q parameter. For this take-home,
        # airport code is used as a pragmatic query string starting point.
        params = {
            "q": airport_code,
            "start_time": start_dt,
            "end_time": end_dt,
            # Changelog notes option_types can return non-bookable price quotes.
            "option_types": "bookable,non_bookable",
        }

        headers = {
            "Authorization": f"Bearer {self.settings.parkwhiz_api_token}",
            "Accept": "application/json",
        }

        response = requests.get(url, params=params, headers=headers, timeout=20)
        if response.status_code != 200:
            raise RuntimeError(
                f"ParkWhiz quotes request failed: {response.status_code} {response.text[:300]}"
            )

        payload = response.json()

        if not isinstance(payload, list):
            raise RuntimeError(
                f"Unexpected ParkWhiz payload type: {type(payload).__name__}"
            )

        normalized_raw_records: list[dict[str, Any]] = []
        for item in payload:
            if not isinstance(item, dict):
                continue

            record = self._map_quote_location_to_internal_raw(item)
            if record is not None:
                normalized_raw_records.append(record)

        return normalized_raw_records

    def _map_quote_location_to_internal_raw(
        self, item: dict[str, Any]
    ) -> dict[str, Any] | None:
        """
        Convert a ParkWhiz API location/quote item into the raw record shape
        expected by app/normalize/facility.py and app/normalize/quote.py.

        This keeps downstream normalization logic unchanged.
        """
        location_id = item.get("location_id") or item.get("id")
        if location_id is None:
            return None

        quote_id = item.get("quote_id") or item.get("purchase_option_id") or f"pwq_{location_id}"

        address = (
            item.get("address1")
            or item.get("address")
            or item.get("street_address")
            or ""
        )

        city = item.get("city")
        state = item.get("state")
        postal_code = item.get("postal_code") or item.get("zip")

        lat = item.get("lat") or item.get("latitude")
        lng = item.get("lng") or item.get("longitude")

        # Price extraction is intentionally defensive because quote/location
        # payloads can differ depending on endpoint shape and expansions.
        total_price = None
        if isinstance(item.get("price"), (int, float)):
            total_price = item["price"]
        elif isinstance(item.get("total_price"), (int, float)):
            total_price = item["total_price"]
        elif isinstance(item.get("price"), dict):
            price_obj = item["price"]
            total_price = (
                price_obj.get("total")
                or price_obj.get("amount")
                or price_obj.get("value")
            )

        currency = "USD"
        if isinstance(item.get("price"), dict):
            currency = item["price"].get("currency", "USD")
        elif isinstance(item.get("currency"), str):
            currency = item["currency"]

        return {
            "listing_id": str(location_id),
            "quote_id": str(quote_id),
            "location_name": item.get("name") or item.get("location_name") or "",
            "address": address,
            "city": city,
            "state": state,
            "postal_code": postal_code,
            "lat": lat,
            "lng": lng,
            "currency": currency,
            "total_price": total_price,
            "source_payload_type": "parkwhiz_quotes",
            "raw_source": item,
        }

    def _fetch_quotes_mock(
        self, airport_code: str, start_dt: str, end_dt: str
    ) -> list[dict[str, Any]]:
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