from typing import Literal

from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    """Base response model with success flag."""

    result: bool = Field(
        ...,
        title="Operation success status",
        description="True if operation was successful",
    )


class ErrorResponse(BaseModel):
    """Error response model for API errors."""

    result: Literal[False] = Field(
        False,
        title="Operation success status",
        description="Always false for error responses",
    )
    error_type: str = Field(
        ..., title="Type of error", description="Class name or category of the error"
    )
    error_message: str = Field(
        ..., title="Error description", description="Human-readable error message"
    )
