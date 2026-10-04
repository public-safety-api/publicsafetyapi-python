"""
publicsafetyapi — Python SDK for the publicsafetyapi.dev API

US public safety facility data — police stations, fire stations, hospitals,
and EMS locations — sourced from HIFLD (DHS/CISA) and CMS federal datasets.

Usage:
    from publicsafetyapi import PublicSafetyAPI

    client = PublicSafetyAPI(api_key="psk_live_...")

    # Find nearest fire stations
    stations = client.stations.nearby(
        address="12865 Main St, Apple Valley, CA",
        type="fire",
        radius_miles=10,
    )
    print(stations[0].name, stations[0].distance_miles)

    # Which police department has jurisdiction?
    j = client.jurisdiction(
        address="12865 Main St, Apple Valley, CA",
        type="police",
    )
    print(j.likely_agencies[0].name)

    # Look up a specific station
    station = client.stations.get("police-hifld-987654")

Async:
    import asyncio
    from publicsafetyapi import AsyncPublicSafetyAPI

    async def main():
        async with AsyncPublicSafetyAPI(api_key="psk_live_...") as client:
            stations = await client.stations.nearby(address="...", type="fire")

    asyncio.run(main())

Docs:    https://publicsafetyapi.dev/docs
GitHub:  https://github.com/public-safety-api/publicsafetyapi-python
"""

__version__ = "0.2.1"

from ._async_client import AsyncPublicSafetyAPI
from ._client import PublicSafetyAPI
from ._exceptions import (
    AuthenticationError,
    InvalidParamsError,
    NotFoundError,
    PublicSafetyAPIError,
    QuotaExceededError,
    RateLimitError,
)
from ._models import (
    Address,
    AgencySummary,
    GeoPoint,
    Jurisdiction,
    ResponseMeta,
    ResponseSource,
    StateFacilities,
    StateHospitals,
    StateListItem,
    StateSummary,
    Station,
)

__all__ = [
    "__version__",
    "PublicSafetyAPI",
    "AsyncPublicSafetyAPI",
    # Models
    "Station",
    "Address",
    "GeoPoint",
    "AgencySummary",
    "Jurisdiction",
    "StateFacilities",
    "StateHospitals",
    "StateSummary",
    "StateListItem",
    "ResponseMeta",
    "ResponseSource",
    # Exceptions
    "PublicSafetyAPIError",
    "AuthenticationError",
    "QuotaExceededError",
    "NotFoundError",
    "RateLimitError",
    "InvalidParamsError",
]
