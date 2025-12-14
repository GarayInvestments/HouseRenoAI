"""add qualifier compliance tables

Revision ID: 20251214_0100
Revises: f2edebb3266e
Create Date: 2025-12-14 01:00:00.000000

Phase Q.1: Qualifier Compliance Foundation
- Creates 5 new tables for compliance enforcement
- Adds qualifier_id FK to projects table
- Adds licensed_business_id FK to permits table
- Creates triggers for capacity limits and cutoff date enforcement
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251214_0100'
down_revision = 'f2edebb3266e'
branch_labels = None
depends_on = None


def upgrade():
    # 0. Enable pgcrypto extension for gen_random_uuid()
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
    
    # 1. Create licensed_businesses table
    # MEDIUM #4: qualifying_user_id is DENORMALIZED and subject to data drift
    # MITIGATION STRATEGY:
    # - Column retained for UI convenience only (display "current qualifier" without junction query)
    # - NEVER use in API business logic, reporting, or compliance enforcement
    # - NEVER expose via API write endpoints (update via junction table triggers only)
    # - All compliance queries MUST use licensed_business_qualifiers junction table
    # - Future: Consider replacing with database VIEW or computed query in Phase Q.3+
    op.create_table(
        'licensed_businesses',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('business_id', sa.String(50), nullable=False, comment='Business ID: LB-00001'),
        sa.Column('business_name', sa.String(255), nullable=False, comment='DBA or trade name - not unique'),
        sa.Column('legal_name', sa.String(255), nullable=False),
        sa.Column('dba_name', sa.String(255), nullable=True),
        sa.Column('license_number', sa.String(100), nullable=False, unique=True, comment='NCLBGC license number'),
        sa.Column('license_type', sa.String(100), nullable=False, comment='e.g., Unlimited, Intermediate, Limited'),
        sa.Column('license_status', sa.String(50), nullable=False, server_default='active', comment='active, inactive, suspended, revoked'),
        sa.Column('license_issue_date', sa.Date(), nullable=True),
        sa.Column('license_expiration_date', sa.Date(), nullable=True),
        sa.Column('qualifying_user_id', sa.UUID(), nullable=True, comment='DENORMALIZED / UI ONLY - NEVER use in enforcement. Use licensed_business_qualifiers for all compliance queries.'),
        sa.Column('fee_model', sa.String(50), nullable=True, comment='FLAT, MATRIX, HYBRID'),
        sa.Column('active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('business_id')
    )
    # Create FK after users table is confirmed to exist
    op.create_foreign_key('fk_licensed_businesses_qualifying_user_id', 'licensed_businesses', 'users', ['qualifying_user_id'], ['id'], ondelete='SET NULL')
    op.create_index('ix_licensed_businesses_business_id', 'licensed_businesses', ['business_id'])
    op.create_index('ix_licensed_businesses_business_name', 'licensed_businesses', ['business_name'])
    op.create_index('ix_licensed_businesses_license_number', 'licensed_businesses', ['license_number'])
    op.create_index('ix_licensed_businesses_license_status', 'licensed_businesses', ['license_status'])
    op.create_index('ix_licensed_businesses_qualifying_user_id', 'licensed_businesses', ['qualifying_user_id'])
    op.create_index('ix_licensed_businesses_active', 'licensed_businesses', ['active'])

    # 2. Create qualifiers table (WITH USER_ID FOR IDENTITY)
    op.create_table(
        'qualifiers',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('qualifier_id', sa.String(50), nullable=False, comment='Qualifier ID: QF-00001'),
        sa.Column('user_id', sa.UUID(), nullable=False, unique=True, comment='Link to operational user account'),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('license_number', sa.String(100), nullable=False, unique=True, comment='NCLBGC license number'),
        sa.Column('license_type', sa.String(100), nullable=False, comment='e.g., Unlimited, Intermediate, Limited'),
        sa.Column('license_status', sa.String(50), nullable=False, server_default='active', comment='active, inactive, suspended, revoked'),
        sa.CheckConstraint("license_status IN ('active', 'inactive', 'suspended', 'revoked')", name='ck_qualifiers_license_status'),
        sa.Column('license_issue_date', sa.Date(), nullable=True),
        sa.Column('license_expiration_date', sa.Date(), nullable=True),
        sa.Column('max_licenses_allowed', sa.Integer(), nullable=False, server_default='2', comment='Override for max licensed businesses - ONLY SOURCE OF TRUTH'),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('qualifier_id')
    )
    # Create FK to users
    op.create_foreign_key('fk_qualifiers_user_id', 'qualifiers', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_index('ix_qualifiers_qualifier_id', 'qualifiers', ['qualifier_id'])
    op.create_index('ix_qualifiers_user_id', 'qualifiers', ['user_id'])
    op.create_index('ix_qualifiers_license_number', 'qualifiers', ['license_number'])
    op.create_index('ix_qualifiers_license_status', 'qualifiers', ['license_status'])

    # 3. Create licensed_business_qualifiers junction table (many-to-many with time bounds)
    op.create_table(
        'licensed_business_qualifiers',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('licensed_business_id', sa.UUID(), nullable=False),
        sa.Column('qualifier_id', sa.UUID(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False, comment='When qualifier began serving this business'),
        sa.Column('end_date', sa.Date(), nullable=True, comment='Legal relationship termination date (null = active)'),
        sa.Column('cutoff_date', sa.DateTime(timezone=True), nullable=True, comment='Operational cutoff for system actions - can be earlier than end_date for transition periods'),
        sa.Column('relationship_type', sa.String(100), nullable=False, server_default='qualification', comment='qualification, consultation, etc.'),
        sa.CheckConstraint("relationship_type IN ('qualification', 'consultation', 'temporary', 'inactive')", name='ck_lbq_relationship_type'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['licensed_business_id'], ['licensed_businesses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['qualifier_id'], ['qualifiers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_lbq_licensed_business_id', 'licensed_business_qualifiers', ['licensed_business_id'])
    op.create_index('ix_lbq_qualifier_id', 'licensed_business_qualifiers', ['qualifier_id'])
    op.create_index('ix_lbq_active', 'licensed_business_qualifiers', ['licensed_business_id', 'qualifier_id'], 
                    postgresql_where=sa.text('end_date IS NULL'))
    # FIX #4: Add compliance query indexes for reporting
    op.create_index('ix_lbq_active_dates', 'licensed_business_qualifiers', ['qualifier_id', 'start_date', 'end_date'])
    # MUST-FIX #1: Prevent duplicate active relationships for same business-qualifier pair
    op.execute("""
        CREATE UNIQUE INDEX uq_lbq_active_pair
        ON licensed_business_qualifiers (licensed_business_id, qualifier_id)
        WHERE end_date IS NULL
    """)  # Ensures only one active relationship per pair at any time

    # 4. Create oversight_actions table (WITH BUSINESS CONTEXT)
    # CRITICAL: oversight_actions is THE CANONICAL COMPLIANCE RECORD
    # site_visits.oversight_type and inspections.qualifier_attended are SUPPORTING EVIDENCE ONLY
    # Regulators will audit oversight_actions as primary proof of supervision
    op.create_table(
        'oversight_actions',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('action_id', sa.String(50), nullable=False, comment='Action ID: OA-00001'),
        sa.Column('project_id', sa.UUID(), nullable=False),
        sa.Column('licensed_business_id', sa.UUID(), nullable=False, comment='Business context for audit trail'),
        sa.Column('qualifier_id', sa.UUID(), nullable=False),
        sa.Column('licensed_business_qualifier_id', sa.UUID(), nullable=True, comment='MEDIUM FIX #6: Hard FK to exact relationship for immutable audit trail'),
        sa.Column('action_type', sa.String(100), nullable=False, comment='site_visit, plan_review, permit_review, client_meeting'),
        sa.CheckConstraint("action_type IN ('site_visit', 'plan_review', 'permit_review', 'client_meeting', 'inspection_attendance', 'phone_consultation')", name='ck_oversight_actions_action_type'),
        sa.Column('action_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('location', sa.String(255), nullable=True),
        sa.Column('attendees', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Array of attendee objects'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('photos', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Array of photo objects'),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('action_id')
    )
    # Create FKs after table creation
    op.create_foreign_key('fk_oversight_actions_project_id', 'oversight_actions', 'projects', ['project_id'], ['project_id'], ondelete='CASCADE')
    op.create_foreign_key('fk_oversight_actions_licensed_business_id', 'oversight_actions', 'licensed_businesses', ['licensed_business_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_oversight_actions_qualifier_id', 'oversight_actions', 'qualifiers', ['qualifier_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_oversight_actions_lbq_id', 'oversight_actions', 'licensed_business_qualifiers', ['licensed_business_qualifier_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('fk_oversight_actions_created_by', 'oversight_actions', 'users', ['created_by'], ['id'], ondelete='SET NULL')
    op.create_index('ix_oversight_actions_action_id', 'oversight_actions', ['action_id'])
    op.create_index('ix_oversight_actions_project_id', 'oversight_actions', ['project_id'])
    op.create_index('ix_oversight_actions_licensed_business_id', 'oversight_actions', ['licensed_business_id'])
    op.create_index('ix_oversight_actions_qualifier_id', 'oversight_actions', ['qualifier_id'])
    op.create_index('ix_oversight_actions_action_type', 'oversight_actions', ['action_type'])
    op.create_index('ix_oversight_actions_action_date', 'oversight_actions', ['action_date'])
    # FIX #4: Add compliance query index for project-date reporting
    op.create_index('ix_oversight_actions_project_date', 'oversight_actions', ['project_id', 'action_date'])

    # 5. Create compliance_justifications table
    op.create_table(
        'compliance_justifications',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('justification_id', sa.String(50), nullable=False, comment='Justification ID: CJ-00001'),
        sa.Column('rule_violated', sa.String(255), nullable=False, comment='e.g., qualifier_capacity_exceeded, oversight_minimum_not_met'),
        sa.Column('entity_type', sa.String(100), nullable=False, comment='project, permit, licensed_business, qualifier'),
        sa.Column('entity_id', sa.UUID(), nullable=False, comment='ID of the entity being justified'),
        sa.Column('justification_text', sa.Text(), nullable=False),
        sa.Column('approved_by', sa.UUID(), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('justification_id')
    )
    # Create FKs after table creation
    op.create_foreign_key('fk_compliance_justifications_approved_by', 'compliance_justifications', 'users', ['approved_by'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('fk_compliance_justifications_created_by', 'compliance_justifications', 'users', ['created_by'], ['id'], ondelete='SET NULL')
    op.create_index('ix_compliance_justifications_justification_id', 'compliance_justifications', ['justification_id'])
    op.create_index('ix_compliance_justifications_entity', 'compliance_justifications', ['entity_type', 'entity_id'])
    op.create_index('ix_compliance_justifications_rule', 'compliance_justifications', ['rule_violated'])

    # 6. Add compliance columns to projects table (CRITICAL: Business context first)
    # NOTE: engagement_model nullable during Phase Q.1 backfill - will become NOT NULL in Phase Q.2
    op.add_column('projects', sa.Column('licensed_business_id', sa.UUID(), nullable=True, comment='Business entity whose license is used for this project'))
    op.add_column('projects', sa.Column('qualifier_id', sa.UUID(), nullable=True, comment='Qualifier responsible under NCLBGC (references qualifiers table, not users)'))
    op.add_column('projects', sa.Column('engagement_model', sa.String(50), nullable=True, comment='DIRECT_GC or THIRD_PARTY_QUALIFIER'))
    op.execute("ALTER TABLE projects ADD CONSTRAINT ck_projects_engagement_model CHECK (engagement_model IN ('DIRECT_GC', 'THIRD_PARTY_QUALIFIER'))")
    op.add_column('projects', sa.Column('oversight_required', sa.Boolean(), nullable=False, server_default='true', comment='Whether qualifier oversight is legally required'))
    op.add_column('projects', sa.Column('compliance_notes', sa.Text(), nullable=True, comment='Explicit justification or edge-case explanation'))
    op.create_foreign_key('fk_projects_licensed_business_id', 'projects', 'licensed_businesses', ['licensed_business_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('fk_projects_qualifier_id', 'projects', 'qualifiers', ['qualifier_id'], ['id'], ondelete='SET NULL')
    op.create_index('ix_projects_licensed_business_id', 'projects', ['licensed_business_id'])
    op.create_index('ix_projects_qualifier_id', 'projects', ['qualifier_id'])
    op.create_index('ix_projects_engagement_model', 'projects', ['engagement_model'])

    # 7. Add compliance columns to permits table (REGULATOR FACING)
    op.add_column('permits', sa.Column('licensed_business_id', sa.UUID(), nullable=True))
    op.add_column('permits', sa.Column('qualifier_id', sa.UUID(), nullable=True, comment='Qualifier responsible (references qualifiers table, not users)'))
    op.add_column('permits', sa.Column('license_number_used', sa.String(100), nullable=True, comment='Exact license number used on permit application'))
    op.add_column('permits', sa.Column('responsibility_role', sa.String(50), nullable=True, comment='PRIMARY_LICENSE_HOLDER or QUALIFIED_BY_THIRD_PARTY'))
    op.execute("ALTER TABLE permits ADD CONSTRAINT ck_permits_responsibility_role CHECK (responsibility_role IN ('PRIMARY_LICENSE_HOLDER', 'QUALIFIED_BY_THIRD_PARTY'))")
    op.create_foreign_key('fk_permits_licensed_business_id', 'permits', 'licensed_businesses', ['licensed_business_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('fk_permits_qualifier_id', 'permits', 'qualifiers', ['qualifier_id'], ['id'], ondelete='SET NULL')
    op.create_index('ix_permits_licensed_business_id', 'permits', ['licensed_business_id'])
    op.create_index('ix_permits_qualifier_id', 'permits', ['qualifier_id'])

    # 8. Add oversight columns to site_visits table (OVERSIGHT PROOF - SUPPORTING EVIDENCE)
    # IMPORTANT: site_visits oversight fields are SUPPORTING EVIDENCE for oversight_actions
    # Primary compliance record lives in oversight_actions table
    op.add_column('site_visits', sa.Column('oversight_type', sa.String(50), nullable=True, comment='QUALIFIER_SITE_VISIT, PLAN_REVIEW, or INSPECTION_ATTENDANCE'))
    op.execute("ALTER TABLE site_visits ADD CONSTRAINT ck_site_visits_oversight_type CHECK (oversight_type IN ('QUALIFIER_SITE_VISIT', 'PLAN_REVIEW', 'INSPECTION_ATTENDANCE', 'PHONE_CONSULTATION'))")
    op.add_column('site_visits', sa.Column('qualifier_id', sa.UUID(), nullable=True, comment='Qualifier performing oversight (references qualifiers table)'))
    op.add_column('site_visits', sa.Column('qualifier_present', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('site_visits', sa.Column('oversight_justification', sa.Text(), nullable=True, comment='Required explanation for compliance record'))
    op.create_foreign_key('fk_site_visits_qualifier_id', 'site_visits', 'qualifiers', ['qualifier_id'], ['id'], ondelete='SET NULL')
    op.create_index('ix_site_visits_qualifier_id', 'site_visits', ['qualifier_id'])
    op.create_index('ix_site_visits_oversight_type', 'site_visits', ['oversight_type'])

    # 9. Add oversight columns to inspections table (CHAIN LINK - SUPPORTING EVIDENCE)
    # IMPORTANT: inspections.qualifier_attended is SUPPORTING EVIDENCE only
    # Link to oversight_actions via oversight_site_visit_id for full audit trail
    op.add_column('inspections', sa.Column('qualifier_attended', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('inspections', sa.Column('oversight_site_visit_id', sa.UUID(), nullable=True, comment='Links inspection to qualifier oversight visit'))
    op.create_foreign_key('fk_inspections_oversight_site_visit_id', 'inspections', 'site_visits', ['oversight_site_visit_id'], ['visit_id'], ondelete='SET NULL')
    op.create_index('ix_inspections_oversight_site_visit_id', 'inspections', ['oversight_site_visit_id'])

    # 10. Add qualifier flag to users table (UI CONVENIENCE ONLY - NOT COMPLIANCE AUTHORITY)
    op.add_column('users', sa.Column('is_qualifier', sa.Boolean(), nullable=False, server_default='false', comment='UI convenience flag - NOT compliance authority. Use qualifiers table for enforcement.'))
    op.create_index('ix_users_is_qualifier', 'users', ['is_qualifier'])

    # 6. Create business_id sequences for new tables (LOW #3: sequences created before triggers that reference them - correct order)
    op.execute("CREATE SEQUENCE licensed_businesses_business_id_seq START 1;")
    op.execute("CREATE SEQUENCE qualifiers_qualifier_id_seq START 1;")
    op.execute("CREATE SEQUENCE oversight_actions_action_id_seq START 1;")
    op.execute("CREATE SEQUENCE compliance_justifications_justification_id_seq START 1;")

    # 7. Create trigger function for business_id generation
    op.execute("""
        CREATE OR REPLACE FUNCTION generate_business_id()
        RETURNS TRIGGER AS $$
        DECLARE
            prefix TEXT;
            next_num INTEGER;
            new_id TEXT;
        BEGIN
            -- Determine prefix based on table
            CASE TG_TABLE_NAME
                WHEN 'licensed_businesses' THEN
                    prefix := 'LB';
                    next_num := nextval('licensed_businesses_business_id_seq');
                WHEN 'qualifiers' THEN
                    prefix := 'QF';
                    next_num := nextval('qualifiers_qualifier_id_seq');
                WHEN 'oversight_actions' THEN
                    prefix := 'OA';
                    next_num := nextval('oversight_actions_action_id_seq');
                WHEN 'compliance_justifications' THEN
                    prefix := 'CJ';
                    next_num := nextval('compliance_justifications_justification_id_seq');
                ELSE
                    RAISE EXCEPTION 'Unknown table: %', TG_TABLE_NAME;
            END CASE;
            
            -- Generate ID with zero-padding
            new_id := prefix || '-' || LPAD(next_num::TEXT, 5, '0');
            
            -- Assign to appropriate column
            CASE TG_TABLE_NAME
                WHEN 'licensed_businesses' THEN NEW.business_id := new_id;
                WHEN 'qualifiers' THEN NEW.qualifier_id := new_id;
                WHEN 'oversight_actions' THEN NEW.action_id := new_id;
                WHEN 'compliance_justifications' THEN NEW.justification_id := new_id;
            END CASE;
            
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # 8. Create business_id triggers for new tables
    op.execute("""
        CREATE TRIGGER licensed_businesses_business_id_trigger
            BEFORE INSERT ON licensed_businesses
            FOR EACH ROW
            WHEN (NEW.business_id IS NULL OR NEW.business_id = '')
            EXECUTE FUNCTION generate_business_id();
    """)
    op.execute("""
        CREATE TRIGGER qualifiers_qualifier_id_trigger
            BEFORE INSERT ON qualifiers
            FOR EACH ROW
            WHEN (NEW.qualifier_id IS NULL OR NEW.qualifier_id = '')
            EXECUTE FUNCTION generate_business_id();
    """)
    op.execute("""
        CREATE TRIGGER oversight_actions_action_id_trigger
            BEFORE INSERT ON oversight_actions
            FOR EACH ROW
            WHEN (NEW.action_id IS NULL OR NEW.action_id = '')
            EXECUTE FUNCTION generate_business_id();
    """)
    op.execute("""
        CREATE TRIGGER compliance_justifications_justification_id_trigger
            BEFORE INSERT ON compliance_justifications
            FOR EACH ROW
            WHEN (NEW.justification_id IS NULL OR NEW.justification_id = '')
            EXECUTE FUNCTION generate_business_id();
    """)

    # 9. Create trigger function for qualifier capacity check (WITH DATE OVERLAP + FIX UPDATE)
    # LOW #6: RACE CONDITION ACCEPTANCE - Capacity check uses SELECT COUNT without FOR UPDATE
    # Theoretical risk: Under heavy concurrent inserts, two transactions could both count N relationships,
    # both see capacity available, and both insert, exceeding limit by 1.
    # ACCEPTED BECAUSE:
    # - Small qualifier pool (2-5 qualifiers expected, not thousands)
    # - Low write frequency (relationship changes are infrequent: hires, resignations, license additions)
    # - Enforcement context: this is regulatory compliance, not financial/inventory where atomicity critical
    # - Mitigation: unique constraint uq_lbq_active_pair prevents duplicate active relationships for same pair
    # - Cost/benefit: Adding row locks would complicate trigger logic without meaningful risk reduction
    # If high concurrency becomes issue in future: add SELECT ... FOR UPDATE in capacity check
    op.execute("""
        CREATE OR REPLACE FUNCTION check_qualifier_capacity()
        RETURNS TRIGGER AS $$
        DECLARE
            active_count INTEGER;
            max_allowed INTEGER;
        BEGIN
            -- Get max licenses allowed for this qualifier
            SELECT max_licenses_allowed INTO max_allowed
            FROM qualifiers
            WHERE id = NEW.qualifier_id;
            
            -- Count overlapping active relationships for this qualifier
            -- FIX #2: Properly exclude current record on UPDATE
            SELECT COUNT(*) INTO active_count
            FROM licensed_business_qualifiers
            WHERE qualifier_id = NEW.qualifier_id
              AND (
                  (TG_OP = 'INSERT' AND id != COALESCE(NEW.id, '00000000-0000-0000-0000-000000000000'::uuid))
                  OR
                  (TG_OP = 'UPDATE' AND id != OLD.id)
              )
              AND daterange(start_date, COALESCE(end_date, 'infinity'::date)) &&
                  daterange(NEW.start_date, COALESCE(NEW.end_date, 'infinity'::date));
            
            -- Block if at or exceeding capacity
            IF active_count >= max_allowed THEN
                RAISE EXCEPTION 'Qualifier capacity exceeded: Qualifier can serve maximum % licensed businesses (currently serving % with overlapping dates)', max_allowed, active_count;
            END IF;
            
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # 10. Create capacity enforcement trigger (ON INSERT OR UPDATE)
    op.execute("""
        CREATE TRIGGER licensed_business_qualifiers_capacity_trigger
            BEFORE INSERT OR UPDATE ON licensed_business_qualifiers
            FOR EACH ROW
            EXECUTE FUNCTION check_qualifier_capacity();
    """)

    # 11. Create trigger function for cutoff date enforcement (WITH PROPER JOIN + GUARD CLAUSE)
    # MEDIUM #5: CURRENT LIMITATION - Trigger joins through project.licensed_business_id + project.qualifier_id
    # This assumes project has correct qualifier AT TIME OF ACTION. Risk: if project qualifier updated later
    # for correction/backfill, historical oversight actions may retroactively fail validation if re-checked.
    # PHASE Q.2 HARDENING PLAN:
    # - Make oversight_actions.licensed_business_qualifier_id NOT NULL (currently nullable for Phase Q.1 backfill)
    # - Change trigger to use licensed_business_qualifier_id FK directly instead of re-deriving from project
    # - This creates immutable audit trail: action locked to exact relationship at time of occurrence
    # - No retroactive invalidation risk, supports correction workflow
    op.execute("""
        CREATE OR REPLACE FUNCTION check_qualifier_cutoff()
        RETURNS TRIGGER AS $$
        DECLARE
            relationship RECORD;
        BEGIN
            -- FIX #1: Guard clause for missing project context
            IF NEW.project_id IS NULL THEN
                RETURN NEW;
            END IF;
            
            -- CRITICAL FIX #3: Use action_date, not CURRENT_DATE for historical correctness
            -- Get the qualifier relationship for this project + licensed business
            SELECT lbq.cutoff_date, lbq.end_date, p.licensed_business_id, p.qualifier_id
            INTO relationship
            FROM licensed_business_qualifiers lbq
            JOIN projects p ON p.licensed_business_id = lbq.licensed_business_id 
                           AND p.qualifier_id = lbq.qualifier_id
            WHERE p.id = NEW.project_id
              AND daterange(lbq.start_date, COALESCE(lbq.end_date, 'infinity'::date)) @> NEW.action_date::date
            ORDER BY lbq.start_date DESC
            LIMIT 1;
            
            -- FIX ISSUE #1: Check NULL first before accessing fields
            IF relationship IS NULL THEN
                RAISE EXCEPTION 'No active qualifier relationship found for this project on %', NEW.action_date::date;
            END IF;
            
            -- FIX #1: If project missing required context, warn but allow (for backfill scenario)
            IF relationship.licensed_business_id IS NULL OR relationship.qualifier_id IS NULL THEN
                RAISE WARNING 'Project % missing licensed_business_id or qualifier_id - oversight action created without full compliance check', NEW.project_id;
                RETURN NEW;
            END IF;
            
            -- If cutoff date exists and has passed, block the action
            IF relationship.cutoff_date IS NOT NULL AND NOW() > relationship.cutoff_date THEN
                RAISE EXCEPTION 'Qualifier cutoff date passed: No actions allowed after %', relationship.cutoff_date;
            END IF;
            
            -- If relationship has ended, block the action (use action_date for historical correctness)
            IF relationship.end_date IS NOT NULL AND NEW.action_date::date > relationship.end_date THEN
                RAISE EXCEPTION 'Qualifier relationship ended: No actions allowed after %', relationship.end_date;
            END IF;
            
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # 12. Create cutoff enforcement trigger on oversight_actions
    op.execute("""
        CREATE TRIGGER oversight_actions_cutoff_trigger
            BEFORE INSERT OR UPDATE ON oversight_actions
            FOR EACH ROW
            EXECUTE FUNCTION check_qualifier_cutoff();
    """)

    # 13. Create updated_at trigger function (MUST-FIX #2: scoped name to avoid collision)
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column_compliance()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # 14. Create updated_at triggers for new tables
    op.execute("""
        CREATE TRIGGER licensed_businesses_updated_at_trigger
            BEFORE UPDATE ON licensed_businesses
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column_compliance();
    """)
    op.execute("""
        CREATE TRIGGER qualifiers_updated_at_trigger
            BEFORE UPDATE ON qualifiers
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column_compliance();
    """)
    op.execute("""
        CREATE TRIGGER licensed_business_qualifiers_updated_at_trigger
            BEFORE UPDATE ON licensed_business_qualifiers
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column_compliance();
    """)
    op.execute("""
        CREATE TRIGGER oversight_actions_updated_at_trigger
            BEFORE UPDATE ON oversight_actions
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column_compliance();
    """)


def downgrade():
    # Drop triggers first
    op.execute("DROP TRIGGER IF EXISTS oversight_actions_cutoff_trigger ON oversight_actions;")
    op.execute("DROP TRIGGER IF EXISTS licensed_business_qualifiers_capacity_trigger ON licensed_business_qualifiers;")
    op.execute("DROP TRIGGER IF EXISTS compliance_justifications_justification_id_trigger ON compliance_justifications;")
    op.execute("DROP TRIGGER IF EXISTS oversight_actions_action_id_trigger ON oversight_actions;")
    op.execute("DROP TRIGGER IF EXISTS qualifiers_qualifier_id_trigger ON qualifiers;")
    op.execute("DROP TRIGGER IF EXISTS licensed_businesses_business_id_trigger ON licensed_businesses;")
    op.execute("DROP TRIGGER IF EXISTS oversight_actions_updated_at_trigger ON oversight_actions;")
    op.execute("DROP TRIGGER IF EXISTS licensed_business_qualifiers_updated_at_trigger ON licensed_business_qualifiers;")
    op.execute("DROP TRIGGER IF EXISTS qualifiers_updated_at_trigger ON qualifiers;")
    op.execute("DROP TRIGGER IF EXISTS licensed_businesses_updated_at_trigger ON licensed_businesses;")
    
    # Drop functions (FIX #3: Complete function cleanup)
    op.execute("DROP FUNCTION IF EXISTS check_qualifier_cutoff();")
    op.execute("DROP FUNCTION IF EXISTS check_qualifier_capacity();")
    op.execute("DROP FUNCTION IF EXISTS generate_business_id();")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column_compliance() CASCADE;")  # CASCADE drops dependent triggers
    
    # Drop sequences
    op.execute("DROP SEQUENCE IF EXISTS compliance_justifications_justification_id_seq;")
    op.execute("DROP SEQUENCE IF EXISTS oversight_actions_action_id_seq;")
    op.execute("DROP SEQUENCE IF EXISTS qualifiers_qualifier_id_seq;")
    op.execute("DROP SEQUENCE IF EXISTS licensed_businesses_business_id_seq;")
    
    # Remove columns from users table
    op.drop_index('ix_users_is_qualifier', 'users')
    op.drop_column('users', 'is_qualifier')  # max_licenses_allowed was already removed in upgrade
    
    # Remove columns from inspections table
    op.drop_constraint('fk_inspections_oversight_site_visit_id', 'inspections', type_='foreignkey')
    op.drop_index('ix_inspections_oversight_site_visit_id', 'inspections')
    op.drop_column('inspections', 'oversight_site_visit_id')
    op.drop_column('inspections', 'qualifier_attended')
    
    # Remove columns from site_visits table
    op.execute("ALTER TABLE site_visits DROP CONSTRAINT IF EXISTS ck_site_visits_oversight_type")
    op.drop_constraint('fk_site_visits_qualifier_id', 'site_visits', type_='foreignkey')
    op.drop_index('ix_site_visits_oversight_type', 'site_visits')
    op.drop_index('ix_site_visits_qualifier_id', 'site_visits')
    op.drop_column('site_visits', 'oversight_justification')
    op.drop_column('site_visits', 'qualifier_present')
    op.drop_column('site_visits', 'qualifier_id')
    op.drop_column('site_visits', 'oversight_type')
    
    # Remove columns from permits table
    op.execute("ALTER TABLE permits DROP CONSTRAINT IF EXISTS ck_permits_responsibility_role")
    op.drop_constraint('fk_permits_qualifier_id', 'permits', type_='foreignkey')
    op.drop_constraint('fk_permits_licensed_business_id', 'permits', type_='foreignkey')
    op.drop_index('ix_permits_qualifier_id', 'permits')
    op.drop_index('ix_permits_licensed_business_id', 'permits')
    op.drop_column('permits', 'responsibility_role')
    op.drop_column('permits', 'license_number_used')
    op.drop_column('permits', 'qualifier_id')
    op.drop_column('permits', 'licensed_business_id')
    
    # Remove columns from projects table
    op.execute("ALTER TABLE projects DROP CONSTRAINT IF EXISTS ck_projects_engagement_model")
    op.drop_constraint('fk_projects_qualifier_id', 'projects', type_='foreignkey')
    op.drop_constraint('fk_projects_licensed_business_id', 'projects', type_='foreignkey')
    op.drop_index('ix_projects_engagement_model', 'projects')
    op.drop_index('ix_projects_qualifier_id', 'projects')
    op.drop_index('ix_projects_licensed_business_id', 'projects')
    op.drop_column('projects', 'compliance_notes')
    op.drop_column('projects', 'oversight_required')
    op.drop_column('projects', 'engagement_model')
    op.drop_column('projects', 'qualifier_id')
    op.drop_column('projects', 'licensed_business_id')
    
    # Drop FKs from compliance_justifications
    op.drop_constraint('fk_compliance_justifications_created_by', 'compliance_justifications', type_='foreignkey')
    op.drop_constraint('fk_compliance_justifications_approved_by', 'compliance_justifications', type_='foreignkey')
    
    # Drop FKs from oversight_actions
    op.drop_constraint('fk_oversight_actions_created_by', 'oversight_actions', type_='foreignkey')
    op.drop_constraint('fk_oversight_actions_lbq_id', 'oversight_actions', type_='foreignkey')
    op.drop_constraint('fk_oversight_actions_licensed_business_id', 'oversight_actions', type_='foreignkey')
    op.drop_constraint('fk_oversight_actions_qualifier_id', 'oversight_actions', type_='foreignkey')
    op.drop_constraint('fk_oversight_actions_project_id', 'oversight_actions', type_='foreignkey')
    
    # Drop FK from licensed_businesses
    op.drop_constraint('fk_licensed_businesses_qualifying_user_id', 'licensed_businesses', type_='foreignkey')
    
    # Drop unique constraint on active LBQ pairs
    op.execute("DROP INDEX IF EXISTS uq_lbq_active_pair;")
    
    # Drop tables
    op.drop_table('compliance_justifications')
    op.drop_table('oversight_actions')
    op.drop_table('licensed_business_qualifiers')
    op.drop_table('qualifiers')
    op.drop_table('licensed_businesses')
