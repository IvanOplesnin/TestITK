import uuid

import pytest
from fastapi import HTTPException

from backend.crud import get_wallet_by_uuid, update_wallet, create_wallet


@pytest.mark.asyncio
async def test_deposit_and_withdraw(async_session):
    wallet_uuid = await create_wallet(async_session)
    assert isinstance(uuid.UUID(wallet_uuid), uuid.UUID)

    wallet = await get_wallet_by_uuid(async_session, wallet_uuid)
    assert wallet is not None
    assert wallet.balance == 0


@pytest.mark.asyncio
async def test_deposit_and_withdraw(async_session):
    wallet_uuid = await create_wallet(async_session)

    op1 = str(uuid.uuid4())
    await update_wallet(
        async_session,
        wallet_uuid=wallet_uuid,
        amount=100,
        operation_uuid=op1,
        type_operation="deposit"
    )
    wallet = await get_wallet_by_uuid(async_session, wallet_uuid)
    assert wallet.balance == 100

    op2 = str(uuid.uuid4())
    await update_wallet(
        async_session,
        wallet_uuid=wallet_uuid,
        amount=50,
        operation_uuid=op2,
        type_operation="withdraw"
    )
    wallet = await get_wallet_by_uuid(async_session, wallet_uuid)
    assert wallet.balance == 50


@pytest.mark.asyncio
async def test_overdraw_raises(async_session):
    wallet_uuid = await create_wallet(async_session)
    with pytest.raises(HTTPException) as exc:
        await update_wallet(
            async_session,
            wallet_uuid=wallet_uuid,
            amount=10,
            operation_uuid=str(uuid.uuid4()),
            type_operation="withdraw"
        )
    assert exc.value.status_code == 400
    assert "Not enough money" in exc.value.detail


@pytest.mark.asyncio
async def test_not_wallet_raises(async_session):
    with pytest.raises(HTTPException) as exc:
        await update_wallet(
            async_session,
            wallet_uuid="12313231",
            amount=10,
            operation_uuid=str(uuid.uuid4()),
            type_operation="withdraw"
        )
    assert exc.value.status_code == 404
    assert "Wallet not found" in exc.value.detail


@pytest.mark.asyncio
async def test_idempotency(async_session):
    wallet_uuid = await create_wallet(async_session)
    op_uuid = str(uuid.uuid4())

    await update_wallet(
        async_session,
        wallet_uuid=wallet_uuid,
        amount=20,
        operation_uuid=op_uuid,
        type_operation="deposit"
    )
    with pytest.raises(HTTPException) as exc:
        await update_wallet(
            async_session,
            wallet_uuid=wallet_uuid,
            amount=20,
            operation_uuid=op_uuid,
            type_operation="deposit"
        )
    assert exc.value.detail == "Transaction already exists"
