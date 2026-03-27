import re
import requests
from bs4 import BeautifulSoup
from typing import Any

from app.providers.base import BaseProvider


class SpotHeroProvider(BaseProvider):
    provider_name = "spothero"

    AIRPORT_URLS = {
        "SFO": "https://spothero.com/airport/san-francisco/sfo-parking",
        "LAX": "https://spothero.com/airport/los-angeles/lax-parking",
    }

    def fetch_quotes(
        self, airport_code: str, start_dt: str, end_dt: str
    ) -> list[dict[str, Any]]:

        airport_code = airport_code.upper()
        url = self.AIRPORT_URLS.get(airport_code)

        if not url:
            return []

        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=20,
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text("\n", strip=True)

        lines = [line.strip() for line in text.splitlines() if line.strip()]

        results = []

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for parking listing pattern
            if "Park" in line and i + 5 < len(lines):

                title = line
                address = lines[i + 1]

                # Example: "(1397 Reviews)"
                reviews_line = lines[i + 2]

                # "From" + "$XX.XX"
                if lines[i + 3] == "From":
                    price_line = lines[i + 4]

                    price_match = re.search(r"\$([0-9]+(?:\.[0-9]+)?)", price_line)
                    review_match = re.search(r"\((\d+)\s+Reviews\)", reviews_line)

                    if price_match:
                        price = float(price_match.group(1))
                        review_count = (
                            int(review_match.group(1)) if review_match else None
                        )

                        # Basic address parsing
                        address_parts = address.split(",")
                        street = address_parts[0].strip()
                        city = address_parts[1].strip() if len(address_parts) > 1 else None

                        state = None
                        zip_code = None
                        if len(address_parts) > 2:
                            state_zip = address_parts[2].strip().split()
                            if len(state_zip) >= 1:
                                state = state_zip[0]
                            if len(state_zip) >= 2:
                                zip_code = state_zip[1]

                        results.append(
                            {
                                "facility_id": f"sh_{airport_code}_{i}",
                                "rate_id": f"shr_{airport_code}_{i}",
                                "facility_name": title,
                                "street_address": street,
                                "municipality": city,
                                "region": state,
                                "zip": zip_code,
                                "latitude": None,
                                "longitude": None,
                                "currency_code": "USD",
                                "price": price,
                                "display_price": f"${price}",
                                "review_score": None,
                                "review_count": review_count,
                                "amenities": [],
                                "shuttle_frequency_minutes": None,
                                "distance_to_airport_miles": None,
                                "is_refundable": None,
                                "inventory_status": "available",
                            }
                        )

            i += 1

        return results