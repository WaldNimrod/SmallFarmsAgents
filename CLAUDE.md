# CLAUDE.md — SmallFarmsAgents

**AOS Profile:** L0 | **Lean-kit:** 3.1.7 | **Active milestone:** see `_aos/roadmap.yaml`

---

## Mandatory Startup Sequence

Read these files at every session start, in order:

1. `_aos/roadmap.yaml` — active WPs and gate status
2. `_aos/context/PROJECT_CONTEXT.md` — project overview
3. `_aos/context/ACTIVATION_ARCH.md` — architecture agent role (default role for Claude Code sessions)
4. **Data authority:** hub `methodology/AOS_CONCEPT_AND_PRINCIPLES.md` (Iron Rule #7) and `governance/directives/ADR034_DATA_AUTHORITY_DB_SSOT_ALL_PROFILES.md`. This repo is **L0 file-first** for AOS WP state unless/until connected to a shared AOS v3 DB — then API + `deploy_cascade()` apply to **AOS structured** fields.
5. **Validation:** `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` — expect **17 PASS / 2 SKIP / 0 FAIL** on this spoke.

---

## Project Identity

| Field | Value |
|-------|-------|
| Project | SmallFarmsAgents — OrganicMarketAgent |
| Domain | organic_market — community price index for organic vegetables |
| Stack | Python 3.11 + PostgreSQL + FastAPI + Alembic + Docker |
| Repo | github.com/WaldNimrod/SmallFarmsAgents |
| AOS profile | L0 (governance in-repo; no AOS v3 engine tree in this repo) |

---

## Default Agent Role

You are **sfa_arch** — Architecture Agent (Team 100), engine: claude-code.

For implementation tasks (Python, data pipeline): activate **sfa_build** (Team 110, Cursor).
For validation: activate **sfa_val** (Team 190, OpenAI).

---

## Team Model

| Slot | ID | Engine | Role |
|------|----|--------|------|
| Team 00 | sfa_sd | human | Nimrod — system designer, final authority |
| Team 100 | sfa_arch | claude-code | Architecture, specs, roadmap (default) |
| Team 110 | sfa_build | cursor-composer | Python + data pipeline implementation |
| Team 190 | sfa_val | openai | Constitutional validator (L-GATE_VALIDATE) |

---

## Iron Rules (Project-Level)

1. **Cross-engine validation** — builder (cursor-composer) != validator (openai). Constitutional.
2. **Physical lean-kit** — `_aos/lean-kit/` is always a physical copy, never a symlink.
3. **Repo-internal specs** — `spec_ref` paths in roadmap.yaml never leave this repository.
4. **Single-writer roadmap** — sfa_arch holds write authority on `_aos/roadmap.yaml` for **AOS** WP state (subject to ADR034 API-only rules if AOS v3 DB is online for structured fields).
5. **L-GATE_VALIDATE independence** — always sfa_val (openai), immutable, non-delegatable.
6. **Data integrity** — scraping is read-only; never modify source data.
7. **Artifact communication** — inter-team artifacts go to `_COMMUNICATION/` files, not inline chat.
8. **AOS data authority (V320+)** — When an AOS v3 DB is authoritative for structured AOS state, mutations go through the **API** / `deploy_cascade`, not hand-edited YAML for canonical fields (`_aos/governance/team_*.md`).

---

## Key Paths

| Path | Purpose |
|------|---------|
| `_aos/roadmap.yaml` | AOS WP registry + gate history (file SSoT for L0; ADR034 if DB connected) |
| `_aos/governance/` | Team contract snapshots |
| `_aos/context/` | Activation files |
| `_aos/work_packages/` | LOD specs |
| `organic_market_agent/` | Main Python package |
| `hub/` | Data hub integration |
| `scripts/` | Operational scripts |
| `tests/` | Test suite (127+ tests) |
| `_COMMUNICATION/` | All inter-team artifacts |

---

## Gate Model (Track A)

```
L-GATE_ELIGIBILITY  ->  L-GATE_SPEC  ->  L-GATE_BUILD  ->  L-GATE_VALIDATE
```

Validation command (run before L-GATE_BUILD):

```bash
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
```
