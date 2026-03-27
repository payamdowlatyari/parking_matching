from __future__ import annotations

from typing import Any

import requests

from app.providers.base import BaseProvider


class ParkWhizProvider(BaseProvider):
    """
    ParkWhiz provider.

    Uses the publicly reachable ParkWhiz v4 quotes endpoint discovered from the
    browser flow. This implementation intentionally avoids mock data and does
    not require an API token.

    Current working request shape:
    - GET https://api.parkwhiz.com/v4/quotes/
    - Required in practice: start_time, end_time, q
    - Helpful: returns=offstreet_bookable

    Notes:
    - This is based on the consumer web flow and may be subject to anonymous
      rate limiting or future changes.
    - Airport searches use a small amount of provider-specific metadata
      (bounds, anchor coordinates, venue_id) per airport.
    """

    provider_name = "parkwhiz"
    base_url = "https://api.parkwhiz.com/v4/quotes/"

    AIRPORT_SEARCH_PARAMS: dict[str, dict[str, Any]] = {
        "SFO": {
            "bounds": (
                37.63440138961927,
                -122.41387042820453,
                37.594401389619264,
                -122.37387042820454,
            ),
            "anchor_coordinates": (37.61440138961927, -122.39387042820454),
            "venue_id": 40,
        },
        "LAX": {
            "bounds": (
                33.9616,
                -118.4285,
                33.9216,
                -118.3885,
            ),
            "anchor_coordinates": (33.9416, -118.4085),
            "venue_id": 107,
        },
        "ORD": {
            "bounds": (
                42.0018,
                -87.9278,
                41.9618,
                -87.8878,
            ),
            "anchor_coordinates": (41.9818, -87.9078),
            "venue_id": 15,
        },
    }

    def fetch_quotes(
        self, airport_code: str, start_dt: str, end_dt: str
    ) -> list[dict[str, Any]]:
        airport_code = airport_code.upper()
        return self._fetch_quotes_real(airport_code, start_dt, end_dt)

    def _fetch_quotes_real(
        self, airport_code: str, start_dt: str, end_dt: str
    ) -> list[dict[str, Any]]:
        params = self.AIRPORT_SEARCH_PARAMS.get(airport_code)
        if not params:
            raise ValueError(f"Unsupported ParkWhiz airport code: {airport_code}")

        q = self._build_q(params)
        query_params = {
            "start_time": start_dt,
            "end_time": end_dt,
            "q": q,
            "returns": "offstreet_bookable",
        }

        response = requests.get(
            self.base_url,
            params=query_params,
            headers={"Accept": "application/json"},
            timeout=20,
        )
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

    def _build_q(self, params: dict[str, Any]) -> str:
        north, west, south, east = params["bounds"]
        anchor_lat, anchor_lng = params["anchor_coordinates"]
        venue_id = params["venue_id"]
        return (
            f"bounds:{north},{west},{south},{east} "
            f"anchor_coordinates:{anchor_lat},{anchor_lng} "
            f"venue_id:{venue_id}"
        )

    def _map_quote_item(self, item: dict[str, Any]) -> dict[str, Any] | None:
        embedded = item.get("_embedded", {}) if isinstance(item.get("_embedded"), dict) else {}
        location_obj = embedded.get("pw:location", {})
        if not isinstance(location_obj, dict):
            location_obj = {}

        purchase_options = item.get("purchase_options")
        primary_option = (
            purchase_options[0]
            if isinstance(purchase_options, list) and purchase_options and isinstance(purchase_options[0], dict)
            else {}
        )

        location_id = item.get("location_id") or location_obj.get("id") or item.get("id")
        if location_id is None:
            return None

        quote_id = (
            primary_option.get("id")
            or item.get("id")
            or item.get("quote_id")
            or item.get("purchase_option_id")
            or f"pwq_{location_id}"
        )

        price_obj = primary_option.get("price") if isinstance(primary_option.get("price"), dict) else {}
        base_price_obj = (
            primary_option.get("base_price")
            if isinstance(primary_option.get("base_price"), dict)
            else {}
        )
        total_price = (
            price_obj.get("USD")
            or primary_option.get("total_price")
            or item.get("total_price")
            or item.get("price_total")
        )
        base_price = base_price_obj.get("USD")

        def _to_float(value: Any) -> Any:
            if isinstance(value, str):
                try:
                    return float(value)
                except ValueError:
                    return value
            return value

        total_price = _to_float(total_price)
        base_price = _to_float(base_price)

        entrances = location_obj.get("entrances")
        entrance_coords = None
        if isinstance(entrances, list) and entrances and isinstance(entrances[0], dict):
            candidate = entrances[0].get("coordinates")
            if isinstance(candidate, list) and len(candidate) >= 2:
                entrance_coords = candidate

        lat = None
        lng = None
        if entrance_coords:
            lat = entrance_coords[0]
            lng = entrance_coords[1]
        elif isinstance(location_obj.get("coordinates"), dict):
            coords_obj = location_obj["coordinates"]
            lat = coords_obj.get("latitude")
            lng = coords_obj.get("longitude")
        else:
            lat = location_obj.get("lat") or item.get("lat")
            lng = location_obj.get("lng") or item.get("lng")

        cancellable_status = (
            primary_option.get("cancellable_status")
            if isinstance(primary_option.get("cancellable_status"), dict)
            else {}
        )
        space_availability = (
            primary_option.get("space_availability")
            if isinstance(primary_option.get("space_availability"), dict)
            else {}
        )

        return {
            "listing_id": str(location_id),
            "quote_id": str(quote_id),
            "location_name": location_obj.get("name") or item.get("name") or "",
            "address": location_obj.get("address1") or item.get("address1") or item.get("address"),
            "city": location_obj.get("city") or item.get("city"),
            "state": location_obj.get("state") or item.get("state"),
            "postal_code": location_obj.get("postal_code") or item.get("postal_code") or item.get("zip"),
            "lat": lat,
            "lng": lng,
            "currency": location_obj.get("currency") or "USD",
            "total_price": total_price,
            "base_price": base_price,
            "is_bookable": space_availability.get("status") == "available",
            "parking_type": primary_option.get("name"),
            "shuttle": primary_option.get("shuttle"),
            "cancellable": cancellable_status.get("cancellable_now"),
            "cancellation_code": cancellable_status.get("code"),
            "cancellation_message": cancellable_status.get("message"),
            "pickup_instructions": primary_option.get("pickup_instructions"),
            "dropoff_instructions": primary_option.get("dropoff_instructions"),
            "site_url": location_obj.get("site_url") or item.get("site_url"),
            "phone": location_obj.get("phone") or item.get("phone"),
            "capacity": location_obj.get("capacity") or item.get("capacity"),
            "hours": location_obj.get("hours") or item.get("hours"),
            "operating_hours": location_obj.get("operating_hours") or item.get("operating_hours"),
            "non_bookable_rates": item.get("non_bookable_rates"),
            "raw_source": item,
        }
