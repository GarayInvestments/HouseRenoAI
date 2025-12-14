# 📘 Documentation Governance & Triage Policy

**Location**: `/docs/README.md`  
**Status**: Canonical  
**Audience**: Humans + Copilot  
**Last Updated**: December 13, 2025

---

## 1. Purpose

This document defines:

- The official `/docs` folder structure
- The rules for adding, moving, merging, or deleting documentation
- The classification system used to triage existing docs
- **Document lifecycle and update frequency expectations**
- The instructions Copilot must follow when touching documentation

**No documentation changes should be made without following this policy.**

---

## 2. Canonical /docs Folder Structure

```
docs/
├─ README.md                     # This document (governance policy)
│
├─ roadmap/
│  ├─ PROJECT_ROADMAP.md
│  └─ QUALIFIER_COMPLIANCE_MIGRATION_PLAN.md  # **Migration roadmap for compliance features**
│
├─ operations/
│  └─ IMPLEMENTATION_TRACKER.md
│
├─ architecture/
│  ├─ QUALIFIER_COMPLIANCE_SYSTEM_OVERVIEW.md  # **Strategic Intent - READ FIRST**
│  ├─ FRONTEND_ARCHITECTURE.md
│  ├─ AUTHENTICATION_MODEL.md
│  └─ (future: BACKEND_ARCHITECTURE.md)
│
├─ business/
│  └─ BUSINESS_ENTITY_AND_BILLING_MODEL.md
│
├─ audits/
│  └─ PYDANTIC_VALIDATION_DEBUGGING.md
│
├─ guides/                       # Operational how-tos
│  ├─ API_DOCUMENTATION.md
│  ├─ QUICKBOOKS_GUIDE.md
│  ├─ TROUBLESHOOTING.md
│  ├─ CHAT_TESTING_SOP.md
│  └─ WORKFLOW_GUIDE.md
│
├─ setup/                        # Onboarding
│  ├─ SETUP_GUIDE.md
│  ├─ SETUP_NEW_MACHINE.md
│  ├─ SETUP_QUICK_REFERENCE.md
│  └─ GIT_SECRET_SETUP.md
│
├─ deployment/                   # Operations
│  └─ DEPLOYMENT.md
│
├─ technical/                    # Active technical reference
│  ├─ PAYMENTS_FEATURE_DESIGN.md
│  └─ LOGGING_SECURITY.md
│
├─ frontend/                     # Specialized subdomain
│  ├─ FRONTEND_IMPLEMENTATION_SUMMARY.md
│  ├─ FRONTEND_ARCHITECTURE.md
│  ├─ FRONTEND_AUDIT_LOG.md
│  └─ FRONTEND_BACKLOG.md
│
├─ history/                      # Read-only archive
│  ├─ PHASE_COMPLETIONS/
│  ├─ session-logs/
│  ├─ metrics/
│  └─ archive/
│
└─ _triage/                      # Temporary holding area
```

---

## 3. Documentation Classification System

Every document must belong to exactly one category.

### 🟢 KEEP (Active, Authoritative)

- Still reflects current or future system behavior
- Still influences decisions
- Updated intentionally

**Action**: Move to proper folder, continue maintaining

### 🟡 CONSOLIDATE (Valid but Duplicated)

- Information is correct
- But exists in multiple places
- Or mixed with outdated status notes

**Action**:
1. Merge into a canonical doc
2. Delete original after merge

### 🔵 ARCHIVE (Historical Only)

- Describes completed work
- Useful for reference or audits
- Must not affect current decisions

**Action**:
1. Move to `/docs/history/`
2. Freeze permanently

### 🔴 DELETE (Noise)

- Scratch notes
- Superseded drafts
- Contradicts current architecture
- No longer trusted

**Action**: Delete permanently

---

## 4. Triage Workflow (Mandatory Order)

1. Move questionable docs into `/docs/_triage/`
2. Classify using the system above
3. Take the required action
4. **`_triage/` must end empty**

---

## 5. Rules for Creating New Docs

Copilot and humans must follow:

❌ **No new status files**  
❌ **No phase notes outside IMPLEMENTATION_TRACKER.md**  
❌ **No one-off debugging docs unless explicitly approved**  

✅ **One doc per concern**  
✅ **One source of truth per topic**  

### If information belongs in:

- **Daily work** → `operations/IMPLEMENTATION_TRACKER.md`
- **Strategy** → `roadmap/PROJECT_ROADMAP.md`
- **System behavior** → `architecture/`
- **Business rules** → `business/`
- **How-to guides** → `guides/`
- **Setup instructions** → `setup/`
- **Deployment procedures** → `deployment/`
- **Technical specs** → `technical/`
- **Completed work** → `history/`

---

## 6. Document Lifecycle & Update Frequency

### Update Frequency by Folder

| Folder | Frequency | Trigger | Examples |
|--------|-----------|---------|----------|
| `operations/` | **Daily** | Task starts/completes, blockers found | IMPLEMENTATION_TRACKER.md |
| `roadmap/` | **Weekly** | Priorities shift, phases planned | PROJECT_ROADMAP.md |
| `guides/` | **As needed** | New issues discovered, features added | TROUBLESHOOTING.md, API_DOCUMENTATION.md |
| `setup/` | **As needed** | New dependencies, env vars, tools | SETUP_GUIDE.md |
| `technical/` | **During development** | Feature design, schema changes | PAYMENTS_FEATURE_DESIGN.md |
| `audits/` | **One-time** | After audit completes → archive | PYDANTIC_VALIDATION_DEBUGGING.md (canonical) |
| `architecture/` | **Rarely** | Major system redesigns only | AUTHENTICATION_MODEL.md |
| `business/` | **Rarely** | Business rules change | BUSINESS_ENTITY_AND_BILLING_MODEL.md |
| `deployment/` | **Rarely** | Platform migrations, process changes | DEPLOYMENT.md |
| `frontend/` | **As needed** | UI changes, component updates | FRONTEND_BACKLOG.md |
| `history/` | **Never** | Read-only archive | All files |

### When to Archive Documents

**Move to `history/` when document has ANY of these signals:**

🔴 **Status Indicators**:
- Contains "Status: ✅ COMPLETED" or "Status: DONE"
- Title includes "Complete", "Completion", "Progress Report", "Status Report"
- Has completion date in past tense (e.g., "Completed: December 10, 2025")

🔴 **Content Indicators**:
- All tasks marked complete (no forward-looking work)
- Describes past work in past tense ("we implemented...")
- Contains metrics/results from specific dates
- References "before/after" comparisons

🔴 **Folder-Specific Rules**:
- **operations/**: Status reports, progress docs → archive when phase complete
- **technical/**: Design docs → archive when feature shipped
- **audits/**: Audit reports → archive immediately after completion
- **operations/**: Implementation plans → archive when all items done

**Examples that MUST be archived**:
- ❌ `operations/CRUD_PROGRESS_REPORT.md` (completion report)
- ❌ `technical/BUSINESS_ID_COMPLETE.md` (completion doc)
- ❌ `technical/BASELINE_METRICS.md` (dated metrics)
- ❌ `audits/SCHEMA_MODEL_AUDIT.md` (one-time audit)

**Examples that STAY active**:
- ✅ `operations/IMPLEMENTATION_TRACKER.md` (living tracker)
- ✅ `roadmap/PROJECT_ROADMAP.md` (forward-looking)
- ✅ `guides/TROUBLESHOOTING.md` (continuously updated)
- ✅ `audits/PYDANTIC_VALIDATION_DEBUGGING.md` (canonical reference)

### Document Types by Update Pattern

**Living Documents** (never archived):
- Trackers with ongoing tasks
- How-to guides that accumulate solutions
- Roadmaps with future phases
- Canonical troubleshooting references

**Completion Documents** (archive immediately):
- Progress reports
- Status summaries with completion dates
- Audit reports after resolution
- Phase completion summaries

**Reference Documents** (archive when superseded):
- Design specs after implementation
- Baseline metrics after comparison complete
- Implementation plans after execution
- Migration guides after migration done

---

## 7. Copilot Instructions (Non-Negotiable)

When working with documentation, Copilot must:

1. ✅ **Check this README first**
2. ✅ **Never create a new doc without justification**
3. ✅ **Prefer updating existing canonical docs**
4. ✅ **Flag duplication instead of creating new files**
5. ✅ **Ask before introducing new top-level docs**
6. ✅ **Archive completed work immediately** (use signals from Section 6)
7. ✅ **Update `IMPLEMENTATION_TRACKER.md` after completing tasks**

**If unsure, Copilot must stop and ask.**

---

## 8. Enforcement Principle

> **Documentation clarity is more important than documentation volume.**
> 
> **A smaller, trusted docs set is always preferred.**

---

## 9. Canonical Documents

**If you are looking for:**

- **Current priorities** → `roadmap/PROJECT_ROADMAP.md`
- **Active work & blockers** → `operations/IMPLEMENTATION_TRACKER.md`
- **System design** → `architecture/`
- **Business rules** → `business/`
- **Debugging rationale** → `audits/`
- **How-to guides** → `guides/`
- **Setup instructions** → `setup/`
- **Deployment procedures** → `deployment/`
- **Technical specs** → `technical/`
- **Completed work** → `history/`

---

## 10. Quick Navigation

### 🎯 I need to...

**Understand the project plan**  
→ `roadmap/PROJECT_ROADMAP.md`

**Check current work status**  
→ `operations/IMPLEMENTATION_TRACKER.md`

**Understand system architecture**  
→ `architecture/` (frontend, auth, backend)

**Set up my environment**  
→ `setup/SETUP_GUIDE.md`

**Use an API**  
→ `guides/API_DOCUMENTATION.md`

**Deploy changes**  
→ `deployment/DEPLOYMENT.md`

**Troubleshoot an issue**  
→ `guides/TROUBLESHOOTING.md`

**Find historical context**  
→ `history/`

### 📂 Directory Purposes

| Directory | Purpose | Examples |
|-----------|---------|----------|
| `roadmap/` | Strategic planning | PROJECT_ROADMAP.md |
| `operations/` | Daily work tracking | IMPLEMENTATION_TRACKER.md |
| `architecture/` | System design | Frontend, Auth, Backend |
| `business/` | Business rules | Billing model, entity types |
| `audits/` | Debugging guides | Pydantic validation |
| `guides/` | How-to instructions | API docs, QuickBooks, troubleshooting |
| `setup/` | Onboarding | Environment setup, secrets config |
| `deployment/` | Operations | Deployment procedures |
| `technical/` | Active specs | Feature designs, logging patterns |
| `frontend/` | Frontend subdomain | Summary, architecture, backlog |
| `history/` | Completed work | Phase summaries, migration status |
| `_triage/` | Temporary holding | Unclassified docs (must end empty) |

---

## 11. Current Triage Status

**Date**: December 13, 2025  
**Status**: ✅ Complete

**Actions Completed**:
- ✅ Created canonical folder structure
- ✅ Created governance policy (this document)
- ✅ Analyzed existing docs for classification
- ✅ Moved docs to canonical locations
- ✅ Consolidated duplicate auth docs
- ✅ Archived historical docs
- ✅ Verified _triage/ is empty

---

## 12. Backup & Recovery

**Navigation Backup**: The original navigation README is preserved at `_triage/README_NAVIGATION_BACKUP.md` and will be archived after triage completion.

**Rollback**: If governance policy proves problematic, restore navigation README from backup.

---

**Maintained By**: Development Team  
**Enforcement**: Copilot + Manual Review  
**Next Review**: After triage completion
