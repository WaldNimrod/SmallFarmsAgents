"""CLI runner for the 8-phase Crop Data Model Migration.

Usage:
    python -m organic_market_agent.crop_book.canon.migrate <phase> [--dry-run]

Phases:
    phase1  — Unit normalize (source_values.unit)
    phase2  — Enum canonicalize (T2/T3 source_values.value_text)
    phase3  — crop_attribute layer (migration 058 + attribute resolver)
    phase4  — Derive/dedup (delete stored T4 rows)
    phase5  — Rename + alias (field_name in source_values + enrichment + policy)
    phase6  — Drop duplicated columns (migration 059 — LAST DESTRUCTIVE)
    phase7  — Data-quality pass (name_he, storage_life_text, seeder_roller_plate)
    phase8  — Re-enrich + coverage snapshot
    all     — Run all 8 phases in order

Each phase is idempotent. Dumps are taken before phases 1/3/4/6 by the caller
(or by this runner when --auto-dump is passed).
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import re
import subprocess
import sys
from decimal import Decimal
from typing import Any

logger = logging.getLogger("cb_migrate")


def _get_session():
    """Return a SQLAlchemy Session connected to oma-postgres."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from dotenv import load_dotenv
    load_dotenv()
    # Import all models to ensure SQLAlchemy mapper is fully configured
    import organic_market_agent.crop_book.models  # noqa
    import organic_market_agent.crop_book.enrichment_models  # noqa
    import organic_market_agent.crop_book.attribute_models  # noqa
    db_url = os.environ.get("DATABASE_URL", "postgresql://oma@localhost:5433/organic_market_agent")
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    return Session()


def _dump_db(tag: str, dry_run: bool) -> str:
    """pg_dump | gzip → data/backups/. Returns filename."""
    import datetime as _dt
    ts = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"data/backups/pre-{tag}-{ts}.sql.gz"
    if dry_run:
        logger.info("[dry-run] Would dump DB to %s", fname)
        return fname
    os.makedirs("data/backups", exist_ok=True)
    cmd = (
        f"docker exec oma-postgres pg_dump -U oma -d organic_market_agent "
        f"| gzip > {fname}"
    )
    logger.info("Dumping DB: %s", fname)
    ret = subprocess.call(cmd, shell=True)
    if ret != 0:
        logger.warning("pg_dump exited with code %d", ret)
    else:
        logger.info("Dump complete: %s", fname)
    return fname


# ===========================================================================
# Phase 1 — Unit normalize
# ===========================================================================

def phase1(dry_run: bool = False) -> dict[str, Any]:
    """Normalize source_values.unit using UNIT_VARIANT_MAP."""
    from organic_market_agent.crop_book.canon.units import UNIT_VARIANT_MAP, normalize_unit
    from organic_market_agent.crop_book.models import CropVarietySourceValue

    session = _get_session()
    try:
        all_sv = session.query(CropVarietySourceValue).all()
        updated = 0
        for sv in all_sv:
            new_unit = normalize_unit(sv.field_name, sv.unit)
            if new_unit != (sv.unit or ""):
                logger.debug(
                    "unit normalize: variety=%s field=%r %r → %r",
                    sv.variety_id, sv.field_name, sv.unit, new_unit,
                )
                if not dry_run:
                    sv.unit = new_unit
                updated += 1

        if not dry_run:
            session.commit()
            logger.info("Phase 1: updated %d unit values", updated)
        else:
            logger.info("[dry-run] Phase 1: would update %d unit values", updated)

        # AC-02 check
        from sqlalchemy import text
        result = session.execute(text(
            "SELECT DISTINCT unit FROM crop_variety_source_values WHERE unit IS NOT NULL AND unit != '' ORDER BY unit"
        )).fetchall()
        distinct_units = [r[0] for r in result]
        logger.info("Phase 1 AC-02: distinct units after normalize: %s", distinct_units)

        # Check for non-canonical residuals
        from organic_market_agent.crop_book.canon.units import ALL_CANONICAL_UNITS
        bad = [u for u in distinct_units if u not in ALL_CANONICAL_UNITS]
        if bad:
            logger.warning("Phase 1 AC-02: non-canonical units still present: %s", bad)
        else:
            logger.info("Phase 1 AC-02: PASS — all units in canonical registry")

        return {"updated": updated, "distinct_units": distinct_units, "non_canonical": bad}
    finally:
        session.close()


# ===========================================================================
# Phase 2 — Enum canonicalize
# ===========================================================================

def phase2(dry_run: bool = False) -> dict[str, Any]:
    """Canonicalize T2/T3 value_text in source_values."""
    from organic_market_agent.crop_book.canon.enums import (
        canonicalize_enum, parse_month_list, ENUM_TOKENS, OPEN_VOCAB_ATTRS,
    )
    from organic_market_agent.crop_book.models import CropVarietySourceValue

    # Fields to canonicalize
    CLOSED_ENUM_FIELDS = {
        "planting_method", "frost_tolerance_class",
        "storage_ethylene_sensitivity", "harvest_unit", "harvest_stage",
    }
    LIST_FIELDS = {
        "seed_months_list": "sowing_months",
        "transplant_months_list": "transplant_months",
    }

    session = _get_session()
    try:
        updated_enum = 0
        updated_list = 0
        dq_log: list[dict] = []

        # Closed-enum fields
        for field_name in CLOSED_ENUM_FIELDS:
            rows = session.query(CropVarietySourceValue).filter_by(field_name=field_name).all()
            for sv in rows:
                if not sv.value_text:
                    continue
                canonical = canonicalize_enum(field_name, sv.value_text)
                tokens = ENUM_TOKENS.get(field_name)
                if canonical and tokens and canonical not in tokens:
                    dq_log.append({
                        "field": field_name, "raw": sv.value_text,
                        "canonical": canonical, "variety_id": sv.variety_id,
                    })
                if canonical and canonical != sv.value_text:
                    logger.debug(
                        "enum collapse: %r %r → %r (variety=%s)",
                        field_name, sv.value_text, canonical, sv.variety_id,
                    )
                    if not dry_run:
                        sv.value_text = canonical
                    updated_enum += 1

        # Open-vocab fields — normalize only
        for field_name in OPEN_VOCAB_ATTRS:
            rows = session.query(CropVarietySourceValue).filter_by(field_name=field_name).all()
            for sv in rows:
                if not sv.value_text:
                    continue
                normalized = canonicalize_enum(field_name, sv.value_text)
                if normalized and normalized != sv.value_text:
                    if not dry_run:
                        sv.value_text = normalized
                    updated_enum += 1

        # List fields (CSV → keep as-is for source_values; attribute_resolver converts)
        # We just validate/log them here; actual list conversion happens in Phase 3
        for source_field, canonical_attr in LIST_FIELDS.items():
            rows = session.query(CropVarietySourceValue).filter_by(field_name=source_field).all()
            for sv in rows:
                if sv.value_text:
                    parsed = parse_month_list(sv.value_text)
                    if parsed is None:
                        dq_log.append({
                            "field": source_field, "raw": sv.value_text,
                            "variety_id": sv.variety_id, "note": "unparseable month list",
                        })
                    updated_list += 1

        if not dry_run:
            session.commit()
            logger.info("Phase 2: updated %d enum + %d list validations", updated_enum, updated_list)
        else:
            logger.info("[dry-run] Phase 2: would update %d enum values", updated_enum)

        if dq_log:
            logger.warning("Phase 2 DQ: %d out-of-set or unparseable values: %s",
                           len(dq_log), json.dumps(dq_log, ensure_ascii=False))
        else:
            logger.info("Phase 2 AC-03: PASS — 0 out-of-set closed-enum values")

        return {"updated_enum": updated_enum, "dq_violations": len(dq_log), "dq_log": dq_log}
    finally:
        session.close()


# ===========================================================================
# Phase 3 — crop_attribute layer
# ===========================================================================

def phase3(dry_run: bool = False) -> dict[str, Any]:
    """Run migration 058 (DDL) + attribute resolver (DML)."""
    import subprocess as _sp

    # Run migration 058 (creates crop_attribute table)
    if not dry_run:
        logger.info("Phase 3: running alembic upgrade 058")
        ret = _sp.call(
            ["python3", "-m", "alembic", "upgrade", "058"],
            cwd="/Users/nimrod/Documents/SmallFarmsAgents",
        )
        if ret != 0:
            raise RuntimeError("alembic upgrade 058 failed")
    else:
        logger.info("[dry-run] Phase 3: would run alembic upgrade 058")

    # Run attribute resolver
    from organic_market_agent.crop_book.importer.attribute_resolver import run_attribute_resolver
    session = _get_session()
    try:
        summary = run_attribute_resolver(session, dry_run=dry_run)
        if not dry_run:
            session.commit()
        logger.info("Phase 3: %s", summary)

        # AC-04 check
        from sqlalchemy import text
        result = session.execute(text(
            "SELECT attribute_name, COUNT(*) FROM crop_attribute GROUP BY attribute_name ORDER BY attribute_name"
        )).fetchall()
        attr_counts = {r[0]: r[1] for r in result}

        from organic_market_agent.crop_book.importer.attribute_resolver import ALL_ATTRIBUTES
        missing_attrs = [a for a in ALL_ATTRIBUTES if a not in attr_counts]
        logger.info("Phase 3 AC-04: attribute counts: %s", attr_counts)
        if missing_attrs:
            logger.warning("Phase 3 AC-04: attributes with 0 rows: %s", missing_attrs)
        else:
            logger.info("Phase 3 AC-04: PASS — all 11 §7.2 attributes present")

        return {
            "resolver_summary": str(summary),
            "attr_counts": attr_counts,
            "missing_attrs": missing_attrs,
        }
    finally:
        session.close()


# ===========================================================================
# Phase 4 — Derive / dedup
# ===========================================================================

def phase4(dry_run: bool = False) -> dict[str, Any]:
    """Delete stored T4 (derived) rows from BOTH tables; convert per-m²-only crops first.

    Canon rule (LOD200 §6.4): yield_per_m2, oxide nutrients (p2o5/k2o),
    plants_per_m2, and avg_revenue are DERIVED — never stored.

    Correctness note: derived fields must be removed from BOTH:
      - crop_variety_source_values  (source data that drives enrichment)
      - crop_field_enrichment       (cached consensus rows)
    Deleting only from crop_field_enrichment is insufficient because Phase 8
    re-enrichment will regenerate them from the surviving source_values rows.

    Safety conversions are applied first (idempotent):
      - p2o5 → elemental P (÷ 2.29) for varieties lacking p_kg_ha
      - k2o → elemental K (÷ 1.205) for varieties lacking k_kg_ha
      - yield_per_m2_kg → avg_yield_per_bed_m (× 0.8) for varieties lacking bed_m
    """
    from sqlalchemy import text

    # The 4 canon-forbidden derived fields + avg_revenue (all must be 0 in both tables)
    DERIVED_FIELDS = [
        "yield_per_m2_kg",
        "nutrient_removal_p2o5_kg_ha",
        "nutrient_removal_k2o_kg_ha",
        "plants_per_m2",
        "avg_revenue_per_bed_m",
    ]

    session = _get_session()
    try:
        # ------------------------------------------------------------------
        # Step 1a: Safety — oxide → elemental P conversion
        # Insert nutrient_removal_p_kg_ha for any variety_id that has p2o5
        # but no elemental p (idempotent: skip if elemental already exists).
        # ------------------------------------------------------------------
        p_inserted = 0
        if not dry_run:
            p_result = session.execute(text("""
                INSERT INTO crop_variety_source_values
                    (variety_id, field_name, source, value_numeric, unit, note,
                     trust_tier, confidence_weight)
                SELECT
                    v.variety_id,
                    'nutrient_removal_p_kg_ha',
                    v.source || ':derived_from_oxide',
                    v.value_numeric / 2.29,
                    'kg_per_ha',
                    'Derived from nutrient_removal_p2o5_kg_ha / 2.29 (P2O5->P elemental)',
                    v.trust_tier,
                    v.confidence_weight
                FROM crop_variety_source_values v
                WHERE v.field_name = 'nutrient_removal_p2o5_kg_ha'
                  AND v.value_numeric IS NOT NULL
                  AND v.variety_id NOT IN (
                    SELECT DISTINCT variety_id
                    FROM crop_variety_source_values
                    WHERE field_name = 'nutrient_removal_p_kg_ha'
                  )
            """))
            p_inserted = p_result.rowcount
            if p_inserted:
                logger.info("Phase 4 safety: inserted %d elemental P rows (from P2O5)", p_inserted)

        # ------------------------------------------------------------------
        # Step 1b: Safety — oxide → elemental K conversion
        # ------------------------------------------------------------------
        k_inserted = 0
        if not dry_run:
            k_result = session.execute(text("""
                INSERT INTO crop_variety_source_values
                    (variety_id, field_name, source, value_numeric, unit, note,
                     trust_tier, confidence_weight)
                SELECT
                    v.variety_id,
                    'nutrient_removal_k_kg_ha',
                    v.source || ':derived_from_oxide',
                    v.value_numeric / 1.205,
                    'kg_per_ha',
                    'Derived from nutrient_removal_k2o_kg_ha / 1.205 (K2O->K elemental)',
                    v.trust_tier,
                    v.confidence_weight
                FROM crop_variety_source_values v
                WHERE v.field_name = 'nutrient_removal_k2o_kg_ha'
                  AND v.value_numeric IS NOT NULL
                  AND v.variety_id NOT IN (
                    SELECT DISTINCT variety_id
                    FROM crop_variety_source_values
                    WHERE field_name = 'nutrient_removal_k_kg_ha'
                  )
            """))
            k_inserted = k_result.rowcount
            if k_inserted:
                logger.info("Phase 4 safety: inserted %d elemental K rows (from K2O)", k_inserted)

        # ------------------------------------------------------------------
        # Step 1c: Safety — yield_per_m2_kg → avg_yield_per_bed_m conversion
        # For varieties with ONLY per-m² yield (no per-bed-m). Idempotent.
        # ------------------------------------------------------------------
        converted = 0
        m2_only = session.execute(text("""
            SELECT DISTINCT cvsv.variety_id
            FROM crop_variety_source_values cvsv
            WHERE cvsv.field_name = 'yield_per_m2_kg'
              AND cvsv.variety_id NOT IN (
                SELECT DISTINCT variety_id
                FROM crop_variety_source_values
                WHERE field_name IN ('avg_yield_per_bed_m', 'yield_per_bed_m')
              )
        """)).fetchall()

        m2_only_ids = [r[0] for r in m2_only]

        if m2_only_ids:
            logger.info("Phase 4: converting %d per-m²-only varieties to per-bed-m", len(m2_only_ids))
            for vid in m2_only_ids:
                rows = session.execute(text("""
                    SELECT id, value_numeric, unit
                    FROM crop_variety_source_values
                    WHERE variety_id = :vid AND field_name = 'yield_per_m2_kg'
                    AND value_numeric IS NOT NULL
                """), {"vid": vid}).fetchall()

                for row in rows:
                    new_val = float(row[1]) * 0.8  # m²→bed_m: multiply by bed_width 0.8
                    if not dry_run:
                        session.execute(text("""
                            INSERT INTO crop_variety_source_values
                                (variety_id, field_name, source, value_numeric, unit, note)
                            SELECT :vid, 'avg_yield_per_bed_m', source,
                                   :new_val, 'kg_per_bed_m',
                                   'converted from yield_per_m2_kg × 0.8 (bed_width=0.8m)'
                            FROM crop_variety_source_values WHERE id = :row_id
                        """), {"vid": vid, "new_val": new_val, "row_id": row[0]})
                    converted += 1

        # ------------------------------------------------------------------
        # Step 2: Delete derived fields from BOTH tables (idempotent)
        # crop_variety_source_values must be cleaned FIRST so that Phase 8
        # re-enrichment cannot regenerate derived enrichment rows.
        # ------------------------------------------------------------------
        deleted_sv: dict[str, int] = {}
        deleted_enrichment: dict[str, int] = {}

        for field_name in DERIVED_FIELDS:
            # Count + delete from source_values
            sv_cnt = session.execute(text(
                "SELECT COUNT(*) FROM crop_variety_source_values WHERE field_name = :fn"
            ), {"fn": field_name}).scalar() or 0
            deleted_sv[field_name] = sv_cnt

            if not dry_run and sv_cnt:
                session.execute(text(
                    "DELETE FROM crop_variety_source_values WHERE field_name = :fn"
                ), {"fn": field_name})
                logger.info(
                    "Phase 4: deleted %d source_values rows for derived field %r",
                    sv_cnt, field_name,
                )

            # Count + delete from crop_field_enrichment
            en_cnt = session.execute(text(
                "SELECT COUNT(*) FROM crop_field_enrichment WHERE field_name = :fn"
            ), {"fn": field_name}).scalar() or 0
            deleted_enrichment[field_name] = en_cnt

            if not dry_run and en_cnt:
                session.execute(text(
                    "DELETE FROM crop_field_enrichment WHERE field_name = :fn"
                ), {"fn": field_name})
                logger.info(
                    "Phase 4: deleted %d enrichment rows for derived field %r",
                    en_cnt, field_name,
                )

        if not dry_run:
            session.commit()

        # ------------------------------------------------------------------
        # AC-05 check — both tables must have 0 rows for all derived fields
        # ------------------------------------------------------------------
        residual_sv: dict[str, int] = {}
        residual_en: dict[str, int] = {}
        for field_name in DERIVED_FIELDS:
            residual_sv[field_name] = session.execute(text(
                "SELECT COUNT(*) FROM crop_variety_source_values WHERE field_name = :fn"
            ), {"fn": field_name}).scalar() or 0
            residual_en[field_name] = session.execute(text(
                "SELECT COUNT(*) FROM crop_field_enrichment WHERE field_name = :fn"
            ), {"fn": field_name}).scalar() or 0

        all_zero = all(v == 0 for v in {**residual_sv, **residual_en}.values())
        logger.info(
            "Phase 4 AC-05: residual source_values=%s enrichment=%s",
            residual_sv, residual_en,
        )
        if all_zero:
            logger.info("Phase 4 AC-05: PASS — 0 stored derived rows in both tables")
        else:
            logger.warning(
                "Phase 4 AC-05: FAIL — non-zero derived rows: sv=%s en=%s",
                residual_sv, residual_en,
            )

        return {
            "safety_p_inserted": p_inserted,
            "safety_k_inserted": k_inserted,
            "converted_per_m2": converted,
            "deleted_source_values": deleted_sv,
            "deleted_enrichment": deleted_enrichment,
            "residual_sv": residual_sv,
            "residual_en": residual_en,
            "ac05_pass": all_zero,
        }
    finally:
        session.close()


# ===========================================================================
# Phase 5 — Rename + alias
# ===========================================================================

def phase5(dry_run: bool = False) -> dict[str, Any]:
    """Rename field_name in source_values, enrichment, and field_policy keys."""
    from organic_market_agent.crop_book.canon.field_registry import RENAME_MAP
    from sqlalchemy import text

    session = _get_session()
    try:
        sv_updated: dict[str, int] = {}
        en_updated: dict[str, int] = {}

        for old_name, canonical_name in RENAME_MAP.items():
            if old_name == canonical_name:
                continue

            # source_values
            cnt = session.execute(text(
                "SELECT COUNT(*) FROM crop_variety_source_values WHERE field_name = :fn"
            ), {"fn": old_name}).scalar() or 0
            sv_updated[old_name] = cnt

            if cnt and not dry_run:
                session.execute(text(
                    "UPDATE crop_variety_source_values SET field_name = :new WHERE field_name = :old"
                ), {"new": canonical_name, "old": old_name})
                logger.info("Phase 5: renamed source_values %r → %r (%d rows)", old_name, canonical_name, cnt)

            # crop_field_enrichment
            cnt_e = session.execute(text(
                "SELECT COUNT(*) FROM crop_field_enrichment WHERE field_name = :fn"
            ), {"fn": old_name}).scalar() or 0
            en_updated[old_name] = cnt_e

            if cnt_e and not dry_run:
                session.execute(text(
                    "UPDATE crop_field_enrichment SET field_name = :new WHERE field_name = :old"
                ), {"new": canonical_name, "old": old_name})
                logger.info("Phase 5: renamed enrichment %r → %r (%d rows)", old_name, canonical_name, cnt_e)

        if not dry_run:
            session.commit()
            logger.info("Phase 5: renames committed")

        # AC-06 check: verify no old names remain in source_values or enrichment
        residual_sv: list[str] = []
        residual_en: list[str] = []
        for old_name in RENAME_MAP:
            cnt = session.execute(text(
                "SELECT COUNT(*) FROM crop_variety_source_values WHERE field_name = :fn"
            ), {"fn": old_name}).scalar() or 0
            if cnt:
                residual_sv.append(f"{old_name}({cnt})")
            cnt_e = session.execute(text(
                "SELECT COUNT(*) FROM crop_field_enrichment WHERE field_name = :fn"
            ), {"fn": old_name}).scalar() or 0
            if cnt_e:
                residual_en.append(f"{old_name}({cnt_e})")

        ac06_pass = not residual_sv and not residual_en
        if ac06_pass:
            logger.info("Phase 5 AC-06: PASS — no old field names remain")
        else:
            logger.warning("Phase 5 AC-06: residual sv=%s en=%s", residual_sv, residual_en)

        return {
            "sv_updated": sv_updated,
            "en_updated": en_updated,
            "residual_sv": residual_sv,
            "residual_en": residual_en,
            "ac06_pass": ac06_pass,
        }
    finally:
        session.close()


# ===========================================================================
# Phase 6 — Drop duplicated columns (migration 059)
# ===========================================================================

def phase6(dry_run: bool = False) -> dict[str, Any]:
    """Run migration 059 (DDL — drops §7.4 columns)."""
    import subprocess as _sp

    if dry_run:
        logger.info("[dry-run] Phase 6: would run alembic upgrade 059")
        return {"action": "dry_run_skip"}

    logger.info("Phase 6: running alembic upgrade 059")
    ret = _sp.call(
        ["python3", "-m", "alembic", "upgrade", "059"],
        cwd="/Users/nimrod/Documents/SmallFarmsAgents",
    )
    if ret != 0:
        raise RuntimeError("alembic upgrade 059 failed")

    logger.info("Phase 6 AC-08: migration 059 complete")
    return {"alembic_059": "applied"}


# ===========================================================================
# Phase 7 — Data-quality pass
# ===========================================================================

def phase7(dry_run: bool = False) -> dict[str, Any]:
    """DQ: purge name_he pollution, seeder_roller_plate residue, storage_life_text,
    validate nursery trio."""
    from sqlalchemy import text

    session = _get_session()
    try:
        results: dict[str, Any] = {}

        # --- D8: purge duration text from variety name_he ---
        # Pattern: name_he values containing digits + Hebrew time words
        polluted = session.execute(text(r"""
            SELECT id, name_he
            FROM crop_varieties
            WHERE name_he ~ '[0-9]'
              AND (name_he ~ 'יום|שבוע|חודש|שנה')
        """)).fetchall()
        results["name_he_polluted_count"] = len(polluted)
        logger.info("Phase 7 D8: %d polluted name_he rows", len(polluted))

        if polluted and not dry_run:
            # Set name_he = NULL for polluted variety rows
            # (they are non-default varieties where name was a duration string)
            for row in polluted:
                session.execute(text(
                    "UPDATE crop_varieties SET name_he = NULL WHERE id = :vid"
                ), {"vid": row[0]})
            logger.info("Phase 7 D8: nulled %d polluted name_he values", len(polluted))
        results["name_he_polluted_nulled"] = len(polluted) if not dry_run else 0

        # --- seeder_roller_plate source_values residue ---
        srp_cnt = session.execute(text(
            "SELECT COUNT(*) FROM crop_variety_source_values WHERE field_name = 'seeder_roller_plate'"
        )).scalar() or 0
        results["seeder_roller_plate_residue"] = srp_cnt
        logger.info("Phase 7: seeder_roller_plate source_values rows: %d", srp_cnt)

        if srp_cnt and not dry_run:
            session.execute(text(
                "DELETE FROM crop_variety_source_values WHERE field_name = 'seeder_roller_plate'"
            ))
            logger.info("Phase 7: deleted %d seeder_roller_plate residue rows", srp_cnt)

        # --- storage_life_text DROP (F-190-MIG-02) ---
        slt_cnt = session.execute(text(
            "SELECT COUNT(*) FROM crop_variety_source_values WHERE field_name = 'storage_life_text'"
        )).scalar() or 0
        results["storage_life_text_rows"] = slt_cnt
        logger.info("Phase 7 F-190-MIG-02: storage_life_text rows: %d", slt_cnt)

        if slt_cnt and not dry_run:
            session.execute(text(
                "DELETE FROM crop_variety_source_values WHERE field_name = 'storage_life_text'"
            ))
            logger.info("Phase 7: deleted %d storage_life_text rows", slt_cnt)

        # --- Nursery trio validation (canonical names — F-190-MIG-03) ---
        # nursery_days_to_germinate ≤ nursery_days_to_potting ≤ days_in_nursery
        trio_violations: list[dict] = []

        from sqlalchemy import text as _t
        # Get all varieties with at least some nursery data
        nursery_data = session.execute(_t("""
            SELECT variety_id, field_name, value_best
            FROM crop_field_enrichment
            WHERE field_name IN ('nursery_days_to_germinate', 'nursery_days_to_potting', 'days_in_nursery')
        """)).fetchall()

        # Group by variety
        trio_by_variety: dict[int, dict[str, float]] = {}
        for row in nursery_data:
            vid, fname, val = row
            if val is not None:
                trio_by_variety.setdefault(vid, {})[fname] = float(val)

        for vid, fields in trio_by_variety.items():
            germ = fields.get("nursery_days_to_germinate")
            pot = fields.get("nursery_days_to_potting")
            total = fields.get("days_in_nursery")

            violations = []
            if germ is not None and pot is not None and germ > pot:
                violations.append(f"nursery_days_to_germinate({germ}) > nursery_days_to_potting({pot})")
            if pot is not None and total is not None and pot > total:
                violations.append(f"nursery_days_to_potting({pot}) > days_in_nursery({total})")
            if germ is not None and total is not None and germ > total:
                violations.append(f"nursery_days_to_germinate({germ}) > days_in_nursery({total})")

            if violations:
                trio_violations.append({"variety_id": vid, "violations": violations})

        results["nursery_trio_violations"] = len(trio_violations)
        if trio_violations:
            logger.warning("Phase 7 trio violations: %s", trio_violations)
        else:
            logger.info("Phase 7 F-190-MIG-03: nursery trio PASS — 0 violations")

        if not dry_run:
            session.commit()

        # AC-09 checks
        # Verify zero residuals
        final_slt = session.execute(text(
            "SELECT COUNT(*) FROM crop_variety_source_values WHERE field_name = 'storage_life_text'"
        )).scalar() or 0
        final_srp = session.execute(text(
            "SELECT COUNT(*) FROM crop_variety_source_values WHERE field_name = 'seeder_roller_plate'"
        )).scalar() or 0
        final_name_he = session.execute(text(r"""
            SELECT COUNT(*) FROM crop_varieties
            WHERE name_he ~ '[0-9]' AND (name_he ~ 'יום|שבוע|חודש|שנה')
        """)).scalar() or 0

        results.update({
            "final_storage_life_text": final_slt,
            "final_seeder_roller_plate": final_srp,
            "final_polluted_name_he": final_name_he,
            "trio_violations_list": trio_violations,
        })

        ac09_pass = (final_slt == 0 and final_srp == 0 and final_name_he == 0
                     and len(trio_violations) == 0)
        results["ac09_pass"] = ac09_pass
        if ac09_pass:
            logger.info("Phase 7 AC-09: PASS")
        else:
            logger.warning("Phase 7 AC-09: FAIL — see results")

        return results
    finally:
        session.close()


# ===========================================================================
# Phase 8 — Re-enrich + coverage snapshot
# ===========================================================================

def phase8(dry_run: bool = False) -> dict[str, Any]:
    """Re-run enrichment_runner (numerics) + attribute_resolver (categoricals).
    Generate COVERAGE_SNAPSHOT_CB1.
    """
    from organic_market_agent.crop_book.importer.enrichment_runner import run_enrichment
    from organic_market_agent.crop_book.importer.attribute_resolver import run_attribute_resolver
    from sqlalchemy import text

    session = _get_session()
    try:
        # Re-run enrichment (numerics)
        logger.info("Phase 8: running enrichment_runner")
        enrich_summary = run_enrichment(session, dry_run=dry_run)
        if not dry_run:
            session.commit()
        logger.info("Phase 8 enrichment: %s", enrich_summary)

        # Re-run attribute resolver (categoricals)
        logger.info("Phase 8: running attribute_resolver")
        attr_summary = run_attribute_resolver(session, dry_run=dry_run)
        if not dry_run:
            session.commit()
        logger.info("Phase 8 attributes: %s", attr_summary)

        # Generate coverage snapshot
        # Mandatory fields (from calculator_meta required_book_fields, canonical names)
        MANDATORY_FIELDS = [
            "days_to_maturity", "spacing_in_row_cm", "rows_per_bed",
            "yield_per_bed_m", "price_documented", "seeds_per_g",
            "days_in_nursery", "succession_interval_weeks",
            "harvest_window_max_days",
            "nutrient_removal_n_kg_per_ha",
            "germination_temp_c_min", "germination_temp_c_opt", "germination_temp_c_max",
        ]
        MANDATORY_ATTRS = [
            "planting_method", "frost_tolerance_class", "season_window",
            "sowing_months", "transplant_months",
        ]

        # Get all default varieties
        varieties = session.execute(text("""
            SELECT cv.id, c.name_he as crop_name_he, c.name_en as crop_name_en
            FROM crop_varieties cv
            JOIN crops c ON c.id = cv.crop_id
            WHERE cv.is_default = TRUE
            ORDER BY c.name_he
        """)).fetchall()

        # Get enrichment coverage
        enrich_data = session.execute(text("""
            SELECT variety_id, field_name
            FROM crop_field_enrichment
            WHERE field_name = ANY(:fields)
              AND value_best IS NOT NULL
        """), {"fields": MANDATORY_FIELDS}).fetchall()
        enrich_set = {(r[0], r[1]) for r in enrich_data}

        # Get attribute coverage
        attr_data = session.execute(text("""
            SELECT variety_id, attribute_name
            FROM crop_attribute
            WHERE attribute_name = ANY(:attrs)
        """), {"attrs": MANDATORY_ATTRS}).fetchall()
        attr_set = {(r[0], r[1]) for r in attr_data}

        complete = []
        partial = []

        for v in varieties:
            vid = v[0]
            crop_name = v[1] or v[2] or str(vid)

            # Check all mandatory numeric fields
            missing_numeric = [f for f in MANDATORY_FIELDS if (vid, f) not in enrich_set]
            missing_attr = [a for a in MANDATORY_ATTRS if (vid, a) not in attr_set]
            all_missing = missing_numeric + missing_attr

            if not all_missing:
                complete.append({"variety_id": vid, "crop": crop_name})
            else:
                partial.append({
                    "variety_id": vid,
                    "crop": crop_name,
                    "missing": all_missing,
                })

        logger.info("Phase 8: COMPLETE=%d, PARTIAL=%d", len(complete), len(partial))

        return {
            "enrich_summary": str(enrich_summary),
            "attr_summary": str(attr_summary),
            "complete_count": len(complete),
            "partial_count": len(partial),
            "complete": complete,
            "partial": partial,
        }
    finally:
        session.close()


# ===========================================================================
# Main CLI
# ===========================================================================

PHASE_FNS = {
    "phase1": (phase1, True),   # (fn, dump_before)
    "phase2": (phase2, False),
    "phase3": (phase3, True),
    "phase4": (phase4, True),
    "phase5": (phase5, False),
    "phase6": (phase6, True),
    "phase7": (phase7, False),
    "phase8": (phase8, False),
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Crop Data Model Migration CLI (WP-CB-MIG 8 phases)"
    )
    parser.add_argument(
        "phase",
        choices=list(PHASE_FNS.keys()) + ["all"],
        help="Phase to run (or 'all' for all 8 phases in order)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Compute but do not write to DB",
    )
    parser.add_argument(
        "--auto-dump", action="store_true",
        help="Take pg_dump before phases that write (1/3/4/6)",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    phases_to_run = list(PHASE_FNS.keys()) if args.phase == "all" else [args.phase]

    for phase_name in phases_to_run:
        fn, dump_before = PHASE_FNS[phase_name]
        if dump_before and args.auto_dump:
            _dump_db(phase_name, args.dry_run)

        logger.info("=== Running %s%s ===", phase_name, " [dry-run]" if args.dry_run else "")
        try:
            result = fn(dry_run=args.dry_run)
            print(json.dumps({"phase": phase_name, "result": result}, ensure_ascii=False, indent=2, default=str))
        except Exception as exc:
            logger.error("Phase %s FAILED: %s", phase_name, exc, exc_info=True)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
