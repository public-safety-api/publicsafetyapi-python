from __future__ import annotations

from typing import Optional, Union

import httpx

from . import __version__
from ._client import EntityType, _types_csv
from ._http import _raise_for_error
from ._models import Jurisdiction, Station, StateListItem, StateSummary

BASE_URL = "https://api.publicsafetyapi.dev"


class _AsyncStationsResource:
    def __init__(self, http: httpx.AsyncClient):
        self._http = http

    async def list(
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
        resp = await self._http.get("/v1/stations", params=params)
        _raise_for_error(resp)
        return [Station._from_dict(s) for s in resp.json()["data"]]

    async def get(self, station_id: str) -> Station:
        resp = await self._http.get(f"/v1/stations/{station_id}")
        _raise_for_error(resp)
        return Station._from_dict(resp.json()["data"])

    async def nearby(
        self,
        *,
        address: Optional[str] = None,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        type: Optional[Union[EntityType, list[EntityType]]] = None,
        radius_miles: float = 10,
        limit: int = 5,
    ) -> list[Station]:
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
        resp = await self._http.get("/v1/stations/nearby", params=params)
        _raise_for_error(resp)
        return [Station._from_dict(s) for s in resp.json()["data"]]


class _AsyncStatesResource:
    def __init__(self, http: httpx.AsyncClient):
        self._http = http

    async def list(self) -> list[StateListItem]:
        resp = await self._http.get("/v1/states")
        _raise_for_error(resp)
        return [StateListItem._from_dict(s) for s in resp.json()["data"]]

    async def summary(self, code: str) -> StateSummary:
        resp = await self._http.get(f"/v1/states/{code.upper()}/summary")
        _raise_for_error(resp)
        return StateSummary._from_dict(resp.json()["data"])


class AsyncPublicSafetyAPI:
    """
    Asynchronous client for publicsafetyapi.dev. Mirrors PublicSafetyAPI's surface.

    Usage:
        import asyncio
        from publicsafetyapi import AsyncPublicSafetyAPI

        async def main():
            async with AsyncPublicSafetyAPI(api_key="psk_live_...") as client:
                stations = await client.stations.nearby(address="...", type="fire")
                print(stations[0].name)

        asyncio.run(main())
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
        self._http = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
            headers={
                "X-API-Key": api_key,
                "User-Agent": f"publicsafetyapi-python/{__version__} async",
            },
        )
        self.stations = _AsyncStationsResource(self._http)
        self.states = _AsyncStatesResource(self._http)

    async def jurisdiction(
        self,
        *,
        address: Optional[str] = None,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        type: EntityType = "police",
    ) -> Jurisdiction:
        params: dict = {"type": type}
        if address:
            params["address"] = address
        if lat is not None:
            params["lat"] = lat
        if lng is not None:
            params["lng"] = lng
        resp = await self._http.get("/v1/jurisdiction", params=params)
        _raise_for_error(resp)
        body = resp.json()
        merged = {**body["data"]}
        if "jurisdictionNote" in body:
            merged["jurisdictionNote"] = body["jurisdictionNote"]
        return Jurisdiction._from_dict(merged)

    async def health(self) -> dict:
        resp = await self._http.get("/v1/health")
        _raise_for_error(resp)
        return resp.json()

    async def close(self) -> None:
        await self._http.aclose()

    async def __aenter__(self) -> "AsyncPublicSafetyAPI":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()
