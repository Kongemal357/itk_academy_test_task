import traceback

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from src.api.v1.schemas.base import ErrorResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


def add_exception_handlers(app: FastAPI):
    """Adds custom exception handlers to the FastAPI application.

    Registers four exception handlers for different types of exceptions:
    - HTTP exceptions (StarletteHTTPException)
    - Database integrity errors (IntegrityError)
    - Request validation errors (RequestValidationError)
    - Generic unhandled exceptions (Exception)

    :param app: The FastAPI application instance to which handlers will be added.
    :type app: FastAPI

    :return: None
    :rtype: None

    .. note::
        This function should be called during application setup to ensure
        consistent error handling across all endpoints.

    .. warning::
        The generic exception handler will print the full traceback to stderr
        for debugging purposes, so ensure proper logging in production.
    """

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handles HTTP exceptions raised by the application.

        Converts StarletteHTTPException to a standardized JSON error response.

        :param request: The incoming request that caused the exception.
        :type request: Request
        :param exc: The caught HTTP exception.
        :type exc: StarletteHTTPException

        :return: JSON response with error details.
        :rtype: JSONResponse

        .. note::
            Preserves the original status code and detail message from the exception.
        """
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                result=False, error_type="HTTPException", error_message=exc.detail
            ).model_dump(),
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        """Handles database integrity errors.

        Converts SQLAlchemy IntegrityError to a standardized JSON error response.

        :param request: The incoming request that caused the exception.
        :type request: Request
        :param exc: The caught integrity error.
        :type exc: IntegrityError

        :return: JSON response with error details (status 400).
        :rtype: JSONResponse

        .. note::
            Returns HTTP 400 status code as integrity errors are typically
            caused by client-side data validation issues.
        """
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                result=False, error_type="IntegrityError", error_message=str(exc.orig)
            ).model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        """Handles request validation errors.

        Converts Pydantic RequestValidationError to a standardized JSON error response.
        Extracts the first validation error for cleaner error messages.

        :param request: The incoming request that caused the exception.
        :type request: Request
        :param exc: The caught validation error.
        :type exc: RequestValidationError

        :return: JSON response with error details (status 422).
        :rtype: JSONResponse

        .. note::
            Returns only the first validation error to simplify client error handling.
            Format: "field_name: error_message"
        """
        first_error = exc.errors()[0]
        error_message = f"{first_error['loc'][-1]}: {first_error['msg']}"
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                result=False, error_type="ValidationError", error_message=error_message
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """Handles all uncaught exceptions.

        Acts as a catch-all handler for any exceptions not handled by specific handlers.
        Prints traceback for debugging and returns a generic server error response.

        :param request: The incoming request that caused the exception.
        :type request: Request
        :param exc: The caught exception.
        :type exc: Exception

        :return: JSON response with error details (status 500).
        :rtype: JSONResponse

        .. warning::
            This handler will catch ALL exceptions, so ensure proper logging
            and avoid exposing sensitive information in production.
        """
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                result=False, error_type=type(exc).__name__, error_message=str(exc)
            ).model_dump(),
        )
