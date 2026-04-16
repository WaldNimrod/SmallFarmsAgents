# PROJECT CONTEXT — SmallFarmsAgents

## AOS environment (read first)

- **Repository role:** **Spoke** — product + governance (L0); organic market domain; not the AOS hub.
- **Profile:** L0 — `_aos/metadata.yaml` (lean-kit snapshot in `_aos/lean-kit/`).
- **AOS structured WP / gate / lod state:** This repo runs **L0 governance** without an in-tree AOS v3 dashboard engine. **`_aos/roadmap.yaml`** remains the practical registry for AOS work packages and gates **for file-based workflows**. If this project is later connected to a **shared AOS v3 PostgreSQL** used for structured AOS state, mutations must follow **API + `deploy_cascade()`** per hub `governance/directives/ADR034_DATA_AUTHORITY_DB_SSOT_ALL_PROFILES.md` and `methodology/AOS_CONCEPT_AND_PRINCIPLES.md` (Iron Rule #7) — same rules as other profiles when the DB is online.
- **Application / domain data:** Product database and code under `organic_market_agent/`, `hub/`, etc. — domain SSoT per `CODE_STANDARDS` / WP specs (separate from AOS governance files).
- **Roadmap file:** `_aos/roadmap.yaml` — AOS WP list + `gate_history[]`; single-writer per Iron Rule unless/until ADR034 DB path is active.
- **Boundaries:** `_aos/project_identity.yaml` (`organic_market` domain — forbidden patterns enforced by `validate_aos.sh` Check 12)
- **Hub (methodology read-only):** `/Users/nimrod/Documents/agents-os` — do not author hub files from this repo
- **Validation:** `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` — typically **17 PASS / 2 SKIP / 0 FAIL** on this spoke.

## Team entry

- **Architecture / specs:** `_aos/context/ACTIVATION_ARCH.md` or `_COMMUNICATION/team_100/` mandates
- **Implementation (Python/data):** `_aos/context/ACTIVATION_BUILDER.md` or Team 110 routing
- **Validation:** `_aos/context/ACTIVATION_VALIDATOR.md` — L-GATE_BUILD / cross-engine vs builder

## Domain profile

### What this product is

Community AI agent platform for **Israel's organic farming market**. Core product: **OrganicMarketAgent** — community price index for organic vegetables (scraping/normalizing Israeli retail + farm sources). Stack: Python 3.11, PostgreSQL, FastAPI, Alembic, Docker. **Domain id:** `organic_market` (Hebrew NLP, price normalization).

### Current focus

Active milestone and WPs: `_aos/roadmap.yaml`. Run `validate_aos.sh` before any gate declaration. Historical phases (M1–M9) are background only — current truth is roadmap + LOD400 for assigned WP.

### Standards / SSOT

- Application code standards: `_aos/context/CODE_STANDARDS.md` (if present) and package `organic_market_agent/`
- Tests: `tests/` — maintain bar established in pre-AOS QA cycles
- Documentation: `documentation/` English hub
- Integration / handoff: `_COMMUNICATION/`, `hub/` data integration as specified per WP
- AOS data authority (when AOS DB shared): hub ADR034 (read-only path above)

### Repository map (quick)

| Area | Purpose |
|------|---------|
| `organic_market_agent/` | Main Python package |
| `hub/` | Data hub integration |
| `scripts/` | Operational scripts |
| `tests/` | Test suite |
| `_aos/work_packages/` | LOD specs |
