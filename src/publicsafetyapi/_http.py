import re

import httpx

from ._exceptions import (
    AuthenticationError,
    InvalidParamsError,
    NotFoundError,
    PublicSafetyAPIError,
    QuotaExceededError,
    RateLimitError,
)


# Identifiers are interpolated into the request path, and httpx resolves that
# path against base_url, collapsing ".." segments. An unvalidated id such as
# "../../v2/internal/admin" would therefore send the request, with the
# caller's API key, to a different path on the API host; "?" and "#" would
# inject a query string or fragment. Allowlist rather than blocklist: every
# real identifier is alphanumeric with optional "-"/"_". fullmatch rather than
# match with "$", since "$" also matches just before a trailing newline.
_SAFE_ID = re.compile(r"[A-Za-z0-9_-]{1,64}")


def _safe_id(value: object, field: str) -> str:
    """Return the identifier as a string, or raise if it could escape the path."""
    if isinstance(value, int) and not isinstance(value, bool):
        value = str(value)
    if not isinstance(value, str) or not _SAFE_ID.fullmatch(value):
        raise ValueError(
            f"{field} must contain only letters, digits, '-' or '_' "
            f"(got {value!r})"
        )
    return value


def _raise_for_error(response: httpx.Response) -> None:
    if response.status_code == 200:
        return
    try:
        detail = response.json().get("detail", {})
        if isinstance(detail, str):
            message, code = detail, None
        else:
            message = detail.get("message", response.text)
            code = detail.get("code")
    except Exception:
        message, code = response.text, None

    status = response.status_code
    if status == 400:
        raise InvalidParamsError(message, status_code=status, code=code)
    if status == 401:
        raise AuthenticationError(message, status_code=status, code=code)
    if status == 402:
        raise QuotaExceededError(message, status_code=status, code=code)
    if status == 404:
        raise NotFoundError(message, status_code=status, code=code)
    if status == 429:
        raise RateLimitError(message, status_code=status, code=code)
    raise PublicSafetyAPIError(message, status_code=status, code=code)
