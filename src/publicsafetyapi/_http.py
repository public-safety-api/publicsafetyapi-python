import httpx

from ._exceptions import (
    AuthenticationError,
    InvalidParamsError,
    NotFoundError,
    PublicSafetyAPIError,
    QuotaExceededError,
    RateLimitError,
)


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
