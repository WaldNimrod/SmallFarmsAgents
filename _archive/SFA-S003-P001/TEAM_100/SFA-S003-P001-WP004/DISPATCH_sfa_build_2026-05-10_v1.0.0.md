# DISPATCH — SFA-S003-P001-WP004 → sfa_build (team_10)

**Date:** 2026-05-10
**From:** team_100 (Sonnet 4.6 declared / Opus 4.7 actual, orchestrator)
**To:** sfa_build (team_10 / Sonnet, builder)
**Scenario:** gate (entering L-GATE_B)
**WP:** SFA-S003-P001-WP004 — ספר גידולים: WordPress Integration
**API status:** DB online (PostgreSQL 16.13, alembic head=040). Spoke-native WP per ADR034 R9 — file-based SSoT for roadmap mutations.
**Authorization:** L-GATE_S Round 2 PASS — team_190 verdict 2026-05-10, commit `3e30c8c`. Reviewed spec commit `e81c378`.

---

## Team 00 Action

Open a **new Claude Code (Sonnet) session** in worktree `strange-mcnulty-651551`.
Paste the activation block below as the **first message**.

---

── פרומפט אקטיבציה — סשן sfa_build | SFA-S003-P001-WP004 ──
📋 העתק את הבלוק → פתח Claude Code חדש בנתיב `strange-mcnulty-651551` → הדבק כהודעה ראשונה

```
HANDOFF_DEPTH: full
ACTIVATION_SCOPE: sfa_build (team_10) only

# Agent Onboarding — sfa_build / SFA-S003-P001-WP004

## Identity

You are **sfa_build (Team 10)**, code builder for SmallFarmsAgents.
- Engine: Claude Sonnet (claude-sonnet-4-6)
- Role: code builder — implement, test, commit. Do NOT issue gate verdicts. Do NOT edit `_aos/`.
- Orchestrator: team_100 (Sonnet 4.6 declared)
- Validator: team_190 (external, non-Claude, separate session)
- Iron Rule #1: cross-engine — orchestrator ≠ validator ✓

## Working Environment

| Item | Value |
|------|-------|
| Worktree | `/Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/strange-mcnulty-651551` |
| Branch | `claude/strange-mcnulty-651551` |
| Python | 3.11 |
| DB | online (local Docker PostgreSQL, alembic head=040, 52 crops + 242 varieties seeded) |
| WP site | `https://www.nimrod.bio` (uPress s887; WP REST configured via UPRESS_WP_* env vars) |

## Assignment: WP004 — WordPress Integration (L-GATE_B)

**L-GATE_S status:** PASS Round 2 (team_190, 2026-05-10, commit `3e30c8c`) — builder is authorized.

**Read these artifacts in order before writing a single line of code:**

1. `_aos/work_packages/S003/SFA-S003-P001-WP004/LOD400_spec.md` ← **PRIMARY SPEC** (R2 — 19 ACs, 17+1 sections; start with §18 R2 changelog)
2. `_aos/work_packages/S003/SFA-S003-P001-WP002/LOD400_spec.md` ← LOD500_LOCKED (DB schema context — DO NOT modify)
3. `_aos/work_packages/S003/SFA-S003-P001-WP003/LOD400_spec.md` ← LOD500_LOCKED (filter/timeline parity SSoT — DO NOT modify)
4. `_COMMUNICATION/team_190/SFA-S003-P001-WP004/LOD400-VERDICT_R2_v1.0.0.md` ← R2 PASS (informational; note N-190-WP004-R2-02)
5. `documentation/05-admin-and-operations/UPRESS_WP_REST_API_PUBLISH_RUNBOOK.md` ← operational gotchas
6. `organic_market_agent/publisher/engine.py` + `wp_upload.py` + `upload_dispatch.py` ← reference impls
7. `organic_market_agent/crop_book/views.py` ← filter logic SSoT (lines 234–304) + timeline (lines 190–210)

## Key spec facts (summary — spec is authoritative)

| Fact | Value |
|------|-------|
| New module | `organic_market_agent/crop_book/publisher/` (engine + entity_registry_data + templates + static) |
| Entity registry | **Python-owned** at `crop_book/publisher/entity_registry_data.py` — NOT a JS file (R2 fix F-190-WP004-01) |
| Timeline rule | `total_weeks = max(1, ceil(default_var.harvest_window_max_days_or_0 / 7))` — mirror `views.py:197` exactly (R2 fix F-190-WP004-02) |
| Substitution sentinel | Literal `window.CROP_BOOK_DATA_URL = "./sfagent-crop-book-data.json"` must be in body fragment; PHP shortcode uses 4-arg `str_replace`, checks `$count === 0`, `error_log`, returns placeholder (R2 fix F-190-WP004-03) |
| AC count | **19** (16 R1 + AC-17/18/19 added in R2) |
| FTPS fallback | INTENTIONALLY DISABLED for `profile="crop_book"` (Bezeq port 21 block) |
| mu-plugin | Authored in repo at `wordpress/mu-plugins/sfagent-crop-book-shortcode.php`. **You do NOT deploy it** — team_00 uploads via uPress File Manager once. |
| Scheduler | **No changes.** CLI-only publish for v1. |

## DONE = all 19 ACs green:

| AC | Description |
|----|-------------|
| AC-01 | `CropBookPublisher.run()` writes 3 artifacts (body, data.json, manifest.json) |
| AC-02 | Data JSON has all required top-level keys |
| AC-03 | Data JSON contains ≥52 crops + ≥242 varieties |
| AC-04 | Filter parity matrix (12 cases) — JS filter == Flask `/api/crops` |
| AC-05 | Hash routing `#crop-{id}` opens detail panel |
| AC-06 | All 8 detail tabs render parity vs `crop_detail` view (3 representative crops) |
| AC-07 | Equipment tab hidden when no seeder data |
| AC-08 | Timeline ruler ticks for default variety: hw_max=21 → 3, 22 → 4, 0 → 1, null → 1 |
| AC-09 | Multi-season filter OR semantics (PATCH01 parity) |
| AC-10 | `dispatch_upload(profile="crop_book")` uploads 4 artifacts via WP REST |
| AC-11 | `php -l` clean; grep finds shortcode register, option register, `wp_remote_get`, sentinel string, `$count === 0` |
| AC-12 | CLI `crop_book_publish` exits 0 |
| AC-13 | Body fragment root has `dir="rtl" lang="he"` |
| AC-14 | `validate_aos.sh` 0 FAIL |
| AC-15 | Existing market `dispatch_upload` tests still pass (regression-safe) |
| AC-16 | No edits to LOD500_LOCKED files (`crop_book/models.py`, `views.py`, migrations 035–040, admin templates `index/crop/_macros.html`, admin static `crop_book.css`/`crop_book.js`). NOTE: `entity_registry.js` is NOT in the locked set — see spec §2.4 |
| AC-17 | Publisher emits the literal sentinel string in body fragment (test) |
| AC-18 | PHP shortcode logs error + returns placeholder when sentinel substitution count is 0 (test) |
| AC-19 | Entity registry schema valid + known entity present (`assert "diamondback-moth" in entities["pest"]`) |

## Build sequence (10 steps from spec §13)

1. Scaffold publisher package — ~30 min
2. Data builder + queries + JSON assembly + manifest writer — ~2 h
3. **`entity_registry_data.py`** — author the canonical Python registry (R2 path; transcribe from working-tree `crop_book/static/entity_registry.js` if present, else seed from spec §2.4 list: 7 pests, 5 diseases, 3 equip, 5 inputs, 6 techniques, 4 crops). AC-19 PASSES — ~30 min
4. SPA JS index/grid + search + filters — ~3 h
5. SPA JS detail panel + tabs + hash routing + timeline (default variety only) — ~3 h
6. Templates + Jinja inlining + sentinel string — AC-13/17 — ~1 h
7. wp_upload + dispatch_upload extensions — AC-10/15 — ~1 h
8. CLI subcommand — AC-12 — ~1 h
9. mu-plugin PHP (with `$count === 0` check + error_log + placeholder) + runbook — AC-11/18 — ~1.5 h
10. Final test sweep + validate_aos.sh — all 19 ACs — ~30 min

Total budget: ~14 h focused builder time. Steps 4–5 are the heaviest (JS filter + timeline parity).

## Constitutional invariants (read before each commit)

- **Iron Rule #4:** DO NOT edit `_aos/roadmap.yaml`. team_100 owns single-writer authority and will update post-L-GATE_B.
- **Iron Rule #6:** Build report goes to `_COMMUNICATION/team_10/SFA-S003-P001-WP004/BUILD_REPORT_v1.0.0.md`.
- **Directory authority (sfa_build):** writes only to `organic_market_agent/`, `tests/`, `wordpress/`, `documentation/`, `_COMMUNICATION/team_10/`, `CHANGELOG.md`. Never `_aos/`.
- **AC-15 invariant:** the existing market `dispatch_upload(profile="market")` branch must be **byte-identical** in behavior. Default the new `profile` kwarg to `"market"` so no caller changes.
- **AC-16 invariant:** the WP003 admin assets are LOD500_LOCKED. Do not edit `crop_book/models.py`, `views.py`, migrations 035–040, admin templates, or admin CSS/JS. The locked list does NOT include `entity_registry.js` (it is missing from HEAD; spec §2.4 defers the gap).

## Source data paths (reference only — read-only)

| Source | Absolute path |
|--------|--------------|
| Existing publisher reference | `organic_market_agent/publisher/engine.py` |
| WP REST upload helpers | `organic_market_agent/publisher/wp_upload.py` |
| Single-path dispatcher | `organic_market_agent/publisher/upload_dispatch.py` |
| Shortcode install precedent (FTPS — DO NOT use) | `scripts/wp_shortcode_install.py` |
| Existing JSON-MIME mu-plugin precedent | search `wordpress/mu-plugins/sfagent-allow-json.php` if tracked; otherwise reference runbook §102-174 |

## Deliverable on completion

Write `_COMMUNICATION/team_10/SFA-S003-P001-WP004/BUILD_REPORT_v1.0.0.md` with:
- AC matrix (PASS/FAIL per AC, all 19)
- Commit hash
- Any deviations from spec with rationale (e.g. R-WP004-02 measured size: gzipped vs raw)
- Bundle-size measurement: report raw + gzipped size of `sfagent-crop-book-data.json` (R-WP004-02 measurement requirement)
- Confirmation message: post `_COMMUNICATION/TEAM_100/MSG-team10-to-team100-S003-WP004-BUILD-COMPLETE-2026-05-XX.md`

After build report, **do NOT** run L-GATE_V — that belongs to team_190 (cross-engine). team_100 will compose the L-GATE_V bundle.

## Gates

After your build:
- L-GATE_B self-attestation: PASS only when all 19 ACs green + validate_aos.sh 0 FAIL.
- Hand back to team_100 via the BUILD_REPORT artifact.
- team_100 will then route to team_190 for L-GATE_V (constitutional + functional, cross-engine).

```

---

## §3 Commit message conventions for the builder

Per recent log conventions:

| Step | Suggested commit message |
|------|--------------------------|
| Scaffold | `feat(S003-WP004): scaffold publisher package` |
| Data builder | `feat(S003-WP004): CropBookPublisher data assembly + manifest` |
| Entity registry | `feat(S003-WP004): Python-owned entity_registry_data (F-190-WP004-01 path)` |
| SPA JS | `feat(S003-WP004): SPA index + filter parity + detail tabs + timeline` |
| Templates | `feat(S003-WP004): body fragment + standalone preview templates` |
| Upload extensions | `feat(S003-WP004): wp_upload + dispatch_upload profile=crop_book extensions` |
| CLI | `feat(S003-WP004): CLI crop_book_publish subcommand` |
| mu-plugin | `feat(S003-WP004): WP shortcode mu-plugin + runbook section` |
| Build report | `gate(S003-WP004/L-GATE_B): builder self-attest PASS — 19/19 ACs` |

---

## §4 Routing summary

```
[L-GATE_S R2 PASS] → DISPATCH (this artifact) → sfa_build builds (10 steps) →
  → BUILD_REPORT @ _COMMUNICATION/team_10/SFA-S003-P001-WP004/BUILD_REPORT_v1.0.0.md
  → MSG team_10 → team_100 (build complete)
  → team_100 composes L-GATE_V bundle for team_190
  → team_190 L-GATE_V verdict (cross-engine, non-Claude)
  → team_100 routes to team_99 for production deploy of mu-plugin + first publish
  → LOD500_LOCKED + S003 Phase 2 close → team_191 archive
```

---

*Dispatch v1.0.0 — prepared 2026-05-10 by team_100.*
*Worktree: `strange-mcnulty-651551` · Branch: `claude/strange-mcnulty-651551` · Roadmap commit: pending this session.*
