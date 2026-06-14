class PublicSafetyAPIError(Exception):
    """Base exception for all publicsafetyapi errors."""

    def __init__(self, message: str, status_code: int | None = None, code: str | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.code = code

    def __repr__(self) -> str:
        return f"{type(self).__name__}({super().__str__()!r}, status_code={self.status_code}, code={self.code!r})"


class AuthenticationError(PublicSafetyAPIError):
    """401 — missing, invalid, or revoked API key."""


class QuotaExceededError(PublicSafetyAPIError):
    """402 — monthly quota reached or prepaid balance empty."""


class NotFoundError(PublicSafetyAPIError):
    """404 — station / jurisdiction not found, or no stations in radius."""


class RateLimitError(PublicSafetyAPIError):
    """429 — too many requests per minute."""


class InvalidParamsError(PublicSafetyAPIError):
    """400 — invalid query parameters or unresolvable address."""
