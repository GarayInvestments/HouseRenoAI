"""add_quickbooks_invoice_fields

Revision ID: e3b3d8b8d28d
Revises: 044de0a80b9e
Create Date: 2025-12-15 12:57:52.754944

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e3b3d8b8d28d'
down_revision: Union[str, None] = '044de0a80b9e'  # String, not number
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add QuickBooks-specific invoice fields
    op.add_column('invoices', sa.Column('email_status', sa.String(50), nullable=True, comment='QB email status: NotSet, NeedToSend, EmailSent'))
    op.add_column('invoices', sa.Column('print_status', sa.String(50), nullable=True, comment='QB print status: NotSet, NeedToPrint, PrintComplete'))
    op.add_column('invoices', sa.Column('bill_email', sa.String(255), nullable=True, comment='Customer billing email from QB'))
    op.add_column('invoices', sa.Column('bill_address', sa.JSON(), nullable=True, comment='Billing address from QB (JSONB)'))
    op.add_column('invoices', sa.Column('ship_address', sa.JSON(), nullable=True, comment='Shipping address from QB (JSONB)'))
    op.add_column('invoices', sa.Column('currency_code', sa.String(3), nullable=True, comment='Currency code (USD, etc)'))
    op.add_column('invoices', sa.Column('payment_terms', sa.String(50), nullable=True, comment='QB payment terms (Net 10, Net 30, etc)'))
    op.add_column('invoices', sa.Column('qb_metadata', sa.JSON(), nullable=True, comment='QB metadata (CreateTime, LastUpdatedTime)'))
    op.add_column('invoices', sa.Column('private_note', sa.Text(), nullable=True, comment='Internal notes from QB'))
    op.add_column('invoices', sa.Column('customer_memo', sa.Text(), nullable=True, comment='Message to customer from QB'))
    
    # Create indexes for commonly queried fields
    op.create_index('ix_invoices_email_status', 'invoices', ['email_status'])
    op.create_index('ix_invoices_print_status', 'invoices', ['print_status'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_invoices_print_status', 'invoices')
    op.drop_index('ix_invoices_email_status', 'invoices')
    
    # Drop columns
    op.drop_column('invoices', 'customer_memo')
    op.drop_column('invoices', 'private_note')
    op.drop_column('invoices', 'qb_metadata')
    op.drop_column('invoices', 'payment_terms')
    op.drop_column('invoices', 'currency_code')
    op.drop_column('invoices', 'ship_address')
    op.drop_column('invoices', 'bill_address')
    op.drop_column('invoices', 'bill_email')
    op.drop_column('invoices', 'print_status')
    op.drop_column('invoices', 'email_status')
