# BUILD REPORT — SFA-S003-P004-WP-CB-UI-TAILS — team_10 (Claude Opus) — v1.0.0

**Date:** 2026-06-12 · **Builder:** team_10 (Claude Opus 4.8) · **Gate next:** L-GATE_VALIDATE (external, non-Claude)
**Branch / HEAD:** `feat/wp-cb-ui-tails` @ **`c4304f4`** (pushed to origin; off `origin/main` 609a8d5 + cherry-picked head-start `ab71d9f`)
**Spec built to:** `_COMMUNICATION/TEAM_100/SFA-S003-P004-WP-CB-UI-TAILS/SPEC_2026-06-12_v1.0.0.md` (incl. §8 + §9 remediation)
**L-GATE_S:** PASS_WITH_FINDINGS (team_190 / GPT-5.2 Cursor) — findings folded per §9.

## What was built (render-layer only, `sfa_delivery/`)
| AC | Delivered | Evidence |
|----|-----------|----------|
| **AC-1.1** live chip (slug OR hebrew_name) | adopted head-start `ab71d9f` | `CropBookViewController::entry()`; existing route test |
| **AC-1.2** estimate **infrastructure** | `entry()` reads `crops.payload_json.market_estimate {price_min,price_max,unit}` → muted/dashed `.cc__price--est` chip `מחיר מוערך ₪min–₪max/unit` in **both** cards + table; honest-omit when absent; **live > estimate > none** | `book_entry.php`, `redesign.css .cc__price--est`; tests `testBookIndexEstimateChipFromPayloadWhenNoLivePrice`, `testBookIndexLivePriceWinsOverEstimate` |
| **AC-1.3/1.4** honesty + priority | estimate renders only when `price_min>0` and no live price | tests above |
| **AC-2.1/2.3** provenance | F-UI-01 payload fallback now classifies internal-curated values `'NI'` (→ PR), consistent with the `crop_attribute` path (L982); MISSING stays `''` (AC-2.2); stale comment fixed | `CropBookViewController` buildCb1Fields + the §(b) comment |
| **AC-2.4** | deep payload provenance cue test | `testDeepProvenanceCueFromVarietyPayload` (pv-validated at `depth=deep`) |
| **AC-3** calc parity | `/calc/` already on-DS at desktop+375; deltas are intentional/honest → no change | qa_probe `overflow=false`; screenshots |

## Verification (VC hooks)
- **VC-1 phpunit:** `237 / 237` pass (origin/main 232 + head-start 2 + 3 new), 0 fail.
- **VC-2 validate_aos:** **0 FAIL** (31 PASS / 21 SKIP).
- **VC-3 scope:** 4 files, all `sfa_delivery/` (controller, book_entry, redesign.css, test). No schema/data/pipeline/`_aos`.
- **VC-4 AC-1.*:** route tests cover live / estimated / none + priority + both views.
- **VC-6 AC-3:** `qa_probe.mjs --shots` `/calc/` + `/crop-book/` overflow=false at 375 + 1440.

## ⚠ Finding the validator must weigh (AC-2)
The `source_classes → .srcpill` path the spec/L-GATE_S assumed drives the deep provenance **pill** lives in
`templates/macros/crop_topics.php`, which **`book_crop.php` does not include** — it is **unused dead code**. So no
user-visible pill was dropping. The crop page's real visible field provenance is the **`pv-*` cue** (from
`field_state`), which already works from the payload (the AC-2.4 test asserts it). The `winning_source_class`→`NI`
change is therefore **data-correctness + forward-compat** (it makes `source_classes`, exposed to the template,
accurate rather than spuriously empty) — not a new visible pill. **No fabrication** under any branch. A separate
follow-up (wire `crop_topics` into `book_crop.php`) would be needed to render the EX/PR/WR srcpill on the page.

## Not done (out of scope / honest)
- The `market_estimate` DATA is empty in production until **WP-CB-MARKET-RANGES** (team_80) delivers — the chip
  stays honestly empty until then (AC-1.2 is the render infra; tests prove it with a fixture).
- AC-3 made no code change (parity already met; forcing the mockup's 15-grid / date-calc hint would regress the
  shipped calc decisions + honest stub marking).
