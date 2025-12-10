"""Expand ID columns to accommodate UUIDs (step 1)

Revision ID: 002_expand_id_columns
Revises: 001
Create Date: 2025-12-10 16:20:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002_expand_id_columns'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade():
    # Expand client_id column size
    op.alter_column('clients', 'client_id',
                   existing_type=sa.VARCHAR(length=16),
                   type_=sa.String(length=50),
                   existing_nullable=False)
    
    # Expand project_id column size
    op.alter_column('projects', 'project_id',
                   existing_type=sa.VARCHAR(length=16),
                   type_=sa.String(length=50),
                   existing_nullable=False)
    
    # Expand project client_id foreign key
    op.alter_column('projects', 'client_id',
                   existing_type=sa.VARCHAR(length=16),
                   type_=sa.String(length=50),
                   existing_nullable=True)
    
    # Expand permit_id column size
    op.alter_column('permits', 'permit_id',
                   existing_type=sa.VARCHAR(length=16),
                   type_=sa.String(length=50),
                   existing_nullable=False)
    
    # Expand permit project_id foreign key
    op.alter_column('permits', 'project_id',
                   existing_type=sa.VARCHAR(length=16),
                   type_=sa.String(length=50),
                   existing_nullable=True)
    
    # Expand permit client_id foreign key
    op.alter_column('permits', 'client_id',
                   existing_type=sa.VARCHAR(length=16),
                   type_=sa.String(length=50),
                   existing_nullable=True)
    
    # Expand payment_id column size
    op.alter_column('payments', 'payment_id',
                   existing_type=sa.VARCHAR(length=16),
                   type_=sa.String(length=50),
                   existing_nullable=False)
    
    # Expand payment project_id foreign key
    op.alter_column('payments', 'project_id',
                   existing_type=sa.VARCHAR(length=16),
                   type_=sa.String(length=50),
                   existing_nullable=True)
    
    # Expand payment client_id foreign key
    op.alter_column('payments', 'client_id',
                   existing_type=sa.VARCHAR(length=16),
                   type_=sa.String(length=50),
                   existing_nullable=True)

def downgrade():
    # Reverse all changes (back to VARCHAR(16))
    op.alter_column('payments', 'client_id',
                   existing_type=sa.String(length=50),
                   type_=sa.VARCHAR(length=16),
                   existing_nullable=True)
    
    op.alter_column('payments', 'project_id',
                   existing_type=sa.String(length=50),
                   type_=sa.VARCHAR(length=16),
                   existing_nullable=True)
    
    op.alter_column('payments', 'payment_id',
                   existing_type=sa.String(length=50),
                   type_=sa.VARCHAR(length=16),
                   existing_nullable=False)
    
    op.alter_column('permits', 'client_id',
                   existing_type=sa.String(length=50),
                   type_=sa.VARCHAR(length=16),
                   existing_nullable=True)
    
    op.alter_column('permits', 'project_id',
                   existing_type=sa.String(length=50),
                   type_=sa.VARCHAR(length=16),
                   existing_nullable=True)
    
    op.alter_column('permits', 'permit_id',
                   existing_type=sa.String(length=50),
                   type_=sa.VARCHAR(length=16),
                   existing_nullable=False)
    
    op.alter_column('projects', 'client_id',
                   existing_type=sa.String(length=50),
                   type_=sa.VARCHAR(length=16),
                   existing_nullable=True)
    
    op.alter_column('projects', 'project_id',
                   existing_type=sa.String(length=50),
                   type_=sa.VARCHAR(length=16),
                   existing_nullable=False)
    
    op.alter_column('clients', 'client_id',
                   existing_type=sa.String(length=50),
                   type_=sa.VARCHAR(length=16),
                   existing_nullable=False)
