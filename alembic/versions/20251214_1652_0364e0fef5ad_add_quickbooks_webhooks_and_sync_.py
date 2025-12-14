"""add_quickbooks_webhooks_and_sync_infrastructure

Revision ID: 0364e0fef5ad
Revises: 0723fefbcd06
Create Date: 2025-12-14 16:52:48.009817

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0364e0fef5ad'
down_revision: Union[str, None] = '0723fefbcd06'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add columns to existing quickbooks_customers_cache
    op.add_column('quickbooks_customers_cache', sa.Column('qb_last_modified', sa.TIMESTAMP(timezone=True), nullable=True))
    op.add_column('quickbooks_customers_cache', sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False))
    op.add_column('quickbooks_customers_cache', sa.Column('sync_error', sa.Text(), nullable=True))
    op.create_index('ix_qb_customers_last_modified', 'quickbooks_customers_cache', ['qb_last_modified'])
    
    # 2. Add columns to existing quickbooks_invoices_cache
    op.add_column('quickbooks_invoices_cache', sa.Column('qb_last_modified', sa.TIMESTAMP(timezone=True), nullable=True))
    op.add_column('quickbooks_invoices_cache', sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False))
    op.add_column('quickbooks_invoices_cache', sa.Column('sync_error', sa.Text(), nullable=True))
    op.create_index('ix_qb_invoices_last_modified', 'quickbooks_invoices_cache', ['qb_last_modified'])
    
    # 3. Create quickbooks_payments_cache table
    op.create_table(
        'quickbooks_payments_cache',
        sa.Column('qb_payment_id', sa.String(50), primary_key=True, nullable=False),
        sa.Column('customer_id', sa.String(50), nullable=True),
        sa.Column('invoice_id', sa.String(50), nullable=True),
        sa.Column('amount', sa.Numeric(12, 2), nullable=True),
        sa.Column('payment_date', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('payment_method', sa.String(50), nullable=True),
        sa.Column('reference_number', sa.String(100), nullable=True),
        sa.Column('qb_data', sa.JSON(), nullable=True),
        sa.Column('qb_last_modified', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('sync_error', sa.Text(), nullable=True),
        sa.Column('cached_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False)
    )
    op.create_index('ix_qb_payments_cached_at', 'quickbooks_payments_cache', ['cached_at'])
    op.create_index('ix_qb_payments_customer_id', 'quickbooks_payments_cache', ['customer_id'])
    op.create_index('ix_qb_payments_invoice_id', 'quickbooks_payments_cache', ['invoice_id'])
    op.create_index('ix_qb_payments_last_modified', 'quickbooks_payments_cache', ['qb_last_modified'])
    
    # 4. Create webhook_events table
    op.create_table(
        'webhook_events',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('event_id', sa.String(100), unique=True, nullable=False),
        sa.Column('realm_id', sa.String(50), nullable=False),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=True),
        sa.Column('entity_ids', sa.JSON(), nullable=True),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('processed', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('processed_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('processing_error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False)
    )
    op.create_index('ix_webhook_events_event_id', 'webhook_events', ['event_id'])
    op.create_index('ix_webhook_events_processed', 'webhook_events', ['processed'])
    op.create_index('ix_webhook_events_created_at', 'webhook_events', ['created_at'])
    op.create_index('ix_webhook_events_entity_type', 'webhook_events', ['entity_type'])
    
    # 5. Create sync_status table
    op.create_table(
        'sync_status',
        sa.Column('entity_type', sa.String(50), primary_key=True, nullable=False),
        sa.Column('last_sync_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('last_sync_duration_ms', sa.Integer(), nullable=True),
        sa.Column('records_synced', sa.Integer(), nullable=True),
        sa.Column('sync_errors', sa.Integer(), server_default='0', nullable=False),
        sa.Column('last_error_message', sa.Text(), nullable=True),
        sa.Column('is_syncing', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('next_sync_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False)
    )
    op.create_index('ix_sync_status_last_sync_at', 'sync_status', ['last_sync_at'])
    
    # 6. Insert initial sync_status records for the three entity types
    op.execute("""
        INSERT INTO sync_status (entity_type, records_synced, sync_errors)
        VALUES 
            ('customers', 0, 0),
            ('invoices', 0, 0),
            ('payments', 0, 0)
    """)


def downgrade() -> None:
    # Drop new tables
    op.drop_table('sync_status')
    op.drop_table('webhook_events')
    op.drop_table('quickbooks_payments_cache')
    
    # Remove columns from quickbooks_invoices_cache
    op.drop_index('ix_qb_invoices_last_modified', 'quickbooks_invoices_cache')
    op.drop_column('quickbooks_invoices_cache', 'sync_error')
    op.drop_column('quickbooks_invoices_cache', 'is_active')
    op.drop_column('quickbooks_invoices_cache', 'qb_last_modified')
    
    # Remove columns from quickbooks_customers_cache
    op.drop_index('ix_qb_customers_last_modified', 'quickbooks_customers_cache')
    op.drop_column('quickbooks_customers_cache', 'sync_error')
    op.drop_column('quickbooks_customers_cache', 'is_active')
    op.drop_column('quickbooks_customers_cache', 'qb_last_modified')
