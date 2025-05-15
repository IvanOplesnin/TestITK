from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.wallet import WalletOperation


async def get_wallet_operation_by_uuid(session: AsyncSession, uuid: str) -> WalletOperation | None:
    if uuid:
        stmt = select(WalletOperation).where(WalletOperation.uuid == uuid)
        operation = await session.execute(stmt)
        operation = operation.scalar_one_or_none()
        return operation
