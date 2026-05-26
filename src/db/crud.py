import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.db import models


async def get_wallet_by_uuid(
    wallet_uuid: uuid.UUID,
    session: AsyncSession,
) -> Optional[models.Wallet]:
    """Retrieve a wallet by UUID. Returns None if not found."""
    wallet_result = await session.execute(
        select(models.Wallet).where(models.Wallet.uuid == wallet_uuid)
    )
    return wallet_result.scalar_one_or_none()


async def select_wallet_for_update_by_uuid(
    wallet_uuid: uuid.UUID,
    session: AsyncSession,
) -> Optional[models.Wallet]:
    """Retrieve a wallet by UUID with row-level lock for update.

    Uses SELECT ... FOR UPDATE to prevent concurrent modifications.
    Returns None if wallet not found.
    """
    wallet_result = await session.execute(
        select(models.Wallet).where(models.Wallet.uuid == wallet_uuid).with_for_update()
    )
    return wallet_result.scalar_one_or_none()
