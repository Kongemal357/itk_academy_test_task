import asyncio
from uuid import UUID

from fastapi import APIRouter, Depends, Path, HTTPException
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.api.v1.schemas.wallet import WalletBalanceResponse, WalletOperationResponse, \
    WalletOperationRequest, OperationType
from src.db.database import get_session
from src.db.crud import get_wallet_by_uuid, select_wallet_for_update_by_uuid
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


@router.post(
    "/{wallet_uuid}/operation",
    response_model=WalletOperationResponse,
    responses=error_dict_400_404_409_422_500,
    summary="Perform a deposit or withdrawal operation",
    description="""
    Performs a DEPOSIT or WITHDRAW on a wallet.
    Concurrent requests are handled atomically via row-level locking.
    """,
)
async def post_wallet_transaction(
        transaction: WalletOperationRequest,
        wallet_uuid: UUID = Path(
            ...,
            title="Wallet UUID",
            description="""
                UUID of the wallet to be used for the transaction.
                Must be a valid UUID v4 format.
                """,
        ),
        session: AsyncSession = Depends(get_session),
):
    """Processes a deposit or withdrawal transaction on a specific wallet.

    Retrieves the wallet with a row-level lock to ensure atomicity under
    concurrent requests. Validates sufficient funds for withdrawal operations
    before updating the balance.

    :param transaction: Operation details including operation type
        (DEPOSIT or WITHDRAW) and amount.
    :type transaction: WalletOperationRequest
    :param wallet_uuid: UUID of the wallet to perform the transaction on.
    :type wallet_uuid: UUID
    :param session: Database session dependency for executing queries.
    :type session: AsyncSession

    :return: Response containing the wallet UUID, updated balance,
        operation type, and transaction amount.
    :rtype: WalletOperationResponse

    :raises HTTPException 400: If insufficient funds for withdrawal
        or invalid operation type.
    :raises HTTPException 404: If the wallet specified by wallet_uuid
        is not found in the database.
    :raises HTTPException 409: If a data integrity error occurs
        during the transaction.
    :raises HTTPException 500: If a database connection error
        or unexpected database error occurs.

    .. note::
        This endpoint uses row-level locking (SELECT ... FOR UPDATE)
        to prevent race conditions during concurrent operations on
        the same wallet.

    .. warning::
        The wallet must exist in the database, otherwise a 404 error
        will be returned. Withdrawal operations require sufficient funds.
    """
    try:
        wallet = await select_wallet_for_update_by_uuid(wallet_uuid=wallet_uuid, session=session)
        if not wallet:
            raise HTTPException(status_code=404, detail="Non-existent wallet uuid")

        if transaction.operation_type == OperationType.DEPOSIT:
            new_balance = wallet.balance + transaction.amount

        elif transaction.operation_type == OperationType.WITHDRAW:
            if wallet.balance < transaction.amount:
                raise HTTPException(
                    status_code=400,
                    detail="Insufficient funds"
                )
            else:
                new_balance = wallet.balance - transaction.amount

        else:
            raise HTTPException(status_code=500, detail="Invalid type operation")

        wallet.balance = new_balance
        await session.commit()

        return WalletOperationResponse(
            uuid=wallet.uuid,
            balance=new_balance,
            operation_type=transaction.operation_type,
            amount=transaction.amount,
        )

    except asyncio.TimeoutError:
        await session.rollback()
        raise HTTPException(status_code=408, detail="Request timeout")

    except HTTPException:
        await session.rollback()
        raise

    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Data integrity error")

    except OperationalError:
        await session.rollback()
        raise HTTPException(status_code=500, detail="Database connection error")

    except SQLAlchemyError:
        await session.rollback()
        raise HTTPException(status_code=500, detail="Database error")