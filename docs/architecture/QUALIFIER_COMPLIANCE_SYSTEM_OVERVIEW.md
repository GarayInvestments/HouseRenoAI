# Qualifier-Based Permit Compliance Platform

**High-Level System Intent and Direction**

**Status**: ✅ Authoritative Intent Document  
**Purpose**: Defines what the system is becoming, not just what it currently does.

---

## 1. Executive Summary

This platform is evolving from a general construction project management tool into a **Qualifier-centric permit compliance system** designed to operate within the regulatory expectations of the North Carolina Licensing Board for General Contractors (NCLBGC).

While the current implementation focuses on clients, projects, permits, inspections, and payments, the true business model centers on:

- **Licensed qualifiers**
- **Qualified business entities** (House Renovators and third-party companies)
- **Permit-level compliance responsibility**
- **Demonstrable oversight and involvement**
- **Fee-based compliance services** (not license rental)

This document clarifies that distinction and establishes the future direction of the system.

---

## 1.1. Locked Assumptions (Non-Negotiable Compliance Model)

**Status**: ✅ Confirmed December 14, 2025  
**Authority**: Regulatory Requirements + Business Policy

### Regulatory
- **Jurisdiction**: North Carolina only (NCLBGC)
- **Qualifier limit**: Max **2 Licensed Businesses per qualifier** (hard limit)
- **Enforcement**: **Hard block** when limit reached (not warning)
- **Qualifier exit**: **Hard cutoff timestamp** - no actions allowed after exit date

### Oversight
- **Valid oversight actions** (all count equally):
  - Site visits
  - Plan reviews
  - Permit application reviews
  - Client meetings
- **Minimum requirement**: System-enforced (blocks permit issuance if not met)
- **Historical data**: Manual backfill where known, flag as unverified otherwise

### Project Relationships
- **Project ↔ Licensed Business**: **1:1** (project belongs to exactly one Licensed Business)
- **Project ↔ Qualifier**: **1:1** (project assigned to one qualifier at creation)
- **Mid-project qualifier change**: **Not allowed** (prevents compliance ambiguity)

### Financial
- **Who pays qualifier**: Licensed Business (not client)
- **Fee model**: Hybrid
  - Flat fee (current)
  - Matrix-based by project cost (future)

### Governance
- **Non-compliance handling**: Actions allowed **only with logged justification**
- **Audit trail**: Full history required for all compliance-critical actions

**Why This Matters**: These assumptions enable the system to **prevent illegal states** rather than merely document them. Partial implementation is more dangerous than no implementation.

---

## 2. The Core Business Reality (What Actually Happens)

### Two Operating Scenarios

**Scenario A: House Renovators as GC**
- Homeowner is the client
- House Renovators LLC is the contracting entity
- Qualifier is internal
- Permit compliance is delivered directly

**Scenario B: Third-Party Contractor Qualification**
- Another company contracts with the client
- That company pulls permits under its own name
- A House Renovators–affiliated qualifier qualifies that company
- House Renovators provides permit compliance services, not construction labor

**In both cases, the platform's real value is ensuring:**
- The qualifier's legal responsibility is clear
- Permit compliance is properly supervised
- Oversight can be proven if challenged

---

## 3. Regulatory Lens (Why This Matters)

From the perspective of NCLBGC:

- **Licenses belong to businesses** (Licensed Businesses hold NCLBGC licenses)
- Each Licensed Business must have an **assigned Qualifier**
- A qualifier may serve **no more than 2 Licensed Businesses**
- The qualifier must exercise **real oversight** (not symbolic)
- **"License rental" is prohibited** (qualifier must have bona fide relationship)
- Documentation and consistency are critical

**This system must therefore answer, at any moment:**

> "Who was the qualifier, for which Licensed Business, on which permit, and what oversight occurred?"

**The system must also prevent:**

> "Can this qualifier take on another Licensed Business?" (blocks if at 2/2 capacity)  
> "Can this project proceed?" (blocks if Licensed Business has no qualifier or oversight minimum not met)

---

## 4. Current State of the Application (As Implemented Today)

### What the System Does Well
- Tracks clients, projects, permits, inspections
- Associates permits to projects
- Handles inspections, deficiencies, and documents
- Supports billing and QuickBooks integration
- Enforces authentication and auditability

### Implicit Assumptions in Current Design
- A single business entity is implied
- Qualifier responsibility is not explicitly modeled
- Permit compliance is assumed, not formalized
- Oversight activity is operational, not compliance-driven

**This is functional, but it does not yet reflect the true legal and business structure.**

---

## 5. Intended Future State (Target Model)

### System Identity Shift

**From:**  
A project-centric construction management system

**To:**  
A Qualifier-centric permit compliance platform that supports multiple business entities

### Core Concepts in the Target Model

At a high level, the system will explicitly model:

1. **Licensed Businesses** (entities holding NCLBGC licenses)
2. **Qualifiers** (individuals who qualify Licensed Businesses, max 2 at a time)
3. **Licensed Business ↔ Qualifier relationships** (time-bound, auditable assignments)
4. **Projects belong to Licensed Businesses** (1:1 relationship)
5. **Projects assigned to Qualifier at creation** (1:1 relationship, no mid-project changes)
6. **System-enforced capacity limits** (qualifier cannot serve more than 2 Licensed Businesses)
7. **Oversight requirements** (minimum oversight enforced before permit issuance)
8. **Compliance justifications** (logged when rules are overridden)
9. **Compliance services** as billable offerings

**Projects and permits are containers for compliance work performed under a Licensed Business's authority using assigned Qualifier(s) legal responsibility.**

### Enforcement Rules (Non-Negotiable)

The system must **block** (not warn) these illegal states:

- ❌ Creating a Licensed Business without an assigned Qualifier
- ❌ Assigning a Qualifier to more than 2 Licensed Businesses
- ❌ Creating a Project under a Licensed Business with no valid Qualifier
- ❌ Qualifier taking action after their cutoff/exit date
- ❌ Permits issued without minimum oversight requirement met
- ❌ Compliance rule overrides without logged justification

These are **hard failures at write-time**, not validation warnings.

---

## 6. Minimum Oversight Requirements (System-Enforced)

### Regulatory Basis

North Carolina licensing statutes and the North Carolina Building Code require that licensed contractors **personally superintend work and be present or meaningfully involved in required inspections**, but they do **not prescribe a numeric frequency** of oversight actions. As a result, this system defines a minimum oversight standard that reflects regulatory intent, inspection practice, and audit defensibility rather than arbitrary counts.

* * *

### 1. Oversight Unit of Enforcement

**Oversight is enforced at the permit level, not aggregated solely at the project level.**

- Each permit represents a distinct scope of regulated work.
- Each permit must independently demonstrate qualifier oversight.
- Projects with multiple permits must satisfy oversight requirements for **each permit**.

**Rationale**: Building, electrical, plumbing, and mechanical permits are inspected and evaluated independently by code officials.

* * *

### 2. Minimum Oversight Threshold

For each permit:

- **At least one documented oversight action is required**
- The action must be recorded **after permit issuance and before final permit completion or closure**

This is a **hard enforcement rule**. A permit may not be finalized or relied upon for compliance if this requirement is unmet.

* * *

### 3. Valid Oversight Actions

The following oversight actions are considered equally valid when properly documented:

- Site visit
- Permit application or revision review
- Plan review with documented findings or corrections
- Client or contractor meeting related to permitted work

Each action must include:

- Qualifier identifier
- Timestamp
- Oversight type
- Associated permit and licensed business

* * *

### 4. Plan Review Clarification

- **Plan review actions may count toward minimum oversight** only if they:

    - Occur after the qualifier–business relationship is active, and
    - Result in documented verification, correction, or compliance guidance

Plan review **does not replace field oversight**, but may satisfy the minimum requirement when field activity has not yet occurred.

* * *

### 5. Time Window Enforcement

Oversight actions are valid only if they occur:

- **On or after the permit issuance date**
- **Before permit finalization, expiration, or cancellation**
- **Before the qualifier's exit or cutoff timestamp**

Any oversight action recorded outside this window is invalid for compliance purposes.

* * *

### 6. Enforcement Outcomes

The system must block the following actions if minimum oversight is not satisfied:

- Permit finalization
- Project compliance completion
- Compliance reporting as "satisfied"
- Any downstream process that relies on permit compliance status

Overrides are permitted **only with a logged compliance justification**.

* * *

### 7. Audit Interpretation Rule

At audit time, the system must be able to answer:

> "For this permit, which qualifier exercised oversight, when did it occur, and under which licensed business's authority?"

If the system cannot answer this question definitively, the permit is considered **non-compliant** regardless of project completion status.

* * *

### Design Intent (Non-Negotiable)

This standard intentionally:

- Prevents symbolic or backfilled oversight from satisfying compliance
- Avoids arbitrary numeric requirements unsupported by statute
- Aligns with how inspectors and licensing boards evaluate supervision
- Prioritizes **provable oversight over activity volume**

* * *

### Qualifier Exit Impact on Active Projects

When a qualifier's relationship with a Licensed Business ends, the following rules apply immediately:

1. **All active projects under that Licensed Business enter a frozen compliance state**

    - No new permits may be created
    - No existing permits may advance status
    - No inspections may be scheduled or completed
    - No compliance milestones may be closed

2. **Projects may not be reassigned to a new qualifier**

    - Mid-project qualifier substitution is prohibited
    - This prevents retroactive ambiguity of legal responsibility

3. **Permitted continuation requires explicit compliance justification**

    - Any action taken on an affected project after qualifier exit requires:

        - A logged compliance justification
        - Identification of interim risk mitigation
        - Explicit acknowledgement of regulatory exposure

4. **System responsibility**

    - The system must surface affected projects immediately upon qualifier exit
    - Compliance reports must flag all frozen projects as "Qualifier Absent"

**Regulatory Rationale**

North Carolina licensing enforcement evaluates responsibility based on **who was legally accountable at the time work occurred**. Allowing silent continuation after qualifier exit creates indefensible gaps and license rental risk.

This policy ensures:

- Clear cutoff of responsibility
- No implied or retroactive supervision
- Audit-safe documentation of any exceptional continuation

**Why This Is the Right Line**

- It does **not** invent a new qualifier midstream
- It forces conscious, documented decisions
- It mirrors how boards treat suspended or expired license situations

---

## 7. What This Means for the Application and Copilot

### Copilot's Role Must Shift

**Copilot should not think primarily in terms of:**
- "projects and tasks"
- "CRUD for entities"
- "general construction workflows"

**Copilot must think in terms of:**
- **Enforcement over validation** (block illegal states at write-time)
- Compliance responsibility and legal limits
- Qualifier capacity constraints (max 2 Licensed Businesses)
- Qualifier cutoff dates (hard enforcement after exit)
- Oversight minimums (block permits if not met)
- Regulatory defensibility
- Proof over convenience

**When suggesting features, schemas, or workflows, Copilot should ask:**
- "Does this **prevent** illegal states or just document them?"
- "Can this be explained to a regulator?"
- "Does this enforce the 2-Licensed-Business limit per Qualifier?"
- "Does this respect qualifier cutoff dates?"
- "Does this require a compliance justification for overrides?"
- "Does this avoid license rental risk?"

---

## 8. Why This Is a Strategic Inflection Point

This reframing:

- ✅ Reduces regulatory risk
- ✅ Enables multi-company scaling
- ✅ Separates construction execution from compliance responsibility
- ✅ Aligns the software with how licensing boards actually think
- ✅ Turns compliance into a structured, defensible service offering

**This is not scope creep.**  
**This is scope correction.**

---

## 9. Guardrails Going Forward

1. **Compliance intent** takes precedence over convenience
2. **Qualifier clarity** beats feature velocity
3. **Data structure** must reflect legal reality
4. **Documentation** must support defensibility
5. **"Would this survive an audit?"** is a valid design question

---

## 10. One-Sentence System Definition (Canonical)

> **This platform exists to manage qualifier-based permit compliance across multiple Licensed Businesses while maintaining clear regulatory accountability, defensible oversight records, and enforced legal limits.**

---

## 11. Relationship to Existing Documentation

This document:

- ✅ Frames `BUSINESS_ENTITY_AND_BILLING_MODEL.md`
- ✅ Guides future schema changes
- ✅ Informs Copilot behavior
- ✅ Does not replace implementation details
- ✅ Precedes technical design

---

## Referenced By

- `docs/business/BUSINESS_ENTITY_AND_BILLING_MODEL.md` - Detailed business model
- `.github/copilot-instructions.md` - AI assistant behavior guidelines
- Future architecture decisions requiring compliance perspective

---

**Last Updated**: December 14, 2025  
**Authority Level**: Strategic Intent (supersedes convenience-driven decisions)
