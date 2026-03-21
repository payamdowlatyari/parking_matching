"""Text normalization utilities for parking lot names and addresses."""

import re
import unicodedata


# Common street-type abbreviations to expand for consistent comparison
_STREET_ABBREVIATIONS: dict[str, str] = {
    r"\bst\.?\b": "street",
    r"\bave\.?\b": "avenue",
    r"\bblvd\.?\b": "boulevard",
    r"\bdr\.?\b": "drive",
    r"\brd\.?\b": "road",
    r"\bln\.?\b": "lane",
    r"\bct\.?\b": "court",
    r"\bpl\.?\b": "place",
    r"\bhwy\.?\b": "highway",
    r"\bpkwy\.?\b": "parkway",
}


def normalize(text: str) -> str:
    """Return a cleaned, lower-cased version of *text* suitable for matching.

    Steps applied:
    1. Unicode NFKD normalization + ASCII-only encoding.
    2. Lower-case.
    3. Expand common street abbreviations.
    4. Remove punctuation except hyphens and spaces.
    5. Collapse whitespace.
    """
    # 1. Unicode normalize
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    # 2. Lower-case
    text = text.lower()
    # 3. Expand abbreviations
    for pattern, replacement in _STREET_ABBREVIATIONS.items():
        text = re.sub(pattern, replacement, text)
    # 4. Remove punctuation except hyphens and spaces
    text = re.sub(r"[^\w\s-]", " ", text)
    # 5. Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_name(name: str) -> str:
    """Normalize a parking lot name, stripping provider prefixes if present."""
    # Remove common provider suffixes like "– ParkWhiz" or "- SpotHero"
    name = re.sub(r"[-–]\s*(parkwhiz|spothero|cheap airport parking)\s*$", "", name, flags=re.IGNORECASE)
    return normalize(name)


def normalize_address(address: str) -> str:
    """Normalize a street address string."""
    return normalize(address)
