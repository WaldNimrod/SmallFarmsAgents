---
id: VERDICT_SFA-S003-P004-WP-CB-SRC-SWEEP_L-GATE_VALIDATE_v1.0.0
type: VERDICT
gate: L-GATE_VALIDATE
from: team_190
to: team_100
cc:
  - team_00
  - team_50
  - team_99
date: 2026-06-11
project: smallfarmsagents
wp: SFA-S003-P004-WP-CB-SRC-SWEEP
subject: Unified SRC-SWEEP + crop-taxonomy / data-integrity remediation
mandate: _COMMUNICATION/TEAM_100/SFA-S003-P004-WP-CB-SRC-SWEEP/VALIDATION_MANDATE_2026-06-11_v2.0.0.md
build_report: _COMMUNICATION/TEAM_100/SFA-S003-P004-WP-CB-SRC-SWEEP/COMPLETION_REPORT_2026-06-11_v1.0.0.md
build_branch: feat/wp-cb-src-sweep
build_commit: dfea7e66d57377201b3ec466563b22afec9b639f
validated_head: 2f102fed9d9da93ab3f1f2ee2dfbad33dbe53b91
validator_engine: Cursor Agent (Composer — non-Claude)
phase_owner: team_190
round: R1
---

# L-GATE_VALIDATE Verdict — SFA-S003-P004-WP-CB-SRC-SWEEP (unified)

## 0. Verdict Box

**Verdict:** PASS  
**WP / Gate / Round:** SFA-S003-P004-WP-CB-SRC-SWEEP / L-GATE_VALIDATE / R1  
**Next step:** team_100 closure protocol — archive mandate (team_191 `ARCHIVE_MANIFEST.md`) → roadmap `LOD500_LOCKED`.

## 1. Verdict Summary

Constitutional L-GATE_VALIDATE **PASS** on branch `feat/wp-cb-src-sweep` at build commit `dfea7e6` (validated HEAD `2f102fe` — docs-only mandate v2.0.0 after code freeze; no application drift). Team 190 (Cursor — **non-Claude**) independently re-executed VC-1..VC-12 for the unified scope (SRC-SWEEP content + crop-taxonomy / data-integrity remediation). Backend **798 passed / 1 skipped**, delivery **233 passed**, `validate_aos.sh` **0 FAIL**, local DB integrity checks green, production API + HTML + CDP probes confirm scoped deploy and postharvest correction. Cross-engine requirement satisfied (builder = Claude Code / team_100; validator ≠ builder per IR#1 / IR#5).

## 2. Parameters

| Field | Value |
|---|---|
| Team ID | team_190 |
| Engine | Cursor Agent (Composer — non-Claude) |
| Gate authority | L-GATE_VALIDATE |
| Builder | team_100 (Claude Code) |
| Cross-engine (IR#1 / IR#5) | Satisfied |
| Mandate | `_COMMUNICATION/TEAM_100/SFA-S003-P004-WP-CB-SRC-SWEEP/VALIDATION_MANDATE_2026-06-11_v2.0.0.md` |
| Build report | `_COMMUNICATION/TEAM_100/SFA-S003-P004-WP-CB-SRC-SWEEP/COMPLETION_REPORT_2026-06-11_v1.0.0.md` |
| Branch | `feat/wp-cb-src-sweep` |
| Build commit (code) | `dfea7e6` |
| Validated HEAD | `2f102fe` (mandate doc only; `dfea7e6` is ancestor) |
| Independence | All VC checks re-executed locally against current DB (no `seed --all` pre-step) |

## 3. Criteria Table (VC-1..VC-12)

| # | Criterion | Result | Evidence |
|---|-----------|--------|----------|
| **VC-1** | Backend `tests/crop_book` | **PASS** | `python3 -m pytest tests/crop_book -q` → **798 passed, 1 skipped**, 0 failed (62.9s). `test_ac05_derived_fields.py` → **8 passed**. Builder cited 797 pass + 1 known-fail on retired www-tier upload test; validator reproduces **5/5 pass** on `test_wp_upload_crop_book.py` (known-fail no longer reproduces — advisory only). |
| **VC-2** | Delivery PHPUnit | **PASS** | `cd sfa_delivery && php vendor/bin/phpunit` → **233 tests, 737 assertions, OK** (1 PHPUnit deprecation advisory). |
| **VC-3** | `validate_aos.sh` | **PASS** | **31 PASS / 21 SKIP / 0 FAIL**. L-GATE_BUILD exit criterion satisfied. |
| **VC-4** | L39 mesclun (crop #31) | **PASS** | Local DB: crop #31 `עלי בייבי` / `name_en=Lettuce: Salad Mix`; variety `חסה בייבי` (`Baby Lettuce (Salanova one-cut mix)`); `cultivar_recommendation` SV from `NI:jmf_ft_mesclun_v1`; **4** internal `crop_knowledge_notes` from same source (irrigation, harvest_marker, cultivar_recommendation, growing_tip). |
| **VC-5** | L45 base-data cherry-pick | **PASS** | Local DB: **62** `crop_variety_source_values` with `source=OP:il_farm_2017_l45`; **22** internal notes across **22** distinct crops. Exclusions documented in `scripts/extract_l45_basedata.py` (calendar, prices, budget, trees, cannabis). |
| **VC-6** | License firewall | **PASS** | `crop_knowledge_notes` absent from `_AGRONOMY_FIELD_WHITELIST` (25 agronomy fields only). `test_ni_publisher_isolation.py` + `TestContentLicenseFirewall` pass. Production HTML: `Salanova` / `Green Oakleaf` **absent** on `/crop-book/salad-mix/` and `/crop-book/cilantro/`. |
| **VC-7** | Publisher `--crop-ids` scoping | **PASS** | Code review + logic verification of `sfa_ingest_push.py`: `CROP_KEYED` set excludes `products`/`cover_crops`; scoped `--table all` limits to crop-keyed tables; ambiguous `--slugs` → `SystemExit` with disambiguation message; non-keyed table + scope → error. |
| **VC-8** | Taxonomy dedup | **PASS** | `constants.py` maps confirmed (`Basil→בזיל`, `Rutabaga→לפת`, `Salad Mix→עלי בייבי`, `Greenhouse Heirloom Tomato→עגבנייה`). `test_seed_taxonomy_fix.py` → **25 passed**. Local DB: **73 crops**, **0** duplicate `name_he`; cultivars preserved — `Aroma 2 F1` + `Nufar` on בזיל #4 (10 varieties); `Joan` on לפת #51 (3 varieties). |
| **VC-9** | Post-seed derived-field strip | **PASS** | `test_strip_derived_fields_*` + full `test_seed_taxonomy_fix.py` / `test_ac05_derived_fields.py` green; `seed.py` auto-strip on `--all` with `--no-strip-derived` escape hatch present. |
| **VC-10** | uc_davis postharvest fix | **PASS** | `uc_davis_postharvest.py` binds `name_he` per sample tuple (no `he_labels[]`). `test_c4_uc_davis_postharvest.py` → 2 passed. Production API storage: peas `0–2°C / 7–10d`, cilantro `0–2 / 7–14d`, broccoli `0–2 / 10–14d`, basil `12–15 / 5–10d` — not prior mis-attributions. |
| **VC-11** | DATA_INTEGRITY_CANON.md | **PASS** | `documentation/03-data-and-schema/DATA_INTEGRITY_CANON.md` present (binding runbook). |
| **VC-12** | Production smoke | **PASS** | `GET /api/v1/crops` → **count=70**. `/api/v1/crops/salad-mix` → `variety_count=13`; `/api/v1/crops/basil` → `variety_count=10`; `/api/v1/crops/turnips` (לפת) → `variety_count=3`. Cilantro page: no `90–180` shelf-life pattern; storage API `7–14d`. `qa_probe.mjs` → **6/6 PASS** (3 routes × mobile+desktop), `overflow=false`, forbidden `Salanova` absent. Site `HTTP/2 200`. |

## 4. Independent Command Evidence

### VC-1 (backend)

```text
798 passed, 1 skipped in 62.88s
test_ac05_derived_fields: 8 passed
test_wp_upload_crop_book: 5 passed (known-fail cited in mandate not reproduced)
```

### VC-2 (delivery)

```text
Tests: 233, Assertions: 737 — OK
```

### VC-3 (AOS)

```text
RESULT: 31 PASS / 21 SKIP / 0 FAIL
```

### VC-12 (production + CDP)

```text
/api/v1/crops count: 70
/api/v1/crops/salad-mix variety_count: 13
/api/v1/crops/basil variety_count: 10
/api/v1/crops/turnips variety_count: 3 (hebrew_name: לפת)
/api/v1/crops/cilantro storage.life_days: {"min": 7, "max": 14}
qa_probe: verdict PASS, failures 0, 6/6 pages overflow=false
```

## 5. Findings

No BLOCKER, MAJOR, or MINOR findings. Round #1 clean on VC-1..VC-12.

**Advisory (non-blocking):**

- **F-190-SRCSWEEP-01 (INFO):** Backend pass count **798** vs builder-cited **797** — retired `test_dispatch_upload_crop_book_profile` now passes (5/5); gate criterion met or exceeded.
- **F-190-SRCSWEEP-02 (INFO):** Mandate deferred items stand — 3 thin keep-crops local-only until enriched; `idan_planner.py` still emits forbidden derived fields neutralised by auto-strip (per mandate §Deferred).

## 6. Builder Cross-Check

| Builder claim | Validator reproduction |
|---|---|
| 797 pass / 1 skip / 1 known-fail | **798 pass / 1 skip / 0 fail** (known-fail absent) ✓ |
| 233 PHP pass | **233 pass** ✓ |
| validate_aos 0 FAIL | **0 FAIL** ✓ |
| 73 crops / 0 dup names | **73 / 0** ✓ |
| L45 62 SV + 22 notes | **62 / 22×22 crops** ✓ |
| Production 70 crops | **70** ✓ |
| salad-mix 13 / basil 10 / לפת 3 | **13 / 10 / 3** ✓ |
| Postharvest corrected live | API + HTML confirm ✓ |

## 7. Route Recommendation

**PASS** — Authorize team_100 archive + `LOD500_LOCKED` per mandate closure protocol.

---

*Constitutional validator: team_190 · Engine: Cursor (non-Claude) · IR#1 / IR#5 satisfied*
