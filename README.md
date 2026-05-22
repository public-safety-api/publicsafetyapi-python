# publicsafetyapi-sdk

**Python SDK for [publicsafetyapi.dev](https://publicsafetyapi.dev)** — the developer API for US public safety facility data.

Every police station, fire station, hospital, and EMS location in the United States — sourced from HIFLD (DHS/CISA) and CMS federal datasets — in a single clean REST API.

---

## Installation

```bash
pip install publicsafetyapi-sdk
```

## Quick Start

```python
from publicsafetyapi import PublicSafetyAPI

client = PublicSafetyAPI(api_key="psk_live_...")

# Find the 5 nearest fire stations to any US address
stations = client.stations.nearby(
    address="12865 Main St, Apple Valley, CA",
    type="fire",
    radius_miles=10
)
for s in stations:
    print(f"{s.name} — {s.distance_miles:.1f} mi")

# Which police department has jurisdiction over an address?
result = client.jurisdiction(
    address="12865 Main St, Apple Valley, CA",
    type="police"
)
print(result.likely_agencies[0].name)  # "Apple Valley Police Department"

# Look up any facility by ID
hospital = client.stations.get("hospital-hifld-112233")
print(hospital.trauma_level)    # "Level II"
print(hospital.beds)            # 212
print(hospital.cms_ccn)         # "050317"
```

## What's Covered

| Entity Type | Source | Records |
|-------------|--------|---------|
| Police stations | HIFLD (DHS/CISA) | 68,000+ |
| Fire stations | HIFLD (DHS/CISA) | 55,000+ |
| EMS stations | HIFLD (DHS/CISA) | 10,000+ |
| Hospitals | HIFLD + CMS | 7,500+ |

## API Key

Get a free API key (500 calls/month) at **[publicsafetyapi.dev](https://publicsafetyapi.dev)**.

## Full SDK

The full SDK implementation ships with `v0.2.0` alongside the API launch.  
Sign up at [publicsafetyapi.dev](https://publicsafetyapi.dev) for early access.

## Related

- [districtapi-sdk](https://pypi.org/project/districtapi-sdk/) — US school districts
- [libraryapi-sdk](https://pypi.org/project/libraryapi-sdk/) — US public libraries

## License

MIT
