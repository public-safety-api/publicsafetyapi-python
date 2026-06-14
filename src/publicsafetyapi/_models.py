"""Dataclass models for publicsafetyapi responses. Hand-rolled (no pydantic) to keep deps to httpx only."""
from dataclasses import dataclass, field, fields
from typing import Any, Optional, Union, get_args, get_origin


def _camel_to_snake(s: str) -> str:
    out: list[str] = []
    for i, ch in enumerate(s):
        if ch.isupper() and i > 0:
            out.append("_")
        out.append(ch.lower())
    return "".join(out)


_FIELD_TYPE_CACHE: dict[type, dict[str, Optional[type]]] = {}


def _resolve_dataclass_types(cls) -> dict[str, Optional[type]]:
    """For each field on cls, return the inner dataclass type (or None for scalars/lists)."""
    cached = _FIELD_TYPE_CACHE.get(cls)
    if cached is not None:
        return cached
    out: dict[str, Optional[type]] = {}
    for f in fields(cls):
        annot = f.type
        if isinstance(annot, str):
            cleaned = annot.replace("Optional[", "").rstrip("]").strip()
            out[f.name] = _DATACLASS_TYPES.get(cleaned)
            continue
        if get_origin(annot) is Union:
            inner = [a for a in get_args(annot) if a is not type(None)]
            if len(inner) == 1:
                annot = inner[0]
        out[f.name] = annot if isinstance(annot, type) and getattr(annot, "__module__", "") == __name__ else None
    _FIELD_TYPE_CACHE[cls] = out
    return out


def _from_dict(cls, data: Optional[dict]):
    """Build a dataclass instance from a camelCase dict, ignoring unknown keys."""
    if data is None:
        return None
    snake = {_camel_to_snake(k): v for k, v in data.items()}
    sub_types = _resolve_dataclass_types(cls)
    kwargs: dict[str, Any] = {}
    for f in fields(cls):
        v = snake.get(f.name)
        sub = sub_types[f.name]
        if v is None:
            # Preserve default (e.g. empty list) when key absent
            continue
        if sub is not None:
            kwargs[f.name] = sub._from_dict(v)
        else:
            kwargs[f.name] = v
    return cls(**kwargs)


_DATACLASS_TYPES: dict[str, type] = {}


@dataclass
class Address:
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    county: Optional[str] = None
    county_fips: Optional[str] = None

    @classmethod
    def _from_dict(cls, d):
        return _from_dict(cls, d)


@dataclass
class GeoPoint:
    lat: Optional[float] = None
    lng: Optional[float] = None

    @classmethod
    def _from_dict(cls, d):
        return _from_dict(cls, d)


@dataclass
class Station:
    station_id: Optional[str] = None
    entity_type: Optional[str] = None  # "police" | "fire" | "ems" | "hospital"
    facility_type: Optional[str] = None
    facility_type_label: Optional[str] = None
    name: Optional[str] = None
    address: Optional[Address] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    geo: Optional[GeoPoint] = None
    # Hospital-only fields (None for other types)
    cms_ccn: Optional[str] = None
    beds: Optional[int] = None
    trauma_level: Optional[str] = None
    has_helipad: Optional[bool] = None
    ownership_type: Optional[str] = None
    accreditation: Optional[str] = None
    # Populated only on /nearby responses
    distance_miles: Optional[float] = None
    status: Optional[str] = None

    @classmethod
    def _from_dict(cls, d):
        return _from_dict(cls, d)


@dataclass
class AgencySummary:
    """Condensed station record used inside a jurisdiction response."""
    station_id: Optional[str] = None
    entity_type: Optional[str] = None
    name: Optional[str] = None
    facility_type_label: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    status: Optional[str] = None

    @classmethod
    def _from_dict(cls, d):
        return _from_dict(cls, d)


@dataclass
class Jurisdiction:
    jurisdiction_id: Optional[str] = None
    boundary_type: Optional[str] = None      # "incorporated_place" | "county" | "tribal"
    boundary_source: Optional[str] = None    # "approximate" | "exact"
    place_name: Optional[str] = None
    state: Optional[str] = None
    geoid: Optional[str] = None
    likely_agencies: list[AgencySummary] = field(default_factory=list)
    jurisdiction_note: Optional[str] = None

    @classmethod
    def _from_dict(cls, d):
        if d is None:
            return None
        snake = {_camel_to_snake(k): v for k, v in d.items()}
        agencies = snake.get("likely_agencies") or []
        kwargs = {
            "jurisdiction_id":   snake.get("jurisdiction_id"),
            "boundary_type":     snake.get("boundary_type"),
            "boundary_source":   snake.get("boundary_source"),
            "place_name":        snake.get("place_name"),
            "state":             snake.get("state"),
            "geoid":             snake.get("geoid"),
            "likely_agencies":   [AgencySummary._from_dict(a) for a in agencies if a is not None],
            "jurisdiction_note": snake.get("jurisdiction_note"),
        }
        return cls(**kwargs)


@dataclass
class StateFacilities:
    police_stations: Optional[int] = None
    fire_stations: Optional[int] = None
    ems_stations: Optional[int] = None
    hospitals: Optional[int] = None
    total: Optional[int] = None

    @classmethod
    def _from_dict(cls, d):
        return _from_dict(cls, d)


@dataclass
class StateHospitals:
    total_licensed_beds: Optional[int] = None
    trauma_centers: Optional[int] = None

    @classmethod
    def _from_dict(cls, d):
        return _from_dict(cls, d)


@dataclass
class StateSummary:
    state: Optional[str] = None
    data_version: Optional[str] = None
    facilities: Optional[StateFacilities] = None
    hospitals: Optional[StateHospitals] = None

    @classmethod
    def _from_dict(cls, d):
        return _from_dict(cls, d)


@dataclass
class StateListItem:
    state: Optional[str] = None
    police_stations: Optional[int] = None
    fire_stations: Optional[int] = None
    ems_stations: Optional[int] = None
    hospitals: Optional[int] = None
    total_facilities: Optional[int] = None

    @classmethod
    def _from_dict(cls, d):
        return _from_dict(cls, d)


@dataclass
class ResponseMeta:
    request_id: Optional[str] = None
    credits_used: Optional[int] = None
    credits_remaining: Optional[int] = None

    @classmethod
    def _from_dict(cls, d):
        return _from_dict(cls, d)


@dataclass
class ResponseSource:
    provider: Optional[str] = None
    data_version: Optional[str] = None
    updated_at: Optional[str] = None
    freshness_days: Optional[int] = None

    @classmethod
    def _from_dict(cls, d):
        return _from_dict(cls, d)


for _cls in [
    Address, GeoPoint, Station, AgencySummary, Jurisdiction,
    StateFacilities, StateHospitals, StateSummary, StateListItem,
    ResponseMeta, ResponseSource,
]:
    _DATACLASS_TYPES[_cls.__name__] = _cls
