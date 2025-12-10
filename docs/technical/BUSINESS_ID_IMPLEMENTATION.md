# Business ID Implementation - Technical Design

**Status:** 🎯 Ready to Implement  
**Date:** December 10, 2025  
**Approach:** PostgreSQL sequences + atomic generation + human-friendly format

---

## Overview

Add immutable, human-friendly business IDs to all core entities alongside existing technical primary keys. These IDs are designed for external communication, UI display, invoicing, and customer-facing documents.

**Examples:**
- Client: `CL-00001`, `CL-00002`
- Project: `PRJ-00001`, `PRJ-00002`
- Permit: `PRM-00001`, `PRM-00002`
- Inspection: `INS-00001`, `INS-00002`
- Invoice: `INV-2025-00001`, `INV-2025-00002`
- Change Order: `CO-PRJ-00001-001`, `CO-PRJ-00001-002`

---

## Design Decisions

### ✅ **What We're Doing**

1. **PostgreSQL Sequences** - Database-managed, atomic counter
2. **Separate business_id column** - Keep existing PKs unchanged
3. **Format: PREFIX-NUMBER** - Easy to read, type, and communicate
4. **Generated at INSERT** - Atomic, no race conditions
5. **Immutable** - Never changes once assigned
6. **Indexed & Unique** - Fast lookups, guaranteed uniqueness
7. **Backfill migration** - Safe migration for existing records

### ❌ **What We're NOT Doing**

- ❌ Replacing existing PKs (client_id, project_id) - too risky
- ❌ UUIDs - not human-friendly
- ❌ Application-level generation - race conditions
- ❌ Cryptographic IDs - overkill for this use case
- ❌ Hierarchical complex schemes - keep it simple

---

## Schema Changes

### Database Sequences

```sql
-- Create sequences for each entity type
CREATE SEQUENCE client_business_id_seq START 1;
CREATE SEQUENCE project_business_id_seq START 1;
CREATE SEQUENCE permit_business_id_seq START 1;
CREATE SEQUENCE inspection_business_id_seq START 1;
CREATE SEQUENCE payment_business_id_seq START 1;
CREATE SEQUENCE invoice_business_id_seq START 1;
CREATE SEQUENCE change_order_business_id_seq START 1;
```

### Table Columns

```sql
-- Add business_id to all core tables
ALTER TABLE clients 
  ADD COLUMN business_id VARCHAR(20) UNIQUE;

ALTER TABLE projects 
  ADD COLUMN business_id VARCHAR(20) UNIQUE;

ALTER TABLE permits 
  ADD COLUMN business_id VARCHAR(20) UNIQUE;

ALTER TABLE inspections 
  ADD COLUMN business_id VARCHAR(20) UNIQUE;

ALTER TABLE payments 
  ADD COLUMN business_id VARCHAR(20) UNIQUE;

-- Create indexes for fast lookups
CREATE UNIQUE INDEX idx_clients_business_id ON clients(business_id);
CREATE UNIQUE INDEX idx_projects_business_id ON projects(business_id);
CREATE UNIQUE INDEX idx_permits_business_id ON permits(business_id);
CREATE UNIQUE INDEX idx_inspections_business_id ON inspections(business_id);
CREATE UNIQUE INDEX idx_payments_business_id ON payments(business_id);
```

### Generation Functions

```sql
-- Function to generate client business ID
CREATE OR REPLACE FUNCTION generate_client_business_id()
RETURNS VARCHAR(20) AS $$
BEGIN
  RETURN 'CL-' || LPAD(nextval('client_business_id_seq')::TEXT, 5, '0');
END;
$$ LANGUAGE plpgsql;

-- Function to generate project business ID
CREATE OR REPLACE FUNCTION generate_project_business_id()
RETURNS VARCHAR(20) AS $$
BEGIN
  RETURN 'PRJ-' || LPAD(nextval('project_business_id_seq')::TEXT, 5, '0');
END;
$$ LANGUAGE plpgsql;

-- Function to generate permit business ID
CREATE OR REPLACE FUNCTION generate_permit_business_id()
RETURNS VARCHAR(20) AS $$
BEGIN
  RETURN 'PRM-' || LPAD(nextval('permit_business_id_seq')::TEXT, 5, '0');
END;
$$ LANGUAGE plpgsql;

-- Function to generate inspection business ID
CREATE OR REPLACE FUNCTION generate_inspection_business_id()
RETURNS VARCHAR(20) AS $$
BEGIN
  RETURN 'INS-' || LPAD(nextval('inspection_business_id_seq')::TEXT, 5, '0');
END;
$$ LANGUAGE plpgsql;

-- Function to generate payment business ID
CREATE OR REPLACE FUNCTION generate_payment_business_id()
RETURNS VARCHAR(20) AS $$
BEGIN
  RETURN 'PAY-' || LPAD(nextval('payment_business_id_seq')::TEXT, 5, '0');
END;
$$ LANGUAGE plpgsql;

-- Function to generate invoice business ID (includes year)
CREATE OR REPLACE FUNCTION generate_invoice_business_id()
RETURNS VARCHAR(20) AS $$
BEGIN
  RETURN 'INV-' || EXTRACT(YEAR FROM CURRENT_DATE)::TEXT || '-' || 
         LPAD(nextval('invoice_business_id_seq')::TEXT, 5, '0');
END;
$$ LANGUAGE plpgsql;
```

### Triggers for Auto-Generation

```sql
-- Trigger to auto-generate client business_id
CREATE OR REPLACE FUNCTION set_client_business_id()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.business_id IS NULL THEN
    NEW.business_id := generate_client_business_id();
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_set_client_business_id
  BEFORE INSERT ON clients
  FOR EACH ROW
  EXECUTE FUNCTION set_client_business_id();

-- Trigger for projects
CREATE OR REPLACE FUNCTION set_project_business_id()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.business_id IS NULL THEN
    NEW.business_id := generate_project_business_id();
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_set_project_business_id
  BEFORE INSERT ON projects
  FOR EACH ROW
  EXECUTE FUNCTION set_project_business_id();

-- Trigger for permits
CREATE OR REPLACE FUNCTION set_permit_business_id()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.business_id IS NULL THEN
    NEW.business_id := generate_permit_business_id();
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_set_permit_business_id
  BEFORE INSERT ON permits
  FOR EACH ROW
  EXECUTE FUNCTION set_permit_business_id();

-- Trigger for inspections
CREATE OR REPLACE FUNCTION set_inspection_business_id()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.business_id IS NULL THEN
    NEW.business_id := generate_inspection_business_id();
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_set_inspection_business_id
  BEFORE INSERT ON inspections
  FOR EACH ROW
  EXECUTE FUNCTION set_inspection_business_id();

-- Trigger for payments
CREATE OR REPLACE FUNCTION set_payment_business_id()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.business_id IS NULL THEN
    NEW.business_id := generate_payment_business_id();
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_set_payment_business_id
  BEFORE INSERT ON payments
  FOR EACH ROW
  EXECUTE FUNCTION set_payment_business_id();
```

---

## Alembic Migration

```python
# alembic/versions/003_add_business_ids.py
"""Add business IDs to core entities

Revision ID: 003
Revises: 002
Create Date: 2025-12-10
"""

from alembic import op
import sqlalchemy as sa

revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create sequences
    op.execute("CREATE SEQUENCE client_business_id_seq START 1;")
    op.execute("CREATE SEQUENCE project_business_id_seq START 1;")
    op.execute("CREATE SEQUENCE permit_business_id_seq START 1;")
    op.execute("CREATE SEQUENCE inspection_business_id_seq START 1;")
    op.execute("CREATE SEQUENCE payment_business_id_seq START 1;")
    op.execute("CREATE SEQUENCE invoice_business_id_seq START 1;")
    op.execute("CREATE SEQUENCE change_order_business_id_seq START 1;")
    
    # Add columns (nullable initially for backfill)
    op.add_column('clients', sa.Column('business_id', sa.String(20), nullable=True))
    op.add_column('projects', sa.Column('business_id', sa.String(20), nullable=True))
    op.add_column('permits', sa.Column('business_id', sa.String(20), nullable=True))
    op.add_column('inspections', sa.Column('business_id', sa.String(20), nullable=True))
    op.add_column('payments', sa.Column('business_id', sa.String(20), nullable=True))
    
    # Create generation functions
    op.execute("""
        CREATE OR REPLACE FUNCTION generate_client_business_id()
        RETURNS VARCHAR(20) AS $$
        BEGIN
          RETURN 'CL-' || LPAD(nextval('client_business_id_seq')::TEXT, 5, '0');
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    op.execute("""
        CREATE OR REPLACE FUNCTION generate_project_business_id()
        RETURNS VARCHAR(20) AS $$
        BEGIN
          RETURN 'PRJ-' || LPAD(nextval('project_business_id_seq')::TEXT, 5, '0');
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    op.execute("""
        CREATE OR REPLACE FUNCTION generate_permit_business_id()
        RETURNS VARCHAR(20) AS $$
        BEGIN
          RETURN 'PRM-' || LPAD(nextval('permit_business_id_seq')::TEXT, 5, '0');
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    op.execute("""
        CREATE OR REPLACE FUNCTION generate_inspection_business_id()
        RETURNS VARCHAR(20) AS $$
        BEGIN
          RETURN 'INS-' || LPAD(nextval('inspection_business_id_seq')::TEXT, 5, '0');
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    op.execute("""
        CREATE OR REPLACE FUNCTION generate_payment_business_id()
        RETURNS VARCHAR(20) AS $$
        BEGIN
          RETURN 'PAY-' || LPAD(nextval('payment_business_id_seq')::TEXT, 5, '0');
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Create triggers
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
    
    op.execute("""
        CREATE TRIGGER trigger_set_client_business_id
          BEFORE INSERT ON clients
          FOR EACH ROW
          EXECUTE FUNCTION set_client_business_id();
    """)
    
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
    
    op.execute("""
        CREATE TRIGGER trigger_set_project_business_id
          BEFORE INSERT ON projects
          FOR EACH ROW
          EXECUTE FUNCTION set_project_business_id();
    """)
    
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
    
    op.execute("""
        CREATE TRIGGER trigger_set_permit_business_id
          BEFORE INSERT ON permits
          FOR EACH ROW
          EXECUTE FUNCTION set_permit_business_id();
    """)
    
    op.execute("""
        CREATE OR REPLACE FUNCTION set_inspection_business_id()
        RETURNS TRIGGER AS $$
        BEGIN
          IF NEW.business_id IS NULL THEN
            NEW.business_id := generate_inspection_business_id();
          END IF;
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    op.execute("""
        CREATE TRIGGER trigger_set_inspection_business_id
          BEFORE INSERT ON inspections
          FOR EACH ROW
          EXECUTE FUNCTION set_inspection_business_id();
    """)
    
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
    
    op.execute("""
        CREATE TRIGGER trigger_set_payment_business_id
          BEFORE INSERT ON payments
          FOR EACH ROW
          EXECUTE FUNCTION set_payment_business_id();
    """)
    
    # Create indexes
    op.create_index('idx_clients_business_id', 'clients', ['business_id'], unique=True)
    op.create_index('idx_projects_business_id', 'projects', ['business_id'], unique=True)
    op.create_index('idx_permits_business_id', 'permits', ['business_id'], unique=True)
    op.create_index('idx_inspections_business_id', 'inspections', ['business_id'], unique=True)
    op.create_index('idx_payments_business_id', 'payments', ['business_id'], unique=True)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_clients_business_id', table_name='clients')
    op.drop_index('idx_projects_business_id', table_name='projects')
    op.drop_index('idx_permits_business_id', table_name='permits')
    op.drop_index('idx_inspections_business_id', table_name='inspections')
    op.drop_index('idx_payments_business_id', table_name='payments')
    
    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS trigger_set_client_business_id ON clients;")
    op.execute("DROP TRIGGER IF EXISTS trigger_set_project_business_id ON projects;")
    op.execute("DROP TRIGGER IF EXISTS trigger_set_permit_business_id ON permits;")
    op.execute("DROP TRIGGER IF EXISTS trigger_set_inspection_business_id ON inspections;")
    op.execute("DROP TRIGGER IF EXISTS trigger_set_payment_business_id ON payments;")
    
    # Drop functions
    op.execute("DROP FUNCTION IF EXISTS set_client_business_id();")
    op.execute("DROP FUNCTION IF EXISTS set_project_business_id();")
    op.execute("DROP FUNCTION IF EXISTS set_permit_business_id();")
    op.execute("DROP FUNCTION IF EXISTS set_inspection_business_id();")
    op.execute("DROP FUNCTION IF EXISTS set_payment_business_id();")
    op.execute("DROP FUNCTION IF EXISTS generate_client_business_id();")
    op.execute("DROP FUNCTION IF EXISTS generate_project_business_id();")
    op.execute("DROP FUNCTION IF EXISTS generate_permit_business_id();")
    op.execute("DROP FUNCTION IF EXISTS generate_inspection_business_id();")
    op.execute("DROP FUNCTION IF EXISTS generate_payment_business_id();")
    
    # Drop columns
    op.drop_column('clients', 'business_id')
    op.drop_column('projects', 'business_id')
    op.drop_column('permits', 'business_id')
    op.drop_column('inspections', 'business_id')
    op.drop_column('payments', 'business_id')
    
    # Drop sequences
    op.execute("DROP SEQUENCE IF EXISTS client_business_id_seq;")
    op.execute("DROP SEQUENCE IF EXISTS project_business_id_seq;")
    op.execute("DROP SEQUENCE IF EXISTS permit_business_id_seq;")
    op.execute("DROP SEQUENCE IF EXISTS inspection_business_id_seq;")
    op.execute("DROP SEQUENCE IF EXISTS payment_business_id_seq;")
    op.execute("DROP SEQUENCE IF EXISTS invoice_business_id_seq;")
    op.execute("DROP SEQUENCE IF EXISTS change_order_business_id_seq;")
```

---

## Backfill Script

```python
# scripts/backfill_business_ids.py
"""
Safely backfill business_id for existing records.

Usage:
  python scripts/backfill_business_ids.py --dry-run  # Preview changes
  python scripts/backfill_business_ids.py            # Apply changes
  python scripts/backfill_business_ids.py --entity clients  # Specific entity
"""

import asyncio
import argparse
from datetime import datetime
from sqlalchemy import select, update, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db_session
from app.db.models import Client, Project, Permit, Inspection, Payment

class BusinessIDBackfill:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.stats = {
            'clients': {'total': 0, 'backfilled': 0, 'skipped': 0},
            'projects': {'total': 0, 'backfilled': 0, 'skipped': 0},
            'permits': {'total': 0, 'backfilled': 0, 'skipped': 0},
            'inspections': {'total': 0, 'backfilled': 0, 'skipped': 0},
            'payments': {'total': 0, 'backfilled': 0, 'skipped': 0},
        }
    
    async def backfill_clients(self, session: AsyncSession):
        """Backfill client business IDs."""
        print("\n=== Backfilling Clients ===")
        
        # Get clients without business_id
        result = await session.execute(
            select(Client).where(Client.business_id.is_(None))
        )
        clients = result.scalars().all()
        
        self.stats['clients']['total'] = len(clients)
        
        for client in clients:
            # Generate business_id using database function
            if not self.dry_run:
                result = await session.execute(text("SELECT generate_client_business_id()"))
                business_id = result.scalar()
                client.business_id = business_id
                self.stats['clients']['backfilled'] += 1
                print(f"  ✓ {client.client_id} → {business_id}")
            else:
                print(f"  [DRY RUN] Would assign business_id to {client.client_id}")
                self.stats['clients']['backfilled'] += 1
        
        if not self.dry_run:
            await session.commit()
    
    async def backfill_projects(self, session: AsyncSession):
        """Backfill project business IDs."""
        print("\n=== Backfilling Projects ===")
        
        result = await session.execute(
            select(Project).where(Project.business_id.is_(None))
        )
        projects = result.scalars().all()
        
        self.stats['projects']['total'] = len(projects)
        
        for project in projects:
            if not self.dry_run:
                result = await session.execute(text("SELECT generate_project_business_id()"))
                business_id = result.scalar()
                project.business_id = business_id
                self.stats['projects']['backfilled'] += 1
                print(f"  ✓ {project.project_id} → {business_id}")
            else:
                print(f"  [DRY RUN] Would assign business_id to {project.project_id}")
                self.stats['projects']['backfilled'] += 1
        
        if not self.dry_run:
            await session.commit()
    
    async def backfill_permits(self, session: AsyncSession):
        """Backfill permit business IDs."""
        print("\n=== Backfilling Permits ===")
        
        result = await session.execute(
            select(Permit).where(Permit.business_id.is_(None))
        )
        permits = result.scalars().all()
        
        self.stats['permits']['total'] = len(permits)
        
        for permit in permits:
            if not self.dry_run:
                result = await session.execute(text("SELECT generate_permit_business_id()"))
                business_id = result.scalar()
                permit.business_id = business_id
                self.stats['permits']['backfilled'] += 1
                print(f"  ✓ {permit.permit_id} → {business_id}")
            else:
                print(f"  [DRY RUN] Would assign business_id to {permit.permit_id}")
                self.stats['permits']['backfilled'] += 1
        
        if not self.dry_run:
            await session.commit()
    
    async def backfill_inspections(self, session: AsyncSession):
        """Backfill inspection business IDs."""
        print("\n=== Backfilling Inspections ===")
        
        result = await session.execute(
            select(Inspection).where(Inspection.business_id.is_(None))
        )
        inspections = result.scalars().all()
        
        self.stats['inspections']['total'] = len(inspections)
        
        for inspection in inspections:
            if not self.dry_run:
                result = await session.execute(text("SELECT generate_inspection_business_id()"))
                business_id = result.scalar()
                inspection.business_id = business_id
                self.stats['inspections']['backfilled'] += 1
                print(f"  ✓ {inspection.inspection_id} → {business_id}")
            else:
                print(f"  [DRY RUN] Would assign business_id to {inspection.inspection_id}")
                self.stats['inspections']['backfilled'] += 1
        
        if not self.dry_run:
            await session.commit()
    
    async def backfill_payments(self, session: AsyncSession):
        """Backfill payment business IDs."""
        print("\n=== Backfilling Payments ===")
        
        result = await session.execute(
            select(Payment).where(Payment.business_id.is_(None))
        )
        payments = result.scalars().all()
        
        self.stats['payments']['total'] = len(payments)
        
        for payment in payments:
            if not self.dry_run:
                result = await session.execute(text("SELECT generate_payment_business_id()"))
                business_id = result.scalar()
                payment.business_id = business_id
                self.stats['payments']['backfilled'] += 1
                print(f"  ✓ {payment.payment_id} → {business_id}")
            else:
                print(f"  [DRY RUN] Would assign business_id to {payment.payment_id}")
                self.stats['payments']['backfilled'] += 1
        
        if not self.dry_run:
            await session.commit()
    
    async def run(self, entity: str = None):
        """Run backfill for all or specific entity."""
        async with get_db_session() as session:
            if entity == 'clients' or entity is None:
                await self.backfill_clients(session)
            
            if entity == 'projects' or entity is None:
                await self.backfill_projects(session)
            
            if entity == 'permits' or entity is None:
                await self.backfill_permits(session)
            
            if entity == 'inspections' or entity is None:
                await self.backfill_inspections(session)
            
            if entity == 'payments' or entity is None:
                await self.backfill_payments(session)
        
        self.print_summary()
    
    def print_summary(self):
        """Print backfill summary."""
        print("\n" + "="*80)
        print("BACKFILL SUMMARY")
        print("="*80)
        
        if self.dry_run:
            print("MODE: DRY RUN (no changes made)")
        else:
            print("MODE: LIVE (changes committed)")
        
        print("\n")
        
        for entity, stats in self.stats.items():
            if stats['total'] > 0:
                print(f"{entity.upper()}:")
                print(f"  Total without business_id: {stats['total']}")
                print(f"  Backfilled:                {stats['backfilled']}")
                print(f"  Skipped:                   {stats['skipped']}")
                success_rate = (stats['backfilled'] / stats['total'] * 100) if stats['total'] > 0 else 0
                print(f"  Success Rate:              {success_rate:.1f}%")
                print()


async def main():
    parser = argparse.ArgumentParser(description='Backfill business IDs for existing records')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without committing')
    parser.add_argument('--entity', choices=['clients', 'projects', 'permits', 'inspections', 'payments'],
                       help='Backfill specific entity only')
    
    args = parser.parse_args()
    
    backfill = BusinessIDBackfill(dry_run=args.dry_run)
    await backfill.run(entity=args.entity)


if __name__ == '__main__':
    asyncio.run(main())
```

---

## Model Updates

```python
# app/db/models.py - Add business_id to models

class Client(Base):
    __tablename__ = "clients"
    
    # Existing PK
    client_id: Mapped[str] = mapped_column(String(16), primary_key=True)
    
    # NEW: Business ID (human-friendly)
    business_id: Mapped[str | None] = mapped_column(String(20), unique=True, index=True)
    
    # ... rest of fields


class Project(Base):
    __tablename__ = "projects"
    
    project_id: Mapped[str] = mapped_column(String(16), primary_key=True)
    
    # NEW: Business ID
    business_id: Mapped[str | None] = mapped_column(String(20), unique=True, index=True)
    
    # ... rest of fields


class Permit(Base):
    __tablename__ = "permits"
    
    permit_id: Mapped[str] = mapped_column(String(16), primary_key=True)
    
    # NEW: Business ID
    business_id: Mapped[str | None] = mapped_column(String(20), unique=True, index=True)
    
    # ... rest of fields


class Inspection(Base):
    __tablename__ = "inspections"
    
    inspection_id: Mapped[str] = mapped_column(String(16), primary_key=True)
    
    # NEW: Business ID
    business_id: Mapped[str | None] = mapped_column(String(20), unique=True, index=True)
    
    # ... rest of fields


class Payment(Base):
    __tablename__ = "payments"
    
    payment_id: Mapped[str] = mapped_column(String(16), primary_key=True)
    
    # NEW: Business ID
    business_id: Mapped[str | None] = mapped_column(String(20), unique=True, index=True)
    
    # ... rest of fields
```

---

## API Changes

### DBService Methods

```python
# app/services/db_service.py - Add lookup by business_id

class DBService:
    
    async def get_client_by_business_id(self, business_id: str) -> dict | None:
        """Get client by business ID (e.g., 'CL-00001')."""
        cache_key = f"client_biz_{business_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        async with self.get_session() as session:
            result = await session.execute(
                select(Client).where(Client.business_id == business_id)
            )
            client = result.scalar_one_or_none()
        
        if client:
            data = self._client_to_dict(client)
            self._cache[cache_key] = data
            return data
        return None
    
    async def get_project_by_business_id(self, business_id: str) -> dict | None:
        """Get project by business ID (e.g., 'PRJ-00001')."""
        cache_key = f"project_biz_{business_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        async with self.get_session() as session:
            result = await session.execute(
                select(Project).where(Project.business_id == business_id)
            )
            project = result.scalar_one_or_none()
        
        if project:
            data = self._project_to_dict(project)
            self._cache[cache_key] = data
            return data
        return None
    
    # Similar for permits, inspections, payments...
```

### API Endpoints

```python
# app/routes/clients.py - Add business_id lookup

@router.get("/by-business-id/{business_id}")
async def get_client_by_business_id(business_id: str):
    """Get client by business ID (e.g., CL-00001)."""
    client = await db_service.get_client_by_business_id(business_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


# app/routes/projects.py - Add business_id lookup

@router.get("/by-business-id/{business_id}")
async def get_project_by_business_id(business_id: str):
    """Get project by business ID (e.g., PRJ-00001)."""
    project = await db_service.get_project_by_business_id(business_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
```

### Response Changes

```python
# All existing endpoints now return business_id

GET /v1/clients
Response:
[
  {
    "Client ID": "12345678",      # Technical PK (unchanged)
    "business_id": "CL-00001",    # NEW: Human-friendly ID
    "Full Name": "John Doe",
    ...
  }
]

GET /v1/projects/P-001
Response:
{
  "Project ID": "P-001",
  "business_id": "PRJ-00042",     # NEW
  "Client ID": "12345678",
  "Project Name": "Kitchen Remodel",
  ...
}
```

---

## Tests

```python
# tests/test_business_ids.py

import pytest
import asyncio
from sqlalchemy import select
from app.db.models import Client, Project, Permit
from app.services.db_service import db_service

class TestBusinessIDGeneration:
    
    @pytest.mark.asyncio
    async def test_client_business_id_auto_generated(self):
        """Test that business_id is auto-generated on insert."""
        client = await db_service.create_client(
            full_name="Test Client",
            email="test@example.com"
        )
        
        assert client['business_id'] is not None
        assert client['business_id'].startswith('CL-')
        assert len(client['business_id']) == 8  # CL-00001
    
    @pytest.mark.asyncio
    async def test_business_id_uniqueness(self):
        """Test that business_ids are unique."""
        client1 = await db_service.create_client(full_name="Client 1", email="c1@test.com")
        client2 = await db_service.create_client(full_name="Client 2", email="c2@test.com")
        
        assert client1['business_id'] != client2['business_id']
    
    @pytest.mark.asyncio
    async def test_business_id_sequential(self):
        """Test that business_ids increment sequentially."""
        client1 = await db_service.create_client(full_name="Client 1", email="c1@test.com")
        client2 = await db_service.create_client(full_name="Client 2", email="c2@test.com")
        
        # Extract numbers
        num1 = int(client1['business_id'].split('-')[1])
        num2 = int(client2['business_id'].split('-')[1])
        
        assert num2 == num1 + 1
    
    @pytest.mark.asyncio
    async def test_concurrent_business_id_generation(self):
        """Test that concurrent inserts get unique business_ids (no race conditions)."""
        tasks = [
            db_service.create_client(full_name=f"Client {i}", email=f"c{i}@test.com")
            for i in range(10)
        ]
        
        clients = await asyncio.gather(*tasks)
        business_ids = [c['business_id'] for c in clients]
        
        # All should be unique
        assert len(business_ids) == len(set(business_ids))
    
    @pytest.mark.asyncio
    async def test_lookup_by_business_id(self):
        """Test finding records by business_id."""
        client = await db_service.create_client(full_name="John Doe", email="john@test.com")
        business_id = client['business_id']
        
        # Lookup by business_id
        found = await db_service.get_client_by_business_id(business_id)
        
        assert found is not None
        assert found['business_id'] == business_id
        assert found['Full Name'] == "John Doe"
    
    @pytest.mark.asyncio
    async def test_business_id_immutable(self):
        """Test that business_id cannot be changed after creation."""
        client = await db_service.create_client(full_name="Test", email="test@test.com")
        original_business_id = client['business_id']
        
        # Try to update (should not change business_id)
        await db_service.update_client(
            client['Client ID'],
            full_name="Updated Name"
        )
        
        # Verify business_id unchanged
        updated = await db_service.get_client(client['Client ID'])
        assert updated['business_id'] == original_business_id


class TestBackfillMigration:
    
    @pytest.mark.asyncio
    async def test_backfill_dry_run_safe(self):
        """Test that dry-run doesn't modify database."""
        # Create clients without business_id (simulate old records)
        # ... test implementation
        pass
    
    @pytest.mark.asyncio
    async def test_backfill_idempotent(self):
        """Test that running backfill multiple times is safe."""
        # Run backfill twice, verify no duplicates or errors
        pass
    
    @pytest.mark.asyncio
    async def test_backfill_handles_existing_ids(self):
        """Test that backfill skips records that already have business_ids."""
        # Create mix of records with and without business_ids
        # Run backfill
        # Verify only null records were updated
        pass


class TestAPIEndpoints:
    
    @pytest.mark.asyncio
    async def test_get_client_by_business_id_endpoint(self, client):
        """Test GET /v1/clients/by-business-id/{business_id}."""
        # Create client
        create_response = await client.post('/v1/clients', json={
            'full_name': 'Test Client',
            'email': 'test@example.com'
        })
        business_id = create_response.json()['business_id']
        
        # Lookup by business_id
        response = await client.get(f'/v1/clients/by-business-id/{business_id}')
        
        assert response.status_code == 200
        assert response.json()['business_id'] == business_id
    
    @pytest.mark.asyncio
    async def test_business_id_included_in_list_responses(self, client):
        """Test that business_id is included in list endpoints."""
        response = await client.get('/v1/clients')
        
        assert response.status_code == 200
        clients = response.json()
        
        for client_data in clients:
            assert 'business_id' in client_data
            if client_data['business_id']:
                assert client_data['business_id'].startswith('CL-')
```

---

## Implementation Checklist

### Phase 1: Database (2 hours)
- [ ] Create Alembic migration `003_add_business_ids.py`
- [ ] Add sequences for each entity
- [ ] Add generation functions
- [ ] Add trigger functions
- [ ] Add columns with indexes
- [ ] Test migration up/down locally

### Phase 2: Models (30 minutes)
- [ ] Add `business_id` field to all models
- [ ] Update `__table_args__` with unique constraints
- [ ] Verify models load correctly

### Phase 3: Service Layer (2 hours)
- [ ] Add `get_*_by_business_id()` methods
- [ ] Update `_*_to_dict()` to include business_id
- [ ] Add caching for business_id lookups
- [ ] Test service methods

### Phase 4: API Routes (1 hour)
- [ ] Add `/by-business-id/{business_id}` endpoints
- [ ] Update existing responses to include business_id
- [ ] Test endpoints manually

### Phase 5: Backfill Script (2 hours)
- [ ] Create `scripts/backfill_business_ids.py`
- [ ] Add dry-run mode
- [ ] Add entity-specific backfill
- [ ] Add progress reporting
- [ ] Test backfill locally

### Phase 6: Testing (3 hours)
- [ ] Write generation tests
- [ ] Write uniqueness tests
- [ ] Write concurrency tests
- [ ] Write lookup tests
- [ ] Write backfill tests
- [ ] Write API tests
- [ ] All tests pass

### Phase 7: Documentation (1 hour)
- [ ] Update API docs with business_id examples
- [ ] Document backfill procedure
- [ ] Add troubleshooting guide

**Total Time:** ~11 hours (1.5 days)

---

## Usage Examples

### Creating New Records

```python
# Automatic generation
client = await db_service.create_client(
    full_name="Jane Smith",
    email="jane@example.com"
)
# Returns: { "Client ID": "abcd1234", "business_id": "CL-00123", ... }
```

### Looking Up Records

```python
# By technical PK (unchanged)
client = await db_service.get_client("abcd1234")

# By business ID (NEW)
client = await db_service.get_client_by_business_id("CL-00123")
```

### API Calls

```bash
# Create client (auto-generates business_id)
curl -X POST http://localhost:8000/v1/clients \
  -H "Content-Type: application/json" \
  -d '{"full_name":"John Doe","email":"john@example.com"}'

# Response:
{
  "Client ID": "abcd1234",
  "business_id": "CL-00456",
  "Full Name": "John Doe",
  ...
}

# Lookup by business_id
curl http://localhost:8000/v1/clients/by-business-id/CL-00456
```

### Backfilling Existing Data

```bash
# Dry-run first (preview changes)
python scripts/backfill_business_ids.py --dry-run

# Backfill specific entity
python scripts/backfill_business_ids.py --entity clients

# Backfill all entities
python scripts/backfill_business_ids.py
```

---

## Benefits

1. **Human-Friendly** - Easy to read, type, communicate over phone
2. **Immutable** - Never changes, safe for external references
3. **Sequential** - Numbers increment predictably
4. **Atomic** - Database-managed, no race conditions
5. **Performant** - Indexed for fast lookups
6. **Backwards Compatible** - Existing PKs unchanged
7. **Safe Migration** - Dry-run mode, idempotent backfill

---

## Next Steps

1. Review this design
2. Run Phase 1 (create migration)
3. Test locally with `alembic upgrade head`
4. Proceed with Phases 2-7
5. Deploy to production

**Ready to implement?**
