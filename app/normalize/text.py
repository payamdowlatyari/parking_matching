import re

ABBREVIATIONS = {
    "st": "street",
    "rd": "road",
    "ave": "avenue",
    "blvd": "boulevard",
    "dr": "drive",
    "ln": "lane",
    "ct": "court",
    "intl": "international",
    "apt": "airport",
}

WEAK_NAME_TOKENS = {
    "parking",
    "airport",
    "lot",
    "garage",
    "self",
    "park",
}


def normalize_text(value: str | None) -> str:
    """
    Normalize general text fields for comparison.

    Steps:
    - lowercase
    - remove punctuation
    - collapse repeated whitespace
    - expand common abbreviations
    """
    if not value:
        return ""

    value = value.lower().strip()
    value = re.sub(r"[^\w\s]", " ", value)
    value = re.sub(r"\s+", " ", value).strip()

    parts = value.split()
    normalized_parts = [ABBREVIATIONS.get(part, part) for part in parts]

    return " ".join(normalized_parts)


def normalize_name(value: str | None) -> str:
    """
    Normalize facility names and remove weak/common tokens that often
    do not help distinguish one parking lot from another.
    """
    normalized = normalize_text(value)
    parts = [part for part in normalized.split() if part not in WEAK_NAME_TOKENS]
    return " ".join(parts)


def normalize_postal_code(value: str | None) -> str:
    """
    Normalize postal code by stripping whitespace and punctuation-like
    characters, keeping only letters, numbers, and hyphens.
    """
    if not value:
        return ""

    value = value.strip().upper()
    value = re.sub(r"[^A-Z0-9\-]", "", value)
    return value