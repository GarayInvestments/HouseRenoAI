"""add_server_default_to_payment_id

Revision ID: cba01e589593
Revises: 9075ee4dbe57
Create Date: 2025-12-10 22:41:37.103249

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'cba01e589593'
down_revision: Union[str, None] = '9075ee4dbe57'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add server_default to payment_id column
    op.alter_column('payments', 'payment_id',
                    server_default=sa.text('gen_random_uuid()'),
                    existing_type=postgresql.UUID(as_uuid=False),
                    existing_nullable=False)


def downgrade() -> None:
    # Remove server_default from payment_id column
    op.alter_column('payments', 'payment_id',
                    server_default=None,
                    existing_type=postgresql.UUID(as_uuid=False),
                    existing_nullable=False)
