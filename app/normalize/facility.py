from app.models import ParkingLot


def normalize_parking_lot(provider: str, raw_record: dict, airport_code: str) -> ParkingLot:
    """
    Convert a provider-specific raw record into the shared ParkingLot model.
    """
    provider = provider.lower()

    if provider == "parkwhiz":
        return ParkingLot(
            provider=provider,
            provider_lot_id=str(raw_record["listing_id"]),
            airport_code=airport_code.upper(),
            name=raw_record.get("location_name", ""),
            address1=raw_record.get("address"),
            city=raw_record.get("city"),
            state=raw_record.get("state"),
            postal_code=raw_record.get("postal_code"),
            latitude=raw_record.get("lat"),
            longitude=raw_record.get("lng"),
            raw_payload=raw_record,
        )

    if provider == "spothero":
        return ParkingLot(
            provider=provider,
            provider_lot_id=str(raw_record["facility_id"]),
            airport_code=airport_code.upper(),
            name=raw_record.get("facility_name", ""),
            address1=raw_record.get("street_address"),
            city=raw_record.get("municipality"),
            state=raw_record.get("region"),
            postal_code=raw_record.get("zip"),
            latitude=raw_record.get("latitude"),
            longitude=raw_record.get("longitude"),
            raw_payload=raw_record,
        )

    if provider == "cheap_airport_parking":
        geo = raw_record.get("geo") or {}
        return ParkingLot(
            provider=provider,
            provider_lot_id=str(raw_record["id"]),
            airport_code=airport_code.upper(),
            name=raw_record.get("title", ""),
            address1=raw_record.get("address_1"),
            city=raw_record.get("city_name"),
            state=raw_record.get("state_code"),
            postal_code=raw_record.get("zip_code"),
            latitude=geo.get("lat"),
            longitude=geo.get("lng"),
            raw_payload=raw_record,
        )

    raise ValueError(f"Unsupported provider: {provider}")