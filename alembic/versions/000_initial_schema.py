"""Initial schema

Revision ID: 000
Revises: 
Create Date: 2025-12-10 18:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '000'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create clients table
    op.create_table('clients',
    sa.Column('client_id', sa.String(length=16), nullable=False),
    sa.Column('full_name', sa.String(length=255), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('phone', sa.String(length=50), nullable=True),
    sa.Column('address', sa.Text(), nullable=True),
    sa.Column('city', sa.String(length=100), nullable=True),
    sa.Column('state', sa.String(length=50), nullable=True),
    sa.Column('zip_code', sa.String(length=20), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=True),
    sa.Column('client_type', sa.String(length=50), nullable=True),
    sa.Column('qb_customer_id', sa.String(length=50), nullable=True),
    sa.Column('qb_display_name', sa.String(length=255), nullable=True),
    sa.Column('qb_sync_status', sa.String(length=50), nullable=True),
    sa.Column('qb_last_sync', sa.DateTime(timezone=True), nullable=True),
    sa.Column('extra', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.PrimaryKeyConstraint('client_id')
    )
    op.create_index('ix_clients_email', 'clients', ['email'], unique=False)
    op.create_index('ix_clients_extra_gin', 'clients', ['extra'], unique=False, postgresql_using='gin')
    op.create_index('ix_clients_full_name', 'clients', ['full_name'], unique=False)
    op.create_index('ix_clients_full_name_lower', 'clients', [sa.text('lower(full_name)')], unique=False)
    op.create_index('ix_clients_qb_customer_id', 'clients', ['qb_customer_id'], unique=False)
    op.create_index('ix_clients_status', 'clients', ['status'], unique=False)

    # Create projects table
    op.create_table('projects',
    sa.Column('project_id', sa.String(length=16), nullable=False),
    sa.Column('client_id', sa.String(length=16), nullable=True),
    sa.Column('project_name', sa.String(length=255), nullable=True),
    sa.Column('project_address', sa.Text(), nullable=True),
    sa.Column('project_type', sa.String(length=100), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=True),
    sa.Column('budget', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('actual_cost', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('start_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('completion_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('qb_estimate_id', sa.String(length=50), nullable=True),
    sa.Column('qb_invoice_id', sa.String(length=50), nullable=True),
    sa.Column('extra', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.PrimaryKeyConstraint('project_id')
    )
    op.create_index('ix_projects_client_id', 'projects', ['client_id'], unique=False)
    op.create_index('ix_projects_dates', 'projects', ['start_date', 'end_date'], unique=False)
    op.create_index('ix_projects_extra_gin', 'projects', ['extra'], unique=False, postgresql_using='gin')
    op.create_index('ix_projects_status', 'projects', ['status'], unique=False)

    # Create permits table
    op.create_table('permits',
    sa.Column('permit_id', sa.String(length=16), nullable=False),
    sa.Column('project_id', sa.String(length=16), nullable=True),
    sa.Column('client_id', sa.String(length=16), nullable=True),
    sa.Column('permit_number', sa.String(length=100), nullable=True),
    sa.Column('permit_type', sa.String(length=100), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=True),
    sa.Column('application_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('approval_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('expiration_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('issuing_authority', sa.String(length=255), nullable=True),
    sa.Column('inspector_name', sa.String(length=255), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('extra', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.PrimaryKeyConstraint('permit_id')
    )
    op.create_index('ix_permits_client_id', 'permits', ['client_id'], unique=False)
    op.create_index('ix_permits_extra_gin', 'permits', ['extra'], unique=False, postgresql_using='gin')
    op.create_index('ix_permits_permit_number', 'permits', ['permit_number'], unique=True)
    op.create_index('ix_permits_project_id', 'permits', ['project_id'], unique=False)
    op.create_index('ix_permits_status', 'permits', ['status'], unique=False)

    # Create payments table
    op.create_table('payments',
    sa.Column('payment_id', sa.String(length=16), nullable=False),
    sa.Column('client_id', sa.String(length=16), nullable=True),
    sa.Column('project_id', sa.String(length=16), nullable=True),
    sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('payment_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('payment_method', sa.String(length=50), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=True),
    sa.Column('check_number', sa.String(length=50), nullable=True),
    sa.Column('transaction_id', sa.String(length=100), nullable=True),
    sa.Column('qb_payment_id', sa.String(length=50), nullable=True),
    sa.Column('qb_sync_status', sa.String(length=50), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('extra', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.PrimaryKeyConstraint('payment_id')
    )
    op.create_index('ix_payments_client_id', 'payments', ['client_id'], unique=False)
    op.create_index('ix_payments_extra_gin', 'payments', ['extra'], unique=False, postgresql_using='gin')
    op.create_index('ix_payments_payment_date', 'payments', ['payment_date'], unique=False)
    op.create_index('ix_payments_project_id', 'payments', ['project_id'], unique=False)
    op.create_index('ix_payments_qb_payment_id', 'payments', ['qb_payment_id'], unique=False)
    op.create_index('ix_payments_status', 'payments', ['status'], unique=False)

    # Create users table
    op.create_table('users',
    sa.Column('user_id', sa.String(length=16), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('full_name', sa.String(length=255), nullable=True),
    sa.Column('role', sa.String(length=50), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
    sa.Column('extra', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # Create quickbooks_tokens table
    op.create_table('quickbooks_tokens',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('realm_id', sa.String(length=50), nullable=False),
    sa.Column('access_token', sa.Text(), nullable=False),
    sa.Column('refresh_token', sa.Text(), nullable=False),
    sa.Column('access_token_expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('refresh_token_expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('environment', sa.String(length=20), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_quickbooks_tokens_realm_id', 'quickbooks_tokens', ['realm_id'], unique=True)

    # Create quickbooks_customers_cache table
    op.create_table('quickbooks_customers_cache',
    sa.Column('qb_customer_id', sa.String(length=50), nullable=False),
    sa.Column('display_name', sa.String(length=255), nullable=True),
    sa.Column('company_name', sa.String(length=255), nullable=True),
    sa.Column('given_name', sa.String(length=255), nullable=True),
    sa.Column('family_name', sa.String(length=255), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('phone', sa.String(length=50), nullable=True),
    sa.Column('qb_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('cached_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.PrimaryKeyConstraint('qb_customer_id')
    )
    op.create_index('ix_qb_customers_cached_at', 'quickbooks_customers_cache', ['cached_at'], unique=False)

    # Create quickbooks_invoices_cache table
    op.create_table('quickbooks_invoices_cache',
    sa.Column('qb_invoice_id', sa.String(length=50), nullable=False),
    sa.Column('customer_id', sa.String(length=50), nullable=True),
    sa.Column('doc_number', sa.String(length=50), nullable=True),
    sa.Column('total_amount', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('balance', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('qb_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('cached_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.PrimaryKeyConstraint('qb_invoice_id')
    )
    op.create_index('ix_quickbooks_invoices_cache_cached_at', 'quickbooks_invoices_cache', ['cached_at'], unique=False)
    op.create_index('ix_quickbooks_invoices_cache_customer_id', 'quickbooks_invoices_cache', ['customer_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_quickbooks_invoices_cache_customer_id', table_name='quickbooks_invoices_cache')
    op.drop_index('ix_quickbooks_invoices_cache_cached_at', table_name='quickbooks_invoices_cache')
    op.drop_table('quickbooks_invoices_cache')
    op.drop_index('ix_qb_customers_cached_at', table_name='quickbooks_customers_cache')
    op.drop_table('quickbooks_customers_cache')
    op.drop_index('ix_quickbooks_tokens_realm_id', table_name='quickbooks_tokens')
    op.drop_table('quickbooks_tokens')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
    op.drop_index('ix_payments_status', table_name='payments')
    op.drop_index('ix_payments_qb_payment_id', table_name='payments')
    op.drop_index('ix_payments_project_id', table_name='payments')
    op.drop_index('ix_payments_payment_date', table_name='payments')
    op.drop_index('ix_payments_extra_gin', table_name='payments')
    op.drop_index('ix_payments_client_id', table_name='payments')
    op.drop_table('payments')
    op.drop_index('ix_permits_status', table_name='permits')
    op.drop_index('ix_permits_project_id', table_name='permits')
    op.drop_index('ix_permits_permit_number', table_name='permits')
    op.drop_index('ix_permits_extra_gin', table_name='permits')
    op.drop_index('ix_permits_client_id', table_name='permits')
    op.drop_table('permits')
    op.drop_index('ix_projects_status', table_name='projects')
    op.drop_index('ix_projects_extra_gin', table_name='projects')
    op.drop_index('ix_projects_dates', table_name='projects')
    op.drop_index('ix_projects_client_id', table_name='projects')
    op.drop_table('projects')
    op.drop_index('ix_clients_status', table_name='clients')
    op.drop_index('ix_clients_qb_customer_id', table_name='clients')
    op.drop_index('ix_clients_full_name_lower', table_name='clients')
    op.drop_index('ix_clients_full_name', table_name='clients')
    op.drop_index('ix_clients_extra_gin', table_name='clients')
    op.drop_index('ix_clients_email', table_name='clients')
    op.drop_table('clients')
