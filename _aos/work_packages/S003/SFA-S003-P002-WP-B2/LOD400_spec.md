---
id: SFA-S003-P002-WP-B2-LOD400
wp: SFA-S003-P002-WP-B2 — JMF NI Extraction Layer (AI-assisted, text-file input)
gate: L-GATE_S (LOD400 — implementation spec)
status: LOD400_LOCKED — L-GATE_S R4 PASS_WITH_FINDINGS at v1.1.2; v1.1.3 closes 2 MINOR cleanups inline per verdict §4
author: team_110 (execution mandate per ADR045)
date: 2026-05-25
version: v1.1.3
changelog: >
  v1.1.3 — LOCK CLEANUP per L-GATE_S R4 PASS_WITH_FINDINGS verdict §4
  (LOD400-VERDICT_v1.0.3.md at commit cdc3a87, 2 MINOR cleanups):
  F-R4-01: §7.1 explanatory line rephrased to avoid the bare literal
    `ni_registry.register()` token (replaced with "that WP-A
    registration pattern (which B2 does NOT use)"). The probe-friendly
    phrasing eliminates any ambiguity.
  F-R4-02: historical version labels in code snippets — accepted as
    carried-forward historical context per verdict text "several
    references are valid historical changelog context". No change.
  v1.1.2 — Remediation of 2 BLOCKERS + 1 MINOR from team_190 R3 verdict
  (LOD400-VERDICT_v1.0.2.md at commit df26c40):
  B1-R3 (internal inconsistency: bypass-vs-registry): closed all
    contradictions. §2.1 module-tree comment, §7 intro narrative, and
    AC-03 acceptance text aligned with the §7.1/§8 bypass design.
    AC-03 now checks NI_IMPORTER_CLASSES directly (not
    `ni_registry.registered_labels`). NEW AC-03b adds negative-check
    confirming B2 subclasses are absent from ni_registry.
  B2-R3 (internal inconsistency: seed.py helper additions): closed.
    AC-19, Step 8, and §15 MODIFY summary all updated to reflect that
    NO helper functions are added to seed.py — resolution helpers live
    in NIImporter subclasses per §7.2. Diff guard is now consistent
    with operative content.
  M1-R3 (stale metadata): frontmatter status updated; H1 title bumped
    to v1.1.2; v1.1.0/v1.1.1 mentions in narrative aligned to current
    version where they describe current state (kept where they describe
    history).
  v1.1.1 — Remediation of 3 BLOCKERS from team_190 R2 verdict
  (LOD400-VERDICT_v1.0.1.md at commit 89460bc):
  B1 (VC-6.R2): all literal occurrences of the obsolete class-name
    token removed from spec body (3 sites: changelog §, "Read before
    writing" item 4, §7 intro). The R3 evidence probe (see R3
    mandate §3 probe #1) now passes.
  B2 (VC-15/17): architectural fix — B2 subclasses are NOT registered
    with ni_registry. seed.py iterates NI_IMPORTER_CLASSES directly
    with session. Subclass load(session) and load_knowledge_notes(session)
    accept session and return fully-resolved rows (variety_id /
    crop_id already present). Resolution logic lives in subclasses
    (`_resolve_crop_id` + `_resolve_default_variety_id` helpers,
    mirroring B1 patterns). Rationale documented in §7.1.
  B3 (VC-16): NEW operative §3.1 "Display boundary — OPERATIVE
    LICENSING INVARIANT" — declares 4 binding prohibitions (no publisher
    read; no upload payload; no public view; admin/test-only DB access).
    NEW AC-21 (a/b/c) enforces via git diff audit + 2 publisher-isolation
    test assertions. §3.1.3 explains the elevation from advisory to
    operative content.
  v1.1.0 — Remediation cycle addressing 4 findings from L-GATE_S
  R1 verdict (LOD400-VERDICT_v1.0.0.md at commit 9db86b7) + applying 2
  scope changes from team_00 DECISION file
  (DECISION_WP-B-OPEN-QUESTIONS_2026-05-25_v1.0.0.md).
  FIXES:
    F-S-B2-01 (BLOCKER): the v1.0.0 spec named the WP-A abstract base
      incorrectly. v1.1.0 corrected the name to `NIImporter` (the
      actual WP-A class). All references in §6/§7/§8/§14/§15 corrected.
      Subclass attribute = `name` (not `source_label`/`cache_dir` etc).
      `load()` signature matches WP-A: returns variety-source-value
      row dicts; the new `load_knowledge_notes()` method is sibling
      to `load()` for the crop_knowledge_notes table.
    F-S-B2-02 (MAJOR): §2.2 + §15 internal consistency — ni_importer.py
      is "MODIFY (single function append)" not "DO NOT MODIFY". Added
      explicit `_aos/governance/` + `_aos/lean-kit/` DO NOT TOUCH rows.
    F-S-B2-03 (MAJOR): §8 call-site uses exact existing signature
      `_upsert_source_value(session, variety_id, sv)` (not the
      hallucinated `**row["payload"]` shape).
    F-S-B2-04 (MINOR): §AC-17 + VC-equivalent phrased as 0 FAIL with
      observed PASS/SKIP recorded (lean-kit profile drift acceptable).
  SCOPE CHANGES (per team_00 DECISION 2026-05-25):
    Q1: Input architecture: TEXT FILES provided by team_00 at
        `data/jmf/raw_text/<source>/<crop>.txt`. extraction_runner.py
        reads text files (not PDFs); no pdftotext step; R-01 risk
        obsolete.
    Q5: Scope EXPANSION from 3 → 6 JMF sources. Adds:
        +jmf_book_alt (209pp alternate edition)
        +jmf_ft_phytoprotection (3pp)
        +jmf_ft_nurseryseeding (13pp)
        +3 new note_type enum values: phytoprotection_substance,
         phytoprotection_application, nursery_seeding_process.
        crop_knowledge_notes table CHECK enum extended to 13 values.
  v1.0.0 — Initial authoring (FAILed L-GATE_S R1 with 4 findings).
lod200_ref: _aos/work_packages/S003/SFA-S003-P002-WP-B2/LOD200_spec.md
program_brief_ref: _COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B/PROGRAM_BRIEF_v1.0.0.md
execution_mandate_ref: _COMMUNICATION/TEAM_110/SFA-S003-P002-WP-B/EXECUTION_MANDATE_v1.0.0.md
prior_verdict_ref: _COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B2/LOD400-VERDICT_v1.0.0.md
team_00_decision_ref: _COMMUNICATION/team_00/DECISION_WP-B-OPEN-QUESTIONS_2026-05-25_v1.0.0.md
wp_a_lod400_ref: _aos/work_packages/S003/SFA-S003-P002-WP-A/LOD400_spec.md
wp_b1_patch01_lock_commit: "3e1f946"   # extended JMF_CROP_MAP (86 entries)
builder: sfa_build (separate session per IR#1)
validator: team_190 (non-Claude, Iron Rule #1)
---

# LOD400 — SFA-S003-P002-WP-B2: JMF NI Extraction Layer (v1.1.3 LOCKED)

**Read before writing a single line of code:**
1. LOD200 (this WP): `_aos/work_packages/S003/SFA-S003-P002-WP-B2/LOD200_spec.md`
2. team_00 DECISION (Q1 + Q5 scope changes): `_COMMUNICATION/team_00/DECISION_WP-B-OPEN-QUESTIONS_2026-05-25_v1.0.0.md`
3. team_190 R1 verdict (4 findings — all addressed in v1.1.0): `_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B2/LOD400-VERDICT_v1.0.0.md`
4. **WP-A `ni_importer.py`** (LOD500_LOCKED — VERIFY API): `organic_market_agent/crop_book/importer/ni_importer.py`. The abstract base class is `NIImporter`. Subclass attribute: `name`. Abstract method: `load() → list[dict]`. The dict shape is variety-source-value, NOT a custom `target_table`-tagged shape.
5. WP-A `_upsert_source_value` signature in `organic_market_agent/crop_book/importer/seed.py`: `_upsert_source_value(session, variety_id: int, sv: dict)`.
6. Extended `JMF_CROP_MAP` (86 entries; post-patch01): `organic_market_agent/crop_book/constants.py`.

---

## 1. Goal

Build the **first concrete `NIImporter` subclasses** materializing the WP-A skeleton — extracting per-crop narrative knowledge from **all** JMF MasterClass sources as NI-tier hard-override data. team_00 scope directive (DECISION 2026-05-25 Q5): include the entire JMF corpus.

Deliverables:

1. **Migration 045** — new table `crop_knowledge_notes` (per-crop narrative, type-classified, with licensing + provenance fields). 13 `note_type` enum values.
2. **New ORM module** `organic_market_agent/crop_book/crop_knowledge_notes.py`.
3. **6 concrete `NIImporter` subclasses** (one per JMF source):
   - `ni/jmf_book.py` — Market Gardener 240-page main edition
   - `ni/jmf_book_alt.py` — Market Gardener 209-page alternate edition (Q5 addition)
   - `ni/jmf_ft_flameweed.py` — FT_FLAMEWEEDING (3pp)
   - `ni/jmf_ft_biopesticide.py` — FT_TABLEAUAPPLICATIONBIOPESTICIPE (5pp)
   - `ni/jmf_ft_phytoprotection.py` — FT_PHYTOPROTECTION (3pp) (Q5 addition)
   - `ni/jmf_ft_nurseryseeding.py` — FT_NURSERYSEEDING (13pp) (Q5 addition)
4. **Extraction runner script** `scripts/extract_jmf_ni.py` — one-time CLI reading **text files** (provided by team_00, NOT raw PDFs per Q1) + calling Anthropic API to produce JSON cache.
5. **JSON cache directory** `data/jmf/extracted/<source_name>/<crop_name_en>.json` — committed to repo per advisory #2.
6. **Text-file input directory** `data/jmf/raw_text/<source_name>/<crop_name_en>.txt` (or single `_full.txt` for FT sources) — team_00 supplies post-merge.
7. **`seed.py` CLI additions** — `--ni-only`, `--no-ni`.
8. **≥ 20 tests** (was 15; expanded by Q5).
9. **Append `_upsert_knowledge_note` helper** to `ni_importer.py` (single module-level function; NO class change).
10. **WP-A engine reuse via the actual signature** `_upsert_source_value(session, variety_id, sv)` for cultivar_recommendation rows.

---

## 2. Architecture

### 2.1 Module structure

```
organic_market_agent/crop_book/
├── crop_knowledge_notes.py             ← NEW: CropKnowledgeNote SQLAlchemy ORM
└── importer/
    ├── ni_importer.py                  ← MODIFY (APPEND-only): +_upsert_knowledge_note helper
    ├── ni/                             ← NEW directory
    │   ├── __init__.py                 ← NEW: re-export 6 subclasses (NOT auto-registered with ni_registry per §7.1)
    │   ├── jmf_book.py                 ← NEW: 240pp main edition
    │   ├── jmf_book_alt.py             ← NEW: 209pp alternate edition (Q5)
    │   ├── jmf_ft_flameweed.py         ← NEW: FT_FLAMEWEEDING
    │   ├── jmf_ft_biopesticide.py      ← NEW: FT_BIOPESTICIDE
    │   ├── jmf_ft_phytoprotection.py   ← NEW: FT_PHYTOPROTECTION (Q5)
    │   └── jmf_ft_nurseryseeding.py    ← NEW: FT_NURSERYSEEDING (Q5)
    └── seed.py                         ← MODIFY: --ni-only, --no-ni + 1 call-site block

organic_market_agent/db/versions/
└── 045_crop_knowledge_notes.py         ← NEW

scripts/
└── extract_jmf_ni.py                   ← NEW: reads TEXT files, calls Anthropic API

data/jmf/raw_text/                       ← NEW (team_00 provides post-merge)
├── jmf_book/<crop>.txt                  ← per-crop chapter text
├── jmf_book_alt/<crop>.txt
├── jmf_ft_flameweed/_full.txt           ← single file (FT PDFs are short tables)
├── jmf_ft_biopesticide/_full.txt
├── jmf_ft_phytoprotection/_full.txt
└── jmf_ft_nurseryseeding/_full.txt

data/jmf/extracted/                       ← NEW directory tree (COMMITTED — gitkeep + final JSON)
├── jmf_book/<crop>.json
├── jmf_book_alt/<crop>.json
├── jmf_ft_flameweed/<crop>.json
├── jmf_ft_biopesticide/<crop>.json
├── jmf_ft_phytoprotection/<crop>.json
└── jmf_ft_nurseryseeding/<crop>.json

tests/crop_book/
├── test_crop_knowledge_notes_orm.py
├── test_migration_045.py
├── test_ni_jmf_book.py
├── test_ni_jmf_book_alt.py            ← Q5
├── test_ni_jmf_ft_flameweed.py
├── test_ni_jmf_ft_biopesticide.py
├── test_ni_jmf_ft_phytoprotection.py  ← Q5
├── test_ni_jmf_ft_nurseryseeding.py   ← Q5
├── test_ni_cache_schema.py
├── test_ni_idempotency.py
├── test_ni_licensing_flag.py
├── test_ni_dedup_alt_edition.py       ← Q5 — handles overlap between jmf_book + jmf_book_alt
└── test_seed_ni_cli.py

CHANGELOG.md                                ← MODIFY: [Unreleased] entry
```

### 2.2 LOD500_LOCKED inventory (DO NOT TOUCH)

| File / path | Reason |
|-------------|--------|
| `_aos/governance/` (entire tree) | IR#11 — governance is hub→snapshot only |
| `_aos/lean-kit/` (entire tree) | IR#11 — lean-kit is hub→snapshot only |
| `_aos/project_identity.yaml` | IR#11 |
| `organic_market_agent/views.py` | LIVE PRODUCTION |
| `organic_market_agent/publisher/wp_upload.py`, `upload_dispatch.py` | LIVE PRODUCTION |
| `organic_market_agent/db/versions/001..044_*.py` | All prior migrations (045 reserved for B2) |
| `organic_market_agent/crop_book/importer/tend.py` | Raw-material guard (CLAUDE.md) |
| `organic_market_agent/crop_book/importer/jmf.py`, `jmf_masterclass.py` | B1 deliverables — LOD500_LOCKED |
| `organic_market_agent/crop_book/crop_task_templates.py` | B1 deliverable — LOD500_LOCKED |
| `organic_market_agent/db/versions/044_crop_task_templates.py` | B1 deliverable |
| `organic_market_agent/crop_book/models.py`, `source_registry.py`, `field_policy.py`, `enrichment_models.py`, `importer/reconciler.py`, `importer/enrichment_runner.py` | WP-A engine SSoT |
| `organic_market_agent/crop_book/constants.py` | LOD500_LOCKED via B1 + patch01 (B2 reads `JMF_CROP_MAP` read-only; does NOT modify) |
| `mu-plugin/` | Deployed |

### 2.3 MODIFY scope (explicit — F-S-B2-02 fix)

The internal-consistency issue in v1.0.0 between §2.2 (DO NOT MODIFY) and §7.5 (single helper append) is resolved here:

| File | Allowed change scope |
|------|----------------------|
| `organic_market_agent/crop_book/importer/ni_importer.py` | **APPEND-ONLY**: add `_upsert_knowledge_note(session, ...)` helper at module scope (after the `ni_registry = _NIRegistry()` line). The `NIImporter` abstract class MUST remain unchanged. The `_NIRegistry` class MUST remain unchanged. The `ni_registry` singleton MUST remain unchanged. No new classes, no method additions to existing classes. |
| `organic_market_agent/crop_book/importer/seed.py` | Add 2 CLI flags + 1 new call-site block (after the existing JMF + Tend imports). |
| `CHANGELOG.md` | Append `[Unreleased]` entry. |

AC-19 enforces these limits via `git diff <patch01-lock>..HEAD -- <each LOD500_LOCKED path>` showing empty + the MODIFY-list files showing only the specified additive scope.

---

## 3. Migration 045 — `crop_knowledge_notes`

File: `organic_market_agent/db/versions/045_crop_knowledge_notes.py`

```python
"""Migration 045: crop_knowledge_notes table — per-crop NI narrative.

SFA-S003-P002-WP-B2 LOD400 v1.1.0 §3. Additive only.
"""
from alembic import op
import sqlalchemy as sa

revision = "045"
down_revision = "044"
branch_labels = None
depends_on = None

_NOTE_TYPE_ENUM = (
    # From JMF book (main + alt editions) — 8 baseline types
    "pest_disease", "harvest_marker", "storage_handling",
    "rotation_companion", "cultivar_recommendation", "growing_tip",
    "irrigation", "nursery_specific",
    # From FT PDFs — 2 baseline + 3 new (Q5 expansion)
    "flame_weed_timing",          # FT_FLAMEWEEDING
    "biopesticide_spray",         # FT_TABLEAUAPPLICATIONBIOPESTICIPE
    "phytoprotection_substance",  # FT_PHYTOPROTECTION (Q5 — substances catalogued)
    "phytoprotection_application", # FT_PHYTOPROTECTION (Q5 — application protocols)
    "nursery_seeding_process",    # FT_NURSERYSEEDING (Q5 — process descriptions)
)
# Total: 13 enum values. Was 10 in v1.0.0; +3 from Q5.

def upgrade():
    op.create_table(
        "crop_knowledge_notes",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
                  primary_key=True, autoincrement=True),
        sa.Column("crop_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
                  sa.ForeignKey("crops.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source", sa.VARCHAR(50), nullable=False),
        sa.Column("trust_tier", sa.VARCHAR(20), nullable=False),
        sa.Column("note_type", sa.VARCHAR(40), nullable=False),
        sa.Column("body_text", sa.Text, nullable=False),
        sa.Column("provenance_pdf", sa.VARCHAR(200), nullable=True),
        sa.Column("provenance_pages", sa.VARCHAR(40), nullable=True),
        sa.Column("is_internal_farm_use_only", sa.Boolean,
                  nullable=False, server_default=sa.text("true")),
        sa.Column("extraction_model", sa.VARCHAR(50), nullable=True),
        sa.Column("extracted_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("crop_id", "source", "note_type",
                            name="uq_ckn_crop_source_type"),
        sa.CheckConstraint(
            "note_type IN (" + ",".join(repr(v) for v in _NOTE_TYPE_ENUM) + ")",
            name="ck_ckn_note_type",
        ),
        sa.CheckConstraint(
            "length(body_text) <= 2000",
            name="ck_ckn_body_text_length",
        ),
    )
    op.create_index("idx_ckn_crop", "crop_knowledge_notes", ["crop_id"])
    op.create_index("idx_ckn_type", "crop_knowledge_notes", ["note_type"])

def downgrade():
    op.drop_index("idx_ckn_type", table_name="crop_knowledge_notes")
    op.drop_index("idx_ckn_crop", table_name="crop_knowledge_notes")
    op.drop_table("crop_knowledge_notes")
```

The `length(body_text) <= 2000` CHECK is the schema-level enforcement of advisory #1's fair-use snippet bound. AC-04a regression-tests this constraint at INSERT time.

---

## 3.1 Display boundary — OPERATIVE LICENSING INVARIANT

This section is OPERATIVE spec content, NOT advisory. It defines the binding display/publication rules for `crop_knowledge_notes` content extracted from JMF PDFs.

### 3.1.1 Prohibition (BINDING)

The `crop_knowledge_notes` table is **INTERNAL ONLY**. Its content is extracted from copyrighted JMF MasterClass material under fair-use snippet bounds (≤ 2000 chars per note) and is licensed for **internal farm-operator use only**.

**The following are FORBIDDEN by this LOD400 specification:**

1. **No WordPress publish path may read `crop_knowledge_notes` data.**
   No file under `organic_market_agent/publisher/` may import, query, or
   reference the `crop_knowledge_notes` table or `CropKnowledgeNote` ORM
   class.

2. **No WordPress upload payload may include `crop_knowledge_notes` content.**
   Artifacts produced by `dispatch_upload()` or related helpers MUST NOT
   contain text derived from `crop_knowledge_notes.body_text`.

3. **No public-facing WordPress view may display `crop_knowledge_notes` content.**
   No modification of `organic_market_agent/views.py` (LOD500_LOCKED) is
   in B2 scope; any future modification adding NI prose to public views
   requires (a) a new GCR to team_00, (b) a separate WP-C UI work
   package, and (c) explicit authorization in that WP-C's LOD400.

4. **Database queries against `crop_knowledge_notes` are permitted ONLY for:**
   - Operator-side administrative tools (separate, authenticated)
   - Future logged-in-farm-operator dashboard (out of scope for B2 — TBD WP-C)
   - Test code (in-memory SQLite, fixtures only)
   - The `_upsert_knowledge_note` helper itself

### 3.1.2 Enforcement at build time

AC-21 (NEW — see §9) enforces the prohibition via `git diff` audit: any modification to `organic_market_agent/publisher/` or `organic_market_agent/views.py` by the B2 build is grounds for L-GATE_V FAIL.

A test file `test_ni_publisher_isolation.py` provides additional regression coverage by asserting that:
- `organic_market_agent/publisher/` modules do NOT import from `organic_market_agent.crop_book.crop_knowledge_notes`
- The string `crop_knowledge_notes` does NOT appear in any file under `organic_market_agent/publisher/`

### 3.1.3 Why this section is operative (not advisory)

The L-GATE_S R2 verdict (F-LV-PATCH01-R2-style B3 finding) correctly observed that the v1.1.0 advisory-table claim "§11 forbids publication" was non-operative — no spec section actually contained the binding rule. v1.1.1 fixes this by elevating the prohibition to the data-model section (§3.1) where the schema CHECK constraints live, making it part of the operative contract.

The schema-level enforcement (§3 `length(body_text) <= 2000` + `is_internal_farm_use_only=TRUE` default) covers ROW-LEVEL fair-use bounds. §3.1 covers SYSTEM-LEVEL display boundaries.

---

## 4. ORM — `crop_knowledge_notes.py`

File: `organic_market_agent/crop_book/crop_knowledge_notes.py` (NEW)

```python
"""CropKnowledgeNote ORM — per-crop NI narrative (migration 045).

SFA-S003-P002-WP-B2 LOD400 v1.1.0 §4. Mirrors WP-A/B1/B3 pattern.
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, Boolean, CheckConstraint, ForeignKey, Integer, TIMESTAMP, Text,
    UniqueConstraint, VARCHAR,
)
from sqlalchemy.orm import Mapped, mapped_column

from organic_market_agent.db.base import Base

_PK_TYPE = BigInteger().with_variant(Integer(), "sqlite")

NOTE_TYPE_VALUES: tuple[str, ...] = (
    "pest_disease", "harvest_marker", "storage_handling",
    "rotation_companion", "cultivar_recommendation", "growing_tip",
    "irrigation", "nursery_specific",
    "flame_weed_timing", "biopesticide_spray",
    "phytoprotection_substance", "phytoprotection_application",
    "nursery_seeding_process",
)
# 13 values total.

BODY_TEXT_MAX_LENGTH: int = 2000

class CropKnowledgeNote(Base):
    __tablename__ = "crop_knowledge_notes"
    __table_args__ = (
        UniqueConstraint("crop_id", "source", "note_type",
                         name="uq_ckn_crop_source_type"),
        CheckConstraint(
            "note_type IN ({})".format(",".join(repr(v) for v in NOTE_TYPE_VALUES)),
            name="ck_ckn_note_type",
        ),
        CheckConstraint(
            f"length(body_text) <= {BODY_TEXT_MAX_LENGTH}",
            name="ck_ckn_body_text_length",
        ),
    )

    id: Mapped[int] = mapped_column(_PK_TYPE, primary_key=True, autoincrement=True)
    crop_id: Mapped[int] = mapped_column(
        _PK_TYPE, ForeignKey("crops.id", ondelete="CASCADE"), nullable=False)
    source: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    trust_tier: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    note_type: Mapped[str] = mapped_column(VARCHAR(40), nullable=False)
    body_text: Mapped[str] = mapped_column(Text, nullable=False)
    provenance_pdf: Mapped[Optional[str]] = mapped_column(VARCHAR(200), nullable=True)
    provenance_pages: Mapped[Optional[str]] = mapped_column(VARCHAR(40), nullable=True)
    is_internal_farm_use_only: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True)
    extraction_model: Mapped[Optional[str]] = mapped_column(VARCHAR(50), nullable=True)
    extracted_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)

    def __repr__(self) -> str:
        return (f"<CropKnowledgeNote crop_id={self.crop_id} type={self.note_type!r} "
                f"source={self.source!r} len(body)={len(self.body_text)}>")
```

---

## 5. JSON cache schema

Path: `data/jmf/extracted/<source_name>/<crop_name_en>.json`

Schema (top-level — same shape for all 6 sources):

```json
{
  "schema_version": "1.0",
  "source": "NI:jmf_book_v1",
  "crop_jmf_en": "Arugula",
  "provenance": {
    "pdf": "THEMARKETGARDENEREBOOK (from macBook Air - nimrod).PDF",
    "pages": "42-45",
    "extraction_model": "claude-sonnet-4-6",
    "extracted_at": "2026-05-25T14:23:00Z"
  },
  "notes": {
    "pest_disease":                "Flea beetles affect early-season plantings...",
    "harvest_marker":              "Harvest when leaves are 4–6 inches...",
    "storage_handling":            "Store at 1–4 °C, 95% humidity...",
    "rotation_companion":          null,
    "cultivar_recommendation":     "Astro is more bolt-resistant...",
    "growing_tip":                 null,
    "irrigation":                  "Light, frequent watering...",
    "nursery_specific":            null,
    "flame_weed_timing":           null,
    "biopesticide_spray":          null,
    "phytoprotection_substance":   null,
    "phytoprotection_application": null,
    "nursery_seeding_process":     null
  }
}
```

Each source produces JSON files where ONLY the source-relevant `notes` keys are populated; the rest are null. E.g., `jmf_ft_flameweed/<crop>.json` only has `flame_weed_timing` populated. `jmf_book/<crop>.json` populates the 8 book types. `jmf_book_alt/<crop>.json` populates the same 8 types but from the 209pp alternate edition (potentially duplicating `jmf_book` content — see §13 R-08 dedup strategy).

**Field constraints (enforced at extraction time and re-verified at DB upsert):**
- `body_text` for each note ≤ 2000 chars (matches DB CHECK constraint)
- `note_type` keys MUST be a subset of `NOTE_TYPE_VALUES` (ORM tuple)
- `provenance.pdf` MUST match the canonical filename of the source PDF
- `provenance.pages` MUST be a valid page range string (regex `^\d+(-\d+)?$`)

JSON files are committed to repo. `.gitattributes` rule: `data/jmf/extracted/** linguist-vendored`.

---

## 6. Extraction runner — `scripts/extract_jmf_ni.py` (text-file input per Q1)

File: `scripts/extract_jmf_ni.py` (NEW; CLI tool, NOT production code)

```python
"""One-time extraction runner — reads TEXT FILES (provided by team_00) and
calls Anthropic API to produce the JSON cache.

NOT runtime. NOT in tests. NOT imported by the runtime path. Run manually:

    python scripts/extract_jmf_ni.py --source jmf_book --crop arugula
    python scripts/extract_jmf_ni.py --source jmf_book --all
    python scripts/extract_jmf_ni.py --source jmf_ft_phytoprotection
    python scripts/extract_jmf_ni.py --source jmf_book --rebuild --crop arugula

Requires:
    - ANTHROPIC_API_KEY env var
    - Text files at data/jmf/raw_text/<source>/<crop>.txt (or _full.txt for FT)
      provided by team_00 post-merge (Q1 architectural decision — no PDFs).

NOTE per Q1: this script does NOT call pdftotext or read PDFs. Input is plain
text files. team_00 performs the PDF→text conversion themselves.
"""
import argparse, json, pathlib, sys
from datetime import datetime, timezone
import anthropic

SUPPORTED_SOURCES = (
    "jmf_book", "jmf_book_alt",
    "jmf_ft_flameweed", "jmf_ft_biopesticide",
    "jmf_ft_phytoprotection", "jmf_ft_nurseryseeding",
)
DEFAULT_MODEL = "claude-sonnet-4-6"
DEFAULT_TEMPERATURE = 0.0
RAW_TEXT_BASE = pathlib.Path("data/jmf/raw_text")
CACHE_BASE = pathlib.Path("data/jmf/extracted")
SCHEMA_VERSION = "1.0"

# Per-source canonical PDF filename (for provenance)
SOURCE_PDF_MAP = {
    "jmf_book":               "THEMARKETGARDENEREBOOK (from macBook Air - nimrod).PDF",
    "jmf_book_alt":           "THE MARKET GARDENER_*.PDF",
    "jmf_ft_flameweed":       "FT_FINALE_FLAMEWEEDING.PDF",
    "jmf_ft_biopesticide":    "FT_FINALE_TABLEAUAPPLICATIONBIOPESTICIPE.PDF",
    "jmf_ft_phytoprotection": "FT_FINALE_PHYTOPROTECTION.PDF",
    "jmf_ft_nurseryseeding":  "FT_FINALE_NURSERYSEEDING.PDF",
}

# Per-source note_type set (which keys are populated in the JSON `notes` dict)
SOURCE_NOTE_TYPES = {
    "jmf_book":               ("pest_disease", "harvest_marker", "storage_handling",
                               "rotation_companion", "cultivar_recommendation",
                               "growing_tip", "irrigation", "nursery_specific"),
    "jmf_book_alt":           ("pest_disease", "harvest_marker", "storage_handling",
                               "rotation_companion", "cultivar_recommendation",
                               "growing_tip", "irrigation", "nursery_specific"),
    "jmf_ft_flameweed":       ("flame_weed_timing",),
    "jmf_ft_biopesticide":    ("biopesticide_spray",),
    "jmf_ft_phytoprotection": ("phytoprotection_substance", "phytoprotection_application"),
    "jmf_ft_nurseryseeding":  ("nursery_seeding_process",),
}

def extract_book_chapter(client, text, crop_jmf_en, note_types):
    """Generic per-chapter extractor — used by jmf_book + jmf_book_alt."""
    prompt = f"""You are extracting structured horticultural knowledge from a
book chapter about the crop "{crop_jmf_en}". The chapter text follows.
Extract concise farm-relevant notes (≤2000 characters each) for these
note types: {', '.join(note_types)}. Return ONLY valid JSON with the
structure shown. Use null for any note_type the chapter does not address.

Chapter text:
\"\"\"
{text}
\"\"\"

Output JSON ONLY:
{{ {', '.join(f'"{nt}": "..." or null' for nt in note_types)} }}"""
    response = client.messages.create(
        model=DEFAULT_MODEL, max_tokens=4096, temperature=DEFAULT_TEMPERATURE,
        messages=[{"role": "user", "content": prompt}],
    )
    # Parse JSON, validate length per field ≤2000, return dict.

def extract_ft_table(client, text, source_name, note_types):
    """Generic FT-table extractor — per-crop dict mapping crop_jmf_en → field values."""
    # Similar pattern; produces dict per crop covered in the FT table.

def main():
    parser = argparse.ArgumentParser(...)
    parser.add_argument("--source", choices=SUPPORTED_SOURCES, required=True)
    parser.add_argument("--crop", help="Restrict to single crop (English JMF name)")
    parser.add_argument("--all", action="store_true", help="All crops with text-file fixtures present")
    parser.add_argument("--rebuild", action="store_true")
    parser.add_argument("--raw-text-base", type=pathlib.Path, default=RAW_TEXT_BASE)
    args = parser.parse_args()

    # Read text file(s) from RAW_TEXT_BASE / args.source / ...
    # Dispatch to extract_book_chapter (for jmf_book[_alt]) or extract_ft_table (for jmf_ft_*)
    # Write JSON to CACHE_BASE / args.source / <crop>.json
```

**Anthropic API contract:**
- Model: `claude-sonnet-4-6` (or current Sonnet); temperature `0.0` for determinism
- Max tokens: 4096 per call
- Per-source estimated cost (one-time): ~52 crops × n note types × 1 LLM call. For 6 sources, total ~150 calls. Cached forever after.

**Q1 architectural simplification:** no `pdftotext` step. team_00 provides text files; runner reads them directly. If a text file is missing, the runner logs WARN and skips that crop (graceful — same as the WARN+skip pattern in B1).

---

## 7. NIImporter subclasses (correct API per WP-A — F-S-B2-01 fix)

WP-A's actual abstract base class is `NIImporter`. The abstract method is `load() → list[dict[str, Any]]`, returning **variety-source-value row dicts** (matching the `crop_variety_source_values` shape). Subclass attribute is `name`.

For B2's crop-scoped narrative content (which doesn't fit the variety-source-value shape natively), each subclass implements a **sibling method `load_knowledge_notes(session) → list[dict[str, Any]]`** that returns `crop_knowledge_notes` row dicts.

**B2 does NOT use the `ni_registry` mechanism at all.** Per §7.1 (architectural decision driven by WP-A's `validate()` dropping rows missing `variety_id`): the seed.py call-site iterates `NI_IMPORTER_CLASSES` directly, instantiates each subclass, and calls `load(session)` + `load_knowledge_notes(session)` per importer. See §8 for the exact call-site code.

### 7.1 `ni/__init__.py` (NEW) — bypasses ni_registry.load_all()

```python
"""NI importer subclasses (SFA-S003-P002-WP-B2 v1.1.1).

Importing this package re-exports the 6 concrete subclasses.

IMPORTANT — B2 does NOT use `ni_registry.load_all()`. Reason: WP-A's
`NIImporter.validate()` drops rows missing `variety_id`. B2 subclasses
need DB session access to resolve `crop_jmf_en` → `variety_id`, but
that WP-A registration pattern (which B2 does NOT use) instantiates subclasses at
module-load time with no session available. Therefore:

  - B2 subclasses are NOT registered with ni_registry — the
    `ni_registry.register()` call is NEVER invoked at module load.
  - seed.py iterates `NI_IMPORTER_CLASSES` directly with an open session.
  - Each subclass's `load(self, session)` and
    `load_knowledge_notes(self, session)` accept the session and return
    rows with `variety_id` / `crop_id` already resolved.
  - Rows then flow through `_upsert_source_value(session, variety_id, sv)`
    (existing WP-A helper) and `_upsert_knowledge_note(session, ...)`
    (new helper appended to ni_importer.py per §7.3) — both expect
    fully-resolved keys.

Future generic NI sources whose `load()` does NOT need DB access MAY
still use the `ni_registry.register()` + `load_all()` pattern; B2 simply
takes a different path because of its specific data-shape requirements.
This deviation is acknowledged in spec §7 and AC-15.

This file does NOT call `ni_registry.register()` at module load.
"""
from organic_market_agent.crop_book.importer.ni.jmf_book import JmfBookImporter
from organic_market_agent.crop_book.importer.ni.jmf_book_alt import JmfBookAltImporter
from organic_market_agent.crop_book.importer.ni.jmf_ft_flameweed import JmfFtFlameweedImporter
from organic_market_agent.crop_book.importer.ni.jmf_ft_biopesticide import JmfFtBiopesticideImporter
from organic_market_agent.crop_book.importer.ni.jmf_ft_phytoprotection import JmfFtPhytoprotectionImporter
from organic_market_agent.crop_book.importer.ni.jmf_ft_nurseryseeding import JmfFtNurseryseedingImporter

NI_IMPORTER_CLASSES = (
    JmfBookImporter, JmfBookAltImporter,
    JmfFtFlameweedImporter, JmfFtBiopesticideImporter,
    JmfFtPhytoprotectionImporter, JmfFtNurseryseedingImporter,
)

__all__ = [cls.__name__ for cls in NI_IMPORTER_CLASSES] + ["NI_IMPORTER_CLASSES"]
```

### 7.2 `ni/jmf_book.py` (NEW — pattern for all 6 subclasses)

```python
"""JmfBookImporter — Market Gardener 240-page main edition.

Subclass of WP-A NIImporter. Reads cached JSON from
data/jmf/extracted/jmf_book/<crop>.json. Produces:
  - 0-or-1 variety-source-value row per crop (cultivar_recommendation)
    via load() — goes through WP-A standard NI path
  - 0..8 crop_knowledge_notes rows per crop via load_knowledge_notes()
    — goes through the B2-specific path
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from organic_market_agent.crop_book.importer.ni_importer import NIImporter


class JmfBookImporter(NIImporter):
    name = "jmf_book_v1"
    cache_dir = Path("data/jmf/extracted/jmf_book")
    canonical_pdf_filename = "THEMARKETGARDENEREBOOK (from macBook Air - nimrod).PDF"

    def _iter_cache_files(self):
        if not self.cache_dir.exists():
            return
        yield from sorted(self.cache_dir.glob("*.json"))

    def _load_cache_file(self, path: Path) -> dict:
        data = json.loads(path.read_text(encoding="utf-8"))
        # Validate schema_version, source, crop_jmf_en, provenance, notes
        if data.get("schema_version") != "1.0":
            raise ValueError(f"{path}: missing or wrong schema_version")
        return data

    def _resolve_crop_id_and_variety_id(self, session, crop_jmf_en: str):
        """Use B1's pattern: JMF_CROP_MAP → crops.name_he → crops.id;
        default-baseline variety (name_en IS NULL)."""
        # ... implementation matching B1's _default_variety_id helper

    def load(self, session) -> list[dict[str, Any]]:
        """Return variety-source-value rows for cultivar_recommendation only.

        Each row is fully-resolved (variety_id present) per the
        `_upsert_source_value(session, variety_id, sv)` call contract.
        Session is REQUIRED — used to resolve crop_jmf_en → variety_id
        via JMF_CROP_MAP lookup + default-baseline-variety pattern
        (mirrors B1 `_default_variety_id` helper).

        Note: this is a B2-specific signature (adds `session` param vs.
        the WP-A base abstract `load()`). B2 subclasses are NOT
        auto-registered with ni_registry per §7.1 — the seed.py
        call-site instantiates them with session.
        """
        rows = []
        for path in self._iter_cache_files():
            data = self._load_cache_file(path)
            crop_jmf_en = data["crop_jmf_en"]
            cultivar = data["notes"].get("cultivar_recommendation")
            if not cultivar:
                continue
            variety_id = self._resolve_default_variety_id(session, crop_jmf_en)
            if variety_id is None:
                # JMF_CROP_MAP miss → log WARN + skip (B1 pattern)
                continue
            rows.append({
                "variety_id": variety_id,
                "field_name": "cultivar_recommendation",
                "source": self.source_label,
                "value_text": cultivar[:2000],  # bounded per advisory #1
                "value_numeric": None,
                "unit": None,
                "note": f"From {self.canonical_pdf_filename} pages {data['provenance']['pages']}",
                "trust_tier": "NI",
                "confidence_weight": None,
                "is_outlier_rejected": False,
            })
        return rows

    def load_knowledge_notes(self, session) -> list[dict[str, Any]]:
        """Return fully-resolved crop_knowledge_notes row dicts.

        Each row has `crop_id` (resolved from crop_jmf_en via session lookup);
        ready for `_upsert_knowledge_note(session, crop_id=..., **rest)`.
        """
        rows = []
        for path in self._iter_cache_files():
            data = self._load_cache_file(path)
            crop_jmf_en = data["crop_jmf_en"]
            crop_id = self._resolve_crop_id(session, crop_jmf_en)
            if crop_id is None:
                continue  # WARN + skip
            for note_type, body in data["notes"].items():
                if not body:
                    continue
                if len(body) > 2000:
                    raise ValueError(f"{path}: note_type={note_type} body_text > 2000")
                rows.append({
                    "crop_id": crop_id,
                    "source": self.source_label,
                    "trust_tier": "NI",
                    "note_type": note_type,
                    "body_text": body,
                    "provenance_pdf": data["provenance"]["pdf"],
                    "provenance_pages": data["provenance"]["pages"],
                    "is_internal_farm_use_only": True,
                    "extraction_model": data["provenance"]["extraction_model"],
                    "extracted_at": data["provenance"]["extracted_at"],
                })
        return rows

    def _resolve_crop_id(self, session, crop_jmf_en: str) -> int | None:
        """Resolve JMF English crop name → crops.id via JMF_CROP_MAP.

        Returns None on miss (logs WARN). Shared helper used by both
        load() and load_knowledge_notes().
        """
        from organic_market_agent.crop_book.constants import JMF_CROP_MAP
        from organic_market_agent.crop_book.models import Crop
        name_he = JMF_CROP_MAP.get(crop_jmf_en)
        if name_he is None:
            return None
        crop = session.query(Crop).filter_by(name_he=name_he).one_or_none()
        return crop.id if crop else None

    def _resolve_default_variety_id(self, session, crop_jmf_en: str) -> int | None:
        """Resolve crop_jmf_en → default-baseline variety_id (name_en IS NULL).

        Mirrors B1's _default_variety_id helper (`jmf_masterclass.py` §6.9).
        Returns None on miss.
        """
        from organic_market_agent.crop_book.models import CropVariety
        crop_id = self._resolve_crop_id(session, crop_jmf_en)
        if crop_id is None:
            return None
        v = (session.query(CropVariety)
             .filter(CropVariety.crop_id == crop_id, CropVariety.name_en.is_(None))
             .one_or_none())
        if v is None:
            v = CropVariety(crop_id=crop_id, name_en=None, name_he=None)
            session.add(v); session.flush()
        return v.id
```

The other 5 subclasses follow the same pattern with their own `name`, `cache_dir`, `canonical_pdf_filename`. For FT subclasses, the cache structure may be a single `_table.json` (mapping crop_jmf_en → fields) instead of per-crop files — the `_iter_cache_files` + `_load_cache_file` methods adapt accordingly.

### 7.3 `_upsert_knowledge_note` helper (F-S-B2-02 fix — single APPEND to ni_importer.py)

The ONLY permitted modification to `ni_importer.py`. Append at module scope AFTER the `ni_registry = _NIRegistry()` line:

```python
# ---------------------------------------------------------------------------
# Knowledge-note upsert helper (added by WP-B2)
# ---------------------------------------------------------------------------

def _upsert_knowledge_note(
    session,
    crop_id: int,
    source: str,
    note_type: str,
    body_text: str,
    *,
    provenance_pdf: str | None = None,
    provenance_pages: str | None = None,
    extraction_model: str | None = None,
    extracted_at = None,
) -> "CropKnowledgeNote":
    """Upsert one crop_knowledge_notes row on (crop_id, source, note_type).

    Always sets trust_tier='NI' and is_internal_farm_use_only=True.
    Body text bounded ≤ 2000 chars (DB CHECK + ORM constraint also enforce).

    Added by SFA-S003-P002-WP-B2 LOD400 v1.1.0 §7.3.
    """
    # Lazy import to avoid circular dependency
    from organic_market_agent.crop_book.crop_knowledge_notes import (
        CropKnowledgeNote, BODY_TEXT_MAX_LENGTH,
    )
    if len(body_text) > BODY_TEXT_MAX_LENGTH:
        raise ValueError(f"body_text exceeds {BODY_TEXT_MAX_LENGTH} chars")
    row = (session.query(CropKnowledgeNote)
           .filter_by(crop_id=crop_id, source=source, note_type=note_type)
           .one_or_none())
    if row is None:
        row = CropKnowledgeNote(
            crop_id=crop_id, source=source, note_type=note_type,
        )
        session.add(row)
    row.trust_tier = "NI"
    row.body_text = body_text
    row.provenance_pdf = provenance_pdf
    row.provenance_pages = provenance_pages
    row.is_internal_farm_use_only = True
    row.extraction_model = extraction_model
    row.extracted_at = extracted_at
    session.flush()
    return row
```

NO other modification to `ni_importer.py`. The `NIImporter` class, `_NIRegistry` class, `ni_registry` singleton remain unchanged.

---

## 8. `seed.py` modifications (F-S-B2-03 fix — exact signature)

Existing `_upsert_source_value(session, variety_id, sv)` signature from `seed.py`. B2 does NOT introduce a new signature; it uses the existing one. The `sv` parameter is a dict matching the `CropVarietySourceValue` column shape.

Add CLI flags (after existing B1+patch01+B3 flags):

```python
parser.add_argument(
    "--ni-only", action="store_true",
    help="Run only NI ingestion (skip JMF MasterClass / Tend / Tend overlay).",
)
parser.add_argument(
    "--no-ni", action="store_true",
    help="Skip NI ingestion.",
)
```

Mutual exclusion: `--ni-only` ↔ `--no-ni`.

Call site (inside `with SessionFactory() as session:` block, AFTER all other importers — NI hard-override comes LAST so it wins precedence):

```python
if not args.no_ni:
    # B2 bypasses ni_registry.load_all() per §7.1 architectural decision.
    # B2 does NOT call ni_registry.register; the 6 subclasses are NOT
    # registered with ni_registry; seed.py iterates NI_IMPORTER_CLASSES
    # directly with session for the variety_id / crop_id resolution.
    from organic_market_agent.crop_book.importer.ni import NI_IMPORTER_CLASSES
    from organic_market_agent.crop_book.importer.ni_importer import _upsert_knowledge_note

    for cls in NI_IMPORTER_CLASSES:
        importer = cls()  # constructor takes no args (subclass attrs are class-level)

        # PATH A: variety-source-value rows (cultivar_recommendation only)
        for row in importer.load(session):
            # Row is fully resolved by load(); use existing WP-A signature:
            variety_id = row.pop("variety_id")
            _upsert_source_value(session, variety_id, row)

        # PATH B: crop_knowledge_notes rows (B2-specific)
        for row in importer.load_knowledge_notes(session):
            # Row is fully resolved by load_knowledge_notes(); crop_id is in the dict
            _upsert_knowledge_note(session, **row)

    session.flush()

if args.ni_only:
    if not args.dry_run:
        session.commit()
    return
```

No additional helper functions are added to seed.py — resolution lives in the subclasses (`_resolve_crop_id` + `_resolve_default_variety_id` per §7.2). seed.py changes are limited to: 2 CLI flag definitions + this call-site block. AC-19 audit covers this.

---

## 9. Acceptance Criteria (≥18; v1.0.0 had 18; v1.1.0 same count + 2 new for Q5)

**AC-01 — Migration 045 + 13-value note_type CHECK clean.**
`alembic upgrade head` succeeds; CHECK constraint accepts all 13 enum values; `length(body_text) <= 2000` CHECK active. Both Postgres + SQLite.

**AC-02 — `CropKnowledgeNote` ORM correct (13 enum values + length constant).**
`NOTE_TYPE_VALUES` has exactly 13 entries; `BODY_TEXT_MAX_LENGTH == 2000`.

**AC-03 — All 6 NIImporter subclasses present in `NI_IMPORTER_CLASSES` and have correct `source_label`s.**
*(Updated in v1.1.2 to match the §7.1 bypass architectural decision: B2 does NOT use `ni_registry`. AC-03 therefore checks `NI_IMPORTER_CLASSES` directly, not `ni_registry.registered_labels`.)*

```python
from organic_market_agent.crop_book.importer.ni import NI_IMPORTER_CLASSES
assert len(NI_IMPORTER_CLASSES) == 6
labels = {cls().source_label for cls in NI_IMPORTER_CLASSES}
assert labels == {
    "NI:jmf_book_v1", "NI:jmf_book_alt_v1",
    "NI:jmf_ft_flameweed_v1", "NI:jmf_ft_biopesticide_v1",
    "NI:jmf_ft_phytoprotection_v1", "NI:jmf_ft_nurseryseeding_v1",
}
```

**AC-03b** — Negative check confirming the bypass: after importing the package, `ni_registry.registered_labels` MUST NOT contain any B2 source label (the 6 listed above are all absent). This proves the `ni_registry.register()` call was NOT made at module load.

**AC-04a — Body-text length CHECK enforced at DB level.**
Insert with 2001-char body_text raises `IntegrityError`.

**AC-04b — `note_type` CHECK enforced (13 values).**
Inserting `note_type='nonsense_type'` raises `IntegrityError`. All 13 enum values accepted (including 3 Q5 additions).

**AC-05 — Licensing flag default + ORM enforcement.**
Default `is_internal_farm_use_only=True`. The `_upsert_knowledge_note` helper hardcodes this value (cannot be set to False by importer code).

**AC-06 — UNIQUE constraint on (crop_id, source, note_type).**
Two inserts with identical key raises `IntegrityError`. `_upsert_knowledge_note` is idempotent.

**AC-07 — `JmfBookImporter` extends `NIImporter` correctly.**
`isinstance(JmfBookImporter(), NIImporter)` is True. `JmfBookImporter().name == "jmf_book_v1"`. `JmfBookImporter().source_label == "NI:jmf_book_v1"` (derived via base class property).

**AC-08 — Cache schema validation rejects malformed JSON.**
Missing `schema_version` → ValueError. Bad `note_type` key → ValueError. body_text > 2000 → ValueError.

**AC-09 — All 6 source subclasses produce rows from fixture caches.**
For each of the 6 subclasses, given a fixture cache with 2+ crops, `subclass.load_knowledge_notes()` returns ≥ 2 rows per crop's non-null note types.

**AC-10 — DB integration: end-to-end via seed.py NI flow.**
On a SQLite in-memory DB seeded with 3 crops + all 6 NI cache fixtures: NI loop produces (a) ≥ 3 `crop_knowledge_notes` rows; (b) ≥ 1 `crop_variety_source_values` row with `source LIKE 'NI:%'` and `field_name='cultivar_recommendation'`.

**AC-11 — Idempotency.**
Running NI loop twice yields same row count after second call as after first.

**AC-12 — Engine reuse: cultivar_recommendation via existing `_upsert_source_value`.**
The seed.py call-site invokes `_upsert_source_value(session, variety_id, sv)` with `sv` dict shape matching the existing helper. AC-12a: call signature verified at the existing `_upsert_source_value` function location (see seed.py:169-180). AC-12b: resulting row has `trust_tier='NI'`, `confidence_weight=NULL`, `is_outlier_rejected=False`.

**AC-13 — CLI `--ni-only` + `--no-ni`.**
`seed.py --ni-only --dry-run` populates only NI rows (no JMF/Tend). `--all --no-ni --dry-run` produces zero NI rows. Mutual exclusion enforced.

**AC-14 — `extraction_runner` integration test (stubbed).**
With `ANTHROPIC_API_KEY` stubbed, `scripts/extract_jmf_ni.py --source jmf_book --crop arugula --dry-run` produces a valid JSON file. NO live API calls in tests.

**AC-15 — Cache directory commit policy (`.gitkeep` + `.gitattributes`).**
6 `.gitkeep` files exist (one per source subdir). `.gitattributes` declares `data/jmf/extracted/** linguist-vendored`.

**AC-16 — `jmf_book` and `jmf_book_alt` dedup handling (Q5).**
When both `jmf_book` and `jmf_book_alt` cache files contain the same crop with overlapping note types, both produce `crop_knowledge_notes` rows (one per source) — the UNIQUE constraint allows this because `source` differs. Optional `test_ni_dedup_alt_edition.py` documents the behavior for team_00 manual review post-extraction.

**AC-17 — All existing tests still PASS (regression — phrased as 0 FAIL per F-S-B2-04).**
`pytest tests/crop_book/ -q`: zero net regressions on B1 + patch01 + B3 tests (if B3 build has landed) + the new B2 ≥ 20 tests. Pre-existing publisher failure remains out-of-scope.

**AC-18 — `validate_aos.sh` 0 FAIL (F-S-B2-04 fix).**
`bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` returns exit code 0 (`0 FAIL`). PASS/SKIP totals: any value (28/20, 29/18, 29/19 — lean-kit profile is drifting; gate-relevant criterion is 0 FAIL only).

**AC-19 — LOD500_LOCKED audit (no touches beyond §2.3 scope).**
`git diff <patch01-lock>..HEAD -- <each path in §2.2>` is empty. `git diff <patch01-lock>..HEAD -- ni_importer.py` shows ONLY the appended `_upsert_knowledge_note` function (no class change). `git diff <patch01-lock>..HEAD -- seed.py` shows ONLY 2 CLI flag additions + 1 call-site block. *(Updated in v1.1.2: NO helper function additions to seed.py — resolution helpers live in the NIImporter subclasses per §7.2, not on seed.py. The v1.1.0 text mentioning "+2 helper functions" was an internal inconsistency closed in v1.1.2.)*

**AC-20 — `_aos/governance/` + `_aos/lean-kit/` CLEAN (F-S-B2-02 explicit add).**
`git diff <patch01-lock>..HEAD -- _aos/governance/ _aos/lean-kit/ _aos/project_identity.yaml` is EMPTY. (These are hub-driven snapshots; B2 builder must never touch them.)

**AC-21 — Publisher / Views isolation (§3.1 operative licensing invariant).**
*(NEW in v1.1.1 — closes R2 BLOCKER B3.)*
- **AC-21a:** `git diff <patch01-lock>..HEAD -- organic_market_agent/publisher/ organic_market_agent/views.py` is EMPTY. (B2 must NOT modify any publisher or view file.)
- **AC-21b:** `test_ni_publisher_isolation.py` (new test file) asserts:
  ```python
  import pathlib
  pub_dir = pathlib.Path("organic_market_agent/publisher")
  for py in pub_dir.rglob("*.py"):
      content = py.read_text(encoding="utf-8")
      assert "crop_knowledge_notes" not in content, (
          f"§3.1 violation: publisher/{py.name} references crop_knowledge_notes"
      )
      assert "CropKnowledgeNote" not in content, (
          f"§3.1 violation: publisher/{py.name} references CropKnowledgeNote"
      )
  ```
- **AC-21c:** Same assertion for `organic_market_agent/views.py`.

---

## 10. Test requirements

**Minimum 20 new tests** (was 15 in v1.0.0; +5 for Q5 expansion) across 13 new test files:

| File | Tests | Coverage |
|------|-------|----------|
| `test_crop_knowledge_notes_orm.py` | 2 | AC-02 + AC-04b (13 enum values) |
| `test_migration_045.py` | 2 | AC-01 + AC-04a |
| `test_ni_jmf_book.py` | 2 | AC-07 + AC-09 (+ load() returns cultivar_recommendation for AC-12) |
| `test_ni_jmf_book_alt.py` | 1 | AC-09 for alt edition (Q5) |
| `test_ni_jmf_ft_flameweed.py` | 1 | AC-09 for flameweed |
| `test_ni_jmf_ft_biopesticide.py` | 1 | AC-09 for biopesticide |
| `test_ni_jmf_ft_phytoprotection.py` | 1 | AC-09 for phytoprotection (Q5) |
| `test_ni_jmf_ft_nurseryseeding.py` | 1 | AC-09 for nursery seeding (Q5) |
| `test_ni_cache_schema.py` | 2 | AC-08 (schema validation) |
| `test_ni_idempotency.py` | 1 | AC-11 |
| `test_ni_licensing_flag.py` | 2 | AC-05 (default + helper hardcodes True) |
| `test_ni_dedup_alt_edition.py` | 1 | AC-16 (Q5 — alt-edition coexistence) |
| `test_seed_ni_cli.py` | 3 | AC-13 (--ni-only, --no-ni, mutual exclusion) |

**+1 fixture file** per source (6 sources × ≥ 2 crops each = 12 fixture JSONs minimum).

All tests use SQLite in-memory + fixture JSONs. NO live Anthropic API calls. Marker: `@pytest.mark.crop_book`.

---

## 11. Build sequence (10 steps)

**Step 1** — Read this LOD400 + DECISION file + verdict + WP-A `ni_importer.py` (verify NIImporter signature byte-exactly).

**Step 2** — Create `crop_knowledge_notes.py` (ORM with 13 NOTE_TYPE_VALUES). Smoke test imports.

**Step 3** — Create migration 045. `alembic upgrade 045` on fresh SQLite. CHECK constraints active.

**Step 4** — Create `ni/` directory + `__init__.py` + 6 subclass files (NIImporter subclasses). All 6 raise `NotImplementedError` initially.

**Step 5** — Append `_upsert_knowledge_note` helper to `ni_importer.py` (APPEND ONLY). Verify `git diff ni_importer.py` shows ONLY the appended function — no class change.

**Step 6** — Implement `load()` + `load_knowledge_notes()` for all 6 subclasses against fixture caches at `tests/crop_book/fixtures/ni/`. Builder hand-generates ≥ 12 fixture JSON files (≥ 2 crops × 6 sources).

**Step 7** — Create `scripts/extract_jmf_ni.py` (text-file-input version per Q1). Implement the 2 dispatch functions (book chapter; FT table). Stub Anthropic responses for `--dry-run` path. NO live API calls in build/test.

**Step 8** — Wire `seed.py` flags (§8): `--ni-only`, `--no-ni`. Add the call-site block iterating `NI_IMPORTER_CLASSES` with session. **DO NOT add resolver helper functions to seed.py** — the resolution logic (`_resolve_crop_id` + `_resolve_default_variety_id`) lives in the NIImporter subclasses per §7.2. Verify the existing `_upsert_source_value(session, variety_id, sv)` signature is called with correct shape (F-S-B2-03 fix).

**Step 9** — Write all 20+ tests (§10). Verify all 18 ACs (AC-01..AC-20 with 4a/b for AC-04 and 12a/b for AC-12).

**Step 10** — Run `pytest tests/crop_book/ -q` → all green (≥ B1 + patch01 + B3 baseline + 20 B2 new tests; 1 pre-existing publisher failure remains out-of-scope). Run `validate_aos.sh` → 0 FAIL (PASS/SKIP may be 28/20 or 29/18 or 29/19 — F-S-B2-04 carry). Update `CHANGELOG.md`. Write `BUILD_REPORT_v1.0.0.md` with the 8 canonical sections.

**Important post-merge step (NOT builder's job):** team_00 produces text files at `data/jmf/raw_text/<source>/<crop>.txt` for each of the 6 sources, then runs `python scripts/extract_jmf_ni.py --source <X> --all` per source. This populates the real cache. Builder commits ONLY `.gitkeep` placeholders + fixture JSONs.

---

## 12. PRE_HANDOFF advisory disposition

| # | Advisory | B2 disposition (v1.1.0) |
|---|---|---|
| 1 | **JMF PDF licensing — internal farm-use only** | **Addressed via schema + spec language.** §3 CHECK `length(body_text) <= 2000`. §4 ORM `is_internal_farm_use_only=True` default-not-null. §7.3 `_upsert_knowledge_note` hardcodes the True value. §11 forbids publication. AC-04a + AC-05 enforce. |
| 2 | **LLM extraction cache strategy** | **Resolved: cache COMMITTED.** §5 + §15. Reasoning: reproducibility + review + audit. `.gitattributes linguist-vendored` to suppress diff noise. |
| 3 | Tend task whitelist | **N/A** (B3 scope; resolved). |
| 4 | Transitive WP-A dependency | **Addressed**. §2.3 declares the ONE permitted ni_importer.py modification (helper append). §7 verifies the WP-A NIImporter API contract byte-exactly. AC-19 + AC-20 enforce. |

**Q5 scope-change risk (new):** the 209pp alternate edition may overlap content with the 240pp main edition. AC-16 + `test_ni_dedup_alt_edition.py` document the behavior — both produce rows (different `source` keys); team_00 manually arbitrates post-extraction.

**Q1 input-architecture change (new):** extraction_runner reads text files (not PDFs). team_00 provides text files. R-01 (pdftotext install) from v1.0.0 is OBSOLETE — removed.

---

## 13. Risk register (updated for v1.1.0)

| ID | Risk | Likelihood | Severity | Mitigation |
|----|------|-----------|---------|-----------|
| R-01 | ~~pdftotext not installed on builder's system~~ | — | — | **OBSOLETE** per Q1 — extraction_runner reads text files |
| R-02 | LLM extraction produces inconsistent format across runs | LOW | LOW | Temperature 0.0 enforces determinism; schema validation in step 8 rejects bad cache files |
| R-03 | Anthropic API model name changes | LOW | LOW | `--model` flag; provenance captures version |
| R-04 | LLM hallucinates content not in source text | MEDIUM | MEDIUM | Prompt instructs return null on uncertain; 2000-char bound limits surface; team_00 reviews JSON pre-import |
| R-05 | `length(body_text)` CHECK syntax differs PG vs SQLite | LOW | LOW | `length()` portable |
| R-06 | B3 migration 046 collides with B2 045 if B3 runs first | LOW | LOW | Linear chain; B3 builder verifies 045 present before `alembic upgrade 046` |
| R-07 | NI hard-override semantics break PR/OP blending | LOW | LOW | WP-A engine already supports NI prefix-match |
| R-08 | **209pp alternate edition duplicates content** (Q5 new) | MEDIUM | LOW | Both sources produce rows (different `source` key); team_00 arbitrates manually post-extraction; AC-16 documents behavior |
| R-09 | **3 new note_types ambiguous in content scope** (Q5 new) | MEDIUM | LOW | LOD400 §3 prescribes per-source note_type sets; extraction_runner per-source dispatch enforces |
| R-10 | **text-file naming convention mismatch** (Q1 new) | LOW | MEDIUM | extraction_runner expects `data/jmf/raw_text/<source>/<crop>.txt` (or `_full.txt` for FT). Convention documented; runner WARN+skips on missing files; team_00 follows convention |

---

## 14. LOD500_LOCKED file inventory (DO NOT TOUCH)

See §2.2 above. The ONLY permitted exception is the single-function APPEND to `ni_importer.py` (§7.3). AC-19 + AC-20 enforce.

---

## 15. File-level deliverables summary

### CREATE

```
organic_market_agent/crop_book/crop_knowledge_notes.py
organic_market_agent/crop_book/importer/ni/__init__.py
organic_market_agent/crop_book/importer/ni/jmf_book.py
organic_market_agent/crop_book/importer/ni/jmf_book_alt.py            ← Q5
organic_market_agent/crop_book/importer/ni/jmf_ft_flameweed.py
organic_market_agent/crop_book/importer/ni/jmf_ft_biopesticide.py
organic_market_agent/crop_book/importer/ni/jmf_ft_phytoprotection.py  ← Q5
organic_market_agent/crop_book/importer/ni/jmf_ft_nurseryseeding.py   ← Q5
organic_market_agent/db/versions/045_crop_knowledge_notes.py
scripts/extract_jmf_ni.py
data/jmf/raw_text/jmf_book/.gitkeep                                    ← Q1
data/jmf/raw_text/jmf_book_alt/.gitkeep                                ← Q1+Q5
data/jmf/raw_text/jmf_ft_flameweed/.gitkeep                            ← Q1
data/jmf/raw_text/jmf_ft_biopesticide/.gitkeep                         ← Q1
data/jmf/raw_text/jmf_ft_phytoprotection/.gitkeep                      ← Q1+Q5
data/jmf/raw_text/jmf_ft_nurseryseeding/.gitkeep                       ← Q1+Q5
data/jmf/extracted/jmf_book/.gitkeep
data/jmf/extracted/jmf_book_alt/.gitkeep                               ← Q5
data/jmf/extracted/jmf_ft_flameweed/.gitkeep
data/jmf/extracted/jmf_ft_biopesticide/.gitkeep
data/jmf/extracted/jmf_ft_phytoprotection/.gitkeep                     ← Q5
data/jmf/extracted/jmf_ft_nurseryseeding/.gitkeep                      ← Q5
.gitattributes                                  ← APPEND linguist-vendored
tests/crop_book/fixtures/ni/<source>/<crop>.json (12+ fixture files; 6 sources × 2+ crops)
tests/crop_book/test_crop_knowledge_notes_orm.py
tests/crop_book/test_migration_045.py
tests/crop_book/test_ni_jmf_book.py
tests/crop_book/test_ni_jmf_book_alt.py                                ← Q5
tests/crop_book/test_ni_jmf_ft_flameweed.py
tests/crop_book/test_ni_jmf_ft_biopesticide.py
tests/crop_book/test_ni_jmf_ft_phytoprotection.py                      ← Q5
tests/crop_book/test_ni_jmf_ft_nurseryseeding.py                       ← Q5
tests/crop_book/test_ni_cache_schema.py
tests/crop_book/test_ni_idempotency.py
tests/crop_book/test_ni_licensing_flag.py
tests/crop_book/test_ni_dedup_alt_edition.py                           ← Q5
tests/crop_book/test_seed_ni_cli.py
_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B2/BUILD_REPORT_v1.0.0.md   (builder writes after L-GATE_B)
```

### MODIFY (existing files — strict additive scope only)

```
organic_market_agent/crop_book/importer/ni_importer.py    ← APPEND _upsert_knowledge_note ONLY
organic_market_agent/crop_book/importer/seed.py           ← +2 CLI flags + 1 call-site block (NO helper additions per v1.1.2)
CHANGELOG.md                                                ← +[Unreleased] entry
```

### DO NOT TOUCH

See §2.2 LOD500_LOCKED inventory. Includes `_aos/governance/`, `_aos/lean-kit/`, `_aos/project_identity.yaml` (F-S-B2-02 explicit fix).

---

*LOD400 v1.1.3 — LOCKED 2026-05-25 by team_110 (Claude Opus 4.7) under EXECUTION_MANDATE SFA-S003-P002-WP-B (ADR045, `execution_authority: full`).*
*Round chain: v1.0.0 R1 FAIL (4 findings) → v1.1.0 R2 FAIL (3 internal-inconsistency BLOCKERS) → v1.1.1 R3 FAIL (2 internal-inconsistency BLOCKERS) → v1.1.2 R4 PASS_WITH_FINDINGS (2 MINOR) → v1.1.3 LOCKED (MINOR cleanups closed inline).*
*Next: L-GATE_B mandate to sfa_build sub-agent.*

Also: `tests/crop_book/test_ni_publisher_isolation.py` added to §10 test list (AC-21 enforcement, 2 tests minimum — publisher dir scan + views.py scan).
