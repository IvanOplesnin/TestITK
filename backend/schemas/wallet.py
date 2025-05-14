from typing import Literal

from pydantic import BaseModel, Field


class OperationRequest(BaseModel):
    operation_uuid: str
    operation_type: Literal["DEPOSIT", "WITHDRAW"]
    amount: float = Field(gt=0)


class WalletResponse(BaseModel):
    wallet_id: int
    wallet_uuid: str
    balance: int

    class Config:
        from_attributes = True
