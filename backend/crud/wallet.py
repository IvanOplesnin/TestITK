import uuid

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud.operation import get_wallet_operation_by_uuid
from backend.models.wallet import Wallet, WalletOperation


def create_uuid():
    return str(uuid.uuid1())


async def create_wallet(session: AsyncSession):
    while True:
        new_uuid = create_uuid()
        if not await get_wallet_by_uuid(session, new_uuid):
            break

    new_wallet = Wallet(uuid=new_uuid, balance=0)
    session.add(new_wallet)
    await session.flush()
    await session.commit()
    return new_wallet.id


async def get_wallet_by_uuid(session: AsyncSession, wallet_uuid: str):
    stmt = select(Wallet).where(Wallet.uuid == wallet_uuid)
    wallet = await session.execute(stmt)
    return wallet.scalar_one_or_none()


async def update_wallet(
        session: AsyncSession,
        wallet_id: str,
        amount: int,
        operation_uuid: str,
        type_operation: str
):
    transaction = await get_wallet_operation_by_uuid(session, operation_uuid)
    if transaction:
        raise HTTPException(status_code=400, detail="Transaction already exists")
    wallet = await get_wallet_by_uuid(session, wallet_id)
    direction = 1 if type_operation.lower() == 'deposit' else -1
    if wallet:
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
            return new_operation.id
        else:
            raise HTTPException(status_code=400, detail='Not enough money')
    else:
        raise HTTPException(status_code=400, detail='Not found wallet')
