# Team 190 — Supplemental Information Request: v1.1.0 Preflight Readiness

**Date:** 2026-04-08  
**From:** Team 190 (Package Validation / Constitutional Preflight)  
**To:** Team 100 (Architecture)  
**Status:** INFORMATION REQUEST — no preflight executed  
**Scope reviewed:** `docs/GLOSSARY.md` → `SPEC-20260408-PHASE-A-LOD400` → `MANDATE-20260408-V1-1-LOD400-EXEC` → `HANDOFF-20260408-V1-1-ORCH-TEAM10`

---

## Purpose

Team 190 reviewed the current v1.1.0 execution chain only to refresh role memory,
canonical procedure, final target, and future preflight scope readiness.

At this stage, Team 190 is **not** executing package validation on a completion
bundle. This document requests clarifications needed to avoid future false
PASS/FAIL decisions during the v1.1.0 constitutional preflight.

---

## Team 190 current understanding

1. Team 190 performs **procedural / constitutional preflight** on the final
   completion package before Team 50 QA. Team 190 does **not** replace Team 50
   technical QA and does **not** validate live runtime behavior.
2. For v1.1.0, the future Team 190 handoff is expected only after:
   - all implementation phases are complete,
   - the Team 10 completion report is filed with all required evidence,
   - Team 20 migration state is confirmed,
   - deviations, if any, carry Team 100 approval.
3. The intended release flow remains:
   Team 10 completion bundle → Team 190 preflight → Team 50 QA → G-V1.1.

---

## Clarification requests

### 1. Authoritative source for Phase B and Phase E run commands

The reviewed documents do not align on the exact execution contract:

- `SPEC-20260408-PHASE-A-LOD400` uses
  `python -m organic_market_agent scheduler.run_ingestion --run-type manual --normalize`
  in both B1 and E1.
- `MANDATE-20260408-V1-1-LOD400-EXEC` uses
  `python -m organic_market_agent scheduler.run_ingestion --run-type manual --all-sources`
  followed by `run_normalizer` in Task 2, and
  `python -m organic_market_agent run_ingestion --run-type manual --normalize`
  in Task 5.
- `HANDOFF-20260408-V1-1-ORCH-TEAM10` instructs Team 10 to request Nimrod to run
  `run_ingestion --run-type manual --normalize` plus `run_normalizer`.

**Request:** Team 100 should publish one canonical command set for:
- Phase B full run
- Phase E final run
- whether `run_normalizer` is required as a separate step
- whether `--all-sources` is canonical or redundant

### 2. Authoritative task map for Phases C and D

The three documents diverge materially:

- In the spec:
  - C1 = eggs
  - C2 = passion fruit
  - C3 = blueberries research
  - C4 = `basket_tier_resolver.py`
  - D1 = Pantry ADR authored by Team 100
- In the mandate:
  - C2 = basket alias remapping
  - C3 = Pantry ADR
  - D1 = unit summary report
- In the handoff:
  - C2 = basket alias remapping
  - C3 references blueberry findings for Pantry ADR
  - D1 = unit normalization summary report

**Request:** Team 100 should issue a delta or corrected orchestration document that
aligns Phase C/D task numbering, ownership, and artifact expectations with the
LOD400 spec.

### 3. Authoritative API contract for `resolve_basket_tier()`

There is a direct contract conflict:

- The spec defines `resolve_basket_tier(csa_context_json, price_amount, session) -> tuple[Optional[str], str]`
  with `Optional[str]` input payload semantics and `Decimal` price handling.
- The mandate defines
  `resolve_basket_tier(csa_context_json: dict | None, price_amount: float | None, session: Session) -> str | None`.

This is not a cosmetic mismatch; it changes both function signature and expected
return semantics.

**Request:** Team 100 should confirm the binding API contract in one correction note,
and Team 10 should be instructed to implement only that version.

### 4. Future Team 190 evaluation basis

Because the spec, mandate, and handoff are not fully aligned, Team 190 needs an
explicit review rule for the future completion-package preflight.

**Request:** Team 100 should confirm whether Team 190 must validate the final
completion package against:

1. `SPEC-20260408-PHASE-A-LOD400` only,
2. spec + mandate,
3. spec + mandate + handoff,
4. or spec as primary with mandate/handoff treated as non-binding coordination aids.

### 5. Completion-bundle artifact list expected at Team 190 handoff

The spec completion section lists 11 required items. The mandate and handoff add
or rename artifacts such as a unit summary report and different Phase C/D outputs.

**Request:** Team 100 should publish the exact artifact checklist Team 190 should
expect in the future preflight request, including:
- mandatory files,
- optional files,
- acceptable substitutions when operator actions are manual,
- how approved deviations must be cited.

---

## Interim Team 190 operating position

Until clarification is issued, Team 190 will retain the following provisional view:

- `SPEC-20260408-PHASE-A-LOD400` is the highest-confidence implementation and
  evidence contract for v1.1.0.
- `MANDATE-20260408-V1-1-LOD400-EXEC` and
  `HANDOFF-20260408-V1-1-ORCH-TEAM10` currently contain coordination value but
  should not be used as independent constitutional truth where they conflict with
  the spec.

This provisional position is **not** a final ruling and should be superseded by a
Team 100 clarification artifact.

---

## Requested next step from Team 100

Issue one of the following before Team 10 reaches final preflight:

1. a short delta note resolving the five items above, or
2. corrected versions of the mandate / handoff documents, or
3. a canonical preflight checklist for Team 190 that explicitly resolves document precedence.

---

**Filed by:** Team 190  
**Function:** Constitutional / package preflight readiness review
