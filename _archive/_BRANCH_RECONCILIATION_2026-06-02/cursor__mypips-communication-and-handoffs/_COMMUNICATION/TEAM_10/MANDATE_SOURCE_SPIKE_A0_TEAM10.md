---
document_type: MANDATE
version: "1.0"
---

# Mandate — Source Onboarding Phase A Technical Spike

**Mandate ID:** MANDATE-20260404-SOURCE-SPIKE-A0
**From:** Team 100 (Architecture)
**To:** Team 10 (Feature Dev)
**Date:** 2026-04-04
**Priority:** HIGH
**Gate dependency:** Blocks Phase A source onboarding
**Status:** COMPLETED

---

## 1. Context

Team 10 delivered a Phase A/B source onboarding report identifying 11 farm URLs for Phase A and 7 retail URLs for Phase B. Team 100 requires a technical spike on all Phase A URLs before committing engineering resources.

**Triggered by:** `_COMMUNICATION/TEAM_100/reports/2026-04-04_SOURCE_ONBOARDING_PHASES_A_B_TEAM100.md`
**Related documents:**
- `_COMMUNICATION/TEAM_80/organic_vegetable_sites.md`
- `_COMMUNICATION/TEAM_10/reports/2026-04-03_organic_vegetable_sites_relevance_TEAM10.md`
- `docs/SOURCE_MAP_MASTER_HE.md`

---

## 2. Spike Results — New Phase A URLs (8 sites)

| # | Requested URL | Actual URL | HTTP | Platform | Products | Prices | Viable? |
|---|---|---|---|---|---|---|---|
| 1 | bensfarm.co.il | www.bensfarm.co.il | 200 | **Rexail (Next.js SSR)** | 70 organic vegetables | **Yes — full per-kg/unit** | **YES** |
| 2 | offaime.co.il | ofaimme.com | 200 | WooCommerce | 30 items (wine, dairy, gifts) | Yes but NOT vegetables | No — wrong category |
| 3 | hameshek.com | www.hameshek.com | 403 | Custom SPA (Cloudflare) | Meat, poultry, fish, deli | Unknown (blocked) | No — meat retailer |
| 4 | meshekhavivian.co.il | havivian.co.il | 200 | OpenCart | 41 vegetable info pages | **No prices** (CSA model) | No — no price data |
| 5 | ecofarm.co.il | ecofarm.co.il | 200 | WooCommerce | Tour tickets only; produce shop at meshek.net is login-gated | No public prices | No — login required |
| 6 | meshekrappaport.co.il | NXDOMAIN | — | — | — | — | **DEAD** |
| 7 | meshek8.co.il | meshek8.co.il | 200 | WordPress | — | — | **Wrong business** (design studio) |
| 8 | organic-israel.com | organic-israel.org.il | 200 | WordPress + JetEngine | Farm directory (~59 entries) | No prices | **Discovery only** |

### Detailed Finding: Ben's Farm (SOLE VIABLE CANDIDATE)

**Platform:** Rexail — Israeli e-commerce SaaS built on Next.js with SSR.

**Data extraction:** All 70 products with prices are embedded in `<script id="__NEXT_DATA__">` as JSON at `props.pageProps.initialReduxState.storeProduct.storeProductById`. No CSS selectors needed — parse JSON from SSR payload.

**Available fields per product:** `fullName`, `price`, `soldByWeight`, `sellingUnit.name`, `productCategory.name`, `productQuality.name` (marks organic), `activeForOnline`, `imageUrl`.

**Sample data:**

| Product | Price (₪) | Unit |
|---|---|---|
| עגבניה | 18.9 | ק"ג |
| אבוקדו | 19.9 | ק"ג |
| בטטה | 16.9 | ק"ג |
| באק צ'וי | 12.9 | ק"ג |
| כוסברה | 9.0 | צרור |

**New collector approach:** HTTP GET homepage → parse `__NEXT_DATA__` JSON → extract from Redux store. No browser needed.

**New `platform_family`:** `rexail` — potentially reusable for other Israeli farms using Rexail.

---

## 3. Spike Results — Existing Source Reassessment

| Source | Code | Status | Finding | Action |
|---|---|---|---|---|
| Chubeza .com | SRC003 | No change | Blog/CSA info site; all ordering via easyFarm subdomain. Static basket prices (₪105/₪130) in editorial text. | Keep existing easyFarm profile |
| Etz Hasadeh .co.il | SRC006 | **OUT OF SCOPE** | Redirects 301 to kemach.co.il (flour mill). EasyFarm subdomain has only 2 catering platters. | **Deactivate SRC006** |
| Sadeh Yarok | SRC008 | **SITE DEAD** | 502 on ALL endpoints including /wp-json/. Server offline behind Cloudflare. | **Deactivate SRC008** |
| Zinger Organic | SRC009 | **SITE DEAD** | 502 on ALL endpoints. Was JS-challenge-protected even when alive (Feb 2026 Wayback shows only Cloudflare interstitial). | **Deactivate SRC009** |

---

## 4. Corrected URL Registry

| Original URL | Correct URL | Notes |
|---|---|---|
| offaime.co.il | ofaimme.com | Double M in domain |
| meshekhavivian.co.il | havivian.co.il | Different domain entirely |
| meshekrappaport.co.il | NXDOMAIN | Domain does not exist |
| organic-israel.com | organic-israel.org.il | .org.il, not .com |

---

## 5. Recommendations

### Immediate (Phase A)

1. **Onboard Ben's Farm (bensfarm.co.il)** — create SRC021, build Rexail collector + parser
2. **Deactivate SRC006** (Etz Hasadeh — flour mill, not vegetable farm)
3. **Deactivate SRC008** (Sadeh Yarok — site dead)
4. **Deactivate SRC009** (Zinger Organic — site dead)

### Future Discovery

5. **organic-israel.org.il** — use farm directory (~59 entries) to discover new source candidates in a future spike
6. **Rexail platform family** — if Ben's Farm works well, scan for other Israeli farms using Rexail

### Scope Reduction Notice

Phase A reduces from 8 new sources to **1 viable source**. The remaining 7 are dead, wrong business type, login-gated, or lack price data. This is a significant gap that should inform the next discovery cycle.

---

*Issued by: Team 100 (Architecture)*
*Date: 2026-04-04*
*Authorized by: Team 100 (Architecture)*
