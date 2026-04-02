---
document_type: MANDATE
version: "1.0"
---

# Mandate — M9 Blog Post + Content Strategy

**Mandate ID:** MANDATE-20260402-M9-BLOG-POST
**From:** Team 100 (Architecture)
**To:** Team 80 (Product & Strategy)
**Date:** 2026-04-02
**Priority:** MEDIUM
**Gate dependency:** Blocks G9
**Status:** PLANNED — activates after G8

---

## 1. Context

M8 delivers UX improvements to the live public page. M9 builds on this with
content that drives organic traffic and begins community participation.

Team 80 originally proposed a blog post titled "Why my farm was not profitable"
which was approved in concept by Team 100 and Nimrod.

**Triggered by:** Team 80 handoff package `smallfarms_agent_handoff/06_blog_post.md`
**Related documents:**
- `_COMMUNICATION/TEAM_100/reports/2026-04-02_M8_M10_DETAILED_SPEC_TEAM100.md`
- `_COMMUNICATION/TEAM_80/smallfarms_agent_handoff/06_blog_post.md`
- `_COMMUNICATION/TEAM_80/smallfarms_agent_handoff/05_copy.md`

---

## 2. Requirements

### Task 1 — Obtain Briefing from Nimrod

Before writing, Team 80 must receive a briefing from Nimrod containing:
- Key talking points to include
- Topics or details to omit
- Preferred tone (personal, community-oriented, not corporate)
- Any specific anecdotes or examples to mention
- Link targets (SmallFarmsAgent page, WhatsApp contact)

**Acceptance criterion:** Briefing received and documented.

---

### Task 2 — Draft Blog Post in Hebrew

Write a Hebrew blog post with the following structure:
1. **The Reality** — farming experience, what worked, the community
2. **The Problem** — pricing opacity, hidden costs, no accessible tools
3. **The Shift** — from hands-on farming to building systems with AI
4. **The Solution** — shared pricing data, transparent tools, community-driven
5. **Closing** — invitation to participate, link to SmallFarmsAgent page

**Constraints:**
- Length: 800–1200 words
- Language: Hebrew
- Tone: personal, authentic, community voice — not corporate or sales-heavy
- Must reference the live pricing tool with a link
- Must include WhatsApp contact link
- Do NOT include full personal history — hint and give context, don't overshare

**Acceptance criterion:** Draft delivered as a markdown file in `_COMMUNICATION/TEAM_80/reports/`.

---

### Task 3 — SEO Recommendations

Provide a short SEO guidance document for the WordPress admin to configure:
- Recommended page title for the SmallFarmsAgent page
- Meta description (Hebrew, max 160 characters)
- Open Graph title and description
- Suggested blog post title and meta description
- Recommended internal linking strategy (blog ↔ tool page)

**Acceptance criterion:** SEO guidance document delivered in `_COMMUNICATION/TEAM_80/reports/`.

---

## 3. Out of Scope

- Publishing the blog post (Nimrod does this manually in WordPress)
- Code changes to the public template (Team 10 handles in M8)
- WordPress admin configuration (Nimrod or Team 10)
- Database changes
- Authentication or user roles

---

## 4. Verification Checklist

- [ ] Nimrod briefing received and documented
- [ ] Blog post draft in Hebrew, 800–1200 words
- [ ] SEO guidance document delivered
- [ ] Nimrod approves blog post content
- [ ] Blog post cross-references SmallFarmsAgent page

---

## 5. Completion Report

When all tasks are complete, file a **Completion Report** using:
`_COMMUNICATION/TEMPLATES/COMPLETION_REPORT.md`

Save at:
`_COMMUNICATION/TEAM_80/reports/2026-XX-XX_M9_BLOG_POST_COMPLETE_TEAM80.md`

---

## 6. Escalation

If blocked on Nimrod briefing:
1. File a report in `_COMMUNICATION/TEAM_80/reports/` with prefix `BLOCKED_`
2. Tag with `[USER ACTION REQUIRED]`

---

*Issued by: Team 100 (Architecture)*
*Date: 2026-04-02*
*Authorized by: Team 100 (Architecture)*
