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
- The instructions Copilot must follow when touching documentation

**No documentation changes should be made without following this policy.**

---

## 2. Canonical /docs Folder Structure

```
docs/
├─ README.md                     # This document (governance policy)
│
├─ roadmap/
│  └─ PROJECT_ROADMAP.md
│
├─ operations/
│  └─ IMPLEMENTATION_TRACKER.md
│
├─ architecture/
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

## 6. Copilot Instructions (Non-Negotiable)

When working with documentation, Copilot must:

1. ✅ **Check this README first**
2. ✅ **Never create a new doc without justification**
3. ✅ **Prefer updating existing canonical docs**
4. ✅ **Flag duplication instead of creating new files**
5. ✅ **Ask before introducing new top-level docs**

**If unsure, Copilot must stop and ask.**

---

## 7. Enforcement Principle

> **Documentation clarity is more important than documentation volume.**
> 
> **A smaller, trusted docs set is always preferred.**

---

## 8. Quick Navigation

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

## 9. Current Triage Status

**Date**: December 13, 2025  
**Status**: 🚧 In Progress

See `_triage/TRIAGE_ANALYSIS.md` for complete classification plan.

**Actions Completed**:
- ✅ Created canonical folder structure
- ✅ Created governance policy (this document)
- ✅ Analyzed existing docs for classification

**Actions Pending**:
- ⏳ Move docs to canonical locations
- ⏳ Consolidate duplicate auth docs
- ⏳ Archive historical docs
- ⏳ Verify _triage/ is empty

---

## 10. Backup & Recovery

**Navigation Backup**: The original navigation README is preserved at `_triage/README_NAVIGATION_BACKUP.md` and will be archived after triage completion.

**Rollback**: If governance policy proves problematic, restore navigation README from backup.

---

**Maintained By**: Development Team  
**Enforcement**: Copilot + Manual Review  
**Next Review**: After triage completion
