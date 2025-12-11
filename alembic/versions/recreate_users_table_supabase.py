"""recreate users table for supabase auth

Revision ID: recreate_users_supabase
Revises: cba01e589593
Create Date: 2025-12-11

This migration:
1. Drops old users table (if exists)
2. Creates new users table with Supabase Auth mapping
3. Adds proper indexes and constraints
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'recreate_users_supabase'
down_revision = 'cba01e589593'  # Latest migration
branch_label = None
depends_on = None


def upgrade() -> None:
    """Create new users table with Supabase Auth integration"""
    
    # Drop old users table if it exists
    op.execute("DROP TABLE IF EXISTS users CASCADE")
    
    # Create new users table
    op.create_table(
        'users',
        
        # Primary key - our internal UUID
        sa.Column('id', postgresql.UUID(as_uuid=False), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        
        # Supabase Auth user ID - maps to auth.users.id
        sa.Column('supabase_user_id', postgresql.UUID(as_uuid=False), nullable=False, unique=True, index=True),
        
        # User profile information (duplicated from auth.users for performance)
        sa.Column('email', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(50), nullable=True),
        
        # Role-based access control
        # Roles: admin, pm (project manager), inspector, client, finance
        sa.Column('role', sa.String(50), nullable=False, server_default='client', index=True),
        
        # Status flags
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('is_email_verified', sa.Boolean, nullable=False, server_default='false'),
        
        # Activity tracking
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_activity_at', sa.DateTime(timezone=True), nullable=True),
        
        # App-specific metadata (permissions, preferences, settings)
        # Example: {"permissions": ["view_permits", "create_invoices"], "preferences": {"theme": "dark"}}
        sa.Column('app_metadata', postgresql.JSONB, nullable=True),
        
        # Audit fields
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    
    # Create GIN index on JSONB app_metadata for fast queries
    op.create_index(
        'ix_users_app_metadata_gin',
        'users',
        ['app_metadata'],
        postgresql_using='gin'
    )
    
    # Create partial index for active users (common query)
    op.execute("""
        CREATE INDEX ix_users_active 
        ON users(is_active) 
        WHERE is_active = true
    """)
    
    # Create case-insensitive index on email for search
    op.execute("""
        CREATE INDEX ix_users_email_lower 
        ON users(LOWER(email))
    """)
    
    # Add check constraint for valid roles
    op.execute("""
        ALTER TABLE users
        ADD CONSTRAINT check_valid_role
        CHECK (role IN ('admin', 'pm', 'inspector', 'client', 'finance'))
    """)
    
    # Create trigger to update updated_at timestamp
    op.execute("""
        CREATE OR REPLACE FUNCTION update_users_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        
        CREATE TRIGGER users_updated_at_trigger
        BEFORE UPDATE ON users
        FOR EACH ROW
        EXECUTE FUNCTION update_users_updated_at();
    """)
    
    # Create function to sync user data from auth.users on trigger
    op.execute("""
        CREATE OR REPLACE FUNCTION sync_user_from_auth()
        RETURNS TRIGGER AS $$
        BEGIN
            -- When a user is created in auth.users, create corresponding app user
            INSERT INTO public.users (supabase_user_id, email, full_name, is_email_verified)
            VALUES (
                NEW.id,
                NEW.email,
                COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.raw_user_meta_data->>'name'),
                NEW.email_confirmed_at IS NOT NULL
            )
            ON CONFLICT (supabase_user_id) DO UPDATE
            SET 
                email = EXCLUDED.email,
                full_name = EXCLUDED.full_name,
                is_email_verified = EXCLUDED.is_email_verified,
                updated_at = CURRENT_TIMESTAMP;
            
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER;
        
        -- Note: Trigger on auth.users requires superuser privileges
        -- This will be set up manually via Supabase Dashboard or supabase CLI
        -- CREATE TRIGGER on_auth_user_created
        -- AFTER INSERT OR UPDATE ON auth.users
        -- FOR EACH ROW EXECUTE FUNCTION sync_user_from_auth();
    """)


def downgrade() -> None:
    """Drop users table and related objects"""
    
    # Drop triggers (if they exist)
    op.execute("DROP TRIGGER IF EXISTS users_updated_at_trigger ON users")
    op.execute("DROP FUNCTION IF EXISTS update_users_updated_at()")
    op.execute("DROP FUNCTION IF EXISTS sync_user_from_auth()")
    
    # Drop table
    op.drop_table('users')
