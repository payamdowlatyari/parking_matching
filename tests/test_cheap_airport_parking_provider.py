import pytest
from unittest.mock import Mock, patch

from app.providers.cheap_airport_parking import CheapAirportParkingProvider


AIRPORT_HTML = """
<html>
  <body>
    <a href="/lot/Aloft-SFO">Aloft San Francisco Airport</a>
    <a href="/lot/Travelodge-SFO-Airport">Travelodge SFO Airport</a>
    <a href="/lot/Aloft-SFO">Aloft San Francisco Airport</a> <!-- duplicate -->
  </body>
</html>
"""

ALOFT_LOT_HTML = """
<html>
  <body>
    <h1>Aloft San Francisco Airport</h1>
    <div>from $11.49 / day</div>
    <div>4.9 out of 5 Based on 319 verified reviews</div>
    <div>401 East Millbrae Avenue, Millbrae, CA 94030</div>
    <div>Outdoor Self Parking</div>
    <div>Distance from Airport 1.1 mi</div>
    <div>Shuttle Interval, min 15</div>
    <div>accessible 24/7</div>
  </body>
</html>
"""

TRAVELODGE_LOT_HTML = """
<html>
  <body>
    <h1>Travelodge SFO Airport</h1>
    <div>from $9.95 / day</div>
    <div>4.2 out of 5 Based on 121 verified reviews</div>
    <div>326 South Airport Boulevard, South San Francisco, CA 94080</div>
    <div>Indoor Valet Parking</div>
    <div>Distance from Airport 2.3 mi</div>
    <div>Shuttle Interval, min 20</div>
  </body>
</html>
"""

BROKEN_AIRPORT_HTML = """
<html>
  <body>
    <div>No lot links here</div>
  </body>
</html>
"""

BROKEN_LOT_HTML = """
<html>
  <body>
    <h1>Broken Lot Page</h1>
    <div>Some random content</div>
  </body>
</html>
"""


def make_response(text: str, status_code: int = 200) -> Mock:
    response = Mock()
    response.status_code = status_code
    response.text = text
    response.raise_for_status = Mock()
    if status_code >= 400:
        response.raise_for_status.side_effect = Exception(f"HTTP {status_code}")
    return response


def mocked_requests_get(url, timeout=20, headers=None):
    if url == "https://www.cheapairportparking.org/sfo":
        return make_response(AIRPORT_HTML)
    if url == "https://www.cheapairportparking.org/lot/Aloft-SFO":
        return make_response(ALOFT_LOT_HTML)
    if url == "https://www.cheapairportparking.org/lot/Travelodge-SFO-Airport":
        return make_response(TRAVELODGE_LOT_HTML)
    raise AssertionError(f"Unexpected URL requested: {url}")


@patch("app.providers.cheap_airport_parking.requests.get")
def test_fetch_quotes_parses_airport_and_lot_pages(mock_get):
    mock_get.side_effect = mocked_requests_get

    provider = CheapAirportParkingProvider()
    results = provider.fetch_quotes(
        airport_code="SFO",
        start_dt="2026-03-25T10:00:00",
        end_dt="2026-03-27T10:00:00",
    )

    assert len(results) == 2

    first = results[0]
    assert first["id"] == "Aloft-SFO"
    assert first["quote_ref"] == "Aloft-SFO"
    assert first["title"] == "Aloft San Francisco Airport"
    assert first["address_1"] == "401 East Millbrae Avenue"
    assert first["city_name"] == "Millbrae"
    assert first["state_code"] == "CA"
    assert first["zip_code"] == "94030"
    assert first["pricing"]["currency"] == "USD"
    assert first["pricing"]["total"] == 11.49
    assert first["pricing"]["display_total"] == "$11.49"
    assert first["pricing"]["daily_from"] == 11.49
    assert first["lot_type"] == "self"
    assert first["parking_type"] == "outdoor"
    assert first["airport_shuttle"]["included"] is True
    assert first["airport_shuttle"]["frequency_minutes"] == 15
    assert first["airport_shuttle"]["hours"] == "24/7"
    assert first["reviews"]["rating"] == 4.9
    assert first["reviews"]["count"] == 319

    second = results[1]
    assert second["id"] == "Travelodge-SFO-Airport"
    assert second["title"] == "Travelodge SFO Airport"
    assert second["address_1"] == "326 South Airport Boulevard"
    assert second["city_name"] == "South San Francisco"
    assert second["state_code"] == "CA"
    assert second["zip_code"] == "94080"
    assert second["pricing"]["total"] == 9.95
    assert second["lot_type"] == "valet"
    assert second["parking_type"] == "indoor"
    assert second["airport_shuttle"]["frequency_minutes"] == 20
    assert second["airport_shuttle"]["hours"] is None
    assert second["reviews"]["rating"] == 4.2
    assert second["reviews"]["count"] == 121


@patch("app.providers.cheap_airport_parking.requests.get")
def test_fetch_quotes_deduplicates_duplicate_lot_links(mock_get):
    mock_get.side_effect = mocked_requests_get

    provider = CheapAirportParkingProvider()
    results = provider.fetch_quotes(
        airport_code="SFO",
        start_dt="2026-03-25T10:00:00",
        end_dt="2026-03-27T10:00:00",
    )

    ids = [r["id"] for r in results]
    assert ids.count("Aloft-SFO") == 1
    assert len(results) == 2


@patch("app.providers.cheap_airport_parking.requests.get")
def test_fetch_quotes_returns_empty_when_no_lot_links_found(mock_get):
    mock_get.return_value = make_response(BROKEN_AIRPORT_HTML)

    provider = CheapAirportParkingProvider()
    results = provider.fetch_quotes(
        airport_code="SFO",
        start_dt="2026-03-25T10:00:00",
        end_dt="2026-03-27T10:00:00",
    )

    assert results == []


@patch("app.providers.cheap_airport_parking.requests.get")
def test_fetch_quotes_skips_broken_lot_pages(mock_get):
    def side_effect(url, timeout=20, headers=None):
        if url == "https://www.cheapairportparking.org/sfo":
            return make_response(AIRPORT_HTML)
        if url == "https://www.cheapairportparking.org/lot/Aloft-SFO":
            return make_response(BROKEN_LOT_HTML)
        if url == "https://www.cheapairportparking.org/lot/Travelodge-SFO-Airport":
            return make_response(TRAVELODGE_LOT_HTML)
        raise AssertionError(f"Unexpected URL requested: {url}")

    mock_get.side_effect = side_effect

    provider = CheapAirportParkingProvider()
    results = provider.fetch_quotes(
        airport_code="SFO",
        start_dt="2026-03-25T10:00:00",
        end_dt="2026-03-27T10:00:00",
    )

    assert len(results) == 1
    assert results[0]["id"] == "Travelodge-SFO-Airport"


@patch("app.providers.cheap_airport_parking.requests.get")
def test_fetch_quotes_raises_on_airport_page_http_error(mock_get):
    mock_get.return_value = make_response("error", status_code=500)

    provider = CheapAirportParkingProvider()

    with pytest.raises(Exception, match="HTTP 500"):
        provider.fetch_quotes(
            airport_code="SFO",
            start_dt="2026-03-25T10:00:00",
            end_dt="2026-03-27T10:00:00",
        )


@patch("app.providers.cheap_airport_parking.requests.get")
def test_fetch_quotes_returns_empty_for_unknown_airport_page(mock_get):
    mock_get.return_value = make_response(BROKEN_AIRPORT_HTML)

    provider = CheapAirportParkingProvider()
    results = provider.fetch_quotes(
        airport_code="XXX",
        start_dt="2026-03-25T10:00:00",
        end_dt="2026-03-27T10:00:00",
    )

    assert results == []