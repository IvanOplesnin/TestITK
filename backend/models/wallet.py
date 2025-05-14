import asyncio
import enum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column

from backend.db import engine


class TypeOperation(enum.Enum):
    withdraw = "WITHDRAW"
    deposit = "DEPOSIT"


class Base(DeclarativeBase):
    pass


class Wallet(Base):
    __tablename__ = "wallet"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    uuid: Mapped[str] = mapped_column(nullable=False, unique=True)
    balance: Mapped[int] = mapped_column(nullable=0, default=0)

    transactions: Mapped[list["WalletOperation"]] = relationship(
        back_populates="wallet",
        passive_deletes=True
    )

    def __repr__(self):
        return f"Wallet(id={self.id}, uuid={self.uuid}, balance={self.balance})"


class WalletOperation(Base):
    __tablename__ = "wallet_transaction"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    uuid: Mapped[str] = mapped_column(nullable=False, unique=True)
    id_wallet: Mapped[int] = mapped_column(
        ForeignKey("wallet.id", ondelete="CASCADE"),
        nullable=False
    )
    type: Mapped[TypeOperation] = mapped_column(nullable=False)
    amount: Mapped[int] = mapped_column(nullable=False)

    wallet: Mapped["Wallet"] = relationship(back_populates="transactions")

    def __repr__(self):
        return (f"WalletTransaction(id={self.id}, "
                f"uuid={self.uuid}, "
                f"id_wallet={self.id_wallet}, "
                f"type={self.type}, "
                f"amount={self.amount})")


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(
            Base.metadata.create_all
        )


if __name__ == "__main__":
    asyncio.run(init_db())
