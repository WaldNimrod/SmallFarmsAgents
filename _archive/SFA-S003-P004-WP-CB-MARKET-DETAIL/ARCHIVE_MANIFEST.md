# ARCHIVE MANIFEST — SFA-S003-P004-WP-CB-MARKET-DETAIL

**Archived:** 2026-06-12 · **By:** team_100 (closure) · **Iron Rule #15 / POST_GATE_ARCHIVE_PROCEDURE**
**Terminal state:** `COMPLETE` / `LOD500_LOCKED`

## Outcome
`/market/{slug}` re-skinned from Class-B v2 to the redesign DS (render-layer only). Built by team_10 (Claude) on
`feat/wp-cb-market-detail` @ **`58a2023`**.
- **AC-1** DS re-skin (`.pcard` hero / DS graph / history table / stats; new `.md*` section in `redesign.css`).
- **AC-2** emoji-fold (`📦📭📊📖◐` → `.gi` glyphs). **AC-3** watercolor hero via `$product['wc_art']` (no controller
  change — the §8 correction). **AC-4** `.fresh.f/.a/.s`. **AC-5** `90י/שנה` disabled `בקרוב` (team_00 LOCKED).
  **AC-6** empty-state clean. **AC-7** crop-book xlink + LOCKED disclaimer preserved.
- Trend colors fixed to the price-index convention (rising=red, falling=green).

## Gates
- **L-GATE_S:** PASS_WITH_FINDINGS — team_190 (GPT-5.2 Cursor, non-Claude), commit `77e3ec9`.
- **L-GATE_VALIDATE:** **PASS** — team_190 (Cursor Composer, non-Claude), commit `af8eae4`.
- **Deploy:** FTPS → uPress (`sfa.nimrod.bio`) 2026-06-12, from the Mac (release `15b4a0a`). Production smoke PASS
  (`/market/prd017`,`/market/prd018`: re-skin live, AC-5 `בקרוב`, zero emoji, zero Class-B, no errors).

## Archived artifacts
- `team_100/SPEC_2026-06-12_v1.0.0.md` (incl. §8 + §9 remediation) · `team_100/BRIEF_register_2026-06-08_v1.0.0.md`
- `team_100/VALIDATION_MANDATE_team190_LGATE-S_2026-06-12_v1.0.0.md` · `team_100/BUILD_REPORT_2026-06-12_v1.0.0.md`
- `team_190/WP-CB-MARKET-DETAIL_LGATE-S_VERDICT_v1.0.0.md` · `team_190/WP-CB-MARKET-DETAIL_LGATE-V_VERDICT_v1.0.0.md`

## Follow-up (advisory, out of this WP)
- Spawned background task: physically retire the now-dead Class-B blocks (`.pbig/.pgraph/.pstats/.pdetail/.phist/
  .emptybox/.fresh--*`) from `classb.css` (keep the shared `.spark`; re-run all Class-B routes through qa_probe).
