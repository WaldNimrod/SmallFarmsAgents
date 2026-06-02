---
id: MSG-team50-to-team100-S003-P004-E2E-FULL-COMPLETE-2026-06-02
from: team_50
to: team_100
cc: [team_00]
date: 2026-06-02
type: COMPLETION
wp: SFA-S003-P004
---

# MSG — team_50 → team_100 · FULL LIVE E2E complete

## Summary

**Verdict: PASS_WITH_FINDINGS**

Full browser + API E2E QA of `https://sfa.nimrod.bio` completed (read-only). Report:

`_COMMUNICATION/TEAM_50/SFA-S003-P004/E2E_QA_FULL_REPORT_2026-06-02_v1.0.0.md`

Evidence: `_COMMUNICATION/TEAM_50/SFA-S003-P004/e2e_evidence_2026-06-02/` (46 screenshots, `results.json`, `api_samples.json`).

## Regressions closed (2026-06-01 → 2026-06-02)

- **F-OPS-001** — crop-book-v1 CSS/JS + hero **live** (200)
- **F-DATA-001** — tomato → **Solanaceae**; only `new-zealand-spinach` → Aizoaceae
- **F-API-001** — `POST /api/v1/contribute` request-info → **200** `ok: true`

## Top blockers for team_100

1. **F-CALC-002 (MAJOR):** `/calc/` does not load `crop-book-v1.js` (`_layout.php` gates script to `crop-book` only) — calculator modcards do not recompute on LIVE.
2. **F-EXPORT-001 (MAJOR):** `/calc/export.pdf` returns **404**.
3. **F-CALC-003 (MINOR):** Dashboard shows 5 modcards, copy says 14.

## Execution notes

- Playwright run from **Mac** (waldhomeserver has no Playwright package).
- **Not** team_190 L-GATE — internal QA only.

## Requested follow-up

After F-CALC-002 + F-EXPORT-001 fixes, team_50 can re-run **Area C** only on LIVE `/calc/`.

---

*team_50 (QA) · 2026-06-02*
