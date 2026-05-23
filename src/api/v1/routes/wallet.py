from uuid import UUID

from fastapi import APIRouter, Depends, Path, HTTPException
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.api.v1.schemas.wallet import WalletBalanceResponse
from src.db.database import get_session
from src.db.crud import get_wallet_by_uuid
from src.utils.error_dict import error_dict_400_404_409_422_500

router = APIRouter(prefix="/wallets")


@router.get(
    "/{wallet_uuid}",
    response_model=WalletBalanceResponse,
    responses=error_dict_400_404_409_422_500,
    summary="Get wallet's balance",
    description="""
    Retrieves the current balance of a specific wallet.
    Returns the wallet UUID and its current balance. Does not require authentication.
    """,
)
async def get_balance(
        wallet_uuid: UUID = Path(
        ...,
        title="Wallet UUID",
        description="""
        The UUID of the wallet to retrieve balance for.
        Must be a valid UUID v4 format.
        """,
    ),
        session: AsyncSession = Depends(get_session),
):
    """Retrieves the current balance information for a specific wallet.

        Fetches the wallet's UUID and current balance based on the provided
        wallet UUID.

        :param wallet_uuid: UUID of the wallet to retrieve balance for.
        :type wallet_uuid: UUID
        :param session: Database session dependency for executing queries.
        :type session: AsyncSession

        :return: Response containing the wallet UUID and current balance.
        :rtype: WalletBalanceResponse

        :raises HTTPException 404: If the wallet specified by wallet_uuid is not found
        in the database.
        :raises HTTPException 500: If a database error occurs during query execution.

        .. note::
            This endpoint does not require authentication.

        .. warning::
            The wallet must exist in the database, otherwise a 404 error will be returned.
        """
    try:
        wallet = await get_wallet_by_uuid(wallet_uuid=wallet_uuid, session=session)
        if not wallet:
            raise HTTPException(status_code=404, detail="Non-existent wallet uuid.")

        return wallet
    except HTTPException:
        raise

    except IntegrityError:
        raise HTTPException(status_code=409, detail="Data integrity error")

    except OperationalError:
        raise HTTPException(status_code=500, detail="Database connection error")

    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")


async def post_wallet_transaction():
    pass