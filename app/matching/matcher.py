"""Parking lot matcher: groups NormalizedFacility entries that represent the same physical lot."""

from itertools import combinations

from app.models import MatchedFacility, NormalizedFacility
from app.normalize.text import normalize_address, normalize_name

# Maximum distance (degrees lat/lng) used for geo proximity matching.
_GEO_THRESHOLD = 0.002  # roughly 200 m


def _geo_close(a: NormalizedFacility, b: NormalizedFacility) -> bool:
    """Return True when both lots have coordinates within *_GEO_THRESHOLD*."""
    if None in (a.latitude, a.longitude, b.latitude, b.longitude):
        return False
    return (
        abs(a.latitude - b.latitude) <= _GEO_THRESHOLD  # type: ignore[operator]
        and abs(a.longitude - b.longitude) <= _GEO_THRESHOLD  # type: ignore[operator]
    )


def _address_match(a: NormalizedFacility, b: NormalizedFacility) -> bool:
    """Return True when both lots share the same normalised address."""
    return normalize_address(a.address1) == normalize_address(b.address1)


def _name_match(a: NormalizedFacility, b: NormalizedFacility) -> bool:
    """Return True when both lots share the same normalised name."""
    return normalize_name(a.facility_name) == normalize_name(b.facility_name)


def match(facilities: list[NormalizedFacility]) -> list[MatchedFacility]:
    """Compare all cross-provider facility pairs and return FacilityMatch objects.
    Matching is based on a combination of geo proximity, address similarity, and name similarity.
    """
    matched_results: list[MatchedFacility] = []

    for fac_a, fac_b in combinations(facilities, 2):
        if fac_a.airport_code != fac_b.airport_code:
            continue  # Only compare lots at the same airport

        if _geo_close(fac_a, fac_b) and _address_match(fac_a, fac_b) and _name_match(fac_a, fac_b):
            matched_results.append(MatchedFacility(
                canonical_name=normalize_name(fac_a.facility_name),
                canonical_address=normalize_address(fac_a.address1),
                entries=[fac_a, fac_b],
            ))

    return matched_results  
