"""add_additional_type_enums

Revision ID: 044de0a80b9e
Revises: bf5d364b4f5d
Create Date: 2025-12-14 23:30:15.333379

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '044de0a80b9e'
down_revision: Union[str, None] = 'bf5d364b4f5d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ========================================================================
    # 1. Permit Type ENUM
    # ========================================================================
    permit_type_enum = sa.Enum(
        'BUILDING',
        'ELECTRICAL',
        'PLUMBING',
        'MECHANICAL',
        'ZONING',
        'FIRE',
        'ENVIRONMENTAL',
        'OTHER',
        name='permit_type_enum',
        create_type=True
    )
    permit_type_enum.create(op.get_bind(), checkfirst=True)
    
    # Migrate existing permit_type values
    op.execute("""
        UPDATE permits 
        SET permit_type = CASE
            WHEN LOWER(permit_type) IN ('building permit', 'building', 'residential addition', 'residential alteration') THEN 'BUILDING'
            WHEN LOWER(permit_type) IN ('electrical', 'electric') THEN 'ELECTRICAL'
            WHEN LOWER(permit_type) IN ('plumbing', 'plumb') THEN 'PLUMBING'
            WHEN LOWER(permit_type) IN ('mechanical', 'hvac', 'mech') THEN 'MECHANICAL'
            WHEN LOWER(permit_type) IN ('zoning', 'zone') THEN 'ZONING'
            WHEN LOWER(permit_type) IN ('fire', 'fire safety') THEN 'FIRE'
            WHEN LOWER(permit_type) IN ('environmental', 'env') THEN 'ENVIRONMENTAL'
            WHEN LOWER(permit_type) IN ('plan review', 'other') THEN 'OTHER'
            ELSE 'OTHER'
        END
        WHERE permit_type IS NOT NULL
    """)
    
    op.alter_column(
        'permits',
        'permit_type',
        type_=permit_type_enum,
        postgresql_using='permit_type::permit_type_enum',
        existing_type=sa.String(100),
        existing_nullable=True
    )
    
    # ========================================================================
    # 2. Project Type ENUM
    # ========================================================================
    project_type_enum = sa.Enum(
        'NEW_CONSTRUCTION',
        'RENOVATION',
        'REMODEL',
        'ADDITION',
        'RESIDENTIAL',
        'COMMERCIAL',
        'OTHER',
        name='project_type_enum',
        create_type=True
    )
    project_type_enum.create(op.get_bind(), checkfirst=True)
    
    # Migrate existing project_type values
    op.execute("""
        UPDATE projects 
        SET project_type = CASE
            WHEN LOWER(project_type) IN ('new construction', 'new build', 'new_construction') THEN 'NEW_CONSTRUCTION'
            WHEN LOWER(project_type) = 'renovation' THEN 'RENOVATION'
            WHEN LOWER(project_type) = 'remodel' THEN 'REMODEL'
            WHEN LOWER(project_type) = 'addition' THEN 'ADDITION'
            WHEN LOWER(project_type) = 'residential' THEN 'RESIDENTIAL'
            WHEN LOWER(project_type) = 'commercial' THEN 'COMMERCIAL'
            WHEN LOWER(project_type) = 'other' THEN 'OTHER'
            ELSE 'OTHER'
        END
        WHERE project_type IS NOT NULL
    """)
    
    op.alter_column(
        'projects',
        'project_type',
        type_=project_type_enum,
        postgresql_using='project_type::project_type_enum',
        existing_type=sa.String(100),
        existing_nullable=True
    )
    
    # ========================================================================
    # 3. License Type ENUM (for licensed_businesses)
    # ========================================================================
    license_type_enum = sa.Enum(
        'GENERAL_CONTRACTOR',
        'ELECTRICAL',
        'PLUMBING',
        'MECHANICAL',
        'SPECIALTY',
        name='license_type_enum',
        create_type=True
    )
    license_type_enum.create(op.get_bind(), checkfirst=True)
    
    # Migrate existing license_type values
    op.execute("""
        UPDATE licensed_businesses 
        SET license_type = CASE
            WHEN LOWER(license_type) IN ('general contractor', 'general', 'gc', 'general_contractor') THEN 'GENERAL_CONTRACTOR'
            WHEN LOWER(license_type) IN ('electrical', 'electric', 'electrician') THEN 'ELECTRICAL'
            WHEN LOWER(license_type) IN ('plumbing', 'plumber') THEN 'PLUMBING'
            WHEN LOWER(license_type) IN ('mechanical', 'hvac', 'mech') THEN 'MECHANICAL'
            WHEN LOWER(license_type) IN ('specialty', 'special', 'other') THEN 'SPECIALTY'
            ELSE 'SPECIALTY'
        END
        WHERE license_type IS NOT NULL
    """)
    
    op.alter_column(
        'licensed_businesses',
        'license_type',
        type_=license_type_enum,
        postgresql_using='license_type::license_type_enum',
        existing_type=sa.String(100),
        existing_nullable=False
    )
    
    # ========================================================================
    # 4. License Status ENUM (for licensed_businesses and qualifiers)
    # ========================================================================
    license_status_enum = sa.Enum(
        'ACTIVE',
        'INACTIVE',
        'SUSPENDED',
        'REVOKED',
        name='license_status_enum',
        create_type=True
    )
    license_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Migrate licensed_businesses.license_status
    op.execute("""
        UPDATE licensed_businesses 
        SET license_status = CASE
            WHEN LOWER(license_status) = 'active' THEN 'ACTIVE'
            WHEN LOWER(license_status) IN ('inactive', 'expired') THEN 'INACTIVE'
            WHEN LOWER(license_status) = 'suspended' THEN 'SUSPENDED'
            WHEN LOWER(license_status) = 'revoked' THEN 'REVOKED'
            ELSE 'ACTIVE'
        END
        WHERE license_status IS NOT NULL
    """)
    
    # Drop default before type change (existing default is lowercase 'active')
    op.alter_column('licensed_businesses', 'license_status', server_default=None)
    
    op.alter_column(
        'licensed_businesses',
        'license_status',
        type_=license_status_enum,
        postgresql_using='license_status::license_status_enum',
        existing_type=sa.String(50),
        existing_nullable=False,
        server_default=sa.text("'ACTIVE'")  # Add back with correct uppercase default
    )
    
    # Migrate qualifiers.license_status
    # Drop CHECK constraint first (only allows lowercase values)
    op.drop_constraint('ck_qualifiers_license_status', 'qualifiers', type_='check')
    
    op.execute("""
        UPDATE qualifiers 
        SET license_status = CASE
            WHEN LOWER(license_status) = 'active' THEN 'ACTIVE'
            WHEN LOWER(license_status) IN ('inactive', 'expired') THEN 'INACTIVE'
            WHEN LOWER(license_status) = 'suspended' THEN 'SUSPENDED'
            WHEN LOWER(license_status) = 'revoked' THEN 'REVOKED'
            ELSE 'ACTIVE'
        END
        WHERE license_status IS NOT NULL
    """)
    
    # Drop default before type change (existing default is lowercase 'active')
    op.alter_column('qualifiers', 'license_status', server_default=None)
    
    op.alter_column(
        'qualifiers',
        'license_status',
        type_=license_status_enum,
        postgresql_using='license_status::license_status_enum',
        existing_type=sa.String(50),
        existing_nullable=False,
        server_default=sa.text("'ACTIVE'")  # Add back with correct uppercase default
    )
    
    # ========================================================================
    # 5. Action Type ENUM (for oversight_actions)
    # ========================================================================
    action_type_enum = sa.Enum(
        'SITE_VISIT',
        'PLAN_REVIEW',
        'PERMIT_REVIEW',
        'CLIENT_MEETING',
        'INSPECTION_ATTENDANCE',
        'PHONE_CONSULTATION',
        name='action_type_enum',
        create_type=True
    )
    action_type_enum.create(op.get_bind(), checkfirst=True)
    
    # Migrate oversight_actions.action_type
    op.execute("""
        UPDATE oversight_actions 
        SET action_type = CASE
            WHEN LOWER(action_type) IN ('site visit', 'site_visit', 'visit') THEN 'SITE_VISIT'
            WHEN LOWER(action_type) IN ('plan review', 'plan_review', 'review') THEN 'PLAN_REVIEW'
            WHEN LOWER(action_type) IN ('permit review', 'permit_review') THEN 'PERMIT_REVIEW'
            WHEN LOWER(action_type) IN ('client meeting', 'client_meeting', 'meeting') THEN 'CLIENT_MEETING'
            WHEN LOWER(action_type) IN ('inspection attendance', 'inspection_attendance', 'inspection') THEN 'INSPECTION_ATTENDANCE'
            WHEN LOWER(action_type) IN ('phone consultation', 'phone_consultation', 'phone', 'call') THEN 'PHONE_CONSULTATION'
            ELSE 'SITE_VISIT'
        END
        WHERE action_type IS NOT NULL
    """)
    
    op.alter_column(
        'oversight_actions',
        'action_type',
        type_=action_type_enum,
        postgresql_using='action_type::action_type_enum',
        existing_type=sa.String(100),
        existing_nullable=True
    )


def downgrade() -> None:
    # Revert all columns to String types
    op.alter_column('permits', 'permit_type', type_=sa.String(100), existing_nullable=True)
    op.alter_column('projects', 'project_type', type_=sa.String(100), existing_nullable=True)
    op.alter_column('licensed_businesses', 'license_type', type_=sa.String(100), existing_nullable=False)
    op.alter_column('licensed_businesses', 'license_status', type_=sa.String(50), existing_nullable=False)
    op.alter_column('qualifiers', 'license_status', type_=sa.String(50), existing_nullable=False)
    op.alter_column('oversight_actions', 'action_type', type_=sa.String(100), existing_nullable=True)
    
    # Drop ENUM types
    sa.Enum(name='permit_type_enum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='project_type_enum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='license_type_enum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='license_status_enum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='action_type_enum').drop(op.get_bind(), checkfirst=True)
