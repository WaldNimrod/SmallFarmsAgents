# VALIDATION MANDATE — WP-CB-UI-patch01 (L-GATE_V **R2**) — team_100 → team_190 — v1.0.0

**Date:** 2026-06-04 · **From:** team_100 (Opus) · **To:** team_190 (**NON-CLAUDE**, IR#1/#5) · **Routed by:** team_00
**Repo:** `/Users/nimrod/Documents/SmallFarmsAgents` · branch `claude/ui-polish-hub-cropbook-2026-06-03`
**Live target:** https://sfa.nimrod.bio · **deployed SHA `6703313`** · **served `?v=1780520599`** (cf-cache MISS on re-probe)
**Gate:** L-GATE_V **R2** — live visual re-validation after team_99 FINAL deploy. Supersedes R1 (FAIL — precondition only).

## 0. Cross-engine (IR#1/#5 — MANDATORY)
Builder = Claude Sonnet (team_10); L-GATE_B = Claude Opus (team_100). This L-GATE_V **MUST run on a NON-CLAUDE engine** (Cursor/GPT/Codex). State the engine in the verdict header. A Claude verdict is void.

## 1. Why R2 (what changed since R1)
R1 (2026-06-03, Cursor/Composer GPT) returned **FAIL 0/9 — but solely on the PRECONDITION**: the patch had not been deployed (live still served pre-patch01 CSS/HTML). The **branch code passed every check** (R1 right-hand column = PASS for C1–C9). Since then:
- **team_99 FINAL-deployed `6703313`** (MSG-HUB-20260604-001): WI-1..WI-7 served; CSS `?v=` `1780515224`→`1780520599`; lftp 12/12 exit 0; smoke 4/4 PASS.
- **team_100 independently VERIFIED the deploy is live + correct** (`_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-UI-patch01/TEAM100_VERIFICATION_REAUDIT_2026-06-04.md`): the 3 live CSS files are **byte-identical to branch**, all WI-5/6/7 markers present at live = local counts.
- **A prior team_50 "NO-GO" was a FALSE NO-GO on the CSS** (it probed the wrong file — `hub.css` instead of `crop-book-v1.css` — and read a stale cache). team_100 **rejected** it. Do not rely on it.

So R2 should now find the C1–C9 set **live and PASS** on `6703313`.

## 2. Checks (C1–C9) — run against LIVE `6703313` + code
> **Cache-bust discipline (critical — this is what tripped the false NO-GO):** probe each asset at **`?v=1780520599`** (or force `cf-cache-status: MISS`); never trust a cached `1780515224`. WI-5 lives in **`crop-book-v1.css`**, WI-6 in **`classb.css`**, table rules in **`crop-book-deep.css`** — probe the correct file per marker.

- **C1 (hub `/`):** open-tools row spans **full content width** (no trailing gap); `.hub-grid` uses `auto-fit`; **4 tiles** (3 live + Field-Log teaser).
- **C2 (Field-Log tile):** renders **"יומן השדה" + "בפיתוח"**, class `is-dev`, **non-clickable** (no href / aria-disabled), muted/dashed — reads as in-development, not an available tool.
- **C3 (`/crop-book/`):** crop grid **markedly denser** (≥5–6 cols desktop; `.cards-grid` `minmax(120px,1fr)`, gap 10px); cards compact; **no horizontal overflow** on this page; RTL intact; filters/search/audience toggle work; 200.
- **C4 (mobile legibility):** **`/` and `/crop-book/`** remain legible and **no horizontal overflow** at narrow width. *(Scope note: `/crop-book/table` is carved out — see §3 Known Residual; do NOT fail C4 on `/crop-book/table`.)*
- **C5 (constitutional):** delivery-tier only; palette `#f8fbf8` (no cream); classb.css loaded last; composer green; validate_aos 0 FAIL; IR#4 (no builder roadmap edit).
- **C6 (hub copy):** GARDENER card reads **"גנן"** (not "גינאי ביתי"); hub tagline on ONE line desktop, wraps clean mobile, no overflow.
- **C7 (terminology):** customer-facing copy uses **"חקלאות מקומית" / "חקלאי מקומי"** — no "חקלאות קטנה"/"חקלאי קטן" on `/`, `/community`, `/market/` disclaimer, or page subtitle. (Unrelated "קטן/קטנה" — small garden/contribution — may remain.)
- **C8 (Tend removed):** `/about` + crop/variety pages carry **no customer-facing Tend** mention (generic field-data wording).
- **C9 (hub CTA):** `/` shows `.hub-cta` with two offers — secondary "שתפו אותנו…"→/community, **primary** "ספרו לנו…"→WhatsApp/contact; both work; primary prominent; RTL + stacks on mobile.

**Also live to spot-confirm (WI-5/6/7, not gating C1–C9):** `/crop-book/` entry-path cards compact via `cb-paths{display:grid}` (4 mod-cards, not giant); app-shell logo sized via `.sh__mark{width:34px;height:34px;overflow:hidden}` + `.sh__mark svg{width:100%}`; crop-detail + market-detail no 375 overflow.

## 3. KNOWN RESIDUAL — explicitly OUT OF SCOPE for this gate
**`/crop-book/table` @375 still horizontally overflows on live `6703313`** (scrollWidth ≈517 > 375; RTL scroll-origin leak). The fix is **WI-8** (`.cb-table-page { overflow-x: clip }`, commit `c7b4368`) **+ WI-9** (responsive table toggle, `e798bc8`) — both committed on the branch but **NOT in the deployed `6703313`**. They land with the **WP-CB-UI-FIDELITY** deploy (which is stacked on top and includes them). Tracking: team_50 PRELAUNCH-QA (`SFA-S003-P004-WP-PRELAUNCH-QA`).
→ **Do NOT fail patch01 C1–C9 on the `/crop-book/table` overflow.** If you choose to record it, mark it `INFO` with disposition "deferred to FIDELITY deploy / team_50 PRELAUNCH-QA". Confirm the OTHER WI-7 pages (`/crop-book/{slug}`, `/market/{slug}`) are overflow-clean at 375 (they are, per team_100 CDP).

## 4. Verdict → `_COMMUNICATION/team_190/SFA-S003-P004/WP-CB-UI-patch01/WP-CB-UI-patch01_LGATE-V_R2_VERDICT_v1.0.0.md`
```yaml
wp: SFA-S003-P004-WP-CB-UI-patch01
gate: L-GATE_V
correction_cycle: R2
validator_engine: <non-Claude — name it>
branch_head_live: 6703313
served_asset_version: 1780520599
result: PASS | PASS_WITH_FINDINGS | FAIL
checks: <n/9>            # C1..C9
findings:
  - id: F-190-PATCH01-V-R2-NN
    severity: BLOCKER | MAJOR | MINOR | INFO
    summary: ...
    evidence: <live probe @ ?v=1780520599 + file:line>
    disposition: ...
known_residual_ack: "/crop-book/table @375 overflow — WI-8/9 undeployed; deferred to FIDELITY deploy (acknowledged, not a C1–C9 failure)"
summary: <one paragraph>
```
- **PASS / PASS_WITH_FINDINGS** → team_100 advances patch01 to **LOD500_LOCKED** + records the gate.
- **FAIL** → back to team_10/team_99 with the failing check.

Notify via a MSG in `_COMMUNICATION/team_100/` (ADR043 naming).

## 5. Cursor prompt (paste into the NON-CLAUDE validator)
> You are **team_190** on a **NON-CLAUDE** engine (Cursor/GPT/Codex — confirm in the verdict header; IR#1/#5). Repo
> `/Users/nimrod/Documents/SmallFarmsAgents`, branch `claude/ui-polish-hub-cropbook-2026-06-03`, deployed LIVE to
> https://sfa.nimrod.bio at SHA `6703313`, served `?v=1780520599`. Gate: **L-GATE_V R2** for **WP-CB-UI-patch01**.
> R1 failed only because the deploy hadn't happened; it's now live. **Cache-bust every asset to `?v=1780520599`**
> (force cf-cache MISS) — a stale cache caused a prior false NO-GO; WI-5 is in `crop-book-v1.css`, WI-6 in
> `classb.css`. Run §2 checks **C1–C9** against the LIVE site + code: hub open-tools full-width + 4th non-clickable
> "יומן השדה / בפיתוח" `is-dev` tile (C1/C2); `/crop-book/` dense grid ≥5–6 cols, no overflow, RTL, filters work
> (C3); `/` and `/crop-book/` mobile legible no overflow (C4 — **`/crop-book/table` is OUT OF SCOPE, see below**);
> delivery-tier + palette + composer + validate 0 FAIL + IR#4 (C5); "גנן" + one-line tagline (C6); "חקלאות/חקלאי
> מקומי" no "קטנה/קטן" on /, /community, /market disclaimer (C7); no Tend on /about (C8); `.hub-cta` dual offers,
> primary→WhatsApp (C9). **KNOWN RESIDUAL (do NOT fail on it):** `/crop-book/table` @375 still overflows — WI-8/9
> fix is undeployed and lands with the FIDELITY deploy; record at most as INFO/deferred. Emit the verdict YAML (§4).

---
*team_100 verification of the live deploy: `…/SFA-S003-P004-WP-CB-UI-patch01/TEAM100_VERIFICATION_REAUDIT_2026-06-04.md`. team_99 deploy report: `_COMMUNICATION/team_99/SFA-S003-P004-WP-CB-UI-patch01/DEPLOY_REPORT_v1.0.0.md` (sha 6703313).*
