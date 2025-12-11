"""add_invoice_payment_tracking_columns

Revision ID: 1792b711773f
Revises: 7efbcd4142a3
Create Date: 2025-12-11 00:04:20.273770

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '1792b711773f'
down_revision: Union[str, None] = '7efbcd4142a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add payment tracking columns to invoices table."""
    
    # Add amount_paid column (tracks total payments received)
    op.add_column('invoices', sa.Column('amount_paid', sa.Numeric(12, 2), nullable=True, server_default='0'))
    
    # Add balance_due column (calculated: total_amount - amount_paid)
    op.add_column('invoices', sa.Column('balance_due', sa.Numeric(12, 2), nullable=True))
    
    # Initialize balance_due for existing records
    op.execute('UPDATE invoices SET balance_due = COALESCE(total_amount, 0) - COALESCE(amount_paid, 0)')


def downgrade() -> None:
    """Remove payment tracking columns from invoices table."""
    
    op.drop_column('invoices', 'balance_due')
    op.drop_column('invoices', 'amount_paid')
