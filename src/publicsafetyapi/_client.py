from __future__ import annotations

from typing import Optional, Union

import httpx

from . import __version__
from ._http import _raise_for_error
from ._models import Jurisdiction, Station, StateListItem, StateSummary

BASE_URL = "https://api.publicsafetyapi.dev"

EntityType = str  # "police" | "fire" | "ems" | "hospital"


def _types_csv(t: Optional[Union[EntityType, list[EntityType]]]) -> Optional[str]:
    if t is None:
        return None
    if isinstance(t, str):
        return t
    return ",".join(t)


class _StationsResource:
    def __init__(self, http: httpx.Client):
        self._http = http

    def list(
        self,
        *,
        type: Optional[Union[EntityType, list[EntityType]]] = None,
        state: Optional[str] = None,
        county_fips: Optional[str] = None,
        zip: Optional[str] = None,
        name: Optional[str] = None,
        status: str = "OPEN",
        limit: int = 25,
        offset: int = 0,
    ) -> list[Station]:
        """Search stations by type, state, county FIPS, ZIP, or name."""
        params: dict = {"status": status, "limit": limit, "offset": offset}
        t = _types_csv(type)
        if t:
            params["type"] = t
        if state:
            params["state"] = state
        if county_fips:
            params["county_fips"] = county_fips
        if zip:
            params["zip"] = zip
        if name:
            params["name"] = name
        resp = self._http.get("/v1/stations", params=params)
        _raise_for_error(resp)
        return [Station._from_dict(s) for s in resp.json()["data"]]

    def get(self, station_id: str) -> Station:
        """Fetch a single station by its id, e.g. 'police-hifld-987654'."""
        resp = self._http.get(f"/v1/stations/{station_id}")
        _raise_for_error(resp)
        return Station._from_dict(resp.json()["data"])

    def nearby(
        self,
        *,
        address: Optional[str] = None,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        type: Optional[Union[EntityType, list[EntityType]]] = None,
        radius_miles: float = 10,
        limit: int = 5,
    ) -> list[Station]:
        """Find the nearest stations to an address or coordinate."""
        params: dict = {"radius_miles": radius_miles, "limit": limit}
        if address:
            params["address"] = address
        if lat is not None:
            params["lat"] = lat
        if lng is not None:
            params["lng"] = lng
        t = _types_csv(type)
        if t:
            params["type"] = t
        resp = self._http.get("/v1/stations/nearby", params=params)
        _raise_for_error(resp)
        return [Station._from_dict(s) for s in resp.json()["data"]]


class _StatesResource:
    def __init__(self, http: httpx.Client):
        self._http = http

    def list(self) -> list[StateListItem]:
        """List all US states with their facility counts."""
        resp = self._http.get("/v1/states")
        _raise_for_error(resp)
        return [StateListItem._from_dict(s) for s in resp.json()["data"]]

    def summary(self, code: str) -> StateSummary:
        """State-level rollup for a 2-letter state code."""
        resp = self._http.get(f"/v1/states/{code.upper()}/summary")
        _raise_for_error(resp)
        return StateSummary._from_dict(resp.json()["data"])


class PublicSafetyAPI:
    """
    Synchronous client for the publicsafetyapi.dev REST API.

    Usage:
        from publicsafetyapi import PublicSafetyAPI

        client = PublicSafetyAPI(api_key="psk_live_...")

        # Find the 5 nearest fire stations
        stations = client.stations.nearby(
            address="12865 Main St, Apple Valley, CA",
            type="fire",
            radius_miles=10,
        )
        print(stations[0].name, stations[0].distance_miles)

        # Jurisdiction lookup
        j = client.jurisdiction(
            address="12865 Main St, Apple Valley, CA",
            type="police",
        )
        print(j.likely_agencies[0].name)

    Args:
        api_key: Your publicsafetyapi.dev API key. Get one free at https://publicsafetyapi.dev/pricing.
        base_url: Override the API base URL (e.g. for staging).
        timeout: Per-request timeout in seconds (default 30).
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = BASE_URL,
        timeout: float = 30.0,
    ):
        if not api_key:
            raise ValueError("api_key is required. Get one at https://publicsafetyapi.dev/pricing")
        self._http = httpx.Client(
            base_url=base_url,
            timeout=timeout,
            headers={
                "X-API-Key": api_key,
                "User-Agent": f"publicsafetyapi-python/{__version__}",
            },
        )
        self.stations = _StationsResource(self._http)
        self.states = _StatesResource(self._http)

    def jurisdiction(
        self,
        *,
        address: Optional[str] = None,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        type: EntityType = "police",
    ) -> Jurisdiction:
        """
        Determine which agency has jurisdiction over a location.
        Provide either `address` or `lat`+`lng`. Costs 2 credits per call.
        """
        params: dict = {"type": type}
        if address:
            params["address"] = address
        if lat is not None:
            params["lat"] = lat
        if lng is not None:
            params["lng"] = lng
        resp = self._http.get("/v1/jurisdiction", params=params)
        _raise_for_error(resp)
        body = resp.json()
        merged = {**body["data"]}
        if "jurisdictionNote" in body:
            merged["jurisdictionNote"] = body["jurisdictionNote"]
        return Jurisdiction._from_dict(merged)

    def health(self) -> dict:
        """Hit /v1/health. Does not require an API key and does not consume credits."""
        resp = self._http.get("/v1/health")
        _raise_for_error(resp)
        return resp.json()

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "PublicSafetyAPI":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
