import uuid
import pytest
from fastapi import status

WALLET1 = "00000000-0000-0000-0000-000000000001"
WALLET2 = "00000000-0000-0000-0000-000000000002"


@pytest.mark.asyncio
async def test_get_wallet(client):
    r = await client.get(f"/api/v1/wallets/{WALLET1}")
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert data["id"] == 1
    assert data["uuid"] == WALLET1
    assert data["balance"] == 100


@pytest.mark.asyncio
async def test_get_wallet_not_found(client):
    random_uuid = str(uuid.uuid4())
    r = await client.get(f"/api/v1/wallets/{random_uuid}")
    assert r.status_code == status.HTTP_404_NOT_FOUND
    data = r.json()
    assert data["detail"] == "Wallet not found"


@pytest.mark.asyncio
async def test_deposit_via_endpoint(client):
    new_op = str(uuid.uuid4())
    payload = {
        "operation_uuid": new_op,
        "operation_type": "DEPOSIT",
        "amount": 2000
    }
    r = await client.post(f"/api/v1/wallets/{WALLET1}/operation", json=payload)
    assert r.status_code == status.HTTP_200_OK
    op_id = r.json()
    assert op_id == new_op

    r2 = await client.get(f"/api/v1/wallets/{WALLET1}")
    data = r2.json()
    assert data["balance"] == 2100


@pytest.mark.asyncio
async def test_withdraw_insufficient_funds(client):
    op_uuid = str(uuid.uuid4())
    payload = {
        "operation_uuid": op_uuid,
        "operation_type": "WITHDRAW",
        "amount": 9999
    }
    r = await client.post(f"/api/v1/wallets/{WALLET2}/operation", json=payload)
    assert r.status_code == status.HTTP_400_BAD_REQUEST
    assert "Not enough money" in r.json()["detail"]


@pytest.mark.asyncio
async def test_idempotent_operation(client):
    op_uuid = str(uuid.uuid4())
    payload = {
        "operation_uuid": op_uuid,
        "operation_type": "DEPOSIT",
        "amount": 10
    }
    # первый запрос
    r1 = await client.post(f"/api/v1/wallets/{WALLET2}/operation", json=payload)
    assert r1.status_code == status.HTTP_200_OK

    # повторный — уже ошибка
    r2 = await client.post(f"/api/v1/wallets/{WALLET2}/operation", json=payload)
    assert r2.status_code == status.HTTP_400_BAD_REQUEST
    assert "Transaction already exists" in r2.json()["detail"]
