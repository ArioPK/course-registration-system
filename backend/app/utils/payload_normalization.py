# backend/app/utils/payload_normalization.py

from __future__ import annotations

from typing import Any, Dict


def _coerce_int(v: Any) -> Any:
    """Coerce simple numeric strings to int; otherwise return as-is."""
    if isinstance(v, bool):
        return v  # avoid bool->int surprises; let schema validation handle it
    if isinstance(v, int):
        return v
    if isinstance(v, str):
        s = v.strip()
        try:
            # int("10") works; int(" 10 ") works; int("10.5") throws
            return int(s)
        except Exception:
            return v
    return v


def normalize_unit_limits_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Accept both snake_case and camelCase keys.

    Rules:
    - snake_case wins if both are present
    - maps minUnits -> min_units, maxUnits -> max_units
    - ignores unknown keys by returning only {min_units, max_units}
    - optionally coerces numeric strings to int
    """
    min_v = data.get("min_units", data.get("minUnits"))
    max_v = data.get("max_units", data.get("maxUnits"))

    out: Dict[str, Any] = {}
    if min_v is not None:
        out["min_units"] = _coerce_int(min_v)
    if max_v is not None:
        out["max_units"] = _coerce_int(max_v)
    return out
