---
id: LICENSE_AUDIT_SFA-S003-P002-WP-C4_v1.0.0
from: team_10 (sfa_build)
date: 2026-05-27
wp: SFA-S003-P002-WP-C4
---

# License / TOS Audit — WP-C4 Web Sources

**Policy:** Store **derived numeric values and classifications only** in PostgreSQL. Do not persist raw prose from sources with restrictive scraping terms.

| Source | Tier | License class | Storage approach | Flag |
|--------|------|---------------|------------------|------|
| UC ANR 164220 | PR | Extension educational | Numeric temps only | OK |
| Purdue HO-186 | PR | Extension educational | Cross-val log only | OK |
| OSU / CSU / UMN frost | PR | Extension educational | Enum `frost_tolerance_class` only | OK |
| UMD B-1 pH | PR | Extension educational | pH numeric only | OK |
| NE Veg Guide | PR | Extension educational | NPK kg/ha + yield context in `note` | OK |
| FAO i0058e | PR | FAO Open Knowledge | Supplement; numeric only if parsed | OK |
| IL MoA / Shaham | NI | Government (IL) | Month flags + Hebrew labels; no full PDF text | OK — Hebrew UTF-8 |
| Vital Seeds | OP | Commercial | Seeds/gram numeric; cite source label | **Review** — commercial site; derived numbers only |
| Osborne / Johnnyseeds fallback | OP | Commercial | Cross-val with Vital; flagged when >20% diff | **Review** |
| UF/IFAS companion | PR | Extension educational | Pair compatibility enum; `evidence_strength=weak` | OK |
| UC Davis Cantwell (K-State mirror) | PR | Extension educational | Storage numerics + ethylene codes | OK |

No source blocked ingestion entirely. Commercial seed sites ingested as OP tier with audit flag per AC-C4-19.
