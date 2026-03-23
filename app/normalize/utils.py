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
