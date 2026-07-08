# ARCHIVE_MANIFEST — SFA-S003-P004-WP-CB-SRC-SWEEP

**Archived:** 2026-06-11 · **By:** team_100 (ADR042 closure) · **Terminal state:** LOD500_LOCKED
**Iron Rule #15 / POST_GATE_ARCHIVE_PROCEDURE** · L-GATE_VALIDATE PASS → archive on closure (ADR042 Step 1).

## Outcome

Source-data tail integration **plus** a crop-taxonomy / data-integrity remediation (team_00 directed the
second mid-flight; both validated under one unified L-GATE_VALIDATE).

**A — WP-CB-SRC-SWEEP (source sweep).** A full DB-verified audit confirmed the crop-book corpus was already
comprehensively integrated (~50 sources); only two of the remaining raw files held genuine value:
- **L39 (JMF Masterclass mesclun):** new variety **חסה בייבי** under crop #31 (עלי בייבי) + cultivar source
  value (`NI:jmf_ft_mesclun_v1`) + 4 internal species notes (JMF → internal-only firewall).
- **L45 (real IL-farm-2017 workbook):** cherry-pick of the `נתוני בסיס` sheet → `OP:il_farm_2017_l45`
  (62 source-values: days_to_maturity / spacing_in_row_cm / rows_per_bed + 22 internal notes / 22 crops).
  Cannabis / price / budget / trees / calendar sheets intentionally excluded.
- **Deprioritized via DECISION:** L43 (business economics), L44 (OCR'd LED spec sheet), L26 (bank receipt),
  L38 (empty Italian OCR), jmf_book_alt (no source PDF).
- **Publisher:** added `--crop-ids` / `--slugs` scoped-deploy capability (crop-keyed tables only).

**B — Crop taxonomy + data-integrity remediation (team_00 2026-06-10).** Rule: *"different agricultural
product = different crop."*
- Dedup: `Basil→בזיל`, `Rutabaga→לפת`, `Salad Mix→עלי בייבי`, `Heirloom Tomato→עגבנייה` now resolve to
  canonical crops (no minting); keep-crops (Celeriac / Chinese Cabbage / Hot Pepper / Brussels Sprouts)
  created with correct `name_en` + sibling family. Local DB: **77 → 73 crops, 0 duplicate-name crops**;
  merged cultivars preserved (Aroma 2 F1 + Nufar → בזיל, Joan → לפת).
- `seed --all` now auto-strips the 5 canon-forbidden DERIVED fields post-seed (closes the AC-05 re-seed gap).
- `uc_davis_postharvest`: fixed a systemic `he_labels[]`↔`samples[]` positional misalignment (+ broken
  padding) that gave **31 crops** wrong storage data; `name_he` is now bound intrinsically per sample row.
- New canon doc `documentation/03-data-and-schema/DATA_INTEGRITY_CANON.md`.

**Deploy (LIVE, scoped, from the Mac).** salad-mix +`חסה בייבי` (variety count 12→13); בזיל +cultivars (8→10);
לפת +Joan (2→3); the 31-crop uc_davis postharvest correction. Production stayed at **70 crops** (no stale /
duplicate crops deployed). qa_probe overflow=false on all checked pages.

## Gate record

| Gate | Result | Validator | Engine |
|------|--------|-----------|--------|
| L-GATE_E (REGISTER) | REGISTER | team_00 | — |
| L-GATE_SPEC | PASS | team_100 | Claude Code |
| L-GATE_BUILD | PASS | team_100 | Claude Code (builder) |
| L-GATE_VALIDATE (R1) | FAIL (AC-05 derived fields) → remediated R2 | team_190 | Cursor (non-Claude — IR#1/#5) |
| L-GATE_VALIDATE (R2, unified) | **PASS** (VC-1..VC-12) | team_190 | Cursor (non-Claude — IR#1/#5) |
| DEPLOY | **LIVE** | team_100 | Mac → HMAC → uPress |

**Verdict artifacts (PASS, 2 non-blocking advisories):**
- `_COMMUNICATION/TEAM_190/SFA-S003-P004/WP-CB-SRC-SWEEP/WP-CB-SRC-SWEEP_LGATE-V_VERDICT_v1.0.0.md`
- `_COMMUNICATION/TEAM_100/MSG-team190-to-team100-SFA-S003-P004-WP-CB-SRC-SWEEP-LGATE-V-VERDICT-2026-06-11.md`

Mandate: `VALIDATION_MANDATE_2026-06-11_v2.0.0.md` · Spec: `SPEC_2026-06-11_v1.0.0.md` ·
Decision: `DECISION_DEPRIORITIZED_SOURCES_2026-06-11_v1.0.0.md` · Build report: `COMPLETION_REPORT_2026-06-11_v1.0.0.md` ·
Taxonomy report: `_COMMUNICATION/TEAM_100/REPORT_CROP_TAXONOMY_ALIGNMENT_2026-06-11_v1.0.0.md`.

## Commit SHAs (branch `feat/wp-cb-src-sweep`)

| Item | SHA |
|------|-----|
| SRC-SWEEP build (L39 + L45 + publisher scoping) + scoped deploy | `0e0edbd` |
| R2: strip forbidden DERIVED fields (AC-05) + corrected baseline | `07f3b67` |
| Taxonomy: prevent minting dups/derived (maps + keep-crop identity + auto-strip) | `20b8998` |
| Heirloom → עגבנייה merge | `9d33099` |
| uc_davis postharvest misalignment fix (31 crops) | `dfea7e6` |
| Unified validation mandate v2.0.0 | `2f102fe` |

## Validation evidence (team_190, independent)

VC-1 backend 798 pass / 1 skip (AC-05 8/8) · VC-2 delivery 233/233 · VC-3 validate_aos 0 FAIL ·
VC-4..VC-7 SRC-SWEEP content + firewall + scoping · VC-8 73 crops/0 dups · VC-9 auto-strip ·
VC-10 postharvest corrected · VC-11 canon doc · VC-12 prod 70 crops + qa_probe 6/6 overflow=false.

## Deferred (non-blocking, post-lock)

- 3 thin keep-crops (celeriac / chinese-cabbage / hot-pepper) held from production until enriched — local-only.
- `idan_planner.py` still emits `yield_per_m2_kg` (neutralised by the post-seed auto-strip) — low-priority cleanup.
