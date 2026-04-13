# Famely Neusletter + nimrod.bio — executive synthesis and validation appendix

**Date:** 2026-04-11  
**Author:** Team 10 (validation run from SmallFarmsAgents workspace)  
**Scope:** Cross-infrastructure read-only checks. **Famely Neusletter** is not versioned in this repository; see [`documentation/external-references/CROSS_PROJECT_BOUNDARIES.md`](../../../documentation/external-references/CROSS_PROJECT_BOUNDARIES.md).

---

## Source corpus (Team 61 handoff)

Canonical paths on Mac (read for this synthesis):

| File | Role |
|------|------|
| `~/Documents/_agent_comm/inbox/MSG-20260410-009-RESPONSE.md` | `.htaccess` routing: `/agents/` → **403** (not WP-swallowed **404**); newsletter path **200**. |
| `~/Documents/_agent_comm/inbox/MSG-20260410-010-RESPONSE.md` | Pilot **v3.0.0** E2E **SUCCESS**; validation table; **DISTRIBUTED**; weekly cron Fri 09:00 build / 12:00 send Asia/Jerusalem; non-blocking residual issues. |
| `~/Documents/_agent_comm/inbox/MSG-20260410-004-REPORT.md` | Earlier snapshot (**05:30 UTC**). Use for TikTrack/AOS server map; **supersede** for Famely/SFA where **009/010** contradict (emails, cron, distribution). |

**MSG-011 (SFA operational RFI):** `MSG-20260410-011.md` exists in `~/Documents/_agent_comm/outbox/` only. **No** `MSG-*-011-RESPONSE` in `~/Documents/_agent_comm/inbox/` at validation time — treat deep SFA ops report as **pending**.

---

## Executive summary

1. **Routing:** Team 61’s **009** claim — WordPress no longer intercepts `/agents/*` — **confirmed** on 2026-04-11: `/agents/` returns **403**, dated newsletter HTML returns **200**.
2. **Pilot narrative (010):** Build **v3.0.0** reported successful distribution, real Hebrew opener/closer, weather, structure checks, emails to five recipients, FTP upload OK, weekly cron enabled.
3. **Residual quality risk before a “perfect” edition:** **010** lists RSS lanes with **0 items**, **2** outbound links failing automated check (**403** / bot-blocking), character PNGs missing (emoji/CSS fallback), placeholder-class hits (expected per 010).
4. **Reconciliation with 004:** Close stale Famely items that **010** already resolves (email distribution, cron, counter/DISTRIBUTED narrative). **004** SFA `/runs` Jinja issue — **superseded** by fixes in this repo; confirm deployed revision on server separately if needed.

---

## Open tasks (prioritized)

**A — Content / QA**

1. **Article URLs:** Live HTML fetched 2026-04-11 shows **article `href`s under `https://example.com/...`** (path stubs). This **conflicts** with **010**’s “No example.com: ✅ 0” — either the published artifact differs from the build **010** validated, or the checker definition changed. **Action:** Replace stubs with real canonical URLs in the Famely builder/config, or document intentional slug routing if a redirect layer is added later.
2. **Links flagged “broken” in 010 (403):** Decide replace vs keep vs footnote (“site blocks automated requests”).
3. **Feeds returning 0 items** (per **010** — e.g. Cirque / Dance Magazine / Aerial Expo): fix source URLs or deactivate in config.
4. **Character assets:** PNGs vs emoji fallback — align with family-facing polish expectations.

**B — Technical hygiene**

5. Reconcile **004** action items against **009/010** so roadmap items are not duplicated (emails, FTP MKD, cron, distribution status).

**C — Pending Team 61 RFI**

6. **MSG-011:** Await **`MSG-*-011-RESPONSE`** in inbox before treating SFA deep-dive ops as complete.

---

## Validation appendix — live HTTP (2026-04-11)

**Method:** `curl` GET; link check with `curl -L` and browser-like `User-Agent`. Artifact saved locally as `/tmp/neusletter-2026-04-10.html` during the run.

| Check | Result | Evidence / notes |
|-------|--------|------------------|
| `GET https://www.nimrod.bio/agents/newsletter/2026-04-10/index.html` | **PASS** | HTTP **200**; body **37,894** bytes (differs from **010**’s logged 41,780 — possible CDN/compression or artifact update). |
| `GET https://www.nimrod.bio/agents/` | **PASS** (per **009** intent) | HTTP **403** — not **404** / WP intercept. |
| No `lorem ipsum` | **PASS** | 0 matches |
| No literal `TODO` / `MOCK` | **PASS** | 0 matches |
| No `example.com` in article links | **FAIL** | **32** occurrences of `example.com` in `href`s — distinct article URLs under `https://example.com/<slug>` (all return **404** when fetched as public HTTP). |
| Opener / weather / closer / puzzle / survey | **PASS** | Section markers present in HTML text |
| Google Fonts stylesheet | **PASS** | `https://fonts.googleapis.com/css2?family=Bangers&family=Patrick+Hand&display=swap` → HTTP **200** |
| Inline CSS | **N/A** | Styles embedded in `<style>`; no separate `.css` asset links in body |

**Outbound link sample (all `href="https://example.com/..."` in this snapshot):** HTTP **404** for each tested stub path (expected for non-existent paths on `example.com`).

---

## Conclusion

Infrastructure path and dated static HTML availability **match** Team 61 **009**. Content-link quality on the live **2026-04-10** HTML **does not** match **010**’s “zero example.com” validation — **treat as a content/config gap** to fix in the Famely pipeline before calling the edition “link-clean” for family readers.

---

*End of report.*
