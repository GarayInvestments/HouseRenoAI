"""add_client_status_enum

Revision ID: e4374cb11fda
Revises: 0364e0fef5ad
Create Date: 2025-12-14 23:22:38.551083

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e4374cb11fda'
down_revision: Union[str, None] = '0364e0fef5ad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create ENUM type for client status
    client_status_enum = sa.Enum(
        'INTAKE',
        'ACTIVE', 
        'ON_HOLD',
        'COMPLETED',
        'ARCHIVED',
        name='client_status_enum',
        create_type=True
    )
    
    # Create the ENUM type in PostgreSQL
    client_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Migrate existing string values to ENUM-compatible values
    # Update any existing statuses to map to new ENUM
    op.execute("""
        UPDATE clients 
        SET status = CASE
            WHEN LOWER(status) IN ('active', 'current') THEN 'ACTIVE'
            WHEN LOWER(status) IN ('inactive', 'hold', 'paused') THEN 'ON_HOLD'
            WHEN LOWER(status) IN ('completed', 'finished', 'closed') THEN 'COMPLETED'
            WHEN LOWER(status) IN ('archived', 'deleted') THEN 'ARCHIVED'
            WHEN LOWER(status) IN ('lead', 'prospect', 'new') THEN 'INTAKE'
            ELSE 'INTAKE'
        END
        WHERE status IS NOT NULL
    """)
    
    # Alter the column to use the ENUM type
    op.alter_column(
        'clients',
        'status',
        type_=client_status_enum,
        postgresql_using='status::client_status_enum',
        existing_type=sa.String(50),
        existing_nullable=True,
        existing_server_default=None
    )


def downgrade() -> None:
    # Revert column to String type
    op.alter_column(
        'clients',
        'status',
        type_=sa.String(50),
        existing_type=sa.Enum(
            'INTAKE',
            'ACTIVE',
            'ON_HOLD', 
            'COMPLETED',
            'ARCHIVED',
            name='client_status_enum'
        ),
        existing_nullable=True
    )
    
    # Drop the ENUM type
    sa.Enum(name='client_status_enum').drop(op.get_bind(), checkfirst=True)
