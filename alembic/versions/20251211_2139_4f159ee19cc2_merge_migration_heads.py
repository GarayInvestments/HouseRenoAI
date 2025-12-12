"""merge_migration_heads

Revision ID: 4f159ee19cc2
Revises: 1fd9ea7652d5, qb_token_is_active, add_password_hash
Create Date: 2025-12-11 21:39:54.513040

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4f159ee19cc2'
down_revision: Union[str, None] = ('1fd9ea7652d5', 'qb_token_is_active', 'add_password_hash')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
