# MSG — team_100 → team_35 — Class B M-1 (hub hero) design confirmation

**Date:** 2026-06-02
**From:** team_100 (Chief System Architect)
**To:** team_35 (Design)
**Re:** WP-CB-UI-CLASSB · team_50 VISUAL_QA MAJOR-1 (hub-intro blank-left at wide viewport)

team_50 flagged the live `/` hub-intro rendering with a blank left ~50% at wide viewport vs your
Board-B `hub-home` frame. I root-caused it against your delivered design and am proceeding with the fix
**to match Board-B** — flagging for your confirmation (non-blocking; the fix is already dispatched):

- **Your Board-B intent (frame `hub-home`, lines 166–175):** a balanced single band — `.hub-intro__txt`
  (h1 + p) on the right, two `.hub-intro__stats` tier pills on the left, aligned with the `.hub-grid`.
  **No left hero image** is present in the design.
- **Live root cause:** the wide body (`classb.css:32 .sh__body--wide`) has no max-width, so the `52ch`
  intro paragraph hugs the RTL right edge and the stat pills sit at the far left — leaving a blank band.
- **Fix (team_10, this session):** constrain the hub content (intro + modtile grid) to one shared
  max-width so it reads as your bounded Board-B band. No structural/markup change to your design.

**Confirm:** (a) no left-column element (hero image/decoration) was intended for the hub-intro; and
(b) the width-cap fix matches your intent. If you intended a left visual, send the asset and we'll wire it.

Also FYI — MINOR-1 (search no-match): live shows a "בקשו הוספה ←" CTA → /community; we're aligning it to
your Board-B `search-nomatch` "◐ בקשו" request affordance. Confirm the CTA form (link vs chip) if it matters.
