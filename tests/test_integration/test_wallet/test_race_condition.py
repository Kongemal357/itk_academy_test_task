import asyncio
import uuid
from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from src.api.v1.schemas.wallet import OperationType
from src.db.models import Wallet


@pytest.mark.integration
async def test_withdraw_race_condition_prevented(integration_client, db_session):
    wallet_uuid = uuid.uuid4()
    wallet = Wallet(uuid=wallet_uuid, balance=Decimal("1000"))
    db_session.add(wallet)
    await db_session.commit()

    async def withdraw_600():
        async with AsyncClient(
            transport=integration_client._transport, base_url="http://test"
        ) as client:
            return await client.post(
                f"/api/v1/wallets/{wallet_uuid}/operation",
                json={"operation_type": OperationType.WITHDRAW, "amount": "600"},
            )

    r1, r2 = await asyncio.gather(withdraw_600(), withdraw_600())

    statuses = {r1.status_code, r2.status_code}
    assert statuses == {200, 400}

    await db_session.refresh(wallet)
    assert wallet.balance == Decimal("400")


@pytest.mark.integration
async def test_concurrent_deposits(integration_client, db_session):
    wallet_uuid = uuid.uuid4()
    wallet = Wallet(uuid=wallet_uuid, balance=Decimal("0"))
    db_session.add(wallet)
    await db_session.commit()

    async def deposit_100():
        async with AsyncClient(
            transport=integration_client._transport, base_url="http://test"
        ) as client:
            return await client.post(
                f"/api/v1/wallets/{wallet_uuid}/operation",
                json={"operation_type": OperationType.DEPOSIT, "amount": "100"},
            )

    tasks = [deposit_100() for _ in range(10)]
    responses = await asyncio.gather(*tasks)

    assert all(r.status_code == 200 for r in responses)

    await db_session.refresh(wallet)
    assert wallet.balance == Decimal("1000")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_concurrent_blocked_row(integration_client, db_session, engine):
    wallet_uuid = uuid.uuid4()
    wallet = Wallet(uuid=wallet_uuid, balance=Decimal("1000"))
    db_session.add(wallet)
    await db_session.commit()

    async with engine.connect() as conn:
        async with conn.begin() as transaction:
            result = await conn.execute(
                select(Wallet).where(Wallet.uuid == wallet_uuid).with_for_update()
            )
            result.scalar_one()

            async with AsyncClient(
                transport=integration_client._transport, base_url="http://test"
            ) as client:
                # Без nowait — запрос подвиснет
                # Сервер будет ждать 10 сек (command_timeout), потом упадёт с 50
                response = await client.post(
                    f"/api/v1/wallets/{wallet_uuid}/operation",
                    json={"operation_type": "DEPOSIT", "amount": "500"},
                    timeout=15,  # ждём дольше, чем command_timeout
                )

            assert response.status_code == 408

            await transaction.rollback()
