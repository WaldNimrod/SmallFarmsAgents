---
document_type: ARCH_DECISION
version: "1.0"
---

# Architectural Decision — Content Strategy, Privacy Messaging, and Strategic Narrative
**Decision ID:** ARCH-20260405-CONTENT-STRATEGY-PRIVACY
**From:** Team 100 (Architecture)
**To:** Team 10, Team 80, Nimrod
**Date:** 2026-04-05
**Type:** CLARIFICATION

---

## 1. Context

Public-facing copy now needs to serve two different purposes that must not be mixed carelessly:
1. A policy / privacy layer that explains what public data is shown, what is hidden, and why.
2. A strategic / marketing layer that explains why the product exists and what larger mission it serves.

A review of the current content sources shows that these two layers are currently blurred. Legacy Team 80 copy describes a calculator product, while the implemented public surface is an aggregated price index. The current public page also mixes product explanation with broader consulting / future-services messaging.

**References:**
- `_COMMUNICATION/TEAM_80/smallfarms_agent_handoff/05_copy.md` — legacy copy source
- `_COMMUNICATION/TEAM_80/smallfarms_agent_handoff/06_blog_post.md` — legacy blog outline
- `organic_market_agent/publisher/templates/public_report_body.html` — current public page body
- `docs/PRIVACY_POLICY.md` — binding privacy policy
- `documentation/01-overview/PROJECT_VISION_AND_SYSTEM_MAP.md` — canonical product framing
- `_COMMUNICATION/TEAM_100/reports/2026-04-05_CONTENT_ARCHITECTURE_PAGE_AND_BLOG_TEAM100.md` — review basis

---

## 2. Findings

| Item | Finding | Severity |
|------|---------|----------|
| F1 | The public product is an aggregated index, not a calculator; legacy calculator wording is now inaccurate. | Critical |
| F2 | Privacy language must remain explicit and simple because privacy is not a side note; it is part of the product contract. | Critical |
| F3 | The page and the blog serve different jobs and should not carry the same message density. | High |
| F4 | The deeper narrative is not only “help the community”; the public product also acts as the visible wedge into a larger strategic objective. | High |
| F5 | If the strategic objective is not stated clearly, the page will drift into vague social-good messaging while the blog drifts into vague founder-story messaging. | High |

---

## 3. Decision

Team 100 formally separates the public content layer into two tracks.

### Track A — Policy / Privacy / Data Contract
This track explains:
- what the public page is
- what data is shown
- what data is intentionally not shown
- why aggregated presentation is required
- how freshness / source counts / limitations should be understood

This track must be:
- precise
- short
- repeatable across page, transparency block, and blog post
- fully aligned with `docs/PRIVACY_POLICY.md`

Canonical message requirements:
- aggregated data only
- no farm-level pricing exposure
- no identification of a specific grower / vendor / source
- data is informative, not a quote or recommendation

### Track B — Strategic / Marketing Narrative
This track explains:
- why Nimrod is investing in the system
- why this product exists now
- what larger direction it opens
- why this problem matters enough to build infrastructure around it

This track must not redefine the current product. It may frame the broader mission, but it must not claim features that the current page does not provide.

### Strategic Interpretation (Team 100 inference)
Team 100's current architectural reading is:

The system exists not only to help the community directly, but also to establish a credible public foundation for a broader farm-technology and AI-agent initiative.

The public index serves four strategic functions at once:
1. It solves a real, narrow, socially legitimate problem.
2. It proves execution credibility in a hard, real-world agricultural domain.
3. It builds trust and attention with the exact audience needed for future products.
4. It acts as the wedge product for a larger MyFarmAgents direction: operational tools, farm intelligence, and paid or bespoke systems later.

This interpretation is treated as the working narrative unless Nimrod corrects it.

### Content Role Split (Binding)
Public page:
- must primarily explain the current public index
- may include a short founder / mission note
- must not become the main place for broad future-vision selling

Blog post:
- may carry the founder narrative and the broader strategic intent
- should connect the current index to the larger mission
- should explicitly distinguish current capability from future direction

### Immediate Privacy Update Plan
Team 100 requires a full text pass on all public-facing privacy-related content with the following order:
1. public-page disclaimer / modal
2. transparency block privacy paragraph
3. tooltip wording related to sources
4. page intro lines that mention data origin
5. blog post privacy section

Every one of these must use one shared canonical wording set.

---

## 4. Mandates Issued

| Mandate | Team | File | Priority |
|---------|------|------|----------|
| Privacy and content wording alignment plan | Team 100 / Nimrod | `_COMMUNICATION/TEAM_100/reports/2026-04-05_CONTENT_ARCHITECTURE_PAGE_AND_BLOG_TEAM100.md` | HIGH |

If Team 10 implementation work is requested next, Team 100 should issue a separate `MANDATE.md` file to Team 10 with exact copy replacements and insertion points.

---

## 5. Next Steps

| Team | Action | When |
|------|--------|------|
| Team 100 | Produce canonical wording pack for privacy / transparency / product-definition text | Immediately |
| Team 100 | Produce message map for page vs blog roles | Immediately |
| Nimrod | Confirm or correct Team 100's strategic interpretation of the system's deeper purpose | Immediately |
| Team 10 | Wait for exact copy mandate before replacing public text | After Team 100 wording pack |
| Team 80 | Treat calculator-oriented legacy copy as superseded for this product surface | Immediately |

---

*Issued by: Team 100 (Architecture)*
*Date: 2026-04-05*
*This decision is binding on all teams unless overridden by Nimrod.*
