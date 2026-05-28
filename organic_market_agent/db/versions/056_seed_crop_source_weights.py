"""056: WP-C5 Phase A — seed crop_source_weights table.

Seeds the DB-driven source weights table created in migration 054 with:
  - All existing labels from SOURCE_REGISTRY (Python constants → DB rows)
  - The new **WR (Web-Research / AI-synthesized)** tier with weight = 0.60
    per DECISION_RECORD §Decision 5 (Option B — Moderate, team_00 approved).

Tier-default rows use prefix patterns (e.g. 'WR:*') so dynamic labels
inherit the right weight without explicit per-label seeds.

Idempotent via INSERT...ON CONFLICT (source_label) DO NOTHING.

Revision ID: 056
Revises: 055
Create Date: 2026-05-28
"""
from alembic import op
import sqlalchemy as sa

revision = "056"
down_revision = "055"
branch_labels = None
depends_on = None


# (source_label, trust_tier, weight, is_hard_override, requires_moderation, notes)
_SEED_ROWS = [
    # --- EX: Expert override (team_00 hardcoded) ---
    ("team_00", "EX", None, True, False,
     "Principal authority — always wins"),

    # --- NI: Nimrod-Input (prefix sentinel + concrete labels) ---
    ("NI:*", "NI", None, True, False,
     "Default for any NI:<name> label (Nimrod-provided file/link)"),
    ("NI:groworganic", "NI", None, True, False, "WP-C1 IL source"),
    ("NI:bustan", "NI", None, True, False, "WP-C1 IL source"),
    ("NI:il_moa_garden_guide", "NI", None, True, False,
     "WP-C4 IL Ministry of Agriculture garden guide"),
    ("NI:shaham_extension", "NI", None, True, False,
     "WP-C4 IL Shaham extension service"),
    ("NI:curtis_stone_book", "NI", None, True, False,
     "WP-C3 OCR — Curtis Stone book"),

    # --- PR: Prescriptive / published research (weight 0.70) ---
    ("JMF", "PR", "0.70", False, False, "JMF MasterClass curated agronomic"),
    ("PR:*", "PR", "0.70", False, False,
     "Default for any PR:<source> label (published research)"),
    ("PR:jmf_cover_crops", "PR", "0.70", False, False, "WP-C1 JMF cover crops"),
    ("PR:uc_anr_germination", "PR", "0.70", False, False, "WP-C4 UC ANR"),
    ("PR:purdue_germination", "PR", "0.70", False, False, "WP-C4 Purdue"),
    ("PR:osu_frost_tolerance", "PR", "0.70", False, False, "WP-C4 OSU"),
    ("PR:csu_planting_guide", "PR", "0.70", False, False, "WP-C4 CSU"),
    ("PR:umn_field_planning", "PR", "0.70", False, False, "WP-C4 UMN"),
    ("PR:umd_soil_ph", "PR", "0.70", False, False, "WP-C4 UMD"),
    ("PR:ne_veg_guide", "PR", "0.70", False, False, "WP-C4 NE veg guide"),
    ("PR:fao_fertilizer_use", "PR", "0.70", False, False, "WP-C4 FAO fertilizer"),
    ("PR:uf_ifas_companion", "PR", "0.70", False, False, "WP-C4 UF-IFAS companion"),
    ("PR:uc_davis_postharvest", "PR", "0.70", False, False,
     "WP-C4 UC Davis Cantwell postharvest"),

    # --- WR: Web-Research / AI-synthesized (NEW — weight 0.60 ★) ---
    # team_00 Decision #5 (Option B — Moderate):
    #   Higher than OP (0.55) because WR draws on multiple published sources.
    #   Lower than PR (0.70) because not first-party / peer-reviewed.
    #   Tunable later via UPDATE ... WHERE source_label = 'WR:*'.
    ("WR:*", "WR", "0.60", False, False,
     "Default for AI-synthesized web research (team_80 multi-engine scout). "
     "team_00 Decision #5 — Option B Moderate. Tune via UPDATE based on "
     "farmer feedback per team_00 critical requirement (DECISION_RECORD §5)."),

    # --- OP: Operational (weight 0.55) ---
    ("OP:*", "OP", "0.55", False, False,
     "Default for any OP:<source> label (operational farm data)"),
    ("Tend", "OP", "0.55", False, False, "Legacy flat Tend export"),
    ("Tend_2018", "OP", "0.55", False, False, "Tend year-export 2018"),
    ("Tend_2019", "OP", "0.55", False, False, "Tend year-export 2019"),
    ("Tend_2020", "OP", "0.55", False, False, "Tend year-export 2020"),
    ("Tend_2021", "OP", "0.55", False, False, "Tend year-export 2021"),
    ("Tend_2022", "OP", "0.55", False, False, "Tend year-export 2022"),
    ("OP:Idan_2017", "OP", "0.55", False, False, "WP-C1 Idan 2017"),
    ("OP:Idan_2018", "OP", "0.55", False, False, "WP-C3 Idan 2018"),
    ("OP:Idan_seedlings", "OP", "0.55", False, False, "WP-C3 Idan seedlings"),
    ("OP:FRANCHI_catalog", "OP", "0.55", False, False, "WP-C3 FRANCHI catalog"),
    ("OP:CurtisStone", "OP", "0.55", False, False, "WP-C3 Curtis Stone"),
    ("OP:vital_seeds_count", "OP", "0.55", False, False, "WP-C4 Vital seed count"),
    ("OP:osborne_seed_count", "OP", "0.55", False, False, "WP-C4 Osborne seed count"),

    # --- MK: Market index (placeholder; importer in WP-B) ---
    ("MK:*", "MK", "0.40", False, False, "Default for MK:<source> (market data)"),
    ("OMA:*", "MK", "0.40", False, False, "OMA community price index"),

    # --- WB: Web blog / third-party (placeholder; importer in WP-B) ---
    ("WB:*", "WB", "0.30", False, False, "Default for WB:<source> (web/blog)"),

    # --- UC: User-Community (moderation required) ---
    ("UC:*", "UC", None, False, True,
     "User-contributed — requires moderation; NULL weight until moderator sets one"),
]


def upgrade() -> None:
    bind = op.get_bind()

    # Use core-level insert with ON CONFLICT DO NOTHING for idempotency.
    # On SQLite the same syntax works (INSERT OR IGNORE → expressed via
    # ON CONFLICT DO NOTHING in modern SQLite ≥ 3.24).
    stmt = sa.text("""
        INSERT INTO crop_source_weights
          (source_label, trust_tier, weight, is_hard_override,
           requires_moderation, notes)
        VALUES
          (:label, :tier, :weight, :hard, :mod, :notes)
        ON CONFLICT (source_label) DO NOTHING
    """)
    for label, tier, weight, hard, mod, notes in _SEED_ROWS:
        bind.execute(stmt, {
            "label": label,
            "tier": tier,
            "weight": weight,
            "hard": hard,
            "mod": mod,
            "notes": notes,
        })


def downgrade() -> None:
    bind = op.get_bind()
    sa_ = sa
    labels = [row[0] for row in _SEED_ROWS]
    bind.execute(
        sa_.text("DELETE FROM crop_source_weights WHERE source_label = ANY(:labels)")
        if bind.dialect.name == "postgresql"
        else sa_.text("DELETE FROM crop_source_weights WHERE source_label IN ("
                      + ",".join(f"'{l}'" for l in labels) + ")"),
        {"labels": labels} if bind.dialect.name == "postgresql" else {},
    )
