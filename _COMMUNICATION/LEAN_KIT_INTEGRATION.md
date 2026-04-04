# Lean Kit Integration — SmallFarmsAgents

**Version:** 1.0.0  
**Date:** 2026-04-05  
**Authority:** S003-P019 Phase 2 — Pilot WP `SFA-P001-WP001`  
**Authoring team:** Team 170 (Lean overlay documentation)

This document is the master integration guide for adopting the **Lean Kit** as a **methodology overlay** on top of SmallFarmsAgents’ existing governance (`ROADMAP.md`, `_COMMUNICATION/`, G-gates, Phase A/B/C). It does not replace SFA processes; it adds a parallel Lean view so every team can execute with shared language for gates, specs, and validation.

---

## 1. What is the Lean Kit

The Lean Kit is a lightweight, documentation-first methodology layer maintained in the **agents-os** repository. It describes how work packages (WPs) move through **Lean gates** (L-GATE_*), how roles map to teams, and how **cross-engine validation** enforces quality at the final gate. For SmallFarmsAgents we use **profile L0**: no Agents OS engine snapshot is required—only the YAML roadmap, team assignments, and methodology documents that live beside your normal milestones.

Think of the Lean Kit as a **shared playbook** for “what stage is this work in?” and “who validates before we call it done?” It uses familiar ideas—eligibility, concept, spec authorization, build, validate—but names them consistently so architecture (Team 100), feature and infra builders (Teams 10/20), QA (Team 50), and the project lead stay aligned. The kit is intentionally **non-invasive**: your milestone gates (Gₙ), QA mandates, and CHANGELOG discipline remain the source of truth for delivery; Lean adds a thin tracking layer for the pilot and future WPs.

In day-to-day terms, the Lean Kit gives you **one place in agents-os** (`projects/sfa/`) where the pilot WP, its spec reference, and gate history are recorded. That makes it easy for any session—Cursor, OpenAI, or human—to open the same facts without hunting through chat history.

---

## 2. Why SmallFarmsAgents at M10 (overlay rationale)

SmallFarmsAgents is adopting the Lean Kit at **M10 — Source Expansion & Data Quality** because M9 site optimization is closed and the program is at a natural **inflection point**: multiple parallel tracks (dictionary, parsers, headless browsing, sources) need clear ownership and validation without rewriting how SFA already runs Phase A/B/C and G-gates.

The **overlay** model means: we **do not** migrate ROADMAP.md into agents-os, and we **do not** change folder ownership under `_COMMUNICATION/`. We **add** Lean terminology and a pilot WP (`SFA-P001-WP001`) whose deliverables are **these onboarding documents**—proving the overlay can land without touching application code. That minimizes risk to collectors, DB migrations, and production pipelines while still giving every team an activation path for the next Lean-gated WPs after M10.

M10 is also where **architecture (Team 100)** and **execution teams** coordinate intensely; having a single Lean integration guide plus per-team activation prompts reduces ramp time when new WPs are cut from the milestone plan.

---

## 3. Team role map (SFA → Lean)

Canonical mapping from `agents-os/projects/sfa/team_assignments.yaml`:

| SFA team / ID | Lean role | Engine | Responsibility (summary) |
|---------------|-----------|--------|----------------------------|
| **sfa_team_100** (SFA Architecture / Team 100) | SPEC_AUTHOR | cursor | Spec authority: LOD200/LOD400 for Lean WPs; concept and spec gates |
| **sfa_team_10** (SFA Feature Dev / Team 10) | ORCHESTRATOR | cursor | Routes WPs, task flow within milestones; build gate execution for feature work |
| **sfa_team_20** (SFA Infrastructure / Team 20) | IMPLEMENTATION_TEAM | cursor | Infra WPs: DB, Alembic, Docker; build gate with self-QA |
| **sfa_team_50** (SFA QA / Team 50) | CONSTITUTIONAL_VALIDATOR | openai | Cross-engine validator: L-GATE_V; Phase B / G-gate QA unchanged in substance |
| **nimrod** (Project lead) | ARCH_APPROVER | human | Human approval at L-GATE_S and ratification at L-GATE_V |

**cross_engine_validator:** `sfa_team_50` — mandatory different engine from Cursor builders for Lean validation.

---

## 4. Lean Gate Model for SFA (Track B)

Pilot WP `SFA-P001-WP001` uses **Track B** (concept gate included):

```
L-GATE_E  →  L-GATE_C  →  L-GATE_S  →  L-GATE_B  →  L-GATE_V
(eligible)   (concept)    (spec+auth)   (build)      (validate)
```

| Gate | Meaning for SFA |
|------|------------------|
| **L-GATE_E** | Eligibility — WP is safe to track; low risk or scoped correctly |
| **L-GATE_C** | Concept approved (Track B) — approach agreed before full spec |
| **L-GATE_S** | Spec + authorization — LOD200 (or equivalent) approved; execution allowed |
| **L-GATE_B** | Build complete — deliverables exist; builder self-QA done |
| **L-GATE_V** | Validate — **sfa_team_50** (OpenAI) checks package vs acceptance criteria; Iron Rule enforced |

SFA’s **Phase A (implementation)** maps closely to work up to and including **L-GATE_B**. **Phase B (QA)** and **Gₙ PASS** align with **L-GATE_V** and sign-off. See also `agents-os/projects/sfa/MILESTONE_MAP.md` for milestone ↔ Lean equivalence.

---

## 5. Pilot WP: SFA-P001-WP001

**ID:** `SFA-P001-WP001`  
**Label:** Lean Kit Integration Guide — `LEAN_KIT_INTEGRATION.md`  
**Purpose:** Deliver this integration guide plus four **team activation prompts** (Teams 100, 10, 20, 50) under `_COMMUNICATION/`, so every SFA team can start Lean execution immediately.

| Actor | Role in this pilot |
|-------|---------------------|
| **Team 170** | Authored PD1–PD5 (documentation build on Cursor) |
| **Team 100 (SFA)** | SPEC_AUTHOR — owns future LOD specs for WPs; consumes integration + activation |
| **Team 10** | ORCHESTRATOR — routes execution; uses activation for gate expectations |
| **Team 20** | IMPLEMENTATION_TEAM — infra track; uses activation for L-GATE_B expectations |
| **Team 50** | CONSTITUTIONAL_VALIDATOR — runs **L-GATE_V** validation (OpenAI) using `LEAN_KIT_ACTIVATION_TEAM50.md` |
| **Nimrod** | ARCH_APPROVER — ratifies Team 50 result; final roadmap closure per mandate |

**What this proves:** The overlay can ship **documentation-only** pilot output with **no application code changes**, committed on **SmallFarmsAgents `main`**, while agents-os records gate progression in `projects/sfa/roadmap.yaml`.

---

## 6. Where to find Lean Kit docs (agents-os paths)

Use a local clone of **agents-os** (example root: `/Users/nimrod/Documents/agents-os/`). Primary paths:

| Path | Content |
|------|---------|
| `projects/smallfarmsagents.yaml` | Project registry entry for SmallFarmsAgents |
| `projects/sfa/roadmap.yaml` | Pilot WP, `current_lean_gate`, `gate_history`, `spec_ref` |
| `projects/sfa/team_assignments.yaml` | Teams, engines, Lean roles, Iron Rule note |
| `projects/sfa/MILESTONE_MAP.md` | SFA milestone ↔ Lean gate mapping |
| `projects/sfa/SFA_P001_WP001_LOD200_SPEC.md` | LOD200 spec for the pilot WP |
| `projects/sfa/LESSONS_LEARNED.md` | Phase 1 lessons |
| `lean-kit/examples/example-project/roadmap.yaml` | Format reference (note: `lod_status` comment in `projects/sfa/roadmap.yaml` follows mandate verbatim) |
| `lean-kit/templates/` | Optional templates for terminology alignment |

**Spec reference for Phase 2 acceptance:** `agents-os/projects/sfa/SFA_P001_WP001_LOD200_SPEC.md` §3–§4 (sections PAC-01..PAC-06 baseline; Phase 2 mandate extends PAC-07..PAC-10 operationally).

---

## 7. Iron Rule — cross-engine validation

**Rule:** Work built primarily on **Cursor** (Teams **10** and **20**) must be validated at **L-GATE_V** by **sfa_team_50** on **OpenAI** — a **different engine**. This is **not optional** and **not waivable** for Lean-tracked WPs.

**Why OpenAI for Team 50:** It guarantees an independent toolchain and review style from the builders, reducing blind spots and aligning with the Lean Kit’s constitutional validator pattern. Team 50’s existing QA mandates (Phase B, integration, data quality, E2E) remain; L-GATE_V is **additive** documentation and checklist discipline, not a replacement.

**If spec is not met:** Team 50 must record **FAIL** or **PASS_WITH_FINDINGS** with evidence paths; builders address findings before ARCH_APPROVER ratifies closure.

---

## References

- S003-P019 Phase 2 mandate (Team 100 → Team 170), v1.0.1  
- `TEAM_00_LOD200_S003_P019_SMALLFARMSAGENTS_LEAN_ONBOARDING_v1.0.0.md` (Phoenix governance)  
- `SmallFarmsAgents/_COMMUNICATION/ROADMAP.md` — active milestone M10
