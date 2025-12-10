"""convert_id_columns_to_uuid_type

Revision ID: 6dbca8997444
Revises: 002_expand_id_columns
Create Date: 2025-12-10 17:31:21.839035

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '6dbca8997444'
down_revision: Union[str, None] = '002_expand_id_columns'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Convert client_id to UUID
    op.alter_column('clients', 'client_id',
                   existing_type=sa.String(length=50),
                   type_=postgresql.UUID(as_uuid=False),
                   existing_nullable=False,
                   postgresql_using='client_id::uuid')
    
    # Convert project_id to UUID
    op.alter_column('projects', 'project_id',
                   existing_type=sa.String(length=50),
                   type_=postgresql.UUID(as_uuid=False),
                   existing_nullable=False,
                   postgresql_using='project_id::uuid')
    
    # Convert project client_id foreign key to UUID
    op.alter_column('projects', 'client_id',
                   existing_type=sa.String(length=50),
                   type_=postgresql.UUID(as_uuid=False),
                   existing_nullable=True,
                   postgresql_using='client_id::uuid')
    
    # Convert permit_id to UUID
    op.alter_column('permits', 'permit_id',
                   existing_type=sa.String(length=50),
                   type_=postgresql.UUID(as_uuid=False),
                   existing_nullable=False,
                   postgresql_using='permit_id::uuid')
    
    # Convert permit project_id foreign key to UUID
    op.alter_column('permits', 'project_id',
                   existing_type=sa.String(length=50),
                   type_=postgresql.UUID(as_uuid=False),
                   existing_nullable=True,
                   postgresql_using='project_id::uuid')
    
    # Convert permit client_id foreign key to UUID
    op.alter_column('permits', 'client_id',
                   existing_type=sa.String(length=50),
                   type_=postgresql.UUID(as_uuid=False),
                   existing_nullable=True,
                   postgresql_using='client_id::uuid')
    
    # Convert payment_id to UUID
    op.alter_column('payments', 'payment_id',
                   existing_type=sa.String(length=50),
                   type_=postgresql.UUID(as_uuid=False),
                   existing_nullable=False,
                   postgresql_using='payment_id::uuid')
    
    # Convert payment project_id foreign key to UUID
    op.alter_column('payments', 'project_id',
                   existing_type=sa.String(length=50),
                   type_=postgresql.UUID(as_uuid=False),
                   existing_nullable=True,
                   postgresql_using='project_id::uuid')
    
    # Convert payment client_id foreign key to UUID
    op.alter_column('payments', 'client_id',
                   existing_type=sa.String(length=50),
                   type_=postgresql.UUID(as_uuid=False),
                   existing_nullable=True,
                   postgresql_using='client_id::uuid')


def downgrade() -> None:
    # Reverse all changes (back to VARCHAR(50))
    op.alter_column('payments', 'client_id',
                   existing_type=postgresql.UUID(as_uuid=False),
                   type_=sa.String(length=50),
                   existing_nullable=True,
                   postgresql_using='client_id::varchar')
    
    op.alter_column('payments', 'project_id',
                   existing_type=postgresql.UUID(as_uuid=False),
                   type_=sa.String(length=50),
                   existing_nullable=True,
                   postgresql_using='project_id::varchar')
    
    op.alter_column('payments', 'payment_id',
                   existing_type=postgresql.UUID(as_uuid=False),
                   type_=sa.String(length=50),
                   existing_nullable=False,
                   postgresql_using='payment_id::varchar')
    
    op.alter_column('permits', 'client_id',
                   existing_type=postgresql.UUID(as_uuid=False),
                   type_=sa.String(length=50),
                   existing_nullable=True,
                   postgresql_using='client_id::varchar')
    
    op.alter_column('permits', 'project_id',
                   existing_type=postgresql.UUID(as_uuid=False),
                   type_=sa.String(length=50),
                   existing_nullable=True,
                   postgresql_using='project_id::varchar')
    
    op.alter_column('permits', 'permit_id',
                   existing_type=postgresql.UUID(as_uuid=False),
                   type_=sa.String(length=50),
                   existing_nullable=False,
                   postgresql_using='permit_id::varchar')
    
    op.alter_column('projects', 'client_id',
                   existing_type=postgresql.UUID(as_uuid=False),
                   type_=sa.String(length=50),
                   existing_nullable=True,
                   postgresql_using='client_id::varchar')
    
    op.alter_column('projects', 'project_id',
                   existing_type=postgresql.UUID(as_uuid=False),
                   type_=sa.String(length=50),
                   existing_nullable=False,
                   postgresql_using='project_id::varchar')
    
    op.alter_column('clients', 'client_id',
                   existing_type=postgresql.UUID(as_uuid=False),
                   type_=sa.String(length=50),
                   existing_nullable=False,
                   postgresql_using='client_id::varchar')
