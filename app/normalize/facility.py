from copy import deepcopy

from app.models import ParkingLot
from app.normalize.utils import _to_float


def normalize_parking_lot(provider: str, raw_record: dict, airport_code: str) -> ParkingLot:
    """
    Convert a provider-specific raw record into the shared ParkingLot model.

    The normalized fields are kept intentionally small for matching, while the
    full provider-specific payload is preserved in raw_payload for traceability
    and downstream enrichment.
    """
    provider = provider.lower()
    raw_payload = deepcopy(raw_record)

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
            latitude=_to_float(raw_record.get("lat")),
            longitude=_to_float(raw_record.get("lng")),
            raw_payload=raw_payload,
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
            latitude=_to_float(raw_record.get("latitude")),
            longitude=_to_float(raw_record.get("longitude")),
            raw_payload=raw_payload,
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
            latitude=_to_float(geo.get("lat")),
            longitude=_to_float(geo.get("lng")),
            raw_payload=raw_payload,
        )

    raise ValueError(f"Unsupported provider: {provider}")