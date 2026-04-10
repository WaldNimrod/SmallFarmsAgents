# SFA — Post-M9 Product Direction (LOD200)

| Field | Value |
|-------|--------|
| **Package ID** | `SFA-PKG-POST-M9-001` |
| **Version** | 1.0.0 |
| **Date** | 2026-04-11 |
| **LOD** | 200 (concept + requirements + acceptance at package level) |
| **Status** | **SUBMITTED** — pending **Team 190** review, then Team 100 sign-off for execution planning |
| **phase_owner** | Team 100 (Architecture) |
| **correction_cycle** | — (initial issuance) |
| **Repository** | SmallFarmsAgents (OrganicMarketAgent) |
| **Canonical copy** | [`../../TEAM_100/specs/SFA_POST_M9_PRODUCT_DIRECTION_LOD200_v1.0.0.md`](../../TEAM_100/specs/SFA_POST_M9_PRODUCT_DIRECTION_LOD200_v1.0.0.md) |

---

## 1. Purpose

Realign the **post-M9** program after closure of site optimization (G9): freeze obsolete planning bundles, define **two concrete product tracks** for future implementation, and bind **operational feedback** from the home server to this codebase without mixing non-SFA products.

This package **does not** mandate code changes by itself; it authorizes follow-on mandates (Team 100 → Team 10/20) once **Team 190** completes package review per project governance.

---

## 2. Binding decisions (Nimrod / Team 100 — 2026-04-11)

| ID | Topic | Decision |
|----|--------|----------|
| **D1** | Roadmap hygiene in **Agents OS** | Versioning and procedure updates for the **canonical roadmap** live in the **AOS workspace**; an updated procedure will be published there. **Not** a deliverable of the SmallFarmsAgents app repo beyond cross-links. |
| **D2** | **M9C** (blog + community engagement) | **Out of scope for Team 10 (Feature Dev)**. Owned by **Team 80** + **Nimrod** approval. |
| **D3** | **Team 61 — SFA operational feedback** | The **MSG-011** RFI may be **re-sent** only after confirming no reply in **`~/Documents/_agent_comm/inbox/`** following a **pull** from the server **`~/agent_comm/outbox/`** (see [`documentation/05-admin-and-operations/WALD_HOME_SERVER_AGENT_COMMUNICATION.md`](../../../documentation/05-admin-and-operations/WALD_HOME_SERVER_AGENT_COMMUNICATION.md) §3.1). Substantive status content exists in **`MSG-20260410-004-REPORT.md`** when the inbox has been synced from the server. |
| **D4** | **Legacy M10 bundle** (old Items 8–10: WP farmer roles, FarmCostAgent concept, in-page form spec) | **FROZEN.** Not relevant to current system direction; **no execution** until explicitly thawed by Team 100. |
| **D5** | **User contribution (replaces first phase of prior “farmer layer” vision)** | **Phase 1:** **Any registered user** may **submit content** (structured contribution) that passes through **moderation** before publication or ingestion into the public index narrative. The previous multi-role ladder (`pending_farmer` / `farmer` / etc.) is **not** required for this phase. Detailed roles may follow in a later phase after moderation is proven. |
| **D6** | **Farmer value tool (replaces “Phase 3 AI” for first implementation)** | **Phase 1:** implement a **simple calculator or equivalent UI** that helps a farmer **compute product economics correctly** (e.g. unit price, margin, cost allocation) — **deterministic**, **no personal AI agent**, no conversational layer in this phase. Profiles/compare/advanced AI remain **out of scope** until a later milestone. |

---

## 3. Work packages (execution-facing)

### WP-A1 — Moderated submissions (registered users)

| Attribute | Description |
|-----------|-------------|
| **Goal** | Trusted path from **registered user** → **moderator review** → accepted/rejected artifact. |
| **Primary outcomes** | Submission schema; authentication linkage; moderation queue UX; audit trail; alignment with [`docs/PRIVACY_POLICY.md`](../../../docs/PRIVACY_POLICY.md). |
| **Non-goals (v1)** | Full farmer certification, complex RBAC, public edit of live index rows without review. |
| **Owner (next)** | Team 100 **ARCH** + Team 10 implementation mandate after gate approval. |

### WP-A2 — Farmer economics calculator (no AI)

| Attribute | Description |
|-----------|-------------|
| **Goal** | Deliver **clear value** with minimal surface: inputs → outputs (Hebrew RTL), documented formulas, no ML. |
| **Primary outcomes** | Spec for calculation rules; UI placement (public static page and/or linked from SmallFarmsAgent); accessibility per [`docs/RTL_DEVELOPMENT_GUIDE.md`](../../../docs/RTL_DEVELOPMENT_GUIDE.md). |
| **Non-goals (v1)** | AI recommendations, conversational agent, saved multi-farm profiles. |

---

## 4. Package-level acceptance (Team 190)

Team 190 SHALL verify:

| PAC | Criterion |
|-----|-----------|
| **PAC-01** | Decisions D1–D6 are internally consistent and do not contradict `PRIVACY_POLICY.md` intent. |
| **PAC-02** | WP-A1 and WP-A2 have testable goals and explicit non-goals. |
| **PAC-03** | Legacy M10 freeze is explicit so implementers do not start frozen items. |
| **PAC-04** | Team 61 feedback path is actionable (WALD doc §3.1 — pull from server `outbox`). |
| **PAC-05** | `ROADMAP.md` references this package ID after merge. |

---

## 5. Out of scope (this package)

- Implementation code, migrations, and QA test plans (separate mandates after **L-GATE_S** / Team 100 approval).
- **Famely Neusletter**, **TikTrack**, and other non-SFA repositories.
- **AOS** roadmap YAML edits (separate workspace).

---

## 6. References

| Document | Role |
|----------|------|
| [`_COMMUNICATION/ROADMAP.md`](../../ROADMAP.md) | Updated to v5.x — program focus |
| [`documentation/external-references/CROSS_PROJECT_BOUNDARIES.md`](../../../documentation/external-references/CROSS_PROJECT_BOUNDARIES.md) | Repo scope |
| [`_COMMUNICATION/TEAM_80/sfa_handoff_v2/03_farmer_layer.md`](../../TEAM_80/sfa_handoff_v2/03_farmer_layer.md) | Historical vision — **superseded for phase ordering** by §2 D5 |
| [`_COMMUNICATION/TEAM_80/smallfarms_agent_handoff/07_roadmap.md`](../../TEAM_80/smallfarms_agent_handoff/07_roadmap.md) | Historical tools vision — **superseded for first tool** by §2 D6 |

---

## 7. Submission record

| Field | Value |
|-------|--------|
| **Submitted to** | Team 190 (constitutional / package review) |
| **Next** | Team 190 findings → Team 100 amendment or execution mandates |

---

*End of LOD200 package.*
