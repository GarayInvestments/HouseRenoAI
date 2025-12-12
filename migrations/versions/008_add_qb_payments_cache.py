"""Add QuickBooks payments cache table

Revision ID: 008_add_qb_payments_cache
Revises: 007
Create Date: 2025-12-12

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID


# revision identifiers, used by Alembic.
revision = '008_add_qb_payments_cache'
down_revision = '007_add_qb_invoices_cache'
branch_labels = None
depends_on = None


def upgrade():
    # Create quickbooks_payments_cache table
    op.create_table(
        'quickbooks_payments_cache',
        sa.Column('qb_payment_id', sa.String(50), primary_key=True),
        sa.Column('customer_id', sa.String(50), nullable=True, index=True),
        sa.Column('total_amount', sa.Numeric(12, 2), nullable=True),
        sa.Column('payment_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('payment_method', sa.String(50), nullable=True),
        sa.Column('payment_ref_num', sa.String(100), nullable=True),
        sa.Column('qb_data', JSONB, nullable=True),
        sa.Column('cached_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    
    # Create indexes
    op.create_index('ix_qb_payments_cached_at', 'quickbooks_payments_cache', ['cached_at'])
    op.create_index('ix_qb_payments_payment_date', 'quickbooks_payments_cache', ['payment_date'])
    op.create_index('ix_qb_payments_customer_id', 'quickbooks_payments_cache', ['customer_id'])


def downgrade():
    op.drop_table('quickbooks_payments_cache')
