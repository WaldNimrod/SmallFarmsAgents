---
id: L-GATE_V_MANDATE_SFA-S003-P002-WP-UI-patch03_v1.0.0
from: team_100 (Chief Architect)
to: team_190 (Constitutional cross-engine validator)
cc: team_00, team_10, team_50
date: 2026-05-29
type: validation_mandate
wp: SFA-S003-P002-WP-UI-patch03
gate: L-GATE_V
build_commit: "509c5f5"
spec_ref: _aos/work_packages/S003/SFA-S003-P002-WP-UI-patch03/LOD400_spec.md
engine_constraint: "NON-CLAUDE REQUIRED (IR#1) — builder=Claude Sonnet, QA=Claude Haiku, integrator=Claude Opus. Validator MUST be a non-Claude engine (Cursor/Composer, Codex, or GPT-5.x)."
---

# L-GATE_V MANDATE — WP-UI-patch03 (Crop-book detail UX + agronomic data surfacing)

## Why this is a cross-engine handoff
Build (team_10, Claude Sonnet sub-agents) ≠ QA (team_50, Claude Haiku) ≠ integration/deploy
(team_100, Claude Opus). Per **Iron Rule #1 / #5**, the constitutional L-GATE_VALIDATE
verdict MUST come from a **non-Claude** engine. team_100 cannot self-issue it — hence this
mandate to team_190.

## What was built (commit 509c5f5, on main; deployed live)
- **Data (`organic_market_agent/publisher/sfa_ingest_push.py`):** `_fetch_crop_varieties`
  attaches an `agronomy` object (16-field §2 whitelist) to each variety `payload_json`
  from `crop_field_enrichment`; existing keys preserved; idempotent. Re-pushed live
  (364 rows → uPress MySQL via HMAC ingest API, all HTTP 200).
- **Frontend (`sfa_delivery/`):** `CropBookViewController::detail` aliases
  `days_to_maturity→dtm_days`, **backfills the default variety's agronomy with the median
  of sibling varieties** (team_00 ruling 2026-05-29), computes type-safe per-variety
  `agro_delta` vs that baseline; `variety_row.php` renders the agronomic grid with Hebrew
  labels (drops color/taste/shape) + `cb-var__val--delta` highlight; `book_crop.php`
  central-panel layout; `hub.css` typography + delta rule; `entry()` + `book_entry.php`
  landing crop-card grid. New `tests/VarietyRowAgronomyTest.php`.

## Evidence already on record (verify independently — do not trust)
- **Build/QA gate_history:** `_aos/roadmap.yaml` → SFA-S003-P002-WP-UI-patch03
  (L-GATE_B PASS team_10; QA QA_PASS team_50 10/10; DEPLOY LIVE team_100).
- **team_100 independent re-verify:** `php -l` clean ×5; `cd sfa_delivery && composer test`
  → 57 tests / 0 failures (1 pre-existing PHPUnit deprecation); `validate_aos.sh` 29/19/0;
  ingest dry-run 364/364 varieties carry agronomy.

## Acceptance criteria to independently disposition (LOD400 §4)
| AC | Check |
|----|-------|
| AC-U3-01 | ingest variety payload carries `agronomy` (DTM, germination, spacing, pH, storage, NPK, yield) |
| AC-U3-02 | `/crop-book/arugula` variety rows show ≥3 real agronomic values for default |
| AC-U3-03 | DTM no longer "—" when data exists (key map) |
| AC-U3-04 | non-default values differing from the (backfilled) default are highlighted `cb-var__val--delta` |
| AC-U3-05 | detail uses central panel; no large empty left column |
| AC-U3-06 | variety-grid typography readable (font-size bumped) |
| AC-U3-07 | `/crop-book/` landing shows crop cards |
| AC-U3-08 | unsourced product fields (color/taste/shape) removed |
| AC-U3-09 | `php -l` clean; `composer test` 0 new failures (57+); variety_row render test |
| AC-U3-10 | `validate_aos.sh` 0 FAIL; no engine/reconciler/schema change; no `www.nimrod.bio` |
| AC-U3-11 | deployed to `sfa.nimrod.bio` (uPress, NOT home server); live smoke 200 + agronomy visible |

## Live smoke already observed by team_100 (corroborate independently)
- Served from **uPress / Cloudflare** (cf-ray TLV edge) — NOT waldhomeserver.
- `/`, `/crop-book/`, `/crop-book/arugula`, `/crop-book/table` → all **200**.
- arugula default `מצוי-ברירת מחדל` shows חלון קטיף=**45** (computed median of 80/45/38);
  Arugula 80**Δ** / hyd.Rocket 38**Δ** / Wild Rocket 45 (no Δ — equals baseline);
  lettuce shows 20 deltas. Landing renders crop cards.

## Constitutional checks (per CANON)
Cross-engine independence (IR#1); directory authority; delivery tier is a faithful uPress
read-mirror (no derived data pushed to MySQL — the median backfill is render-time only);
no `www.nimrod.bio` reintroduction; locked LOD500 files untouched.

## Deliverable
Write verdict to `_COMMUNICATION/team_190/SFA-S003-P002-WP-UI-patch03/L-GATE_V_VERDICT_v1.0.0.md`.
On PASS → team_100 executes ADR042 closure (archive mandate → roadmap LOD500_LOCKED).

— team_100 (Claude Opus 4.8) 2026-05-29
