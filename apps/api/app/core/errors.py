from fastapi import Request, status
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Application-level error translated into an HTTP error response."""

    def __init__(
        self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


async def app_error_handler(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, AppError)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})