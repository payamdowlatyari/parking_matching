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
    """
    provider = provider.lower()

    if provider == "parkwhiz":
        return ParkingQuote(
            provider=provider,
            provider_quote_id=str(raw_record["quote_id"]),
            provider_lot_id=str(raw_record["listing_id"]),
            airport_code=airport_code.upper(),
            start_utc=start_dt,
            end_utc=end_dt,
            currency=raw_record.get("currency", "USD"),
            price_total=raw_record.get("total_price"),
            raw_payload=raw_record,
        )

    if provider == "spothero":
        return ParkingQuote(
            provider=provider,
            provider_quote_id=str(raw_record["rate_id"]),
            provider_lot_id=str(raw_record["facility_id"]),
            airport_code=airport_code.upper(),
            start_utc=start_dt,
            end_utc=end_dt,
            currency=raw_record.get("currency_code", "USD"),
            price_total=raw_record.get("price"),
            raw_payload=raw_record,
        )

    if provider == "cheap_airport_parking":
        pricing = raw_record.get("pricing") or {}
        return ParkingQuote(
            provider=provider,
            provider_quote_id=str(raw_record["quote_ref"]),
            provider_lot_id=str(raw_record["id"]),
            airport_code=airport_code.upper(),
            start_utc=start_dt,
            end_utc=end_dt,
            currency=pricing.get("currency", "USD"),
            price_total=pricing.get("total"),
            raw_payload=raw_record,
        )

    raise ValueError(f"Unsupported provider: {provider}")