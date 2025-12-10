"""convert_user_id_to_uuid

Revision ID: 9ea476eed090
Revises: 6dbca8997444
Create Date: 2025-12-10 17:34:38.907006

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '9ea476eed090'
down_revision: Union[str, None] = '6dbca8997444'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # First expand the column to accommodate UUIDs
    op.alter_column('users', 'user_id',
                   existing_type=sa.VARCHAR(length=16),
                   type_=sa.String(length=50),
                   existing_nullable=False)
    
    # Note: Data conversion will need to be done separately if users table has data
    # For now, assuming empty or will be migrated separately
    
    # Convert to UUID type
    op.alter_column('users', 'user_id',
                   existing_type=sa.String(length=50),
                   type_=postgresql.UUID(as_uuid=False),
                   existing_nullable=False,
                   postgresql_using='user_id::uuid')


def downgrade() -> None:
    # Reverse back to VARCHAR(16)
    op.alter_column('users', 'user_id',
                   existing_type=postgresql.UUID(as_uuid=False),
                   type_=sa.VARCHAR(length=16),
                   existing_nullable=False,
                   postgresql_using='user_id::varchar')
