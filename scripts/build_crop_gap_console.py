"""Build crop gap validation console (WP-CB-MIG2 WI-11 / AC-12).

Scans the live DB for (crop × missing field) gaps, groups them by the 13
canonical topics, pre-fills best-effort defaults (PR parse where available),
and generates a self-contained HTML page at data/crop_gap_console.html.

The HTML includes:
  - One record per (crop × missing field) gap, grouped by topic
  - Pre-filled default values (PR source or marked agronomic default)
  - Confirm / edit / skip per field
  - Progress indicator
  - Export JSON to clipboard + download
  - No external dependencies (inline CSS/JS)

Usage:
    python scripts/build_crop_gap_console.py --db-url postgresql://...
    python scripts/build_crop_gap_console.py --db-url sqlite:///dev.db --dry-run
    python scripts/build_crop_gap_console.py --db-url sqlite:///dev.db --output data/my_console.html
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPO_ROOT / "data" / "crop_gap_console.html"

# The 13 canonical topics (Canon §15) — used for grouping
TOPIC_KEYS_ORDERED = [
    "varieties", "spacing", "equipment", "soil", "bedprep",
    "sowing", "irrigation", "care", "pest", "harvest",
    "storage", "succession", "yield_inc",
]

TOPIC_LABELS_HE = {
    "varieties":  "זנים",
    "spacing":    "מרווח ופריסה",
    "equipment":  "ציוד וכיוונון",
    "soil":       "קרקע ודישון",
    "bedprep":    "הכנת ערוגה",
    "sowing":     "זריעה/שתילה",
    "irrigation": "השקיה",
    "care":       "טיפוח ועישוב",
    "pest":       "מזיקים ומחלות",
    "harvest":    "קציר",
    "storage":    "שטיפה ואחסון",
    "succession": "רצף וחברה",
    "yield_inc":  "יבול/הכנסה",
}

# Field → topic mapping (Canon §16)
FIELD_TOPIC_MAP: dict[str, str] = {
    # equipment
    "seeder":               "equipment",
    "seeder_settings":      "equipment",
    # spacing
    "spacing_in_row_cm":    "spacing",
    "rows_per_bed":         "spacing",
    # soil
    "soil_ph_target":       "soil",
    "nutrient_removal_n_kg_per_ha": "soil",
    # sowing
    "sowing_months":        "sowing",
    "transplant_months":    "sowing",
    "planting_method":      "sowing",
    "days_in_nursery":      "sowing",
    "seeds_per_g":          "sowing",
    # irrigation
    "irrigation_type":      "irrigation",
    "drip_lines_per_bed":   "irrigation",
    "root_depth_class":     "irrigation",
    "needs_summer_shade":   "irrigation",
    # pest
    "common_pests":         "pest",
    "foliar_feeding_program": "pest",
    # harvest
    "days_to_maturity":     "harvest",
    "harvest_window_max_days": "harvest",
    "harvest_unit":         "harvest",
    "harvest_stage":        "harvest",
    "labor_rate_harvest":   "harvest",
    "unit_size":            "harvest",
    # storage
    "storage_life_days":    "storage",
    "storage_temp_c_min":   "storage",
    "storage_temp_c_max":   "storage",
    "labor_rate_wash":      "storage",
    # succession
    "succession_interval_weeks": "succession",
    "plantings_per_season": "succession",
    "harvest_weeks_span":   "succession",
    "season_window":        "succession",
    # yield_inc
    "yield_per_bed_m":      "yield_inc",
    "price_documented":     "yield_inc",
    # varieties (identity)
    "frost_tolerance_class": "varieties",
}

# Fields to check for gaps (T1 enrichment + T2/T3 attribute fields of interest)
T1_FIELDS_TO_CHECK = [
    "days_to_maturity", "harvest_window_max_days", "spacing_in_row_cm",
    "rows_per_bed", "yield_per_bed_m", "price_documented", "days_in_nursery",
    "seeds_per_g", "succession_interval_weeks", "soil_ph_target",
    "nutrient_removal_n_kg_per_ha", "storage_life_days",
    # MIG2 T1 additions
    "drip_lines_per_bed", "labor_rate_harvest", "labor_rate_wash",
    "plantings_per_season", "harvest_weeks_span",
]

T2_T3_FIELDS_TO_CHECK = [
    "planting_method", "frost_tolerance_class", "sowing_months",
    "harvest_unit", "harvest_stage", "season_window",
    # MIG2 T2/T3 additions
    "irrigation_type", "root_depth_class", "needs_summer_shade",
    "unit_size", "common_pests", "foliar_feeding_program",
]


def _fetch_gap_data(db_url: str) -> list[dict]:
    """Query the DB for (crop × missing_field) gaps.

    Returns list of gap records:
      {crop_id, crop_name_he, crop_slug, variety_id, field_name, topic,
       best_effort_default, default_source, is_numeric}
    """
    from sqlalchemy import create_engine, text

    engine = create_engine(db_url)
    gaps = []

    with engine.connect() as conn:
        # Get all crops + their default variety IDs
        crop_rows = conn.execute(text(
            "SELECT c.id AS crop_id, c.name_he, c.name_en, "
            "       v.id AS variety_id "
            "FROM crops c "
            "LEFT JOIN crop_varieties v ON v.crop_id = c.id AND v.is_default = TRUE "
            "ORDER BY c.name_he"
        )).fetchall()

        if not crop_rows:
            logger.warning("No crops found in DB")
            return []

        # Build variety_id → crop info map
        crop_by_variety: dict[int, dict] = {}
        variety_ids = []
        for row in crop_rows:
            if row[3] is None:
                continue  # no default variety
            vdata = {
                "crop_id": row[0],
                "crop_name_he": row[1] or row[2] or f"crop-{row[0]}",
                "crop_slug": (row[2] or "").lower().replace(" ", "-") or f"crop-{row[0]}",
                "variety_id": row[3],
            }
            crop_by_variety[row[3]] = vdata
            variety_ids.append(row[3])

        if not variety_ids:
            return []

        # Fetch existing T1 enrichment
        vid_list = ",".join(str(v) for v in variety_ids)
        field_list_q = ",".join(f"'{f}'" for f in T1_FIELDS_TO_CHECK)
        enrich_rows = conn.execute(text(
            f"SELECT variety_id, field_name, value_best "
            f"FROM crop_field_enrichment "
            f"WHERE variety_id IN ({vid_list}) AND field_name IN ({field_list_q})"
        )).fetchall()
        existing_t1: dict[tuple, float] = {
            (row[0], row[1]): float(row[2]) for row in enrich_rows if row[2] is not None
        }

        # Fetch existing T2/T3 attributes
        attr_list_q = ",".join(f"'{f}'" for f in T2_T3_FIELDS_TO_CHECK)
        attr_rows = conn.execute(text(
            f"SELECT variety_id, attribute_name, value_canonical, value_list "
            f"FROM crop_attribute "
            f"WHERE variety_id IN ({vid_list}) AND attribute_name IN ({attr_list_q})"
        )).fetchall()
        existing_t2t3: dict[tuple, str] = {}
        for row in attr_rows:
            val = row[2] or (json.dumps(row[3]) if row[3] else None)
            if val is not None:
                existing_t2t3[(row[0], row[1])] = val

        # Fetch PR source values for best-effort defaults
        all_fields = T1_FIELDS_TO_CHECK + T2_T3_FIELDS_TO_CHECK
        all_field_q = ",".join(f"'{f}'" for f in all_fields)
        sv_rows = conn.execute(text(
            f"SELECT variety_id, field_name, value_text, value_numeric, trust_tier "
            f"FROM crop_variety_source_values "
            f"WHERE variety_id IN ({vid_list}) "
            f"  AND field_name IN ({all_field_q}) "
            f"  AND trust_tier IN ('PR', 'EX', 'NI') "
            f"ORDER BY "
            f"  CASE trust_tier WHEN 'EX' THEN 1 WHEN 'NI' THEN 2 ELSE 3 END"
        )).fetchall()
        pr_defaults: dict[tuple, dict] = {}
        for row in sv_rows:
            key = (row[0], row[1])
            if key not in pr_defaults:
                val = row[2] or (str(row[3]) if row[3] is not None else None)
                if val:
                    pr_defaults[key] = {"value": val, "source": row[4]}

    # Build gap list
    for vid, crop_info in crop_by_variety.items():
        for field_name in T1_FIELDS_TO_CHECK:
            if (vid, field_name) not in existing_t1:
                pr = pr_defaults.get((vid, field_name), {})
                gaps.append({
                    "crop_id": crop_info["crop_id"],
                    "crop_name_he": crop_info["crop_name_he"],
                    "crop_slug": crop_info["crop_slug"],
                    "variety_id": vid,
                    "field_name": field_name,
                    "topic": FIELD_TOPIC_MAP.get(field_name, "yield_inc"),
                    "best_effort_default": pr.get("value"),
                    "default_source": pr.get("source", "agronomic_default"),
                    "is_numeric": True,
                })

        for field_name in T2_T3_FIELDS_TO_CHECK:
            if (vid, field_name) not in existing_t2t3:
                pr = pr_defaults.get((vid, field_name), {})
                gaps.append({
                    "crop_id": crop_info["crop_id"],
                    "crop_name_he": crop_info["crop_name_he"],
                    "crop_slug": crop_info["crop_slug"],
                    "variety_id": vid,
                    "field_name": field_name,
                    "topic": FIELD_TOPIC_MAP.get(field_name, "yield_inc"),
                    "best_effort_default": pr.get("value"),
                    "default_source": pr.get("source", "agronomic_default"),
                    "is_numeric": False,
                })

    return gaps


_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SFA Crop Gap Console — WP-CB-MIG2</title>
<style>
body{font-family:Arial,Helvetica,sans-serif;margin:0;padding:1rem;background:#f5f5f0;color:#222;font-size:14px}
h1{font-size:1.4rem;margin-bottom:.5rem}
.meta{color:#666;font-size:.9rem;margin-bottom:1rem}
.progress-bar{height:8px;background:#ddd;border-radius:4px;margin-bottom:1rem;position:sticky;top:0;z-index:10}
.progress-fill{height:100%;background:#4caf50;border-radius:4px;transition:width .2s}
.progress-text{font-size:.8rem;color:#555;text-align:center;margin-bottom:.5rem}
.topic-section{margin-bottom:1.5rem;background:#fff;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,.1)}
.topic-header{padding:.6rem 1rem;background:#e8f5e9;border-radius:8px 8px 0 0;font-weight:bold;font-size:1rem;cursor:pointer;display:flex;justify-content:space-between}
.topic-body{padding:0 .5rem}
.gap-row{padding:.5rem;border-bottom:1px solid #eee;display:grid;grid-template-columns:auto 1fr auto auto auto;gap:.5rem;align-items:center}
.gap-row:last-child{border-bottom:none}
.crop-name{font-weight:bold;min-width:100px}
.field-name{color:#1565c0;font-family:monospace;font-size:.85rem}
.value-input{border:1px solid #ccc;border-radius:4px;padding:.2rem .5rem;font-size:.85rem;width:150px}
.value-input.modified{border-color:#f57c00;background:#fff8e1}
.btn{border:none;border-radius:4px;padding:.25rem .6rem;cursor:pointer;font-size:.8rem}
.btn-confirm{background:#4caf50;color:#fff}
.btn-skip{background:#9e9e9e;color:#fff}
.btn-confirm.active{outline:2px solid #1b5e20}
.btn-skip.active{outline:2px solid #424242}
.source-badge{font-size:.7rem;padding:.1rem .3rem;border-radius:3px;background:#e3f2fd;color:#0d47a1}
.source-badge.agronomic{background:#fff9c4;color:#827717}
.actions-bar{position:sticky;bottom:0;background:#fff;padding:.8rem 1rem;border-top:2px solid #ccc;display:flex;gap:.5rem;flex-wrap:wrap;z-index:10}
.btn-export{background:#1565c0;color:#fff;padding:.4rem .8rem;font-size:.9rem}
.btn-download{background:#283593;color:#fff;padding:.4rem .8rem;font-size:.9rem}
.btn-expand-all{background:#e0e0e0;color:#333;padding:.4rem .8rem;font-size:.85rem}
.count-badge{font-size:.8rem;background:#eee;border-radius:10px;padding:.1rem .4rem}
</style>
</head>
<body>
<h1>SFA Crop Gap Console — WP-CB-MIG2</h1>
<div class="meta">Generated: __GENERATED_AT__ | __TOTAL_GAPS__ gaps across __TOTAL_CROPS__ crops</div>
<div class="progress-bar"><div class="progress-fill" id="pf" style="width:0%"></div></div>
<div class="progress-text" id="pt">0 / __TOTAL_GAPS__ confirmed or skipped</div>

__TOPIC_SECTIONS__

<div class="actions-bar">
  <button class="btn btn-export btn-confirm" onclick="exportJson()">📋 העתק JSON ללוח</button>
  <button class="btn btn-download btn-confirm" onclick="downloadJson()">⬇ הורד JSON</button>
  <button class="btn btn-expand-all" onclick="toggleAll()">הרחב/כווץ הכול</button>
  <span id="export-status" style="font-size:.85rem;color:#2e7d32"></span>
</div>

<script>
const gapData = __GAP_DATA_JSON__;
const decisions = {};

function updateProgress() {
  const total = gapData.length;
  const done = Object.keys(decisions).length;
  const pct = total > 0 ? Math.round(done / total * 100) : 0;
  document.getElementById('pf').style.width = pct + '%';
  document.getElementById('pt').textContent = done + ' / ' + total + ' אושרו/דולגו';
}

function onDecision(gapKey, action) {
  const row = document.querySelector('[data-gap-key="' + CSS.escape(gapKey) + '"]');
  const val = row ? row.querySelector('.value-input').value.trim() : '';
  decisions[gapKey] = {action: action, value: val};
  if (row) {
    row.querySelectorAll('.btn').forEach(b => b.classList.remove('active'));
    const btn = row.querySelector('.btn-' + action);
    if (btn) btn.classList.add('active');
  }
  updateProgress();
}

function onValueChange(input) {
  input.classList.toggle('modified', input.value.trim() !== input.dataset.original);
  const row = input.closest('.gap-row');
  if (row) {
    const gapKey = row.dataset.gapKey;
    if (gapKey && decisions[gapKey]) {
      decisions[gapKey].value = input.value.trim();
    }
  }
}

function buildExportData() {
  return gapData.filter(g => {
    const d = decisions[g.gap_key];
    return d && d.action === 'confirm' && d.value !== '';
  }).map(g => ({
    variety_id: g.variety_id,
    field_name: g.field_name,
    value: decisions[g.gap_key].value,
    is_numeric: g.is_numeric,
    crop_name_he: g.crop_name_he,
    topic: g.topic,
  }));
}

function exportJson() {
  const data = buildExportData();
  const json = JSON.stringify(data, null, 2);
  navigator.clipboard.writeText(json).then(() => {
    document.getElementById('export-status').textContent = '✓ הועתק (' + data.length + ' ערכים)';
    setTimeout(() => { document.getElementById('export-status').textContent = ''; }, 3000);
  }).catch(() => {
    prompt('העתק JSON:', json);
  });
}

function downloadJson() {
  const data = buildExportData();
  const json = JSON.stringify(data, null, 2);
  const blob = new Blob([json], {type: 'application/json'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'nimrod_validation_' + new Date().toISOString().slice(0,10) + '.json';
  a.click();
}

function toggleAll() {
  document.querySelectorAll('.topic-body').forEach(b => {
    b.style.display = b.style.display === 'none' ? '' : 'none';
  });
}

document.querySelectorAll('.topic-header').forEach(h => {
  h.addEventListener('click', () => {
    const body = h.nextElementSibling;
    body.style.display = body.style.display === 'none' ? '' : 'none';
  });
});

updateProgress();
</script>
</body>
</html>
"""


def _build_gap_row_html(gap: dict, gap_key: str) -> str:
    """Render a single gap row as HTML."""
    import html as html_mod
    crop_name = html_mod.escape(gap["crop_name_he"])
    field_name = html_mod.escape(gap["field_name"])
    default_val = html_mod.escape(str(gap["best_effort_default"] or ""))
    src = gap.get("default_source", "agronomic_default")
    src_label = "PR" if src.startswith("PR") else ("NI" if src.startswith("NI") else "default")
    src_class = "agronomic" if src_label == "default" else ""
    gap_key_escaped = html_mod.escape(gap_key)

    return (
        f'<div class="gap-row" data-gap-key="{gap_key_escaped}">'
        f'<span class="crop-name">{crop_name}</span>'
        f'<span class="field-name">{field_name}</span>'
        f'<span class="source-badge {src_class}">{src_label}</span>'
        f'<input class="value-input" type="text" value="{default_val}" '
        f'  data-original="{default_val}" '
        f'  onchange="onValueChange(this)" oninput="onValueChange(this)">'
        f'<button class="btn btn-confirm" onclick="onDecision(\'{gap_key_escaped}\',\'confirm\')">✓ אשר</button>'
        f'<button class="btn btn-skip" onclick="onDecision(\'{gap_key_escaped}\',\'skip\')">✗ דלג</button>'
        f'</div>'
    )


def generate_html(gaps: list[dict]) -> str:
    """Generate the self-contained HTML console."""
    import html as html_mod
    # Assign stable gap keys
    for i, gap in enumerate(gaps):
        gap["gap_key"] = f"g{i}"

    # Group by topic
    by_topic: dict[str, list[dict]] = {}
    for gap in gaps:
        topic = gap["topic"]
        by_topic.setdefault(topic, []).append(gap)

    topic_sections_html = []
    for topic_key in TOPIC_KEYS_ORDERED:
        topic_gaps = by_topic.get(topic_key, [])
        if not topic_gaps:
            continue
        label_he = html_mod.escape(TOPIC_LABELS_HE.get(topic_key, topic_key))
        count = len(topic_gaps)
        rows_html = "".join(_build_gap_row_html(g, g["gap_key"]) for g in topic_gaps)
        topic_sections_html.append(
            f'<div class="topic-section">'
            f'<div class="topic-header">'
            f'  <span>{label_he}</span>'
            f'  <span class="count-badge">{count} פערים</span>'
            f'</div>'
            f'<div class="topic-body">{rows_html}</div>'
            f'</div>'
        )

    gap_data_json = json.dumps(
        [
            {
                "gap_key": g["gap_key"],
                "variety_id": g["variety_id"],
                "field_name": g["field_name"],
                "is_numeric": g["is_numeric"],
                "crop_name_he": g["crop_name_he"],
                "topic": g["topic"],
            }
            for g in gaps
        ],
        ensure_ascii=False,
    )

    unique_crops = len({g["crop_id"] for g in gaps})
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    html_out = _HTML_TEMPLATE
    html_out = html_out.replace("__GENERATED_AT__", now)
    html_out = html_out.replace("__TOTAL_GAPS__", str(len(gaps)))
    html_out = html_out.replace("__TOTAL_CROPS__", str(unique_crops))
    html_out = html_out.replace("__TOPIC_SECTIONS__", "\n".join(topic_sections_html))
    html_out = html_out.replace("__GAP_DATA_JSON__", gap_data_json)
    return html_out


def cli_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build SFA crop gap validation console HTML (WP-CB-MIG2 WI-11)."
    )
    parser.add_argument("--db-url", required=False, default="sqlite:///dev.db",
                        help="SQLAlchemy DB URL.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT),
                        help=f"Output HTML path (default: {DEFAULT_OUTPUT}).")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print gap count + topic breakdown; do not write HTML.")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    logger.info("Scanning DB for gaps: %s", args.db_url)
    try:
        gaps = _fetch_gap_data(args.db_url)
    except Exception as exc:
        logger.error("DB scan failed: %s", exc)
        return 1

    logger.info("Found %d gaps", len(gaps))

    # Topic breakdown
    by_topic: dict[str, int] = {}
    for g in gaps:
        by_topic[g["topic"]] = by_topic.get(g["topic"], 0) + 1
    for tk in TOPIC_KEYS_ORDERED:
        if tk in by_topic:
            print(f"  {TOPIC_LABELS_HE.get(tk, tk):20s}: {by_topic[tk]} gaps")

    if args.dry_run:
        print(f"\nDry-run: {len(gaps)} total gaps — HTML not written.")
        return 0

    html = generate_html(gaps)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    logger.info("Console written to %s (%d bytes)", out_path, len(html))
    print(f"Console written: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(cli_main())
