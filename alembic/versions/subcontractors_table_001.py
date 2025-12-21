"""Add subcontractors table for permit subcontractor tracking

Revision ID: subcontractors_table_001
Revises: 
Create Date: 2025-12-21 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'subcontractors_table_001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create subcontractors table
    op.create_table(
        'subcontractors',
        sa.Column('subcontractor_id', postgresql.UUID(as_uuid=False), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('business_id', sa.String(20), server_default=sa.text('NULL'), nullable=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('permit_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('company_name', sa.String(255), nullable=True),
        sa.Column('trade', sa.String(100), nullable=False),
        sa.Column('license_number', sa.String(100), nullable=True),
        sa.Column('license_state', sa.String(2), nullable=True),
        sa.Column('license_expires', sa.DateTime(timezone=True), nullable=True),
        sa.Column('bond_number', sa.String(100), nullable=True),
        sa.Column('bond_amount', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('bond_expires', sa.DateTime(timezone=True), nullable=True),
        sa.Column('coi_document_id', sa.String(255), nullable=True),
        sa.Column('coi_uploaded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('workers_comp_document_id', sa.String(255), nullable=True),
        sa.Column('workers_comp_uploaded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('workers_comp_expires', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(50), server_default=sa.text("'pending_approval'"), nullable=False),
        sa.Column('approved_by', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('extra', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('subcontractor_id')
    )
    
    # Create unique constraint on business_id
    op.create_unique_constraint('uq_subcontractors_business_id', 'subcontractors', ['business_id'])
    
    # Create indexes
    op.create_index('ix_subcontractors_project', 'subcontractors', ['project_id'])
    op.create_index('ix_subcontractors_permit', 'subcontractors', ['permit_id'])
    op.create_index('ix_subcontractors_status', 'subcontractors', ['status'])
    op.create_index('ix_subcontractors_trade', 'subcontractors', ['trade'])
    op.create_index('ix_subcontractors_email', 'subcontractors', ['email'])
    op.create_index('ix_subcontractors_extra_gin', 'subcontractors', ['extra'], postgresql_using='gin')
    
    # Create business_id auto-increment trigger
    op.execute("""
        CREATE SEQUENCE subcontractors_business_id_seq START 1;
        
        CREATE OR REPLACE FUNCTION set_subcontractor_business_id()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.business_id IS NULL THEN
                NEW.business_id := 'SUB-' || LPAD(nextval('subcontractors_business_id_seq')::TEXT, 5, '0');
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        
        CREATE TRIGGER subcontractors_business_id_trigger
        BEFORE INSERT ON subcontractors
        FOR EACH ROW
        EXECUTE FUNCTION set_subcontractor_business_id();
    """)


def downgrade() -> None:
    # Drop trigger and function
    op.execute("DROP TRIGGER IF EXISTS subcontractors_business_id_trigger ON subcontractors")
    op.execute("DROP FUNCTION IF EXISTS set_subcontractor_business_id()")
    op.execute("DROP SEQUENCE IF EXISTS subcontractors_business_id_seq")
    
    # Drop table
    op.drop_table('subcontractors')
