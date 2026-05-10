# DISPATCH — SFA-S003-P001-WP003 → sfa_build (team_10)

**Date:** 2026-05-08
**From:** team_100 (Sonnet 4.6, orchestrator)
**To:** sfa_build (team_10 / Sonnet, builder)
**Scenario:** gate (entering L-GATE_B)
**WP:** SFA-S003-P001-WP003 — ספר גידולים: UI Views (Flask Blueprint, read-only)
**API status:** Offline-DB fallback — artifact-based dispatch per ADR034 R9
**Authorization:** L-GATE_S PASS (team_190 Round 2, 2026-05-08). WP002 dependency unblocked — LOD500_LOCKED (commit 9b26666).

---

## Team 00 Action

Open a **new Claude Code (Sonnet) session** in worktree `strange-mcnulty-651551`.
Paste the activation block below as the **first message**.

---

── פרומפט אקטיבציה — סשן sfa_build | SFA-S003-P001-WP003 ──
📋 העתק את הבלוק → פתח Claude Code חדש בנתיב `strange-mcnulty-651551` → הדבק כהודעה ראשונה

```
HANDOFF_DEPTH: full
ACTIVATION_SCOPE: sfa_build (team_10) only

# Agent Onboarding — sfa_build / SFA-S003-P001-WP003

## Identity

You are **sfa_build (Team 10)**, code builder for SmallFarmsAgents.
- Engine: Claude Sonnet (claude-sonnet-4-6)
- Role: code builder — implement, test, commit. Do NOT issue gate verdicts.
- Orchestrator: team_100 (Sonnet 4.6)
- Validator: external (team_190, non-Claude, separate session)
- Iron Rule #1: cross-engine — orchestrator ≠ validator ✓

## Working Environment

| Item | Value |
|------|-------|
| Worktree | `/Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/strange-mcnulty-651551` |
| Branch | `claude/strange-mcnulty-651551` |
| Python | 3.11 |
| DB | offline — WP002 models + migrations exist in-tree; use SQLite in-memory for tests |
| Hub DB | offline throughout — ADR034 R9 protocol active |

## Assignment: WP003 — UI Views / Flask Blueprint (L-GATE_B)

**L-GATE_S status:** PASS (team_190 Round 2, 2026-05-08) — builder is authorized.
**WP002 dependency:** LOD500_LOCKED (commit 9b26666). All 6 crop_book tables + models + importer are in-tree. Use the existing `organic_market_agent/crop_book/models.py` — do NOT rewrite or duplicate.

**Read these artifacts in order before writing a single line of code:**

1. `_aos/work_packages/S003/SFA-S003-P001-WP003/LOD400_spec.md` (v2.0.0) ← PRIMARY SPEC
2. `_COMMUNICATION/TEAM_100/SFA-S003-P001-WP001/LOD200_CROP_SCHEMA_2026-05-07_v1.0.0.md` (v1.5.0) ← schema SSoT
3. `_COMMUNICATION/TEAM_100/SFA-S003-P001-WP003/LOD300_UI_MOCKUP_2026-05-07_v1.0.0.md` ← UI wireframes
4. `organic_market_agent/crop_book/models.py` ← existing ORM models (WP002, do not modify)
5. `_COMMUNICATION/team_190/SFA-S003-P001-LOD400-VERDICT_R2_v1.0.0.md` ← L-GATE_S Round 2 PASS

## Key spec facts (summary — spec is authoritative)

| Fact | Value |
|------|-------|
| Blueprint prefix | `/crop-book/` |
| Routes | 3: GET `/crop-book/`, GET `/crop-book/<int:crop_id>/`, GET `/crop-book/api/crops` |
| Templates | `crop_book/index.html`, `crop_book/crop.html`, `crop_book/_macros.html` |
| Static | `organic_market_agent/admin/static/crop_book/crop_book.css` + `crop_book.js` |
| ENTITY_REGISTRY | `organic_market_agent/admin/static/crop_book/entity_registry.js` (repo-owned, no /tmp) |
| Tab visibility | All 8 tabs render always; only ציוד may be hidden when ALL seeder fields NULL |
| Market price | NO live pricebook reads in S003. When pricebook_product_id set: placeholder text. No delta %. |
| Layout | RTL, Hebrew throughout |
| Scope | View-only — zero POST routes, zero edit/delete |

## DONE = all 11 ACs green:

| AC | Description |
|----|-------------|
| AC-01 | Blueprint registered; GET /crop-book/ → 200; GET /crop-book/1/ → 200; GET /crop-book/99999/ → 404; GET /crop-book/api/crops → JSON |
| AC-02 | Category tabs filter crop grid correctly |
| AC-03 | Free-text search + advanced search (DTM max, seasons) functional |
| AC-04 | Crop detail: all 8 tabs render; tabs with no data show "אין נתונים" placeholder, not hidden |
| AC-05 | Variety cards: ★ default, 🔗 grafted badge + rootstock, price + yield |
| AC-06 | כלכלה tab: מחיר מתועד card (with expandable yearly breakdown); מחיר שוק placeholder when pricebook_product_id set; "לא מקושר למחירון" when null |
| AC-07 | Entity tags: styled spans, correct CSS class, hover tooltip, data-etype + data-eid present, no href |
| AC-08 | Timeline tab: proportional phase bars for ארוגולה (DTM=21, harvest_window=80) + עגבנייה (100); graceful fallback for no DTM data |
| AC-09 | RTL layout: html dir=rtl or equivalent; breadcrumb RTL; all labels right-to-left |
| AC-10 | No edit/delete: zero form inputs (except search/filter); no POST routes |
| AC-11 | Tests green: test_views.py (Flask test client, mock DB session); validate_aos.sh 0 FAIL |

## File-level deliverables (spec §5)

### CREATE
```
organic_market_agent/crop_book/views.py
organic_market_agent/crop_book/templates/crop_book/index.html
organic_market_agent/crop_book/templates/crop_book/crop.html
organic_market_agent/crop_book/templates/crop_book/_macros.html
organic_market_agent/admin/static/crop_book/crop_book.css
organic_market_agent/admin/static/crop_book/crop_book.js
organic_market_agent/admin/static/crop_book/entity_registry.js
tests/crop_book/test_views.py
```

### UPDATE
- `organic_market_agent/admin/__init__.py` (or equivalent) — register `crop_book_bp`
- `CHANGELOG.md` — add UI entry under [Unreleased]

## Deliverable on completion

Write `_COMMUNICATION/team_10/SFA-S003-P001-WP003/BUILD_REPORT_v1.0.0.md` with:
- AC matrix (PASS/FAIL per AC)
- Commit hash
- Any deviations from spec with rationale

Do NOT update `_aos/roadmap.yaml` — that is team_100's responsibility after L-GATE_B.
```
