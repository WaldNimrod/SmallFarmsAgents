---
document_type: MANDATE
version: "1.0"
---

# Mandate — M9 Completion Report Update & QA Review Request

**Mandate ID:** MANDATE-20260402-M9-COMPLETION
**From:** Team 100 (Architecture)
**To:** Team 10 (Feature Dev)
**Date:** 2026-04-02
**Priority:** HIGH
**Gate dependency:** Blocks G9
**Status:** ACTIVE

---

## 1. Context

Milestone M9 (Site Optimization + Maintenance + Accessibility) was declared complete by Team 10 on 2026-04-02 in the initial completion report. However, the following updates have since been implemented:

1. WP Accessibility plugin configured (focus outlines, Hebrew labels)
2. Accessibility statement shortcode created
3. Custom zero-plugin contact form (`[sfagent_contact_form]`) implemented
4. Yoast SEO activated (replacing AIOSEO)
5. ezCache configured (replacing WP Rocket)

Additionally, certain WP Admin tasks listed in the original completion report require verification on the live site to confirm they have been performed by Nimrod.

A new QA mandate (`QA_MANDATE_G9.md`) has been issued by Team 100. Team 10 must update the completion report and file a QA Review Request.

**Triggered by:** Gate closure initiative — G9 must be formally closed.
**Related documents:**
- `_COMMUNICATION/TEAM_50/QA_MANDATE_G9.md`
- `_COMMUNICATION/TEAM_10/reports/2026-04-02_M9_SITE_OPTIMIZATION_COMPLETE_TEAM10.md` (original)
- `_COMMUNICATION/TEAM_100/reports/2026-04-02_G8_ACKNOWLEDGMENT_TEAM100.md`
- `_COMMUNICATION/TEAM_100/reports/2026-04-02_G7_ACKNOWLEDGMENT_TEAM100.md`

---

## 2. Requirements

### Task 1 — Update M9 Completion Report

File an updated Completion Report (v2) per the canonical template covering all M9 deliverables including post-original-report additions.

The report must document:

1. **Plugin cleanup** — Contact Form 7 disabled, WPForms removed, unnecessary plugins identified
2. **SEO migration** — AIOSEO → Yoast SEO with data import
3. **Cache replacement** — WP Rocket → ezCache
4. **Zero-plugin contact form** — `[sfagent_contact_form]` shortcode in `functions.php`
5. **WP Accessibility** — configured with focus outlines (#4c3113), Hebrew form labels, no toolbar
6. **Accessibility statement** — `[sfagent_accessibility_statement]` shortcode
7. **CSS architecture** — 3-layer model (`sfagent-base.css` in child theme)
8. **Security** — htaccess hardening, spam comments treatment plan

**WP Admin tasks status** — Document which tasks were completed by Nimrod and which remain pending. Include live site verification evidence.

**Acceptance criterion:** Report filed at `_COMMUNICATION/TEAM_10/reports/2026-04-02_M9_COMPLETION_REPORT_TEAM10_v2.md`

---

### Task 2 — File G9 QA Review Request to Team 50

File a QA Review Request per the canonical template requesting Team 50 to execute `QA_MANDATE_G9.md`.

**Important:** Document in "Known Issues" section any WP Admin tasks that remain pending. These are blocking G9 if they are Critical-weight tests in the mandate.

**Acceptance criterion:** Request filed at `_COMMUNICATION/TEAM_50/reports/2026-04-02_G9_REVIEW_REQUEST_TEAM10.md`

---

## 3. Out of Scope

- M9-Content (content updates beyond critical contact info) — future milestone
- M10 (planning milestone) — not yet started
- Any new feature development
- Google Search Console submission (Nimrod's responsibility)

---

## 4. Verification Checklist

Run these before submitting:

```bash
python3 -m pytest tests/ -q
alembic current
python3 -m organic_market_agent.db.check

# Live site checks
curl -s https://www.nimrod.bio/ | grep -c "wp-accessibility"
curl -s -o /dev/null -w "%{http_code}" https://www.nimrod.bio/sitemap_index.xml
```

Expected results:
- [ ] pytest: 152+ passed, 0 failed
- [ ] Alembic: 030 (head)
- [ ] db.check: RESULT: PASS
- [ ] WP Accessibility loading on live site
- [ ] Yoast sitemap accessible (200)

---

## 5. Completion Report

When both tasks are complete, this mandate is considered fulfilled.

The M9 Completion Report v2 IS the deliverable of Task 1.
The G9 QA Review Request IS the deliverable of Task 2.

---

## 6. Escalation

If blocked:
1. File a report in `_COMMUNICATION/TEAM_10/reports/` with prefix `BLOCKED_`
2. State the exact blocking condition
3. Tag with `[USER ACTION REQUIRED]` if Nimrod must decide

---

*Issued by: Team 100 (Architecture)*
*Date: 2026-04-02*
*Authorized by: Team 100 (Architecture)*
