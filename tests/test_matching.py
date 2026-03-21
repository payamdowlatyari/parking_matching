"""Tests for app.matching.matcher."""

import pytest

from app.matching.matcher import match
from app.models import MatchedLot, ParkingLot


def _lot(provider: str, lot_id: str, name: str, address: str, city: str = "Chicago", state: str = "IL",
         lat: float = 41.88, lng: float = -87.63, price: float = 20.0) -> ParkingLot:
    return ParkingLot(
        provider=provider,
        lot_id=lot_id,
        name=name,
        address=address,
        city=city,
        state=state,
        zip_code="60601",
        latitude=lat,
        longitude=lng,
        price_per_day=price,
    )


class TestMatch:
    def test_empty_input(self):
        assert match([]) == []

    def test_single_lot(self):
        lot = _lot("pw", "1", "Garage A", "123 Main St")
        result = match([lot])
        assert len(result) == 1
        assert result[0].entries == [lot]

    def test_same_address_different_providers_merged(self):
        lot_a = _lot("pw", "1", "Downtown Garage - ParkWhiz", "123 Main St")
        lot_b = _lot("sh", "2", "Downtown Garage - SpotHero", "123 Main Street")
        result = match([lot_a, lot_b])
        # Both share same city and normalised address → 1 cluster
        assert len(result) == 1
        assert len(result[0].entries) == 2

    def test_different_addresses_not_merged(self):
        lot_a = _lot("pw", "1", "Garage A", "123 Main St", lat=41.88, lng=-87.63)
        lot_b = _lot("sh", "2", "Garage B", "999 Oak Ave", lat=41.80, lng=-87.70)
        result = match([lot_a, lot_b])
        assert len(result) == 2

    def test_geo_proximity_merges_lots(self):
        # Lat/lng very close but slightly different addresses (typo)
        lot_a = _lot("pw", "1", "Airport Lot", "10000 W OHare Ave", lat=41.974, lng=-87.907)
        lot_b = _lot("cap", "2", "Airport Lot 2", "10000 W O'Hare Ave", lat=41.974, lng=-87.907)
        result = match([lot_a, lot_b])
        assert len(result) == 1

    def test_different_cities_not_merged(self):
        lot_a = _lot("pw", "1", "Garage A", "123 Main St", city="Chicago", state="IL")
        lot_b = _lot("sh", "2", "Garage A", "123 Main St", city="New York", state="NY")
        result = match([lot_a, lot_b])
        assert len(result) == 2

    def test_canonical_name_set(self):
        lot = _lot("pw", "1", "My Garage", "1 Park Ave")
        result = match([lot])
        assert isinstance(result[0].canonical_name, str)
        assert len(result[0].canonical_name) > 0

    def test_multiple_providers_placeholder_data(self):
        """Integration-style: run the matcher against all provider placeholder data."""
        from app.providers.cheap_airport_parking import CheapAirportParkingProvider
        from app.providers.parkwhiz import ParkWhizProvider
        from app.providers.spothero import SpotHeroProvider

        lots = (
            ParkWhizProvider().fetch()
            + SpotHeroProvider().fetch()
            + CheapAirportParkingProvider().fetch()
        )
        result = match(lots)
        # All 6 placeholder lots; expect some clusters (at least 2)
        assert len(result) >= 2
        # Total entries across all clusters equals total lots
        total_entries = sum(len(m.entries) for m in result)
        assert total_entries == len(lots)
