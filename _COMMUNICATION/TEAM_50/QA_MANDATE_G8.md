---
document_type: QA_MANDATE
version: "1.0"
---

# QA Mandate — Gate G8

**Mandate ID:** QA-MANDATE-G8
**From:** Team 100 (Architecture)
**To:** Team 50 (QA)
**CC:** Team 10 (Feature Dev), Team 80 (Product & Strategy)
**Date:** 2026-04-02
**Milestone:** M8 — UX Polish + Policy Formalization
**Gate:** G8

---

## Scope

M8 introduced two major changes:
1. **CSS Architecture Refactor** — inline styles split into 3-layer system
2. **6 UX Feature Items** — tooltips, CTA banner, visual hierarchy, privacy block,
   transparency bridge, table framing

All changes are in the public page template and supporting CSS/PHP infrastructure.
No database, pipeline, or backend changes.

**Key files changed:**
- `organic_market_agent/publisher/templates/public_report_body.html`
- `organic_market_agent/publisher/static/sfagent-base.css` (NEW)
- `scripts/wp_shortcode_install.py`
- `tests/test_publisher_local.py` (assertion updates)

---

## Pre-conditions (verify before starting)

```bash
# 1. Alembic at 030
alembic current
# Expected: 030 (head)

# 2. DB health
python3.11 -m organic_market_agent.db.check
# Expected: RESULT: PASS

# 3. Full test suite
python3.11 -m pytest tests/ -q
# Expected: 152 passed, 2 skipped

# 4. Docker postgres running
docker ps | grep postgres
# Expected: running container

# 5. Admin server running
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5001/
# Expected: 200
```

---

## Test Suite

### T01 — Full pytest suite

```bash
python3.11 -m pytest tests/ -q
```

**Pass criterion:** 152 passed, 0 failed. 2 skips (upress markers) acceptable.
**Weight:** Critical

---

### T02 — Publisher artifact tests

```bash
python3.11 -m pytest tests/test_publisher_local.py -v
```

**Pass criterion:** All tests pass including:
- `test_publish_body_fragment_generated` — body contains `class="sfagent"` (not old `sfagent-market-report`)
- `test_publish_versioned_filenames` — versioned + fixed-name copies exist
- `test_manifest_last_good_created` — manifest fallback works

**Weight:** Critical

---

### T03 — CSS file exists in repo

```bash
test -f organic_market_agent/publisher/static/sfagent-base.css && echo "PASS" || echo "FAIL"
wc -l organic_market_agent/publisher/static/sfagent-base.css
```

**Pass criterion:** File exists with approximately 280+ lines.
**Weight:** Critical

---

### T04 — Local publish produces valid artifacts

```bash
python3.11 -m organic_market_agent run_publisher --output-dir output/public
```

Verify output:
```bash
# Body fragment uses new class system
grep -c 'class="sfagent"' output/public/public_report_body.html
# Expected: 1

# No old class name
grep -c 'sfagent-market-report' output/public/public_report_body.html
# Expected: 0

# M8 items present
grep -c 'data-tooltip' output/public/public_report_body.html
# Expected: 6

grep -c 'sfa-cta-banner' output/public/public_report_body.html
# Expected: 1

grep -c 'sfa-privacy-block' output/public/public_report_body.html
# Expected: 1

grep -c 'sfa-bridge-link' output/public/public_report_body.html
# Expected: 1

grep -c 'table-framing' output/public/public_report_body.html
# Expected: >= 2 (CSS rule + HTML element)

grep -c 'border-inline-start' output/public/public_report_body.html
# Expected: >= 1
```

**Weight:** Critical

---

## Live Site Tests (MCP Browser Required)

### T05 — External CSS loaded in `<head>`

```bash
curl -s "https://www.nimrod.bio/SmallFarmsAgent/" | grep 'sfagent-base-css'
```

**Pass criterion:** `<link>` tag present with `id='sfagent-base-css'` and
`href` pointing to `flatsome-child/sfagent-base.css` with `ver=` parameter.
**Weight:** Critical

---

### T06 — WordPress page renders correctly

Navigate MCP browser to `https://nimrod.bio/SmallFarmsAgent/`. Take snapshot.

**Pass criterion:**
- Page title contains "Market Report"
- H1 "מדד מחירי חקלאות אורגנית" visible
- Disclaimer modal visible with "הבנתי, תודה" button
- Vision block text visible
- Table with product data visible
- Transparency block visible at bottom

**Weight:** Critical

---

### T07 — M8 Item 1: Tooltips

Navigate MCP browser. Use snapshot to confirm `data-tooltip` attributes on
header cells. If possible, hover/click on a header to verify tooltip appears.

**Pass criterion:**
- 6 statistical `<th>` elements have `data-tooltip` attribute
- Tooltip text is in Hebrew
- "מקורות" tooltip contains privacy-aware text: "ללא חשיפה של חווה ספציפית"

**Weight:** High

---

### T08 — M8 Item 2: CTA Banner

Inspect live page for `.sfa-cta-banner` element.

```bash
curl -s "https://www.nimrod.bio/SmallFarmsAgent/" | grep -A2 'sfa-cta-banner'
```

**Pass criterion:**
- Banner appears between table and transparency block
- Text: "יש לך נתונים מדויקים יותר? עזור לשפר את המדד — זה משרת את כל הקהילה."
- WhatsApp link: `wa.me/972547776770` with pre-filled message
- Button text: "שלח בוואטסאפ"

**Weight:** High

---

### T09 — M8 Item 3: Visual Hierarchy

Inspect live page CSS for price cells.

```bash
curl -s "https://www.nimrod.bio/SmallFarmsAgent/" | grep 'border-inline-start' | head -3
```

**Pass criterion:**
- Average price cells have `border-inline-start: 3px solid var(--sfa-green-light)`
- `price-main` styled with `font-size: 1.15rem; font-weight: 800`
- `price-secondary` styled with `font-size: 0.8rem; color: #9ca3af`

**Weight:** Medium

---

### T10 — M8 Item 4: Privacy Block

```bash
curl -s "https://www.nimrod.bio/SmallFarmsAgent/" | grep -A5 'sfa-privacy-block'
```

**Pass criterion:**
- Lock icon (🔒) visible
- Three bullet points present:
  1. "המערכת מציגה נתונים מצרפיים בלבד."
  2. "אין חשיפה של מחירים ברמת חווה בודדת."
  3. "לא ניתן לזהות מגדל ספציפי."
- Located inside the transparency block (sfa-card--accent)

**Weight:** High

---

### T11 — M8 Item 5: Transparency Bridge

```bash
curl -s "https://www.nimrod.bio/SmallFarmsAgent/" | grep -E '(sfa-bridge-link|sfa-bridge-target|sfagent-dq-box)'
```

**Pass criterion:**
- Bridge link appears above the table: "איך הנתונים נוצרים?"
- Link points to `#sfagent-dq-box` anchor
- Transparency block has `id="sfagent-dq-box"`
- Bridge target text inside dq-box: "הטבלה מעל מבוססת על תהליך זה:"

**Weight:** Medium

---

### T12 — M8 Item 6: Table Framing

```bash
curl -s "https://www.nimrod.bio/SmallFarmsAgent/" | grep 'table-framing'
```

**Pass criterion:**
- H2 element with class `table-framing` appears above the table
- Text: "מדד מחירים מבוסס נתונים אמיתיים מהשטח"

**Weight:** Medium

---

### T13 — Dismiss disclaimer modal (MCP interactive)

Navigate MCP browser. Click "הבנתי, תודה" button. Take snapshot.

**Pass criterion:**
- Modal disappears after click
- Page content (table, CTA, transparency) remains visible
- No JavaScript errors in console

**Weight:** High

---

### T14 — WhatsApp CTA link (MCP interactive)

Inspect the CTA button link via MCP browser.

**Pass criterion:**
- Link href contains `wa.me/972547776770`
- Link href contains pre-filled message text

**Weight:** Medium

---

## Gate Pass Criteria

| # | Criterion | Weight |
|---|-----------|--------|
| 1 | Full pytest suite passes (T01) | Critical |
| 2 | Publisher artifact tests pass with new class names (T02) | Critical |
| 3 | sfagent-base.css exists in repo (T03) | Critical |
| 4 | Local publish produces valid M8 artifacts (T04) | Critical |
| 5 | External CSS loaded in `<head>` on live site (T05) | Critical |
| 6 | WordPress page renders correctly with all elements (T06) | Critical |
| 7 | All 6 M8 feature items verifiable on live page (T07-T12) | High |
| 8 | Interactive tests pass — modal dismiss, CTA link (T13-T14) | High |

**Gate G8 PASS** requires all Critical criteria met. High criteria failures
require documented remediation plan. Medium criteria failures are logged as
known issues.

---

## Reporting

File your gate report at:
`_COMMUNICATION/TEAM_50/reports/2026-04-02_GATE_G8_REPORT_TEAM50.md`

Use the canonical template:
`_COMMUNICATION/TEMPLATES/QA_FINDINGS_REPORT.md`

---

*Issued by: Team 100 (Architecture)*
*Date: 2026-04-02*
