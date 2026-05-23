---
id: DECISION_SFA-S003-P003_DEDICATED_SFA_SUBDOMAIN_v1.0.0
type: DECISION_RECORD
gate: program_opening
from: team_00 (Principal)
recorded_by: team_100 (smallfarmsagents)
date: 2026-05-23
related_program: SFA-S003-P003 (Delivery Infrastructure Migration)
status: APPROVED
authority: team_00 (Principal — single human authority)
next_step: "team_00 executes WP-1 uPress checklist; team_100 packages results into WP-2 LOD400 spec when WP-1 returns."
handoff_to: team_00
handoff_context_pointer: _aos/work_packages/S003/SFA-S003-P003-WP-1/LOD400_spec.md
---

# Decision Record — SFA-S003-P003 Architecture: Dedicated SFA Subdomain (no WordPress)

## §1 The decision

**APPROVED 2026-05-23**: migrate SFA delivery off WordPress shortcode injection on `www.nimrod.bio` and onto a **dedicated SFA subdomain `sfa.nimrod.bio`** hosted on uPress, running **custom lightweight PHP (Slim Framework) + MySQL**, with **no WordPress install** on the new site.

## §2 Trigger (the converging signals)

1. **The bug of 2026-05-23**: the live WP page `/smallfarmsagent/` shows stale 1-product data with placeholder date 2099-08-12. Root cause: uPress nginx firewall returns HTTP 403 to any request with `WordPress/*` in the User-Agent header — even for the site's own static endpoints. The mu-plugin's `wp_remote_get` therefore fails to fetch fresh content from `/smallfarmsagents/market/sfagent-public-report-body.html` and (apparently) returns a stale fallback rather than the canonical `<p style="color:red;">` error message.
2. **Recognition that the WP shortcode model is a structural dead-end** for our trajectory. Every component of friction we've fought (uPress FTPS port-21 block, uPress UA filter, Gutenberg `wp:html` vs `wp:shortcode` block confusion, mu-plugin transient cache, WP page editor save reliability, ezcache, Cloudflare cache, deprecated `wp-views` plugin warnings, stale WP pages from April 2026 that never got updated) is coupling cost. We don't use WP features (no posts, no comments, no Gutenberg, no theme/Customizer, no WooCommerce). We're paying full WP overhead for a "static file serving" use case.
3. **S004 trajectory** (calculator + community + per-user state) demands a real application surface — not a baked HTML fragment posted into a WP page editor. Without migrating now, S004 work would compound the friction.

## §3 The architecture (binding for P003)

```
End user
  │
  ▼
sfa.nimrod.bio (uPress shared hosting, Cloudflare DNS+proxy)
  ├─ Slim Framework 4 PHP app (~5MB, micro-framework)
  ├─ MySQL DB (uPress-provided)
  ├─ Static assets served by nginx (CSS/JS/fonts, edge-cached by CF)
  ├─ Routes:
  │    GET  /crop-book/, /crop-book/<id>     — server-rendered HTML
  │    GET  /market/, /market/<id>           — server-rendered HTML
  │    GET  /api/v1/crops, /api/v1/products  — JSON
  │    POST /api/v1/ingest                   — waldhomeserver push (HMAC auth)
  └─ NO WordPress, NO shortcodes, NO plugins, NO theme

waldhomeserver (private, backend only)
  ├─ PostgreSQL (canonical DB — unchanged)
  ├─ Scrapers, agents, reconciler, AOS infra — unchanged
  └─ Publisher (Python) — push to sfa.nimrod.bio/api/v1/ingest (replaces wp_upload.py path)
```

## §4 Constraints honored

| Constraint | Honored how |
|------------|-------------|
| waldhomeserver = backend only (not strong enough for end users) | uPress is the ONLY public-facing tier. waldhomeserver only does outbound HTTPS pushes. |
| Same FTP credentials as existing site | uPress subdomain hosting uses same account → same FTP. ZERO re-provisioning of upload tooling. |
| Cloudflare integration | Subdomain DNS via existing CF zone. Edge caching for static assets. Pass-through for dynamic. |
| Need a DB on user-facing tier | MySQL on uPress (standard offering). Schema mirrors Postgres on waldhomeserver. |
| Easy to update (dev velocity) | FTP push for code; HTTPS push for data. No WP admin, no Gutenberg, no cache layers to fight. |
| Portable to another host | Standard PHP + MySQL = LAMP universal. Migration = file copy + mysqldump. No proprietary lockin. |
| uPress shared hosting limits | Custom PHP + MySQL is exactly what shared LAMP hosts support best. No need for docker/services/shell. |

## §5 Stack canonized

| Layer | Choice | Rationale |
|-------|--------|-----------|
| PHP framework | **Slim 4** (micro) | ~5MB, just routing + middleware. Trivially swappable to vanilla PHP. |
| DB access | **PDO** | PHP-native, supported everywhere, no ORM overhead. |
| Migrations | Numbered SQL files (`001_init.sql`, etc.) + tiny PHP runner | Standard, portable, auditable. No Phinx/Doctrine. |
| Server-side templates | Plain PHP includes (or Plates if XSS-protection helper needed) | Minimal, native. No Twig overhead. |
| Frontend | Vanilla HTML/CSS/JS (continues current crop_book SPA approach) | No build step, no framework lockin, fast. |
| Auth (later) | Small JWT helper (~50 lines PHP) | When needed. Not blocking for v1. |

## §6 What changes vs current state

| Component | Today | After P003 cutover |
|-----------|-------|--------------------|
| User browses to market index | `www.nimrod.bio/smallfarmsagent/` → mu-plugin → stale fallback | `sfa.nimrod.bio/market/` → MySQL → fresh server-rendered HTML |
| User browses to crop book | `www.nimrod.bio/crop-book/` → mu-plugin → "בטעינה" placeholder | `sfa.nimrod.bio/crop-book/` → MySQL → fresh data |
| Publisher daily push | `wp_upload.py` → WP REST media library / static endpoint upload | `sfa_ingest_push.py` → HTTPS POST to `/api/v1/ingest` |
| Code changes | Edit Python publisher + WP page editor + clear caches + pray | git commit + FTP push + done |
| New WPs (calculator, community) | Build on broken substrate | Build on dedicated stable app |

## §7 What does NOT change

- waldhomeserver role (backend, scrapers, Postgres, agents, AOS infra)
- Iron Rules (#1 cross-engine, #4 single roadmap writer, #5 team_190 owns L-GATE_V, #6 artifact comms, #7 ADR034, etc.)
- F-LV-01 §2 unified-end-state invariants — apply to P003 closure too (validate before merging to main)
- F-LV-01 Hybrid `prod_deploy_authority` field on dispatches
- "No shortcuts, no skips, no patches" test integrity directive
- KNOWN_DEBT.md refresh obligation at P-program closure
- `www.nimrod.bio` continues as marketing/landing/auth-eventual site (separate concerns)

## §8 What WP-A and WP-B (P002) inherit

| WP | Adjustment |
|----|------------|
| **WP-A (Data Enrichment, team_110)** | Architecture spec must account for two-tier persistence: Postgres on waldhomeserver (canonical, all writes here) + MySQL on uPress (read-only mirror, fed via ingest API). Reconciler logic stays Postgres-side. team_100 will update WP-A HANDOFF_CONTEXT in this commit. |
| **WP-B (UX/UI Overhaul, team_35)** | Design book (LOD300) remains canonical — RTL Hebrew, mobile-first, system fonts. **Implementation target changes**: not WordPress shortcode + child theme, but custom PHP+HTML+JS routes on sfa.nimrod.bio. team_100 will update WP-B HANDOFF_PACKAGE in this commit. Design book deliverable is unchanged. |

## §9 The bug of 2026-05-23 → SUPERSEDED

The `/smallfarmsagent/` baked-HTML + UA-filter-fallback bug discovered 2026-05-23 will **not be fixed**. It will be SUPERSEDED at P003 cutover when:
- `sfa.nimrod.bio/market/` goes live
- `www.nimrod.bio/smallfarmsagent/` → 301 redirect to subdomain
- Old mu-plugin removed

This decision saves the ~2-4 hours of mu-plugin surgery + uPress firewall investigation we would otherwise spend, in favor of investing that time directly into the migration that resolves the class-of-problem permanently.

## §10 Migration plan

| WP | Scope | Effort | Status |
|----|-------|--------|--------|
| WP-1 | uPress provisioning + Cloudflare DNS | SMALL (~0.5d + waiting) | ELIGIBLE — team_00 self-executes |
| WP-2 | Slim PHP skeleton + DB schema + ingest endpoint | NORMAL (~2-3d) | BLOCKED on WP-1 |
| WP-3 | User-facing routes (crop-book + market) | NORMAL (~2-3d, leverages WP-B design) | BLOCKED on WP-2 |
| WP-4 | Publisher migration to ingest API | SMALL (~1-2d) | BLOCKED on WP-2 |
| WP-5 (optional, after WP-3+4) | 301 redirects + mu-plugin cleanup | TRIVIAL (~1h) | DEFERRED — open post-WP-3 |

**Total: ~1.5-2 weeks focused work.** Continuous delivery — www.nimrod.bio stays operational (and broken-as-today) until subdomain is fully live. Then atomic cutover via 301.

## §11 Open items / blocking team_00 confirmation

These are answered by team_00's uPress checklist (WP-1 LOD400 spec):
- Subdomain on existing plan? (or new plan/cost?)
- MySQL DB on subdomain? (or separate billing?)
- PHP 8.x available?
- FTP credentials work for subdomain?
- mod_rewrite for clean URLs?
- HTTPS / Let's Encrypt automatic for subdomain?
- Bandwidth / file-size / execution-time limits?
- Cloudflare-to-uPress origin pull works as it does for www?

## §12 Approval

team_00 verbal approval ("go") in-session 2026-05-23. team_100 records this decision artifact + opens P003 with 4 WPs.

---

*Decision recorded 2026-05-23 by team_100 (smallfarmsagents) on behalf of team_00 (Principal).*
*Branch: `claude/gallant-elbakyan-727a60` · Commit: pending.*
