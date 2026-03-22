from app.matching.matcher import (
    classify_match,
    match_parking_lots,
    score_pair,
)
from app.models import ParkingLot


def make_lot(
    *,
    provider: str,
    provider_lot_id: str,
    airport_code: str,
    name: str,
    address1: str | None,
    city: str | None,
    state: str | None,
    postal_code: str | None,
    latitude: float | None,
    longitude: float | None,
) -> ParkingLot:
    return ParkingLot(
        provider=provider,
        provider_lot_id=provider_lot_id,
        airport_code=airport_code,
        name=name,
        address1=address1,
        city=city,
        state=state,
        postal_code=postal_code,
        latitude=latitude,
        longitude=longitude,
        raw_payload={},
    )


def test_similar_lots_score_as_match():
    left = make_lot(
        provider="parkwhiz",
        provider_lot_id="pw_1",
        airport_code="ORD",
        name="Joes Airport Parking",
        address1="123 Main St",
        city="Chicago",
        state="IL",
        postal_code="60666",
        latitude=41.9742,
        longitude=-87.9073,
    )
    right = make_lot(
        provider="spothero",
        provider_lot_id="sh_1",
        airport_code="ORD",
        name="Joe's Airport Parking",
        address1="123 Main Street",
        city="Chicago",
        state="IL",
        postal_code="60666",
        latitude=41.9743,
        longitude=-87.9071,
    )

    score, reason = score_pair(left, right)

    assert score >= 0.85
    assert classify_match(score) == "match"
    assert "name similarity" in reason
    assert "address similarity" in reason


def test_different_lots_score_as_no_match():
    left = make_lot(
        provider="parkwhiz",
        provider_lot_id="pw_2",
        airport_code="ORD",
        name="Skyline Valet Garage",
        address1="500 Remote Rd",
        city="Chicago",
        state="IL",
        postal_code="60666",
        latitude=41.9815,
        longitude=-87.9012,
    )
    right = make_lot(
        provider="spothero",
        provider_lot_id="sh_3",
        airport_code="ORD",
        name="River North Event Parking",
        address1="10 Arena Blvd",
        city="Chicago",
        state="IL",
        postal_code="60610",
        latitude=41.9010,
        longitude=-87.6375,
    )

    score, _ = score_pair(left, right)

    assert score < 0.65
    assert classify_match(score) == "no_match"


def test_missing_geo_can_still_match_based_on_name_and_address():
    left = make_lot(
        provider="parkwhiz",
        provider_lot_id="pw_3",
        airport_code="LAX",
        name="Pacific Park and Fly",
        address1="900 Sepulveda Blvd",
        city="Los Angeles",
        state="CA",
        postal_code="90045",
        latitude=None,
        longitude=None,
    )
    right = make_lot(
        provider="cheap_airport_parking",
        provider_lot_id="cap_2",
        airport_code="LAX",
        name="Pacific Park and Fly",
        address1="900 Sepulveda Boulevard",
        city="Los Angeles",
        state="CA",
        postal_code="90045",
        latitude=None,
        longitude=None,
    )

    score, _ = score_pair(left, right)

    assert score >= 0.65
    assert classify_match(score) in {"possible_match", "match"}


def test_match_parking_lots_skips_same_provider_pairs():
    lots = [
        make_lot(
            provider="parkwhiz",
            provider_lot_id="pw_1",
            airport_code="ORD",
            name="Joes Airport Parking",
            address1="123 Main St",
            city="Chicago",
            state="IL",
            postal_code="60666",
            latitude=41.9742,
            longitude=-87.9073,
        ),
        make_lot(
            provider="parkwhiz",
            provider_lot_id="pw_2",
            airport_code="ORD",
            name="Skyline Valet Garage",
            address1="500 Remote Rd",
            city="Chicago",
            state="IL",
            postal_code="60666",
            latitude=41.9815,
            longitude=-87.9012,
        ),
        make_lot(
            provider="spothero",
            provider_lot_id="sh_1",
            airport_code="ORD",
            name="Joe's Airport Parking",
            address1="123 Main Street",
            city="Chicago",
            state="IL",
            postal_code="60666",
            latitude=41.9743,
            longitude=-87.9071,
        ),
    ]

    matches = match_parking_lots(lots)

    assert len(matches) == 2
    assert all(match.left_provider != match.right_provider for match in matches)