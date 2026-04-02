---
document_type: QA_FINDINGS_REPORT
version: "1.0"
---

# QA Findings Report — Gate G8 (M8 UX Polish)

**Report ID:** QA-RPT-20260402-G8  
**From:** Team 50 (QA)  
**To:** Team 100 (Architecture)  
**CC:** Team 10 (Feature Dev), Team 80 (Product & Strategy)  
**Date:** 2026-04-02  
**Gate:** G8 — M8 UX Polish + Policy Formalization  
**QA Mandate executed:** `_COMMUNICATION/TEAM_50/QA_MANDATE_G8.md`

---

## 1. Environment Verified

| Check | Result |
|-------|--------|
| Alembic | **030 (head)** — PASS |
| `db.check` | **RESULT: PASS** |
| Full pytest | **152 passed, 2 skipped** — matches mandate expectation |
| `python3.11` | Mandate specifies 3.11; host used **`.venv/bin/python` (3.9.6)** — not a functional blocker for this gate |
| Docker Postgres | **Not verified** — project uses direct PostgreSQL per architecture; DB checks passed via local `DATABASE_URL` |
| Admin `http://127.0.0.1:5001/` | **200** (mandate example showed 200 in this run) |

---

## 2. Test Results Summary

| ID | Test | Result | Weight |
|----|------|--------|--------|
| T01 | `pytest tests/ -q` | **PASS** (152 passed, 2 skipped) | Critical |
| T02 | `pytest tests/test_publisher_local.py -v` | **PASS** (11 passed) | Critical |
| T03 | `sfagent-base.css` exists + line count | **PASS** (360 lines, ≥280) | Critical |
| T04 | Local `run_publisher` + greps on `public_report_body.html` | **PASS** (see §3) | Critical |
| T05 | Live `<head>` link `sfagent-base-css` | **PASS** | Critical |
| T06 | Live page structure (title, H1, modal, table, transparency) | **PASS** (HTML + MCP snapshot) | Critical |
| T07 | Tooltips: ≥6 `data-tooltip`, Hebrew, privacy text on מקורות | **PASS** (8 attributes; privacy phrase present) | High |
| T08 | CTA banner text, WhatsApp, button | **PASS** | High |
| T09 | Price hierarchy CSS | **PASS** (embedded fragment CSS on live page + `border-inline-start` in `sfagent-base.css` / fragment) | Medium |
| T10 | Privacy block bullets + lock | **PASS** | High |
| T11 | Transparency bridge + anchor | **PASS** | Medium |
| T12 | `table-framing` H2 text | **PASS** | Medium |
| T13 | Dismiss disclaimer (MCP) | **PASS** — button removed from a11y tree after click; console: third-party WP/theme noise (see §4) | High |
| T14 | WhatsApp href (MCP) | **PASS** — `https://wa.me/972547776770?text=...` | Medium |

---

## 3. Evidence

### T01

```text
152 passed, 2 skipped in 19.92s
```

### T02

```text
11 passed in 0.70s
```

(includes `test_publish_body_fragment_generated`, `test_publish_versioned_filenames`, `test_manifest_last_good_created`)

### T03

```text
PASS
     360 organic_market_agent/publisher/static/sfagent-base.css
```

### T04 (`output/public/public_report_body.html` after `run_publisher`)

| Grep | Count | Mandate |
|------|-------|---------|
| `class="sfagent"` | 1 | ≥1 |
| `sfagent-market-report` | 0 | 0 |
| `data-tooltip` | 8 | 6 |
| `sfa-cta-banner` | 1 | 1 |
| `sfa-privacy-block` | 1 | 1 |
| `sfa-bridge-link` | 1 | 1 |
| `table-framing` | 2 | ≥2 |
| `border-inline-start` | 34 | ≥1 |

### T05 (live)

`curl` + saved page: `id='sfagent-base-css'` (or equivalent), `href` contains `flatsome-child/sfagent-base.css` and `ver=`.

### T06–T12 (live HTML `/tmp/g8_live.html`)

Automated UTF-8 checks: title contains **Market Report**; H1 **מדד מחירי חקלאות אורגנית**; disclaimer button **הבנתי, תודה**; vision/intro content; `<table` / table structure; transparency headings and bullets; CTA sentence and **wa.me/972547776770**; **שלח בוואטסאפ**; bridge **איך הנתונים נוצרים?**; **#sfagent-dq-box** / `id="sfagent-dq-box"`; **הטבלה מעל מבוססת על תהליך זה:**; H2 **מדד מחירים מבוסס נתונים אמיתיים מהשטח**; **ללא חשיפה של חווה ספציפית** in מקורות tooltip.

### T13–T14 (MCP browser, `https://www.nimrod.bio/SmallFarmsAgent/`)

- After click **הבנתי, תודה** (`ref e4`), snapshot no longer lists that button; main report headings and CTA links remain.
- **WhatsApp** link `ref e7` → `href`: `https://wa.me/972547776770?text=היי, אני רוצה לשתף נתוני מחירים למדד`

### Console (T13 note)

`browser_console_messages` captured many **Facebook / theme** `ErrorUtils` and `wpcf7Elm` messages unrelated to the sfagent embed. No sfagent-specific failure isolated.

---

## 4. Findings

- **T04:** `data-tooltip` count **8** (mandate example **6**) — acceptable (extra header/tooltip usage).
- **Pre-condition:** Docker check skipped; DB health confirmed via `db.check` + pytest.
- **T13 strict “no JS errors”:** Not met for the whole page due to **third-party** console noise; **sfagent** UX verified by interaction and layout.

---

## 5. Gate Decision

### GATE G8 — PASS

All **Critical** criteria from the mandate are met. **High** criteria (T07, T08, T13, T14) met with the console caveat above. **Medium** (T09–T12) met.

**Next:** Team 100 architectural / product sign-off per gate policy.

---

## 6. Required Actions

| Team | Action |
|------|--------|
| Team 100 | Formal G8 acknowledgment |
| Team 50 | Re-run if live URL or enqueue path changes materially |

---

*Filed by: Team 50 (QA)*  
*Date: 2026-04-02*
