"""add_quickbooks_payment_fields

Revision ID: 83243f5ed087
Revises: e3b3d8b8d28d
Create Date: 2025-12-15 14:52:00.499668

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '83243f5ed087'
down_revision: Union[str, None] = 'e3b3d8b8d28d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add QuickBooks-specific payment fields
    op.add_column('payments', sa.Column('deposit_account', sa.String(length=50), nullable=True))
    op.add_column('payments', sa.Column('currency_code', sa.String(length=3), nullable=True))
    op.add_column('payments', sa.Column('total_amount', sa.Numeric(precision=12, scale=2), nullable=True))
    op.add_column('payments', sa.Column('unapplied_amount', sa.Numeric(precision=12, scale=2), nullable=True))
    op.add_column('payments', sa.Column('process_payment', sa.Boolean(), nullable=True))
    op.add_column('payments', sa.Column('linked_transactions', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('payments', sa.Column('qb_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('payments', sa.Column('private_note', sa.Text(), nullable=True))
    
    # Create indexes for commonly queried fields
    op.create_index(op.f('ix_payments_currency_code'), 'payments', ['currency_code'], unique=False)
    op.create_index(op.f('ix_payments_deposit_account'), 'payments', ['deposit_account'], unique=False)


def downgrade() -> None:
    # Drop indexes first
    op.drop_index(op.f('ix_payments_deposit_account'), table_name='payments')
    op.drop_index(op.f('ix_payments_currency_code'), table_name='payments')
    
    # Drop columns
    op.drop_column('payments', 'private_note')
    op.drop_column('payments', 'qb_metadata')
    op.drop_column('payments', 'linked_transactions')
    op.drop_column('payments', 'process_payment')
    op.drop_column('payments', 'unapplied_amount')
    op.drop_column('payments', 'total_amount')
    op.drop_column('payments', 'currency_code')
    op.drop_column('payments', 'deposit_account')

