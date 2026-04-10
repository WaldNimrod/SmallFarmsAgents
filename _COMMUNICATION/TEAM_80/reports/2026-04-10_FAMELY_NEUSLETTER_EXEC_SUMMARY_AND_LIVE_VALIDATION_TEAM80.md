# Famely Neusletter + nimrod.bio — Executive summary, live validation, open tasks

| Field | Value |
|-------|--------|
| **Date** | 2026-04-10 |
| **Team** | Team 80 (Product & Strategy) — synthesis for Nimrod |
| **Sources** | Team 61 inbox: `MSG-20260410-009-RESPONSE`, `MSG-20260410-010-RESPONSE`; earlier `MSG-20260410-004-REPORT`; live HTTP/HTML verification (this session) |

---

## 1. Executive summary

- **Routing / hosting:** Team 61 confirms **`.htaccess`** allows static content under **`/agents/`** without WordPress swallowing paths (**009**). Live check: **`https://www.nimrod.bio/agents/`** returns **HTTP 403** (expected “directory listing denied” style — **not** a WordPress 404).
- **Pilot narrative (010):** **v3.0.0** end-to-end run is reported **SUCCESSFUL** — build metrics, **FTP upload OK**, **emails to five family addresses**, **weekly cron** (Friday **09:00** build / **12:00** send, `Asia/Jerusalem`).
- **SFA RFI:** **`MSG-20260410-011`** (detailed SmallFarmsAgents operational report) has **no response file** in `~/Documents/_agent_comm/inbox/` as of this review — treat as **pending**.
- **Live HTML vs Team 61 automated checks — material gap:** The **published** edition at **`https://www.nimrod.bio/agents/newsletter/2026-04-10/index.html`** (verified **HTTP 200**, ~37.9KB) still contains **placeholder article URLs** on **`https://example.com/...`** (16 distinct slug paths; **32** substring hits) and visible copy **`[Mock response for history]`** in the “today in history” block. **This contradicts** **010**’s “No example.com: 0” / “No MOCK: 0” table for the artifact now online. **Conclusion:** the live file is **not** “publication-perfect” for family-facing link integrity; treat **010** validation as **deployment/pipeline** success, not **content URL** final QA.

---

## 2. Situation picture (merged)

| Layer | Status |
|-------|--------|
| **Infrastructure** | `/agents/` path reachable; newsletter HTML **200**. |
| **Build / distribute (server)** | **010:** Pilot **DISTRIBUTED**; cron enabled for weekly Friday builds. |
| **Content quality (live)** | **Issue:** Article **`href`s** use **`example.com`** slugs, not real source URLs. **Issue:** History section shows **mock** placeholder text in body. |
| **Earlier 004 report** | Use for **TikTrack/AOS** context; **Famely** and **SFA `/runs`** items are **partially superseded** by later fixes (**010**, git `2ec3f47`+ for SFA template). |

---

## 3. Open tasks (for a “perfect” next edition)

**Must-fix (before calling the public page “done”):**

1. **Replace `https://example.com/...` article links** with real canonical URLs from RSS curation (or hide “read more” until URLs exist).
2. **Remove or replace `[Mock response for history]`** with real “today in history” content (or remove the block).
3. **Confirm** discovery link checker distinguishes **HEAD 403** (bot block) vs **bad href** — current failure mode is **placeholder domain**, not remote 403.

**Should-fix (quality):**

4. **Character images:** **010** notes PNGs missing; live HTML exposes **characterplaceholder** / fallback — ship assets or accept explicit emoji-only branding.
5. **Feeds with 0 items** (**010**): Cirque du Soleil, Dance Magazine, Aerial Expo — fix or disable in source config.
6. **Reconcile validation script** with production HTML so CI does not green-light **example.com** in `href`.

**Process:**

7. **MSG-011 response** — follow up with Team 61 for SFA ops deep-dive when available.

---

## 4. Live validation appendix (2026-04-10)

**Method:** `curl` + downloaded HTML analysis; `fonts.googleapis.com` checked via fetch; external `example.com` probes from this environment returned **no HTTP status** (connection failure — likely sandbox); qualitative assessment relies on **href targets** and **visible text**.

| Check | Result | Notes |
|-------|--------|--------|
| `GET https://www.nimrod.bio/agents/newsletter/2026-04-10/index.html` | **PASS (200)** | `text/html`; `Last-Modified` present |
| `HEAD https://www.nimrod.bio/agents/` | **PASS (403)** | Matches **009** (“not 404”) |
| `lorem ipsum` in HTML | **PASS (0)** | — |
| `TODO` token in HTML | **PASS (0)** | — |
| `MOCK` token in HTML | **FAIL** | Visible: **`[Mock response for history]`** |
| `example.com` in `href` | **FAIL** | **16** unique `https://example.com/...` article URLs |
| Google Fonts CSS link | **PASS** | Stylesheet returns CSS (`fonts.googleapis.com/css2?...`) |
| Weather / puzzle / survey / closer | **PASS** | Heuristic: keywords present in HTML |
| Opener section | **UNCLEAR** | Regex heuristic did not match; content present in rendered text (see fetch) |

**Canonical URL (bookmark):**  
`https://www.nimrod.bio/agents/newsletter/2026-04-10/index.html`

---

## 5. Source file references (local machine)

| Document | Path |
|----------|------|
| Team 61 — `.htaccess` | `~/Documents/_agent_comm/inbox/MSG-20260410-009-RESPONSE.md` |
| Team 61 — pilot v3.0.0 | `~/Documents/_agent_comm/inbox/MSG-20260410-010-RESPONSE.md` |
| Team 61 — full server report (earlier) | `~/Documents/_agent_comm/inbox/MSG-20260410-004-REPORT.md` |
| SFA RFI (outbound, no reply yet) | `~/Documents/_agent_comm/outbox/MSG-20260410-011.md` |

---

*End of report.*
