#!/usr/bin/env python3
"""Regenerate tools/unresolved_review.html from live unresolvable raw names.

Uses the same query as Admin GET /unresolved (top 200 by count).
Each row includes a feedback field; export JSON/TSV for team / automation.

This HTML is a working snapshot: filling fields does not persist to PostgreSQL
until aliases/rules are created via Admin or migrations from exported data.

Usage (from repo root, with DATABASE_URL or .env):
    python3 tools/generate_unresolved_review_html.py
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env", override=False)

sys.path.insert(0, str(ROOT))


def fetch_unresolved_rows():
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
                SELECT COALESCE(rei.raw_product_name, '') AS raw_product_name,
                       COUNT(*)                            AS cnt,
                       COUNT(DISTINCT sfr.source_id)       AS source_cnt,
                       STRING_AGG(DISTINCT s.code, ', ' ORDER BY s.code) AS source_codes,
                       MAX(rei.extracted_at)               AS last_seen
                FROM raw_extracted_items rei
                JOIN source_fetch_runs sfr ON sfr.id = rei.source_fetch_run_id
                JOIN sources s ON s.id = sfr.source_id
                WHERE rei.extraction_status = 'unresolvable'
                  AND rei.is_quarantined = false
                GROUP BY rei.raw_product_name
                ORDER BY cnt DESC
                LIMIT 200
                """
            )
        ).all()

    out = []
    for r in rows:
        raw = r[0]
        last = r[4]
        out.append(
            {
                "raw_product_name": raw,
                "count": int(r[1]),
                "source_cnt": int(r[2]),
                "source_codes": r[3] or "",
                "last_seen": last.strftime("%Y-%m-%d") if last else "—",
                "url_encoded": quote(raw, safe=""),
            }
        )
    return out


def build_html(items: list[dict], generated_at: str, count: int) -> str:
    items_json = json.dumps(items, ensure_ascii=False, indent=2)
    return f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>לא מזוהים — משוב וטיוטת פעולות</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Heebo:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #f4f6f3;
      --card: #fff;
      --accent: #6b4c1e;
      --accent2: #2d5a27;
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
      max-width: 1000px;
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
      color: var(--accent2);
    }}
    .sub {{
      font-size: 0.8rem;
      color: var(--muted);
      margin-bottom: 0.75rem;
      max-width: 1000px;
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
      background: var(--accent2);
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
    .admin-base {{
      max-width: 1000px;
      margin: 0 auto 0.75rem;
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      align-items: center;
      font-size: 0.8rem;
      color: var(--muted);
    }}
    .admin-base input {{
      flex: 1;
      min-width: 220px;
      padding: 0.35rem 0.5rem;
      border: 1px solid var(--border);
      border-radius: 6px;
      font-family: inherit;
      direction: ltr;
      text-align: left;
    }}
    .list {{
      max-width: 1000px;
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
      gap: 0.65rem;
      grid-template-columns: 1fr;
    }}
    @media (min-width: 720px) {{
      .row {{
        grid-template-columns: 1fr minmax(12rem, 16rem) 1fr;
        align-items: start;
      }}
    }}
    .raw-name {{
      font-weight: 700;
      font-size: 1rem;
      word-break: break-word;
    }}
    .raw-name.empty {{ color: #888; font-style: italic; }}
    .stats {{
      font-size: 0.8rem;
      color: var(--muted);
      direction: ltr;
      unicode-bidi: isolate;
      text-align: right;
    }}
    .stats strong {{ color: #3d4a3a; }}
    .codes {{
      font-size: 0.78rem;
      color: var(--muted);
      direction: ltr;
      unicode-bidi: isolate;
      word-break: break-word;
    }}
    a.row-link {{
      font-size: 0.8rem;
      color: var(--accent2);
      text-decoration: none;
      display: inline-block;
      margin-top: 0.35rem;
    }}
    a.row-link:hover {{ text-decoration: underline; }}
    textarea {{
      width: 100%;
      min-height: 3.6rem;
      resize: vertical;
      font-family: inherit;
      font-size: 0.9rem;
      padding: 0.5rem 0.6rem;
      border: 1px solid var(--border);
      border-radius: 8px;
      line-height: 1.4;
    }}
    textarea:focus {{
      outline: 2px solid var(--accent2);
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
      <button type="button" id="btnCopyJson">העתק JSON (רק עם משוב)</button>
      <button type="button" class="secondary" id="btnCopyJsonAll">העתק JSON (הכל)</button>
      <button type="button" class="ghost" id="btnCopyTsv">העתק TSV</button>
      <button type="button" class="ghost" id="btnDownloadJson">הורד .json</button>
    </div>
  </div>

  <h1 style="max-width:1000px;margin:0 auto 0.25rem;text-align:center">שמות גולמיים לא מזוהים — משוב</h1>
  <p class="sub" style="text-align:center">
    מקור: אותה שאילתה כמו בניהול <strong>לא מזוהים</strong> (<code>/unresolved</code>) — עד 200 שורות לפי תדירות.
    נוצר: <span class="ltr">{generated_at}</span> · <span class="ltr">{count}</span> שורות.
    לרענון: <code class="ltr">python3 tools/generate_unresolved_review_html.py</code>
    <br>
    מלאו משוב רק כשיש החלטה (אליאס, מוצר חדש, תיקון מקור, להתעלם וכו׳). ניתן להדביק JSON בצ׳אט או לשמור קובץ.
  </p>

  <div class="admin-base">
    <label for="adminBaseUrl">כתובת בסיס לניהול (אופציונלי, לקישור &quot;ניתוח&quot;):</label>
    <input type="url" id="adminBaseUrl" placeholder="http://127.0.0.1:5001" autocomplete="off">
  </div>

  <div class="list" id="list"></div>

  <script type="application/json" id="items-json">
{items_json}
  </script>
  <script>
    const ITEMS = JSON.parse(document.getElementById("items-json").textContent.trim());

    const listEl = document.getElementById("list");
    const statusEl = document.getElementById("status");
    const adminBaseInput = document.getElementById("adminBaseUrl");

    const LS_KEY = "unresolved_review_admin_base";

    function loadBase() {{
      try {{
        const v = localStorage.getItem(LS_KEY);
        if (v) adminBaseInput.value = v;
      }} catch (e) {{}}
    }}
    function saveBase() {{
      try {{
        localStorage.setItem(LS_KEY, adminBaseInput.value.trim());
      }} catch (e) {{}}
    }}
    adminBaseInput.addEventListener("change", () => {{ saveBase(); wireDetailLinks(); }});
    adminBaseInput.addEventListener("input", () => {{ wireDetailLinks(); }});
    loadBase();

    function setStatus(msg, ok) {{
      statusEl.textContent = msg || "";
      statusEl.style.color = ok === false ? "#a33" : "var(--muted)";
    }}

    function adminDetailHref(enc) {{
      const b = adminBaseInput.value.trim().replace(/\\/+$/, "");
      if (!b) return null;
      return b + "/unresolved/" + enc;
    }}

    function wireDetailLinks() {{
      document.querySelectorAll("a.row-link[data-enc]").forEach((a) => {{
        const enc = a.getAttribute("data-enc");
        const h = adminDetailHref(enc);
        if (h) a.setAttribute("href", h);
        else a.setAttribute("href", "#");
      }});
    }}

    function buildRows() {{
      ITEMS.forEach((item, i) => {{
        const raw = item.raw_product_name;
        const display = raw === "" ? "(ריק)" : raw;
        const emptyClass = raw === "" ? " empty" : "";
        const row = document.createElement("div");
        row.className = "row";
        row.dataset.index = String(i);
        const linkHtml = `<a class="row-link" href="#" data-enc="${{escapeAttr(item.url_encoded)}}" target="_blank" rel="noopener">פתח ניתוח בניהול ↗</a>`;
        row.innerHTML = `
          <div>
            <div class="raw-name${{emptyClass}}">${{escapeHtml(display)}}</div>
            ${{linkHtml}}
          </div>
          <div>
            <div class="stats"><strong>${{item.count}}</strong> הופעות · <strong>${{item.source_cnt}}</strong> מקורות</div>
            <div class="meta" style="font-size:0.75rem;color:var(--muted);margin-top:0.25rem">נצפה אחרון: <span class="ltr">${{escapeHtml(item.last_seen)}}</span></div>
          </div>
          <div>
            <div class="codes" title="קודי מקור">${{escapeHtml(item.source_codes || "—")}}</div>
            <textarea id="note-${{i}}" placeholder="משוב / החלטה (למשל: אליאס ל־PRD008, שם שגוי במקור SRC00x, להוסיף מוצר…)" rows="3"></textarea>
          </div>
        `;
        listEl.appendChild(row);
      }});
      wireDetailLinks();
    }}

    function escapeHtml(s) {{
      const d = document.createElement("div");
      d.textContent = s;
      return d.innerHTML;
    }}
    function escapeAttr(s) {{
      return s.replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;");
    }}

    function collectPayload(onlyWithNote) {{
      return ITEMS.map((item, i) => {{
        const note = document.getElementById("note-" + i).value.trim();
        return {{
          raw_product_name: item.raw_product_name,
          count: item.count,
          source_cnt: item.source_cnt,
          source_codes: item.source_codes,
          last_seen: item.last_seen,
          feedback: note,
        }};
      }}).filter((r) => !onlyWithNote || r.feedback.length > 0);
    }}

    async function copyText(text) {{
      try {{
        await navigator.clipboard.writeText(text);
        setStatus("הועתק ללוח.", true);
      }} catch (e) {{
        setStatus("לא ניתן להעתיק אוטומטית — נסו הורדה או העתקה ידנית.", false);
      }}
    }}

    function wrapExport(items) {{
      return {{
        exported_at: new Date().toISOString(),
        source: "tools/unresolved_review.html",
        schema: "unresolved_change_requests_v1",
        generated_from: "postgresql.raw_extracted_items (unresolvable, top 200)",
        items,
      }};
    }}

    document.getElementById("btnCopyJson").addEventListener("click", () => {{
      copyText(JSON.stringify(wrapExport(collectPayload(true)), null, 2));
    }});

    document.getElementById("btnCopyJsonAll").addEventListener("click", () => {{
      copyText(JSON.stringify(wrapExport(collectPayload(false)), null, 2));
    }});

    document.getElementById("btnCopyTsv").addEventListener("click", () => {{
      const rows = collectPayload(false);
      const header = ["raw_product_name", "count", "source_cnt", "source_codes", "last_seen", "feedback"].join("\\t");
      const lines = rows.map((r) =>
        [
          r.raw_product_name.replace(/\\t/g, " ").replace(/\\n/g, " "),
          r.count,
          r.source_cnt,
          (r.source_codes || "").replace(/\\t/g, " "),
          r.last_seen,
          r.feedback.replace(/\\t/g, " ").replace(/\\n/g, " "),
        ].join("\\t")
      );
      copyText([header, ...lines].join("\\n"));
    }});

    document.getElementById("btnDownloadJson").addEventListener("click", () => {{
      const blob = new Blob([JSON.stringify(wrapExport(collectPayload(false)), null, 2)], {{
        type: "application/json;charset=utf-8",
      }});
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = "unresolved_change_requests_" + new Date().toISOString().slice(0, 10) + ".json";
      a.click();
      URL.revokeObjectURL(a.href);
      setStatus("הקובץ הורד.", true);
    }});

    listEl.addEventListener("click", (e) => {{
      const a = e.target.closest("a.row-link");
      if (!a) return;
      if (a.getAttribute("href") === "#") {{
        e.preventDefault();
        setStatus("הזינו כתובת בסיס לניהול בשדה למעלה", false);
      }}
    }});

    buildRows();
  </script>
</body>
</html>
"""


def main() -> None:
    items = fetch_unresolved_rows()
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    out_path = ROOT / "tools" / "unresolved_review.html"
    out_path.write_text(
        build_html(items, generated_at, len(items)),
        encoding="utf-8",
    )
    print(f"Wrote {out_path} ({len(items)} unresolved raw names)")


if __name__ == "__main__":
    main()
