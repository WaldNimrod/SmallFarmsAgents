---
id: SFA-S003-P004-WP-CB-UI-CLASSB-LOD100
wp: SFA-S003-P004-WP-CB-UI-CLASSB — v2 design for the hub/market/search/community/about/account surfaces
gate: L-GATE_E (BLOCKED on team_35)
status: BLOCKED — opened 2026-06-02
author: team_100
depends_on: SFA-S003-P004-WP-CB-UI-ALIGN
design_mandate: _COMMUNICATION/team_35/SFA-S003-P004-WP-CB-UI-CLASSB/DESIGN_MANDATE_team35_v2-surfaces_2026-06-02_v1.0.0.md
---

# LOD100 — WP-CB-UI-CLASSB (direction only; BLOCKED on team_35)

Holds the **Class B** surfaces from the WP-CB-UI-ALIGN split — the ones team_35 never designed in v2:
hub/home (`/`), market list+detail (`/market`, `/market/{slug}`), search (`/search`), community
(`/community`), about/tiers (`/about`), account (nav hook).

**Blocked** until team_35 delivers v2 templates per the DESIGN_REQUEST. team_00 rule: structure/style/
interface EXACT to team_35; a missing template is requested, never guessed.

On unblock: team_100 authors LOD400 (embedding the team_35 frames) → team_190 L-GATE_S → team_10 build
(reusing the `.sh` app-shell built in Class A) → team_50 **visual** QA (design-vs-live per screen) →
team_190 L-GATE_V (non-Claude, IR#1/#5) → ADR042 closure.

Not for execution now.
