# MSG — team_190 → team_100 — L-GATE_V R1 verdict

**Date:** 2026-06-02 · **WP:** SFA-S003-P004-WP-CB-UI-ALIGN · **Gate:** L-GATE_V · **Round:** 1  
**Live:** https://sfa.nimrod.bio · **deployed_sha:** `b72bcca`

**Result:** **FAIL** — ADR042 closure **blocked**

**Verdict:** `_COMMUNICATION/team_190/SFA-S003-P004/WP-CB-UI-ALIGN/WP-CB-UI-ALIGN_LGATE-V_VERDICT_v1.0.0.md`

**BLOCKER:** `/calc/export.pdf` → **404** on live (CSV 200 OK). Fix hosting/route; re-smoke PDF print view.

**MAJOR:** (1) Crop pages show raw enum/field keys (`direct_seed`, `yield_per_bed_m`, …) — AC-3/AC-6. (2) Calc dash crop `<select>` empty — cannot bind to real crop.

**PASS:** V1 computed `#f8fbf8`, V2 `.sh` site-wide, V6 routes 200, V7 mobile-nav + `sh__icon` `<a>` accepted.

**Visual summary:** book-entry **PASS**; crop surfaces **FAIL** (content); calc-dash **PARTIAL** (shell PASS, PDF FAIL).

→ Build fix + live re-QA + **L-GATE_V R2**.

---
*ADR043 notification.*
