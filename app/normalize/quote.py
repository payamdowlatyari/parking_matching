from copy import deepcopy

from app.models import ParkingQuote


def normalize_parking_quote(
    provider: str,
    raw_record: dict,
    airport_code: str,
    start_dt: str,
    end_dt: str,
) -> ParkingQuote:
    """
    Convert a provider-specific raw record into the shared ParkingQuote model.

    The quote model captures the fields needed for comparison/export while
    preserving the original provider payload in raw_payload.
    """
    provider = provider.lower()
    raw_payload = deepcopy(raw_record)

    if provider == "parkwhiz":
        return ParkingQuote(
            provider=provider,
            provider_quote_id=str(raw_record["quote_id"]),
            provider_lot_id=str(raw_record["listing_id"]),
            airport_code=airport_code.upper(),
            start_utc=start_dt,
            end_utc=end_dt,
            currency=raw_record.get("currency", "USD"),
            price_total=_to_float(raw_record.get("total_price")),
            raw_payload=raw_payload,
        )

    if provider == "spothero":
        return ParkingQuote(
            provider=provider,
            provider_quote_id=str(raw_record["quote_id"]),
            provider_lot_id=str(raw_record["listing_id"]),
            airport_code=airport_code.upper(),
            start_utc=start_dt,
            end_utc=end_dt,
            currency=raw_record.get("currency_code", "USD"),
            price_total=_to_float(raw_record.get("price")),
            raw_payload=raw_payload,
        )

    if provider == "cheapairportparking":
        return ParkingQuote(
            provider=provider,
            provider_quote_id=str(raw_record["quote_id"]),
            provider_lot_id=str(raw_record["listing_id"]),
            airport_code=airport_code.upper(),
            start_utc=start_dt,
            end_utc=end_dt,
            currency=raw_record.get("currency", "USD"),
            price_total=_to_float(raw_record.get("total_price")),
            raw_payload=raw_payload,
        )

    raise ValueError(f"Unsupported provider: {provider}")


def _to_float(value):
    """
    Safely convert numeric-like provider fields to float.
    """
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None