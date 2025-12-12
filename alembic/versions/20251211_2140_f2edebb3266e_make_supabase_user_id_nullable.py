"""make_supabase_user_id_nullable

Revision ID: f2edebb3266e
Revises: 4f159ee19cc2
Create Date: 2025-12-11 21:40:51.724464

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f2edebb3266e'
down_revision: Union[str, None] = '4f159ee19cc2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Make supabase_user_id nullable to support local users without Supabase Auth
    op.alter_column('users', 'supabase_user_id',
                    existing_type=sa.UUID(),
                    nullable=True)


def downgrade() -> None:
    # Revert to non-nullable (requires data cleanup first)
    op.alter_column('users', 'supabase_user_id',
                    existing_type=sa.UUID(),
                    nullable=False)
