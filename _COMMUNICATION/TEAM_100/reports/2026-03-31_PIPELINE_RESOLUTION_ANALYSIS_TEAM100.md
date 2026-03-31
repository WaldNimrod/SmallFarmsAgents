# Pipeline Resolution Rate — Analysis and Remediation Plan

**Author:** Team 100 (Architecture)
**Date:** 2026-03-31
**Mandate-ID:** ARCH-20260331-RESOLUTION-ANALYSIS
**Status:** ANALYSIS COMPLETE — awaiting Team 10 report before implementation

---

## 1. Baseline Metrics

| Metric | Value | Pct |
|--------|-------|-----|
| Total raw_extracted_items | 502 | 100% |
| `normalized` | 165 | 32.9% |
| `unresolvable` | 262 | 52.2% |
| `ignored` | 68 | 13.5% |
| `extracted` (stuck) | 7 | 1.4% |
| **Resolution rate** (norm / norm+unresolvable) | — | **38.6%** |

**Target:** Reduce unresolvable count by at least 50% (262 -> <=131).

---

## 2. Source-Level Breakdown

| Source | Total | Norm | Unresolvable | Ignored | Norm% |
|--------|-------|------|-------------|---------|-------|
| SRC002 (סבתא יהודית) | 94 | 76 | 11 | 0 | 80.9% |
| SRC003 (ח'ביזה) | 10 | 10 | 0 | 0 | 100% |
| SRC004 (קיימא בית זית) | 398 | 79 | 251 | 68 | 19.8% |

**Conclusion:** SRC004 drives 96% of all unresolvable items. SRC002 and SRC003 are healthy.

---

## 3. Root Cause Analysis

### 3.1 Missing Base Aliases (9 products)

Products that exist in the catalog but only have an "אורגני/אורגנית" alias.
SRC004 lists products WITHOUT the organic suffix, so the normalizer finds no match.

| Product ID | Canonical Name | Current Aliases | Missing Alias |
|------------|---------------|-----------------|---------------|
| PRD038 | לימון | `לימון אורגני` | `לימון` |
| PRD061 | תפוז | `תפוז אורגני` | `תפוז` |
| PRD054 | פפאיה | `פפאיה אורגנית` | `פפאיה` |
| PRD004 | פלפל ירוק | `פלפל חריף ירוק` | `פלפל ירוק` |
| PRD053 | פלפל רמירו | `פלפל רמירו אורגני` + 2 | `פלפל רמירו` |
| PRD036 | קולורבי | `קולורבי אורגני` | `קולורבי` |
| PRD040 | מנגולד | `מנגולד אורגני` + 1 | `מנגולד` |
| PRD050 | סלרי עלים | `סלרי עלים אורגני` + 1 | `סלרי עלים` |
| PRD056 | תפוח אדמה | `תפוח אדמה אורגני` + 2 | `תפוח אדמה` |

**Impact:** Directly resolves 9 SRC004 items.

### 3.2 Missing Variant Aliases (est. ~15 additional items)

SRC004 uses naming variants that don't match existing aliases:

| Raw Name (SRC004) | Should Map To | Product ID |
|--------------------|--------------|------------|
| `מנגולד צבעוני` | מנגולד | PRD040 |
| `דלעת יפנית-אייקידו` | דלעת | PRD037 |
| `מיקס נבטים` | נבטים | PRD033 |
| `מיקס נבטוטים` | נבטים | PRD033 |
| `תפוח עץ אדום - יבוא` | תפוח עץ | PRD042 |
| `תפוח עץ ירוק - ייבוא` | תפוח עץ | PRD042 |
| `תפוח עץ מוזהב - ייבוא` | תפוח עץ | PRD042 |
| `עלי בייבי` | עלי תרד | PRD009 |
| `ארגז ירקות מקומי` | סל ירקות בינוני | PRD026 |
| `ארגז ירקות קיימא` | סל ירקות גדול | PRD027 |
| `שורש כורכום` | כורכום טרי | PRD045 |
| `פול ירוק איטלקי` | אפונה טריה | PRD043 (or new) |
| `פטריות שמפיניון חומות` | NEW PRODUCT needed | — |
| `פטריות רעמת האריה` | NEW PRODUCT needed | — |

**Impact:** Est. ~13 items resolved to existing products + 2 items require new products.

### 3.3 New Products Needed (est. ~10 items across SRC002+SRC004)

Products that appear in multiple sources but don't exist in the catalog:

| Proposed Product | Sources | Items | Priority |
|-----------------|---------|-------|----------|
| שמיר | SRC002, SRC004 | 3 | HIGH — appears in 2 sources |
| פטריות | SRC002, SRC004 | 5 | HIGH — 3 variants in SRC002, 2 in SRC004 |
| רוזמרין | SRC004 | 1 | MEDIUM |
| נענע | SRC004 | 1 | MEDIUM |

**Impact:** ~10 items resolved.

### 3.4 Insufficient Scope-Skip Rules (est. ~160 items)

Only 13 scope-skip rules exist. SRC004 sells ~250 non-produce items that the normalizer attempts to resolve.

**Category analysis of SRC004's 251 unresolvable items:**

| Category | Count | Action |
|----------|-------|--------|
| Non-food (cleaning, cosmetics, candles, hygiene, tools) | ~57 | SCOPE-SKIP |
| Packaged grocery (pasta, flour, spices, condiments, etc.) | ~100 | SCOPE-SKIP |
| Beverages (juice, wine, cider, plant milk) | ~20 | SCOPE-SKIP |
| Snacks/baked (cookies, crackers, granola, halva) | ~25 | SCOPE-SKIP |
| Fresh produce (resolvable with aliases) | ~35 | ADD ALIASES |
| Ambiguous / edge cases | ~14 | REVIEW NEEDED |

### 3.5 Test Data Contamination

| Table | Test Rows | Real Rows |
|-------|-----------|-----------|
| `normalizer_rules` | 60 (100%) | 0 |
| `raw_extracted_items` (stuck extracted) | 7 | — |

All 60 normalizer rules are leftover test data (`m5-rule-*`, `m5-rd-*`).

---

## 4. Proposed Scope-Skip Rules

### 4.1 Non-Food Categories

| # | Category | Match | Pattern | Covers |
|---|----------|-------|---------|--------|
| 14 | cleaning | contains | `שמפו` | 10 items (shampoo) |
| 15 | cleaning | contains | `דאודורנט` | 2 items |
| 16 | cleaning | contains | `נר ריחני` | 4 items |
| 17 | cleaning | contains | `מברשו` | 2 items (toothbrush packs) |
| 18 | cleaning | contains | `נוזל כביסה` | 1 item |
| 19 | cleaning | contains | `נוזל כלים` | 4 items |
| 20 | cleaning | contains | `נוזל רצפות` | 1 item |
| 21 | cleaning | contains | `נוזל לניקוי` | 1 item |
| 22 | cleaning | contains | `מנקה` | 2 items |
| 23 | cleaning | contains | `מלבין` | 1 item |
| 24 | cleaning | contains | `מגבונים` | 2 items |
| 25 | cleaning | contains | `שפריצר` | 1 item |
| 26 | cleaning | contains | `מסיר שומנים` | 1 item |
| 27 | cleaning | contains | `ג'ל כביסה` | 2 items |
| 28 | cleaning | contains | `קפסולות אקולוגי` | 1 item |
| 29 | cleaning | contains | `אבקת הלבנה` | 1 item |
| 30 | cosmetics | contains | `קרם גוף` | 1 item |
| 31 | cosmetics | contains | `חמאת גוף` | 1 item |
| 32 | cosmetics | contains | `מסיכת פנים` | 1 item |
| 33 | cosmetics | contains | `מסכה` | 1 item |
| 34 | cosmetics | contains | `מסכת הזנה` | 1 item |
| 35 | cosmetics | contains | `שמן אתרי` | 1 item |
| 36 | cosmetics | contains | `מרכך הדרים` | 2 items (hair conditioner) |
| 37 | cosmetics | contains | `צנדריקה` | 1 item |
| 38 | other | contains | `תחבושות` | 1 item |
| 39 | other | contains | `ספיגה` | 2 items (pads) |
| 40 | other | contains | `גביעונית` | 1 item |
| 41 | other | contains | `כלי השרשה` | 1 item |
| 42 | other | contains | `קנקן` | 1 item |
| 43 | other | contains | `תבנית` | 1 item |
| 44 | other | contains | `קש מק` | 2 items (straws) |
| 45 | other | contains | `מנבטה` | 1 item |
| 46 | other | contains | `שתילי` | 1 item |
| 47 | other | exact | `טיפ לשליח` | 1 item |
| 48 | other | exact | `אם נדע לבקש חיים` | 1 item (book) |
| 49 | other | exact | `צמחי בר למאכל` | 1 item (book/workshop) |
| 50 | other | contains | `Botany` | 3 items |
| 51 | other | contains | `ערכת` | 1 item (gift set) |
| 52 | other | contains | `מארז חיסכון` | 1 item |
| 53 | other | contains | `מארז 5 מברשות` | 1 item |

**Subtotal non-food: ~57 items**

### 4.2 Packaged Grocery Categories (outside V1 fresh-produce scope)

| # | Category | Match | Pattern | Est. Items |
|---|----------|-------|---------|-----------|
| 54 | dry_grocery | contains | `קמח` | 9 items |
| 55 | dry_grocery | contains | `פסטה` | 4 items |
| 56 | dry_grocery | contains | `קוסקוס` | 2 items |
| 57 | dry_grocery | contains | `בורגול` | 1 item |
| 58 | dry_grocery | contains | `קינואה` | 3 items |
| 59 | dry_grocery | contains | `כוסמת` | 1 item |
| 60 | dry_grocery | contains | `קוואקר` | 4 items |
| 61 | dry_grocery | contains | `עדשים` | 5 items |
| 62 | dry_grocery | contains | `חומוס אורגני` | 1 item |
| 63 | dry_grocery | contains | `פולי אזוקי` | 1 item |
| 64 | dry_grocery | contains | `אפונה ירוקה יבשה` | 1 item |
| 65 | dry_grocery | contains | `גריסי פנינה` | 1 item |
| 66 | dry_grocery | contains | `חומץ` | 5 items |
| 67 | dry_grocery | contains | `חרדל` | 2 items |
| 68 | dry_grocery | contains | `מיונז` | 1 item |
| 69 | dry_grocery | contains | `טחינה` | 2 items |
| 70 | dry_grocery | contains | `ממרח` | 5 items |
| 71 | dry_grocery | contains | `סילאן` | 2 items (SRC002+SRC004) |
| 72 | dry_grocery | contains | `סירופ מייפל` | 2 items |
| 73 | dry_grocery | contains | `דיבס` | 1 item |
| 74 | dry_grocery | contains | `שמן זית` | 4 items (SRC002+SRC004) |
| 75 | dry_grocery | contains | `שמן קוקוס` | 1 item |
| 76 | dry_grocery | contains | `עוגיות` | 5 items |
| 77 | dry_grocery | contains | `ביסקוטי` | 1 item |
| 78 | dry_grocery | contains | `גרנולה` | 1 item |
| 79 | dry_grocery | contains | `קרקר` | 5 items |
| 80 | dry_grocery | contains | `קריספיס` | 1 item |
| 81 | dry_grocery | contains | `וופל` | 1 item |
| 82 | dry_grocery | contains | `חטיף` | 3 items |
| 83 | dry_grocery | contains | `כדורי חלבה` | 2 items |
| 84 | dry_grocery | contains | `מלח` | 5 items (SRC002+SRC004) |
| 85 | dry_grocery | contains | `פפריקה מתוקה` | 1 item |
| 86 | dry_grocery | contains | `פלפל שחור` | 2 items |
| 87 | dry_grocery | contains | `קינמון` | 2 items |
| 88 | dry_grocery | contains | `כמון` | 1 item |
| 89 | dry_grocery | contains | `קארי` | 1 item |
| 90 | dry_grocery | contains | `אבקת חרוב` | 1 item |
| 91 | dry_grocery | contains | `סוכר` | 2 items |
| 92 | dry_grocery | contains | `מקריש` | 1 item |
| 93 | dry_grocery | contains | `אגוז` | 4 items |
| 94 | dry_grocery | contains | `שקד` | 3 items |
| 95 | dry_grocery | contains | `פקאן` | 1 item |
| 96 | dry_grocery | contains | `גרעיני` | 2 items |
| 97 | dry_grocery | contains | `חמוציות` | 1 item |
| 98 | dry_grocery | contains | `צנובר` | 1 item |
| 99 | dry_grocery | contains | `פרג` | 1 item |
| 100 | dry_grocery | contains | `דבש` | 2 items |
| 101 | dry_grocery | contains | `קוקוס טחון` | 1 item |
| 102 | dry_grocery | contains | `רצועות קוקוס` | 1 item |
| 103 | dry_grocery | contains | `נוזל קוקוס` | 2 items |
| 104 | dry_grocery | contains | `קרם קוקוס` | 1 item |
| 105 | dry_grocery | contains | `קרם אגוז` | 1 item |
| 106 | dry_grocery | contains | `יין ` | 3 items |
| 107 | dry_grocery | contains | `סיידר` | 4 items |
| 108 | dry_grocery | contains | `משקה ` | 3 items |
| 109 | dry_grocery | contains | `מיץ` | 5 items |
| 110 | dry_grocery | contains | `סמוצ'י` | 8 items |
| 111 | dry_grocery | contains | `סמוזי` | 1 item |
| 112 | dry_grocery | contains | `תה ` | 7 items |
| 113 | dry_grocery | contains | `דפי לזניה` | 1 item |
| 114 | dry_grocery | contains | `מקרוני` | 1 item |
| 115 | dry_grocery | contains | `פוזילי` | 1 item |
| 116 | dry_grocery | contains | `כפיתה` | 1 item |
| 117 | dry_grocery | contains | `קורנישונים` | 1 item |
| 118 | dry_grocery | contains | `ארטישוק בסגנון` | 1 item (preserved) |
| 119 | dry_grocery | contains | `זיתי` | 1 item |
| 120 | dry_grocery | contains | `סודה` | 1 item |
| 121 | dry_grocery | contains | `אבקת שמרי` | 1 item |
| 122 | dry_grocery | contains | `מיקס לונדון` | 1 item (nut mix) |
| 123 | dry_grocery | contains | `הולי נאטס` | 1 item |
| 124 | dry_grocery | contains | `חמאת בוטנים` | 1 item |
| 125 | dry_grocery | contains | `מארז שמן` | 1 item |
| 126 | dry_grocery | contains | `מקלות קינמון` | 1 item |
| 127 | dry_grocery | contains | `אזוב טחון` | 1 item |
| 128 | dry_grocery | contains | `כורכום טחון` | 1 item |
| 129 | other | exact | `לא משמינים מאוכל` | 1 item (SRC002, book) |
| 130 | other | exact | `לוח שנה בגינה` | 1 item (SRC002, book) |
| 131 | other | exact | `ערמונים קלופים אורגנים` | 1 item (SRC002, preserved) |
| 132 | dry_grocery | contains | `תפוח עץ טבעי מיובש` | 1 item (dried, not fresh) |
| 133 | dry_grocery | contains | `תבואות` | 6 items |

**Subtotal packaged grocery: ~110 items**

> **Note:** Some patterns overlap (e.g., `תבואות` would catch items also matched by `עדשים`). The first matching rule wins. Estimated unique catch after deduplication: ~100 items.

---

## 5. SRC002 Unresolvable Items — Individual Resolution

| # | Raw Name | Price | Recommended Action |
|---|----------|-------|-------------------|
| 1 | `שמיר אורגני` | ₪8.00/יח' | ADD new product "שמיר" + alias |
| 2 | `2 חב' שמיר אורגני ב- 1` | ₪14.00/יח' | ADD alias to שמיר (after creation) |
| 3 | `שמן זית אורגני` | ₪50.50/יח' | SCOPE-SKIP dry_grocery (rule #74 covers) |
| 4 | `פטריות פורטבלו אורגניו` | ₪85.00/ק"ג | ADD new product "פטריות" + alias |
| 5 | `פטריות שיטאקי אורגני` | ₪85.00/ק"ג | ADD alias to פטריות |
| 6 | `פטריות שמפניון אורגניו` | ₪85.00/ק"ג | ADD alias to פטריות |
| 7 | `סילאן אורגני` | ₪28.50/יח' | SCOPE-SKIP dry_grocery (rule #71 covers) |
| 8 | `מלח אטלנטי אפור לח` | ₪22.90/יח' | SCOPE-SKIP dry_grocery (rule #84 covers) |
| 9 | `ערמונים קלופים אורגנים` | ₪11.00/יח' | SCOPE-SKIP other (rule #131) |
| 10 | `לא משמינים מאוכל` | ₪68.00/יח' | SCOPE-SKIP other (rule #129, book) |
| 11 | `לוח שנה בגינה` | ₪84.00/יח' | SCOPE-SKIP other (rule #130, book) |

**Result:** 11 → 0 unresolvable in SRC002.

---

## 6. Impact Estimate

| Action | Items Resolved | Items to Ignored |
|--------|---------------|-----------------|
| Base aliases (9 products) | 9 | — |
| Variant aliases (existing products) | ~13 | — |
| New products + aliases (שמיר, פטריות, etc.) | ~10 | — |
| Scope-skip: non-food | — | ~57 |
| Scope-skip: packaged grocery | — | ~100 |
| Scope-skip: SRC002 non-produce | — | ~5 |
| **Total** | **~32** | **~162** |

**Projected after-state:**

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Normalized | 165 | ~197 | +32 |
| Unresolvable | 262 | ~68 | **-194 (-74%)** |
| Ignored | 68 | ~230 | +162 |
| Resolution rate | 38.6% | **~74%** | +35pp |

**Target of 50% reduction: EXCEEDED (projected 74% reduction)**

---

## 7. Implementation Sequence

### Step 1: Cleanup (prerequisite)
- Delete 60 test `normalizer_rules`
- Mark 7 stuck `extracted` items as `ignored`

### Step 2: Scope-Skip Rules (migration or admin)
- Insert ~80 new `catalog_scope_skip_rules` rows (consolidated from the ~120 patterns above — many can be merged using broader patterns)
- Requires: migration script or admin CRUD (admin is currently read-only for scope-skip)

### Step 3: Add Missing Aliases
- Insert ~9 base aliases (canonical names without אורגני)
- Insert ~15 variant aliases

### Step 4: Add New Products
- Create products: שמיר, פטריות, רוזמרין, נענע
- Create their aliases

### Step 5: Admin UI Enhancement
- Add create/edit/delete for `catalog_scope_skip_rules` in admin
- This enables ongoing maintenance without migrations

### Step 6: Reset + Re-run
- UPDATE `raw_extracted_items` SET `extraction_status='extracted'` WHERE `extraction_status='unresolvable'`
- Run normalizer
- Measure

### Step 7: Verify
- Compare before/after metrics
- Confirm target met

---

## 8. Dependencies

- **Team 10** is currently working on fixes; their completion report is pending
- Implementation should wait for Team 10's report to avoid conflicting changes
- Steps 2-4 can be implemented as a single migration or via admin UI + SQL script
- Step 5 (admin CRUD) is optional but strongly recommended for ongoing maintenance

---

## 9. Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| Overly broad scope-skip catches fresh produce | Each pattern was reviewed item-by-item against actual data |
| `יין` pattern catches "יין" in product names | Uses trailing space: `יין ` (with space) |
| `מלח` catches `מלח ים` food items | Acceptable — all salt items are packaged, outside V1 scope |
| `אגוז` catches future nut products | Can be refined later if nuts enter V1 scope |
| New aliases create false matches | All aliases verified against exact SRC004 raw names |

---

**Signature:** Team 100 (Architecture)
**Date:** 2026-03-31
**Sign-off ID:** ARCH-20260331-RESOLUTION-ANALYSIS
