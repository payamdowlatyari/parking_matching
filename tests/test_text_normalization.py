from app.normalize.text import normalize_name, normalize_postal_code, normalize_text


def test_normalize_text_removes_punctuation():
    assert normalize_text("Joe's Airport Parking!") == "joe s airport parking"


def test_normalize_text_collapses_whitespace():
    assert normalize_text("  123   Main   St  ") == "123 main street"


def test_normalize_text_expands_abbreviations():
    assert normalize_text("456 Elm Rd") == "456 elm road"
    assert normalize_text("789 Sunset Blvd") == "789 sunset boulevard"
    assert normalize_text("LAX Intl Parking") == "lax international parking"


def test_normalize_name_removes_weak_tokens():
    assert normalize_name("Joe's Airport Parking") == "joe s"
    assert normalize_name("Main Street Garage") == "main street"


def test_normalize_postal_code_cleans_value():
    assert normalize_postal_code(" 60666 ") == "60666"
    assert normalize_postal_code("60666-1234") == "60666-1234"
    assert normalize_postal_code(" 60 666 ") == "60666"


def test_normalize_helpers_handle_none():
    assert normalize_text(None) == ""
    assert normalize_name(None) == ""
    assert normalize_postal_code(None) == ""