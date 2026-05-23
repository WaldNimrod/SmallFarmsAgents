# Known Debt Catalog — SmallFarmsAgents

**Last refresh:** 2026-05-23 by team_100 / SFA-S003-P002-WP-C
**Refresh policy:** at every program closure (P-program closing on this spoke), team_100 sweeps new deferred items into this file. Items are CARRIED (still deferred), RESOLVED (with resolution-ref), or PROMOTED (became an active WP). Refresh is part of the F-LV-01 §2 closure obligation.

**SSoT scope:** all deferred / dropped / "later" items across spoke history (S001–current). Hub items are listed in §D only when they may impact our spoke; otherwise out of scope (hub maintains its own backlog).

---

## Index

- [§A — Pre-S004 product debt (consider before opening S004 calculator)](#a--pre-s004-product-debt)
- [§B — Operational follow-ups (admin / governance / non-product)](#b--operational-follow-ups)
- [§C — Tend + MasterClass remaining ingestion (S003 redefinition leftover)](#c--tend--masterclass-remaining-ingestion)
- [§D — Hub V4.3 awareness (informational; not our scope unless promoted)](#d--hub-v43-awareness-informational)
- [§E — Resolved debt (audit trail; items closed since prior refresh)](#e--resolved-debt-audit-trail)
- [§F — Binding policies (NOT deferred; surfaced for visibility)](#f--binding-policies-not-deferred-surfaced-for-visibility)

---

## §A — Pre-S004 product debt

These items influence S004 (calculator + community features) scope. Read this section before opening S004.

### A.1 Crop images / photo gallery
- **Source:** `_aos/work_packages/S003/SFA-S003-P001-WP004/LOD400_spec.md` §15
- **Status:** CARRIED
- **Severity:** LOW (visual polish; non-functional)
- **Description:** Crop book is currently text-only. No crop photographs, no variety photos. Adding images would require: image sourcing pipeline (licensing), CDN/WP media library upload flow, schema column for image URLs on `crop_varieties`, SPA card rendering.
- **S004 impact:** if the UX overhaul (SFA-S003-P002-WP-B) recommends images, this becomes the asset-sourcing prerequisite.
- **Likely future home:** S004 or later visual-polish WP.

### A.2 Daily cron auto-publish for crop book
- **Source:** WP004 §15 + WP004 architecture decision §2.1
- **Status:** CARRIED
- **Severity:** LOW (operational rather than functional)
- **Description:** Crop book publishing is currently CLI-only (`python -m organic_market_agent crop_book_publish --upload`). Market report runs nightly via `scheduler/pipeline.py`. Crop data changes are episodic — daily auto-publish would re-upload identical artifacts most days (wasteful + WP media tracking churn).
- **Trigger to promote:** if WP-A (data enrichment) introduces a daily-changing data source (e.g. live market prices integrated into crop book), revisit.
- **Likely future home:** sibling to WP-A delivery.

### A.3 Mobile-specific responsive tuning (crop book)
- **Source:** WP004 §15 + S002 WP005 RISK_REGISTER R-01 (AC-05 Lighthouse + AC-06 cross-device smoke deferred to team_50)
- **Status:** CARRIED
- **Severity:** MEDIUM (UX gap on the most-likely-used form factor)
- **Description:** WP004 inherits desktop-first SPA. Mobile parity is best-effort, not an AC. Same for market report — Lighthouse + cross-device smoke deferred since S002.
- **PROMOTION CANDIDATE:** SFA-S003-P002-WP-B (UX/UI Overhaul, currently with team_35) explicitly addresses mobile-first design across both modules. Expected to consume this item.
- **Likely future home:** SFA-S003-P002-WP-B + implementation sibling.

### A.4 Combined market + crop-book shortcode
- **Source:** WP004 §15
- **Status:** CARRIED
- **Severity:** LOW (architectural cleanup, not blocking)
- **Description:** Two separate WP shortcodes (`[sfagent_market_report]` + `[sfagent_crop_book]`) — could be unified into one shortcode with a `type=` parameter. Cleaner WP page authoring, marginal performance benefit.
- **Tension with PROMOTION:** WP-B UX overhaul may decide unification is needed (treating two modules as one system). Or may decide separation is correct (different mental models). Defer to WP-B output.
- **Likely future home:** WP-B implementation sibling.

### A.5 Per-variety hash routes
- **Source:** WP004 §15
- **Status:** CARRIED
- **Severity:** LOW (URL deep-linking depth)
- **Description:** Currently `#crop-{id}` deep-links to crop detail. Variety-level deep-link (`#crop-12/variety-87`) NOT supported. Single SPA, hash routing only.
- **Likely future home:** S004 or WP-B output.

### A.6 Internationalization beyond Hebrew (English UI)
- **Source:** WP004 §15
- **Status:** CARRIED
- **Severity:** LOW (audience is Hebrew-primary; English nice-to-have)
- **Description:** All UI in Hebrew. English secondary content welcome but not required.
- **Trigger to promote:** if English-speaking audience reaches material size, revisit.

### A.7 Shared CSS deployment — `sfagent-base.css` unification across both modules
- **Source:** WP004 §15
- **Status:** CARRIED
- **Severity:** LOW (refactoring)
- **Description:** Crop book ships inline CSS in body fragment. Market report uses `sfagent-base.css` (FTPS-deployed, child theme). Could unify into a single shared stylesheet.
- **PROMOTION CANDIDATE:** WP-B design book (LOD300) will produce canonical design tokens. Implementation WP that follows would naturally consolidate the CSS.

### A.8 Bundle-size optimization (R-WP004-02 follow-up)
- **Source:** WP004 §14 R-WP004-02 (originally MEDIUM, now mitigated)
- **Status:** CARRIED (mitigation acceptable for v1; further optimization deferred)
- **Severity:** LOW (gzipped 15KB is well under any threshold)
- **Description:** `sfagent-crop-book-data.json` is ~388KB raw / ~15KB gzipped. Future optimization possibilities: pagination, lazy-loading per crop, chunked data.json by category. Currently unnecessary — uPress gzip is automatic, total page weight tiny.
- **Trigger to promote:** if WP-A enrichment 10x's the JSON size and gzipped passes ~1MB, revisit.

---

## §B — Operational follow-ups

Administrative / governance items, non-product.

### B.1 Provision `team_100@smallfarmsagents` API key on hub
- **Source:** Hub closure `MSG-HUB-20260522-003` §4 + GCR_AOS_MESSAGING_INFRA_HARDENING F-MSG-01
- **Status:** CARRIED
- **Severity:** MEDIUM (unblocks canonical API path; today we file-fallback for every send)
- **Action:** team_00 or team_99 runs `scripts/issue_actor_key.sh smallfarmsagents-team_100` on waldhomeserver; team_00 distributes the key to Mac shell profile as `AOS_ACTOR_API_KEY=...`
- **Effect when done:** team_100 sends use canonical API path (`POST /api/messaging/send` returns 2xx); file-fallback becomes defensive-only.
- **Blocker:** requires team_00 + waldhomeserver SSH access; not something team_100 can self-execute.

### B.2 Mark resolved GCRs in their file frontmatter
- **Source:** Housekeeping — two GCRs hub-resolved 2026-05-22 but our local GCR files still show original `status: pending` state
- **Files:**
  - `_COMMUNICATION/TEAM_100/GCR_AOS_MESSAGING_INFRA_HARDENING_2026-05-10_v1.0.0.md`
  - `_COMMUNICATION/TEAM_100/GCR_UPRESS_FTPS_PROTOCOL_2026-05-10_v1.0.0.md` (team_10 author)
- **Status:** CARRIED
- **Severity:** LOW (audit-trail polish)
- **Action:** edit each GCR's frontmatter:
  ```yaml
  status: CLOSED
  resolved_at: 2026-05-22
  hub_closure_artifact: agents-os:_COMMUNICATION/team_100/MSG-HUB-20260522-{001|003}.md
  hub_addendum: <ref>
  ```
- **Estimated effort:** 5 min

### B.3 `entity_registry.js` admin file canonical commit
- **Source:** F-190-WP004-LV-02 narrative + F-190-WP004-01 R2 fix history + F-190-patch02-03 clarification
- **Status:** CARRIED
- **Severity:** LOW (admin tooltips still work in WP003 since file exists in working tree)
- **Description:** `organic_market_agent/admin/static/crop_book/entity_registry.js` (4009B) EXISTS in working tree and was committed via the canonical S003 merge `d2a61a1`. It was historically referenced by WP003 admin templates but never appeared in a WP003 LOD500 deliverables list. patch02 routed around (Python-owned registry in publisher), but the admin still references the JS via `url_for('static', ...)`.
- **Decision needed:** either (a) formally canonicalize the JS in a WP003-patch03 LOD500 amendment, OR (b) refactor admin to import from publisher's `entity_registry_data.py`. Option (b) is cleaner (single source) but touches LOD500_LOCKED admin templates.
- **Defer trigger:** revisit if WP-A enrichment changes the entity registry schema.

### B.4 `/smallfarmsagent/` WP page has BAKED-IN STALE HTML (not using the shortcode)
- **Source:** Discovered 2026-05-23 by team_100 during team_35 HANDOFF_PACKAGE URL verification
- **Status:** CARRIED — **HIGH SEVERITY (production-visible bug, affects every visitor)**
- **Severity:** HIGH (real users see stale "1 מוצרים · תאריך דוח: 2099-08-12" instead of 34 fresh products)
- **Diagnosis confirmed by:**
  - WP page modified date: `2026-04-02T13:21:18` (over 7 weeks stale)
  - `[sfagent_market_report]` shortcode NOT present in page raw content (verified via `/wp/v2/pages/91325`)
  - Page renders body fragment HTML directly (baked-in, not fetched)
  - Manifest fresh (`product_count: 34, report_date: 2026-05-09, staleness_level: "current"`)
  - Body fragment file fresh (107KB, 34 product rows verified)
  - mu-plugin `sfagent_market_report` shortcode is REGISTERED but page doesn't invoke it
- **Origin:** Someone (likely team_00 in pre-S002 era while testing) pasted the body fragment HTML directly into the WP page editor when the upload pipeline was failing (the body at the time only had 1 product + 2099-08-12 placeholder per pre-WP007 narrative). The page was never updated after WP007 fixed the pipeline (2026-05-07).
- **Fix (trivial — ~2 min):**
  1. team_00 opens `https://www.nimrod.bio/wp-admin/post.php?post=91325&action=edit` (uPress WP admin)
  2. Delete all baked HTML inside the page content (the `<div class="sfagent">` ... `</div>` block)
  3. Replace with the canonical shortcode: `[sfagent_market_report]`
  4. Save → page will immediately render 34 current products from the live manifest
- **Validation post-fix:** `curl https://www.nimrod.bio/smallfarmsagent/ | grep -c "class=\"product-name\""` should jump from `2` to `68` (34 products × 2 layouts)
- **Likely future home:** trivial team_00 manual fix; no WP needed. Optionally absorbed into WP-B output (where team_35 may decide the page restructure).

---

## §C — Tend + MasterClass remaining ingestion

The original S003 was redefined to "crop book" on 2026-05-07, but the originally-planned Tend + MasterClass raw-material processing remains partially ingested. Most of the value-dense data is on disk and unread.

### C.1 Tend tables NOT yet ingested
- **Source:** `_COMMUNICATION/TEAM_100/SFA-S003-DISCOVERY-SUMMARY_2026-05-07_v1.0.0.md`
- **Status:** CARRIED (partial — only subset feeds crop_book)
- **Severity:** MEDIUM (data exists; high latent value for WP-A enrichment + S004 calculator)
- **Inventory:**
  - **Currently ingested** (2022 only): `CROP_PLAN` (529 rows), `PRODUCT_SOLD`, `HARVESTS` (939 rows) — subset
  - **NOT ingested**: `CROPAVAILABILITY` (232 rows), `EXPENSES` (4 rows — very sparse), `GREENHOUSE_PLAN` (287 rows), `LOCATIONS` (200 rows), `ORDERS_RAW_DATA` (bonus per-line-item pricing), and ~8 more tables × 5 years (2018–2022)
  - Cross-year ingestion (2018–2021) NOT done for any table — only 2022 partial
- **Potential consumers:**
  - WP-A (data enrichment) — longitudinal yield/price analysis
  - WP-A2 (farmer calculator in S004) — historical actuals as baseline
  - Future "operational dashboard" WP
- **Likely future home:** WP-A may absorb a subset; full ingestion likely deferred to S004 or later.

### C.2 MasterClass library beyond JMF subset
- **Source:** Discovery summary §MasterClass
- **Status:** CARRIED
- **Severity:** LOW
- **Description:** Currently ingested: JMF (price/yield) benchmarks per crop. NOT ingested: full MasterClass library (other published references, PDFs at `/Users/nimrod/Documents/Market Gardening/MasterClass/`).
- **Trigger to promote:** WP-A team_110 architecture may identify specific MasterClass sources worth ingesting.

### C.3 EXPENSES table caveat
- **Source:** Discovery summary §"EXPENSES Caveat"
- **Status:** CARRIED (informational)
- **Severity:** INFO
- **Description:** EXPENSES is sparse (4 rows in 2022). Not a useful primary source.
- **Implication:** if S004 calculator needs cost data, sourcing has to come from elsewhere (team_00 input, per-farmer profile, market estimates).

---

## §D — Hub V4.3 awareness (informational)

Hub V4.3 follow-ons that may impact our spoke. Not our scope unless explicitly promoted.

### D.1 Cursor cloud agent → hub API access gap
- **Source:** Hub closure `MSG-HUB-20260522-003` §5 #1 + `agents-os:_COMMUNICATION/team_100/TRIAGE_CURSOR_API_ACCESS_ESCALATION_2026-05-22_v1.0.0.md`
- **Status:** CARRIED at hub (V4.3 candidate); awareness for us
- **Severity:** LOW
- **Description:** Cursor cloud sandbox runners cannot reach Tailscale → cannot reach `100.125.98.56:8090` AOS API. Our team_190 sessions running on Cursor (non-Claude per IR#1) work via local Mac with Tailscale — workaround functional.
- **Impact on us:** zero today; if we move team_190 to Cursor cloud, blocked. Likely revisit when hub V4.3 lands.

### D.2 ADR034 R10 addendum (Hub-Native WP File-SSoT Exception)
- **Source:** Hub closure `MSG-HUB-20260522-003` §5 #2 + `agents-os:_COMMUNICATION/team_100/FINDING_HUB_NATIVE_WP_DB_SYNC_NOT_APPLICABLE_2026-05-22_v1.0.0.md`
- **Status:** CARRIED at hub (V4.3); awareness for us
- **Severity:** INFO
- **Description:** Codifies that hub `AOS-V*-WP-*` are file-canonical (parallel to ADR034 R9 for L2 spoke roadmap). Architectural clarity, zero practical impact on us.

---

## §E — Resolved debt (audit trail)

Items closed since the prior catalog refresh (= since inception of this file).

| Resolved date | Item | Resolution-ref |
|---------------|------|----------------|
| 2026-05-23 | F-190-WP004-LV-02 test-harness debt | SFA-S003-P001-WP003-patch02 LOD500_LOCKED (team_190 commit `25c4a22`) |
| 2026-05-23 | N-190-WP004-LV-01 pytest `integration` marker | patch02 Cluster C fix |
| 2026-05-23 | patch02 R1 finding F-190-patch02-01 (AC-10 grep narrower than prose) | team_100 inline AC-10+05 widening (no R2; team_190 §4 explicit pre-authorization) |
| 2026-05-22 | F-LV-01 prod-deploy authority gap | `DECISION_F-LV-01_PROD_DEPLOY_AUTHORITY_2026-05-22_v1.0.0.md` (Hybrid policy approved by team_00) |
| 2026-05-22 | GCR_AOS_MESSAGING_INFRA_HARDENING (all 9 F/R pairs) | Hub `AOS-V4.1-WP-ACTOR-KEY-PROCEDURE` + `AOS-V4.2-WP-MSG-CANON-EXTENSIONS` + `AOS-V4.2-WP-POST-MIGRATION-HARDENING` (all LOD500_LOCKED). ADR043 v1.5.0 + AOS_ACTOR_KEY_PROCEDURE + msg_preflight v1.5 propagated to our `_aos/` |
| 2026-05-22 | GCR_UPRESS_FTPS_PROTOCOL | Hub canon `lean-kit/modules/12-home-server-infrastructure/runbooks/UPRESS_FTPS_PROTOCOL_v1.0.0.md` propagated to our `_aos/lean-kit/.../UPRESS_FTPS_PROTOCOL_v1.0.0.md` |
| 2026-05-22 | F-190-WP004-LV-01 prod-deploy out-of-mandate (WP004 builder) | Retroactively reclassified as compliant under F-LV-01 Hybrid policy `prod_deploy_authority: builder` for SMALL/L0 WPs; recorded as historical |
| 2026-05-22 | team_191 follow-up: WP001 spec_ref → `_archive/` path | team_100 fix to roadmap `spec_ref` (validate_aos Check 4 PASS) |
| 2026-05-13 | R-WP004-02 bundle size measurement | Measured 388KB raw / 15KB gzipped — well under 1MB threshold. Mitigation accepted; further optimization deferred to §A.8 |
| 2026-05-13 | R-WP004-04 entity_registry.js regex extraction risk | Made obsolete by R2 — replaced by Python-owned `entity_registry_data.py` |
| 2026-05-13 | R-WP004-06 sentinel substitution fragility | Mitigated by AC-17 (publisher invariant) + AC-18 (PHP placeholder fallback) + AC-11 grep |

---

## §F — Binding policies (not deferred; surfaced for visibility)

Policies established during S003 that constrain ALL future work. NOT debt — discipline.

### F.1 F-LV-01 §2 unified-end-state invariants (program closure obligation)
- **Source:** `_COMMUNICATION/team_00/DECISION_F-LV-01_PROD_DEPLOY_AUTHORITY_2026-05-22_v1.0.0.md` §2
- **Binding for:** ALL future programs (every P-program closure)
- **Obligation:** team_100 must validate before issuing archive mandate:
  - (a) **Unified deployment** — production reflects full intended functional surface; no partial deploys outstanding
  - (b) **Single canonical branch** — feature branches merged to `main` (or otherwise retired); no orphan branches surviving past program closure
  - (c) **No version drift** — same code base = source of truth for staging + production; no separate "deploy versions" diverging
- **Failing closure** → open follow-up cleanup WP before issuing closure artifacts
- **Refresh this catalog also part of the closure obligation** — every P-program closure adds a row here

### F.2 `prod_deploy_authority` field on DISPATCH (F-LV-01 Hybrid policy)
- **Source:** same DECISION_F-LV-01 §1
- **Binding for:** every DISPATCH artifact going forward
- **Field values:**
  - `builder` — L-GATE_B builder may execute prod deploy in-session (default for L0 / SMALL WPs)
  - `team_99` — prod deploy routed to team_99 server ops (default for LARGE / production-critical WPs)
  - `amend_required` — DISPATCH amendment + team_00 approval required before any prod deploy (security-sensitive WPs)
- **Default tier decision:** team_100 sets at L-GATE_S; team_00 may override at L-GATE_E
- **Local lean-kit cannot be edited** (spoke read-only snapshot per CLAUDE.md). Hub-side amendment to `lean-kit/modules/validation-quality/templates/MANDATE_TEMPLATE.md` was tracked in F-LV-01 decision §5 — may need a future GCR.

### F.3 "No shortcuts, no skips, no patches" — team_00 test integrity directive
- **Source:** team_00 directive 2026-05-22 (in `/AOS_decide` brief for F-LV-02)
- **Binding for:** any test-touching WP
- **Rule:** failing tests must be resolved at root cause. Forbidden: `pytest.skip(...)`, `@pytest.mark.skip`, `@pytest.mark.skipif`, `pytest.importorskip`, `@pytest.mark.xfail`, `--ignore` config, conftest auto-skip hooks. NEW skip-class lines forbidden in patch diffs. Pre-existing skips may remain with explicit carve-out documentation.
- **Codified in:** SFA-S003-P001-WP003-patch02 AC-05 + AC-10 (widened post-R1)
- **Audit pattern:** every test WP BUILD_REPORT MUST include a `skip-class scan attestation line`

### F.4 Cross-engine validator mandate (Iron Rule #1)
- **Source:** CLAUDE.md Iron Rules
- **Binding for:** every L-GATE_S + L-GATE_V validation
- **Rule:** team_190 sessions MUST run on a non-Claude engine (Cursor Composer or Codex). Builder = Claude (Sonnet typically); validator ≠ Claude.

### F.5 Single roadmap writer (Iron Rule #4)
- **Source:** CLAUDE.md Iron Rules
- **Binding for:** `_aos/roadmap.yaml`
- **Rule:** team_100 (smallfarmsagents) is sole writer. No other team writes — including sfa_build, team_190, team_191. Roadmap gate transitions are recorded by team_100 commit after each gate event.

---

## §G — Refresh meta

| Refresh # | Date | Trigger | New items added | Items resolved | Items promoted |
|-----------|------|---------|-----------------|----------------|----------------|
| 1 (initial) | 2026-05-23 | SFA-S003-P002-WP-C — initial catalog creation | 17 (8 in §A, 3 in §B, 3 in §C, 2 in §D, 11 in §E backfill) + 5 binding policies in §F | 11 backfilled from session history | A.3 (mobile parity) likely consumed by WP-B; C.1 (Tend tables) may be partially consumed by WP-A |

---

## §H — Open the next milestone safely

When opening **S004 (calculator + community features)**:

1. Read this file (§A, §B, §C in particular)
2. Decide which §A items become S004 scope vs deferred-further
3. Mark any item that becomes an S004 WP as **PROMOTED** with its WP id in this file's §E
4. Open §B items as parallel operational WPs (or absorb into S004 ops)
5. WP-A2 (farmer calculator, deferred to S004 per project notes line 41) is the natural S004 anchor — uses §C.1 Tend data + crop book + market index
6. WP-A1 (moderated submissions, also deferred to S004) is the community-features anchor

Don't open S004 without doing #1.

---

*Catalog v1.0.0 — authored 2026-05-23 by team_100 (smallfarmsagents) under WP `SFA-S003-P002-WP-C`.*
*Refreshed at every P-program closure per §F.1.*
