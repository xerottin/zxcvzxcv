"""empty message

Revision ID: 50c235054b68
Revises: ca495d320871
Create Date: 2025-08-03 19:26:57.178708

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '50c235054b68'
down_revision: Union[str, None] = 'ca495d320871'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("ALTER TYPE order_status ADD VALUE IF NOT EXISTS 'out_for_delivery'")
    op.execute("ALTER TYPE order_status ADD VALUE IF NOT EXISTS 'completed'")


def downgrade():
    pass