from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Error response model for API errors."""

    error_type: str = Field(
        ..., title="Type of error", description="Class name or category of the error"
    )
    error_message: str = Field(
        ..., title="Error description", description="Human-readable error message"
    )
