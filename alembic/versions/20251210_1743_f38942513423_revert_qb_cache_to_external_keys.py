"""revert_qb_cache_to_external_keys

Revision ID: f38942513423
Revises: 8e3f2dda3aac
Create Date: 2025-12-10 17:43:01.944515

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'f38942513423'
down_revision: Union[str, None] = '8e3f2dda3aac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # QuickBooksCustomerCache: Revert to qb_customer_id as PK
    # Drop current UUID primary key
    op.drop_constraint('quickbooks_customers_cache_pkey', 'quickbooks_customers_cache', type_='primary')
    
    # Drop unique constraint and index on qb_customer_id (we'll make it PK)
    op.drop_constraint('uq_qb_customers_cache_qb_id', 'quickbooks_customers_cache', type_='unique')
    op.drop_index('ix_quickbooks_customers_cache_qb_customer_id', 'quickbooks_customers_cache')
    
    # Make qb_customer_id the primary key
    op.create_primary_key('quickbooks_customers_cache_pkey', 'quickbooks_customers_cache', ['qb_customer_id'])
    
    # Drop cache_id column
    op.drop_column('quickbooks_customers_cache', 'cache_id')
    
    # QuickBooksInvoiceCache: Revert to qb_invoice_id as PK
    # Drop current UUID primary key
    op.drop_constraint('quickbooks_invoices_cache_pkey', 'quickbooks_invoices_cache', type_='primary')
    
    # Drop unique constraint and index on qb_invoice_id (we'll make it PK)
    op.drop_constraint('uq_qb_invoices_cache_qb_id', 'quickbooks_invoices_cache', type_='unique')
    op.drop_index('ix_quickbooks_invoices_cache_qb_invoice_id', 'quickbooks_invoices_cache')
    
    # Make qb_invoice_id the primary key
    op.create_primary_key('quickbooks_invoices_cache_pkey', 'quickbooks_invoices_cache', ['qb_invoice_id'])
    
    # Drop cache_id column
    op.drop_column('quickbooks_invoices_cache', 'cache_id')


def downgrade() -> None:
    # QuickBooksCustomerCache: Add UUID primary key back
    op.add_column('quickbooks_customers_cache', 
                  sa.Column('cache_id', postgresql.UUID(as_uuid=False), nullable=True))
    
    op.execute("UPDATE quickbooks_customers_cache SET cache_id = gen_random_uuid() WHERE cache_id IS NULL")
    op.alter_column('quickbooks_customers_cache', 'cache_id', nullable=False)
    
    op.drop_constraint('quickbooks_customers_cache_pkey', 'quickbooks_customers_cache', type_='primary')
    op.create_primary_key('quickbooks_customers_cache_pkey', 'quickbooks_customers_cache', ['cache_id'])
    
    op.create_unique_constraint('uq_qb_customers_cache_qb_id', 'quickbooks_customers_cache', ['qb_customer_id'])
    op.create_index('ix_quickbooks_customers_cache_qb_customer_id', 'quickbooks_customers_cache', ['qb_customer_id'])
    
    # QuickBooksInvoiceCache: Add UUID primary key back
    op.add_column('quickbooks_invoices_cache', 
                  sa.Column('cache_id', postgresql.UUID(as_uuid=False), nullable=True))
    
    op.execute("UPDATE quickbooks_invoices_cache SET cache_id = gen_random_uuid() WHERE cache_id IS NULL")
    op.alter_column('quickbooks_invoices_cache', 'cache_id', nullable=False)
    
    op.drop_constraint('quickbooks_invoices_cache_pkey', 'quickbooks_invoices_cache', type_='primary')
    op.create_primary_key('quickbooks_invoices_cache_pkey', 'quickbooks_invoices_cache', ['cache_id'])
    
    op.create_unique_constraint('uq_qb_invoices_cache_qb_id', 'quickbooks_invoices_cache', ['qb_invoice_id'])
    op.create_index('ix_quickbooks_invoices_cache_qb_invoice_id', 'quickbooks_invoices_cache', ['qb_invoice_id'])
