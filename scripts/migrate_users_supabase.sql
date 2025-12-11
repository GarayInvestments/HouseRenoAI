-- Recreate users table for Supabase Auth integration
-- This script drops the old users table and creates a new one

-- Drop old table
DROP TABLE IF EXISTS users CASCADE;

-- Create new users table
CREATE TABLE users (
    -- Primary key - our internal UUID
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Supabase Auth user ID - maps to auth.users.id
    supabase_user_id UUID NOT NULL UNIQUE,
    
    -- User profile (duplicated from auth.users for performance)
    email VARCHAR(255) NOT NULL UNIQUE,
    full_name VARCHAR(255),
    phone VARCHAR(50),
    
    -- Role-based access control
    -- Valid roles: admin, pm, inspector, client, finance
    role VARCHAR(50) NOT NULL DEFAULT 'client',
    
    -- Status flags
    is_active BOOLEAN NOT NULL DEFAULT true,
    is_email_verified BOOLEAN NOT NULL DEFAULT false,
    
    -- Activity tracking
    last_login_at TIMESTAMP WITH TIME ZONE,
    last_activity_at TIMESTAMP WITH TIME ZONE,
    
    -- App-specific metadata (permissions, preferences, settings)
    app_metadata JSONB,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX ix_users_supabase_user_id ON users(supabase_user_id);
CREATE UNIQUE INDEX ix_users_email ON users(email);
CREATE INDEX ix_users_role ON users(role);
CREATE INDEX ix_users_app_metadata_gin ON users USING gin(app_metadata);
CREATE INDEX ix_users_email_lower ON users(LOWER(email));
CREATE INDEX ix_users_active ON users(is_active) WHERE is_active = true;

-- Add check constraint for valid roles
ALTER TABLE users
ADD CONSTRAINT check_valid_role
CHECK (role IN ('admin', 'pm', 'inspector', 'client', 'finance'));

-- Create trigger to update updated_at timestamp
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

-- Create function to sync user data from auth.users
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
-- This will need to be set up via Supabase Dashboard:
-- CREATE TRIGGER on_auth_user_created
-- AFTER INSERT OR UPDATE ON auth.users
-- FOR EACH ROW EXECUTE FUNCTION sync_user_from_auth();

-- Insert alembic version record
INSERT INTO alembic_version (version_num) VALUES ('recreate_users_supabase')
ON CONFLICT (version_num) DO NOTHING;
