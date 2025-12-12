"""Add authentication tables for modern token system

Revision ID: 20251211_1630
Revises: 1fd9ea7652d5
Create Date: 2025-12-11 16:30:00

Creates:
- refresh_tokens table (token rotation and family tracking)
- token_blacklist table (revoked access tokens)
- user_sessions table (active session management)
- login_attempts table (security monitoring and rate limiting)

Design principles:
- Short-lived access tokens (15 min) with JWT
- Long-lived refresh tokens (30 days) stored in database
- Token rotation on refresh (old token invalidated)
- Token family tracking (detects token theft)
- Session management for "View Active Sessions" feature
- Login attempt tracking for brute force detection
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251211_1630_add_auth_tables'
down_revision = 'recreate_users_supabase'  # Latest migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create refresh_tokens table
    op.create_table(
        'refresh_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=False), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('token_hash', sa.String(length=255), nullable=False),
        sa.Column('family_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('parent_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('is_used', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('is_revoked', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('issued_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('device_name', sa.String(length=255), nullable=True),
        sa.Column('revocation_reason', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_id'], ['refresh_tokens.id']),
        sa.UniqueConstraint('token_hash')
    )
    
    # Indexes for refresh_tokens
    op.create_index('ix_refresh_tokens_user_id', 'refresh_tokens', ['user_id'])
    op.create_index('ix_refresh_tokens_token_hash', 'refresh_tokens', ['token_hash'], unique=True)
    op.create_index('ix_refresh_tokens_family_id', 'refresh_tokens', ['family_id'])
    op.create_index('ix_refresh_tokens_is_used', 'refresh_tokens', ['is_used'])
    op.create_index('ix_refresh_tokens_is_revoked', 'refresh_tokens', ['is_revoked'])
    op.create_index('ix_refresh_tokens_expires_at', 'refresh_tokens', ['expires_at'])
    
    # Composite indexes for efficient queries
    op.create_index(
        'ix_refresh_tokens_user_active',
        'refresh_tokens',
        ['user_id', 'is_revoked', 'is_used', 'expires_at']
    )
    op.create_index(
        'ix_refresh_tokens_family',
        'refresh_tokens',
        ['family_id', 'is_revoked']
    )
    
    # Create token_blacklist table
    op.create_table(
        'token_blacklist',
        sa.Column('jti', sa.String(length=255), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('token_type', sa.String(length=20), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('reason', sa.String(length=255), nullable=True),
        sa.Column('revoked_by', postgresql.UUID(as_uuid=False), nullable=True),
        sa.PrimaryKeyConstraint('jti'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    
    # Indexes for token_blacklist
    op.create_index('ix_token_blacklist_user_id', 'token_blacklist', ['user_id'])
    op.create_index('ix_token_blacklist_expires_at', 'token_blacklist', ['expires_at'])
    op.create_index(
        'ix_token_blacklist_user_expires',
        'token_blacklist',
        ['user_id', 'expires_at']
    )
    
    # Create user_sessions table
    op.create_table(
        'user_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=False), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('session_token', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('device_name', sa.String(length=255), nullable=True),
        sa.Column('device_type', sa.String(length=50), nullable=True),
        sa.Column('browser', sa.String(length=100), nullable=True),
        sa.Column('os', sa.String(length=100), nullable=True),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('last_activity_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('end_reason', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('session_token')
    )
    
    # Indexes for user_sessions
    op.create_index('ix_user_sessions_user_id', 'user_sessions', ['user_id'])
    op.create_index('ix_user_sessions_session_token', 'user_sessions', ['session_token'], unique=True)
    op.create_index('ix_user_sessions_is_active', 'user_sessions', ['is_active'])
    op.create_index('ix_user_sessions_last_activity_at', 'user_sessions', ['last_activity_at'])
    op.create_index('ix_user_sessions_expires_at', 'user_sessions', ['expires_at'])
    op.create_index('ix_user_sessions_ip_address', 'user_sessions', ['ip_address'])
    
    # Composite indexes for efficient queries
    op.create_index(
        'ix_user_sessions_user_active',
        'user_sessions',
        ['user_id', 'is_active', 'last_activity_at']
    )
    op.create_index(
        'ix_user_sessions_expires_active',
        'user_sessions',
        ['expires_at', 'is_active']
    )
    op.create_index(
        'ix_user_sessions_user_ip',
        'user_sessions',
        ['user_id', 'ip_address']
    )
    
    # Create login_attempts table
    op.create_table(
        'login_attempts',
        sa.Column('id', postgresql.UUID(as_uuid=False), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=False),
        sa.Column('failure_reason', sa.String(length=255), nullable=True),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('attempted_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL')
    )
    
    # Indexes for login_attempts
    op.create_index('ix_login_attempts_email', 'login_attempts', ['email'])
    op.create_index('ix_login_attempts_success', 'login_attempts', ['success'])
    op.create_index('ix_login_attempts_ip_address', 'login_attempts', ['ip_address'])
    op.create_index('ix_login_attempts_attempted_at', 'login_attempts', ['attempted_at'])
    
    # Composite indexes for rate limiting
    op.create_index(
        'ix_login_attempts_ip_time',
        'login_attempts',
        ['ip_address', 'attempted_at']
    )
    op.create_index(
        'ix_login_attempts_email_time',
        'login_attempts',
        ['email', 'attempted_at', 'success']
    )
    op.create_index(
        'ix_login_attempts_failed',
        'login_attempts',
        ['success', 'attempted_at']
    )


def downgrade() -> None:
    # Drop tables in reverse order (respecting foreign keys)
    op.drop_table('login_attempts')
    op.drop_table('user_sessions')
    op.drop_table('token_blacklist')
    op.drop_table('refresh_tokens')
