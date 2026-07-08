# L-GATE_VALIDATE MANDATE — SFA-S003-P004-WP-CB-CONTENT — team_190 — v1.0.0

**Date:** 2026-06-09
**From:** team_100 (builder — Claude Code)
**To:** team_190 (validator — **MUST be a non-Claude engine**: Cursor/Composer or Codex; IR#1/#5)
**WP:** SFA-S003-P004-WP-CB-CONTENT · **Gate:** L-GATE_VALIDATE · **Branch:** `main` @ `161f698`

> Paste the block below as the opening prompt of a fresh **non-Claude** session in this repo
> (`/Users/nimrod/Documents/SmallFarmsAgents`). Constitutional rule: the validator engine must
> differ from the builder engine (Claude Code) — do not run this in Claude Code.

---

```
You are team_190 — the constitutional cross-engine validator for AOS. Builder was Claude Code;
you are NOT Claude Code (IR#1/#5). Perform L-GATE_VALIDATE for SFA-S003-P004-WP-CB-CONTENT on
branch main (@161f698) in /Users/nimrod/Documents/SmallFarmsAgents.

WHAT THE WP DELIVERS: multi-source narrative prose for the crop book, stored WITH source
provenance. Postgres crop_content (canonical = Normal mode) + crop_content_source (per-source =
Deep mode), mirroring the crop_attribute provenance shape. content_type ∈ {story, care_watering,
care_fertilizing, care_pests}. Delivery: CropBookViewController::detail reads the MySQL mirrors;
book_crop.php renders the canonical in Normal mode and per-source text + EX/PR/WR attribution
pills in Deep mode (?depth=deep); honest empty-states preserved for un-authored crops/types.
LICENSE INVARIANT (team_00): every published body is OUR own new Hebrew synthesis — never
verbatim copyrighted source; the public path has zero read of crop_knowledge_notes.

READ FIRST:
- _COMMUNICATION/team_100/SFA-S003-P004-WP-CB-CONTENT/SPEC_2026-06-09_v1.0.0.md  (architecture + §7 packet)
- _COMMUNICATION/team_100/SFA-S003-P004-WP-CB-CONTENT/COMPLETION_REPORT_2026-06-09_v1.0.0.md

RE-EXECUTE INDEPENDENTLY (do not trust the builder's numbers — reproduce them):
VC-1  Backend tests: `pytest tests/crop_book/test_migration_061.py tests/crop_book/test_content_loader.py tests/crop_book/test_ni_publisher_isolation.py -q` → all pass.
VC-2  Full backend suite: `pytest tests/crop_book -q` → 0 failed.
VC-3  Delivery tests: in sfa_delivery, with a COPIED vendor/ (cp -RL, NOT the symlink — worktree autoload trap), `vendor/bin/phpunit --filter 'IngestContentMirror|CropContent'` then the full `vendor/bin/phpunit` → 0 failed. Confirm the 4 content route tests assert: Normal renders canonical with NO per-source leak; Deep renders per-source raw_text + srcpill--ex/pr/wr + attribution link; un-authored crop keeps the empty-state; tables-absent still 200.
VC-4  License firewall: confirm content_loader.py + content_models.py have no import/use of CropKnowledgeNote, and the publisher fetchers (_fetch_crop_content[_source]) read only crop_content tables. `pytest tests/crop_book/test_ni_publisher_isolation.py -q`.
VC-5  Migration 061 reversibility: upgrade then downgrade on a scratch SQLite (see test_migration_061.py pattern) → tables created then dropped cleanly.
VC-6  Honest data: an un-authored crop/content_type renders byte-identically to pre-WP (no fabricated canonical; field_state honest).
VC-7  AOS validation: `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` → 0 FAIL.
VC-8  Two-tier write isolation: confirm authoring/load/push are backend-only; the delivery tier never writes this content (no dataEntry path).
VC-9  Production smoke (AFTER team_00 applies uPress migration 006 + runs the content push): on sfa.nimrod.bio, an authored crop (e.g. /crop-book/lettuce/) at ?depth=simple shows the canonical in hero + care topics with zero horizontal overflow (qa_probe.mjs), and ?depth=deep additionally shows per-source bodies + EX/PR/WR pills + attribution links; an un-authored crop still shows the empty-state. If 006/push not yet applied, record VC-9 as PENDING and validate VC-1..VC-8 on the code+content.

VERDICT: write _COMMUNICATION/team_190/SFA-S003-P004-WP-CB-CONTENT/VERDICT_..._L-GATE_VALIDATE_v1.0.0.md
with PASS/FAIL per VC-1..VC-9 on independent re-execution, your engine name (proving non-Claude),
and an overall verdict. Return the verdict to the team_100 origin → on PASS, team_100 archives +
sets LOD500_LOCKED.
```

---

**Builder evidence (for cross-check, not to be trusted blindly):** backend 767 pass / delivery 233 pass; merged-tree pre-push suite 1076 pass/15 skip; 25 crops / 77 units / 85 variants, 25/25 license-verified.
