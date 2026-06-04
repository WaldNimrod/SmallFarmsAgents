# Competitive Intelligence Report: Farm-Management & Market-Gardening Software (for "SFA")

*Senior product & competitive-intelligence analysis. Sources are public (vendor sites, pricing pages, docs, app stores, G2/Capterra/GetApp/BBB, forums). FACT = sourced; INFERENCE = flagged as reasoning. Current as of June 2026.*

## TL;DR
- **No competitor combines all five SFA pillars (Plan→Execute→Sell→Relate→Improve) in one Hebrew-first, RTL product, and none links a live market-price index to crop-by-crop profitability planning** — these are SFA's two clearest white spaces. The closest production planners (Heirloom, Tend) project *revenue* (price × yield) but do not rank crops by true margin or feed live market prices into the plan.
- **Hebrew/RTL is essentially unserved.** Every reviewed product ships English-first; Farmbrite and Local Line claim multi-currency/some-language support but none documents Hebrew or RTL, and Local Line/Barn2Door/Harvie don't even operate in Israel. Confirmed open ground.
- **Pricing benchmark:** serious market-garden tools cluster at **$25–$40/mo** (Tend Pro $30, Farmbrite crop $29–$59, GrowVeg $29/yr at the hobby end), while sales/CSA platforms run far higher ($79–$200+/mo plus setup fees). A genuinely useful free tier (Tend, Seedtime, Planter) is now table stakes.

## Key Findings
1. **The category splits into three camps:** (a) production/crop planners (Heirloom, Tend, Seedtime, GrowVeg, Planter, LiteFarm, farmOS); (b) operations/records & compliance (Farmbrite, Croptracker, AgriWebb); (c) sales/CSA commerce (Local Line, Barn2Door, Harvie). SFA's ambition to span all three end-to-end is genuinely differentiated.
2. **Tend is the most direct all-in-one threat** — free tier, 39,000+ crop/variety templates, auto seed/spacing calculators, yield+revenue projection, and a Pro tier ($30/mo) adding sales/inventory/CRM/accounting. Trusted by customers in 40+ countries with a team of 50+ engineers (per tend.com). It is in Beta and lacks Hebrew/RTL.
3. **Heirloom (JM Fortier / Market Gardener Institute) is the closest philosophical sibling** — bio-intensive, bed-based, succession-aware, with seed-list/transplant/nursery/workload calculators and revenue projection. But it has no sales/CRM, no cost-accounting/profit-ranking, and is EN/FR only.
4. **Nobody does the "economics link" well.** Revenue projection exists; true cost→margin→"what is most profitable to grow" ranking tied to a live regional price index does not exist in any reviewed product. This is SFA's strongest wedge.
5. **The unified morning cockpit is partially served** (Tend, Heirloom, Seedtime, Farmbrite all have task lists) but none unifies Plan+Sell+CRM into a single role-based "what to do now" view for both manager and farm worker.
6. **Recurring pain points to design around:** opaque/high pricing & surprise charges (Barn2Door), no offline mode (Tend), beta bugs (Tend, Heirloom), clunky drawing tools (GrowVeg), data-hostage on cancellation (GrowVeg, Farmbrite), weak accounting/POS integration (Farmbrite).

---

## A. Per-Competitor Dossiers (10 axes each)

### 1. Tend — tend.com
1. **Data model:** Crops + variety templates (39,000+ preloaded, per tend.com/pricing), farm map/field layout, plantings, tasks, harvests, inventory, orders, customers/vendors/contacts, chart of accounts. Custom data fields on Enterprise (unlimited).
2. **Features:** Advanced crop/production planning; auto-calculates seed lists and in-row spacing; auto-generates season tasks with dependency updates; yield projections by week/month/season; revenue projection; harvest planning; inventory; multi-channel sales (online/wholesale/POS); invoicing; financials; lot traceability & certification reporting; pre-built reports. AI automation credits per tier.
3. **Daily cockpit:** Pre-built dashboards & reports; task/workflow management with assignment; "convert notes into tasks." Roles/permissions (Pro+). iOS & Android apps. **No offline mode** (repeated complaint).
4. **Pricing:** Free forever (1 user, 25 AI credits); Pro $30/mo (5 users); Ultimate $75/mo on tend.com — **but Capterra (2026) lists Ultimate at $104.30/mo flat; verify directly**; Enterprise from $400/mo. Annual saves 33%. No card for free. Source: tend.com/pricing.
5. **Audience/positioning:** Small-to-mid diversified/organic farms; "the leading farm management software for modern growers"; "Farm Management Software of the Year 2025 – AgriBusiness Review."
6. **UX/UI:** Modern, AI-forward; web + native apps; in Beta. Reviewers praise crop planner and onboarding.
7. **Weaknesses:** "There's no offline mode" (Capterra); "Zero support and limited online resources" (one Capterra reviewer); in Beta; advanced features have a learning curve; nursery/tree (long-cycle) use reported as not fully supported.
8. **Tech/integrations:** Shopify & Square (Ultimate); API & webhooks + robotics integrations (Enterprise); AI receipt scanning.
9. **Localization:** English-first; no documented Hebrew/RTL.
10. **Economics link:** Projects yield→revenue and "which crops are projected to bring in the most revenue" via reports; tracks income/expenses; **no live market-price index, no true margin-ranking of crops.** Revenue ≠ profit. *(INFERENCE: closest to SFA but stops at revenue.)*

### 2. Seedtime — seedtime.us
1. **Data model:** Crops with built-in categories & varieties, custom crops/varieties, planting schedules, successions, tasks/task-series, perennials, records (harvest/seeding/transplant counts), Layout (garden mapping w/ location history for rotation), calendar(s).
2. **Features:** Visual year-round calendar (seed/transplant/harvest), drag-and-drop scheduling, auto succession planting, "next best seeding date" algorithm (credit-metered), companion-planting suggestions, winter-gardening protection algorithm, printable views & weekly checklists, Layout mapping.
3. **Daily cockpit:** Daily/weekly auto-compiled task list with check-off; mobile-usable web app. Individual-grower oriented, not role-based teams.
4. **Pricing:** Free forever (10 monthly seeding-date credits, 1 calendar, built-in crops only); Basic and Unlimited paid tiers. Third-party cites ~$29/mo standard / ~$49/mo premium (**unverified vs. site**); 30-day money-back. Source: seedtime.us/pricing.
5. **Audience/positioning:** Home gardeners → small farms/homesteads; anti-spreadsheet, beginner-friendly; US/Canada zone+frost optimized.
6. **UX/UI:** Modern, friendly, visual; mobile web; praised as intuitive. Some features "coming soon."
7. **Weaknesses:** US/Canada-centric (zone/frost); free tier limited; printing/export basic; not built for commercial teams or sales.
8. **Tech/integrations:** Quick-links to seed-company varieties; limited documented integrations.
9. **Localization:** "Worldwide calendar settings" but English UI; no Hebrew/RTL.
10. **Economics link:** None meaningful — planning-only. (Separate $27 "Garden Plan" PDF cites a $2,030.85 tracked harvest value as marketing, not a feature.)

### 3. Heirloom / Market Gardener Institute — heirloom.ag; themarketgardener.com
1. **Data model:** Satellite-map farm with **field blocks and beds**; 250+ crops incl. named cultivars; custom crops; perennials (duplicate-season workaround); successions in space+time; per-crop "Data Charts" storing spacing, days-to-maturity, expected yield, recurring tasks, separate transplant vs direct-seed charts, selling price/unit.
2. **Features:** "Game Plan" season planner (sort by crop/implantation/nursery/harvest date); **auto seed lists & quantities; transplants-to-order; nursery container counts; seeder-density calculation; succession timing; yield/harvest-availability projection; workload/labor prediction**; harvest module (auto-generates harvest/packing/shipping tasks, plan-vs-actual). Sources: heirloom.ag, docs.heirloom.ag.
3. **Daily cockpit:** Detailed **weekly task list** ("Dynamic Task Calendars") w/ week-board/list views, filters, notes, team assignment. **Mobile app launched ~mid-2025** (iOS/Android) as a field companion (tasks, harvest logging, notes); heavy planning still desktop-oriented.
4. **Pricing:** **One free month, no credit card** (signup page). Per-farm billing; each additional farm = 7-day trial then separate subscription; up to 5 owned farms/account, unlimited collaboration. **Standalone per-farm tier dollar amounts are JS-gated/undisclosed.** However, **course-bundled pricing is public** (themarketgardener.com): Masterclass Certificate **$2,250** (includes 3 months Heirloom); Certificate Plus **$2,525** (1-year Heirloom); Pro Plan **$3,950**. Verify standalone subscription directly.
5. **Audience/positioning:** Small-scale regenerative/bio-intensive market gardeners (JM Fortier method); "built by growers, for growers"; "make more profit… without scaling up or working more hours." Thousands of users since Nov 2023; the parent Masterclass has had 4,000+ students since 2018 and Fortier's book has sold 200,000+ copies — a strong existing audience/funnel.
6. **UX/UI:** Modern, map-driven, drag-and-drop; praised as intuitive; desktop-first; active development with frequent fixes.
7. **Weaknesses:** Beta-era bugs (space calc, drag-drop, seeder-density rounding, French translations) in release notes; desktop-first (mobile is companion only); **no sales/CRM/invoicing/expense-accounting**; AI chatbot "in beta, may… provide… inaccurate responses"; vendor-run community limits critical reviews.
8. **Tech/integrations:** AI features (chatbot, performance recommendations); no documented public API/Zapier/accounting integrations.
9. **Localization:** **English + French** (Quebec team); AI support bot multilingual; **no Hebrew/RTL**.
10. **Economics link:** Strong "profit" *marketing* and **revenue projection** (price × yield, "Harvest and Revenue Tally," est. revenue/month). **No cost-accounting, margin-per-crop comparison, "most-profitable-crop" ranking, or market-price index.** Profitability framed as an outcome of efficiency — the exact gap SFA targets.

### 4. Farmbrite — farmbrite.com
1. **Data model:** Crops (200+ preloaded planting details), unlimited crop types & grow locations, livestock (individual/group/flock, genealogy, health), fields/mapping, tasks, harvests/yield, inventory, orders, customers/vendors/contacts, equipment, accounting (Schedule F). Custom fields (5→10→unlimited by tier).
2. **Features:** Crop season planning, harvest traceability (+QR), soil/nutrient/input tracking, seed-order estimation, task/team management, deep livestock suite, accounting/bookkeeping/P&L, e-commerce store (unlimited SKUs), reports/dashboards, climate/satellite (higher tiers), timesheets.
3. **Daily cockpit:** Dynamic dashboard, calendar, to-do lists, reminders; iOS/Android apps; **offline record keeping/scouting**; roles incl. read-only/auditor.
4. **Pricing (USD):** Accounting-only $119/yr. Crop: Essentials $29, Performance $39, Premium $59/mo. Livestock: $29/$49/$79. Complete: $59/$79/$109/mo (annual ≈2 months free). 14-day trial, no card. New-farmer up to 50% off 3 yrs; nonprofit up to 65%; heroes 25%. Source: farmbrite.com/pricing.
5. **Audience/positioning:** Diversified crop + livestock small/mid farms worldwide; "operating system… built by agricultural experts"; strong on livestock + accounting.
6. **UX/UI:** Functional, broad; learning curve on setup/specific features; Wix marketing site; mobile apps maturing.
7. **Weaknesses:** "Not easy to sort livestock and can't export to excel" (G2); "no POS… does not integrate with… accounting… invoicing is separate" (G2); accounting-only "$99 is kind of steep" for once-a-year use (Capterra); graphs hard to interpret; one-transaction-at-a-time entry.
8. **Tech/integrations:** Public API & webhooks (higher tiers); developers.farmbrite.com; RFID/EID scanning; localized currency/measurement.
9. **Localization:** "Language support" claimed across 100+ countries with localized currency/measurement; **no documented Hebrew/RTL** specifically — treat vendor multi-language claim with caution.
10. **Economics link:** Per-animal and per-operation P&L, expense tracking; crop-side is cost/income recording, **not** predictive crop-margin comparison or market-price-driven crop selection.

### 5. AgriWebb — agriwebb.com
1. **Data model:** Livestock-centric — mobs/individual animals, paddocks/farm map, infrastructure, tasks (GPS/photo), treatments, grazing/feed, sale/death records; multi-farm. Crop/pasture records secondary.
2. **Features:** Offline record keeping, mob & individual management, grazing/rotational planner (paid add-on), 27+ customizable reports, **cost of production & gross-margin reports**, average daily gain, compliance/accreditation, hardware (EID/scales) integration.
3. **Daily cockpit:** Interactive farm map "from the palm of your hand," GPS/photo team tasks, flexible roles; mobile + desktop; **works offline**.
4. **Pricing:** Baseline subscription + **per-head pricing** (DSE-based: cattle 8, sheep 1.5); multiple farms at no extra base cost. Third-party (dated) cites Hobby $45 / Advanced $125 / Precision $200 / Corporate $400/mo; grazing-planner add-on $150 USD/yr. **Confirm current via site** (model changed from flat to per-head). Sources: agriwebb.com/pricing, help.agriwebb.com.
5. **Audience/positioning:** Livestock farmers/ranchers (AU/UK/US); "run your most profitable, efficient and sustainable business." Not market-garden focused.
6. **UX/UI:** Polished, map-first, mobile-strong, offline; ~100+ updates/yr.
7. **Weaknesses:** Livestock-only fit (irrelevant crop depth for SFA); per-head cost scales with herd; pricing opacity. Reviewers very positive on offline/maps.
8. **Tech/integrations:** EID readers, weigh scales, water monitoring; marketplace add-ons.
9. **Localization:** English (AU/UK/US); no Hebrew/RTL.
10. **Economics link:** Genuine **cost-of-production & gross-margin** reporting — best economics pattern in the category — but livestock not crop, and retrospective not market-price-predictive.

### 6. Croptracker — croptracker.com
1. **Data model:** Modular — mapping/blocks, plantings, spray, irrigation, harvest/yield, packing/storage/shipping, orders (sale/purchase/consignment), labor/work crews, quality control, GAP audit. Built for fruit/veg growers/packers.
2. **Features:** 80+ automated reports incl. GAP/food-safety; spray/irrigation/production-practice records; harvest & traceability (block→employee); packing (pallets/labels); punch-clock/labor & piece-rate; QC; Harvest Quality Vision / Crop Load Vision (AI imaging).
3. **Daily cockpit:** Real-time field→office data, mobile apps (iPad/Android/iPhone); labor/work-order monitoring. Compliance-centric, not "morning to-do."
4. **Pricing:** Modular "pay for what you use"; SourceForge cites starting ~$5.99/mo per module; Enterprise quoted. Free-trial availability **conflicts across listings**. Source: croptracker.com/pricing.
5. **Audience/positioning:** Commercial fruit/veg growers, packers, co-ops of all sizes since 2006 (Dragonfly IT, Kingston, ON); food-safety/traceability leader.
6. **UX/UI:** Functional; "simple and easy to learn"; mapping praised; **sluggish on poor connectivity** (repeated); fruit-scanning fails "in sun."
7. **Weaknesses:** Connectivity lag; "everything has to be palletized… can not create mixed pallets" (Capterra); payroll break-entry limits; feature overload ("so many features we don't use… hide for a cleaner interface").
8. **Tech/integrations:** API integrations (Enterprise); hardware/scanning; custom SOP/reporting.
9. **Localization:** **English only** (per SourceForge); no Hebrew/RTL.
10. **Economics link:** Labor & production **cost tracking** and cost-per-crop via labor; no predictive crop-profit ranking or market-price index.

### 7. Local Line — localline.ca / localline.co
1. **Data model:** Products/price-lists (per customer segment), shared inventory, orders/subscriptions (CSA), customers (unlimited, segmentation), vendors, delivery/pickup plans, fulfillment, payments, harvest batches/lot tracking, 50+ reports.
2. **Features:** E-commerce storefront, multi-channel (retail/wholesale/CSA/market), price lists, sell-by-weight, subscriptions, one-click invoicing, email campaigns, delivery routing, food-safety record-keeping/traceability, supplier-discovery marketplace.
3. **Daily cockpit:** "Run your business from any device in the field"; 50+ dashboards "every Monday morning." Sales-ops focused, not production tasks.
4. **Pricing:** Flat monthly, **no commission**, no setup fee; plans from **$79/mo** (Core/Premium/Ultimate; some channels list $99–$199). Free migration from Barn2Door/CSAware/etc.; free trial. Source: localline.co/suppliers/pricing.
5. **Audience/positioning:** Farms/food hubs selling direct + wholesale; "farm to fork commerce platform"; "shared infrastructure — not a marketplace." 8,000+ farms, 14+ countries. *Vendor cites both "grow sales 23%/yr" and "33% per year" across different pages — inconsistent; treat as marketing.*
6. **UX/UI:** Modern, e-commerce-grade; praised for ease; storefront fast/branded.
7. **Weaknesses:** No production/agronomy planning (sales-only); price floor higher than hobby tools; needs a separate crop planner (positions itself alongside Tend, not replacing it).
8. **Tech/integrations:** QuickBooks, Mailchimp, Square, Routific, Zapier; advanced API/EDI for buyers.
9. **Localization:** English, French, Spanish, Polish, Croatian, German, Slovenian; USA/Canada/UK/Ireland/AU/NZ/select EU. **No Hebrew/RTL; Israel not served.**
10. **Economics link:** Sales analytics & product-performance, not production-cost→profit planning.

### 8. Barn2Door — barn2door.com
1. **Data model:** Products/inventory (retail+wholesale, sell-by-weight), orders (online + POS, pre-orders, subscriptions), customers, fulfillment (pick-pack, labels, routing), payments (Stripe, ACH, Avalara tax), QuickBooks.
2. **Features:** Farm website builder, email/social marketing, multi-channel sales, subscriptions, POS (handheld device), delivery/pickup/shipping, brand/design services, onboarding/coaching.
3. **Daily cockpit:** Single dashboard for orders across channels; mobile-oriented (70%+ sales via smartphone). Sales-only.
4. **Pricing:** **Opaque — requires sales call.** Third-party/user reports: ~$79/mo Essentials + **setup fee** + **3.9% + $0.30** transaction fee (a point above standard Stripe); higher tiers add account management. **No free trial.** Sources: barn2door.com/pricing, BBB, farmzz.com.
5. **Audience/positioning:** Direct-sales farms (esp. meat/ranch); "the operating system for direct farm sales"; "not the cheap, generic DIY solution."
6. **UX/UI:** Polished, full-service; heavy sales/onboarding touch.
7. **Weaknesses (MOST cited):** Aggressive sales calls; **opaque pricing & surprise/unauthorized charges** ("charged my credit card 3 times without permission"; "$3,700" renewal; "$50 surprise tax" — BBB/Tenereteam/CattleToday); higher transaction fees; "front-of-house" only, "could not manage the day-to-day operations" (BBB); no SMS; setup fee + no free trial.
8. **Tech/integrations:** Stripe, Mailchimp, QuickBooks, Avalara.
9. **Localization:** English (US, all 50 states); no Hebrew/RTL.
10. **Economics link:** None on production; sales/margin-uplift claims only.

### 9. Harvie — harvie.farm **(DISCONTINUED Dec 2024)**
CSA personalization platform: members rate crops 1–5; algorithm matches weekly boxes to preferences; flexible shares, vacation holds, payment plans. Farmer cost: **$500 setup + 7% of all farm-share purchases + a small % of card sales** ("That cost is not insignificant" — The Spoon). Claimed **15–20% retention lift** (The Spoon); Harvie Farms Local claimed **97% month-over-month retention** and ~3× the order value of classic CSAs (harvie.farm). **Platform shut down end of December 2024**; farms migrated to Local Line. **Lesson for SFA:** per-transaction % pricing drew cost complaints; CSA preference-matching is a strong Relate/Sell pattern worth emulating, but pure-sales standalone proved unsustainable. English (US/Canada); no Hebrew/RTL.

### 10. GrowVeg — growveg.com
1. **Data model:** Beds/borders/paths (any shape), 135+ plants/varieties with spacing & local sow/plant/harvest dates, plant list with counts, crop-rotation history, succession, irrigation layout, garden journal.
2. **Features:** Drag-and-drop layout (snap-to-grid), localized planting calendar (5,000+ weather stations), square-foot mode, crop-rotation warnings, companion planting, plant-quantity & spacing auto-calc, email reminders, journal.
3. **Daily cockpit:** Email reminders + journal; no team/role features. Desktop-first; iPad usable.
4. **Pricing:** 7-day trial (no card); **~$29/yr** (US) or $40–$50 region-dependent; multi-year discounts; up to 5 plans/yr. Source: growveg.com/subscribeinfo.
5. **Audience/positioning:** Home/hobby vegetable gardeners, homesteaders, community gardens; mature market leader.
6. **UX/UI:** Polished, well-loved; "drawing tools… can be a little clunky."
7. **Weaknesses:** **Subscription data-hostage** — "if you don't continue to pay… you will not have access to… your historical plans"; clunky shape tools; aggressive onboarding emails; hobby-scale (no sales/CRM).
8. **Tech/integrations:** Minimal; standalone web + companion mobile (Garden Planner Pro $7.99 iOS).
9. **Localization:** Regional sites (US/UK/SA/AU-NZ); English; no Hebrew/RTL.
10. **Economics link:** None — supply/shopping lists, no profit logic.

### 11. Planter — planter.garden
1. **Data model:** Garden grids/raised-bed outlines, 100+ fruits/veg + thousands of varieties, custom plants, companion/combative data, square-foot spacing, notes/events log, tasks.
2. **Features:** Visual layout, companion-planting color system, climate-adjusted planting calendar, square-foot grid, tasks & notifications, seed/event logging.
3. **Daily cockpit:** Tasks & notifications; mobile-first (iOS/Android) + web app.
4. **Pricing:** Free tier (1 garden); Premium (annual sub) + **Lifetime $99.99**; web payments supported in USA/Canada/AU/NZ **and Israel** (notable). Sources: planter.garden/pricing, info.planter.garden.
5. **Audience/positioning:** Beginner→experienced home gardeners; "gardening made easy"; most-recommended first-garden app.
6. **UX/UI:** Beautifully designed, intuitive; responsive to feedback (public backlog).
7. **Weaknesses:** Free tier 1-garden cap; broad (not varietal-specific) advice; "wish there was a better way to visualize drip irrigation"; hobby-scale only.
8. **Tech/integrations:** SeedBox (seed inventory); minimal third-party.
9. **Localization:** English UI; bills in Israel but **no Hebrew/RTL UI** documented.
10. **Economics link:** None.

### 12. farmOS — farmos.org *(benchmark / SFA's chosen backend)*
1. **Data model:** Highly general — **Assets** (Land [fields/beds/paddocks, hierarchical], Plant [groups or individuals], Seed [shares crop/variety taxonomy], Equipment, Structure [greenhouses], Water, Material, Group, Animal), **Logs** (activity, observation, input, harvest, seeding, lab test…), **Quantities, Terms (taxonomy), Plans, Data Streams (sensors), Users.** Crop/variety as taxonomy terms.
2. **Features:** Records/tasks/planning, mapping (OpenLayers), inventory quick-forms, much-improved CSV import/export (v3.1), sensor ingestion, plan relationships, fine-grained crop planning. Extensible via Drupal modules.
3. **Daily cockpit:** Logs/tasks; Field Kit app (native + PWA) with **offline** entry. Drupal role/permission system. UI is generic/admin-grade — *exactly why SFA builds its own Hebrew/RTL UI on top.*
4. **Pricing:** Free, open-source (GPL); self-host or paid hosting (Farmier).
5. **Audience/positioning:** Researchers, developers, farms of all scales wanting data ownership & interoperability.
6. **UX/UI:** Functional/technical, very flexible, not consumer-polished.
7. **Weaknesses (as backend):** Unopinionated model requires SFA to impose conventions; generic UI; setup/hosting expertise needed.
8. **Tech/integrations:** **Drupal/PHP; REST API; farmOS.js; UUIDs; Aggregator; data streams.** Strong openness — ideal headless backend.
9. **Localization:** Drupal i18n supports **any language incl. RTL**; community-contributed translations — SFA can drive Hebrew. (Key enabler.)
10. **Economics link:** Quantities/logs can store costs/prices but no built-in profit engine — SFA's calculators add this layer.

### 13. LiteFarm — litefarm.org *(benchmark)*
1. **Data model:** Farm areas (fields, greenhouses, pastures, buffer/wooded zones, multi-plot), crop catalog **(375 crops; 385+ community-contributed)**, custom crops (shareable), plantings, tasks, inputs, expenses, certifications, animals.
2. **Features:** Planning & recording (planting/harvest/input), task assign/complete, area mapping, expense management, organic-certification support, worker safety, ecosystem-service/biodiversity tracking, **Farm Notes** noticeboard.
3. **Daily cockpit:** Task management (assign/complete), mobile-responsive web; farmworker autonomy emphasized (students choose task order).
4. **Pricing:** **Free, open-source (GPLv3)**, non-profit (UBC Centre for Sustainable Food Systems).
5. **Audience/positioning:** Small/mid sustainable & diversified organic farmers globally; "community-led digital public good"; explicitly anti-lock-in.
6. **UX/UI:** Clean, co-designed with farmers, mobile-responsive; ease-of-use top priority.
7. **Weaknesses:** Lighter on sales/commerce & deep calculators; research-driven cadence.
8. **Tech/integrations:** Open-source; OpenTEAM ecosystem; self-host or hosted.
9. **Localization:** **8 languages — English, French, Spanish, Portuguese, German, Hindi, Malayalam, Punjabi.** No Hebrew yet; no RTL language in set — but proves the multilingual community-translation model.
10. **Economics link:** Expense tracking + certification; sustainability-economics framing, not predictive crop-profit/market-price.

---

## B. Schema-Comparison Matrix (union of how the industry models farm data)
Legend: ● core/strong · ◐ partial/limited · ○ absent/not found

| Data entity / attribute | Tend | Seedtime | Heirloom | Farmbrite | AgriWebb | Croptracker | LocalLine | Barn2Door | GrowVeg | Planter | farmOS | LiteFarm |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Crops (catalog) | ●39k | ● | ●250+ | ●200+ | ◐ | ● | ◐ | ○ | ●135+ | ●100+ | ●tax | ●375 |
| Varieties/cultivars | ● | ● | ● | ◐ | ○ | ◐ | ○ | ○ | ● | ●1000s | ● | ◐ |
| Custom crops/fields | ●Ent | ● | ● | ●5–∞ | ● | ● | ◐ | ○ | ◐ | ● | ● | ● |
| Beds | ◐ | ●Layout | ● | ◐ | ○ | ◐ | ○ | ○ | ● | ●grid | ●Land | ◐ |
| Fields/zones/paddocks | ● | ◐ | ●blocks | ● | ●padd | ●blocks | ○ | ○ | ◐ | ◐ | ●hier | ●multi |
| Plantings | ● | ● | ● | ● | ◐ | ● | ○ | ○ | ● | ● | ●Plant | ● |
| Successions | ● | ● | ● | ◐ | ○ | ◐ | ○ | ○ | ● | ◐ | ◐ | ◐ |
| Tasks (assignable) | ● | ◐solo | ● | ● | ● | ● | ◐ | ◐ | ○ | ◐ | ● | ● |
| Harvests/yield | ● | ◐ | ● | ● | ◐ | ● | ◐ | ○ | ○ | ○ | ●log | ● |
| Inventory | ● | ◐ | ◐ | ● | ◐ | ● | ● | ● | ○ | ◐seed | ●mat | ◐ |
| Sales/orders | ●Pro | ○ | ○ | ● | ◐ | ● | ● | ● | ○ | ○ | ◐ | ○ |
| Customers/CRM | ●Pro | ○ | ○ | ● | ○ | ◐ | ●seg | ● | ○ | ○ | ◐ | ○ |
| Livestock | ◐ | ○ | ○ | ● | ●deep | ○ | ◐ | ◐ | ○ | ○ | ●animal | ◐ |
| Soil/inputs | ●log | ○ | ◐ | ● | ●graz | ●spray | ○ | ○ | ○ | ○ | ●log | ●input |
| Certification/compliance | ●Pro | ○ | ○ | ◐ | ●accr | ●GAP | ◐ | ○ | ○ | ○ | ◐ | ●organic |
| Cost/price per crop | ◐ | ○ | ◐price | ●P&L | ●COP | ◐labor | ◐ | ◐ | ○ | ○ | ◐qty | ◐exp |
| Custom fields | ●Ent | ● | ◐ | ●5–∞ | ◐ | ● | ◐ | ○ | ○ | ◐ | ●Drupal | ◐ |
| Sensors/data streams | ◐ | ○ | ○ | ◐clim | ●EID | ◐ | ○ | ○ | ○ | ○ | ●stream | ○ |
| **Market-price index** | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |

**Schema takeaway:** The industry's union of entities = Crops→Varieties→Plantings (in Beds/Fields/Zones, with Successions) → Tasks → Harvests/Yield → Inventory → Orders/Sales → Customers → Inputs/Soil → Cost/Price → Certification. **Nobody models a market-price index** (uniform ○), and **cost-per-crop is shallow** everywhere except livestock (AgriWebb COP, Farmbrite P&L). SFA's 13-topic crop taxonomy + 14 calculators + price index is a richer agronomic-economic schema than any single competitor.

## C. Feature & Pricing Matrix

| Tool | Free tier | Entry paid | Top paid | Model | Planning calcs | Daily cockpit | Sales/CRM | Offline | API | Hebrew/RTL |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Tend** | ● forever | $30/mo Pro | $75–$104/mo + $400 Ent | Per-tier, user caps | ●seed/spacing/yield/rev | ●tasks+dash | ●Pro | ○ | ●Ent | ○ |
| **Seedtime** | ● forever | ~$29/mo* | Unlimited | Tier+credits | ●succ/seed-date | ●task list | ○ | ○ | ○ | ○ |
| **Heirloom** | 1 mo free | undisclosed | $3,950 course bundle | Per-farm | ●seed/transplant/nursery/workload/yield | ●weekly tasks | ○ | ◐app | ○ | ○ EN/FR |
| **Farmbrite** | 14-day | $29/mo | $109/mo | Per-tier flat | ◐seed-order | ●dash+tasks | ● | ● | ●higher | ○ |
| **AgriWebb** | demo | ~$45/mo* | ~$400/mo* | Base+per-head | ◐grazing | ●map+tasks | ◐ | ● | ◐ | ○ |
| **Croptracker** | varies | ~$5.99/mo/mod | quote | Modular | ◐ | ●field ops | ●orders | ◐ | ●Ent | ○ |
| **Local Line** | trial | $79/mo | $199+/mo | Flat, no commission | ○ | ●sales dash | ● | ◐ | ●buyers | ○ |
| **Barn2Door** | none | ~$79/mo+setup+3.9% | quote | Tier+setup+txn% | ○ | ●orders | ● | ◐ | ◐ | ○ |
| **Harvie** †disc | n/a | $500+7% | — | Txn % | ○ | ◐ | ●CSA | ○ | ◐ | ○ |
| **GrowVeg** | 7-day | ~$29/yr | multi-yr | Annual sub | ●spacing/qty/rotation | ◐email | ○ | ○ | ○ | ○ |
| **Planter** | ●(1 garden) | annual | $99.99 lifetime | Freemium | ◐spacing/calendar | ●tasks/notif | ○ | ◐ | ○ | ○(bills IL) |
| **farmOS** | ● OSS | self-host | hosting | Open-source | ◐modules | ●Field Kit | ◐ | ● | ●strong | ◐i18n incl. RTL |
| **LiteFarm** | ● OSS | — | — | Open-source | ◐ | ●tasks | ○ | ◐ | ◐ | ◐8 langs |

\*Third-party/dated — verify on vendor site. †Harvie discontinued Dec 2024.

## D. White-Space Analysis
1. **Hebrew-first / RTL / Israel — wide open.** Every product is English-first; none documents Hebrew or RTL. Local Line (7 EU languages) and LiteFarm (8 languages) prove multilingual demand and a community-translation path, but neither does Hebrew/RTL — and **Local Line/Barn2Door/Harvie don't operate in Israel.** SFA's RTL-native UI on farmOS (Drupal i18n already supports RTL) is a defensible moat.
2. **Market-price → profit planning — unserved (the strongest wedge).** The market-price-index row is a uniform ○ across all 13 tools. Revenue projection exists (Tend, Heirloom); retrospective cost/margin exists for livestock (AgriWebb COP, Farmbrite P&L); but **no one tells a market gardener "given current Israeli market prices and your costs, crop X earns more ₪/bed-week than crop Y — grow more X."** SFA's price index + crop-profit-comparison + expected-revenue calculators own this outright.
3. **The unified 5-pillar morning cockpit — unserved.** Planners stop at Plan+Execute (Heirloom, Seedtime, GrowVeg); ops tools add records (Farmbrite, Croptracker); sales tools own Sell+some Relate (Local Line, Barn2Door, Harvie). **No product fuses Plan→Execute→Sell→Relate→Improve into one role-based "what to do now" screen for manager and worker.** Tend is closest but has no offline mode and no live-price/profit layer.
4. **Localized small-commercial market-garden depth.** Heirloom/Tend serve this audience globally but in English and without the economics engine; deep bio-intensive bed-and-succession depth localized to Israeli climate/crops/prices is unoccupied.
5. **Freemium community funnel.** Seedtime/Planter/GrowVeg own hobby planning but never graduate users to commercial ops; Tend's free tier is the only credible free→paid funnel and it's English. SFA's free Hebrew home tier → paid market-garden tier is open.

## E. Top 10 UX/Product Pain Points to Design Around
1. **No offline mode** in cloud planners (Tend explicitly) — fatal in the field. *farmOS Field Kit gives SFA offline by default; expose it.*
2. **Opaque pricing & surprise/unauthorized charges** (Barn2Door: "charged my credit card 3 times without permission," "$3,700" renewal, "$50 surprise tax"). *Publish transparent ₪ pricing; no setup fees; easy self-cancel.*
3. **Per-transaction % fees resented** (Barn2Door 3.9%, Harvie 7%). *Flat subscription; never take a cut of grower sales.*
4. **Data hostage on cancellation** (GrowVeg loses historical plans; Farmbrite "no longer able to access… data"). *Guarantee export & post-cancel read access.*
5. **Beta bugs & instability** (Tend, Heirloom space-calc/seeder rounding). *Ship calculators with validated agronomic math; show the formula.*
6. **Clunky drawing/mapping tools & learning curve** (GrowVeg shape tools; Farmbrite setup). *Invest in fast bed/field layout; templates for standard 30-inch beds.*
7. **Poor performance on weak connectivity** (Croptracker "sluggish"; scanning fails). *Offline-first, low-bandwidth UI for rural Israel.*
8. **Accounting/POS integration gaps** (Farmbrite "no POS… invoicing separate from accounting"). *Plan clean accounting + Israeli payment/POS hooks early.*
9. **Feature overload / cluttered UI** (Croptracker "so many features… hide for cleaner interface"). *Role-based views; hide manager complexity from workers.*
10. **Tools force standardized workflows** (Croptracker "everything must be palletized… no mixed pallets"; Harvie rigidity). *Flexible models for the diversified micro-farm reality.*

## F. Recommendations for SFA
1. **Lead with the economics engine — the only true blue ocean.** Headline "what is most profitable to grow this season, in ₪ per bed-week, at current Israeli market prices." Wire the price index → expected-revenue → crop-profit-comparison calculators into Plan. No competitor does this; revenue-only projection (Tend, Heirloom) is the ceiling to beat.
2. **Own Hebrew/RTL as a moat, not a feature.** Build RTL-native from day one (farmOS Drupal i18n already supports RTL). Use LiteFarm's community-translation model as proof it scales, but keep Hebrew first-class.
3. **Make the morning cockpit the product.** A single role-based "today" screen unifying tasks (Execute), harvest→orders (Sell), and customer prefs (Relate) — split manager vs worker views (learn from AgriWebb's GPS/photo team tasks and LiteFarm's worker-autonomy task ordering). This is the "north star" no one has shipped.
4. **Adopt the proven calculator set and exceed it.** Match Heirloom/Tend's auto seed-list, in-row spacing, transplants-to-order, nursery tray/date, succession timing, yield projection, and **workload/labor prediction** — then add SFA's frost-window, fertilizer/compost, plant-population, and seed/input-cost calculators they lack. The 14-calculator suite is a credible feature-superset.
5. **Freemium funnel: free Hebrew home-grower tier → paid market-garden tier.** Mirror Tend/Seedtime's "free forever, no card" hook for community/brand-building; gate commercial features (sales, CRM, multi-user, economics depth) behind paid. Price the commercial tier at the ₪ equivalent of **~$25–$40/mo** to sit at category norm (Tend Pro $30, Farmbrite $29–$59) — undercut by being local + price-index-included.
6. **Flat, transparent pricing; never take a % of sales.** Explicitly avoid Barn2Door/Harvie's resented %+setup-fee model. Publish ₪ prices, self-serve signup, easy cancel — directly countering the category's #1 trust complaint.
7. **Offline-first in the field.** Expose farmOS Field Kit's offline PWA/native capability prominently; it neutralizes Tend's biggest weakness and serves low-connectivity rural areas.
8. **Guarantee data portability & post-cancel read access.** Turn GrowVeg/Farmbrite data-hostage complaints into a marketed promise ("your farm's data is always yours, always exportable") — reinforced by farmOS's open data model.
9. **Don't build standalone sales; integrate or templatize CSA/wholesale.** Local Line ($79+/mo, no Israel presence) and the Harvie shutdown show pure-sales is a hard, separate business. Bake lightweight Sell (price lists, CSA preference-matching à la Harvie's 1–5 crop rating, harvest→order) into the cockpit rather than competing head-on with e-commerce platforms.
10. **Borrow AgriWebb's gross-margin/cost-of-production model for crops.** AgriWebb's one-click COP and gross-margin reporting is the best economics pattern in the category — replicate it crop-side (per-bed, per-succession margin) and combine with the live price index for the predictive layer livestock tools lack.
11. **Schema fields likely missing — add to SFA's data model:** (a) **market-price time series** per crop/grade/channel (no competitor has it); (b) **cost components per planting** (seed, inputs, labor-hours, amendments) to compute true margin; (c) **bed-week / space-time occupancy** as the unit of profitability (₪ per bed-week); (d) **channel-specific price lists** (CSA/market/wholesale/restaurant) like Local Line; (e) **frost/microclimate window** per zone (GrowVeg-style weather-station calibration, localized to Israel); (f) **succession linkage & nursery container/tray attributes** (Heirloom-depth); (g) **role/permission split** (manager vs worker) on every entity; (h) **customer crop-preference ratings** (Harvie pattern) for the Relate/Sell loop.
12. **Position against the right competitor set in Israel: nobody.** Frame messaging as "the first farm OS built for the Israeli market gardener — in Hebrew, with Israeli prices." Global tools (Tend, Heirloom) are the feature benchmark; none localizes. Use their published weaknesses (offline gaps, beta bugs, no profit engine) as your differentiation checklist.

## Caveats
- **Pricing precision:** Tend and Farmbrite figures are from live vendor pages (high confidence), though **Tend's Ultimate tier conflicts** ($75/mo on tend.com vs $104.30/mo on Capterra 2026) — verify. **Heirloom's standalone per-farm price is undisclosed** (JS-gated); only the **course-bundled figures are public** (Masterclass Certificate $2,250 w/ 3 months; Certificate Plus $2,525 w/ 1 year; Pro Plan $3,950). AgriWebb ($45/$125/$200/$400) and Seedtime ($29/$49) are **third-party/dated** — confirm on vendor sites; AgriWebb has moved to baseline + per-head pricing. Croptracker's "$5.99/mo" and free-trial availability conflict across listings.
- **Reviews:** Quotes are paraphrased/kept short from G2, Capterra, GetApp, BBB, forums, and vendor sites; aggregator reviews can be incentivized — treated directionally.
- **Localization claims:** Farmbrite's "language support across 100+ countries" is vendor marketing; no Hebrew/RTL was specifically confirmed. Absence of Hebrew/RTL is asserted where no evidence was found, not from an exhaustive language audit.
- **Vendor metric inconsistency:** Local Line cites both "23%" and "33%" annual sales growth across pages — treat such figures as marketing.
- **Harvie** is discontinued (Dec 2024); included for pricing/CRM lessons only.
- **Marketing vs. fact:** "Make more profit" language (Heirloom, AgriWebb, Tend) is positioning; actual profit-decision tooling is weaker than the copy implies — the core finding that the economics-link white space is open rests on documented feature sets, not slogans.
- **farmOS/LiteFarm** are benchmarks, not competitors; their open-source nature and i18n/RTL capability directly support SFA's architecture choice.