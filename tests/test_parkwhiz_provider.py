import pytest
from unittest.mock import Mock, patch

from app.providers.parkwhiz import ParkWhizProvider


PARKWHIZ_API_RESPONSE = {
    "parking_listings": [
        {
            "id": "pw_1",
            "quote_id": "pwq_1",
            "name": "Joe's Airport Parking",
            "address": {
                "street": "9420 River Street",
                "city": "Schiller Park",
                "state": "IL",
                "postal_code": "60176",
            },
            "location": {
                "lat": 41.9741,
                "lng": -87.8692,
            },
            "pricing": {
                "currency": "USD",
                "total": 28.49,
                "display": "$28.49",
            },
            "reviews": {
                "average": 4.6,
                "count": 318,
            },
            "amenities": ["self_park", "shuttle", "covered_available"],
            "shuttle_frequency_minutes": 15,
            "distance_to_airport_miles": 2.4,
            "refundable": True,
            "availability": "available",
        },
        {
            "id": "pw_2",
            "quote_id": "pwq_2",
            "name": "Skyline Valet",
            "address": {
                "street": "10100 Mannheim Road",
                "city": "Rosemont",
                "state": "IL",
                "postal_code": None,
            },
            "location": {
                "lat": 41.9960,
                "lng": -87.8853,
            },
            "pricing": {
                "currency": "USD",
                "total": 34.95,
                "display": "$34.95",
            },
            "reviews": {
                "average": 4.4,
                "count": 190,
            },
            "amenities": ["valet", "shuttle"],
            "shuttle_frequency_minutes": 10,
            "distance_to_airport_miles": 2.9,
            "refundable": True,
            "availability": "available",
        },
    ]
}

EMPTY_API_RESPONSE = {"parking_listings": []}
MALFORMED_API_RESPONSE = {"unexpected_key": []}


def make_response(json_data, status_code=200) -> Mock:
    response = Mock()
    response.status_code = status_code
    response.json = Mock(return_value=json_data)
    response.raise_for_status = Mock()
    if status_code >= 400:
        response.raise_for_status.side_effect = Exception(f"HTTP {status_code}")
    return response


@patch("app.providers.parkwhiz.requests.get")
def test_fetch_quotes_parses_multiple_results(mock_get):
    mock_get.return_value = make_response(PARKWHIZ_API_RESPONSE)

    provider = ParkWhizProvider()
    results = provider.fetch_quotes(
        airport_code="ORD",
        start_dt="2026-03-25T10:00:00",
        end_dt="2026-03-27T10:00:00",
    )

    assert len(results) == 2

    first = results[0]
    assert first["id"] == "pw_1"
    assert first["quote_id"] == "pwq_1"
    assert first["name"] == "Joe's Airport Parking"
    assert first["street_address"] == "9420 River Street"
    assert first["city"] == "Schiller Park"
    assert first["state"] == "IL"
    assert first["zip_code"] == "60176"
    assert first["latitude"] == 41.9741
    assert first["longitude"] == -87.8692
    assert first["currency"] == "USD"
    assert first["price"] == 28.49
    assert first["display_price"] == "$28.49"
    assert first["review_score"] == 4.6
    assert first["review_count"] == 318
    assert first["amenities"] == ["self_park", "shuttle", "covered_available"]
    assert first["shuttle_frequency_minutes"] == 15
    assert first["distance_to_airport_miles"] == 2.4
    assert first["is_refundable"] is True
    assert first["inventory_status"] == "available"

    second = results[1]
    assert second["id"] == "pw_2"
    assert second["quote_id"] == "pwq_2"
    assert second["name"] == "Skyline Valet"
    assert second["street_address"] == "10100 Mannheim Road"
    assert second["city"] == "Rosemont"
    assert second["state"] == "IL"
    assert second["zip_code"] is None
    assert second["price"] == 34.95


@patch("app.providers.parkwhiz.requests.get")
def test_fetch_quotes_returns_empty_when_no_results(mock_get):
    mock_get.return_value = make_response(EMPTY_API_RESPONSE)

    provider = ParkWhizProvider()
    results = provider.fetch_quotes(
        airport_code="ORD",
        start_dt="2026-03-25T10:00:00",
        end_dt="2026-03-27T10:00:00",
    )

    assert results == []


@patch("app.providers.parkwhiz.requests.get")
def test_fetch_quotes_handles_missing_optional_fields(mock_get):
    payload = {
        "parking_listings": [
            {
                "id": "pw_3",
                "quote_id": "pwq_3",
                "name": "Budget Park",
                "address": {
                    "street": "5440 N River Road",
                    "city": "Rosemont",
                    "state": "IL",
                    "postal_code": None,
                },
                "location": {
                    "lat": None,
                    "lng": None,
                },
                "pricing": {
                    "currency": "USD",
                    "total": 22.10,
                    "display": "$22.10",
                },
                "reviews": {
                    "average": None,
                    "count": 0,
                },
                "amenities": [],
                "shuttle_frequency_minutes": None,
                "distance_to_airport_miles": None,
                "refundable": False,
                "availability": "available",
            }
        ]
    }
    mock_get.return_value = make_response(payload)

    provider = ParkWhizProvider()
    results = provider.fetch_quotes(
        airport_code="ORD",
        start_dt="2026-03-25T10:00:00",
        end_dt="2026-03-27T10:00:00",
    )

    assert len(results) == 1
    result = results[0]
    assert result["zip_code"] is None
    assert result["latitude"] is None
    assert result["longitude"] is None
    assert result["review_score"] is None
    assert result["review_count"] == 0
    assert result["shuttle_frequency_minutes"] is None
    assert result["distance_to_airport_miles"] is None
    assert result["is_refundable"] is False


@patch("app.providers.parkwhiz.requests.get")
def test_fetch_quotes_returns_empty_for_malformed_response(mock_get):
    mock_get.return_value = make_response(MALFORMED_API_RESPONSE)

    provider = ParkWhizProvider()
    results = provider.fetch_quotes(
        airport_code="ORD",
        start_dt="2026-03-25T10:00:00",
        end_dt="2026-03-27T10:00:00",
    )

    assert results == []


@patch("app.providers.parkwhiz.requests.get")
def test_fetch_quotes_raises_on_http_error(mock_get):
    mock_get.return_value = make_response({"error": "server error"}, status_code=500)

    provider = ParkWhizProvider()

    with pytest.raises(Exception, match="HTTP 500"):
        provider.fetch_quotes(
            airport_code="ORD",
            start_dt="2026-03-25T10:00:00",
            end_dt="2026-03-27T10:00:00",
        )


@patch("app.providers.parkwhiz.requests.get")
def test_fetch_quotes_calls_requests_with_expected_params(mock_get):
    mock_get.return_value = make_response(EMPTY_API_RESPONSE)

    provider = ParkWhizProvider()
    provider.fetch_quotes(
        airport_code="ORD",
        start_dt="2026-03-25T10:00:00",
        end_dt="2026-03-27T10:00:00",
    )

    assert mock_get.called
    _, kwargs = mock_get.call_args
    assert "timeout" in kwargs