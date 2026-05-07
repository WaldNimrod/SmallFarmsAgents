# MyPIPS.app Source Onboarding Spike — Technical Assessment

**Date:** 2026-04-04  
**Spike Author:** Team 10 (Feature Dev)  
**Platform:** mypips.app  
**Scope:** 6 store URLs + platform analysis

---

## 1. Platform Overview: What is mypips.app?

**MyPips** is an **Israeli SaaS ordering platform** for independent and community businesses
("מערכת ההזמנות של העסקים העצמאיים והקהילתיים בישראל"). It provides small farms, producers,
and buying groups with branded storefront pages where customers can browse products, place
orders, and pay online.

### Technical Architecture

| Component | Detail |
|---|---|
| **Frontend** | React SPA (not Next.js), MaterializeCSS 0.98 + jQuery 3.6 |
| **Backend** | Firebase / Firestore (project: `plantonic-eco`) |
| **Storage** | Firebase Storage (`plantonic-eco.appspot.com`) |
| **Auth** | Firebase Auth (phone, email/password, Google — anonymous auth DISABLED) |
| **Analytics** | Google Analytics (`G-TJVLV2KR4W`) + Intercom |
| **Payment** | Cardcom (credit card clearing company) |
| **Bundle** | `/static/js/main.e517dfe9.js` (1.66 MB), version `1.139.3` |
| **API Key** | `AIzaSyB_TlgEShaTgAEV9mulKZAjveQgDbO4bGg` (public, in bundle) |

### Data Access Pattern

- **Store metadata:** Server-rendered in `window._INITIAL_STORE_DATA_` (embedded JSON in HTML).
  Accessible via plain `curl`/`httpx` — no JS needed.
- **Product catalog:** Loaded **dynamically** by Firestore client SDK after SPA renders.
  **Requires headless browser** (Playwright). Firestore REST API returns `PERMISSION_DENIED`
  for product subcollections. Anonymous auth is disabled.
- **URL pattern:** `https://mypips.app/{handle}/products` — shows full product catalog.

---

## 2. Per-Source Assessment

### 2.1 fruit4soul — השחקן שהפך לירקן

| Field | Value |
|---|---|
| **URL** | `https://mypips.app/fruit4soul` |
| **HTTP Status** | 200 |
| **Page Size** | 18,981 bytes (HTML shell) |
| **Store ID** | `Zey1TVUVqXnvR1lpPIva` |
| **Store Name** | השחקן שהפך לירקן (The Actor Who Became a Greengrocer) |
| **Active** | Yes |
| **Taking Orders** | **No** (currently closed) |
| **Product Count** | **217 products in 4 categories** |
| **Organic Flag** | `includeOrganic: false` (but has "אורגני בפיקוח 🌱" category) |
| **Categories** | פירות, ירקות, ירק ועשבי תיבול, מוצרי מזווה, אורגני בפיקוח, and more |
| **Order Cycle** | Always (rolling) |
| **Payment** | Credit card (Cardcom) |
| **Category** | **Distributor / CSA** (מפיץ) — works with 25+ farms nationwide |
| **JS Rendering** | **Required** (Firestore SPA) |

**Sample Products (from browser rendering):**

| Product Name | Price | Supplier |
|---|---|---|
| אננס קטן יח' כ 400-500 גר' | ₪17 | אלפרוביץ' |
| אננס ישראלי בינוני יח' כ 0.8-1 קג | ₪35 | אלפרוביץ' |
| 500 גרם תות שדה! גידול BIO | ₪18 | — |
| תות שדה "בונבוניירה" משק 6, גידול BIO, 500 גרם | ₪30 | משק 6 מושב גאולים |
| תות שדה אורגני, מארז 250 גרם | ₪30 | משק 6 |
| תות טרופית בטעם ענבים, מארז 300 גרם | ₪30 | משק 6 מושב גאולים |
| תות לבן ביו, מארז 300 גר' | ₪30 | משק 6 מושב גאולים |

**Product Attributes:** אורגני בפיקוח, ללא ריסוס ישיר, מעושר, תוצרת ישראלית, גידול עצמי,
הדברה ביולוגית BIO, חקלאות בת קיימא, מופחת ריסוס

**Scraping Feasibility:** **HIGH** — large catalog of fruits/vegetables with per-unit prices,
supplier attribution, organic tags. Periodically closed for orders but catalog remains visible.

---

### 2.2 mypips — מייפיפס | MyPips

| Field | Value |
|---|---|
| **URL** | `https://mypips.app/mypips` |
| **HTTP Status** | 200 |
| **Page Size** | 8,076 bytes |
| **Store ID** | `CHAyz2M9F3LwwZoXlVKw` |
| **Store Name** | מייפיפס \| MyPips |
| **Categories** | מסלולים חודשיים, עמלות בהתאם לשימוש, חבילות הודעות, פתרונות שקילה |
| **Category** | **NOT A PRODUCE SELLER** — this is the MyPips company's own subscription store |

**Scraping Feasibility:** **NOT_VIABLE** — sells SaaS subscriptions, not produce.

---

### 2.3 thelab — המעבדה

| Field | Value |
|---|---|
| **URL** | `https://mypips.app/thelab` |
| **HTTP Status** | 200 |
| **Page Size** | 16,569 bytes |
| **Store ID** | `CMz5QrWJHjtAs7ALJk1L` |
| **Store Name** | המעבדה (The Lab) |
| **Active** | Yes |
| **Taking Orders** | Yes |
| **Organic Flag** | false |
| **Categories** | גבינות שמנת, גבינות שקדים אפויות, גבינות גליל, יוגורטים, גבינות מיושנות, מיוחדים |
| **Category** | **Artisan vegan cheese maker** (חנות מוצרי מזון טבעוניים) |

**Scraping Feasibility:** **NOT_VIABLE** — vegan cheese/dairy alternatives, not fresh produce.
Out of scope for organic vegetable price index.

---

### 2.4 anatiyot — הענתיות

| Field | Value |
|---|---|
| **URL** | `https://mypips.app/anatiyot` |
| **HTTP Status** | 200 |
| **Page Size** | 15,975 bytes |
| **Store ID** | `CUFqc8TFHKM7HaQNYrrH` |
| **Store Name** | הענתיות (The Anats) |
| **Active** | Yes |
| **Taking Orders** | **Yes** |
| **Organic Flag** | **true** |
| **Product Count** | 25 categories |
| **Tags** | `['group']` — this is a **buying group / CSA**, not a store |
| **Categories** | פירות, ירקות, עלים ירוקים, נבטים ופטריות, אגוזים ומיובשים, המזווה, שמנים/תבלינים/חליטות |
| **Order Cycle** | **Weekly** (Sun 18:00 → Mon 20:00) |
| **Payment** | Credit card |
| **Description** | Fruit specialists since 2014, direct buying from farmers |
| **Category** | **CSA / Buying Group** (קבוצת רכישה) |

**Product Attributes:** ללא הדברה כימית, אורגני בפיקוח אגריאור, אורגני בפיקוח IQC,
הדברה ביולוגית BIO, ללא ריסוס ישיר

**Scraping Feasibility:** **HIGH** — weekly fresh produce with organic certification,
large category spread, actively taking orders. `includeOrganic: true` is the ONLY store
with this flag. Has own website too: `anatiyot.com`.

---

### 2.5 mashtelatharoe — משתלת הראה

| Field | Value |
|---|---|
| **URL** | `https://mypips.app/mashtelatharoe` |
| **HTTP Status** | 200 |
| **Page Size** | 10,776 bytes |
| **Store ID** | `UrfVezdFWrauwqv584rs` |
| **Store Name** | משלוחי ירקות ופירות - טריים מהשדה לצרכן |
| **Active** | Yes |
| **Taking Orders** | **Yes** |
| **Product Count** | **307 products in 14 categories** |
| **Organic Flag** | false (but has organic products in catalog) |
| **Categories** | פירות, ירקות, ירוקים, מיצים סחוטים, אגוזים ויבשים, מוצרים, מוצרי משתלה, סלים שבועיים |
| **Order Cycle** | **Weekly** (Sun 07:00 → Wed 15:00) |
| **Payment** | Bank transfer, credit card |
| **Description** | Nursery growing unsprayed vegetables and fruit, selling direct without middlemen |
| **Category** | **Farm / Nursery** (משתלה / משק) — grower |

**Sample Products (from browser rendering):**

| Product Name | Price | Supplier |
|---|---|---|
| תפוז טבורי (Navel Orange) | ₪6 | משתלת הראה |
| לימון צהוב (Yellow Lemon) | ₪7 | משתלת הראה |
| פומלית אדומה (Red Pomelo) | ₪6 | משתלת הראה |
| פומלית לבנה (White Pomelo) | ₪6 | משתלת הראה |
| פומלה אדומה (Red Pomelo) | ₪7 | — |
| לימון קוויאר (Finger Lime) | ₪32 | — |
| אבטיח (Watermelon) | ₪7 | משתלת הראה |

**Product Attributes:** ללא דונג, ללא דשן כימי, ללא הדברה כימית, ללא חשש ערלה, מעושר,
אורגני בפיקוח, אורגני ללא פיקוח, מופחת ריסוס

**Scraping Feasibility:** **HIGH** — largest catalog (307 products), actively selling,
direct farmer prices, multiple produce categories. Highest data volume potential.

---

### 2.6 finerotem — משק רתם פיין

| Field | Value |
|---|---|
| **URL** | `https://mypips.app/finerotem` |
| **HTTP Status** | 200 |
| **Page Size** | 13,363 bytes |
| **Store ID** | `GWBKJuxnk2kwoAjWn8P3` |
| **Store Name** | משק רתם פיין בנימינה (Rotem Fine Farm, Binyamina) |
| **Active** | Yes |
| **Taking Orders** | **No** (currently closed) |
| **Organic Flag** | false |
| **Categories** | מארזים מהטבע, פירות, ירקות, ירוקים, שמן זית ויינות בוטיק, דבש/ממרחים/רטבים, מאפים/לחם |
| **Order Cycle** | Always (rolling) |
| **Payment** | Credit card |
| **Description** | 6th generation Israeli farming family in Binyamina, farmer-to-consumer |
| **Category** | **Farm** (משק) — grower, 6th generation |

**Product Attributes:** ללא ריסוס ישיר, מעושר, גידול עצמי, ללא חשש ערלה, כשר

**Scraping Feasibility:** **MEDIUM** — genuine farm with produce categories, but currently
closed for orders (catalog may not be visible). When active, high-value family farm data.

---

## 3. Technical Scraping Architecture

### 3.1 What Works

| Layer | Method | Data Available |
|---|---|---|
| **Store metadata** | `httpx` GET → parse `window._INITIAL_STORE_DATA_` | Store name, categories, organic flag, order status, delivery options, product attributes list |
| **Product catalog** | **Playwright** headless browser → render SPA → extract DOM | Product name, price (₪), supplier/farm name, product attributes, category |

### 3.2 CSS Selectors (from rendered DOM)

| Element | Selector Pattern |
|---|---|
| Product name | `h6` heading within product card |
| Price | `h5` heading with `₪` prefix |
| Supplier name | Text element below product name |
| Product attributes | Tag/chip elements within product card |
| Category header | `h5` heading at category section top |
| Category tabs | `[role="tab"]` elements |

### 3.3 Recommended Collector Architecture

```
platform_family: mypips
scraper_type: playwright (headless browser required)
```

**Phase A — Metadata (httpx, no browser needed):**
1. `GET https://mypips.app/{handle}` 
2. Parse `window._INITIAL_STORE_DATA_` from HTML
3. Extract: store name, categories, active/takingOrders status, organic flag
4. Use as gate: skip stores not taking orders or with irrelevant categories

**Phase B — Products (Playwright):**
1. Navigate to `https://mypips.app/{handle}/products`
2. Wait for Firestore data load (~5-8s)
3. Dismiss welcome popup if present (click "אוקיי" button)
4. Scroll through all categories to lazy-load products
5. Extract product cards from rendered DOM
6. Parse: name, price, supplier, attributes, category

### 3.4 Key Challenges

| Challenge | Mitigation |
|---|---|
| SPA requires JS rendering | Use Playwright headless browser |
| Welcome popup blocks interaction | Auto-dismiss by clicking "אוקיי" |
| Products lazy-loaded per category | Scroll/click through all category tabs |
| Firestore auth required for API | Browser handles auth transparently |
| Stores may be closed for orders | Catalog still visible when closed; metadata check first |
| No REST API for products | Browser-only approach; intercept Firestore traffic as fallback |

---

## 4. Summary Matrix

| Handle | Store Name | Type | Produce? | Products | Active Orders | Organic | Feasibility |
|---|---|---|---|---|---|---|---|
| `fruit4soul` | השחקן שהפך לירקן | Distributor | **Yes** | 217 | No (periodic) | Partial | **HIGH** |
| `mypips` | מייפיפס \| MyPips | SaaS vendor | No | — | Yes | No | **NOT_VIABLE** |
| `thelab` | המעבדה | Vegan cheese | No | — | Yes | No | **NOT_VIABLE** |
| `anatiyot` | הענתיות | CSA / Group | **Yes** | 25+ cats | **Yes** | **Yes** | **HIGH** |
| `mashtelatharoe` | משתלת הראה | Farm/Nursery | **Yes** | 307 | **Yes** | Partial | **HIGH** |
| `finerotem` | משק רתם פיין | Farm | **Yes** | 11 cats | No (periodic) | Partial | **MEDIUM** |

### Recommended for Onboarding (Priority Order)

1. **mashtelatharoe** — largest catalog (307), actively selling, direct farm prices, multiple produce categories
2. **anatiyot** — only `includeOrganic: true` store, CSA/buying group, weekly cycle, certified organic
3. **fruit4soul** — large catalog (217), multi-farm distributor with organic category, currently closed
4. **finerotem** — genuine family farm, currently closed but valuable when active

### Not Viable

- **mypips** — SaaS subscription store, not produce
- **thelab** — vegan cheese maker, not produce

---

## 5. Firestore Store IDs

| Handle | Firestore Document ID |
|---|---|
| `fruit4soul` | `Zey1TVUVqXnvR1lpPIva` |
| `mypips` | `CHAyz2M9F3LwwZoXlVKw` |
| `thelab` | `CMz5QrWJHjtAs7ALJk1L` |
| `anatiyot` | `CUFqc8TFHKM7HaQNYrrH` |
| `mashtelatharoe` | `UrfVezdFWrauwqv584rs` |
| `finerotem` | `GWBKJuxnk2kwoAjWn8P3` |

Firestore path: `groups/{storeId}` (collection name is `groups`, not `stores`)

---

## 6. Discovery Potential

MyPips is a **platform** hosting many stores. The main page (`https://mypips.app/`) and
the merchants page (`https://mypips.info/merchants`) may list additional produce sellers
beyond these 6. A discovery script could:

1. Scrape the merchants listing page for all store handles
2. Fetch metadata for each via `window._INITIAL_STORE_DATA_`
3. Filter by categories containing produce terms (פירות, ירקות, ירוקים, אורגני)
4. Auto-identify viable sources for the price index

This makes mypips a **scalable source platform** — one collector implementation serves
multiple sources through parameterized store handles.
