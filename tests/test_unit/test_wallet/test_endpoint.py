import uuid

import pytest
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError

from src.api.v1.schemas.wallet import OperationType


# =============== GET /wallet/{uuid} ===============
@pytest.mark.unit
async def test_get_balance_200(unit_client, sample_wallet, mocker):
    mocker.patch(
        "src.api.v1.routes.wallet.get_wallet_by_uuid", return_value=sample_wallet
    )

    response = await unit_client.get(f"/api/v1/wallets/{sample_wallet.uuid}")

    assert response.status_code == 200
    assert response.json()["uuid"] == str(sample_wallet.uuid)
    assert response.json()["balance"] == "1000.00"


@pytest.mark.unit
async def test_get_balance_404(unit_client, mocker):
    other_uuid = uuid.uuid4()
    mocker.patch("src.api.v1.routes.wallet.get_wallet_by_uuid", return_value=None)

    response = await unit_client.get(f"/api/v1/wallets/{other_uuid}")

    assert response.status_code == 404
    assert response.json()["error_type"] == "HTTPException"


@pytest.mark.unit
async def test_get_balance_409(unit_client, sample_wallet, mocker):
    mocker.patch(
        "src.api.v1.routes.wallet.get_wallet_by_uuid",
        side_effect=IntegrityError("constraint violated", orig=None, params=None),
    )

    response = await unit_client.get(f"/api/v1/wallets/{sample_wallet.uuid}")

    assert response.status_code == 409
    assert response.json()["error_type"] == "HTTPException"
    assert response.json()["error_message"] == "Data integrity error"


@pytest.mark.unit
async def test_get_balance_500_db_connection(unit_client, sample_wallet, mocker):
    mocker.patch(
        "src.api.v1.routes.wallet.get_wallet_by_uuid",
        side_effect=OperationalError("connection failed", orig=None, params=None),
    )

    response = await unit_client.get(f"/api/v1/wallets/{sample_wallet.uuid}")

    assert response.status_code == 500
    assert response.json()["error_type"] == "HTTPException"
    assert response.json()["error_message"] == "Database connection error"


@pytest.mark.unit
async def test_get_balance_500_db_error(unit_client, sample_wallet, mocker):
    mocker.patch(
        "src.api.v1.routes.wallet.get_wallet_by_uuid",
        side_effect=SQLAlchemyError("db error"),
    )

    response = await unit_client.get(f"/api/v1/wallets/{sample_wallet.uuid}")

    assert response.status_code == 500
    assert response.json()["error_type"] == "HTTPException"
    assert response.json()["error_message"] == "Database error"


# =============== POST /wallet/{uuid}/operation ===============
@pytest.mark.unit
async def test_post_wallet_transaction_deposit_200(unit_client, sample_wallet, mocker):
    mocker.patch(
        "src.api.v1.routes.wallet.select_wallet_for_update_by_uuid",
        return_value=sample_wallet,
    )

    response = await unit_client.post(
        f"/api/v1/wallets/{sample_wallet.uuid}/operation",
        json={"operation_type": OperationType.DEPOSIT, "amount": 100},
    )

    assert response.status_code == 200
    assert response.json()["uuid"] == str(sample_wallet.uuid)
    assert response.json()["operation_type"] == OperationType.DEPOSIT
    assert response.json()["balance"] == "1100.00"  # 1000 + 100
    assert response.json()["amount"] == "100"


@pytest.mark.unit
async def test_post_wallet_transaction_withdraw_200(unit_client, sample_wallet, mocker):
    mocker.patch(
        "src.api.v1.routes.wallet.select_wallet_for_update_by_uuid",
        return_value=sample_wallet,
    )

    response = await unit_client.post(
        f"/api/v1/wallets/{sample_wallet.uuid}/operation",
        json={"operation_type": OperationType.WITHDRAW, "amount": 100},
    )

    assert response.status_code == 200
    assert response.json()["uuid"] == str(sample_wallet.uuid)
    assert response.json()["operation_type"] == OperationType.WITHDRAW
    assert response.json()["balance"] == "900.00"  # 1000 - 100
    assert response.json()["amount"] == "100"


@pytest.mark.unit
async def test_post_wallet_transaction_404_wallet_not_found(
    unit_client, sample_wallet, mocker
):
    mocker.patch(
        "src.api.v1.routes.wallet.select_wallet_for_update_by_uuid", return_value=None
    )

    response = await unit_client.post(
        f"/api/v1/wallets/{sample_wallet.uuid}/operation",
        json={"operation_type": OperationType.DEPOSIT, "amount": 100},
    )

    assert response.status_code == 404
    assert response.json()["error_type"] == "HTTPException"
    assert response.json()["error_message"] == "Non-existent wallet uuid"


@pytest.mark.unit
async def test_post_wallet_transaction_withdraw_400(unit_client, sample_wallet, mocker):
    mocker.patch(
        "src.api.v1.routes.wallet.select_wallet_for_update_by_uuid",
        return_value=sample_wallet,
    )

    response = await unit_client.post(
        f"/api/v1/wallets/{sample_wallet.uuid}/operation",
        json={
            "operation_type": OperationType.WITHDRAW,
            "amount": int(sample_wallet.balance) + 100,
        },
    )

    assert response.status_code == 400
    assert response.json()["error_type"] == "HTTPException"
    assert response.json()["error_message"] == "Insufficient funds"


@pytest.mark.unit
async def test_post_wallet_transaction_deposit_409(unit_client, sample_wallet, mocker):
    mocker.patch(
        "src.api.v1.routes.wallet.select_wallet_for_update_by_uuid",
        side_effect=IntegrityError("constraint violated", orig=None, params=None),
    )

    response = await unit_client.post(
        f"/api/v1/wallets/{sample_wallet.uuid}/operation",
        json={"operation_type": OperationType.DEPOSIT, "amount": 100},
    )

    assert response.status_code == 409
    assert response.json()["error_type"] == "HTTPException"
    assert response.json()["error_message"] == "Data integrity error"


@pytest.mark.unit
async def test_post_wallet_transaction_withdraw_409(unit_client, sample_wallet, mocker):
    mocker.patch(
        "src.api.v1.routes.wallet.select_wallet_for_update_by_uuid",
        side_effect=IntegrityError("constraint violated", orig=None, params=None),
    )

    response = await unit_client.post(
        f"/api/v1/wallets/{sample_wallet.uuid}/operation",
        json={"operation_type": OperationType.WITHDRAW, "amount": 100},
    )

    assert response.status_code == 409
    assert response.json()["error_type"] == "HTTPException"
    assert response.json()["error_message"] == "Data integrity error"


@pytest.mark.unit
async def test_post_wallet_transaction_deposit_500_db_connection(
    unit_client, sample_wallet, mocker
):
    mocker.patch(
        "src.api.v1.routes.wallet.select_wallet_for_update_by_uuid",
        side_effect=OperationalError("connection failed", orig=None, params=None),
    )

    response = await unit_client.post(
        f"/api/v1/wallets/{sample_wallet.uuid}/operation",
        json={"operation_type": OperationType.DEPOSIT, "amount": 100},
    )

    assert response.status_code == 500
    assert response.json()["error_type"] == "HTTPException"
    assert response.json()["error_message"] == "Database connection error"


@pytest.mark.unit
async def test_post_wallet_transaction_withdraw_500_db_connection(
    unit_client, sample_wallet, mocker
):
    mocker.patch(
        "src.api.v1.routes.wallet.select_wallet_for_update_by_uuid",
        side_effect=OperationalError("connection failed", orig=None, params=None),
    )

    response = await unit_client.post(
        f"/api/v1/wallets/{sample_wallet.uuid}/operation",
        json={"operation_type": OperationType.WITHDRAW, "amount": 100},
    )

    assert response.status_code == 500
    assert response.json()["error_type"] == "HTTPException"
    assert response.json()["error_message"] == "Database connection error"


@pytest.mark.unit
async def test_post_wallet_transaction_deposit_500_db_error(
    unit_client, sample_wallet, mocker
):
    mocker.patch(
        "src.api.v1.routes.wallet.select_wallet_for_update_by_uuid",
        side_effect=SQLAlchemyError("db error"),
    )

    response = await unit_client.post(
        f"/api/v1/wallets/{sample_wallet.uuid}/operation",
        json={"operation_type": OperationType.DEPOSIT, "amount": 100},
    )

    assert response.status_code == 500
    assert response.json()["error_type"] == "HTTPException"
    assert response.json()["error_message"] == "Database error"


@pytest.mark.unit
async def test_post_wallet_transaction_withdraw_500_db_error(
    unit_client, sample_wallet, mocker
):
    mocker.patch(
        "src.api.v1.routes.wallet.select_wallet_for_update_by_uuid",
        side_effect=SQLAlchemyError("db error"),
    )

    response = await unit_client.post(
        f"/api/v1/wallets/{sample_wallet.uuid}/operation",
        json={"operation_type": OperationType.WITHDRAW, "amount": 100},
    )

    assert response.status_code == 500
    assert response.json()["error_type"] == "HTTPException"
    assert response.json()["error_message"] == "Database error"
