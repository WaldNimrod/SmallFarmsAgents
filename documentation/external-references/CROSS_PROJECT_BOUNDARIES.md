# Cross-project boundaries (MyFarmAgents ecosystem)

**Applies to:** Agents working in the **SmallFarmsAgents** git repository.

## What this repository is

**SmallFarmsAgents** is the **OrganicMarketAgent (SFA)** codebase: Python package `organic_market_agent`, PostgreSQL schema, admin UI, collectors, publisher, WordPress integration for the **community vegetable price index** on nimrod.bio.

## What this repository is not

It is **not** the home repository for:

| Product | Typical location |
|---------|------------------|
| **Famely Neusletter** | Separate clone on waldhomeserver / Mac (e.g. `famely-neuslettr` or name chosen by Nimrod) — builds static HTML under `/agents/newsletter/` on nimrod.bio |
| **TikTrack** | Own repository and systemd units on the server |
| **Agents OS** (`agents-os`) | Own repository; dashboards/APIs on other ports |

## How confusion happened (root cause)

1. **Shared infrastructure:** nimrod.bio, uPress, waldhomeserver, Team 61 inbox, and `~/Documents/_agent_comm/` are **shared** across products.
2. **Team numbering:** Team 80 “Product & Strategy” can advise multiple products; `_COMMUNICATION/TEAM_80/` **in this repo** was interpreted as “all Team 80 output,” but it is only **SFA-relevant** material for **this** tree.
3. **Session context:** A request about the **newsletter** was executed while the **workspace root** was SmallFarmsAgents, so deliverables landed in the wrong git history.

## Required behavior for agents

1. **Default scope:** In this workspace, implement and document **SFA** unless the user explicitly switches root or names another repo.
2. **Non-SFA tasks:** Provide analysis in chat, or write files under **`~/Documents/_agent_comm/outbox/`** for Team 61, or ask Nimrod to open the **correct repository** in Cursor before creating tracked files.
3. **No silent cross-product commits:** Do not add CHANGELOG entries for other products’ releases into **this** `CHANGELOG.md` except cross-cutting platform notes approved by Team 100.

## Coordination without mixing repos

- **File handoff:** [`WALD_HOME_SERVER_AGENT_COMMUNICATION.md`](../05-admin-and-operations/WALD_HOME_SERVER_AGENT_COMMUNICATION.md) — machine paths, not product-specific.
- **Communication hub:** [`_COMMUNICATION/README.md`](../../_COMMUNICATION/README.md) — templates and gates for **this** repo’s process.

---

*Team 100 alignment — 2026-04-10 corrective note.*
