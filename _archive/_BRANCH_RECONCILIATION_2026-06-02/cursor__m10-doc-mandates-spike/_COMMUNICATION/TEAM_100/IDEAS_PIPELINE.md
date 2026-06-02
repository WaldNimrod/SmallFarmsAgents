---
document_type: IDEAS_PIPELINE
version: "1.0"
---

# Team 100 — Canonical Ideas Pipeline

**Document ID:** IDEAS-PIPELINE-TEAM100  
**Owner:** Team 100 (Architecture)  
**Maintained by:** Team 100 (add ideas via ARCH_DECISION or inline; Nimrod approves promotions)  
**Last updated:** 2026-04-08

---

## Purpose

This document captures ideas, suggestions, and non-spec requests that have been **deferred** from active milestones. Ideas here are:

- Acknowledged as potentially valuable
- **Not in scope** for any current milestone
- **Not lost** — they are tracked here for future sprint planning

An idea moves from this pipeline to an active milestone only when Nimrod approves it and Team 100 issues a mandate.

---

## Status Legend

| Status | Meaning |
|--------|---------|
| `BACKLOG` | Captured, not yet evaluated |
| `EVALUATED` | Team 100 has assessed feasibility and value |
| `DEFERRED` | Explicitly deferred; reason documented |
| `PROMOTED` | Moved to an active milestone |
| `DECLINED` | Decided against; reason documented |

---

## Pipeline

### IDEA-001 — Unit Normalization Summary Report

**Status:** `DEFERRED`  
**Proposed by:** Team 100 (pre-implementation review, 2026-04-08)  
**Triggered by:** Mandate Task 4 had a fabricated "Unit Summary Report" deliverable assigned to Team 10 (no spec authority). Removed from mandate per LOD400 spec alignment.  
**Concept:** After each catalog quality release cycle, generate a cross-product, cross-source summary of all `normalized_unit` values present in `normalized_observations`. Group by product and show count, unit distribution, and flag any residual ambiguities. Could be automated via `catalog_scan_collect_metrics.py` extension or a new `unit_audit` CLI command.  
**Value:** Operator visibility into unit drift over time; useful baseline for future CQ cycles.  
**Blocker:** No spec authority in LOD400 or M10 mandate. Would require a new LOD200 item and Team 80 input on which metrics matter most to operators.  
**Proposed home:** M10.x or a future "Catalog Observability" sub-milestone.  
**Nimrod decision (2026-04-08):** *"Defer — must be saved as idea in ideas pipeline and addressed later."* ✓ Confirmed.

---

## Promotion Process

When Nimrod or Team 80 approves an idea for development:
1. Team 100 moves its status to `PROMOTED` and records the target milestone.
2. Team 100 issues a new LOD200 or LOD400 spec item covering the idea.
3. The idea is removed from this pipeline and tracked in `_COMMUNICATION/ROADMAP.md`.

---

*Owned by: Team 100 (Architecture)*  
*This document is updated whenever ideas are added, promoted, or declined.*
