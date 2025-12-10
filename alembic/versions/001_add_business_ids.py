"""Add business IDs to core entities

Revision ID: 003
Revises: 002
Create Date: 2025-12-10 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = '000'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add business_id columns, sequences, generation functions, and triggers."""
    
    # ========================================
    # Step 1: Create sequences
    # ========================================
    op.execute("CREATE SEQUENCE client_business_id_seq START 1;")
    op.execute("CREATE SEQUENCE project_business_id_seq START 1;")
    op.execute("CREATE SEQUENCE permit_business_id_seq START 1;")
    op.execute("CREATE SEQUENCE payment_business_id_seq START 1;")
    
    # ========================================
    # Step 2: Add columns (nullable for backfill)
    # ========================================
    op.add_column('clients', sa.Column('business_id', sa.String(20), nullable=True))
    op.add_column('projects', sa.Column('business_id', sa.String(20), nullable=True))
    op.add_column('permits', sa.Column('business_id', sa.String(20), nullable=True))
    op.add_column('payments', sa.Column('business_id', sa.String(20), nullable=True))
    
    # ========================================
    # Step 3: Create generation functions
    # ========================================
    
    # Client business ID generator: CL-00001, CL-00002, etc.
    op.execute("""
        CREATE OR REPLACE FUNCTION generate_client_business_id()
        RETURNS VARCHAR(20) AS $$
        BEGIN
          RETURN 'CL-' || LPAD(nextval('client_business_id_seq')::TEXT, 5, '0');
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Project business ID generator: PRJ-00001, PRJ-00002, etc.
    op.execute("""
        CREATE OR REPLACE FUNCTION generate_project_business_id()
        RETURNS VARCHAR(20) AS $$
        BEGIN
          RETURN 'PRJ-' || LPAD(nextval('project_business_id_seq')::TEXT, 5, '0');
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Permit business ID generator: PRM-00001, PRM-00002, etc.
    op.execute("""
        CREATE OR REPLACE FUNCTION generate_permit_business_id()
        RETURNS VARCHAR(20) AS $$
        BEGIN
          RETURN 'PRM-' || LPAD(nextval('permit_business_id_seq')::TEXT, 5, '0');
        END;
        $$ LANGUAGE plpgsql;
    """)
    

    
    # Payment business ID generator: PAY-00001, PAY-00002, etc.
    op.execute("""
        CREATE OR REPLACE FUNCTION generate_payment_business_id()
        RETURNS VARCHAR(20) AS $$
        BEGIN
          RETURN 'PAY-' || LPAD(nextval('payment_business_id_seq')::TEXT, 5, '0');
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # ========================================
    # Step 4: Create trigger functions
    # ========================================
    
    # Client trigger function
    op.execute("""
        CREATE OR REPLACE FUNCTION set_client_business_id()
        RETURNS TRIGGER AS $$
        BEGIN
          IF NEW.business_id IS NULL THEN
            NEW.business_id := generate_client_business_id();
          END IF;
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Project trigger function
    op.execute("""
        CREATE OR REPLACE FUNCTION set_project_business_id()
        RETURNS TRIGGER AS $$
        BEGIN
          IF NEW.business_id IS NULL THEN
            NEW.business_id := generate_project_business_id();
          END IF;
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Permit trigger function
    op.execute("""
        CREATE OR REPLACE FUNCTION set_permit_business_id()
        RETURNS TRIGGER AS $$
        BEGIN
          IF NEW.business_id IS NULL THEN
            NEW.business_id := generate_permit_business_id();
          END IF;
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    

    
    # Payment trigger function
    op.execute("""
        CREATE OR REPLACE FUNCTION set_payment_business_id()
        RETURNS TRIGGER AS $$
        BEGIN
          IF NEW.business_id IS NULL THEN
            NEW.business_id := generate_payment_business_id();
          END IF;
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # ========================================
    # Step 5: Create triggers
    # ========================================
    
    op.execute("""
        CREATE TRIGGER trigger_set_client_business_id
          BEFORE INSERT ON clients
          FOR EACH ROW
          EXECUTE FUNCTION set_client_business_id();
    """)
    
    op.execute("""
        CREATE TRIGGER trigger_set_project_business_id
          BEFORE INSERT ON projects
          FOR EACH ROW
          EXECUTE FUNCTION set_project_business_id();
    """)
    
    op.execute("""
        CREATE TRIGGER trigger_set_permit_business_id
          BEFORE INSERT ON permits
          FOR EACH ROW
          EXECUTE FUNCTION set_permit_business_id();
    """)
    

    
    op.execute("""
        CREATE TRIGGER trigger_set_payment_business_id
          BEFORE INSERT ON payments
          FOR EACH ROW
          EXECUTE FUNCTION set_payment_business_id();
    """)
    
    # ========================================
    # Step 6: Create unique indexes
    # ========================================
    
    op.create_index('idx_clients_business_id', 'clients', ['business_id'], unique=True)
    op.create_index('idx_projects_business_id', 'projects', ['business_id'], unique=True)
    op.create_index('idx_permits_business_id', 'permits', ['business_id'], unique=True)
    op.create_index('idx_payments_business_id', 'payments', ['business_id'], unique=True)


def downgrade() -> None:
    """Remove business_id infrastructure (rollback)."""
    
    # Drop indexes
    op.drop_index('idx_clients_business_id', table_name='clients')
    op.drop_index('idx_projects_business_id', table_name='projects')
    op.drop_index('idx_permits_business_id', table_name='permits')
    op.drop_index('idx_payments_business_id', table_name='payments')
    
    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS trigger_set_client_business_id ON clients CASCADE;")
    op.execute("DROP TRIGGER IF EXISTS trigger_set_project_business_id ON projects CASCADE;")
    op.execute("DROP TRIGGER IF EXISTS trigger_set_permit_business_id ON permits CASCADE;")
    op.execute("DROP TRIGGER IF EXISTS trigger_set_payment_business_id ON payments CASCADE;")
    
    # Drop trigger functions
    op.execute("DROP FUNCTION IF EXISTS set_client_business_id() CASCADE;")
    op.execute("DROP FUNCTION IF EXISTS set_project_business_id() CASCADE;")
    op.execute("DROP FUNCTION IF EXISTS set_permit_business_id() CASCADE;")
    op.execute("DROP FUNCTION IF EXISTS set_payment_business_id() CASCADE;")
    
    # Drop generation functions
    op.execute("DROP FUNCTION IF EXISTS generate_client_business_id() CASCADE;")
    op.execute("DROP FUNCTION IF EXISTS generate_project_business_id() CASCADE;")
    op.execute("DROP FUNCTION IF EXISTS generate_permit_business_id() CASCADE;")
    op.execute("DROP FUNCTION IF EXISTS generate_payment_business_id() CASCADE;")
    
    # Drop columns
    op.drop_column('clients', 'business_id')
    op.drop_column('projects', 'business_id')
    op.drop_column('permits', 'business_id')
    op.drop_column('payments', 'business_id')
    
    # Drop sequences
    op.execute("DROP SEQUENCE IF EXISTS client_business_id_seq CASCADE;")
    op.execute("DROP SEQUENCE IF EXISTS project_business_id_seq CASCADE;")
    op.execute("DROP SEQUENCE IF EXISTS permit_business_id_seq CASCADE;")
    op.execute("DROP SEQUENCE IF EXISTS payment_business_id_seq CASCADE;")
