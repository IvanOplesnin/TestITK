import uuid

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud.operation import get_wallet_operation_by_uuid
from backend.lock_wallet import lock_wallet
from backend.models.wallet import Wallet, WalletOperation


def create_uuid() -> str:
    return str(uuid.uuid4())


async def create_wallet(session: AsyncSession):
    while True:
        new_uuid = create_uuid()
        if not await get_wallet_by_uuid(session, new_uuid):
            break

    new_wallet = Wallet(uuid=new_uuid, balance=0)
    session.add(new_wallet)
    await session.flush()
    await session.commit()
    return new_wallet.uuid


async def get_wallet_by_uuid(session: AsyncSession, wallet_uuid: str) -> Wallet | None:
    stmt = select(Wallet).where(Wallet.uuid == wallet_uuid)

    wallet = await session.execute(stmt)
    wallet = wallet.scalar_one_or_none()
    return wallet


async def update_wallet(
        session: AsyncSession,
        wallet_uuid: str,
        amount: int,
        operation_uuid: str,
        type_operation: str
):
    stmt = select(Wallet).where(Wallet.uuid == wallet_uuid).with_for_update()
    wallet = await session.execute(stmt)
    wallet = wallet.scalar_one_or_none()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    lock = lock_wallet.get_lock(wallet.uuid)
    async with lock:
        transaction = await get_wallet_operation_by_uuid(session, operation_uuid)
        if transaction:
            raise HTTPException(status_code=400, detail="Transaction already exists")

        direction = 1 if type_operation.lower() == 'deposit' else -1
        if wallet.balance + direction * amount >= 0:
            wallet.balance += direction * amount
            new_operation = WalletOperation(
                uuid=operation_uuid,
                type=type_operation.lower(),
                amount=amount,
                id_wallet=wallet.id
            )
            session.add(new_operation)
            await session.flush()
            await session.commit()
            return new_operation.uuid
        else:
            raise HTTPException(status_code=400, detail='Not enough money')
