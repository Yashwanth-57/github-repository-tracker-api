from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    NotFoundError,
    ConflictError,
    ExternalAPIError,
    ExternalAPITimeoutError
)


def error_response(status_code: int, message: str):
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "data": None,
            "error": message
        }
    )


async def global_exception_handler(request: Request, exc: Exception):

    if isinstance(exc, NotFoundError):
        return error_response(
            status_code=404,
            message="Repository not found"
        )

    if isinstance(exc, ConflictError):
        return error_response(
            status_code=409,
            message="Already exists"
        )

    if isinstance(exc, ExternalAPITimeoutError):
        return error_response(
            status_code=503,
            message="External timeout"
        )

    if isinstance(exc, ExternalAPIError):
        return error_response(
            status_code=502,
            message="External API error"
        )

    return error_response(
        status_code=500,
        message="Internal server error"
    )