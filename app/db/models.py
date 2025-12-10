"""
SQLAlchemy async models for PostgreSQL backend.

Purpose: Define database schema with typed columns + JSONB for dynamic fields.
Validation: Run alembic revision --autogenerate to verify model structure.

Key design decisions:
- Use string PKs (client_id, project_id) matching 8-char hex IDs from Sheets
- JSONB 'extra' column for dynamic/evolving schema fields
- GIN indexes on JSONB for fast queries
- created_at/updated_at for audit trail
"""

from datetime import datetime
from typing import Any, Dict
from sqlalchemy import String, Text, DateTime, Boolean, Numeric, Index, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class Client(Base):
    """
    Client/customer entity migrated from Google Sheets 'Clients' tab.
    
    Typed columns: frequently queried fields
    extra: JSONB for dynamic fields (custom fields, legacy columns)
    """
    __tablename__ = "clients"
    
    # Primary key - UUID for unique identification
    client_id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    
    # Business ID - human-friendly immutable ID (CL-00001, CL-00002, etc.)
    business_id: Mapped[str | None] = mapped_column(String(20), unique=True, index=True)
    
    # Core fields
    full_name: Mapped[str | None] = mapped_column(String(255), index=True)
    email: Mapped[str | None] = mapped_column(String(255), index=True)
    phone: Mapped[str | None] = mapped_column(String(50))
    address: Mapped[str | None] = mapped_column(Text)
    city: Mapped[str | None] = mapped_column(String(100))
    state: Mapped[str | None] = mapped_column(String(50))
    zip_code: Mapped[str | None] = mapped_column(String(20))
    
    # Business fields
    status: Mapped[str | None] = mapped_column(String(50), index=True)  # Active, Inactive, Lead
    client_type: Mapped[str | None] = mapped_column(String(50))  # Residential, Commercial
    
    # QuickBooks integration
    qb_customer_id: Mapped[str | None] = mapped_column(String(50), index=True)
    qb_display_name: Mapped[str | None] = mapped_column(String(255))
    qb_sync_status: Mapped[str | None] = mapped_column(String(50))  # synced, pending, error
    qb_last_sync: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    
    # Dynamic fields from Sheets
    extra: Mapped[Dict[str, Any] | None] = mapped_column(JSONB)
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=datetime.utcnow
    )
    
    __table_args__ = (
        # GIN index for JSONB queries
        Index('ix_clients_extra_gin', 'extra', postgresql_using='gin'),
        # Case-insensitive search on name
        Index('ix_clients_full_name_lower', text('lower(full_name)')),
    )


class Project(Base):
    """
    Project entity from 'Projects' sheet tab.
    
    Links to clients via client_id FK.
    """
    __tablename__ = "projects"
    
    # Primary key - UUID for unique identification
    project_id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    
    # Business ID - human-friendly immutable ID (PRJ-00001, PRJ-00002, etc.)
    business_id: Mapped[str | None] = mapped_column(String(20), unique=True, index=True)
    
    # Foreign key to client
    client_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), index=True)
    
    # Core fields
    project_name: Mapped[str | None] = mapped_column(String(255))
    project_address: Mapped[str | None] = mapped_column(Text)
    project_type: Mapped[str | None] = mapped_column(String(100))  # Kitchen Remodel, Addition, etc.
    status: Mapped[str | None] = mapped_column(String(50), index=True)  # Planning, Active, Complete
    
    # Financial
    budget: Mapped[float | None] = mapped_column(Numeric(12, 2))
    actual_cost: Mapped[float | None] = mapped_column(Numeric(12, 2))
    
    # Timeline
    start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completion_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    
    # Notes and description
    description: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    
    # QuickBooks
    qb_estimate_id: Mapped[str | None] = mapped_column(String(50))
    qb_invoice_id: Mapped[str | None] = mapped_column(String(50))
    
    # Dynamic fields
    extra: Mapped[Dict[str, Any] | None] = mapped_column(JSONB)
    
    # Audit
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=datetime.utcnow
    )
    
    __table_args__ = (
        Index('ix_projects_extra_gin', 'extra', postgresql_using='gin'),
        Index('ix_projects_dates', 'start_date', 'end_date'),
    )


class Permit(Base):
    """
    Building permit tracking from 'Permits' sheet.
    """
    __tablename__ = "permits"
    
    # Primary key - UUID for unique identification
    permit_id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    
    # Business ID - human-friendly immutable ID (PRM-00001, PRM-00002, etc.)
    business_id: Mapped[str | None] = mapped_column(String(20), unique=True, index=True)
    
    # Foreign keys
    project_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), index=True)
    client_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), index=True)
    
    # Permit details
    permit_number: Mapped[str | None] = mapped_column(String(100), unique=True, index=True)
    permit_type: Mapped[str | None] = mapped_column(String(100))  # Building, Electrical, Plumbing
    status: Mapped[str | None] = mapped_column(String(50), index=True)  # Pending, Approved, Expired
    
    # Dates
    application_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    approval_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    expiration_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    
    # Details
    issuing_authority: Mapped[str | None] = mapped_column(String(255))
    inspector_name: Mapped[str | None] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text)
    
    # Dynamic fields
    extra: Mapped[Dict[str, Any] | None] = mapped_column(JSONB)
    
    # Audit
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=datetime.utcnow
    )
    
    __table_args__ = (
        Index('ix_permits_extra_gin', 'extra', postgresql_using='gin'),
    )


class Payment(Base):
    """
    Payment tracking from 'Payments' sheet.
    """
    __tablename__ = "payments"
    
    # Primary key - UUID for unique identification
    payment_id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    
    # Business ID - human-friendly immutable ID (PAY-00001, PAY-00002, etc.)
    business_id: Mapped[str | None] = mapped_column(String(20), unique=True, index=True)
    
    # Foreign keys
    client_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), index=True)
    project_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), index=True)
    
    # Payment details
    amount: Mapped[float | None] = mapped_column(Numeric(12, 2))
    payment_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    payment_method: Mapped[str | None] = mapped_column(String(50))  # Check, Credit Card, Wire
    status: Mapped[str | None] = mapped_column(String(50), index=True)  # Pending, Cleared, Failed
    
    # References
    check_number: Mapped[str | None] = mapped_column(String(50))
    transaction_id: Mapped[str | None] = mapped_column(String(100))
    
    # QuickBooks
    qb_payment_id: Mapped[str | None] = mapped_column(String(50), index=True)
    qb_sync_status: Mapped[str | None] = mapped_column(String(50))
    
    # Notes
    notes: Mapped[str | None] = mapped_column(Text)
    
    # Dynamic fields
    extra: Mapped[Dict[str, Any] | None] = mapped_column(JSONB)
    
    # Audit
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=datetime.utcnow
    )
    
    __table_args__ = (
        Index('ix_payments_extra_gin', 'extra', postgresql_using='gin'),
    )


class User(Base):
    """
    User authentication from 'Users' sheet.
    
    Migrated to DB to improve auth performance and security.
    """
    __tablename__ = "users"
    
    # Primary key - UUID for unique identification
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    
    # Auth fields
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    
    # Profile
    full_name: Mapped[str | None] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50), default="user")  # admin, user, readonly
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    
    # Dynamic fields
    extra: Mapped[Dict[str, Any] | None] = mapped_column(JSONB)
    
    # Audit
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=datetime.utcnow
    )


class QuickBooksToken(Base):
    """
    QuickBooks OAuth2 tokens - migrated from 'QB_Tokens' sheet.
    
    Stores access/refresh tokens with automatic expiry tracking.
    """
    __tablename__ = "quickbooks_tokens"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # OAuth tokens
    realm_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    access_token: Mapped[str] = mapped_column(Text)
    refresh_token: Mapped[str] = mapped_column(Text)
    
    # Expiry tracking
    access_token_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    refresh_token_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    
    # Environment
    environment: Mapped[str] = mapped_column(String(20), default="production")  # sandbox, production
    
    # Audit
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=datetime.utcnow
    )


class QuickBooksCustomerCache(Base):
    """
    Cache for QuickBooks customer data to reduce API calls.
    
    TTL-based cache refreshed every 2 minutes during active use.
    """
    __tablename__ = "quickbooks_customers_cache"
    
    # QuickBooks customer ID as primary key
    qb_customer_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    
    # QB data snapshot
    display_name: Mapped[str | None] = mapped_column(String(255))
    company_name: Mapped[str | None] = mapped_column(String(255))
    given_name: Mapped[str | None] = mapped_column(String(255))
    family_name: Mapped[str | None] = mapped_column(String(255))
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(50))
    
    # Full QB response
    qb_data: Mapped[Dict[str, Any] | None] = mapped_column(JSONB)
    
    # Cache metadata
    cached_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=text("CURRENT_TIMESTAMP"),
        index=True
    )
    
    __table_args__ = (
        Index('ix_qb_customers_cached_at', 'cached_at'),
    )


class QuickBooksInvoiceCache(Base):
    """
    Cache for QuickBooks invoice data.
    """
    __tablename__ = "quickbooks_invoices_cache"
    
    # QuickBooks invoice ID as primary key
    qb_invoice_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    
    # Invoice summary
    customer_id: Mapped[str | None] = mapped_column(String(50), index=True)
    doc_number: Mapped[str | None] = mapped_column(String(50))
    total_amount: Mapped[float | None] = mapped_column(Numeric(12, 2))
    balance: Mapped[float | None] = mapped_column(Numeric(12, 2))
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    
    # Full QB response
    qb_data: Mapped[Dict[str, Any] | None] = mapped_column(JSONB)
    
    # Cache metadata
    cached_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=text("CURRENT_TIMESTAMP"),
        index=True
    )
