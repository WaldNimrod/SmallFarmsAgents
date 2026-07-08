# ARCHIVE MANIFEST — SFA-S003-P004-WP-CB-UI-TAILS

**Archived:** 2026-06-12 · **By:** team_100 (closure) · **Iron Rule #15 / POST_GATE_ARCHIVE_PROCEDURE**
**Terminal state:** `COMPLETE` / `LOD500_LOCKED`

## Outcome
3 delivery-tier UI tails (render-layer only). Built by team_10 (Claude) on `feat/wp-cb-ui-tails` @ **`c4304f4`**.
- **AC-1** estimate-price chip **infrastructure** (`crops.payload_json.market_estimate` → muted `.cc__price--est`
  `מחיר מוערך` chip, cards+table; live>estimate>none; honest-omit). Data lands later via WP-CB-MARKET-RANGES (team_80).
- **AC-2** deep-provenance: `winning_source_class`→`NI` data-correctness; finding — the `source_classes`→`.srcpill`
  path (`crop_topics.php`) is unused dead code, so no visible pill was dropping; the `pv-*` cue is the real provenance.
- **AC-3** calc parity verified (no change; deltas are intentional/honest).

## Gates
- **L-GATE_S:** PASS_WITH_FINDINGS — team_190 (GPT-5.2 Cursor, non-Claude), commit `77e3ec9`.
- **L-GATE_VALIDATE:** **PASS** — team_190 (Cursor Composer, non-Claude), commit `af8eae4`.
- **Deploy:** FTPS → uPress (`sfa.nimrod.bio`) 2026-06-12, from the Mac (release `15b4a0a`). Production smoke PASS
  (`/crop-book/` 26 live ₪ chips; no errors).

## Archived artifacts
- `team_100/SPEC_2026-06-12_v1.0.0.md` (incl. §8 + §9 remediation)
- `team_100/VALIDATION_MANDATE_team190_LGATE-S_2026-06-12_v1.0.0.md`
- `team_100/BUILD_REPORT_2026-06-12_v1.0.0.md`
- `team_190/WP-CB-UI-TAILS_LGATE-S_VERDICT_v1.0.0.md`
- `team_190/WP-CB-UI-TAILS_LGATE-V_VERDICT_v1.0.0.md`

## Follow-ups (advisory, out of this WP)
- WP-CB-MARKET-RANGES (team_80) populates the `market_estimate` data.
- Optional: wire `crop_topics.php` into `book_crop.php` to render the EX/PR/WR source pill.
