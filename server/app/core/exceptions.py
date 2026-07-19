"""Base exception classes for consistent API error handling."""


class ApiError(Exception):
    """Base API error with HTTP status code."""

    def __init__(
        self,
        status_code: int,
        message: str,
        is_operational: bool = True,
    ) -> None:
        self.status_code = status_code
        self.message = message
        self.is_operational = is_operational
        super().__init__(self.message)


class NotFoundError(ApiError):
    """Resource not found (404)."""

    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(404, message)


class ValidationError(ApiError):
    """Validation error (422)."""

    def __init__(self, message: str = "Validation failed") -> None:
        super().__init__(422, message)


class ForbiddenError(ApiError):
    """Forbidden access (403)."""

    def __init__(self, message: str = "Forbidden") -> None:
        super().__init__(403, message)


class UnauthorizedError(ApiError):
    """Unauthorized access (401)."""

    def __init__(self, message: str = "Unauthorized") -> None:
        super().__init__(401, message)


class ConflictError(ApiError):
    """Resource conflict (409)."""

    def __init__(self, message: str = "Conflict") -> None:
        super().__init__(409, message)


class ServiceUnavailableError(ApiError):
    """Upstream/service unavailable (503)."""

    def __init__(self, message: str = "Service temporarily unavailable") -> None:
        super().__init__(503, message)
