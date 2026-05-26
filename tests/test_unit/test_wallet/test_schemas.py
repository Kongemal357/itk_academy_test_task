import uuid
from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.api.v1.schemas.wallet import (
    OperationType,
    WalletBalanceResponse,
    WalletOperationRequest,
    WalletOperationResponse,
)

# =============== WalletBalanceResponse ===============


@pytest.mark.unit
def test_balance_response_valid():
    random_uuid = uuid.uuid4()
    request = WalletBalanceResponse(uuid=random_uuid, balance=Decimal("1000"))
    assert request.uuid == random_uuid
    assert request.balance == Decimal("1000")


@pytest.mark.unit
def test_balance_response_invalid_uuid():
    with pytest.raises(ValidationError):
        WalletBalanceResponse(uuid="INVALID-UUID", balance=Decimal("1000"))


@pytest.mark.unit
def test_balance_response_negative_balance():
    random_uuid = uuid.uuid4()
    with pytest.raises(ValidationError):
        WalletBalanceResponse(uuid=random_uuid, balance=Decimal("-1000"))


# =============== WalletOperationRequest ===============


@pytest.mark.unit
def test_operation_deposit_request_valid():
    request = WalletOperationRequest(
        operation_type=OperationType.DEPOSIT, amount=Decimal("1000")
    )
    assert request.operation_type == OperationType.DEPOSIT
    assert request.amount == Decimal("1000")


@pytest.mark.unit
def test_operation_withdraw_request_valid():
    request = WalletOperationRequest(
        operation_type=OperationType.WITHDRAW, amount=Decimal("1000")
    )
    assert request.operation_type == OperationType.WITHDRAW
    assert request.amount == Decimal("1000")


@pytest.mark.unit
def test_operation_request_invalid_type():
    with pytest.raises(ValidationError):
        WalletOperationRequest(operation_type="BAD-OPERATION", amount=Decimal("1000"))


@pytest.mark.unit
def test_operation_request_negative_amount():
    with pytest.raises(ValidationError):
        WalletOperationRequest(
            operation_type=OperationType.DEPOSIT, amount=Decimal("-100")
        )


@pytest.mark.unit
def test_operation_request_zero_amount():
    with pytest.raises(ValidationError):
        WalletOperationRequest(
            operation_type=OperationType.DEPOSIT, amount=Decimal("0")
        )


# =============== WalletOperationResponse ===============


@pytest.mark.unit
def test_operation_deposit_response_valid():
    random_uuid = uuid.uuid4()
    response = WalletOperationResponse(
        operation_type=OperationType.DEPOSIT,
        amount=Decimal("100"),
        uuid=random_uuid,
        balance=Decimal("1000"),
    )
    assert response.operation_type == OperationType.DEPOSIT
    assert response.amount == Decimal("100")
    assert response.uuid == random_uuid
    assert response.balance == Decimal("1000")


@pytest.mark.unit
def test_operation_deposit_response_valid_zero_balance():
    random_uuid = uuid.uuid4()
    response = WalletOperationResponse(
        operation_type=OperationType.DEPOSIT,
        amount=Decimal("100"),
        uuid=random_uuid,
        balance=Decimal("0"),
    )
    assert response.operation_type == OperationType.DEPOSIT
    assert response.amount == Decimal("100")
    assert response.uuid == random_uuid
    assert response.balance == Decimal("0")


@pytest.mark.unit
def test_operation_withdraw_response_valid():
    random_uuid = uuid.uuid4()
    response = WalletOperationResponse(
        operation_type=OperationType.WITHDRAW,
        amount=Decimal("100"),
        uuid=random_uuid,
        balance=Decimal("1000"),
    )
    assert response.operation_type == OperationType.WITHDRAW
    assert response.amount == Decimal("100")
    assert response.uuid == random_uuid
    assert response.balance == Decimal("1000")


@pytest.mark.unit
def test_operation_response_invalid_type():
    random_uuid = uuid.uuid4()
    with pytest.raises(ValidationError):
        WalletOperationResponse(
            operation_type="BAD-OPERATION",
            amount=Decimal("100"),
            uuid=random_uuid,
            balance=Decimal("1000"),
        )


@pytest.mark.unit
def test_operation_response_negative_amount():
    random_uuid = uuid.uuid4()
    with pytest.raises(ValidationError):
        WalletOperationResponse(
            operation_type=OperationType.DEPOSIT,
            amount=Decimal("-100"),
            uuid=random_uuid,
            balance=Decimal("1000"),
        )


@pytest.mark.unit
def test_operation_response_negative_balance():
    random_uuid = uuid.uuid4()
    with pytest.raises(ValidationError):
        WalletOperationResponse(
            operation_type=OperationType.DEPOSIT,
            amount=Decimal("100"),
            uuid=random_uuid,
            balance=Decimal("-1000"),
        )


@pytest.mark.unit
def test_operation_response_zero_amount():
    random_uuid = uuid.uuid4()
    with pytest.raises(ValidationError):
        WalletOperationResponse(
            operation_type=OperationType.DEPOSIT,
            amount=Decimal("0"),
            uuid=random_uuid,
            balance=Decimal("1000"),
        )
