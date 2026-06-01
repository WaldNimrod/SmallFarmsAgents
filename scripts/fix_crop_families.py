"""F-DATA-001 corrective — re-point crops mis-assigned to the wrong botanical family.

Root cause (fixed separately in importer/jmf_masterclass.py): the JMF importer used
``session.query(CropFamily).first()`` as the NOT-NULL family fallback, which returns
the FIRST row in crop_families — **Aizoaceae** (the ice-plant family) — and silently
stamped it onto ~26 crops it created before the Tend baseline ran (tomato, carrots,
lettuce, cucumbers, …).

This corrective re-points each affected crop to its **canonical botanical family**.
The target families were cross-checked against the Tend CROP_PLAN source AND botanical
correctness (note: Tend's CSV mislabels Okra as Solanaceae — Okra is Malvaceae — so we
do NOT blindly trust the CSV; Okra is already correct in the DB and is out of scope here).

New Zealand Spinach (Tetragonia) is LEGITIMATELY Aizoaceae and is intentionally NOT in
the map below — it must keep its family.

Idempotent: only updates a crop when its current family differs from the canonical one,
and only touches the explicit 26 crops below. Safe to re-run.

Usage:
    python scripts/fix_crop_families.py            # DRY-RUN (default) — prints planned changes
    python scripts/fix_crop_families.py --apply    # writes to the live DB (SSoT)
"""
from __future__ import annotations

import argparse
import sys

from organic_market_agent.crop_book.models import Crop, CropFamily
from organic_market_agent.db.session import SessionFactory

# Canonical botanical family per crop (keyed by crops.name_en). These 26 crops were
# wrongly stamped Aizoaceae by the .first() fallback. Each target verified botanically.
CANONICAL_FAMILY_BY_CROP_EN: dict[str, str] = {
    "Arugula": "Brassicaceae",
    "Basil": "Lamiaceae",
    "Beans (default: Pole/Climbing)": "Fabaceae",
    "Beets": "Amaranthaceae",
    "Carrots": "Apiaceae",
    "Chard": "Amaranthaceae",
    "Cucumbers": "Cucurbitaceae",
    "Dill": "Apiaceae",
    "Eggplant": "Solanaceae",
    "Fennel": "Apiaceae",
    "Garlic": "Amaryllidaceae",
    "Ginger": "Zingiberaceae",
    "Kale": "Brassicaceae",
    "Kohlrabi": "Brassicaceae",
    "Lettuce": "Asteraceae",
    "Lettuce: Salad Mix": "Asteraceae",
    "Melons": "Cucurbitaceae",
    "Onions": "Amaryllidaceae",
    "Onions: Scallions": "Amaryllidaceae",
    "Parsley": "Apiaceae",
    "Radishes": "Brassicaceae",
    "Spinach": "Amaranthaceae",
    "Strawberry": "Rosaceae",
    "Summer Squash": "Cucurbitaceae",
    "Tomatoes": "Solanaceae",
    "Winter Squash": "Cucurbitaceae",
}

# Crops legitimately on Aizoaceae — must NOT be changed (sanity guard).
LEGIT_AIZOACEAE = {"New Zealand Spinach"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="F-DATA-001 crop→family corrective")
    parser.add_argument("--apply", action="store_true",
                        help="write changes to the DB (default: dry-run)")
    args = parser.parse_args(argv)
    apply = args.apply

    session = SessionFactory()
    changes: list[tuple[str, str, str]] = []   # (name_en, from_family, to_family)
    skipped_same: list[str] = []
    not_found: list[str] = []
    missing_family: list[str] = []
    try:
        # Pre-resolve target family rows by scientific_name
        fam_by_name = {
            f.scientific_name: f
            for f in session.query(CropFamily).all()
        }

        for name_en, target_family in CANONICAL_FAMILY_BY_CROP_EN.items():
            crop = session.query(Crop).filter_by(name_en=name_en).one_or_none()
            if crop is None:
                not_found.append(name_en)
                continue
            target = fam_by_name.get(target_family)
            if target is None:
                missing_family.append(f"{name_en} → {target_family}")
                continue
            current = crop.family.scientific_name if crop.family else "(none)"
            if crop.family_id == target.id:
                skipped_same.append(name_en)
                continue
            changes.append((name_en, current, target_family))
            if apply:
                crop.family_id = target.id

        # Sanity guard: every crop still on Aizoaceae after this map should be a
        # known-legit one (New Zealand Spinach). Flag any surprise.
        aizo = fam_by_name.get("Aizoaceae")
        unexpected_aizo: list[str] = []
        if aizo is not None:
            for crop in session.query(Crop).filter_by(family_id=aizo.id).all():
                if crop.name_en in CANONICAL_FAMILY_BY_CROP_EN:
                    continue  # will be / was re-pointed
                if crop.name_en in LEGIT_AIZOACEAE:
                    continue
                unexpected_aizo.append(crop.name_en)

        # ---- report ----
        print(f"\n=== F-DATA-001 crop→family corrective ({'APPLY' if apply else 'DRY-RUN'}) ===")
        print(f"planned changes: {len(changes)}  |  already-correct: {len(skipped_same)}")
        for name_en, frm, to in changes:
            print(f"  {name_en:32s} {frm:16s} → {to}")
        if not_found:
            print(f"\n[WARN] crops in map not found in DB: {not_found}")
        if missing_family:
            print(f"\n[WARN] target family row missing: {missing_family}")
        if unexpected_aizo:
            print(f"\n[WARN] crops still on Aizoaceae NOT in map (review!): {unexpected_aizo}")
        else:
            print("\n[OK] no unexpected crops left on Aizoaceae (only legit: "
                  f"{sorted(LEGIT_AIZOACEAE)}).")

        if apply:
            session.commit()
            print(f"\n[APPLIED] {len(changes)} crop family_id updates committed.")
        else:
            session.rollback()
            print("\n[DRY-RUN] no changes written. Re-run with --apply to commit.")

        # Non-zero exit if data integrity surprises that need a human
        return 1 if (not_found or missing_family or unexpected_aizo) else 0
    finally:
        session.close()


if __name__ == "__main__":
    sys.exit(main())
