"""
Authentication models for token management and session tracking.

Purpose: Secure token lifecycle with refresh tokens, revocation, and session management.
Design: Follows OAuth2 best practices with short-lived access tokens and rotating refresh tokens.
"""

from datetime import datetime
from typing import Dict, Any
from sqlalchemy import String, Text, DateTime, Boolean, Index, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.models import Base


class RefreshToken(Base):
    """
    Refresh tokens for secure token rotation.
    
    Design principles:
    - Short-lived access tokens (15 minutes)
    - Long-lived refresh tokens (30 days)
    - Automatic rotation on use (invalidates old token)
    - One-time use only (prevents replay attacks)
    - Device/session tracking for security audit
    
    Security features:
    - Token family tracking (detects token theft)
    - Automatic revocation on suspicious activity
    - IP and user agent tracking
    - Expiration and invalidation
    """
    __tablename__ = "refresh_tokens"
    
    # Primary key
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    
    # User reference
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    
    # Token value (hashed for security)
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    
    # Token family for rotation tracking (detects stolen tokens)
    # All tokens in a refresh chain share the same family_id
    family_id: Mapped[str] = mapped_column(UUID(as_uuid=False), index=True)
    
    # Parent token (for rotation chain tracking)
    parent_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("refresh_tokens.id"))
    
    # Lifecycle flags
    is_used: Mapped[bool] = mapped_column(Boolean, server_default="false", index=True)
    is_revoked: Mapped[bool] = mapped_column(Boolean, server_default="false", index=True)
    
    # Expiration
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    
    # Security metadata
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=text("CURRENT_TIMESTAMP")
    )
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    
    # Device/session tracking
    ip_address: Mapped[str | None] = mapped_column(INET)
    user_agent: Mapped[str | None] = mapped_column(Text)
    device_name: Mapped[str | None] = mapped_column(String(255))  # e.g., "Chrome on Windows", "iOS App"
    
    # Revocation reason
    revocation_reason: Mapped[str | None] = mapped_column(String(255))  # e.g., "logout", "token_theft_detected", "expired"
    
    __table_args__ = (
        # Find active tokens for a user
        Index('ix_refresh_tokens_user_active', 'user_id', 'is_revoked', 'is_used', 'expires_at'),
        # Find tokens by family (for theft detection)
        Index('ix_refresh_tokens_family', 'family_id', 'is_revoked'),
        # Cleanup expired tokens
        Index('ix_refresh_tokens_expires_at', 'expires_at', 'is_revoked'),
    )


class TokenBlacklist(Base):
    """
    Blacklist for revoked access tokens (before they expire naturally).
    
    Use cases:
    - User logout (invalidate current access token)
    - Password reset (invalidate all tokens)
    - Security breach (revoke specific tokens)
    - Admin revocation
    
    TTL: Access tokens are short-lived (15 min), so blacklist entries auto-expire.
    """
    __tablename__ = "token_blacklist"
    
    # Primary key - JWT ID (jti claim)
    jti: Mapped[str] = mapped_column(String(255), primary_key=True)
    
    # User reference (for bulk revocation)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    
    # Token metadata
    token_type: Mapped[str] = mapped_column(String(20))  # "access" or "refresh"
    
    # Revocation details
    revoked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=text("CURRENT_TIMESTAMP")
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    
    # Reason for revocation
    reason: Mapped[str | None] = mapped_column(String(255))  # "logout", "password_reset", "admin_revoke"
    
    # Who revoked (for audit)
    revoked_by: Mapped[str | None] = mapped_column(UUID(as_uuid=False))  # user_id of admin if admin revoked
    
    __table_args__ = (
        # Find blacklisted tokens
        Index('ix_token_blacklist_expires_at', 'expires_at'),
        # Bulk revoke by user
        Index('ix_token_blacklist_user_id', 'user_id', 'expires_at'),
    )


class UserSession(Base):
    """
    Active user sessions for monitoring and management.
    
    Purpose:
    - Track active devices/browsers for each user
    - Enable "View Active Sessions" feature
    - Allow users to revoke sessions remotely
    - Security monitoring (unusual locations, multiple simultaneous logins)
    
    Lifecycle:
    - Created on login
    - Updated on token refresh
    - Marked inactive on logout or token expiration
    - Auto-cleanup after 30 days of inactivity
    """
    __tablename__ = "user_sessions"
    
    # Primary key
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    
    # User reference
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    
    # Session identifier (links to refresh token family)
    session_token: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    
    # Session status
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", index=True)
    
    # Device information
    device_name: Mapped[str | None] = mapped_column(String(255))
    device_type: Mapped[str | None] = mapped_column(String(50))  # "desktop", "mobile", "tablet"
    browser: Mapped[str | None] = mapped_column(String(100))
    os: Mapped[str | None] = mapped_column(String(100))
    
    # Location tracking (for security)
    ip_address: Mapped[str | None] = mapped_column(INET, index=True)
    location: Mapped[str | None] = mapped_column(String(255))  # e.g., "San Francisco, CA, US"
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=text("CURRENT_TIMESTAMP")
    )
    last_activity_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        index=True
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    
    # Termination info
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    end_reason: Mapped[str | None] = mapped_column(String(100))  # "logout", "expired", "revoked", "password_reset"
    
    __table_args__ = (
        # Find active sessions for a user
        Index('ix_user_sessions_user_active', 'user_id', 'is_active', 'last_activity_at'),
        # Cleanup expired sessions
        Index('ix_user_sessions_expires_at', 'expires_at', 'is_active'),
        # Security monitoring (multiple IPs)
        Index('ix_user_sessions_user_ip', 'user_id', 'ip_address'),
    )


class LoginAttempt(Base):
    """
    Track login attempts for security monitoring and rate limiting.
    
    Use cases:
    - Brute force detection
    - Account lockout after N failed attempts
    - Security alerts for unusual activity
    - Compliance audit trail
    
    Retention: Keep 90 days for security analysis.
    """
    __tablename__ = "login_attempts"
    
    # Primary key
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    
    # Attempted email (may not exist in users table)
    email: Mapped[str] = mapped_column(String(255), index=True)
    
    # User ID if successful login
    user_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"))
    
    # Attempt result
    success: Mapped[bool] = mapped_column(Boolean, index=True)
    failure_reason: Mapped[str | None] = mapped_column(String(255))  # "invalid_credentials", "account_locked", "email_not_verified"
    
    # Request metadata
    ip_address: Mapped[str | None] = mapped_column(INET, index=True)
    user_agent: Mapped[str | None] = mapped_column(Text)
    
    # Timestamp
    attempted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=text("CURRENT_TIMESTAMP"),
        index=True
    )
    
    __table_args__ = (
        # Rate limiting: count recent attempts by IP
        Index('ix_login_attempts_ip_time', 'ip_address', 'attempted_at'),
        # Rate limiting: count recent attempts by email
        Index('ix_login_attempts_email_time', 'email', 'attempted_at', 'success'),
        # Security monitoring: failed attempts
        Index('ix_login_attempts_failed', 'success', 'attempted_at'),
    )
