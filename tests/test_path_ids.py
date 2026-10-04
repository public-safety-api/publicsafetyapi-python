"""
Path-injection tests for identifiers interpolated into request paths.

Each identifier must be rejected with ValueError before any request is sent;
otherwise an id like "../../v2/internal/admin" redirects the request, with the
caller's API key, to another path on the API host. Offline: every request
goes to an httpx.MockTransport, so no API key or network access is needed.

Run:
    pytest -v tests/test_path_ids.py
"""
import asyncio

import httpx
import pytest

from publicsafetyapi import AsyncPublicSafetyAPI, PublicSafetyAPI, NotFoundError

BAD_IDS = [
    "../../v2/internal/admin",
    "..",
    ".",
    "a/b",
    "fire-hifld-13184?admin=1",
    "fire-hifld-13184#frag",
    "%2e%2e",
    "fire-hifld-13184\n",
    "fire-hifld-13184 ",
    "",
    "a" * 65,
    "\u0661\u0662\u0663",  # non-ASCII digits
    None,
    True,
]

CALLS = [
    ("stations.get", lambda c, i: c.stations.get(i), "fire-hifld-13184", "/v1/stations/fire-hifld-13184"),
    ("states.summary", lambda c, i: c.states.summary(i), "ca", "/v1/states/CA/summary"),
]


@pytest.fixture
def sent(monkeypatch):
    """Route every client the SDK builds through a transport that records requests."""
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(404, json={"detail": "not found"})

    transport = httpx.MockTransport(handler)
    for cls in (httpx.Client, httpx.AsyncClient):
        init = cls.__init__
        monkeypatch.setattr(
            cls, "__init__", lambda self, *a, _init=init, **kw: _init(self, *a, transport=transport, **kw)
        )
    return requests


def run(is_async, call, ident):
    if is_async:
        async def go():
            async with AsyncPublicSafetyAPI(api_key="test") as c:
                return await call(c, ident)
        return asyncio.run(go())
    with PublicSafetyAPI(api_key="test") as c:
        return call(c, ident)


@pytest.mark.parametrize("is_async", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("name,call,good,path", CALLS, ids=[c[0] for c in CALLS])
@pytest.mark.parametrize("bad", BAD_IDS, ids=repr)
def test_rejects_unsafe_id_before_request(sent, is_async, name, call, good, path, bad):
    with pytest.raises(ValueError, match="must contain only letters, digits"):
        run(is_async, call, bad)
    assert sent == []


@pytest.mark.parametrize("is_async", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("name,call,good,path", CALLS, ids=[c[0] for c in CALLS])
def test_accepts_real_id(sent, is_async, name, call, good, path):
    with pytest.raises(NotFoundError):
        run(is_async, call, good)
    assert [(r.url.host, r.url.raw_path.decode()) for r in sent] == [
        ("api.publicsafetyapi.dev", path)
    ]
