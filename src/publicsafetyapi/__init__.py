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
        radius_miles=10
    )
    print(stations[0].name, stations[0].distance_miles)

    # Which police department covers this address?
    result = client.jurisdiction(
        address="12865 Main St, Apple Valley, CA",
        type="police"
    )
    print(result.likely_agencies[0].name)  # "Apple Valley Police Department"

    # Look up a specific station
    station = client.stations.get("police-hifld-987654")
    print(station.phone)

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

__version__ = "0.1.0"

# Full implementation coming in v0.2.0 — launching with publicsafetyapi.dev
# Sign up for early access at https://publicsafetyapi.dev

__all__ = ["__version__"]
