# add_server_defaults_to_primary_keys

Revision ID: 9ac01f737adf
Revises: 62e3354db1d9
Create Date: 2025-12-10 23:35:41.365946

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9ac01f737adf'
down_revision: Union[str, None] = '62e3354db1d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
