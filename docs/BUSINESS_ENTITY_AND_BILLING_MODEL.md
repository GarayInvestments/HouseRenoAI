# Business Entity & Billing Model

## Purpose

This document defines how **business entities, qualifiers, projects, and variable permit compliance fees** are modeled in the system. It is the authoritative source for licensing responsibility, billing logic, and reporting alignment. This document complements (but does not replace) the technical roadmap and implementation tracker.

---

## Core Principles

1. **Licensing reality first**: Projects must be explicitly tied to the licensed entity under which work is performed.
2. **Qualifiers are people, not companies**: A person can qualify multiple business entities.
3. **Fees are variable and per-project**: There is no global or fixed permit compliance fee.
4. **Billing is auditable**: Every fee must be traceable to a project, entity, and invoice.
5. **Additive, not destructive**: This model extends the current system without breaking existing data.

---

## Definitions

### Business Entity

A **Business Entity** represents a licensed organization or individual operating under a construction license.

Examples:

* House Renovators LLC
* 2States Carolinas
* Daniela Molina Rodriguez (individual license holder)

A business entity:

* Holds a license
* Has one primary qualifier
* Is responsible for permit filings and compliance

---

### Qualifier

A **Qualifier** is a licensed individual responsible for code compliance.

Key rules:

* A qualifier is always a **user/person**
* A qualifier may be associated with **multiple business entities**
* A business entity has **one active qualifier** at a time

Examples:

* Steve Garay qualifies:

  * House Renovators LLC
  * 2States Carolinas
* Daniela Molina Rodriguez qualifies her own projects

---

### Project

A **Project** represents a client engagement executed under a specific business entity and qualifier.

Each project:

* Belongs to **one client**
* Belongs to **one business entity**
* Is governed by **one qualifier** (via the entity)
* May have multiple billable fees

This explicitly answers:

> “Under whose license is this project being executed?”

---

## Data Model Overview

### Business Entities Table

```sql
business_entities (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  license_number TEXT,
  license_state TEXT,
  qualifier_user_id UUID REFERENCES users(id),
  qb_company_id TEXT,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ
)
```

---

### Projects Table (Additive Fields Only)

```sql
projects.business_entity_id UUID REFERENCES business_entities(id)
```

This field is **required for all new projects**.

---

### Project Fees (Billing Services)

Permit compliance is modeled as a **billable service**, not a project attribute.

```sql
project_fees (
  id UUID PRIMARY KEY,
  project_id UUID REFERENCES projects(id),
  fee_type TEXT, -- e.g. 'permit_compliance'
  description TEXT,
  amount NUMERIC(10,2),
  is_estimated BOOLEAN DEFAULT false,
  billed BOOLEAN DEFAULT false,
  qb_invoice_id TEXT,
  created_at TIMESTAMPTZ
)
```

#### Permit Compliance Fee Rules

* No fixed global price
* $3,000 is a **common baseline**, not a constant
* Amount is set **per project**
* Amount may vary based on:

  * Scope
  * Jurisdiction
  * Project type
  * Risk level

---

## Workflow Implications

### Project Creation Flow

1. Select Client
2. Select Business Entity (license holder)
3. System infers Qualifier from entity
4. Enter project details
5. Add Permit Compliance fee (default suggestion = $3,000, editable)

---

### Billing & QuickBooks

* Fees map cleanly to QuickBooks invoices
* Multiple fees may exist per project
* Business entity determines QB company context
* Reporting can group by:

  * Client
  * Business entity
  * Qualifier
  * Fee type

---

## Reporting & Compliance Use Cases

This model supports:

* Total permit fees by qualifier
* Revenue by business entity
* Compliance exposure per license
* Cross-entity project tracking
* Future joint ventures or white-labeling

---

## Non-Goals (Explicit)

This document does NOT:

* Define UI components
* Define permission rules in detail
* Replace the technical roadmap
* Mandate removal of existing fields

---

## Relationship to Other Docs

* **PROJECT_ROADMAP.md**: References this document for business logic
* **IMPLEMENTATION_TRACKER.md**: References this document when implementation work begins

This document is the **authoritative business and licensing model**.

---

## Status

Draft v1.0 – Approved for implementation planning
