import re
from typing import Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from app.providers.base import BaseProvider


class CheapAirportParkingProvider(BaseProvider):
    provider_name = "cheap_airport_parking"
    BASE_URL = "https://www.cheapairportparking.org"

    def fetch_quotes(
        self, airport_code: str, start_dt: str, end_dt: str
    ) -> list[dict[str, Any]]:
        airport_code = airport_code.lower()
        airport_url = f"{self.BASE_URL}/{airport_code}"

        response = requests.get(
            airport_url,
            timeout=20,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Airport pages expose lot links in the footer-style link list, e.g.
        # /lot/Aloft-SFO, /lot/Travelodge-SFO-Airport, etc.
        lot_links = []
        for a in soup.select('a[href^="/lot/"]'):
            href = a.get("href")
            name = a.get_text(" ", strip=True)
            if not href or not name:
                continue
            lot_links.append({
                "name": name,
                "href": urljoin(self.BASE_URL, href),
            })

        # Deduplicate by href
        seen = set()
        deduped_links = []
        for link in lot_links:
            if link["href"] in seen:
                continue
            seen.add(link["href"])
            deduped_links.append(link)

        results: list[dict[str, Any]] = []
        for link in deduped_links:
            details = self._fetch_lot_details(link["href"])
            if not details:
                continue

            results.append(
                {
                    "id": details["slug"],
                    "quote_ref": details["slug"],
                    "title": details["title"] or link["name"],
                    "address_1": details["address_1"],
                    "city_name": details["city_name"],
                    "state_code": details["state_code"],
                    "zip_code": details["zip_code"],
                    "geo": {"lat": None, "lng": None},
                    "pricing": {
                        "currency": "USD",
                        "total": details["price"],
                        "display_total": f"${details['price']:.2f}" if details["price"] is not None else None,
                        "daily_from": details["price"],
                    },
                    "lot_type": details["lot_type"],
                    "parking_type": details["parking_type"],
                    "airport_shuttle": {
                        "included": details["shuttle_interval_minutes"] is not None,
                        "frequency_minutes": details["shuttle_interval_minutes"],
                        "hours": details["shuttle_hours"],
                    },
                    "reviews": {
                        "rating": details["rating"],
                        "count": details["review_count"],
                    },
                    "free_cancellation": None,
                }
            )

        return results

    def _fetch_lot_details(self, lot_url: str) -> dict[str, Any] | None:
        response = requests.get(
            lot_url,
            timeout=20,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        response.raise_for_status()

        text = response.text
        soup = BeautifulSoup(text, "html.parser")
        page_text = soup.get_text("\n", strip=True)

        slug = lot_url.rstrip("/").split("/")[-1]

        # Title
        title = None
        h1 = soup.find("h1")
        if h1:
            title = h1.get_text(" ", strip=True)

        # Price: "from $11.49 / day"
        price = None
        m = re.search(r'from\s+\$([0-9]+(?:\.[0-9]{2})?)\s*/\s*day', page_text, re.I)
        if m:
            price = float(m.group(1))

        # Rating / reviews: "4.9 out of 5 Based on 319 verified reviews"
        rating = None
        review_count = None
        m = re.search(
            r'([0-9]+(?:\.[0-9])?)\s+out of 5\s+Based on\s+([0-9,]+)\s+verified reviews',
            page_text,
            re.I,
        )
        if m:
            rating = float(m.group(1))
            review_count = int(m.group(2).replace(",", ""))

        # Address line: "401 East Millbrae Avenue, Millbrae, CA 94030"
        address_1 = city_name = state_code = zip_code = None
        address_line = None
        for line in page_text.splitlines():
            line = line.strip()
            if re.search(r',\s*[A-Z][a-zA-Z .-]+,\s*[A-Z]{2}\s+\d{5}', line):
                address_line = line
                break

        if address_line:
            m = re.match(r'^(.*?),\s*([^,]+),\s*([A-Z]{2})\s+(\d{5})$', address_line)
            if m:
                address_1 = m.group(1).strip()
                city_name = m.group(2).strip()
                state_code = m.group(3).strip()
                zip_code = m.group(4).strip()

        # Lot / parking type: e.g. "Outdoor Self Parking"
        lot_type = None
        parking_type = None
        m = re.search(r'\b(Outdoor|Indoor)\s+(Self|Valet)\s+Parking\b', page_text, re.I)
        if m:
            parking_type = m.group(1).lower()
            lot_type = m.group(2).lower()

        # Distance
        distance_miles = None
        m = re.search(r'Distance from Airport\s+([0-9]+(?:\.[0-9]+)?)\s*mi', page_text, re.I)
        if m:
            distance_miles = float(m.group(1))

        # Shuttle interval
        shuttle_interval_minutes = None
        m = re.search(r'Shuttle Interval,\s*min\s+([0-9]+)', page_text, re.I)
        if m:
            shuttle_interval_minutes = int(m.group(1))

        # Hours
        shuttle_hours = None
        if "accessible 24/7" in page_text.lower():
            shuttle_hours = "24/7"

        return {
            "slug": slug,
            "title": title,
            "price": price,
            "rating": rating,
            "review_count": review_count,
            "address_1": address_1,
            "city_name": city_name,
            "state_code": state_code,
            "zip_code": zip_code,
            "lot_type": lot_type,
            "parking_type": parking_type,
            "distance_miles": distance_miles,
            "shuttle_interval_minutes": shuttle_interval_minutes,
            "shuttle_hours": shuttle_hours,
        }