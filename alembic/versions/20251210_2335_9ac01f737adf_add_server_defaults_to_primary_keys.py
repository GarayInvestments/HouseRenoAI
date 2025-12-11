"""add_server_defaults_to_primary_keys

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
    """Add DEFAULT gen_random_uuid() to all UUID primary key columns."""
    
    # Enable the uuid-ossp extension if not already enabled
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
    
    # Add DEFAULT to all UUID primary key columns
    # These were defined in models with server_default=text("gen_random_uuid()")
    # but the database columns were created without DEFAULT clauses
    
    tables_and_pk_columns = [
        ('clients', 'client_id'),
        ('projects', 'project_id'),
        ('permits', 'permit_id'),
        ('inspections', 'inspection_id'),
        ('invoices', 'invoice_id'),
        ('payments', 'payment_id'),
        ('site_visits', 'visit_id'),  # Note: column is visit_id, not site_visit_id
    ]
    
    for table, column in tables_and_pk_columns:
        op.execute(f'ALTER TABLE {table} ALTER COLUMN {column} SET DEFAULT gen_random_uuid();')


def downgrade() -> None:
    """Remove DEFAULT from UUID primary key columns."""
    
    tables_and_pk_columns = [
        ('clients', 'client_id'),
        ('projects', 'project_id'),
        ('permits', 'permit_id'),
        ('inspections', 'inspection_id'),
        ('invoices', 'invoice_id'),
        ('payments', 'payment_id'),
        ('site_visits', 'visit_id'),  # Note: column is visit_id, not site_visit_id
    ]
    
    for table, column in tables_and_pk_columns:
        op.execute(f'ALTER TABLE {table} ALTER COLUMN {column} DROP DEFAULT;')
