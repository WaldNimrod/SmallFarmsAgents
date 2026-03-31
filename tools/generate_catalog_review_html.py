#!/usr/bin/env python3
"""Regenerate tools/catalog_review.html from the live products table.

Uses the same ordering as Admin GET /products: display_order, then code.
Ensures every row shown under /products appears on the catalog review page.

Usage (from repo root, with DATABASE_URL or .env):
    python3 tools/generate_catalog_review_html.py
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env", override=False)

# Ensure package import
sys.path.insert(0, str(ROOT))


def fetch_catalog_rows():
    from organic_market_agent.db.session import SessionFactory, engine

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except OperationalError as e:
        raise SystemExit(
            "PostgreSQL not reachable. Set DATABASE_URL and run again.\n" f"Detail: {e}"
        ) from e

    with SessionFactory() as session:
        rows = session.execute(
            text(
                """
                SELECT p.code,
                       p.canonical_name_he,
                       mu.code AS unit_code,
                       p.category,
                       COALESCE(p.seasonality_notes, '') AS seasonality_notes,
                       p.is_active
                FROM products p
                JOIN measurement_units mu ON mu.id = p.default_measurement_unit_id
                ORDER BY p.display_order, p.code
                """
            )
        ).all()

    return [
        {
            "code": r[0],
            "canonical_name_he": r[1],
            "default_measurement_unit_code": r[2],
            "category": r[3],
            "seasonality_notes": r[4] or "",
            "is_active": bool(r[5]),
        }
        for r in rows
    ]


def build_html(catalog: list[dict], generated_at: str, count: int) -> str:
    catalog_json = json.dumps(catalog, ensure_ascii=False, indent=2)
    return f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>קטלוג — טיוטת שינויים (ייצוא לצוות)</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Heebo:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #f4f6f3;
      --card: #fff;
      --accent: #2d5a27;
      --border: #d8e0d4;
      --muted: #5c6658;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      font-family: "Heebo", system-ui, sans-serif;
      background: var(--bg);
      margin: 0;
      padding: 1rem 1rem 6rem;
      color: #1a1f18;
      line-height: 1.45;
    }}
    .toolbar {{
      position: sticky;
      top: 0;
      z-index: 10;
      background: rgba(244, 246, 243, 0.95);
      backdrop-filter: blur(8px);
      border-bottom: 1px solid var(--border);
      padding: 0.75rem 0;
      margin: -1rem -1rem 1rem;
      padding-inline: 1rem;
    }}
    .toolbar-inner {{
      max-width: 960px;
      margin: 0 auto;
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      align-items: center;
    }}
    h1 {{
      font-size: 1.15rem;
      font-weight: 700;
      margin: 0 0 0.25rem 0;
      color: var(--accent);
    }}
    .sub {{
      font-size: 0.8rem;
      color: var(--muted);
      margin-bottom: 0.75rem;
      max-width: 960px;
      margin-inline: auto;
    }}
    .sub code {{ direction: ltr; unicode-bidi: isolate; font-size: 0.85em; }}
    button {{
      font-family: inherit;
      font-weight: 600;
      cursor: pointer;
      border: none;
      border-radius: 8px;
      padding: 0.45rem 0.9rem;
      font-size: 0.875rem;
      background: var(--accent);
      color: #fff;
    }}
    button.secondary {{ background: #3d5c80; }}
    button.ghost {{
      background: #e8ece6;
      color: #1a1f18;
    }}
    button:disabled {{ opacity: 0.5; cursor: not-allowed; }}
    .status {{
      font-size: 0.8rem;
      color: var(--muted);
      min-height: 1.2em;
    }}
    .list {{
      max-width: 960px;
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      gap: 0.65rem;
    }}
    .row {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 0.75rem 1rem;
      display: grid;
      gap: 0.5rem;
      grid-template-columns: 1fr;
    }}
    .row.inactive {{ opacity: 0.85; border-color: #c5c5c5; }}
    @media (min-width: 640px) {{
      .row {{
        grid-template-columns: 7.5rem 1fr 1.2fr;
        align-items: start;
      }}
    }}
    .code {{
      font-weight: 700;
      direction: ltr;
      unicode-bidi: isolate;
      color: var(--accent);
      font-size: 0.95rem;
    }}
    .meta {{
      font-size: 0.8rem;
      color: var(--muted);
      direction: ltr;
      unicode-bidi: isolate;
      text-align: right;
    }}
    .name {{ font-weight: 600; }}
    .badge-inactive {{
      display: inline-block;
      font-size: 0.7rem;
      font-weight: 600;
      padding: 0.15rem 0.45rem;
      border-radius: 4px;
      background: #6c757d;
      color: #fff;
      margin-inline-start: 0.35rem;
      vertical-align: middle;
    }}
    textarea {{
      width: 100%;
      min-height: 3.2rem;
      resize: vertical;
      font-family: inherit;
      font-size: 0.9rem;
      padding: 0.5rem 0.6rem;
      border: 1px solid var(--border);
      border-radius: 8px;
      line-height: 1.4;
    }}
    textarea:focus {{
      outline: 2px solid var(--accent);
      outline-offset: 1px;
    }}
    textarea::placeholder {{ color: #9aa396; }}
  </style>
</head>
<body>
  <div class="toolbar">
    <div class="toolbar-inner">
      <div style="flex:1; min-width:200px">
        <strong>ייצוא</strong>
        <span class="status" id="status"></span>
      </div>
      <button type="button" id="btnCopyJson">העתק JSON (רק עם הערה)</button>
      <button type="button" class="secondary" id="btnCopyJsonAll">העתק JSON (הכל)</button>
      <button type="button" class="ghost" id="btnCopyTsv">העתק TSV</button>
      <button type="button" class="ghost" id="btnDownloadJson">הורד .json</button>
    </div>
  </div>

  <h1 style="max-width:960px;margin:0 auto 0.25rem;text-align:center">טיוטת שינויים — קטלוג מוצרים</h1>
  <p class="sub" style="text-align:center">
    מקור רשימה: טבלת <code>products</code> ב־PostgreSQL — אותה רצף כמו בניהול
    <strong>מוצרים</strong> (<code>/products</code>), כולל מוצרים לא פעילים.
    נוצר: <span class="ltr">{generated_at}</span> · <span class="ltr">{count}</span> שורות.
    לרענון: <code class="ltr">python3 tools/generate_catalog_review_html.py</code>
    <br>
    מלאו רק בשורות שדורשות שינוי. הדביקו את הפלט בצ’אט — פורמט JSON לניתוח אוטומטי.
  </p>

  <div class="list" id="list"></div>

  <script type="application/json" id="catalog-json">
{catalog_json}
  </script>
  <script>
    const CATALOG = JSON.parse(document.getElementById("catalog-json").textContent.trim());

    const listEl = document.getElementById("list");
    const statusEl = document.getElementById("status");

    function setStatus(msg, ok) {{
      statusEl.textContent = msg || "";
      statusEl.style.color = ok === false ? "#a33" : "var(--muted)";
    }}

    function buildRows() {{
      CATALOG.forEach((item, i) => {{
        const code = item.code;
        const nameHe = item.canonical_name_he;
        const unitCode = item.default_measurement_unit_code;
        const category = item.category;
        const season = item.seasonality_notes || "";
        const active = item.is_active !== false;
        const row = document.createElement("div");
        row.className = "row" + (active ? "" : " inactive");
        row.dataset.code = code;
        const badge = active ? "" : '<span class="badge-inactive">לא פעיל</span>';
        row.innerHTML = `
          <div>
            <div class="code">${{code}}</div>
            <div class="meta">${{unitCode}} · ${{category}}</div>
          </div>
          <div>
            <div class="name">${{escapeHtml(nameHe)}}${{badge}}</div>
            <div class="meta">${{escapeHtml(season)}}</div>
          </div>
          <div>
            <textarea id="note-${{i}}" placeholder="השינוי הנדרש (למשל: למזג ל-PRD027, לשנות שם, להסיר מקטלוג…)" rows="2"></textarea>
          </div>
        `;
        listEl.appendChild(row);
      }});
    }}

    function escapeHtml(s) {{
      const d = document.createElement("div");
      d.textContent = s;
      return d.innerHTML;
    }}

    function collectPayload(onlyWithNote) {{
      return CATALOG.map((item, i) => {{
        const note = document.getElementById("note-" + i).value.trim();
        return {{
          code: item.code,
          canonical_name_he: item.canonical_name_he,
          default_measurement_unit_code: item.default_measurement_unit_code,
          category: item.category,
          seasonality_notes: item.seasonality_notes || "",
          is_active: item.is_active,
          change_request: note,
        }};
      }}).filter((r) => !onlyWithNote || r.change_request.length > 0);
    }}

    async function copyText(text) {{
      try {{
        await navigator.clipboard.writeText(text);
        setStatus("הועתק ללוח.", true);
      }} catch (e) {{
        setStatus("לא ניתן להעתיק אוטומטית — השתמשו בהורדה או סמנו ידנית.", false);
      }}
    }}

    document.getElementById("btnCopyJson").addEventListener("click", () => {{
      const data = collectPayload(true);
      const wrap = {{
        exported_at: new Date().toISOString(),
        source: "tools/catalog_review.html",
        schema: "catalog_change_requests_v1",
        generated_from: "postgresql.products",
        items: data,
      }};
      copyText(JSON.stringify(wrap, null, 2));
    }});

    document.getElementById("btnCopyJsonAll").addEventListener("click", () => {{
      const data = collectPayload(false);
      const wrap = {{
        exported_at: new Date().toISOString(),
        source: "tools/catalog_review.html",
        schema: "catalog_change_requests_v1",
        generated_from: "postgresql.products",
        items: data,
      }};
      copyText(JSON.stringify(wrap, null, 2));
    }});

    document.getElementById("btnCopyTsv").addEventListener("click", () => {{
      const rows = collectPayload(false);
      const header = ["code", "canonical_name_he", "category", "unit", "season", "is_active", "change_request"].join("\\t");
      const lines = rows.map(
        (r) =>
          [r.code, r.canonical_name_he, r.category, r.default_measurement_unit_code, r.seasonality_notes, r.is_active ? "true" : "false", r.change_request.replace(/\\t/g, " ").replace(/\\n/g, " ")].join("\\t")
      );
      copyText([header, ...lines].join("\\n"));
    }});

    document.getElementById("btnDownloadJson").addEventListener("click", () => {{
      const wrap = {{
        exported_at: new Date().toISOString(),
        source: "tools/catalog_review.html",
        schema: "catalog_change_requests_v1",
        generated_from: "postgresql.products",
        items: collectPayload(false),
      }};
      const blob = new Blob([JSON.stringify(wrap, null, 2)], {{ type: "application/json;charset=utf-8" }});
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = "catalog_change_requests_" + new Date().toISOString().slice(0, 10) + ".json";
      a.click();
      URL.revokeObjectURL(a.href);
      setStatus("הקובץ הורד.", true);
    }});

    buildRows();
  </script>
</body>
</html>
"""


def main() -> None:
    catalog = fetch_catalog_rows()
    if not catalog:
        raise SystemExit("No products returned — aborting.")
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    out_path = ROOT / "tools" / "catalog_review.html"
    out_path.write_text(
        build_html(catalog, generated_at, len(catalog)),
        encoding="utf-8",
    )
    print(f"Wrote {out_path} ({len(catalog)} products)")


if __name__ == "__main__":
    main()
