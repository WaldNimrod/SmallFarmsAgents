---
id: WP-CB-UI-WI7_LGATE-V_VERDICT_v1.0.0
type: VERDICT
gate: L-GATE_V
from: team_190
to: team_100
cc:
  - team_00
  - team_10
  - team_50
  - team_99
date: 2026-06-11
project: smallfarmsagents
wp: SFA-S003-P004-WP-CB-UI-WI7
subject: WI7 render-layer polish survivability validation at origin/main d259580 + live site
mandate_dir: _COMMUNICATION/team_100/SFA-S003-P004-WP-CB-UI-WI7/
build_report: _COMMUNICATION/TEAM_10/SFA-S003-P004-WP-CB-UI-WI7/BUILD_REPORT_v1.0.0.md
validator_engine: Cursor Agent (GPT-5.5 — non-Claude)
phase_owner: team_190
---

# L-GATE_V Verdict — SFA-S003-P004-WP-CB-UI-WI7

## Engine Attestation

**Validator:** team_190, Cursor Agent (GPT-5.5 — non-Claude).  
**Builder:** team_10, Claude/Sonnet on `claude/ui-polish-hub-cropbook-2026-06-03`.

This satisfies Iron Rule #1 and Iron Rule #5: the constitutional validator is independent from the builder engine, and this verdict is issued by team_190.

## Verdict

```yaml
wp: SFA-S003-P004-WP-CB-UI-WI7
gate: L-GATE_V
result: PASS_WITH_FINDINGS
validated_code_ref: origin/main@d259580
live_site: https://sfa.nimrod.bio
roadmap_disposition_recommendation:
  status: COMPLETE
  phase: done
  lod_status: LOD500_LOCKED
findings:
  - id: F-190-WI7-V-01
    severity: INFO
    summary: The literal live URL /crop-book/search?q=tomato returns no results because the crop-book search route searches Hebrew names; the actual WI7 tomato query used by the test is q=עגבנייה and it renders wc-tomato.png.
    disposition: Non-blocking. This is not a watercolor/CropArt regression; it is a mismatch between the verification prompt's English query shorthand and the shipped route contract.
```

**Disposition:** WI7 deliverables still hold on exact `origin/main@d259580` and on the live site. The INFO finding does not block lock. Team 100 may record the WP as `COMPLETE` / `LOD500_LOCKED`.

## Evidence Summary

| VC | Result | Evidence |
|----|--------|----------|
| VC-1 tests | PASS | Detached exact-head worktree at `d259580`: `composer install` completed; full `vendor/bin/phpunit` passed `232` tests / `736` assertions, with one pre-existing PHPUnit deprecation. WI7-only filter passed `12` tests / `24` assertions. Active workspace branch also passed `234` tests / `739` assertions. |
| VC-2 basket units | PASS | Exact-head code keeps basket unit arms in both `market_list.php::sfa_unit_label()` and `market_product.php` match: `basket_large`, `basket_medium`, `basket_small` -> `לסל`; English snake_case default -> `ליחידה`. Live `/market/` shows `סל ירקות בינוני/גדול/קטן` with `לסל`; `לbasket_large`, `לbasket_medium`, `לbasket_small` absent. |
| VC-3 search watercolor | PASS_WITH_INFO | Exact-head code resolves search result art with `CropArt::file($slug)` and local tests prove known-crop watercolor plus glyph fallback. Live `q=עגבנייה` renders `img.crop-card__art` with `/public_assets/img/crops/wc-tomato.png`. Literal live `q=tomato` returns no result because search SQL matches `hebrew_name LIKE ?`; see F-190-WI7-V-01. |
| VC-4 English eyebrows | PASS | Live home DOM: `.modtile__title small` count is `0`; module tile titles are Hebrew (`ספר גידולים`, `מחירון`, `מחשבון לחקלאי`, etc.). Audience-card English eyebrows are intentionally out of WI7 failure scope. |
| VC-5 kg_per_ha | PASS | Exact-head `FieldRegistry::fmtNumber(80, 'kg_per_ha') === '8'`; `unitLabel('kg_per_ha') === 'ק״ג/דונם'`; other-unit guard test remains green. |
| VC-6 legacy redirects | PASS | Live no-follow HTTP checks: `/crop-book/table?category=summer` -> `301 Location: /crop-book/?season=summer`; `/crop-book/table?category=fast` -> `301 Location: /crop-book/?dtm_max=60`; `/crop-book/table?category=vegetables` -> `200`. |
| VC-7 live + browser QA | PASS | Hub AOS `qa_probe.mjs --shots` against live `/`, `/market/`, `/crop-book/search`: `6/6` pass, mobile `375` and desktop `1440`, `overflow=false` for all pages. Screenshots written under `/tmp/sfa-wi7-live-qa/screenshots/`. |

## Constitutional Checks

| Check | Result | Notes |
|-------|--------|-------|
| Cross-engine independence | PASS | Builder was Claude/Sonnet; validator is GPT-5.5 non-Claude. |
| Scope discipline | PASS | Verified render-layer outcomes only. `/about` tier-badge English and calculator pixel-polish remain explicitly out of WI7 scope. |
| Current-head validation | PASS | Exact `origin/main@d259580` was validated in a detached worktree without altering the dirty active workspace. |
| AOS validation | PASS_WITH_NOTE | Active spoke snapshot: `31 PASS / 21 SKIP / 0 FAIL`. Exact `d259580` does not contain a `validate_aos.sh` file in either `_aos/lean-kit/` or `lean-kit/`, so exact-head AOS script execution was not available. |
| Inter-team artifact route | PASS | Verdict written under `_COMMUNICATION/TEAM_190/SFA-S003-P004/WP-CB-UI-WI7/`; notification sent to team_100. |

## Probe Log

- Exact code ref: `origin/main@d259580` (`archive(WP-CB-UI-MOCKUP-FIDELITY): LOD500_LOCKED...`).
- Active workspace note: current checkout was `feat/wp-cb-book-market-pricechip@ab71d9f`, which contains `d259580` as an ancestor; exact-head validation used detached worktree `/tmp/sfa-wi7-origin-main.pYaYo1`.
- Live browser MCP evidence:
  - Home `.modtile__title` list had no `<small>` English module IDs.
  - Market text contained `לסל` and no raw English basket unit leak.
  - Search `q=עגבנייה` contained `wc-tomato.png` in `img.crop-card__art`.
- Browser QA result file: `/tmp/sfa-wi7-live-qa/qa_probe_result.json`.

## Final Disposition

**PASS_WITH_FINDINGS**. All WI7 acceptance outcomes remain intact at `origin/main@d259580` and on live `https://sfa.nimrod.bio`. The sole INFO finding is not a WI7 blocker.

Team 100 may advance `SFA-S003-P004-WP-CB-UI-WI7` to:

```yaml
status: COMPLETE
phase: done
lod_status: LOD500_LOCKED
```
