---
id: DECISION_WP-B-OPEN-QUESTIONS_2026-05-25_v1.0.0
from: team_00 (Principal)
to: [team_110, team_190]
date: 2026-05-25
type: DECISION
program: SFA-S003-P002-WP-B
project: smallfarmsagents
authority: team_00 Principal (CLAUDE.md Directory Authority)
brief_ref: AOS_decide invocation 2026-05-25 — 5 questions presented; user response per question below
authorizes:
  - Q1 modify: text-file input architecture for B2 (not raw PDFs)
  - Q2 (B): UI follow-up decided AFTER B2 cache populated + reviewed
  - Q3 (A): Tend_2023+ via re-run pattern with --year flag (already in spec)
  - Q4 modify: specific Hebrew terminology values for Parsnips + Shallots; Tomatillos confirmed as-is
  - Q5 modify: ALL JMF PDF sources IN scope for B2 (3 → 6 sources)
---

# DECISION — WP-B Program Open Questions (5)

## 1. Q1 — Live JMF PDF extraction architecture: MODIFY

**Original question:** When should team_00 run `extraction_runner.py` to populate the real cache? (A=after B2 close, B=after B2+B3 close, C=defer)

**team_00 response:**
> "קריאת pdf - אני יבצע המרה של המידע. ואספק קבצי טקסט"
> ("PDF reading — I will perform the conversion of the information. And I will provide text files.")

**Disposition:** Q1 is reframed as a **scope MODIFY** rather than an A/B/C choice. The architectural change: B2's `extraction_runner.py` reads **text files** (provided by team_00), not raw PDFs.

**Specific implications for B2 LOD400:**
- New input path: `data/jmf/raw_text/<source_name>/<crop_name_en>.txt` (text files committed by team_00 alongside the spec)
- `extraction_runner.py` no longer needs `pdftotext` binary or PDF file access — it reads text files + calls Anthropic API for structured JSON extraction
- §6 risk register R-01 ("pdftotext not installed") becomes obsolete — REMOVED
- §13 Open question #1 (`pdftotext install`) becomes obsolete
- The original "manual prepare step" still exists — team_00 still runs `extract_jmf_ni.py` manually post-merge, just against text files instead of PDFs

**Q1 timing question** (when to run extraction): the architectural change resolves it implicitly — extraction can run **as soon as text files are provided by team_00**, independent of B2/B3 closure ordering. Per the principle "work sequentially with what we have" (Q3 wording), team_00 will provide text files and run extraction once B2 LOD500_LOCKS. Effectively maps to original **Option B** (after B2 close) but on team_00's actual content-availability cadence.

## 2. Q2 — UI surface follow-up scoping: B (review first)

**team_00 response:** "b"

**Disposition:** **Option B (review first, then decide).** After B2 cache is populated + DB rows produced + content reviewed, team_00 will assess content quality and decide whether to open a WP-C UI series. No UI WP is opened proactively.

**Implication:** B2 + B3 close without `views.py` modifications. `crop_knowledge_notes` + `crop_harvest_stats` rows accumulate in DB; display routing deferred.

## 3. Q3 — Tend_2023+ future ingestion: A (re-run pattern)

**team_00 response:**
> "כרגע זה המידע שיש לנו ואיתו צריך לעבוד. ולממש את כל המידע ברצף."
> ("Currently this is the data we have and we need to work with it. And realize all the information sequentially.")

**Disposition:** Effectively **Option A (re-run pattern)** — the existing B3 importer with `--tend-overlay-year 2023` covers future years. No per-year WP overhead. The "sequentially" intent reinforces a clean linear ingestion pattern rather than ad-hoc per-year cycles.

**Implication:** B3 LOD400 §13 open question #5 is RESOLVED with Option A. No spec change required.

## 4. Q4 — Hebrew terminology residuals: MODIFY (specific values per term)

**team_00 response:**
> "1. Tomatillos - מאשר תעתיק פשוט
>  2. Parsnips - שורש פטרוזילה
>  3. Shallots - בצלצלי שאלוט"

**Disposition:** Tomatillos confirmed as-is (current `תומאטיו` is acceptable phonetic transliteration). Parsnips + Shallots get new Hebrew values. Effectively **Option B (small follow-up patch)** with specific decisions:

| Key | Before (current) | After (team_00) | Status |
|-----|-------------------|------------------|--------|
| `Tomatillos` | `תומאטיו` | `תומאטיו` (confirmed) | NO CHANGE |
| `Parsnips` | `גזר לבן` (colloquial) | `שורש פטרוזילה` ("parsley root" — literal) | CHANGE |
| `Shallots` | `שאלוט` (transliteration) | `בצלצלי שאלוט` ("shallot small-onions") | CHANGE |

**Implementation plan:** Defer the 2 actual changes to a small **WP-B1-patch02** filed AFTER B2 + B3 both LOD500_LOCKS, to avoid mid-flight churn on `constants.py` while B2/B3 builders are active. Scope: ~2-line spec patch + ~2-line constants.py edit + AC-03 Counter assertion update (no impact — Parsnips/Shallots aren't part of any duplicate-target group).

The DECISION values above are FROZEN here as the authoritative source-of-truth. The patch02 spec will reference this DECISION file by ID.

## 5. Q5 — Alternate JMF ebook + other FT PDFs: MODIFY (include ALL)

**team_00 response:**
> "כל מידע שיש לנו מjm חייב להיות חלק!! הכול כולל הכול זה המידע הכי חשוב ואיכותי שיש לנו."
> ("All information we have from JMF MUST BE INCLUDED!! Everything including everything is the most important and high-quality information we have.")

**Disposition:** **Strong scope EXPANSION for B2** — include ALL JMF PDF sources in scope, not just the 3 originally proposed:

| Source | Status before | Status after |
|--------|---------------|--------------|
| `THEMARKETGARDENEREBOOK (from macBook Air - nimrod).PDF` (240pp main edition) | IN SCOPE | IN SCOPE (unchanged) |
| `THE MARKET GARDENER_*.PDF` (209pp alternate edition) | OUT OF SCOPE (§3) | **IN SCOPE** |
| `FT_FINALE_FLAMEWEEDING*.PDF` (3pp) | IN SCOPE | IN SCOPE (unchanged) |
| `FT_FINALE_TABLEAUAPPLICATIONBIOPESTICIPE*.PDF` (5pp biopesticide table) | IN SCOPE | IN SCOPE (unchanged) |
| `FT_FINALE_PHYTOPROTECTION*.PDF` (3pp) | OUT OF SCOPE (§3) | **IN SCOPE** |
| `FT_FINALE_NURSERYSEEDING*.PDF` (13pp) | OUT OF SCOPE (§3) | **IN SCOPE** |

**Total sources after:** 6 (was 3). **Total NIImporter subclasses:** 6 (was 3).

**Specific implications for B2 LOD400 v1.1.0:**
- §2.1 module structure: 6 importer files under `ni/` (was 3)
- §3 migration 045 note_type CHECK constraint enum: add ≥3 new values (e.g., `phytoprotection_substance`, `phytoprotection_application`, `nursery_seeding_process`) to handle the new sources' content types
- §4 ORM `NOTE_TYPE_VALUES` tuple grows accordingly
- §5 JSON cache schema: 6 sub-directories (one per source)
- §6 extraction_runner: 6 per-source dispatch functions
- §7 NIImporter subclasses: 6 concrete classes (re-named per actual `NIImporter` base — see B2 BLOCKER F-S-B2-01)
- §10 test inventory: +3 fixture sets (one per new source); +3 per-source parser test files
- §15 deliverables: expanded CREATE list

**Rationale (team_00's view):** the entire JMF MasterClass corpus is the highest-quality + most important data available; double-extraction noise concerns (the original rationale for excluding the 209pp alternate edition) are outweighed by the comprehensive-data principle. team_00 will manually review the resulting JSON cache for noise.

**Risk acknowledged:** the 209pp alternate edition may contain content overlapping with the 240pp main edition. Extraction will produce duplicates if both are processed. **Mitigation:** team_00 will manually arbitrate post-extraction (review the two source caches per crop and select the canonical one). This is documented in the v1.1.0 risk register.

---

## Summary table

| Q | Original options | team_00 decision | Implementation impact |
|---|------------------|-------------------|------------------------|
| Q1 | A / B / C | MODIFY (text files) | B2 v1.1.0 §6 reframe extraction_runner input |
| Q2 | A / B / C | B (review first) | No spec change; deferred decision |
| Q3 | A / B / C | A (re-run pattern) | No spec change; resolves §13 OQ #5 |
| Q4 | A / B / C | MODIFY (specific values) | Defer to WP-B1-patch02 after B2+B3 close |
| Q5 | A / B / C | MODIFY (ALL JMF sources) | B2 v1.1.0 scope expansion: 3→6 sources |

## Authorization chain

This DECISION is filed under team_00 Principal authority (CLAUDE.md Directory Authority) and:

1. **Authorizes B2 LOD400 v1.1.0 scope changes** (Q1 + Q5) — team_110 may issue v1.1.0 + R2 mandate without further team_00 confirmation
2. **Authorizes WP-B1-patch02** scope (Q4 Hebrew fix) for filing after B2+B3 LOD500_LOCKS — team_110 may register patch02 in roadmap under L-GATE_E in-session grant pattern (same as patch01)
3. **Resolves** Q2, Q3 (no further action required)

## Next actions for team_110

1. Update B2 LOD400 → v1.1.0 (apply Q1 + Q5 modifications + fix the 4 R1 findings).
2. Issue B2 R2 mandate to team_190 citing this DECISION + the v1.1.0 changes.
3. For B3 (PASS_WITH_FINDINGS already): proceed to Phase 4 transition. Apply F1 carry-fix (path versioning) as a small v1.0.1 cleanup before LOCK.
4. After B2 + B3 LOD500_LOCK: register WP-B1-patch02 for Hebrew terminology corrections per Q4.

---

*DECISION filed 2026-05-25 by team_110 (Claude Opus 4.7) recording team_00's in-session AOS_decide responses.*
*team_00 Principal authority — CLAUDE.md Directory Authority table.*
