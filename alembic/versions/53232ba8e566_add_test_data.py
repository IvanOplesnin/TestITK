"""add test data

Revision ID: 53232ba8e566
Revises: 73eeaeee457b
Create Date: 2025-05-14 03:41:47.245974

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import table

# revision identifiers, used by Alembic.
revision: str = '53232ba8e566'
down_revision: Union[str, None] = '73eeaeee457b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    wallets = table(
        "wallet",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("uuid", sa.String, nullable=False, unique=True),
        sa.Column("balance", sa.Integer, nullable=False),
    )
    op.bulk_insert(
        wallets,
        [
            {"id": 1, "uuid": "1111111111", "balance": 1500},
            {"id": 2, "uuid": "2222222222", "balance": 1500},
            {"id": 3, "uuid": "3333333333", "balance": 1500},
            {"id": 4, "uuid": "4444444444", "balance": 1500},
            {"id": 5, "uuid": "5555555555", "balance": 1500},
        ]
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DELETE FROM wallet WHERE id IN (1,2,3,4,5);")
