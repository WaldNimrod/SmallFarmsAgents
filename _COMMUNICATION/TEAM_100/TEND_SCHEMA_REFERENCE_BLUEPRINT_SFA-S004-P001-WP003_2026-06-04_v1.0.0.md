# Tend — Schema & Module Reference Blueprint (SFA primary architecture reference)

**WP:** SFA-S004-P001-WP003 · **Date:** 2026-06-04 · **Author:** Team 100
**Status:** Deep-dive (public docs) COMPLETE. **Field-exact schema PENDING** an authenticated Tend export from Team 00 (see §6).
**Why Tend is the primary reference:** Team 00 (Nimrod), multi-year Tend user (beta→full), assesses its **modules + data model as excellent**, UI weaker, with a **long learning curve + heavy maintenance burden**. We adopt the schema/modules and build our own Hebrew/RTL headless UI over farmOS.

---

## 0. ⚠ Disambiguation (critical)
There are TWO companies named "Tend": **`tend.com` = the farm product** (this study). **`tend.io` / github.com/tendio/API = an unrelated marketing CRM** — do NOT use its schema. Tend's real farm-app API (`pro-api.tend.com`, `api-v2.tend.com`) is **login-gated**, so all field-level detail below is **inference from public feature/pricing/blog pages + Tend 2.0 announcement**, not a published data dictionary. Module/entity/calculator existence = high confidence; exact field names/types/tier-gating = inference. Tier names (public, ~): **Free → Standard ~$7 → Pro ~$34 → Ultimate ~$104 → Enterprise** (flat-rate) + add-on AI credits/storage.

## 1. Module catalog (16)
1. **Crop Library / Growing Templates** (Free+, core) — reusable agronomic master data. 2. **Visual Crop Planner** (Standard+). 3. **Task Management / Smart Tasks** (Standard+). 4. **Harvest Planner** (Pro+). 5. **Catalog & Inventory Manager** (Standard/Pro). 6. **Orders & eCommerce/Sales** (Pro+). 7. **CRM (Customers/Vendors/Contacts)** (Standard+). 8. **Traceability** (lot/seed-to-sale). 9. **Accounting/Financials** (Pro/Ultimate). 10. **Reports/Analytics** (projected-vs-actual). 11. **Time & Labor/Punch Clock** (Pro+, GPS). 12. **Farm Map/Locations** (Standard+). 13. **Soil Health**. 14. **Notes/Observations**. 15. **AI Assist** (credit-metered). 16. **Integrations** (Shopify Connector, Zapier, public API).

## 2. Entity-relationship spine (the part to ADOPT)
`Crop 1—* GrowingTemplate 1—* TaskTemplate` · `GrowingTemplate 1—* Planting *—1 Bed (Field>Block>Bed)` · `Planting 1—* Task` · `Task(harvest) 1—1 Harvest 1—1 Lot` · `Lot 1—* InventoryRecord(per channel)` · `Product *—* Lot` · `Order *—1 Customer`, `Order *—* Product`, `Order 1—1 Invoice` · `PurchaseOrder *—1 Vendor → Lot` · `Task 1—* TimeEntry → LaborExpense → ChartOfAccounts`.

### GrowingTemplate attribute set (the gem — SFA's calculator-input superset)
"Hundreds of attributes." Confirmed/implied: DTM · harvest window/duration · in-row spacing · between-row spacing · rows-per-bed · seeding requirements (direct vs transplant, cells/tray) · germination rate · estimated loss/mortality % · yield (per area/bed-foot/plant) · growth-stage offsets (gh-seed/transplant/first-harvest) · multi-stage/perennial yield curves [UNVERIFIED] · embedded TaskTemplates · forecasted price. **Ops:** clone-to-many-crops, link/cascade edits, multiple-templates-per-crop, AI-preloaded editable defaults.

**Key entities:** Planting (basis = area/yield/revenue/#plants/maximize-location; one-click succession; **NO sub-bed/intercrop geometry** = known gap). TaskTemplate (priority, equipment, inputs+application-rate, est-labor). Task auto-generates from templates, auto-regenerates on plan change & yearly, auto-writes records on completion. Harvest→Lot (auto lot-ID+barcode). Product (auto-SKU, per-channel price, Kits/recipes). Inventory statuses: incoming/on-hand/committed/expired/available-to-sell (per channel). Location: Field>Block>Bed + greenhouse/rack/shelf/tower. Financials: customizable chart-of-accounts; **economics = self-entered prices only** (no market feed = known gap). Time: GPS clock-in × labor rate → labor expense.

## 3. Calculator / automation inventory
Growing-space-required · seed-quantity/planting-materials (+earliest date needed) · transplant/seed-tray count · yield projection (day/week/month/season) · revenue projection (yield × self-entered price) · succession scheduling · task generation · est-labor-time · labor expense · bed-availability/fit · inventory rollup · cost-of-production/profit-per-crop ranking. **→ This set ≈ SFA's 14 calculators' input/output space; strong parity target.**

## 4. ADOPT / SKIP / ADAPT for SFA (mapped to farmOS Asset/Log/Quantity/Term)
| Tend module | Verdict | Notes |
|---|---|---|
| **Crop Library / GrowingTemplate** | **ADOPT (top priority)** | `plant_type` Term + custom "growing template" bundle. Separate crop-master from per-crop template; multiple-templates-per-crop + clone/cascade. Maps to AssumptionField pattern + 14 calcs. **ADAPT:** metric (cm/m/kg/dunam), Hebrew names, Israeli varieties/seasons. **DO BETTER:** ship a LEAN curated template (13-topic + 14-calc inputs) w/ progressive disclosure — Tend's "hundreds of attributes" = the maintenance burden to avoid. Use Tend's list as a *superset menu*, not a spec to replicate. |
| **Visual Crop Planner / Planting** | **ADOPT concept / ADAPT geometry** | plant Asset + seeding/transplant/harvest Logs; bed = land Asset. ADOPT plan-by-{area/yield/revenue/#plants} + 1-click succession. **BEAT:** add sub-bed/intercrop geometry (Tend lacks; farmOS WKT supports) — real value for intensive Israeli gardens. |
| **Task + TaskTemplate** | **ADOPT** | Log types from template; auto-generate/regenerate server-side, exposed via API. |
| **Harvest Planner** | **ADAPT** | harvest Log+Quantity; orders+field+storage view only if SFA does sales; weather = defer. |
| **Catalog/Product/Kit/SKU** | **ADAPT** | custom Product Asset + auto-SKU; **Kits = CSA box/מנה** (relevant). Barcode optional. |
| **Inventory/Lot/Traceability** | **ADOPT (lite)** | Quantity on Assets + lot Asset/Term; auto lot-ID + seed→sale trace. SKIP heavy GAP/recall v1. |
| **Orders/eCommerce/Store** | **SKIP core / ADAPT minimal** | out of scope headless; model Order/Customer lightly for CSA/box; no storefront (Israeli growers use חשבונית ירוקה + WhatsApp/local). |
| **CRM** | **ADAPT (minimal)** | tiny Customer/Vendor Asset only if CSA/wholesale. |
| **Accounting/P&L** | **ADAPT** | cost via input/labor Logs+Quantity; ADOPT profit-per-crop *reporting* (14 calcs already do this); SKIP full bookkeeping → integrate external. **BEAT:** pull Israeli wholesale market prices for revenue projection (Tend = self-entered only). |
| **Time & Labor/GPS clock** | **SKIP v1** | solo/family gardens; keep est-labor as planning number only. |
| **Farm Map / Field>Block>Bed** | **ADOPT** | land/structure Assets + geometry; ADAPT to dunam; add sub-bed geometry. |
| **Soil Health** | **ADOPT (lite)** | soil Log (quantity+lab term+attachment), metric. |
| **Notes/Observations** | **ADOPT** | observation Log w/ structured fields (pest/disease, final-harvest, termination reason). |
| **AI Assist** | **SKIP v1** | don't gate core data on AI credits. |
| **Integrations** | **ADAPT** | our API IS the integration surface; adopt Tend's REST conventions as defaults. |

## 5. Cross-cutting lessons (Nimrod's verdict, validated)
- **ADOPT the spine** Crop→Template→Planting→Task→Harvest→Lot→Inventory (maps 1:1 to farmOS Asset/Log/Quantity/Term).
- **Learning curve + maintenance = "hundreds of attributes per template" + broad surface → SFA stays lean & opinionated** (curated 13-topic + 14 calcs).
- **Two concrete places to beat Tend:** (a) sub-bed/intercrop geometry, (b) self-entered-prices-only economics → our Israeli market-price index.
- **Weak UI/RTL → our Hebrew-first polished UI is the differentiator** (schema parity, better UX).

## 6. ⚠ Field-exact gap & the ask
Public docs give module/entity/calculator existence + attribute *categories*, but **not field-exact types/names** (real schema is login-gated at `pro-api.tend.com`). **Team 00 has an authenticated Tend account.** A **sample export (CSV/JSON) of one Growing Template + one Planting + one Order/Lot**, or a captured API response, would convert this blueprint from inference → field-exact — the single highest-value input for SFA's data-model design.
