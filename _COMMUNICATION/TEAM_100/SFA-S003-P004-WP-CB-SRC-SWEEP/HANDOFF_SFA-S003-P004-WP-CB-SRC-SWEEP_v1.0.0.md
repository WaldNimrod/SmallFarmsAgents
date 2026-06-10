---
id: HANDOFF_SFA-S003-P004-WP-CB-SRC-SWEEP_v1.0.0
from: team_100 (the session that shipped WP-CB-CONTENT + the source-integration audit)
to: team_100 (implementing session)
date: 2026-06-09
type: session-handoff (aos_handoff full 100)
wp: SFA-S003-P004-WP-CB-SRC-SWEEP
project: SFA-S003-P004
gate: L-GATE_E → L-GATE_SPEC → build
status: REGISTERED — awaits SPEC
engine: Claude Code (builder) — validator MUST differ (IR#1/#5)
---

# HANDOFF — SFA-S003-P004-WP-CB-SRC-SWEEP — team_100 → team_100

**Complete the scan + integration of ALL existing source data (files + sources we provided or
collected), including live deployment + integrity check.**
**Track:** A · **Effort:** MEDIUM-LARGE (extraction + importers + ingest + verify) · **Risk:** MEDIUM (licensing + data quality)

## 0. ⭐ Why this WP exists (team_00 directive)

A source-integration audit during WP-CB-CONTENT found that **collected/extracted data was NOT fully in the DB**.
Most was integrated this session (see §2), but a tail of **raw, never-extracted source files** remains. team_00:
"verify ALL the information we have was integrated **before** going out for another research round." This WP
closes that gap end-to-end: extract → import → DB → (where public) deploy → integrity-check.

## 1. What is ALREADY DONE (this session — do NOT redo)

- **WP-CB-CONTENT** (LOD500_LOCKED, LIVE on sfa.nimrod.bio): 25 crops narrative content + provenance.
- **4 JMF FT specialty guides integrated** → `crop_knowledge_notes` (internal-only): phytoprotection,
  biopesticide, flameweed, nurseryseeding (fixtures promoted to `data/jmf/extracted/jmf_ft_*/`; 10 notes / 7 crops).
- **jmf_book fixed + integrated** → 45 knowledge notes / 20 crops + 2 source-values (was silently 0; the
  list-of-dicts→Text bug poisoned the whole NI transaction — now fixed in jmf_book + jmf_book_alt).
- **NI ingestion hardened**: per-importer + per-path SAVEPOINTs in `_run_ni_ingestion` (one bad importer can
  no longer abort the rest).
- **content_loader `_name_he` override** (Beans→שעועית, Basil→בזיל) — both LIVE.
- **`_slugify` annotation-strip** — clean slugs `/beans/ /scallions/ /salad-mix/ /pac-choi/` LIVE.
- "169 NULL-name_en varieties" = NOT a defect (real Hebrew-named cultivars; resolved by `order_by(is_default desc,id).first()`).

## 2. Scope — what to integrate (the remaining tail)

**A. Unextracted raw source files (on disk, no extractor, no importer → 0 rows in DB):**
| File | Size | Notes |
|------|------|-------|
| `data/external_sources/jmf_extension/L14_FT_FINALE_NURSERYSEEDING.pdf` | 212K | Full JMF nursery-seeding source (the `jmf_ft_nurseryseeding` data dir only has 2 fixture crops — L14 likely covers more). **Licensing: JMF → internal-only `crop_knowledge_notes`.** |
| `data/external_sources/jmf_extension/L26_BEIN_HATLAMIM_hebrew.pdf` | 92K | Hebrew growing guide ("בין התלמים"). |
| `data/external_sources/israeli/L43_customer_leafy_greens.xlsx` | 212K | IL customer leafy-greens data. |
| `data/external_sources/israeli/L44_israel_organic_greens.pdf` | 3.1M | Israeli organic greens guide. |
| `data/external_sources/israeli/L45_2017_data_summary.xlsx` | 60K | 2017 data summary (likely Tend/farm). |
| `data/external_sources/misc_investigate/L38_libretto_orto_italian.pdf` | 2.5M | Italian veg guide — **low priority / candidate to deprioritize**. |
| `data/external_sources/misc_investigate/L39_mesclun_guide.pdf` | 96K | Mesclun/salad-mix — low priority. |

**B. `jmf_book_alt`** — importer wired (`data/jmf/extracted/jmf_book_alt/`, empty) but the alternate
"The Market Gardener" edition PDF is **not present/extracted**. Either locate + extract it, or DEPRIORITIZE
(file a DECISION) since the main `jmf_book` edition is now loaded.

**C. Re-run the FULL audit** (the method below) to confirm EVERY `data/` source maps to an importer that is
wired into `seed.py` AND has rows in the DB. Catch anything else (the audit DB-cross-check already corrected
one false "zero" — always verify against the live DB, not file inspection).

## 3. Method (proven this session)

1. Enumerate every source under `data/` (recurse). For each: extracted-JSON / raw-PDF/xlsx / empty.
2. Map each → its importer (grep importers for the `data/...` path) → seed.py wiring (`--all` block or fast-path).
3. **Cross-check the live DB** (`crop_knowledge_notes` by source/note_type; `crop_variety_source_values` by
   source; `crop_field_enrichment` / `crop_attribute`). DB is the source of truth.
4. For each gap: write an extractor (PDF/xlsx → `_table.json`/per-crop JSON in the right `cache_dir`), confirm
   the importer reads it, wire into `seed.py` if not already, run, verify rows.
5. Crop keying: `JMF_CROP_MAP[crop_jmf_en] → name_he → crops.id`; for DB-name mismatches use the
   `content_loader` `_name_he` override pattern (or the importer crop-resolution idiom).

## 4. Deploy + integrity check (the "live system" + "תקינות" requirement)

- **Public content** (any new `crop_content` / enrichment / attributes): `seed` → `sfa_ingest_push --table …`
  (HMAC, HTTPS, no FTPS) → production smoke (`qa_probe.mjs`, authored crop simple+deep, empty-states intact).
- **Internal knowledge** (`crop_knowledge_notes`, JMF/licensed): DB-only — **NEVER published** (not in the
  ingest allowlist; firewall-tested). Verify it stays internal.
- ⚠ **uPress `/admin/migrate` token is empty by design** (cleared after use). Only needed for NEW delivery
  migrations — set→use→clear via FTPS (team_00 authorizes the `.env` write; Mac IP must be open on uPress).
- Integrity: `pytest tests/crop_book` 0 fail · delivery `vendor/bin/phpunit` 0 fail (copied `vendor/`) ·
  `validate_aos.sh` 0 FAIL · production smoke.

## 5. Architecture / cutover canon (anti-drift — verified 2026-06-09)

The crop-book pipeline runs **ENTIRELY from the Mac**: local Docker `oma-postgres:5433` → `alembic`/`seed` →
FTPS `lftp` deploy + HMAC push to uPress. **waldhomeserver is NOT in the SFA deploy path** (it is the מחירון /
price-index pipeline only). Do not gate on SSH-to-server. The classifier blocks **dumping `.env` secrets**, not
the deploy/DB tools (they load `.env` internally). See `documentation/02-architecture/sfa-delivery-tier.md` §1A.

## 6. Startup + cautions

Read `CLAUDE.md` → `_aos/governance/team_100.md` → this handoff. **Use a `git worktree` per WP** — a parallel
session moved branch refs in the shared checkout during WP-CB-CONTENT (recovered, but costly). DB online → API
for hub mutations; spoke roadmap is file-based (ADR034 R9). Cross-engine L-GATE_VALIDATE at the end (validator ≠
Claude Code). Verdict/closure return to **this team_100 origin**.

## 7. Verdict / done

Every source file under `data/` is either **integrated into the DB** (with DB-confirmed rows) or **explicitly
deprioritized via a DECISION artifact**; any new public data is **LIVE on sfa.nimrod.bio** and smoke-verified;
internal/licensed data stays internal; `validate_aos.sh` 0 FAIL + tests green. Cross-engine L-GATE_VALIDATE PASS → LOD500_LOCK.

## 8. Inputs / references

- Audit findings: this WP §2 + the WP-CB-CONTENT `COMPLETION_REPORT` advisories + `_archive/SFA-S003-P004-WP-CB-CONTENT/ARCHIVE_MANIFEST.md`.
- Importer patterns: `organic_market_agent/crop_book/importer/ni/*` (FT importers, `ni_importer.NIImporter`), `importer/content_loader.py`.
- Seed orchestrator: `organic_market_agent/crop_book/importer/seed.py` (`--all` + fast-paths).
- Ingest/deploy: `publisher/sfa_ingest_push.py`, `scripts/ftp_deploy_sfa_ui.sh`, `documentation/05-admin-and-operations/UI_DEPLOY_RUNBOOK.md`.
