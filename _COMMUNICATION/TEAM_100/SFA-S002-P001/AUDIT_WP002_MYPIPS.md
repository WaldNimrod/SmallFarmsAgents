# AUDIT — SFA-S002-P001-WP002 — MyPIPS Source-Discovery Branch

**Date:** 2026-05-07
**Author:** team_100 (Explore subagent)
**Source branch:** `cursor/mypips-communication-and-handoffs` (2 unique commits, 60 commits behind main)
**Type:** WP_AUDIT_REPORT

---

## Branch content inventory

### RAW-PRESERVE (out of scope — DO NOT TOUCH per team_00)
- `_COMMUNICATION/TEAM_80/TEND_2018–2022/` — farm-ops archives (CROP_PLAN, HARVESTS, SEED_LIST, TASKS, PICK, PACK, 5 years × ZIP/CSV)
- `_COMMUNICATION/TEAM_80/Team 80 MasterClass/` — Hebrew farming education PDFs (~100+ files)
- `_COMMUNICATION/TEAM_80/mypips_discovery_package.zip` — discovery research archive

### MYPIPS-WORK (in scope)
- `_COMMUNICATION/TEAM_10/reports/2026-04-04_MYPIPS_SPIKE_ASSESSMENT_TEAM10.md` — platform analysis (6 store URLs, Firestore architecture, CSS selectors, 4 onboarding candidates)
- `_COMMUNICATION/TEAM_10/reports/2026-04-04_MyPIPS_DISCOVERY_IMPLEMENTATION_TEAM10.md` — CLI tool design (httpx, slugify, canonical vs variant detection)
- `_COMMUNICATION/TEAM_10/reports/2026-04-05_MYPIPS_DISCOVERY_LAYERS_EXPERIMENT_SUMMARY_TEAM10.md` — multi-layer discovery results (L1+L2: 31 slugs, 30 active; L5 variants: 99 probed, 32 active)
- `_COMMUNICATION/TEAM_80/mypips_suspected_links_60.csv` — 60 URL rows, confidence-graded
- `_COMMUNICATION/TEAM_100/reports/2026-04-04_SOURCE_ONBOARDING_STATUS_AND_PHASE2_PLAN.md` — source registry (36 total, 4 MyPIPS as Phase 2C SRC029–032)
- **Stash `stash@{0}`** (currently on this branch):
  - `scripts/mypips_discover.py` — async httpx CLI probe
  - `scripts/mypips_verify_suspected_csv.py`
  - `scripts/mypips_build_onboarding_workbook.py`
  - `organic_market_agent/discovery/mypips_scan.py` — core library
  - `organic_market_agent/models/sources.py` — adds `display_bucket` column (VARCHAR(20), CHECK: `grower|store|chain|discovery|benchmark|verification`)
  - `organic_market_agent/publisher/rolling_aggregate.py` — joins display_bucket → emits `source_types[]`
  - `organic_market_agent/publisher/templates/public_report_body.html` — filter bar UI (הכל / 🌱 מגדלים / 🏪 חנויות / 🏬 רשתות)
  - `documentation/06-scripts-and-cli/README.md` — MyPIPS discovery CLI section

### GENERIC-COMMS / OTHER
- `.gitignore` additions
- `_COMMUNICATION/ROADMAP.md` updates
- AOS governance/validation module deletions (60-commit lag from main; ignore — not MyPIPS work)

---

## Per-source classification

| Source | Hebrew name | Type | Products | Status | Feasibility | Notes |
|--------|-------------|------|----------|--------|-------------|-------|
| **mashtelatharoe** | משתלת הראה | Farm/Nursery | 307 | **COMPLETED** | HIGH | Largest catalog. Direct farm prices. Weekly cycle (Sun–Wed). Firestore DOM. **Priority 1.** |
| **anatiyot** | הננתיות | CSA/Buying group | 25+ cats | **COMPLETED** | HIGH | Only store with `includeOrganic=true`. Weekly cycle Sun 18:00 – Mon 20:00. Cert: אגריאור / IQC / BIO. **Priority 2.** |
| **fruit4soul** | השחקן שהפך לירקן | Distributor | 217 | **COMPLETED** | HIGH | Multi-farm; אורגני בפיקוח. Periodically closed but catalog visible. |
| **finerotem** | משק רתם פיין | Family farm | 11 cats | **COMPLETED** | MEDIUM | Currently closed; high-value when active. |
| **mypips** | מייפיפס | SaaS vendor | — | **NOT_VIABLE** | N/A | Subscription, not produce. Exclude. |
| **thelab** | המעבדה | Vegan cheese | — | **NOT_VIABLE** | N/A | Out of scope. Exclude. |
| **L1+L2 batch** (~30 slugs: agustina, mangolovers, organicfarm, popisrael, sandraperot, vigenbari, flowerstodoor, shivoktary, flowerbulbs, the-group, negohoney, barshah, arava, bestfruit, brodavkameshek, cohen, fourminimonline, freshness, hagitsigal, mahlevot-habraun, meshek-herskovits, mesheknaveh, poli, sal-hagolan, salata, shaked, solomon, +~5) | mixed | mixed | 68–307 each | **PARTIAL** | HIGH–MEDIUM | Search-validated (Google SERP). 30/31 strike. Ready for per-source assessment. |
| **L5 variants** (~32: vigen-bari, pop-israel, fine-rotem, +~25 inferred) | variants | — | — | **PARTIAL (low conf)** | LOW | Hyphen/slash variants; mostly shell pages. Keep for alias expansion. |

---

## Cross-check vs main

`organic_market_agent/sources/` does not exist on main (collectors live in `organic_market_agent/collectors/`). MyPIPS integration is **all new work** — no duplicates.

Phase 2C (per Team 100 onboarding plan): requires Playwright/Selenium for Firestore DOM extraction. One `MypipsCollector` class serving all stores via parameterized `handle`. Skeleton lives in stash.

---

## Volume estimate

| Metric | Count |
|--------|-------|
| URLs probed (`mypips_suspected_links_60.csv`) | 60 |
| Confirmed active | ~35 |
| High-confidence onboarding | 4–6 |
| L1+L2 deduplicated active slugs | 30/31 (~97%) |
| L5 variants active | 32/99 (~32%) |
| Estimated reachable via SERP harvest | 50–100+ additional |

---

## Stash inspection summary

`stash@{0}: WIP: S003-P019 AC-07 clean tree for L-GATE_V revalidation (2026-04-04 Team 170)`

MyPIPS-related changes (apply-ready):
- Models, publisher, templates, docs (listed in MYPIPS-WORK above).
- **Status:** Infrastructure-ready, non-blocking. Apply BEFORE per-source onboarding work.

---

## Recommended integration strategy

### Phase 1 — Apply infrastructure to main
1. Apply stash changes (model `display_bucket`, publisher join, template filter UI, docs section).
2. Add migration to add `display_bucket` column to `sources` table (new migration after WP001 land — likely `034_*` or `075_*` depending on WP001 numbering outcome).
3. Land Team 10 + Team 100 reports under `_COMMUNICATION/` (no conflict — append-only locations).
4. Land `mypips_suspected_links_60.csv` as canonical Phase 1 candidate list.

### Phase 2 — Per-source onboarding (separate sub-tasks)
Onboard the 4 COMPLETED sources in priority order:
1. **mashtelatharoe** (Priority 1, 307 products)
2. **anatiyot** (Priority 2, organic-certified)
3. **fruit4soul** (217 products)
4. **finerotem** (medium feasibility)

For each: implement `MypipsCollector(handle="...")` parameterization, test against live Firestore DOM, register in `sources` table, smoke-test ingestion.

### Phase 3 — Branch cleanup
1. After Phase 1 + Phase 2 land on main: strip MyPIPS-WORK files from `cursor/mypips-communication-and-handoffs`.
2. Rename branch → `archive/raw-material-tend-masterclass-2026-04`.
3. Tag the pre-cleanup head as `archive/mypips-handoffs-732121e`.
4. Tend exports + MasterClass remain on the renamed branch — UNTOUCHED.

---

## Out of scope under WP002

- Phase 2 onboarding **beyond the 4 priority sources** (defer to future WP).
- L5 variant slug expansion (defer).
- Google Custom Search API integration for ongoing harvest (defer).
- Tend exports + MasterClass (raw material, next phase).

---

## Sprint estimate

**LARGE (5–8 days)**:
- Day 1: Apply stash + add migration + land docs.
- Days 2–4: Onboard 4 sources (Playwright collector + per-source tests).
- Day 5: Smoke-test in dev DB, run pipeline end-to-end.
- Days 6–7: QA + remediation.
- Day 8: Branch cleanup + archive tags.

---

*End of audit.*
