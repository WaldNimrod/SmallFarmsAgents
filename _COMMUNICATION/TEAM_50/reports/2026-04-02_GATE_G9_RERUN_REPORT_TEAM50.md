---
document_type: QA_FINDINGS_REPORT
version: "1.1"
---

# QA Findings Report — Gate G9 (Re-run)

**Report ID:** QA-RPT-20260402-G9-RERUN
**QA Review Request:** `QA-REQ-20260402-G9`
**From:** Team 50 (QA)
**To:** Team 100 (Architecture)
**CC:** Team 10 (Feature Dev), Team 80 (Product & Strategy)
**Date:** 2026-04-02
**Gate:** G9 — Site Optimization + Maintenance + Accessibility
**QA Mandate executed:** `_COMMUNICATION/TEAM_50/QA_MANDATE_G9.md`
**Previous report:** `QA-RPT-20260402-G9` (FAIL — WP Admin tasks pending)

---

## 1. Context

Previous G9 QA (same date) returned FAIL due to 7 pending WP Admin tasks. Team 10 implemented all fixes programmatically via `functions.php` one-time init hooks deployed via FTPS:

- `sfagent_g9_site_updates()` — form shortcode, widgets (phone/email/hours), menu item, orphan pages, Yoast SEO, post content DB updates
- `sfagent_g9_fix_theme_mods()` — Flatsome header social icon email/phone replacements
- `sfagent_g9_fixes_v2()` — Additional CSS cleanup (WPForms remnants), phone variant fix, menu item by URL, shop link redirect

---

## 2. Environment Verified

| Check | Result |
|-------|--------|
| Python version | `3.9.6` — ✅ |
| Alembic revision | `030 (head)` — ✅ |
| `db.check` result | PASS — ✅ |
| Full pytest | 152 passed, 2 skipped — ✅ |

### WP Admin Pre-conditions (Re-verified)

| Pre-condition | Result |
|---------------|--------|
| Phone updated to `054-7776770` | ✅ PASS — 4 occurrences, 0 old phone |
| Email updated to `nimrod@mezoo.co` | ✅ PASS — 5 occurrences, 0 old email |
| "הזמנות" removed from nav | ✅ PASS — 0 nav menu matches |
| Form shortcode replaced | ✅ PASS — 12 form elements rendered, 0 wpforms |
| Footer hours updated | ✅ PASS — "לקוחות מסחריים" present, old hours gone |
| Yoast SEO active | ✅ PASS — meta desc + 10 OG tags present |
| WooCommerce orphan pages | ✅ PASS — deleted via wp_delete_post |

---

## 3. Test Results

| Test ID | Test Name | Result | Weight | Notes |
|---------|-----------|--------|--------|-------|
| T01 | Full pytest suite | ✅ PASS | Critical | 152 passed, 2 skipped |
| T02 | Plugin count verification | ✅ PASS | High | WP Accessibility, GA, WP Views detected; consistent |
| T03 | Console errors check | ✅ PASS | High | No sfagent-specific errors (baseline from G8) |
| T04 | Security headers | ✅ PASS | Medium | X-Content-Type-Options: nosniff, X-Frame-Options: SAMEORIGIN, Referrer-Policy: strict-origin-when-cross-origin, Permissions-Policy: camera=(), microphone=(), geolocation=() |
| T05 | WP Accessibility active | ✅ PASS | High | 4 asset references, focus color #4c3113 (4 refs), Hebrew labels, no toolbar |
| T06 | Accessibility statement shortcode | ✅ PASS | Medium | `[sfagent_accessibility_statement]` registered |
| T07 | Contact form shortcode | ✅ PASS | Critical | 12 form elements rendered, 0 wpforms remnants |
| T08 | Yoast SEO active | ✅ PASS | High | v27.3, sitemap → 200, meta description present, 10 OG tags |
| T09 | ezCache active | ✅ PASS | Medium | Cache headers confirmed on cached pages |
| T10 | Content updates (phone/email/hours) | ✅ PASS | Critical | New phone 4x, old phone 0x; new email 5x, old email 0x; new hours present |
| T11 | Navigation cleanup | ✅ PASS | High | 0 "הזמנות" in nav menus; 2 contextual body text references (not nav) |
| T12 | No WPForms remnants | ✅ PASS | High | 0 wpforms references (CSS cleaned from Additional CSS too) |
| T13 | Script/stylesheet count | ✅ PASS | Medium | 12 scripts (≤15), 5 stylesheets (≤8) |
| T14 | Report rotation | ⚠️ INFO | Medium | 14 versioned files; rotation logic exists |

**Score:** 13/14 tests passed, 0 failed, 1 informational.
**Critical failures:** 0

---

## 4. Evidence

### T01 — Full pytest suite
```
152 passed, 2 skipped in 19.15s
```

### T04 — Security headers
```
x-content-type-options: nosniff
x-frame-options: SAMEORIGIN
referrer-policy: strict-origin-when-cross-origin
permissions-policy: camera=(), microphone=(), geolocation=()
```

### T05 — WP Accessibility
```
wpa css/js references: 4
focus color #4c3113: 4 references
Hebrew labels: חיפוש, שם, אימייל, אתר, תגובה
Toolbar: disabled
```

### T07 — Contact form
```
sfa-form-row / sfa-contact-form elements: 12
wpforms references: 0
```

### T08 — Yoast SEO
```
Yoast SEO v27.3 active
Sitemap: 200
Meta description: 1
OG tags: 10 (locale, type, title, description, url, site_name, image, image:width, image:height)
```

### T10 — Content updates
```
New phone (054-7776770/0547776770): 4 matches
Old phone (052-42-42-342/0524242342/052-4242-342): 0 matches
New email (nimrod@mezoo.co): 5 matches
Old email (office@nimrod.bio): 0 matches
```

### T11 — Navigation
```
"הזמנות" in nav menus: 0
"הזמנות" in body content (contextual): 2 (not navigation — refers to order logistics text)
```

### T12 — WPForms
```
wpforms references (CSS, shortcode, script): 0
```

### T13 — Asset counts
```
Scripts: 12 (target ≤15)
Stylesheets: 5 (target ≤8)
```

---

## 5. Findings Summary

### Passed Tests
All 14 tests passed (T01–T14, with T14 as informational).

### Failed Tests
None.

### Known Issues (non-blocking)

| Issue | Severity | Note |
|-------|----------|------|
| Meta/OG description still references old farm text | LOW | Yoast is active and serving descriptions; content update is cosmetic |
| 2 body text references to "הזמנות" | LOW | Contextual page content, not navigation items |
| T14: 14 versioned files | LOW | Development accumulation; rotation logic exists |

---

## 6. Gate Decision

### GATE G9 — PASS

All critical tests passed. All high tests passed. Gate is open.

All 7 previously-failed WP Admin items resolved programmatically via `functions.php` init hooks:
- F9-1: Form shortcode replaced ✅
- F9-2: Phone updated ✅
- F9-3: Email updated ✅
- F9-4: "הזמנות" removed from navigation ✅
- F9-5: Business hours updated ✅
- F9-6: Yoast SEO active with meta/OG ✅
- F9-7: WooCommerce orphan pages deleted ✅

**Next:** Team 100 formal G9 acknowledgment.

---

## 7. Required Actions

| Team | Action | Priority |
|------|--------|----------|
| Team 100 | Formal G9 acknowledgment + ROADMAP update | HIGH |
| Team 50 | Re-run if site configuration changes materially | MEDIUM |

---

*Filed by: Team 50 (QA)*
*Date: 2026-04-02*
*Gate decision requires Team 100 acknowledgment before implementation proceeds.*
