from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.db.database import get_session

router = APIRouter(prefix="/wallets")


@router.get("/{wallet_uuid}")
async def get_balance(
        wallet_uuid: UUID,
        session: AsyncSession = Depends(get_session),
):

    return {"uuid": wallet_uuid}