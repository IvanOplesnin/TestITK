from fastapi import APIRouter, HTTPException
from fastapi.params import Depends

from backend.db import get_session
from backend.schemas import OperationRequest, WalletResponse
from backend.crud import update_wallet, get_wallet_by_uuid

wallet_router = APIRouter(
    prefix="/api/v1/wallets"
)


@wallet_router.post("/{wallet_uuid}/operation")
async def create_operation(
        wallet_uuid: str,
        operation: OperationRequest,
        session=Depends(get_session)
):
    new_operation = await update_wallet(
        session=session,
        wallet_uuid=wallet_uuid,
        amount=operation.amount,
        operation_uuid=operation.operation_uuid,
        type_operation=operation.operation_type
    )
    return new_operation


@wallet_router.get("/{wallet_uuid}", response_model=WalletResponse)
async def get_wallet(wallet_uuid: str, session=Depends(get_session)):
    if wallet_uuid:
        wallet = await get_wallet_by_uuid(session=session, wallet_uuid=wallet_uuid)
        if wallet:
            return wallet
        else:
            raise HTTPException(status_code=404, detail="Wallet not found")
