"""merge_heads_before_webhooks

Revision ID: 0723fefbcd06
Revises: 65f97a541c93, 30dd24a3dbe6
Create Date: 2025-12-14 16:50:08.759252

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0723fefbcd06'
down_revision: Union[str, None] = ('65f97a541c93', '30dd24a3dbe6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
