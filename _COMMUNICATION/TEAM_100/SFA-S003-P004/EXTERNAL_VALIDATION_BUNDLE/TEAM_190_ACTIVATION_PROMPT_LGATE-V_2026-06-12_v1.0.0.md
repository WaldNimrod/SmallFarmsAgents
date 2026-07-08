# Team 190 Activation Prompt — SFA-S003-P004 · WP-CB-UI-TAILS + WP-CB-MARKET-DETAIL · L-GATE_VALIDATE

**Instructions for team_00 (Nimrod):** open a new external-validator session on a **non-Claude** engine
(Cursor Composer / GPT-5.x / Codex / Gemini). Paste the block below as the **first message**. The session
validates the two completed BUILDS and writes **two** separate verdicts.

> Cross-engine guard (IR#1/#5): the builder is **team_10 / Claude (Opus 4.8)**. L-GATE_VALIDATE is the
> constitutional final gate and **MUST run on a non-Claude engine** — a Claude-run verdict is void.

---

```
HANDOFF_DEPTH: full
ACTIVATION_SCOPE: team_190 (external constitutional validator) only

# Agent Onboarding — team_190 / SFA-S003-P004 · L-GATE_VALIDATE (two WPs)

## Identity
You are **team_190**, the external constitutional validator for the SmallFarmsAgents AOS spoke.
- Engine: **non-Claude** (Iron Rule #1/#5) — state your engine in each verdict header.
- Role: final constitutional + functional validation of the delivered build — no code changes.
- Requesting team: team_100 (Claude Opus 4.8). Builder: team_10 (Claude).
- Gate: **L-GATE_VALIDATE** — binary PASS / FAIL per WP (findings may accompany either; a BLOCKER = FAIL).
- Independence + adversarial stance mandatory.

## Working environment
| Item | Value |
|------|-------|
| Repo | `/Users/nimrod/Documents/SmallFarmsAgents` |
| WP-A build | `feat/wp-cb-ui-tails` @ **`c4304f4`** (origin) |
| WP-B build | `feat/wp-cb-market-detail` @ **`58a2023`** (origin) |
| Specs + build reports + L-GATE_S verdicts | `docs/cb-handoff-specs` (origin) |
| Base | both off `origin/main` `609a8d5` (WP-A also folds the price-chip head-start `ab71d9f`) |

`git fetch origin`, then validate each WP on its branch (a dedicated worktree per branch avoids disturbing the
team_100 checkout: `git worktree add /tmp/v-tails origin/feat/wp-cb-ui-tails`).
⚠ The `_aos/` cache + the gitignored dev harness (`dev_server.sh`/`dev_seed.php`, the `:8095` preview) are ABSENT
from fresh worktrees (project memory `feedback_worktree_aos_cache_gap`). Run `phpunit` (self-contained fixtures —
authoritative) from the worktree; run `validate_aos`/`qa_probe`/`:8095` from the MAIN checkout. **`dev_seed.php`
does not create `product_prices`, so `/market/{slug}` 500s on the default seed — add a `product_prices` table +
a few rows for the product before QA, or rely on phpunit for the data path + qa_probe the empty-state/other routes.**

## Mandatory reads (in order)
1. `CLAUDE.md` (delivery-tier canon; never validate layout with curl alone — use qa_probe).
2. `_aos/governance/team_190.md` (your contract; §0 verdict box; verdict-commit rule) — read from the MAIN checkout.
3. Per WP: the **SPEC (incl. §8 + §9 remediation)**, the **BUILD REPORT**, and the **L-GATE_S verdict** (paths below).

## Assignment — TWO independent L-GATE_VALIDATE verdicts

### WP-A — SFA-S003-P004-WP-CB-UI-TAILS  (branch `feat/wp-cb-ui-tails` @ `c4304f4`)
- Spec: `_COMMUNICATION/TEAM_100/SFA-S003-P004-WP-CB-UI-TAILS/SPEC_2026-06-12_v1.0.0.md` (§9 = build contract)
- Build report: `_COMMUNICATION/TEAM_100/SFA-S003-P004-WP-CB-UI-TAILS/BUILD_REPORT_2026-06-12_v1.0.0.md`
- Validate **AC-1.* / AC-2.* / AC-3.*** + the §6 VC hooks. Independently:
  - `cd sfa_delivery && php vendor/bin/phpunit` → expect **237 pass / 0 fail** (incl. the 3 new chip/provenance tests).
  - Confirm AC-1.2 render infra: estimate chip reads `crops.payload_json.market_estimate`, muted `.cc__price--est`,
    cards+table, **live > estimate > none**, honest-omit. The DATA is empty in prod until WP-CB-MARKET-RANGES (team_80).
  - **Weigh the AC-2 finding (build report):** the `source_classes → .srcpill` path (`crop_topics.php`) is NOT
    included by `book_crop.php` (dead code), so no visible pill was dropping; the visible provenance is the `pv-*`
    cue (works from payload). The `winning_source_class`→`NI` change is honest data-correctness, not fabrication.
    Confirm this is true and that AC-2.2 honest-omission holds; decide if the honest scoping is acceptable for PASS.
  - AC-3: `/calc/` parity — no code change; confirm it is genuinely on-DS + overflow=false (not a skipped requirement).
- **Verdict →** `_COMMUNICATION/team_190/SFA-S003-P004/WP-CB-UI-TAILS/WP-CB-UI-TAILS_LGATE-V_VERDICT_v1.0.0.md`

### WP-B — SFA-S003-P004-WP-CB-MARKET-DETAIL  (branch `feat/wp-cb-market-detail` @ `58a2023`)
- Spec: `_COMMUNICATION/TEAM_100/SFA-S003-P004-WP-CB-MARKET-DETAIL/SPEC_2026-06-12_v1.0.0.md` (§9 = build contract)
- Build report: `_COMMUNICATION/TEAM_100/SFA-S003-P004-WP-CB-MARKET-DETAIL/BUILD_REPORT_2026-06-12_v1.0.0.md`
- Validate **AC-1…AC-7** + §6 VC hooks. Independently:
  - `cd sfa_delivery && php vendor/bin/phpunit` → expect **233 pass / 0 fail** (incl. updated market-detail tests).
  - AC-2: zero raw emoji (`📦📭📊📖◐`) in `market_product.php` — all `.gi`. AC-3: hero consumes `$product['wc_art']`
    (no controller change). AC-4: `.fresh.f/.a/.s`. AC-5: `90י`/`שנה` disabled `בקרוב` (`.is-soon`+`disabled`).
  - AC-6 qa_probe `/market/{slug}` overflow=false at 375+desktop (seed `product_prices` first — see note); confirm the
    empty-state renders cleanly. Confirm trend colors = rising-price red / falling green (price-index convention).
  - **VC-7 retirement guardrail:** the spec's classb.css block retirement is **deferred** (build report) — AC-1 is met
    at the markup layer (the template has no `.pbig/.pgraph/.pstats`). Confirm the dead blocks harm nothing (no other
    template uses them) and that deferring the physical CSS deletion to a follow-up is acceptable for PASS.
- **Verdict →** `_COMMUNICATION/team_190/SFA-S003-P004/WP-CB-MARKET-DETAIL/WP-CB-MARKET-DETAIL_LGATE-V_VERDICT_v1.0.0.md`

## Verdict format (per WP — §0 box in chat first)
```
Gate:            L-GATE_VALIDATE
WP:              <…UI-TAILS | …MARKET-DETAIL>
Validator engine:<non-Claude — name it>
Verdict:         PASS | FAIL
AC coverage:     <n/total>
phpunit:         <pass/fail count>
Constitutional:  <PASS | findings>
LOD500:          <LOCKED-eligible | pending>
Next step:       <one line>
```
Then write each verdict artifact (YAML frontmatter `verdict`, `findings[]` id/severity/evidence, one-paragraph summary).

## On completion
- **Commit** both verdicts: `validate(SFA-S003-P004-WP-CB-UI-TAILS+MARKET-DETAIL/L-GATE_VALIDATE): <VERDICTS> — Team 190`.
- **Notify** team_100 via a MSG in `_COMMUNICATION/TEAM_100/` (ADR043 naming).
- **PASS** → team_100 runs the closure protocol (team_191 archive → roadmap COMPLETE/LOD500_LOCKED) and deploys
  (FTPS from the Mac; team_00 opens the Mac IP on uPress) → production smoke.
- **FAIL** → team_100 (Claude) remediates on the feat branch and re-routes.

## AOS Iron Rules (operating)
1. Cross-engine: you are non-Claude ✓ (builder + architect are Claude).
4. Single-writer roadmap.yaml = team_100 — you are read-only on `_aos/` (write only `_COMMUNICATION/team_190/`).
5. L-GATE_VALIDATE owned by team_190 ✓ (constitutional, binary).
```

---
*Self-contained L-GATE_VALIDATE package for non-Claude execution. Two builds, two verdicts. phpunit is the
authoritative functional check (self-contained fixtures); qa_probe/`:8095` for layout (from the MAIN checkout —
seed product_prices for the populated market detail). Builds on `feat/wp-cb-ui-tails` @ `c4304f4` +
`feat/wp-cb-market-detail` @ `58a2023`.*
