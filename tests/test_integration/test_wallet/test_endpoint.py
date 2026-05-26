import pytest
import uuid

from decimal import Decimal

from src.db.models import Wallet
from src.api.v1.schemas.wallet import OperationType


@pytest.mark.integration
async def test_deposit_valid(integration_client, db_session):
    deposit_value = Decimal("100")
    balance_value = Decimal("0")
    wallet_uuid = uuid.uuid4()
    wallet = Wallet(uuid=wallet_uuid, balance=balance_value)
    db_session.add(wallet)
    await db_session.commit()

    response = await integration_client.post(
        f"/api/v1/wallets/{wallet_uuid}/operation",
        json={
            "operation_type": OperationType.DEPOSIT,
            "amount": str(deposit_value)
        }
    )

    assert response.status_code == 200

    await db_session.refresh(wallet)
    assert wallet.balance == (balance_value + deposit_value)


@pytest.mark.integration
async def test_withdraw_valid(integration_client, db_session):
    withdraw_value = Decimal("100")
    balance_value = Decimal("1000")
    wallet_uuid = uuid.uuid4()
    wallet = Wallet(uuid=wallet_uuid, balance=balance_value)
    db_session.add(wallet)
    await db_session.commit()

    response = await integration_client.post(
        f"/api/v1/wallets/{wallet_uuid}/operation",
        json={
            "operation_type": OperationType.WITHDRAW,
            "amount": str(withdraw_value)
        }
    )

    assert response.status_code == 200

    await db_session.refresh(wallet)
    assert wallet.balance == (balance_value - withdraw_value)