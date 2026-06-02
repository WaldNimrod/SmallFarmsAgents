---
id: SFA-S003-P004-WP-SRV-IDEAS-REGISTER
wp: SFA-S003-P004-WP-SRV-IDEAS — server-side ideas register (proposed, UNAPPROVED — review pool)
gate: L-GATE_E (idea register, not for execution)
status: OPEN (register)
author: team_100
created: 2026-06-02
trigger: "team_00 condition on WP-CB-UI-CLASSB Q4 — UI/client-side only; any server-side change is logged here as an idea, never implemented in the UI WP"
---

# Server-side IDEAS register — provenance-tracked, UNAPPROVED

> team_00 standing rule (2026-06-02): the Class B UI work is **client-side / UI only**. If any build proposes a
> server-side change (new endpoint, schema, search ranking/indexing, query change, ingest change), the builder
> **STOPS and logs it here** with clear provenance — it is an **idea to review**, NOT approved, NOT implemented.
> Each entry must state: source (who proposed it + which WP/session), what + why, blast radius, and status
> (PROPOSED). team_00 later triages into a real WP or rejects. Nothing here ships without its own gate.

## Entries

| # | Idea | Source (provenance) | What / why | Blast radius | Status |
|---|------|---------------------|-----------|--------------|--------|
| SRV-1 | Server-side search ranking / full-text index | team_50 E2E QA 2026-06-02 + team_35 §3.4 suggestions | Current `/search` is `hebrew_name LIKE`; a ranked/fuzzy index would improve relevance + power suggest-as-you-type | search controller + possibly a search index/table | PROPOSED — unapproved |
| SRV-2 | Market graph 90-day / yearly aggregates | team_35 §3.3 `.rangesel` | History API serves ≤28d; 90/year need pre-computed aggregates | ingest/aggregation + history endpoint | PROPOSED — unapproved (UI shows disabled per LOD400 §9 #3) |
| SRV-3 | Account auth backend (login/profile/subscriptions) | team_35 §3.7 account | Real account flows behind the v1 UI shell | new auth subsystem | PROPOSED — unapproved (UI shell only + "בקרוב" per §9 #2) |
| SRV-4 | Market price DATA freshness (mirror has no priced rows) | team_50 F-MKT-002 | Ingest not currently populating `last_price`/`product_prices` on the mirror | OMA ingest / sfa_ingest_push | PROPOSED — unapproved (data/OPS, not UI) |

## Rule for the build (team_10) + QA (team_50)
If during WP-CB-UI-CLASSB build a server-side change seems necessary: do NOT implement it. Append a row here
(PROPOSED + provenance), render the honest UI degrade (empty/disabled state), and continue. team_100 reviews;
team_00 decides whether any becomes a real WP.
