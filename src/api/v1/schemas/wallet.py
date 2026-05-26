from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OperationType(str, Enum):
    """Type of wallet operation."""

    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"


class WalletBalanceResponse(BaseModel):
    """Response model for wallet balance endpoint."""

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
        description="""
        Current wallet balance, non-negative decimal with 2 decimal places
        """,
        examples=[1500.00],
    )

    model_config = ConfigDict(from_attributes=True)


class WalletOperationRequest(BaseModel):
    """Input model for wallet operation endpoint."""

    operation_type: OperationType = Field(
        ...,
        title="Type of operation",
        description="Operation of deposit or withdraw on wallet",
    )
    amount: Decimal = Field(
        ...,
        gt=0,
        decimal_places=2,
        title="Transaction amount",
        description="""
        Amount to be transferred to the wallet, must be a non-negative integer
        """,
    )


class WalletOperationResponse(BaseModel):
    """Output model for wallet operation endpoint."""

    operation_type: OperationType = Field(
        ...,
        title="Type of operation",
        description="Operation of deposit or withdraw on wallet",
    )
    amount: Decimal = Field(
        ...,
        gt=0,
        decimal_places=2,
        title="Transaction amount",
        description="""
        Amount to be transferred to the wallet, must be a non-negative integer
        """,
        examples=[100.00],
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
        description="""
        Current wallet balance after transaction,
        non-negative decimal with 2 decimal places
        """,
        examples=[1500.00],
    )

    model_config = ConfigDict(from_attributes=True)
