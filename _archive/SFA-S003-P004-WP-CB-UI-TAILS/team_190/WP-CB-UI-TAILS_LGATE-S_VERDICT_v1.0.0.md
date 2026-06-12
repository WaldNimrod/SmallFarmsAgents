---
id: VERDICT_SFA-S003-P004_WP-CB-UI-TAILS_L-GATE_S_v1.0.0
from: team_190
to: team_100
cc:
  - team_00
  - team_10
  - team_50
date: 2026-06-12
type: validation_verdict
wp: SFA-S003-P004-WP-CB-UI-TAILS
gate: L-GATE_S
validator_engine: GPT-5.2 (Cursor, non-Claude)
result: PASS_WITH_FINDINGS
authorize_build: true
---

# Verdict — SFA-S003-P004-WP-CB-UI-TAILS — L-GATE_S

```yaml
wp: SFA-S003-P004-WP-CB-UI-TAILS
gate: L-GATE_S
validator_engine: GPT-5.2 (Cursor, non-Claude)
result: PASS_WITH_FINDINGS
rootcause_checks: 3/3
precision_checks: 3/4
constitutional_checks: 4/4
findings:
  - id: F-190-TAILS-S-01
    severity: MAJOR
    summary: "Item-1 pin naming is inconsistent: the cited L578–L585 market_link attach is in crop detail (`bookCrop()`), not the crop-book list `entry()` that actually drives the `.cc__price` chip. This risks mis-implementing AC-1.2 in the wrong route."
    evidence: "sfa_delivery/app/Controllers/CropBookViewController.php:210-226 (entry() price map) + 578-588 (bookCrop() market_link attach)"
    disposition: fix-inline
  - id: F-190-TAILS-S-02
    severity: MAJOR
    summary: "Item-2 is directionally correct but under-specified: the current default-variety payload fallback stamps `winning_source_class` as empty, so Deep `srcline` pills cannot appear when the mirror lacks provenance. The spec should name the exact payload key(s) that carry per-field provenance so a junior builder does not guess."
    evidence: "sfa_delivery/app/Controllers/CropBookViewController.php:892-905 + 1022-1052"
    disposition: builder-acknowledge
  - id: F-190-TAILS-S-03
    severity: MINOR
    summary: "AC-1.2/§4.1 mention an estimated chip and a CSS modifier (e.g. `.cc__price--est`), but do not explicitly state whether the estimate must appear in BOTH views (cards + table) or cards only. Clarify to keep tests + UI behavior deterministic."
    evidence: "sfa_delivery/templates/pages/book_entry.php:143-205"
    disposition: builder-acknowledge
authorize_build: true
summary: "PASS_WITH_FINDINGS. The WP is scoped correctly to `sfa_delivery/` and the three root causes are real: price-chip needs a non-product fallback, Deep provenance pills drop when mirror provenance is absent, and `/calc/` needs mockup alignment. The only risks are precision gaps (pin/method naming for Item-1; and missing explicit payload provenance key for Item-2). These are fixable without changing the WP’s architecture; build may proceed with the findings acknowledged and tightened in the build LOD."
```

