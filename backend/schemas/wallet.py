from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


class OperationRequest(BaseModel):
    operation_uuid: str
    operation_type: Literal["DEPOSIT", "WITHDRAW"]
    amount: float = Field(gt=0)


class WalletResponse(BaseModel):
    id: int
    uuid: str
    balance: int

    model_config = ConfigDict(from_attributes=True)

