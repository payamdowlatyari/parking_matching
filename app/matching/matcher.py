from math import atan2, cos, radians, sin, sqrt

from rapidfuzz import fuzz

from app.models import MatchedLot, ParkingLot
from app.normalize.text import normalize_name, normalize_postal_code, normalize_text


def haversine_meters(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """
    Calculate distance between two latitude/longitude points in meters.

    Source: https://en.wikipedia.org/wiki/Haversine_formula
    """
    earth_radius_m = 6_371_000

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    )
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return earth_radius_m * c


def geolocation_similarity(left: ParkingLot, right: ParkingLot) -> float:
    """
    Convert geographic distance into a 0-1 similarity score.

    Distance is measured in meters.
    - 1.0 for <= 50m
    - 0.85 for <= 150m
    - 0.6 for <= 400m
    - 0.3 for <= 800m
    - 0.0 for > 800m or missing geolocation
    """
    if (
        left.latitude is None
        or left.longitude is None
        or right.latitude is None
        or right.longitude is None
    ):
        return 0.0

    distance = haversine_meters(
        left.latitude,
        left.longitude,
        right.latitude,
        right.longitude,
    )

    if distance <= 50:
        return 1.0
    if distance <= 150:
        return 0.85
    if distance <= 400:
        return 0.6
    if distance <= 800:
        return 0.3
    return 0.0


def exact_field_score(left_value: str | None, right_value: str | None) -> float:
    """
    Return 1.0 for an exact normalized match, else 0.0.
    """
    if not left_value or not right_value:
        return 0.0

    return 1.0 if normalize_text(left_value) == normalize_text(right_value) else 0.0


def postal_code_score(left_value: str | None, right_value: str | None) -> float:
    """
    Return 1.0 if postal codes match after normalization, else 0.0.
    """
    left_postal = normalize_postal_code(left_value)
    right_postal = normalize_postal_code(right_value)

    if not left_postal or not right_postal:
        return 0.0

    return 1.0 if left_postal == right_postal else 0.0


def score_pair(left: ParkingLot, right: ParkingLot) -> tuple[float, str]:
    """
    Score a pair of parking lots using weighted similarity signals.

    Weights:
    - 0.40: Name similarity
    - 0.30: Address similarity
    - 0.20: Geo similarity
    - 0.10: Locality similarity

    Returns:
        A tuple containing the total similarity score (0.0-1.0) and a reason string.
    """
    name_score = (
        fuzz.token_set_ratio(normalize_name(left.name), normalize_name(right.name)) / 100
    )

    address_score = (
        fuzz.token_set_ratio(
            normalize_text(left.address1),
            normalize_text(right.address1),
        )
        / 100
    )

    geo_score = geolocation_similarity(left, right)

    locality_score = (
        0.5 * exact_field_score(left.city, right.city)
        + 0.3 * exact_field_score(left.state, right.state)
        + 0.2 * postal_code_score(left.postal_code, right.postal_code)
    )

    total_score = (
        0.40 * name_score
        + 0.30 * address_score
        + 0.20 * geo_score
        + 0.10 * locality_score
    )

    reasons: list[str] = []

    if name_score >= 0.9:
        reasons.append("high name similarity")
    elif name_score >= 0.75:
        reasons.append("moderate name similarity")

    if address_score >= 0.9:
        reasons.append("high address similarity")
    elif address_score >= 0.75:
        reasons.append("moderate address similarity")

    if geo_score >= 0.85:
        reasons.append("near-identical geolocation")
    elif geo_score >= 0.6:
        reasons.append("nearby geolocation")

    if exact_field_score(left.city, right.city):
        reasons.append("same city")

    if exact_field_score(left.state, right.state):
        reasons.append("same state")

    if postal_code_score(left.postal_code, right.postal_code):
        reasons.append("same postal code")

    reason = "; ".join(reasons) if reasons else "weak overall similarity"

    return total_score, reason


def classify_match(score: float) -> str:
    """
    Convert a numeric similarity score into a match label.

    - "match" for scores >= 0.85
    - "possible_match" for scores >= 0.65
    - "no_match" for scores < 0.65
    """
    if score >= 0.85:
        return "match"
    if score >= 0.65:
        return "possible_match"
    return "no_match"


def match_parking_lots(parking_lots: list[ParkingLot]) -> list[MatchedLot]:
    """
    Compare parking lots pairwise within the same airport across different providers.

    Returns:
        A list of MatchedLot instances.
    """
    matches: list[MatchedLot] = []

    for i, left in enumerate(parking_lots):
        for right in parking_lots[i + 1 :]:
            if left.airport_code != right.airport_code:
                continue

            if left.provider == right.provider:
                continue

            score, reason = score_pair(left, right)
            decision = classify_match(score)

            matches.append(
                MatchedLot(
                    airport_code=left.airport_code,
                    left_provider=left.provider,
                    left_lot_id=left.provider_lot_id,
                    right_provider=right.provider,
                    right_lot_id=right.provider_lot_id,
                    score=round(score, 4),
                    decision=decision,
                    reason=reason,
                )
            )

    return matches