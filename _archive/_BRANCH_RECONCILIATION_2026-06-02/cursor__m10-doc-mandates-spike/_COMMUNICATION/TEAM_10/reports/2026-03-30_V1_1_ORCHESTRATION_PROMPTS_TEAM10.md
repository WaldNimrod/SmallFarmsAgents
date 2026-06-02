# v1.1.0 orchestration — per-actor mandate packages and paste-ready prompts

**Date:** 2026-03-30  
**Owner:** Team 10 (orchestrator)  
**Spine:** `_COMMUNICATION/TEAM_10/HANDOFF_V1_1_ORCHESTRATION_TEAM10.md` (HANDOFF-20260408-V1-1-ORCH-TEAM10)

Use English for all cross-team artifacts. Each block below is a **first-contact** package: role, mandatory reads, concrete ask, wait condition, and a short paste-ready message.

---

## Team 20 (Infrastructure)

**Role and objective:** Own Alembic revisions under `organic_market_agent/db/versions/`. Apply and confirm migrations; Team 10 must not run `alembic upgrade head` on shared databases without your written confirmation.

**Mandatory reads**

- [docs/GLOSSARY.md](docs/GLOSSARY.md)
- [_COMMUNICATION/TEAM_10/HANDOFF_V1_1_ORCHESTRATION_TEAM10.md](../HANDOFF_V1_1_ORCHESTRATION_TEAM10.md) §5.1, §3 (authority table)
- [_COMMUNICATION/TEAM_20/reports/2026-03-30_V1_1_MIGRATION_072_REQUEST_TEAM10.md](../../TEAM_20/reports/2026-03-30_V1_1_MIGRATION_072_REQUEST_TEAM10.md)

**Your ask (H1)**

- Create and apply migration **072** (or next revision) for **SRC_WA** source + profiles per the SQL in the migration request.
- File confirmation in `_COMMUNICATION/TEAM_20/reports/` including `alembic current` = head.

**Wait condition**

- Team 10 proceeds to Phase B operator work only after that confirmation exists.

**Paste-ready prompt**

> Team 20 — please implement HANDOFF H1 for v1.1.0: migration request `2026-03-30_V1_1_MIGRATION_072_REQUEST_TEAM10.md` (SRC_WA + profiles). Team 10 has not run `alembic upgrade head`. Reply with revision id and `alembic current` output in `_COMMUNICATION/TEAM_20/reports/`. Thank you.

---

## Team 100 (Architecture)

**Role and objective:** Resolve spec/code conflicts, approve new product codes, sign off tier-range or Pantry ADR policy when data disagrees with ARCH/CQ-MASTER.

**Mandatory reads**

- GLOSSARY, LOD400 Phase A spec, HANDOFF §5.3 / §9
- Delta: [_COMMUNICATION/TEAM_100/reports/2026-03-30_DELTA_WHATSAPP_INSERT_SPEC_TEAM10.md](../../TEAM_100/reports/2026-03-30_DELTA_WHATSAPP_INSERT_SPEC_TEAM10.md)

**Your ask (H3 + delta)**

- Respond to the WhatsApp §A4.3 `INSERT` delta with a binding choice (admin-only vs schema change vs synthetic asset/run recipe).
- When C3 blueberry research is ready, sign Pantry ADR per spec §D1.

**Wait condition**

- Team 10 does not publish executable `psql` for WhatsApp until Team 100 updates the spec or approves a workaround.

**Paste-ready prompt**

> Team 100 — Team 10 filed `2026-03-30_DELTA_WHATSAPP_INSERT_SPEC_TEAM10.md`. SPEC §A4.3 INSERT cannot run against current `raw_extracted_items` (NOT NULL FKs, column names, no `pending_manual`). Please issue erratum or ADR so we can finalize `WHATSAPP_DATA_SUBMISSION_PROTOCOL.md` Section 5 with an executable operator path.

---

## Nimrod (operator)

**Role and objective:** Run full pipeline on the workstation that holds credentials and Postgres; FTPS upload; optional WP REST blog draft per §A4.

**Mandatory reads**

- HANDOFF §5.2, §4 Phase B / Phase E
- [_COMMUNICATION/TEAM_10/reports/2026-03-30_V1_1_PHASE_B_REQUEST_TEAM10.md](2026-03-30_V1_1_PHASE_B_REQUEST_TEAM10.md)

**Your ask (H2 / H6)**

- Start Docker/Postgres, confirm Team 20 migration applied, run Phase B commands; later Phase E + `--upload` as required.
- If WP Application Password is missing, create blog placeholder manually and note in completion report.

**Wait condition**

- Team 10 updates completion report evidence after you paste outputs.

**Paste-ready prompt**

> Nimrod — v1.1.0 Phase B is unblocked when Team 20 confirms DB head. Please run the command block in `2026-03-30_V1_1_PHASE_B_REQUEST_TEAM10.md` and send back ingestion summary + `public_report.json` stats (product count, PRD027 count). FTPS deferred to Phase E per HANDOFF.

---

## Team 190 (Constitutional preflight)

**Role and objective:** Validate governance package **before** Team 50 sees QA artifacts.

**Mandatory reads**

- HANDOFF §5.4
- [_COMMUNICATION/TEAM_190/PREFLIGHT_REQUEST_V1_1_TEAM10.md](../../TEAM_190/PREFLIGHT_REQUEST_V1_1_TEAM10.md)

**Your ask (H4)**

- **Hold** until completion report is **COMPLETE**; then run preflight checklist and issue PASS/FAIL.

**Wait condition**

- Team 10 replaces HOLD in preflight file or files new dated request with full links.

**Paste-ready prompt**

> Team 190 — `PREFLIGHT_REQUEST_V1_1_TEAM10.md` is intentionally on HOLD. No action until Team 10 marks v1.1.0 completion COMPLETE and attaches full evidence. We will re-file or update when ready.

---

## Team 50 (QA)

**Role and objective:** Execute `QA_MANDATE_G_V1_1` when and only when preflight PASS and completion package is complete.

**Mandatory reads**

- [_COMMUNICATION/TEAM_50/QA_MANDATE_G_V1_1.md](../../TEAM_50/QA_MANDATE_G_V1_1.md)
- [_COMMUNICATION/TEAM_50/reports/2026-03-30_V1_1_QA_REQUEST_TEAM10.md](../../TEAM_50/reports/2026-03-30_V1_1_QA_REQUEST_TEAM10.md)

**Your ask (H5)**

- **Do not start** while QA request header says BLOCKED.

**Wait condition**

- Team 190 PASS + updated completion report.

**Paste-ready prompt**

> Team 50 — QA request for G-V1.1 is on file but BLOCKED (partial completion). We will notify you when Team 190 preflight PASS and final evidence are attached.

---

## Team 10 (self — implementers)

**Mandatory reads:** GLOSSARY → Phase A LOD400 spec → `MANDATE_V1_1_LOD400_EXEC_TEAM10.md` → HANDOFF.  
**Session startup:** HANDOFF §8 before each session.

---

*Prepared by Team 10 orchestration (wave 1), 2026-03-30.*
