"""add_jurisdictions_table

Revision ID: 1fd9ea7652d5
Revises: 1792b711773f
Create Date: 2025-12-11 08:18:48.030638

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1fd9ea7652d5'
down_revision: Union[str, None] = '1792b711773f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create jurisdictions table
    op.create_table(
        'jurisdictions',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('state', sa.String(length=2), nullable=False),
        sa.Column('requirements', sa.dialects.postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_jurisdictions_name', 'jurisdictions', ['name'])
    op.create_index('idx_jurisdictions_state', 'jurisdictions', ['state'])
    op.create_index('idx_jurisdictions_requirements', 'jurisdictions', ['requirements'], postgresql_using='gin')


def downgrade() -> None:
    op.drop_index('idx_jurisdictions_requirements', table_name='jurisdictions')
    op.drop_index('idx_jurisdictions_state', table_name='jurisdictions')
    op.drop_index('idx_jurisdictions_name', table_name='jurisdictions')
    op.drop_table('jurisdictions')
