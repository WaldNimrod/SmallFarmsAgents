# M13 data snapshot + M10.4/M10.5 freeze record (Team 10)

**Date:** 2026-04-06  
**From:** Team 10 (Feature Dev)  
**To:** Team 50 (QA), Team 100 (Architecture), Nimrod (product)  
**Purpose:** Evidence for **G11** / M13 forward motion and documentation of **frozen** M10.4/M10.5 scope per Nimrod direction.

---

## 1. Product direction (summary)

- **M10.4 + M10.5:** Frozen **as-is** — additional sources collected; original LOD/QA targets for these sub-phases are **not** pursued further at this time. **Final G10 closure** on M10.4/M10.5 is **deferred** to a future optimization milestone (see ROADMAP v5.4).
- **M13-PRE:** Original **hard blocking** criteria (G-PRE-1..7) are **waived** as gate blockers via addendum; Team 50 may still validate and issue **PASS / CONDITIONAL PASS** on **G11** with explicit waivers.
- **M13:** Proceed to completion on **current** publish reality; privacy rules remain **binding**.

---

## 2. Publish snapshot (local run, authoritative DB)

Captured immediately before this report:

| Metric | Value |
|--------|------|
| `run_publisher` | Success |
| `public_report.json` products | **76** |
| `report_schema_version` | **3.0** |
| `manifest.json` schema_version | **3.0** |
| `manifest.community_sources` (rolling window context) | **22** |

**Waiver note (G11 / legacy M13-PRE G-PRE-5):** Published product count is **below 90**. Nimrod accepts advancing M13; Team 50 should record **CONDITIONAL PASS** or explicit waiver on mandate T06 / G11 checklist item **product_count >= 90** if still literal in QA text.

Publish viability: **≥2 distinct community sources** in rolling window (engine rule) — satisfied (22 sources in manifest snapshot).

---

## 3. SQL evidence (same DB)

### 3.1 CSA sources — raw rows on last fetch per source

| Code | raw_extracted_items (last run) |
|------|-------------------------------|
| SRC033 | 3 |
| SRC034 | 2 |
| SRC035 | 0 (parser policy: no stable basket SKUs on entry URL) |

**G-PRE-3 (informational):** 2 of 3 CSA sources with data — **met** for “≥2 of 3”.

### 3.2 SRC036 (retail) — resolution snapshot

Query: normalized vs unresolvable on linked REI for SRC036 (all runs in join — indicative).

| Code | normalized | unresolvable | pct |
|------|------------|--------------|-----|
| SRC036 | 75 | 0 | 100.0% |

*(If Team 50 uses a stricter per–last-run only slice, they may attach their own query output.)*

### 3.3 mypips priority set (sample)

Normalized row counts observed for subset of priority codes (any successful runs):

| Code | normalized REI count |
|------|---------------------|
| SRC041 | 124 |
| SRC053 | 113 |
| SRC060 | 56 |
| SRC061 | 61 |
| SRC070 | 116 |

Other codes in the 9-source set may be inactive or empty on this DB; **M10.4 is frozen** — no mandate to reach “5 of 9” for M13 unblock.

---

## 4. M13 implementation status (codebase — Phase A/B)

Already in repo (for G11 verification):

- Publisher v3: `details`, `price_series`, variants, CSA merge + sanitization (incl. phone strip), manifest 3.0.
- Public templates: accordion, Chart.js, filters including **baskets**, RTL-oriented chart.
- Admin: CSA drill-down on basket product detail (full internal `csa_context`).

---

## 5. References

- ROADMAP v5.4 (M10 freeze, G10 deferral, M13-PRE addendum pointer)
- `_COMMUNICATION/TEAM_10/MANDATE_M13_PRE_DATA_FOUNDATION_TEAM10_ADDENDUM.md`
- `2026-04-06_QA_REQUEST_G11_M13_TEAM10.md` (updated waivers)

---

*End of snapshot — regenerate numbers after major ingestion if re-baselining G11.*
