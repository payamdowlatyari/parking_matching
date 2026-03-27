from __future__ import annotations

import re
from typing import Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from app.providers.base import BaseProvider


class CheapAirportParkingProvider(BaseProvider):
    """
    Cheap Airport Parking provider.

    This provider scrapes public HTML pages because a stable public API was not
    identified. It returns displayed lot information and publicly listed pricing,
    which may represent starting/day rates rather than a fully recalculated quote
    for the requested date range.
    """

    provider_name = "cheapairportparking"
    base_url = "https://www.cheapairportparking.org"

    SUPPORTED_AIRPORTS = {
        "SFO": "/sfo",
        "LAX": "/lax",
        "ORD": "/ord",
        "JFK": "/jfk",
    }

    def fetch_quotes(
        self, airport_code: str, start_dt: str, end_dt: str
    ) -> list[dict[str, Any]]:
        airport_code = airport_code.upper()
        airport_path = self.SUPPORTED_AIRPORTS.get(airport_code)
        if not airport_path:
            raise ValueError(f"Unsupported CheapAirportParking airport code: {airport_code}")

        airport_url = urljoin(self.base_url, airport_path)
        airport_html = self._get_html(airport_url)
        airport_soup = BeautifulSoup(airport_html, "html.parser")

        listings = self._extract_airport_listings(airport_soup, airport_url, airport_code)
        print(
            f"Extracted {len(listings)} listings for {airport_code} from CheapAirportParking"
        )

        enriched: list[dict[str, Any]] = []
        for listing in listings:
            lot_url = listing.get("lot_url")
            if not lot_url:
                listing["requested_start_dt"] = start_dt
                listing["requested_end_dt"] = end_dt
                enriched.append(listing)
                continue

            try:
                lot_html = self._get_html(lot_url)
                lot_soup = BeautifulSoup(lot_html, "html.parser")
                detail_data = self._extract_lot_details(lot_soup, lot_url)
                listing.update(detail_data)
            except Exception as exc:
                listing["detail_fetch_error"] = str(exc)

            listing["requested_start_dt"] = start_dt
            listing["requested_end_dt"] = end_dt
            enriched.append(listing)

        return enriched

    def _get_html(self, url: str) -> str:
        response = requests.get(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/146.0.0.0 Safari/537.36"
                )
            },
            timeout=20,
        )
        if response.status_code != 200:
            raise RuntimeError(
                f"CheapAirportParking request failed: {response.status_code} {url}"
            )
        return response.text

    def _extract_airport_listings(
        self, soup: BeautifulSoup, airport_url: str, airport_code: str
    ) -> list[dict[str, Any]]:
        text_lines = [line.strip() for line in soup.get_text("\n").splitlines()]
        text_lines = [line for line in text_lines if line]

        name_to_url: dict[str, str] = {}
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if "/lot/" not in href:
                continue
            name = a.get_text(" ", strip=True)
            if not name:
                continue
            name_to_url[self._normalize_name(name)] = urljoin(self.base_url, href)

        start_idx = None
        start_header = f"popular lots at {airport_code.lower()} airport"

        for i, line in enumerate(text_lines):
            if line.strip().lower() == start_header:
                start_idx = i + 1
                break

        if start_idx is None:
            return []

        end_idx = len(text_lines)
        for i in range(start_idx, len(text_lines)):
            line = text_lines[i].strip()
            if line.startswith("###"):
                end_idx = i
                break
            if line.lower() in {
                f"{airport_code.lower()} parking",
                f"parking around {airport_code.lower()} airport",
            }:
                end_idx = i
                break

        section = text_lines[start_idx:end_idx]

        cleaned: list[str] = []
        for line in section:
            lowered = line.lower()
            if lowered == "view all":
                continue
            if "image:" in lowered:
                continue
            cleaned.append(line)

        listings: list[dict[str, Any]] = []
        i = 0
        while i < len(cleaned) - 4:
            name = cleaned[i]
            rating_value_line = cleaned[i + 1]
            rating_suffix_line = cleaned[i + 2]
            review_line = cleaned[i + 3]
            price_line = cleaned[i + 4]

            if (
                re.fullmatch(r"\d+(?:\.\d+)?", rating_value_line)
                and rating_suffix_line.strip().lower() == "of 5"
                and re.fullmatch(r"\d+\s+reviews?", review_line, re.I)
                and re.fullmatch(r"\$\d+(?:\.\d{2})?", price_line)
            ):
                rating_line = f"{rating_value_line} {rating_suffix_line}"
                normalized_name = self._normalize_name(name)
                lot_url = name_to_url.get(normalized_name)
                listing_id = self._slug_from_lot_url(lot_url) if lot_url else self._slugify(name)

                listings.append(
                    {
                        "listing_id": listing_id,
                        "quote_id": listing_id,
                        "location_name": name,
                        "address": None,
                        "city": None,
                        "state": None,
                        "postal_code": None,
                        "lat": None,
                        "lng": None,
                        "currency": "USD",
                        "total_price": self._parse_money(price_line),
                        "display_price": self._parse_money(price_line),
                        "price_kind": "starting_daily_rate",
                        "is_bookable": True,
                        "review_score": self._parse_rating(rating_value_line),
                        "review_count": self._parse_review_count(review_line),
                        "lot_url": lot_url,
                        "source_airport_url": airport_url,
                        "raw_source": {
                            "summary_name": name,
                            "summary_rating_text": rating_line,
                            "summary_review_text": review_line,
                            "summary_price_text": price_line,
                        },
                    }
                )
                i += 5
            else:
                i += 1

        deduped: dict[str, dict[str, Any]] = {}
        for listing in listings:
            deduped[listing["listing_id"]] = listing

        return list(deduped.values())

    def _extract_lot_details(
        self, soup: BeautifulSoup, lot_url: str
    ) -> dict[str, Any]:
        text_lines = [line.strip() for line in soup.get_text("\n").splitlines()]
        text_lines = [line for line in text_lines if line]

        detail: dict[str, Any] = {
            "lot_url": lot_url,
        }

        title = self._find_h1_text(soup)
        if title:
            detail["location_name"] = title

        price_line = self._find_line_matching(text_lines, r"from \$\d+(?:\.\d{2})?\s*/\s*day")
        if price_line:
            detail["total_price"] = self._parse_money(price_line)
            detail["display_price"] = detail["total_price"]
            detail["price_kind"] = "starting_daily_rate"

        rating_line = self._find_line_matching(
            text_lines, r"\d+(?:\.\d+)?\s+out of 5\s+Based on\s+\d+\s+verified reviews"
        )
        if rating_line:
            rating_match = re.search(r"(\d+(?:\.\d+)?)\s+out of 5", rating_line)
            reviews_match = re.search(r"(\d+)\s+verified reviews", rating_line)
            if rating_match:
                detail["review_score"] = float(rating_match.group(1))
            if reviews_match:
                detail["review_count"] = int(reviews_match.group(1))

        address_line = self._find_address_line(text_lines)
        if address_line:
            detail["address"] = address_line
            parsed = self._parse_us_address(address_line)
            detail.update(parsed)

        parking_type = self._extract_parking_type(text_lines)
        if parking_type:
            detail["parking_type"] = parking_type

        distance_line = self._find_line_matching(
            text_lines, r"Distance from Airport\s+\d+(?:\.\d+)?\s+mi"
        )
        if distance_line:
            match = re.search(r"(\d+(?:\.\d+)?)\s+mi", distance_line)
            if match:
                detail["distance_to_airport_miles"] = float(match.group(1))

        shuttle_line = self._find_line_matching(text_lines, r"Shuttle Interval,\s*min\s+\d+")
        if shuttle_line:
            match = re.search(r"(\d+)$", shuttle_line)
            if match:
                detail["shuttle_frequency_minutes"] = int(match.group(1))
                detail["shuttle"] = True

        capacity_line = self._find_line_matching(text_lines, r"Lot Capacity\s+\d+")
        if capacity_line:
            match = re.search(r"(\d+)$", capacity_line)
            if match:
                detail["lot_capacity"] = int(match.group(1))

        hours_text = self._line_after(text_lines, "Parking Lot Operation and Shuttle Hours")
        if hours_text:
            detail["hours"] = hours_text

        arrival_info = self._line_after(text_lines, "Arrival Info")
        if arrival_info:
            detail["arrival_info"] = arrival_info

        return detail

    def _extract_parking_type(self, lines: list[str]) -> str | None:
        for i, line in enumerate(lines):
            if line.strip() == "To":
                for j in range(i + 1, min(i + 8, len(lines))):
                    candidate = lines[j].strip()
                    if not candidate:
                        continue
                    if "parking" in candidate.lower():
                        return candidate
        return None

    def _find_h1_text(self, soup: BeautifulSoup) -> str | None:
        h1 = soup.find("h1")
        if h1:
            return h1.get_text(" ", strip=True)
        return None

    def _find_line_matching(self, lines: list[str], pattern: str) -> str | None:
        regex = re.compile(pattern, re.I)
        for line in lines:
            if regex.search(line):
                return line
        return None

    def _line_after(self, lines: list[str], label: str) -> str | None:
        for i, line in enumerate(lines):
            if line.strip().lower() == label.strip().lower():
                collected: list[str] = []
                for j in range(i + 1, min(i + 8, len(lines))):
                    candidate = lines[j].strip()
                    if not candidate:
                        continue
                    lowered = candidate.lower()
                    if lowered in {
                        "arrival info",
                        "parking lot operation and shuttle hours",
                        "distance from airport",
                        "shuttle interval, min",
                        "lot capacity",
                    }:
                        break
                    collected.append(candidate)
                if collected:
                    return " ".join(collected)
        return None

    def _find_address_line(self, lines: list[str]) -> str | None:
        for line in lines:
            if re.search(r",\s*[A-Z]{2}\s+\d{5}", line):
                return line.replace(" Map", "").strip()
        return None

    def _parse_us_address(self, address: str) -> dict[str, Any]:
        match = re.match(
            r"^(?P<street>.+?),\s*(?P<city>.+?),\s*(?P<state>[A-Z]{2})\s+(?P<zip>\d{5})$",
            address,
        )
        if not match:
            return {"city": None, "state": None, "postal_code": None}

        return {
            "city": match.group("city").strip(),
            "state": match.group("state").strip(),
            "postal_code": match.group("zip").strip(),
        }

    def _parse_money(self, text: str) -> float | None:
        match = re.search(r"\$([0-9]+(?:\.[0-9]{2})?)", text)
        return float(match.group(1)) if match else None

    def _parse_rating(self, text: str) -> float | None:
        match = re.search(r"(\d+(?:\.\d+)?)", text)
        return float(match.group(1)) if match else None

    def _parse_review_count(self, text: str) -> int | None:
        match = re.search(r"(\d+)\s+reviews?", text, re.I)
        return int(match.group(1)) if match else None

    def _slug_from_lot_url(self, lot_url: str | None) -> str:
        if not lot_url:
            return ""
        return lot_url.rstrip("/").split("/")[-1]

    def _slugify(self, text: str) -> str:
        return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")

    def _normalize_name(self, text: str) -> str:
        return re.sub(r"\s+", " ", text.strip()).lower()