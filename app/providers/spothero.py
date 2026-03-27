from typing import Any

import requests

from app.providers.base import BaseProvider


class SpotHeroProvider(BaseProvider):
    """
    SpotHero provider using the public airport search endpoint discovered from
    the browser flow.

    Working request shape:
    GET https://api.spothero.com/v2/search/airport
      ?iata=SFO
      &starts=2026-03-28T12:00:00
      &ends=2026-04-01T12:00:00
      &oversize=false
      &show_unavailable=false
    """

    provider_name = "spothero"
    base_url = "https://api.spothero.com/v2/search/airport"

    def fetch_quotes(
        self, airport_code: str, start_dt: str, end_dt: str
    ) -> list[dict[str, Any]]:
        airport_code = airport_code.upper()
        return self._fetch_quotes_real(airport_code, start_dt, end_dt)

    def _fetch_quotes_real(
        self, airport_code: str, start_dt: str, end_dt: str
    ) -> list[dict[str, Any]]:
        params = {
            "iata": airport_code,
            "starts": start_dt,
            "ends": end_dt,
            "oversize": "false",
            "show_unavailable": "false",
        }

        response = requests.get(
            self.base_url,
            params=params,
            headers={"Accept": "application/json"},
            timeout=20,
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"SpotHero airport search failed: {response.status_code} {response.text[:300]}"
            )

        payload = response.json()
        if not isinstance(payload, dict):
            raise RuntimeError(
                f"Unexpected SpotHero payload type: {type(payload).__name__}"
            )

        results = payload.get("results", [])
        if not isinstance(results, list):
            raise RuntimeError("Unexpected SpotHero payload: 'results' is not a list")

        normalized: list[dict[str, Any]] = []
        for item in results:
            if not isinstance(item, dict):
                continue
            mapped = self._map_result_item(item)
            if mapped:
                normalized.append(mapped)

        return normalized

    def _map_result_item(self, item: dict[str, Any]) -> dict[str, Any] | None:
        facility = item.get("facility") if isinstance(item.get("facility"), dict) else {}
        facility_common = (
            facility.get("common") if isinstance(facility.get("common"), dict) else {}
        )
        facility_airport = (
            facility.get("airport") if isinstance(facility.get("airport"), dict) else {}
        )

        rates = item.get("rates")
        primary_rate = (
            rates[0] if isinstance(rates, list) and rates and isinstance(rates[0], dict) else {}
        )

        quote = primary_rate.get("quote") if isinstance(primary_rate.get("quote"), dict) else {}
        quote_meta = quote.get("meta") if isinstance(quote.get("meta"), dict) else {}

        order = quote.get("order")
        primary_order = (
            order[0] if isinstance(order, list) and order and isinstance(order[0], dict) else {}
        )

        addresses = facility_common.get("addresses")
        primary_address = (
            addresses[0]
            if isinstance(addresses, list) and addresses and isinstance(addresses[0], dict)
            else {}
        )

        total_price_obj = (
            quote.get("total_price") if isinstance(quote.get("total_price"), dict) else {}
        )
        display_price_obj = (
            primary_order.get("total_price")
            if isinstance(primary_order.get("total_price"), dict)
            else total_price_obj
        )

        def cents_to_dollars(value: Any) -> float | None:
            if isinstance(value, (int, float)):
                return value / 100.0
            return None

        total_price = cents_to_dollars(total_price_obj.get("value"))

        facility_id = (
            primary_order.get("facility_id")
            or facility_common.get("id")
            or item.get("id")
        )
        if facility_id is None:
            return None

        quote_id = (
            quote_meta.get("quote_mac")
            or primary_order.get("rate_id")
            or quote.get("id")
            or primary_rate.get("id")
            or f"shq_{facility_id}"
        )

        availability = (
            item.get("availability") if isinstance(item.get("availability"), dict) else {}
        )
        cancellation = (
            facility_common.get("cancellation")
            if isinstance(facility_common.get("cancellation"), dict)
            else {}
        )
        transportation = (
            facility_airport.get("transportation")
            if isinstance(facility_airport.get("transportation"), dict)
            else {}
        )
        transportation_schedule = (
            transportation.get("schedule")
            if isinstance(transportation.get("schedule"), dict)
            else {}
        )
        rating = (
            facility_common.get("rating")
            if isinstance(facility_common.get("rating"), dict)
            else {}
        )
        distance = item.get("distance") if isinstance(item.get("distance"), dict) else {}

        return {
            "listing_id": str(facility_id),
            "quote_id": str(quote_id),
            "location_name": facility_common.get("title") or facility_common.get("name") or "",
            "address": primary_address.get("street_address"),
            "city": primary_address.get("city"),
            "state": primary_address.get("state"),
            "postal_code": primary_address.get("postal_code"),
            "lat": primary_address.get("latitude"),
            "lng": primary_address.get("longitude"),
            "currency": total_price_obj.get("currency_code") or "USD",
            "total_price": total_price,
            "is_bookable": bool(availability.get("available")),
            "display_price": cents_to_dollars(display_price_obj.get("value")),
            "distance_to_airport_meters": distance.get("linear_meters"),
            "shuttle": bool(transportation),
            "shuttle_type": transportation.get("type"),
            "shuttle_frequency_minutes": transportation_schedule.get("fast_frequency"),
            "shuttle_frequency_slow_minutes": transportation_schedule.get("slow_frequency"),
            "shuttle_duration_minutes": transportation_schedule.get("duration"),
            "cancellable": cancellation.get("allowed_by_customer"),
            "review_score": rating.get("average"),
            "review_count": rating.get("count"),
            "inventory_status": availability.get("available"),
            "available_spaces": availability.get("available_spaces"),
            "raw_source": item,
        }