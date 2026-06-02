# Team 100 — Pre-Implementation Review: Information Completions Request

**Document ID:** REVIEW-20260408-PREIMPL-COMPLETIONS  
**Date:** 2026-04-08  
**Author:** Team 100 (Architecture)  
**Audience:** Nimrod (project lead) + Team 10 (DO NOT begin implementation until this is resolved)  
**Status:** BLOCKING — implementation hold until Section A errors are corrected and Section B questions answered  
**Trigger:** Mandatory pre-implementation document review per Team 100 ONBOARDING §First Actions

---

## Background

Before signaling Team 10 to begin implementation, Team 100 performed a full cross-document review of the active package:

- `docs/GLOSSARY.md`
- `_COMMUNICATION/TEAM_100/reports/2026-04-08_PHASE_A_LOD400_SPEC_TEAM100.md` (SPEC-20260408-PHASE-A-LOD400)
- `_COMMUNICATION/TEAM_10/MANDATE_V1_1_LOD400_EXEC_TEAM10.md` (MANDATE-20260408-V1-1-LOD400-EXEC)
- `_COMMUNICATION/TEAM_10/HANDOFF_V1_1_ORCHESTRATION_TEAM10.md` (HANDOFF-20260408-V1-1-ORCH-TEAM10)

Supporting context read: `_COMMUNICATION/ROADMAP.md`, `_COMMUNICATION/TEAM_100/CANONICAL_PROGRAM_BRIEF_PHASES_A_B_TEAM100.md`, `_COMMUNICATION/TEAM_50/QA_MANDATE_G_V1_1.md`, `_COMMUNICATION/TEAM_10/MANDATE_V1_1_CONSOLIDATED_TEAM10.md`.

The review found **3 material errors** in the mandate and handoff documents (Section A) and **4 open questions** requiring either Nimrod direction or explicit Team 100 policy (Section B). These must be resolved before Team 10 opens a session.

---

## Section A — Material Errors (require correction before implementation)

These are verifiable contradictions between the issued mandate/handoff and the governing LOD400 spec. They are not interpretive disagreements — the spec is explicit.

---

### Error A1 — Phase C task list in mandate is wrong (C2 and C3 misidentified)

**Severity:** HIGH — affects two CQ packages; Team 10 would skip CQ-P04 and CQ-P05 entirely and do undocumented work instead.

**File:** `_COMMUNICATION/TEAM_10/MANDATE_V1_1_LOD400_EXEC_TEAM10.md` § Task 3  
**Same error in:** `_COMMUNICATION/TEAM_10/HANDOFF_V1_1_ORCHESTRATION_TEAM10.md` § Session 3 / Phase C

**What the mandate says (WRONG):**
| Label | Mandate text |
|-------|-------------|
| C2 | "Basket Alias Remapping — verify all basket product aliases map to PRD025/026/027" |
| C3 | "Pantry ADR — create the Pantry architectural decision record (spec §C3)" |

**What the LOD400 spec says (CORRECT):**

| Label | Spec text (lines 52–55, 774–870) |
|-------|----------------------------------|
| C1 | Eggs Unit Audit (CQ-P03) |
| C2 | **Passion Fruit Disambiguation (CQ-P04)** — source × unit matrix for PRD072; classify each source as genuine per-fruit or mislabeled kg; add source-scoped `normalizer_rules` where needed |
| C3 | **Blueberries Pack Research (CQ-P05)** — `source × pack_description × grams_if_known` research table for PRD086; backlog items for D1 Pantry ADR |
| C4 | CSA Basket Tier Mapping (CQ-P07) — `basket_tier_resolver.py` |

**Root cause:** The mandate author substituted "Basket Alias Remapping" (not a CQ package) for Passion Fruit, and "Pantry ADR" (which is a Phase D, Team 100 deliverable) for Blueberries. Neither substitution has a basis in the LOD400 spec.

**Required correction to mandate:** Replace Task 3 Phase C description to match the spec exactly:
- C2 → Passion Fruit Disambiguation (CQ-P04)
- C3 → Blueberries Pack Research (CQ-P05)
- Remove "Basket Alias Remapping" (no spec authority)
- Move Pantry ADR to Phase D (see A2)

---

### Error A2 — Phase D task in mandate is wrong (Team 100 deliverable attributed to Team 10 as a different task)

**Severity:** HIGH — Team 100 D1 deliverable (Pantry ADR) is missing from the mandate entirely; a fabricated "Unit Summary Report" (not in spec) is assigned to Team 10 instead.

**File:** `_COMMUNICATION/TEAM_10/MANDATE_V1_1_LOD400_EXEC_TEAM10.md` § Task 4  
**Same error in:** `_COMMUNICATION/TEAM_10/HANDOFF_V1_1_ORCHESTRATION_TEAM10.md` § Session 4

**What the mandate says (WRONG):**
> Task 4 — Phase D: Unit Summary Report
> Owner: Team 10
> Produce the unit normalization summary report documenting all unit strings in normalized_observations grouped by product...

This task does not exist in the LOD400 spec.

**What the LOD400 spec says (CORRECT):**

> Phase D — Architecture (after C3 research table)
> D1: Pantry ADR (CQ-P06)
> Owner: **Team 100** (spec) — this is authored by Team 100, not Team 10
> Note: CQ-P06 is spec-only. Any implementation requires a separate mandate after ADR is signed.
> File: `_COMMUNICATION/TEAM_100/reports/2026-04-08_ADR_PACK_WEIGHT_COMPARISON_TEAM100.md`

**Implications:**
1. Team 100 has a deliverable (D1 — Pantry ADR) that is not in the mandate or handoff as a Team 100 action item.
2. The coordination protocol between Team 10 (provides C3 blueberry research) and Team 100 (consumes C3 to write D1 ADR) is missing entirely from the handoff document.
3. There is an implicit blocking dependency: Team 10 must complete C3 before Team 100 can write D1. This handoff path is not described anywhere.

**Required correction to mandate:**
- Remove the fabricated "Unit Summary Report" task
- Replace Task 4 with the correct Phase D description: "Team 100 authors Pantry ADR (D1) after receiving Team 10's C3 research table; Team 10's Phase D responsibility is to file the C3 output and notify Team 100"
- Update handoff document to document the C3 → D1 handoff between Team 10 and Team 100

---

### Error A3 — Completion report requirements in mandate are incomplete and mislabeled

**Severity:** MEDIUM — affects what Team 10 includes in the completion report; Team 50 will check against the QA mandate (T09, T10) and find it inconsistent.

**File:** `_COMMUNICATION/TEAM_10/MANDATE_V1_1_LOD400_EXEC_TEAM10.md` § 5. Completion Report (items 3–6)

**What the mandate says:**
- Item 3: "Source × unit matrix for eggs (C1)" ← correct
- Item 4: "PRD027 confirmation evidence" ← correct
- Item 5: "basket_tier_resolver.py test output (8 cases, all PASS)" ← correct
- **Item 6: "Pantry ADR file path (C3)"** ← WRONG — C3 is Blueberries, not Pantry ADR; the ADR is not a Team 10 deliverable

**What the QA mandate (G-V1.1) checks:**
- T08: Source × unit matrix for eggs ← present in mandate item 3 ✓
- **T09: Source × unit matrix for passion fruit (PRD072) with per-source classification** ← MISSING from mandate completion items
- **T10: Blueberries research table (PRD086)** ← MISSING from mandate completion items
- T12: Pantry ADR ← this is a Team 100 deliverable, not a Team 10 completion item

**Required correction:** Add two missing items to mandate completion report requirements:
- Passion fruit source × unit matrix (C2) with per-source classification
- Blueberries research table (C3) with grams_if_known column

Remove incorrect "Pantry ADR file path (C3)" from Team 10 completion items. Replace with a note that D1 is produced by Team 100 after receiving C3 output.

---

## Section B — Open Questions (require Nimrod direction or explicit policy)

These are genuine ambiguities not resolvable from the current document set. Each has a proposed default from Team 100 that Nimrod can accept or override.

---

### Question B1 — SRC_WA registration: who creates the migration and when?

**Context:** The LOD400 spec A4.2 (WhatsApp Protocol) says:
> `source_id` = community WhatsApp source (register SRC_WA in migration if not present)

And the A4.3 psql INSERT example uses `WHERE s.source_code = 'SRC_WA'`.

The migration that registers this source has not been assigned. Options:

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **Option 1** | Include SRC_WA `INSERT` in migration 072 alongside the alias batch | Single migration deployment | Mixes catalog data with source registration |
| **Option 2** | Separate migration 073 specifically for SRC_WA | Clean separation of concerns | Extra migration step |
| **Option 3** | Team 10 seeds SRC_WA directly via admin UI `/sources/new` (no migration) | No Team 20 involvement | Not reproducible; not in migration history |

**Team 100 proposed default:** Option 1 — include in migration 072. The alias batch migration is already the first required step in Phase A; adding SRC_WA registration there avoids an extra migration and keeps the deployment atomic.

**Question for Nimrod:** Accept Option 1, or prefer Option 2 for cleaner separation?

---

### Question B2 — Phase D Pantry ADR: should Team 100 write it during this release cycle?

**Context:** The LOD400 spec explicitly assigns D1 (Pantry ADR) to Team 100 as an output of this release. The spec even specifies the exact file path and content structure. However:

- Team 100 needs Team 10's C3 blueberry research table as input.
- The ADR is spec-only (no code). The G-V1.1 QA gate T12 only checks that "ADR document present with chosen approach."
- If Team 100 delays the ADR until after G-V1.1, the gate will fail on T12 (MEDIUM priority — not automatically fatal, but needs a waiver).

**Options:**

| Option | Description |
|--------|-------------|
| **Option A** | Team 100 writes D1 ADR as part of this release cycle, after Team 10 delivers C3 research table. D1 is included in the completion package. (Spec-compliant.) |
| **Option B** | Defer D1 ADR to a separate Team 100 work item after G-V1.1. T12 granted a MEDIUM-priority waiver with Team 100 sign-off. (Requires explicit waiver.) |

**Team 100 proposed default:** Option A — this is what the spec intends. Team 100 can author D1 quickly once Team 10's C3 table is available (estimated < 0.5 session effort). The spec content is pre-defined and the preferred option (Approach B — product_variants table) is already decided in ARCH-20260406-CQ-MASTER.

**Question for Nimrod:** Accept Option A (Team 100 authors D1 in this cycle), or grant a T12 waiver and defer?

---

### Question B3 — "Unit Summary Report" (Phase D in mandate): real deliverable or fabrication?

**Context:** The mandate Task 4 specifies a "Unit Summary Report" assigned to Team 10 — a document covering all unit strings in `normalized_observations` grouped by product. This deliverable does **not appear in** the LOD400 spec, the consolidated mandate, or the CQ master approval.

**Options:**

| Option | Description |
|--------|-------------|
| **Option A** | Remove it — it was fabricated, no spec authority. Mandate is corrected to match spec. |
| **Option B** | Retain it as an additional (non-CQ, non-spec) deliverable: Nimrod wants this report. Explicitly acknowledge it as an enhancement beyond the spec, assign it, and add it to completion report requirements. |

**Team 100 proposed default:** Option A — remove. If Nimrod finds it valuable, it can be added with explicit scope acknowledgment. Including it without spec authority creates ambiguity for Team 50 and Team 190 (they will not know whether to evaluate it).

**Question for Nimrod:** Remove (Option A) or retain as an explicitly scoped extra deliverable (Option B)?

---

### Question B4 — GLOSSARY.md: should it be updated before implementation begins?

**Context:** `docs/GLOSSARY.md` is at version 1.1 (2026-03-31). It does not include the following terms that will be introduced or formalized in v1.1.0:

| Missing term | Notes |
|---|---|
| `pending_manual` | New `extraction_status` value for WhatsApp-submitted data |
| `SRC_WA` | Community WhatsApp submission source (new source_code) |
| `basket_tier_resolver` | New normalizer module (new named component) |
| `resolve_basket_tier()` | New public function (new named API) |
| Team 190 | Not in the Team Terms table in glossary |
| `G-V1.1` | New gate designation (not in glossary) |
| Pantry ADR / `product_variants` | Upcoming ADR terminology |

Team 100 is the maintainer of GLOSSARY.md. Updating it now (before implementation) reduces the risk of terminology drift.

**Options:**

| Option | Description |
|--------|-------------|
| **Option A** | Update GLOSSARY now — Team 100 adds the above terms before signaling Team 10 to start. |
| **Option B** | Update GLOSSARY as part of the v1.1.0 Phase C documentation step (post-gate, pre-version-bump). |

**Team 100 proposed default:** Option B — GLOSSARY updates are part of the milestone documentation phase (Phase C in the release flow). Adding them mid-implementation is fine as long as Team 10 has the spec as reference. This avoids a blocking pre-work item.

**Question for Nimrod:** Accept Option B (GLOSSARY update at milestone close), or prefer Option A (update now)?

---

## Section C — Non-Blocking Observations (no decision required)

These do not block implementation but are flagged for completeness.

### C1 — Team 10 ONBOARDING.md is stale

`_COMMUNICATION/TEAM_10/ONBOARDING.md` Active Mandate table still lists M7 as "PENDING Nimrod approval." It does not reference the current active mandate `MANDATE_V1_1_LOD400_EXEC_TEAM10.md`. This is cosmetic and does not affect implementation (the mandate and handoff are the authoritative guides), but a new Team 10 agent reading ONBOARDING first may be confused.

**Recommendation:** Team 100 updates this file as part of milestone close documentation (not now).

### C2 — Canonical Program Brief bibliography is incomplete

`_COMMUNICATION/TEAM_100/CANONICAL_PROGRAM_BRIEF_PHASES_A_B_TEAM100.md` § 5.2 does not list the Phase A LOD400 spec, the LOD400 execution mandate, or the orchestration handoff. These were produced after the brief was last updated (2026-04-07).

**Recommendation:** Update brief § 5.2 at milestone close to add the three new documents.

### C3 — Phase E pipeline command uses non-standard module path

The LOD400 spec and mandate include:
```bash
python -m organic_market_agent scheduler.run_ingestion --run-type manual --normalize
```

The standard invocation in the codebase uses `organic_market_agent.scheduler.run_ingestion` (dotted path). Team 10 should verify the exact working CLI invocation before the Phase B/E runs — the spec may have a notation difference. This is not a blocker; Team 10 verifies at runtime.

---

## Section D — Requested Actions

| # | Action | Owner | Blocking? |
|---|--------|-------|-----------|
| D1 | Correct mandate Phase C (C2 = Passion Fruit, C3 = Blueberries; remove "Basket Alias Remapping") | Team 100 | YES |
| D2 | Correct mandate Phase D (remove "Unit Summary Report"; document Team 100 D1 ADR ownership + C3→D1 handoff) | Team 100 | YES |
| D3 | Correct mandate completion report items (add C2 passion fruit matrix, add C3 blueberries table; remove misattributed Pantry ADR item) | Team 100 | YES |
| D4 | Correct same errors in handoff document (Session 3 and Session 4 sections) | Team 100 | YES |
| D5 | Decide B1: SRC_WA migration ownership (Option 1 proposed) | Nimrod | YES |
| D6 | Decide B2: Phase D Pantry ADR — write in this cycle or defer with waiver (Option A proposed) | Nimrod | YES |
| D7 | Decide B3: "Unit Summary Report" — remove or retain as explicit extra deliverable (Option A proposed) | Nimrod | LOW |
| D8 | Decide B4: GLOSSARY update timing — now or at milestone close (Option B proposed) | Nimrod | LOW |

**Team 10 implementation hold applies until D1–D6 are resolved.**  
D7 and D8 can be decided after implementation starts without blocking it.

---

*Filed by: Team 100 (Architecture)*  
*Date: 2026-04-08*  
*Status: Awaiting Nimrod direction on Section B + Team 100 self-correction on Section A*
