#!/usr/bin/env python3
"""Build static SmallFarmsAgents client hub from JSON data files.

Usage:
    python scripts/build_sfa_client_hub.py
    python scripts/build_sfa_client_hub.py --out hub/dist

Output: hub/dist/ (index.html, roadmap.html, tasks.html, assets/)
"""

from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Dict, Optional

HUB_ROOT = Path(__file__).resolve().parent.parent / "hub"
DATA_DIR = HUB_ROOT / "data"
SRC_DIR = HUB_ROOT / "src"
SSOT_DIR = HUB_ROOT / "ssot"
DEFAULT_DIST = HUB_ROOT / "dist"

WHATSAPP_URL = "https://wa.me/972547776770"
BRAND_TEXT = "Agents OS @ nimrod.bio"
EXPORT_TYPE = "sfa-feedback"
DEFAULT_RESPONDENT = "Nimrod"


def load_json(path: Path) -> dict:
    if not path.exists():
        print(f"[ERROR] Missing data file: {path}")
        sys.exit(1)
    return json.loads(path.read_text(encoding="utf-8"))


def load_json_optional(path: Path) -> dict | None:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


STATUS_BADGE = {
    "completed": '<span class="badge badge-done">הושלם</span>',
    "in_progress": '<span class="badge badge-run">בביצוע</span>',
    "not_started": '<span class="badge badge-todo">לא התחיל</span>',
    "blocked": '<span class="badge badge-blocked">חסום</span>',
    "qa": '<span class="badge badge-qa">QA</span>',
    "pending": '<span class="badge badge-pending">ממתין</span>',
    "answered": '<span class="badge badge-done">הוגש</span>',
    "deferred": '<span class="badge badge-blocked">נדחה</span>',
}

PRIORITY_BADGE = {
    "גבוהה": '<span class="badge badge-high">גבוהה</span>',
    "בינונית": '<span class="badge badge-medium">בינונית</span>',
    "נמוכה": '<span class="badge badge-low">נמוכה</span>',
}


def load_ssot_answers() -> dict[str, dict]:
    """Load latest SSOT answers per decision ID from hub/ssot/responses/."""
    responses_dir = SSOT_DIR / "responses"
    if not responses_dir.exists():
        return {}
    answers: dict[str, dict] = {}
    for f in sorted(responses_dir.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        export = data.get("sourceExport", data)
        for a in export.get("answers", []):
            if a.get("id"):
                answers[a["id"]] = a
    return answers


def head(title: str, extra_scripts: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{escape(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Frank+Ruhl+Libre:wght@700&family=Heebo:wght@300;400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/hub-base.css">
<link rel="stylesheet" href="assets/hub.css">
{extra_scripts}
</head>
<body>
"""


def nav(active: str) -> str:
    items = [
        ("index.html", "כניסה"),
        ("roadmap.html", "מפת דרכים"),
        ("tasks.html", "משימות והחלטות"),
    ]
    parts = ["<nav>"]
    for href, label in items:
        page_key = href.replace(".html", "")
        if page_key == active:
            parts.append(f"<strong>{escape(label)}</strong>")
        else:
            parts.append(f'<a href="{href}">{escape(label)}</a>')
    parts.append("</nav>")
    return "\n".join(parts)


def foot(generated_iso: str) -> str:
    return f"""<footer class="project-foot">
ממשק תקשורת ומצב עבודה — SmallFarmsAgents<br>
נוצר אוטומטית: {escape(generated_iso)}<br>
ממשק זה אינו מחליף תיעוד רשמי — לשימוש פנימי בלבד.
</footer>
<div class="hub-brand">
<a href="{WHATSAPP_URL}" target="_blank" rel="noopener">{BRAND_TEXT}</a>
</div>
</body>
</html>"""


def status_html(status: str) -> str:
    return STATUS_BADGE.get(status, f'<span class="badge">{escape(status)}</span>')


def page_index(updates: dict, roadmap: dict, tasks: dict, generated_iso: str) -> str:
    milestones = roadmap.get("milestones", [])
    done_count = sum(1 for m in milestones if m["status"] == "completed")
    total_count = len(milestones)

    all_tasks = []
    for sec in tasks.get("sections", []):
        all_tasks.extend(sec.get("tasks", []))
    tasks_done = sum(1 for t in all_tasks if t.get("status") == "completed")
    tasks_total = len(all_tasks)

    html = head("SmallFarmsAgents — ממשק מצב עבודה")
    html += nav("index")
    html += '<div class="wrap">\n'
    html += "<h1>SmallFarmsAgents — ממשק מצב עבודה</h1>\n"
    html += f'<p class="subtitle">{escape(roadmap.get("summaryHe", ""))}</p>\n'

    html += '<div class="stats-row">\n'
    html += f'<div class="stat-card"><div class="stat-number">{done_count}/{total_count}</div><div class="stat-label">אבני דרך הושלמו</div></div>\n'
    html += f'<div class="stat-card"><div class="stat-number">{tasks_done}/{tasks_total}</div><div class="stat-label">משימות הושלמו</div></div>\n'

    current = roadmap.get("currentFocusId", "")
    current_ms = next((m for m in milestones if m["id"] == current), None)
    current_label = escape(current_ms["titleHe"]) if current_ms else "\u2014"
    html += f'<div class="stat-card"><div class="stat-number" style="font-size:1.2rem">{escape(current)}</div><div class="stat-label">מוקד נוכחי: {current_label}</div></div>\n'
    html += "</div>\n"

    html += "<h2>עדכונים אחרונים</h2>\n"
    for item in updates.get("items", [])[:5]:
        html += '<div class="card">\n'
        html += f'<div class="card-date">{escape(item["date"])}</div>\n'
        html += f'<div class="card-title">{escape(item["titleHe"])}</div>\n'
        html += f'<div class="card-body">{escape(item["bodyHe"])}</div>\n'
        html += "</div>\n"

    html += "</div>\n"
    html += foot(generated_iso)
    return html


def page_roadmap(roadmap: dict, generated_iso: str) -> str:
    milestones = roadmap.get("milestones", [])
    current_id = roadmap.get("currentFocusId", "")

    html = head("מפת דרכים — SmallFarmsAgents")
    html += nav("roadmap")
    html += '<div class="wrap">\n'
    html += "<h1>מפת דרכים</h1>\n"
    html += f'<p class="subtitle">{escape(roadmap.get("summaryHe", ""))}</p>\n'

    html += '<div class="table-wrap"><table class="data">\n'
    html += "<thead><tr><th>קוד</th><th>אבן דרך</th><th>סטטוס</th><th>פרטים</th></tr></thead>\n"
    html += "<tbody>\n"
    for m in milestones:
        row_class = ' class="current"' if m["id"] == current_id else ""
        html += f"<tr{row_class}>"
        html += f"<td><strong>{escape(m['code'])}</strong></td>"
        html += f"<td>{escape(m['titleHe'])}</td>"
        html += f"<td>{status_html(m['status'])}</td>"
        html += f"<td>{escape(m.get('detailHe', ''))}</td>"
        html += "</tr>\n"
    html += "</tbody></table></div>\n"

    breakdown = roadmap.get("currentFocusBreakdown")
    if breakdown and breakdown.get("milestoneId") == current_id:
        html += '<div class="focus-breakdown">\n'
        html += f"<h2>{escape(breakdown['titleHe'])}</h2>\n"
        html += f"<p>{escape(breakdown.get('introHe', ''))}</p>\n"

        for section in breakdown.get("sections", []):
            html += '<div class="focus-section">\n'
            html += f"<h3>{escape(section['titleHe'])}</h3>\n"
            html += '<div class="table-wrap"><table class="data">\n'
            html += "<thead><tr><th>מזהה</th><th>משימה</th><th>סטטוס</th><th>מצב</th></tr></thead>\n"
            html += "<tbody>\n"
            for task in section.get("tasks", []):
                html += "<tr>"
                html += f'<td><span class="d-id">{escape(task["id"])}</span></td>'
                html += f"<td>{escape(task['titleHe'])}</td>"
                html += f"<td>{status_html(task.get('status', 'not_started'))}</td>"
                html += f"<td>{escape(task.get('stateHe', ''))}</td>"
                html += "</tr>\n"
            html += "</tbody></table></div>\n"
            html += "</div>\n"

        html += "</div>\n"

    html += "</div>\n"
    html += foot(generated_iso)
    return html


def page_tasks(
    tasks_data: dict,
    decisions_data: dict,
    ssot_answers: dict[str, dict],
    generated_iso: str,
) -> str:
    decisions = decisions_data.get("decisions", [])
    decision_ids = [d["id"] for d in decisions]

    scripts = '<script src="assets/feedback.js"></script>'
    html = head("משימות והחלטות — SmallFarmsAgents", extra_scripts="")
    html += nav("tasks")
    html += '<div class="wrap">\n'
    html += "<h1>משימות והחלטות פתוחות</h1>\n"

    for section in tasks_data.get("sections", []):
        html += f"<h2>{escape(section['titleHe'])}</h2>\n"
        for task in section.get("tasks", []):
            priority = task.get("priorityHe", "")
            priority_html = PRIORITY_BADGE.get(priority, "")
            html += '<div class="task-row">\n'
            html += f'<div class="task-title">{status_html(task.get("status", "not_started"))} {escape(task["titleHe"])} {priority_html}</div>\n'
            html += f'<div class="task-state">{escape(task.get("stateHe", ""))}</div>\n'
            html += "</div>\n"

    html += "<h2>החלטות פתוחות</h2>\n"
    if decisions_data.get("introHe"):
        html += f'<p class="subtitle">{escape(decisions_data["introHe"])}</p>\n'

    for d in decisions:
        did = d["id"]
        ssot = ssot_answers.get(did, {})
        effective_status = "answered" if ssot.get("choice") or ssot.get("notes") else d.get("status", "pending")
        ssot_choice = ssot.get("choice", "")
        ssot_notes = ssot.get("notes", "")

        html += '<details class="decision-detail">\n'
        html += f'<summary><span class="d-id">{escape(did)}</span> {escape(d["titleHe"])} {status_html(effective_status)}</summary>\n'
        html += '<div class="decision-content">\n'
        html += f"<dt>הקשר</dt><dd>{escape(d.get('contextHe', ''))}</dd>\n"
        html += f"<dt>אפשרויות</dt><dd>{escape(d.get('optionsHe', ''))}</dd>\n"
        html += f"<dt>המלצה</dt><dd>{escape(d.get('recommendationHe', ''))}</dd>\n"

        html += f'<div class="feedback-field"><label for="choice-{escape(did)}">בחירה</label>'
        html += f'<input type="text" id="choice-{escape(did)}" value="{escape(ssot_choice)}" placeholder="הקלד בחירה..."></div>\n'

        html += f'<div class="feedback-field"><label for="notes-{escape(did)}">הערות</label>'
        html += f'<textarea id="notes-{escape(did)}" placeholder="הערות נוספות...">{escape(ssot_notes)}</textarea></div>\n'

        html += "</div>\n</details>\n"

    html += '<div class="respondent-field feedback-field">\n'
    html += f'<label for="respondent">שם המשיב</label>\n'
    html += f'<input type="text" id="respondent" value="{escape(DEFAULT_RESPONDENT)}" placeholder="שם...">\n'
    html += "</div>\n"

    html += '<div class="export-section">\n'
    html += '<p>ייצוא כל התשובות לקובץ JSON להעברה לצוות</p>\n'
    html += '<button class="btn-export" id="btn-export-json">ייצוא תשובות</button>\n'
    html += "</div>\n"

    html += "</div>\n"

    html += f"{scripts}\n"
    ids_json = json.dumps(decision_ids, ensure_ascii=False)
    html += f"""<script>
HubFeedback.init({{
  exportType: "{EXPORT_TYPE}",
  defaultRespondent: "{DEFAULT_RESPONDENT}",
  decisionIds: {ids_json}
}});
</script>\n"""

    html += foot(generated_iso)
    return html


def build(dist_dir: Path) -> None:
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True)

    roadmap = load_json(DATA_DIR / "roadmap.json")
    updates = load_json(DATA_DIR / "updates.json")
    tasks = load_json(DATA_DIR / "tasks.json")
    decisions = load_json(DATA_DIR / "decisions.json")
    ssot_answers = load_ssot_answers()

    if ssot_answers:
        print(f"[INFO] Loaded {len(ssot_answers)} SSOT answers")

    generated_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    assets_dir = dist_dir / "assets"
    assets_dir.mkdir()
    for asset_name in ("hub-base.css", "hub.css", "feedback.js"):
        src = SRC_DIR / "assets" / asset_name
        if src.exists():
            shutil.copy2(src, assets_dir / asset_name)
        else:
            print(f"[WARN] Asset not found: {src}")

    (dist_dir / "index.html").write_text(
        page_index(updates, roadmap, tasks, generated_iso), encoding="utf-8"
    )
    (dist_dir / "roadmap.html").write_text(
        page_roadmap(roadmap, generated_iso), encoding="utf-8"
    )
    (dist_dir / "tasks.html").write_text(
        page_tasks(tasks, decisions, ssot_answers, generated_iso), encoding="utf-8"
    )

    (dist_dir / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")

    metadata = {
        "generatedAt": generated_iso,
        "schemaVersion": 1,
        "project": "SmallFarmsAgents",
    }
    (dist_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    data_out = dist_dir / "data"
    data_out.mkdir()
    for name in ("roadmap.json", "updates.json", "tasks.json", "decisions.json"):
        src = DATA_DIR / name
        if src.exists():
            shutil.copy2(src, data_out / name)

    print(f"[OK] Hub built → {dist_dir}")
    print(f"     Generated: {generated_iso}")
    file_count = sum(1 for _ in dist_dir.rglob("*") if _.is_file())
    print(f"     Files: {file_count}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Build SmallFarmsAgents client hub")
    parser.add_argument("--out", type=str, default=None, help="Output directory")
    args = parser.parse_args()

    out = Path(args.out) if args.out else DEFAULT_DIST
    build(out)
