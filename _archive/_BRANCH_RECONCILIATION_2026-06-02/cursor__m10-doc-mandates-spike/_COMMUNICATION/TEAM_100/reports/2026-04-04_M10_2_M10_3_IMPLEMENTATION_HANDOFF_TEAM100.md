---
document_type: ARCHITECTURE_HANDOFF
version: "1.0"
---

# M10.2 + M10.3 — Implementation handoff to Team 100

**Report ID:** RPT-20260404-M10-HANDOFF-T100  
**From:** Team 10 (Feature Dev)  
**To:** Team 100 (Architecture)  
**CC:** Team 50 (QA), Nimrod (project lead)  
**Date:** 2026-04-04  
**Mandates:** M10.2 dictionary optimization; M10.3 static parsers; **MANDATE-20260404-M10-CORRECTIONS**

---

## 1. Executive summary

Team 10 delivered **Alembic data migrations** (032–035 M10.2; 036–039 M10.3 + dictionary follow-up), **four parser modules** (Nizat, Rexail, Eranorgani, Tamari) with **Rexail** extended for `storeProductsByCategoryId`, **DB activation** of SRC025–SRC028, and **dictionary** scope-skip/alias rows so active **community** sources reach **100%** normalized vs. (normalized + unresolvable) in the verification SQL.

**Publish:** `catalog_renormalize` + `run_publisher **--upload**` executed successfully (**8** FTPS artifacts). **`public_report.json`** contains **83** products (satisfies ≥70 M10.2 and ≥80 M10.3). **Live:** `https://www.nimrod.bio/smallfarmsagent/` returned **HTTP 200** immediately after upload.

---

## 2. Team 50 QA (agent mandate)

| Artifact | Path |
|----------|------|
| Canonical QA mandate (agent-executable) | `_COMMUNICATION/TEAM_50/QA_MANDATE_M10_G10_TEAM50.md` |
| QA Findings Report | `_COMMUNICATION/TEAM_50/reports/2026-04-04_G10_M10_QA_FINDINGS_TEAM50.md` |

**Outcome:** **CONDITIONAL PASS** for M10 scope — pending **Team 100** formal G10 architectural approval per `ROADMAP.md`. Non-blocking: **4** pytest failures in admin `runs.html` (pre-existing Jinja issue).

---

## 3. Team 190 preflight

| Report | Path |
|--------|------|
| M10.2 package | `_COMMUNICATION/TEAM_190/reports/2026-04-04_M10_2_PACKAGE_VALIDATION_TEAM190.md` |
| M10.3 package | `_COMMUNICATION/TEAM_190/reports/2026-04-04_M10_3_PACKAGE_VALIDATION_TEAM190.md` |

---

## 4. Code and migration map (for architectural review)

| Area | Location |
|------|----------|
| Parsers | `organic_market_agent/parsers/nizat.py`, `rexail.py`, `eranorgani.py`, `tamari.py`, `selector_catalog.py` |
| Engine map | `organic_market_agent/parsers/engine.py` |
| ORM / CHECK mirror | `organic_market_agent/models/normalizer.py` |
| Migrations | `032`–`035` (M10.2); `036`–`039` (M10.3 + URLs + dictionary) |
| Tests | `tests/test_m10_3_parsers.py` |

---

## 5. Integration / public interface

- **WordPress / uPress:** Artifacts under configured `UPRESS_UPLOAD_PATH` (default `wp-content/uploads/market/`): versioned + fixed `public_report*`, `manifest.json`, `manifest_last_good.json`.  
- **Public URL:** `https://www.nimrod.bio/smallfarmsagent/` — verified **200** after upload.  
- **Nimrod human check:** Confirm embedded report body and freshness banner match expectations in the browser (QA used HTTP-level check only).

---

## 6. Risks for Team 100 attention

1. **Global scope-skip prefix** `גבינת ` (Tamari cheese SKUs) — audit cross-source false positives over time.  
2. **Rexail / Tamari** share Next.js Redux shape; Tamari parser delegates to Rexail then HTML fallback.  
3. **Python 3.9** on the QA host vs. project **3.11+** lock — recommend CI/production on 3.11+.

---

## 7. Requested Team 100 actions

1. Record **architectural approval** (or documented exceptions) for **G10** M10.2+M10.3 slice.  
2. Confirm **no conflict** with mypips / migration **031** constraints (no rollback; 38 candidates inactive per corrections).  
3. Prioritize admin **`runs.html`** fix if full green CI is a release gate.

---

*Prepared by: Team 10*  
*Date: 2026-04-04*
