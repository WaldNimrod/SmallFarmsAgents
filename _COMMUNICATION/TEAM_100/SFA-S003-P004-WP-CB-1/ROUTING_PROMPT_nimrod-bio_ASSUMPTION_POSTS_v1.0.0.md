# CROSS-DOMAIN ROUTING PROMPT — SFA → nimrod-bio — team_100 — v1.0.0

**Date:** 2026-05-30
**From:** team_100 (SmallFarmsAgents spoke)
**To:** team_100 / nimrod-bio spoke (`/Users/nimrod/Documents/nimrod-bio/`, domain `wordpress`)
**Routed by:** team_00 (Nimrod) — cross-domain; SFA session does not write to nimrod-bio
**Subject:** Create 2 placeholder blog posts for Crop Book `AssumptionField` "read more" links
**for_hub:** true
**target_domain:** nimrod-bio

---

## Why

The SFA Crop Book v1 (`SFA-S003-P004-WP-CB-1`) introduces an **`AssumptionField`** UI component: a planning default the user can override, paired with an explainer and a **"read more →" link to a full nimrod.bio blog post**. Two AssumptionFields must ship at launch with a live post link:
1. **germination_rate** (default 90%)
2. **bed_width** (default 80 cm)

These posts **do not exist yet**. We need them created **with placeholder content** now, so SFA can wire the final canonical URLs into the calculator UI immediately and avoid a later rewrite when the site moves from its temporary dev address to the main domain.

---

## The prompt to run (in the nimrod-bio spoke)

> You are team_100 in the **nimrod-bio** WordPress spoke. Create **two new blog posts** (Hebrew, RTL — site language) with **placeholder body content** (a heading + 2–3 short paragraphs of lorem-style placeholder text + a "תוכן מלא בקרוב" note). These are link targets for an external app; real content comes later. Requirements:
>
> **Post 1 — Seed germination & seed aging**
> - Working title (HE): *"אחוז נביטה ולמה זרעים מתיישנים — איך לחשב כמה זרעים לקנות"*
> - Proposed stable slug: `seed-germination-rate`
> - Theme (for the eventual real content): what germination rate means, why 90% is a sensible default, how seeds lose viability with age, how to test germination, when to raise the over-sow factor.
>
> **Post 2 — Why 80 cm garden beds**
> - Working title (HE): *"למה ערוגה ברוחב 80 ס״מ — התרגום שלנו לסטנדרט של JM Fortier"*
> - Proposed stable slug: `garden-bed-width-80cm`
> - Theme: why we standardize on **80 cm** bed width (our deliberate translation of JM Fortier's 30″, not 75 cm), and what it means for plant spacing/population calculations.
>
> **Permalink requirement (important — temporary→main domain move):**
> The site is currently served from the temporary dev address `https://nimrod-bio-2026.s887.upress.link` and will move to the main domain `https://nimrod.bio` soon. Create each post so its **slug is fixed now** and its **final canonical URL** will be:
> - `https://nimrod.bio/seed-germination-rate/`
> - `https://nimrod.bio/garden-bed-width-80cm/`
> (Adjust the path prefix only if the site's permalink structure requires it — e.g. `/blog/<slug>/` — but keep the slug stable across the domain move.)
>
> **Return to the requester:**
> 1. The **final canonical URL** of each post (the `nimrod.bio/...` form we should hard-code).
> 2. The **current working URL** on the temp dev address (so we can preview before the move).
> 3. Confirmation that the slug is permanent and will survive the temp→main domain migration (no auto-redirect/slug change).
> 4. Post IDs (for reference).

---

## What SFA does with the result

SFA sets, in `organic_market_agent/crop_book/assumptions.py` (`ASSUMPTIONS` registry, LOD400 §4):
- `germination_rate.post_url = "https://nimrod.bio/seed-germination-rate/"`
- `bed_width.post_url = "https://nimrod.bio/garden-bed-width-80cm/"`

We wire the **final canonical (`nimrod.bio`) URLs**, not the temp dev URLs — so the links are correct the moment the site moves. Until the move, the posts are reachable via the returned temp working URL for preview/QA.

---

*Hand this to the nimrod-bio spoke (separate session). Return the URLs to SFA `_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-1/`.*
