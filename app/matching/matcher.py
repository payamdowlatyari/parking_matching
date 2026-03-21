"""Parking lot matcher: groups ParkingLot entries that represent the same physical lot."""

from app.models import MatchedLot, ParkingLot
from app.normalize.text import normalize_address, normalize_name

# Maximum distance (degrees lat/lng) used for geo proximity matching.
_GEO_THRESHOLD = 0.002  # roughly 200 m


def _geo_close(a: ParkingLot, b: ParkingLot) -> bool:
    """Return True when both lots have coordinates within *_GEO_THRESHOLD*."""
    if None in (a.latitude, a.longitude, b.latitude, b.longitude):
        return False
    return (
        abs(a.latitude - b.latitude) <= _GEO_THRESHOLD  # type: ignore[operator]
        and abs(a.longitude - b.longitude) <= _GEO_THRESHOLD  # type: ignore[operator]
    )


def _address_match(a: ParkingLot, b: ParkingLot) -> bool:
    """Return True when both lots share the same normalised address."""
    return normalize_address(a.address) == normalize_address(b.address)


def _name_match(a: ParkingLot, b: ParkingLot) -> bool:
    """Return True when both lots share the same normalised name."""
    return normalize_name(a.name) == normalize_name(b.name)


def match(lots: list[ParkingLot]) -> list[MatchedLot]:
    """Group *lots* into MatchedLot clusters using address + geo proximity.

    Two lots are considered the same physical location when they share the
    same city/state, have a matching normalised address **or** are
    geographically close (within *_GEO_THRESHOLD* degrees).
    """
    clusters: list[list[ParkingLot]] = []

    for lot in lots:
        placed = False
        for cluster in clusters:
            representative = cluster[0]
            same_city = (
                lot.city.lower() == representative.city.lower()
                and lot.state.lower() == representative.state.lower()
            )
            if same_city and (_address_match(lot, representative) or _geo_close(lot, representative)):
                cluster.append(lot)
                placed = True
                break
        if not placed:
            clusters.append([lot])

    matched: list[MatchedLot] = []
    for cluster in clusters:
        # Use the longest name as canonical (more descriptive)
        canonical_name = normalize_name(max(cluster, key=lambda l: len(l.name)).name)
        canonical_address = normalize_address(cluster[0].address)
        matched.append(MatchedLot(canonical_name=canonical_name, canonical_address=canonical_address, entries=cluster))

    return matched
