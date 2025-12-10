"""convert_qb_cache_to_uuid

Revision ID: 8e3f2dda3aac
Revises: 9ea476eed090
Create Date: 2025-12-10 17:37:25.319825

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '8e3f2dda3aac'
down_revision: Union[str, None] = '9ea476eed090'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # QuickBooksCustomerCache: Add new UUID primary key column
    op.add_column('quickbooks_customers_cache', 
                  sa.Column('cache_id', postgresql.UUID(as_uuid=False), nullable=True))
    
    # Generate UUIDs for existing rows (if any)
    op.execute("UPDATE quickbooks_customers_cache SET cache_id = gen_random_uuid() WHERE cache_id IS NULL")
    
    # Make cache_id NOT NULL
    op.alter_column('quickbooks_customers_cache', 'cache_id', nullable=False)
    
    # Drop old primary key constraint
    op.drop_constraint('quickbooks_customers_cache_pkey', 'quickbooks_customers_cache', type_='primary')
    
    # Add new primary key on cache_id
    op.create_primary_key('quickbooks_customers_cache_pkey', 'quickbooks_customers_cache', ['cache_id'])
    
    # Make qb_customer_id unique instead of primary key
    op.create_unique_constraint('uq_qb_customers_cache_qb_id', 'quickbooks_customers_cache', ['qb_customer_id'])
    op.create_index('ix_quickbooks_customers_cache_qb_customer_id', 'quickbooks_customers_cache', ['qb_customer_id'])
    
    # QuickBooksInvoiceCache: Add new UUID primary key column
    op.add_column('quickbooks_invoices_cache', 
                  sa.Column('cache_id', postgresql.UUID(as_uuid=False), nullable=True))
    
    # Generate UUIDs for existing rows (if any)
    op.execute("UPDATE quickbooks_invoices_cache SET cache_id = gen_random_uuid() WHERE cache_id IS NULL")
    
    # Make cache_id NOT NULL
    op.alter_column('quickbooks_invoices_cache', 'cache_id', nullable=False)
    
    # Drop old primary key constraint
    op.drop_constraint('quickbooks_invoices_cache_pkey', 'quickbooks_invoices_cache', type_='primary')
    
    # Add new primary key on cache_id
    op.create_primary_key('quickbooks_invoices_cache_pkey', 'quickbooks_invoices_cache', ['cache_id'])
    
    # Make qb_invoice_id unique instead of primary key
    op.create_unique_constraint('uq_qb_invoices_cache_qb_id', 'quickbooks_invoices_cache', ['qb_invoice_id'])
    op.create_index('ix_quickbooks_invoices_cache_qb_invoice_id', 'quickbooks_invoices_cache', ['qb_invoice_id'])


def downgrade() -> None:
    # QuickBooksInvoiceCache: Reverse changes
    op.drop_index('ix_quickbooks_invoices_cache_qb_invoice_id', 'quickbooks_invoices_cache')
    op.drop_constraint('uq_qb_invoices_cache_qb_id', 'quickbooks_invoices_cache', type_='unique')
    op.drop_constraint('quickbooks_invoices_cache_pkey', 'quickbooks_invoices_cache', type_='primary')
    op.create_primary_key('quickbooks_invoices_cache_pkey', 'quickbooks_invoices_cache', ['qb_invoice_id'])
    op.drop_column('quickbooks_invoices_cache', 'cache_id')
    
    # QuickBooksCustomerCache: Reverse changes
    op.drop_index('ix_quickbooks_customers_cache_qb_customer_id', 'quickbooks_customers_cache')
    op.drop_constraint('uq_qb_customers_cache_qb_id', 'quickbooks_customers_cache', type_='unique')
    op.drop_constraint('quickbooks_customers_cache_pkey', 'quickbooks_customers_cache', type_='primary')
    op.create_primary_key('quickbooks_customers_cache_pkey', 'quickbooks_customers_cache', ['qb_customer_id'])
    op.drop_column('quickbooks_customers_cache', 'cache_id')
