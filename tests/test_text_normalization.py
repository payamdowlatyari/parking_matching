"""Tests for app.normalize.text."""

import pytest

from app.normalize.text import normalize, normalize_address, normalize_name


class TestNormalize:
    def test_lowercases(self):
        assert normalize("HELLO WORLD") == "hello world"

    def test_strips_whitespace(self):
        assert normalize("  hello   world  ") == "hello world"

    def test_removes_punctuation(self):
        # Apostrophe becomes a space; commas and periods are stripped
        assert normalize("O'Hare, Airport.") == "o hare airport"

    def test_expands_street_abbreviation(self):
        assert normalize("123 Main St.") == "123 main street"

    def test_expands_avenue_abbreviation(self):
        assert normalize("456 Oak Ave") == "456 oak avenue"

    def test_unicode_normalization(self):
        # Accented characters should be transliterated to ASCII
        result = normalize("Café Résumé")
        assert "e" in result  # accent stripped

    def test_collapses_inner_whitespace(self):
        assert normalize("a  b   c") == "a b c"


class TestNormalizeName:
    def test_strips_parkwhiz_suffix(self):
        name = "O'Hare Airport Parking – ParkWhiz"
        result = normalize_name(name)
        assert "parkwhiz" not in result

    def test_strips_spothero_suffix(self):
        name = "Downtown Garage - SpotHero"
        result = normalize_name(name)
        assert "spothero" not in result

    def test_preserves_core_name(self):
        result = normalize_name("Downtown Garage - SpotHero")
        assert "downtown" in result
        assert "garage" in result


class TestNormalizeAddress:
    def test_expands_street(self):
        assert normalize_address("123 Main St") == "123 main street"

    def test_expands_avenue(self):
        assert normalize_address("456 Oak Ave") == "456 oak avenue"

    def test_handles_period_abbreviation(self):
        assert normalize_address("5700 S. Cicero Ave.") == "5700 s cicero avenue"
