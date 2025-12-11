"""extend_permits_with_workflow_columns

Revision ID: 7efbcd4142a3
Revises: 9ac01f737adf
Create Date: 2025-12-10 23:59:03.953961

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '7efbcd4142a3'
down_revision: Union[str, None] = '9ac01f737adf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add workflow columns to permits table for approval tracking and status history."""
    
    # Add status_history JSONB column for tracking status changes
    op.add_column('permits', sa.Column('status_history', postgresql.JSONB, nullable=True))
    
    # Add approval workflow columns
    op.add_column('permits', sa.Column('approved_by', sa.String(255), nullable=True))
    op.add_column('permits', sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    """Remove workflow columns from permits table."""
    
    op.drop_column('permits', 'approved_at')
    op.drop_column('permits', 'approved_by')
    op.drop_column('permits', 'status_history')
