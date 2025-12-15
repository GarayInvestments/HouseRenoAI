"""add_status_enums_for_all_tables

Revision ID: bf5d364b4f5d
Revises: e4374cb11fda
Create Date: 2025-12-14 23:26:12.091261

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bf5d364b4f5d'
down_revision: Union[str, None] = 'e4374cb11fda'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ========================================================================
    # 1. Projects Status ENUM
    # ========================================================================
    project_status_enum = sa.Enum(
        'PLANNING',
        'PERMIT_UNDER_REVIEW',
        'INSPECTIONS_IN_PROGRESS',
        'ON_HOLD',
        'COMPLETED',
        'CANCELLED',
        name='project_status_enum',
        create_type=True
    )
    project_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Migrate existing project statuses
    op.execute("""
        UPDATE projects 
        SET status = CASE
            WHEN LOWER(status) = 'planning' THEN 'PLANNING'
            WHEN LOWER(status) IN ('permit under review', 'permit_under_review') THEN 'PERMIT_UNDER_REVIEW'
            WHEN LOWER(status) IN ('inspections in progress', 'inspections_in_progress', 'active', 'in progress') THEN 'INSPECTIONS_IN_PROGRESS'
            WHEN LOWER(status) IN ('on hold', 'on_hold', 'paused') THEN 'ON_HOLD'
            WHEN LOWER(status) IN ('completed', 'finished', 'closed') THEN 'COMPLETED'
            WHEN LOWER(status) IN ('cancelled', 'canceled', 'inactive') THEN 'CANCELLED'
            ELSE 'PLANNING'
        END
        WHERE status IS NOT NULL
    """)
    
    op.alter_column(
        'projects',
        'status',
        type_=project_status_enum,
        postgresql_using='status::project_status_enum',
        existing_type=sa.String(100),
        existing_nullable=True
    )
    
    # ========================================================================
    # 2. Permits Status ENUM
    # ========================================================================
    permit_status_enum = sa.Enum(
        'DRAFT',
        'SUBMITTED',
        'UNDER_REVIEW',
        'APPROVED',
        'ISSUED',
        'INSPECTIONS_IN_PROGRESS',
        'CLOSED',
        'EXPIRED',
        'REJECTED',
        name='permit_status_enum',
        create_type=True
    )
    permit_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Migrate existing permit statuses
    op.execute("""
        UPDATE permits 
        SET status = CASE
            WHEN LOWER(status) = 'draft' THEN 'DRAFT'
            WHEN LOWER(status) IN ('submitted', 'pending') THEN 'SUBMITTED'
            WHEN LOWER(status) IN ('under review', 'under_review', 'review') THEN 'UNDER_REVIEW'
            WHEN LOWER(status) = 'approved' THEN 'APPROVED'
            WHEN LOWER(status) = 'issued' THEN 'ISSUED'
            WHEN LOWER(status) IN ('inspections in progress', 'inspections_in_progress') THEN 'INSPECTIONS_IN_PROGRESS'
            WHEN LOWER(status) = 'closed' THEN 'CLOSED'
            WHEN LOWER(status) = 'expired' THEN 'EXPIRED'
            WHEN LOWER(status) = 'rejected' THEN 'REJECTED'
            ELSE 'DRAFT'
        END
        WHERE status IS NOT NULL
    """)
    
    op.alter_column(
        'permits',
        'status',
        type_=permit_status_enum,
        postgresql_using='status::permit_status_enum',
        existing_type=sa.String(50),
        existing_nullable=True
    )
    
    # ========================================================================
    # 3. Invoices Status ENUM (QuickBooks-aligned)
    # ========================================================================
    invoice_status_enum = sa.Enum(
        'DRAFT',
        'SENT',
        'PARTIALLY_PAID',
        'PAID',
        'VOID',
        'OVERDUE',
        name='invoice_status_enum',
        create_type=True
    )
    invoice_status_enum.create(op.get_bind(), checkfirst=True)
    
    op.alter_column(
        'invoices',
        'status',
        type_=invoice_status_enum,
        postgresql_using='status::invoice_status_enum',
        existing_type=sa.String(50),
        existing_nullable=True
    )
    
    # ========================================================================
    # 4. Payments Status ENUM
    # ========================================================================
    payment_status_enum = sa.Enum(
        'PENDING',
        'POSTED',
        'FAILED',
        'REFUNDED',
        name='payment_status_enum',
        create_type=True
    )
    payment_status_enum.create(op.get_bind(), checkfirst=True)
    
    op.alter_column(
        'payments',
        'status',
        type_=payment_status_enum,
        postgresql_using='status::payment_status_enum',
        existing_type=sa.String(50),
        existing_nullable=True
    )


def downgrade() -> None:
    # Revert all columns to String types
    op.alter_column('projects', 'status', type_=sa.String(100), existing_nullable=True)
    op.alter_column('permits', 'status', type_=sa.String(50), existing_nullable=True)
    op.alter_column('invoices', 'status', type_=sa.String(50), existing_nullable=True)
    op.alter_column('payments', 'status', type_=sa.String(50), existing_nullable=True)
    
    # Drop ENUM types
    sa.Enum(name='project_status_enum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='permit_status_enum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='invoice_status_enum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='payment_status_enum').drop(op.get_bind(), checkfirst=True)
