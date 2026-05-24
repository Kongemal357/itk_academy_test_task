from decimal import Decimal
from enum import Enum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from src.api.v1.schemas.base import BaseResponse


class OperationType(str, Enum):
    """Type of wallet operation."""
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"


class WalletBalanceResponse(BaseResponse):
    """Response model for wallet balance endpoint."""

    result: Literal[True] = Field(
        default=True,
        title="Operation success status",
        description="Always true for successful balance retrieval",
    )
    uuid: UUID = Field(
        ...,
        title="Wallet UUID",
        description="UUID of the requested wallet",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    balance: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        title="Wallet balance",
        description="Current wallet balance, non-negative decimal with 2 decimal places",
        examples=[1500.00],
    )


class WalletOperationRequest(BaseModel):
    """Input model for wallet operation endpoint."""

    operation_type: OperationType = Field(
        ...,
        title="Type of operation",
        description="Operation of deposit or withdraw on wallet"
    )
    amount: Decimal = Field(
        ...,
        gt=0,
        decimal_places=2,
        title="Transaction amount",
        description="Amount to be transferred to the wallet, must be a non-negative integer",
    )


class WalletOperationResponse(BaseResponse):
    """Output model for wallet operation endpoint."""

    result: Literal[True] = Field(
        default=True,
        title="Operation success status",
        description="Always true for successful request",
    )
    operation_type:  OperationType = Field(
        ...,
        title="Type of operation",
        description="Operation of deposit or withdraw on wallet"
    )
    amount: Decimal = Field(
        ...,
        gt=0,
        decimal_places=2,
        title="Transaction amount",
        description="Amount to be transferred to the wallet, must be a non-negative integer",
    )
    uuid: UUID = Field(
        ...,
        title="Wallet UUID",
        description="UUID of the requested wallet",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    balance: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        title="Wallet balance",
        description="Current wallet balance after transaction, non-negative decimal with 2 decimal places",
        examples=[1500.00],
    )
