"""add_business_id_sequences_and_triggers

Revision ID: 62e3354db1d9
Revises: cba01e589593
Create Date: 2025-12-10 22:45:10.720753

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '62e3354db1d9'
down_revision: Union[str, None] = 'cba01e589593'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create sequences for business IDs (IF NOT EXISTS for idempotency)
    op.execute("CREATE SEQUENCE IF NOT EXISTS client_business_id_seq START 1")
    op.execute("CREATE SEQUENCE IF NOT EXISTS project_business_id_seq START 1")
    op.execute("CREATE SEQUENCE IF NOT EXISTS permit_business_id_seq START 1")
    op.execute("CREATE SEQUENCE IF NOT EXISTS inspection_business_id_seq START 1")
    op.execute("CREATE SEQUENCE IF NOT EXISTS invoice_business_id_seq START 1")
    op.execute("CREATE SEQUENCE IF NOT EXISTS payment_business_id_seq START 1")
    op.execute("CREATE SEQUENCE IF NOT EXISTS site_visit_business_id_seq START 1")
    
    # Drop existing functions if they exist (for idempotency)
    op.execute("DROP FUNCTION IF EXISTS generate_client_business_id() CASCADE")
    op.execute("DROP FUNCTION IF EXISTS generate_project_business_id() CASCADE")
    op.execute("DROP FUNCTION IF EXISTS generate_permit_business_id() CASCADE")
    op.execute("DROP FUNCTION IF EXISTS generate_inspection_business_id() CASCADE")
    op.execute("DROP FUNCTION IF EXISTS generate_invoice_business_id() CASCADE")
    op.execute("DROP FUNCTION IF EXISTS generate_payment_business_id() CASCADE")
    op.execute("DROP FUNCTION IF EXISTS generate_site_visit_business_id() CASCADE")
    
    # Create trigger function for clients
    op.execute("""
        CREATE OR REPLACE FUNCTION generate_client_business_id()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.business_id IS NULL THEN
                NEW.business_id := 'CL-' || LPAD(nextval('client_business_id_seq')::TEXT, 5, '0');
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Create trigger function for projects
    op.execute("""
        CREATE OR REPLACE FUNCTION generate_project_business_id()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.business_id IS NULL THEN
                NEW.business_id := 'PRJ-' || LPAD(nextval('project_business_id_seq')::TEXT, 5, '0');
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Create trigger function for permits
    op.execute("""
        CREATE OR REPLACE FUNCTION generate_permit_business_id()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.business_id IS NULL THEN
                NEW.business_id := 'PER-' || LPAD(nextval('permit_business_id_seq')::TEXT, 5, '0');
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Create trigger function for inspections
    op.execute("""
        CREATE OR REPLACE FUNCTION generate_inspection_business_id()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.business_id IS NULL THEN
                NEW.business_id := 'INS-' || LPAD(nextval('inspection_business_id_seq')::TEXT, 5, '0');
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Create trigger function for invoices
    op.execute("""
        CREATE OR REPLACE FUNCTION generate_invoice_business_id()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.business_id IS NULL THEN
                NEW.business_id := 'INV-' || LPAD(nextval('invoice_business_id_seq')::TEXT, 5, '0');
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Create trigger function for payments
    op.execute("""
        CREATE OR REPLACE FUNCTION generate_payment_business_id()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.business_id IS NULL THEN
                NEW.business_id := 'PAY-' || LPAD(nextval('payment_business_id_seq')::TEXT, 5, '0');
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Create trigger function for site visits
    op.execute("""
        CREATE OR REPLACE FUNCTION generate_site_visit_business_id()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.business_id IS NULL THEN
                NEW.business_id := 'SV-' || LPAD(nextval('site_visit_business_id_seq')::TEXT, 5, '0');
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Drop existing triggers if they exist (for idempotency)
    op.execute("DROP TRIGGER IF EXISTS client_business_id_trigger ON clients")
    op.execute("DROP TRIGGER IF EXISTS project_business_id_trigger ON projects")
    op.execute("DROP TRIGGER IF EXISTS permit_business_id_trigger ON permits")
    op.execute("DROP TRIGGER IF EXISTS inspection_business_id_trigger ON inspections")
    op.execute("DROP TRIGGER IF EXISTS invoice_business_id_trigger ON invoices")
    op.execute("DROP TRIGGER IF EXISTS payment_business_id_trigger ON payments")
    op.execute("DROP TRIGGER IF EXISTS site_visit_business_id_trigger ON site_visits")
    
    # Create triggers for all tables
    op.execute("""
        CREATE TRIGGER client_business_id_trigger
        BEFORE INSERT ON clients
        FOR EACH ROW EXECUTE FUNCTION generate_client_business_id()
    """)
    
    op.execute("""
        CREATE TRIGGER project_business_id_trigger
        BEFORE INSERT ON projects
        FOR EACH ROW EXECUTE FUNCTION generate_project_business_id()
    """)
    
    op.execute("""
        CREATE TRIGGER permit_business_id_trigger
        BEFORE INSERT ON permits
        FOR EACH ROW EXECUTE FUNCTION generate_permit_business_id()
    """)
    
    op.execute("""
        CREATE TRIGGER inspection_business_id_trigger
        BEFORE INSERT ON inspections
        FOR EACH ROW EXECUTE FUNCTION generate_inspection_business_id()
    """)
    
    op.execute("""
        CREATE TRIGGER invoice_business_id_trigger
        BEFORE INSERT ON invoices
        FOR EACH ROW EXECUTE FUNCTION generate_invoice_business_id()
    """)
    
    op.execute("""
        CREATE TRIGGER payment_business_id_trigger
        BEFORE INSERT ON payments
        FOR EACH ROW EXECUTE FUNCTION generate_payment_business_id()
    """)
    
    op.execute("""
        CREATE TRIGGER site_visit_business_id_trigger
        BEFORE INSERT ON site_visits
        FOR EACH ROW EXECUTE FUNCTION generate_site_visit_business_id()
    """)


def downgrade() -> None:
    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS client_business_id_trigger ON clients")
    op.execute("DROP TRIGGER IF EXISTS project_business_id_trigger ON projects")
    op.execute("DROP TRIGGER IF EXISTS permit_business_id_trigger ON permits")
    op.execute("DROP TRIGGER IF EXISTS inspection_business_id_trigger ON inspections")
    op.execute("DROP TRIGGER IF EXISTS invoice_business_id_trigger ON invoices")
    op.execute("DROP TRIGGER IF EXISTS payment_business_id_trigger ON payments")
    op.execute("DROP TRIGGER IF EXISTS site_visit_business_id_trigger ON site_visits")
    
    # Drop trigger functions
    op.execute("DROP FUNCTION IF EXISTS generate_client_business_id()")
    op.execute("DROP FUNCTION IF EXISTS generate_project_business_id()")
    op.execute("DROP FUNCTION IF EXISTS generate_permit_business_id()")
    op.execute("DROP FUNCTION IF EXISTS generate_inspection_business_id()")
    op.execute("DROP FUNCTION IF EXISTS generate_invoice_business_id()")
    op.execute("DROP FUNCTION IF EXISTS generate_payment_business_id()")
    op.execute("DROP FUNCTION IF EXISTS generate_site_visit_business_id()")
    
    # Drop sequences
    op.execute("DROP SEQUENCE IF EXISTS client_business_id_seq")
    op.execute("DROP SEQUENCE IF EXISTS project_business_id_seq")
    op.execute("DROP SEQUENCE IF EXISTS permit_business_id_seq")
    op.execute("DROP SEQUENCE IF EXISTS inspection_business_id_seq")
    op.execute("DROP SEQUENCE IF EXISTS invoice_business_id_seq")
    op.execute("DROP SEQUENCE IF EXISTS payment_business_id_seq")
    op.execute("DROP SEQUENCE IF EXISTS site_visit_business_id_seq")
