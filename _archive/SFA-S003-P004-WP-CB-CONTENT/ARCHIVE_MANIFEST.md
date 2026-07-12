# ARCHIVE_MANIFEST — SFA-S003-P004-WP-CB-CONTENT

**Archived:** 2026-06-09 · **By:** team_100 (ADR042 closure) · **Terminal state:** LOD500_LOCKED
**Iron Rule #15 / POST_GATE_ARCHIVE_PROCEDURE** · L-GATE_VALIDATE PASS → archive on closure (ADR042 Step 1).

## Outcome

Multi-source **narrative crop-book content with provenance**. A content unit = `(crop, content_type)`,
`content_type ∈ {story, care_watering, care_fertilizing, care_pests}`, stored in two new Postgres tables
(`crop_content` canonical + `crop_content_source` per-source) mirroring the `crop_attribute` provenance
shape. **Normal mode** serves OUR consolidated Hebrew canonical; **Deep mode** (`?depth=deep`) serves the
full text per source with EX/PR/WR attribution pills + links. Honest empty-states preserved for un-authored
crops. **License invariant (team_00):** every published body is OUR own new Hebrew synthesis — never verbatim
copyrighted source; the public path has zero read of `crop_knowledge_notes` (firewall-tested).

**Content:** 25 crops · 77 content units · 85 source variants, authored via an orchestrated
author→adversarial-verify Workflow (50 agents; 25/25 license-verified, 0 flagged). **LIVE on
`https://sfa.nimrod.bio`** — cutover entirely from the Mac (local `oma-postgres:5433` → FTPS → uPress).

## Gate record

| Gate | Result | Validator | Engine |
|------|--------|-----------|--------|
| L-GATE_E (REGISTER) | REGISTER | team_00 | — |
| L-GATE_SPEC | PASS | team_100 | Claude Code |
| L-GATE_BUILD | PASS | team_100 | Claude Code (builder) |
| L-GATE_VALIDATE | **PASS** (VC-1..VC-8, R1 clean; VC-9 satisfied post-deploy) | team_190 | Cursor / Composer (non-Claude — IR#1/#5) |
| DEPLOY | **LIVE** | team_100 | Mac → FTPS/HMAC → uPress |

**Verdict artifact (PASS, no findings):**
`_COMMUNICATION/TEAM_190/SFA-S003-P004-WP-CB-CONTENT/VERDICT_SFA-S003-P004-WP-CB-CONTENT_L-GATE_VALIDATE_v1.0.0.md`
(archived copy: `team_190/VERDICT_…_v1.0.0.md`). Spec: `SPEC_2026-06-09_v1.0.0.md`. Build report:
`COMPLETION_REPORT_2026-06-09_v1.0.0.md`.

## Commit / deploy SHAs

| Item | SHA |
|------|-----|
| Build (pipeline + tests) | `56bc693` |
| Content (25 crops) + SPEC | `e9022bd` |
| Completion report | `e25679f` |
| Merge → main | `161f698` |
| Validated HEAD (team_190) | `50c5a1a` (docs-only after merge; `161f698` ancestor) |
| DEPLOY=LIVE (roadmap) | `faf3b82` |

## Evidence

- **Builder (team_100, Claude Code):** backend `pytest tests/crop_book` **767 passed / 1 skipped**; delivery
  `vendor/bin/phpunit` **233 passed**; migration 061 up/down reversible on SQLite; license firewall tests
  green; `validate_aos.sh` **0 FAIL**. Content loader smoke: 25 crops → 77 `crop_content` + 85
  `crop_content_source` rows.
- **Cross-engine L-GATE_VALIDATE (team_190, Cursor/Composer — IR#1/#5):** independent reproduction at
  `50c5a1a`: VC-1 17 passed · VC-2 767/1 · VC-3 delivery 8 (filtered) + 233 (full) on a copied tree with
  physical `vendor/` · VC-4 firewall intact · VC-5 061 reversible · VC-6 empty-states locked · VC-7
  `validate_aos.sh` 31 PASS/21 SKIP/0 FAIL · VC-8 two-tier isolation. **No BLOCKER/MAJOR/MINOR.**
- **Production (team_100, post-verdict — closes VC-9):** local `oma-postgres` migrated to 061 + content
  loaded (22/25 crops resolved → 68/74 rows; 3 unseeded skipped). uPress delivery migration `006_crop_content`
  applied via token-gated `/admin/migrate` (token set→used→**cleared**, `.env` restored byte-identical, site
  200 throughout). HMAC content push **0 rejected**. Smoke: authored crops (peppers/carrots/lettuce/kale/
  beets/cabbage/spinach…) render Normal canonical hero + care "מדריך SFA" + Deep per-source EX/PR/WR pills;
  un-authored crops keep honest empty-states. `qa_probe.mjs` **overflow=false / pass=true** mobile(375)+desktop
  on 3 content-heavy Deep pages.

## Advisories (non-blocking, carried forward)

- 3 hydro-only crops (פאק צ'וי / קולרובי / רוקט) deferred — geresh filename mismatch; empty-states preserved.
- Beans (Bush/Pole) authored but orphaned — `JMF_CROP_MAP` key `שעועית שיחית`/`מטפסת` ≠ DB generic `שעועית`.
- Data-integration audit: 4 JMF FT guides (phytoprotection/biopesticide/flameweed/nurseryseeding) sit in
  `tests/fixtures/` but never promoted to `data/` → 0 rows in `crop_knowledge_notes`. Recommend integrating
  before the next research round (separate follow-up).

## Step 3 (multi-engine propagation)

**Skipped — verified:** no `core/governance/` modified during this WP (`git log 161f698^..HEAD -- _aos/governance/ core/governance/` empty).

## Addendum — 2026-07-09 (Domain Doc & Archival Sweep, DOMAIN_DOC_ARCHIVE_SWEEP_PROCEDURE_v1.0.0)

Despite this manifest recording an archive on 2026-06-09, two artifacts were found still fully live under
`_COMMUNICATION/` (never actually moved at that time):

| Former path | Archived path |
|-------------|---------------|
| `_COMMUNICATION/TEAM_100/SFA-S003-P004-WP-CB-CONTENT/COMPLETION_REPORT_2026-06-09_v1.0.0.md` | `_archive/SFA-S003-P004-WP-CB-CONTENT/team_100/COMPLETION_REPORT_2026-06-09_v1.0.0.md` |
| `_COMMUNICATION/TEAM_190/SFA-S003-P004-WP-CB-CONTENT/VALIDATION_MANDATE_2026-06-09_v1.0.0.md` | `_archive/SFA-S003-P004-WP-CB-CONTENT/team_190/VALIDATION_MANDATE_2026-06-09_v1.0.0.md` |

**Not moved (left in place, INV-3 — never delete):** `_COMMUNICATION/TEAM_190/SFA-S003-P004-WP-CB-CONTENT/VERDICT_SFA-S003-P004-WP-CB-CONTENT_L-GATE_VALIDATE_v1.0.0.md`
is a byte-identical duplicate of the file already archived at `team_190/VERDICT_…_v1.0.0.md` (diff confirmed
identical). No new content to move; flagged here rather than silently overwritten or deleted. `roadmap.yaml`
gate_history (L-GATE_VALIDATE) embedded path repointed to the archived copy same session.

**Pre-existing gap (not introduced by this sweep, not fixed — no document content invented):** `spec_ref` in
`roadmap.yaml` for this WP points to `_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-CONTENT/SPEC_2026-06-09_v1.0.0.md`,
which does not exist anywhere in the tree (not live, not archived) despite this manifest's line 32 citing it as
an evidence artifact. Flagged as ESCALATE (subtype `MISSING-SPEC-ARTIFACT`) in the sweep report — Phase 1 D-2/D-3
gap, authoring/locating the correct SPEC file is a judgment task, not weak-engine-mechanical.

**2026-07-12 disposition (team_60):** WAIVED per `CENTRALIZED_SWEEP_REVIEW_team_120_M11_FLEET_HYGIENE_2026-07-10_v1.0.0.md`
§6 — the file is genuinely gone/never produced (pre-existing historical gap), not repointable to a real artifact.
A matching `notes:` addendum was added to the `SFA-S003-P004-WP-CB-CONTENT` row in `_aos/roadmap.yaml`. Per that
review's §10 item 3, this waiver requires **team_100 sign-off** to count toward a certified 0-FAIL — pending as of
this pass.

Executed by: sweep session — see `_COMMUNICATION/team_120/SWEEP_REPORT_smallfarmsagents_2026-07-09_v1.0.0.md`.
Not committed (left staged per procedure — team_60 to review/commit).
