import pytest
from unittest.mock import Mock, patch

from app.providers.spothero import SpotHeroProvider


SFO_HTML = """
<html>
  <body>
    <div>
      Aloft Hotel San Francisco Airport - Uncovered Self Park
      401 East Millbrae Avenue, Millbrae, CA 94030
      (1397 Reviews)
      From
      $45.98
      Per Day
    </div>

    <div>
      Oyster Point Garage SFO - Covered Self Park
      500 Marina Blvd, Brisbane, CA 94005
      (245 Reviews)
      From
      $18.50
      Per Day
    </div>
  </body>
</html>
"""

LAX_HTML = """
<html>
  <body>
    <div>
      Sunrise LAX Parking - Uncovered Self Park
      6151 W Century Blvd, Los Angeles, CA 90045
      (412 Reviews)
      From
      $29.10
      Per Day
    </div>
  </body>
</html>
"""

BROKEN_HTML = """
<html>
  <body>
    <div>
      Some random content with no valid parking listing pattern
    </div>
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


@patch("app.providers.spothero.requests.get")
def test_fetch_quotes_parses_multiple_sfo_results(mock_get):
    mock_get.return_value = make_response(SFO_HTML)

    provider = SpotHeroProvider()
    results = provider.fetch_quotes(
        airport_code="SFO",
        start_dt="2026-03-25T10:00:00",
        end_dt="2026-03-27T10:00:00",
    )

    assert len(results) == 2

    first = results[0]
    assert first["facility_name"] == "Aloft Hotel San Francisco Airport - Uncovered Self Park"
    assert first["street_address"] == "401 East Millbrae Avenue"
    assert first["municipality"] == "Millbrae"
    assert first["region"] == "CA"
    assert first["zip"] == "94030"
    assert first["currency_code"] == "USD"
    assert first["price"] == 45.98
    assert first["display_price"] == "$45.98"
    assert first["review_count"] == 1397
    assert first["inventory_status"] == "available"

    second = results[1]
    assert second["facility_name"] == "Oyster Point Garage SFO - Covered Self Park"
    assert second["street_address"] == "500 Marina Blvd"
    assert second["municipality"] == "Brisbane"
    assert second["region"] == "CA"
    assert second["zip"] == "94005"
    assert second["price"] == 18.50
    assert second["review_count"] == 245


@patch("app.providers.spothero.requests.get")
def test_fetch_quotes_parses_lax_result(mock_get):
    mock_get.return_value = make_response(LAX_HTML)

    provider = SpotHeroProvider()
    results = provider.fetch_quotes(
        airport_code="LAX",
        start_dt="2026-03-25T10:00:00",
        end_dt="2026-03-27T10:00:00",
    )

    assert len(results) == 1

    result = results[0]
    assert result["facility_name"] == "Sunrise LAX Parking - Uncovered Self Park"
    assert result["street_address"] == "6151 W Century Blvd"
    assert result["municipality"] == "Los Angeles"
    assert result["region"] == "CA"
    assert result["zip"] == "90045"
    assert result["price"] == 29.10
    assert result["review_count"] == 412


@patch("app.providers.spothero.requests.get")
def test_fetch_quotes_returns_empty_for_unsupported_airport(mock_get):
    provider = SpotHeroProvider()
    results = provider.fetch_quotes(
        airport_code="ORD",
        start_dt="2026-03-25T10:00:00",
        end_dt="2026-03-27T10:00:00",
    )

    assert results == []
    mock_get.assert_not_called()


@patch("app.providers.spothero.requests.get")
def test_fetch_quotes_returns_empty_when_no_valid_patterns_found(mock_get):
    mock_get.return_value = make_response(BROKEN_HTML)

    provider = SpotHeroProvider()
    results = provider.fetch_quotes(
        airport_code="SFO",
        start_dt="2026-03-25T10:00:00",
        end_dt="2026-03-27T10:00:00",
    )

    assert results == []


@patch("app.providers.spothero.requests.get")
def test_fetch_quotes_raises_on_http_error(mock_get):
    mock_get.return_value = make_response("error", status_code=500)

    provider = SpotHeroProvider()

    with pytest.raises(Exception, match="HTTP 500"):
        provider.fetch_quotes(
            airport_code="SFO",
            start_dt="2026-03-25T10:00:00",
            end_dt="2026-03-27T10:00:00",
        )