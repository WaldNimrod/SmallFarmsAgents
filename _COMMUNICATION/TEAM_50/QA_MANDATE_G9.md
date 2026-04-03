---
document_type: QA_MANDATE
version: "1.0"
---

# QA Mandate — Gate G9

**Mandate ID:** `QA-MANDATE-G9`
**From:** Team 100 (Architecture)
**To:** Team 50 (QA)
**CC:** Team 10 (Feature Dev), Team 80 (Product & Strategy)
**Date:** 2026-04-02
**Milestone:** M9 — Site Optimization + Maintenance + Accessibility
**Gate:** G9

---

## Pre-conditions (verify before starting)

```bash
# 1. Alembic at 030
alembic current
# Expected: 030 (head)

# 2. DB healthy
python3 -m organic_market_agent.db.check
# Expected: RESULT: PASS

# 3. Full test suite
python3 -m pytest tests/ -q
# Expected: 152+ passed, 0 failed
```

### WP Admin Pre-conditions (Nimrod must complete before QA)

The following must be verified on the live site before executing tests:

- [ ] Phone number updated to `054-7776770` (not `052-42-42-342` or `0524242342`)
- [ ] Email updated to `nimrod@mezoo.co` (not `office@nimrod.bio`)
- [ ] "הזמנות" (Orders) removed from navigation menu
- [ ] `[wpforms id="90050"]` replaced with `[sfagent_contact_form]` on homepage
- [ ] Footer business hours updated ("הגינה פועלת כיום מול לקוחות מסחריים בלבד ובהזמנה מראש")
- [ ] Yoast SEO meta description and OG tags updated
- [ ] WooCommerce orphan pages (`/shop`, `/cart`, `/checkout`, `/my-account`) deleted or redirected

**If any WP Admin pre-condition is NOT met, document as FAIL and halt gate.**

---

## Test Suite

### T01 — Full pytest suite

```bash
python3 -m pytest tests/ -q
```

**Pass criterion:** 0 failures. Document any skips with rationale.
**Weight:** Critical

---

### T02 — Plugin count verification

```bash
curl -s https://www.nimrod.bio/ | grep -o "plugins/[^/]*/" | sort -u | wc -l
```

**Pass criterion:** Active plugin references consistent with expected ~12 active plugins. No conflicts in browser console.
**Weight:** High

---

### T03 — Console errors check

Navigate to homepage and `/smallfarmsagent/` via MCP browser. Check `browser_console_messages`.

**Pass criterion:** 0 JavaScript errors from sfagent or site code. Third-party noise (Facebook SDK, theme) is documented but not blocking.
**Weight:** High

---

### T04 — Security headers

```bash
curl -sI https://www.nimrod.bio/ | grep -iE "x-content-type|x-frame|referrer-policy|permissions-policy"
```

**Pass criterion:** At least `X-Content-Type-Options` and `X-Frame-Options` present.
**Weight:** Medium

---

### T05 — WP Accessibility active

```bash
# Check for WP Accessibility CSS/JS on live page
curl -s https://www.nimrod.bio/ | grep -c "wp-accessibility"

# Check focus outline CSS
curl -s https://www.nimrod.bio/ | grep -o "outline.*4c3113"
```

Verify via MCP browser:
- Tab key produces visible focus outlines
- No accessibility toolbar/overlay visible

**Pass criterion:** WP Accessibility assets loading, focus CSS injected with `#4c3113`, no visible toolbar.
**Weight:** High

---

### T06 — Accessibility statement shortcode

Create a test page or verify shortcode output:

```bash
curl -s https://www.nimrod.bio/ | grep -c "sfagent-a11y-statement"
```

Or test locally by checking `functions.php` for the shortcode registration.

**Pass criterion:** `[sfagent_accessibility_statement]` shortcode registered and renders Hebrew accessibility statement with correct contact info.
**Weight:** Medium

---

### T07 — Contact form shortcode

```bash
curl -s https://www.nimrod.bio/ | grep -c "sfagent-contact-form"
```

**Pass criterion:** `[sfagent_contact_form]` renders as a functional form (not raw shortcode text). No `[wpforms` remnants.
**Weight:** Critical

---

### T08 — Yoast SEO active

```bash
# Sitemap accessible
curl -s -o /dev/null -w "%{http_code}" https://www.nimrod.bio/sitemap_index.xml

# Meta description present
curl -s https://www.nimrod.bio/ | grep -c 'name="description"'

# OG tags present
curl -s https://www.nimrod.bio/ | grep -c 'property="og:'
```

**Pass criterion:** Sitemap returns 200, meta description present, OG tags present.
**Weight:** High

---

### T09 — ezCache active

```bash
# Check for caching headers
curl -sI https://www.nimrod.bio/ | grep -iE "cache|x-cache|ezcache"
```

**Pass criterion:** Cache-related headers present indicating caching is active.
**Weight:** Medium

---

### T10 — Content updates on live site

```bash
# Phone number
curl -s https://www.nimrod.bio/ | grep -c "054-7776770"
curl -s https://www.nimrod.bio/ | grep -c "0547776770"

# Email
curl -s https://www.nimrod.bio/ | grep -c "nimrod@mezoo.co"

# Old values should NOT appear
curl -s https://www.nimrod.bio/ | grep -c "052-42-42-342"
curl -s https://www.nimrod.bio/ | grep -c "0524242342"
curl -s https://www.nimrod.bio/ | grep -c "office@nimrod.bio"
```

**Pass criterion:**
- New phone `054-7776770` or `0547776770` appears at least once
- New email `nimrod@mezoo.co` appears at least once
- Old phone `052-42-42-342` and `0524242342` appear 0 times
- Old email `office@nimrod.bio` appears 0 times
**Weight:** Critical

---

### T11 — Navigation menu cleanup

```bash
curl -s https://www.nimrod.bio/ | grep -c "הזמנות"
```

**Pass criterion:** "הזמנות" (Orders) appears 0 times in page HTML.
**Weight:** High

---

### T12 — No WPForms remnants

```bash
curl -s https://www.nimrod.bio/ | grep -c "wpforms"
curl -s https://www.nimrod.bio/ | grep -c '\[wpforms'
```

**Pass criterion:** 0 matches for `wpforms` in page source (no CSS, no shortcodes, no scripts).
**Weight:** High

---

### T13 — Script/stylesheet count

```bash
curl -s https://www.nimrod.bio/ | grep -oE '<script[^>]+src=' | wc -l
curl -s https://www.nimrod.bio/ | grep -oE "<link[^>]+stylesheet" | wc -l
```

**Pass criterion:** Reasonable counts (target: <=15 scripts, <=8 stylesheets). Document actual counts.
**Weight:** Medium

---

### T14 — Report rotation

```bash
ls -la output/public/public_report-*.json | wc -l
```

**Pass criterion:** Versioned file count managed by rotation logic. Document actual count.
**Weight:** Medium

---

## Gate Pass Criteria

| # | Criterion | Weight |
|---|-----------|--------|
| 1 | Full pytest suite passes (0 failures) — T01 | Critical |
| 2 | Contact form renders (no WPForms remnants) — T07, T12 | Critical |
| 3 | Content updates live (phone, email, hours) — T10 | Critical |
| 4 | WP Accessibility active with focus CSS — T05 | High |
| 5 | Yoast SEO active (sitemap, meta, OG) — T08 | High |
| 6 | Navigation cleaned ("הזמנות" removed) — T11 | High |
| 7 | Console errors minimized — T03 | High |
| 8 | Plugin count and cache active — T02, T09 | Medium |
| 9 | Security headers present — T04 | Medium |
| 10 | Accessibility statement shortcode — T06 | Medium |
| 11 | Script/stylesheet optimization — T13 | Medium |
| 12 | Report rotation — T14 | Medium |

**Gate G9 PASS** requires all Critical criteria met. High criteria failures require documented remediation plan. Medium criteria failures are logged as known issues.

---

## Reporting

File your gate report at: `_COMMUNICATION/TEAM_50/reports/2026-04-02_GATE_G9_REPORT_TEAM50.md`
Follow the canonical QA Findings Report template.
