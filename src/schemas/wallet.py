from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class WalletIn(BaseModel):
    """Input model for wallet transaction."""

    operation_type:  Literal["DEPOSIT", "WITHDRAW"] = Field(
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



