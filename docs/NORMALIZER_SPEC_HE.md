# מפרט מנגנון Normalizer — SmallFarms Market Data System

גרסה: 1.0  
תאריך: 2026-03-29

---

## 1. עיקרון יסוד

המנגנון הוא **data-driven לחלוטין** — כל חוקי הנרמול, aliases, merges ו-flags נשמרים בטבלאות PostgreSQL.

**תוצאה מעשית:**
- admin / agent יכול לשנות חוק normalizer ב-DB ללא deploy
- שינויים גורמים לתוצאה שונה בריצה הבאה
- כל שינוי נרשם ב-`audit_log`
- אפשר לבדוק "מה היה יוצא אם החוק היה אחרת" על raw היסטורי

---

## 2. ארכיטקטורת המנגנון

```
raw_extracted_item
        │
        ▼
┌─────────────────────────────┐
│   NormalizerEngine          │
│                             │
│  1. load_rules(source_id)   │  ← מ-DB, per-run cache
│  2. resolve_product()       │  alias matching
│  3. resolve_unit()          │  unit_conversions
│  4. resolve_price()         │  המרה + correction
│  5. resolve_organic_flag()  │  מקור + rules
│  6. calc_confidence()       │  multi-factor
│  7. apply_observation_flags()  ← DB flags
└─────────────────────────────┘
        │
        ▼
normalized_observation
```

---

## 3. שלבי הנרמול

### 3.1 שלב 1 — טעינת Rules

בתחילת כל ingestion run, המנגנון טוען מ-DB:

```python
def load_rules_for_source(source_id: int) -> NormalizerRuleSet:
    """
    טוען:
    - normalizer_profile של המקור
    - normalizer_rules לפי priority ASC
    - product_aliases (גלובלי + ספציפי למקור)
    - observation_flags פעילים
    - unit_conversions
    
    מאחסן ב-memory לכל משך ה-run (לא query per item).
    """
```

**מבנה RuleSet בזיכרון:**

```python
@dataclass
class NormalizerRuleSet:
    profile: NormalizerProfile
    rules: list[NormalizerRule]           # ממוינים לפי priority
    aliases: dict[str, ProductAlias]      # key: alias_text_normalized
    observation_flags: list[ObservationFlag]
    unit_conversions: dict[tuple, UnitConversion]  # key: (from_code, to_code)
```

---

### 3.2 שלב 2 — Resolve Product (alias matching)

**אלגוריתם:**

```python
def resolve_product(raw_name: str, ruleset: NormalizerRuleSet) -> ProductMatch | None:
    """
    1. normalize_text(raw_name):
       - lowercase
       - strip whitespace
       - הסרת תוכן בסוגריים: "עגבנייה (אדומה)" → "עגבנייה"
       - הסרת יחידות נפוצות: "עגבנייה ק\"ג" → "עגבנייה"
       - הסרת מילות מפתח: "ירק", "טרי", "עונתי"
    
    2. בדוק product_alias ספציפי למקור (source_id=X) לפי normalized text
       → exact match → return ProductMatch(confidence=alias.confidence)
    
    3. בדוק product_alias גלובלי (source_id=NULL) לפי normalized text
       → exact match → return ProductMatch(confidence=alias.confidence * 0.95)
    
    4. בדוק normalizer_rules מסוג 'product_alias' לפי priority:
       - match_type='exact': השוואה ישירה
       - match_type='contains': raw_name contains pattern
       - match_type='regex': re.search(pattern, raw_name)
       → match → return ProductMatch(confidence=rule_confidence)
    
    5. לא נמצא → return None (פריט יסומן 'unresolvable')
    """
```

**דוגמת Rule בDB:**

```sql
INSERT INTO normalizer_rules (normalizer_profile_id, rule_kind, match_type,
    match_pattern, replacement_value, priority, notes)
VALUES (
    1, 'product_alias', 'regex',
    '^עגבניה?[^שרי]*$',  -- עגבנייה/עגבניה שאינה שרי
    'PRD001',             -- product code
    10,
    'עגבנייה רגילה'
);
```

---

### 3.3 שלב 3 — Resolve Unit

```python
def resolve_unit(
    raw_unit_text: str,
    raw_price_text: str,
    raw_quantity_text: str,
    product: Product,
    ruleset: NormalizerRuleSet
) -> UnitResolution:
    """
    1. normalize raw_unit_text:
       - 'קג', 'ק"ג', 'kg', 'קילו' → 'kg'
       - 'יחידה', 'יח\'', 'ראש' → 'unit'
       - 'צרור', 'חבילה קטנה' → 'bunch'
       - 'מארז 500', '500 גרם' → 'pack_500g'
       - 'סל', 'ארגז' → infer basket type
    
    2. בדוק normalizer_rules מסוג 'unit_map':
       match_pattern: text גולמי
       replacement_value: unit code
    
    3. בדוק normalizer_rules מסוג 'quantity_parse':
       לחלץ כמות מהטקסט: "2 ק\"ג" → quantity=2, unit='kg'
    
    4. אם לא נמצא → unresolvable_reason='no_unit'
    
    Returns:
        UnitResolution(
            display_unit_code,
            normalized_unit_code,  # תמיד 'kg' אם ניתן להמרה
            factor,                # לחישוב מחיר לק"ג
            method,                # 'exact'/'heuristic'/'unresolvable'
            confidence_impact      # מורידים confidence אם heuristic
        )
    """
```

**טבלת מיפוי ראשונית (normalizer_rules סוג unit_map):**

| match_pattern | replacement_value | match_type |
|---|---|---|
| ק"ג | kg | exact |
| קג | kg | exact |
| קילו | kg | contains |
| kg | kg | exact |
| גרם | g | exact |
| יחידה | unit | exact |
| יח' | unit | exact |
| ראש | unit | exact |
| צרור | bunch | exact |
| חבילה | bunch | contains |
| מארז 250 | pack_250g | contains |
| מארז 500 | pack_500g | contains |
| 500 גרם | pack_500g | exact |
| 250 גרם | pack_250g | exact |
| סל קטן | basket_small | contains |
| סל בינוני | basket_medium | contains |
| סל גדול | basket_large | contains |
| ארגז שבועי | basket_medium | contains |

---

### 3.4 שלב 4 — Resolve Price

```python
def resolve_price(
    raw_price_text: str,
    display_unit: str,
    normalized_unit: str,
    conversion_factor: float,
    ruleset: NormalizerRuleSet
) -> PriceResolution:
    """
    1. parse raw_price_text:
       - הסרת תווים: '₪', 'ש"ח', ',', spaces
       - regex: r'(\d+\.?\d*)' → float
       - טיפול בטווחים: '12-15' → avg(12, 15)
    
    2. בדוק normalizer_rules מסוג 'price_correction':
       לתיקון שגיאות מחיר ידועות (למשל מקור שמציג מחיר ל-100 גרם)
       match_pattern: source_id pattern
       replacement_value: json עם הוראת תיקון
    
    3. חשב normalized_price_value:
       אם display_unit == normalized_unit: price = raw_price
       אחרת: price = raw_price * conversion_factor
       
       דוגמה: raw=5.00 ILS, unit=pack_500g, factor=2.0 (לק"ג) → 10.00 ILS/kg
    
    Returns:
        PriceResolution(
            price_amount,           # כפי שהוצג
            normalized_price_value, # לק"ג; None אם לא ניתן
            currency_code,          # 'ILS'
            method
        )
    """
```

---

### 3.5 שלב 5 — Organic Flag

```python
def resolve_organic_flag(
    raw_product_name: str,
    raw_payload: dict,
    source: Source,
    ruleset: NormalizerRuleSet
) -> bool:
    """
    1. אם source.market_scope == 'community' → True כברירת מחדל
       (כל המקורות הקהילתיים נחשבים אורגניים לV1)
    
    2. בדוק normalizer_rules מסוג 'organic_flag':
       - True patterns: 'אורגני', 'organic', 'ביו', 'IQC', 'סקאל'
       - False patterns: 'קונבנציונלי', 'לא אורגני'
    
    3. אם source.market_scope == 'benchmark' → False כברירת מחדל
    
    Returns: bool
    """
```

---

### 3.6 שלב 6 — חישוב Confidence Score

```python
def calculate_confidence(
    product_match: ProductMatch,
    unit_resolution: UnitResolution,
    price_resolution: PriceResolution,
    source: Source
) -> float:
    """
    נקודת התחלה: 1.0
    
    הפחתות:
    - product מ-rule (לא alias ישיר): -0.05
    - product מ-regex (לא exact): -0.05
    - unit resolution = heuristic: -0.10
    - price מ-טווח (ממוצע): -0.05
    - price_correction הופעל: -0.10
    - source.priority < 5: -0.05
    
    הגדלות:
    - alias confidence גבוה (>= 0.95): +0.02 (עד max 1.0)
    - source.priority >= 8: +0.03
    
    minimum: 0.30 (מתחת לזה → flag_status='review')
    
    Returns: float [0.30, 1.0]
    """
```

---

### 3.7 שלב 7 — Apply Observation Flags

```python
def apply_observation_flags(
    observation: NormalizedObservation,
    source: Source,
    ruleset: NormalizerRuleSet
) -> tuple[str, str | None]:
    """
    בדוק observation_flags פעילים ב-DB:
    
    1. scope='single': observation_id == this observation
       → flag_status, flag_reason
    
    2. scope='source_product': source_id + product_id == this
       → flag_status, flag_reason
    
    3. scope='all_from_source': source_id == this
       → flag_status, flag_reason
    
    4. confidence_score < 0.40 → auto-flag 'review'
    
    Returns: (flag_status, flag_reason)
    """
```

---

## 4. מנגנוני ניהול admin/agent

### 4.1 Product Merge

**מצב:** שני מוצרים בDB (PRD008 "חסה" ו-PRD031 "חסה ראש") שהם אותו מוצר.

**פעולה:**

```sql
-- 1. יצירת merge record
INSERT INTO product_merges (source_product_id, target_product_id, reason, merged_by)
VALUES (31, 8, 'אותו מוצר, שמות שונים', 'admin');

-- 2. הזזת aliases
UPDATE product_aliases SET product_id = 8 WHERE product_id = 31;

-- 3. הזזת observations (reprocessing)
UPDATE normalized_observations SET product_id = 8 WHERE product_id = 31;

-- 4. deactivate source product
UPDATE products SET is_active = false WHERE id = 31;
```

**ב-NormalizerEngine:**

```python
def get_canonical_product_id(product_id: int) -> int:
    """בדוק product_merges; אם קיים merge פעיל → החזר target"""
    merge = db.query(ProductMerge).filter_by(
        source_product_id=product_id, is_active=True
    ).first()
    return merge.target_product_id if merge else product_id
```

---

### 4.2 Hide Observation / Source

**מצב:** מקור מסוים מחזיר מחירים כפולים שגויים.

**פעולה:**

```sql
-- הסתרת כל תצפיות ממקור X על מוצר Y
INSERT INTO observation_flags
    (source_id, product_id, flag_type, scope, reason, created_by)
VALUES
    (7, 1, 'hide', 'source_product', 'מקור SRC007 מחיר לא ריאלי על עגבנייה', 'admin');
```

**ב-NormalizerEngine — הטמעה ב-daily_aggregates:**

```python
# בעת חישוב אגרגט — observations עם flag_status='hidden' מוסננות
observations = db.query(NormalizedObservation).filter(
    NormalizedObservation.product_id == product_id,
    NormalizedObservation.flag_status.in_(['ok', 'review']),
    NormalizedObservation.is_benchmark == False,
    NormalizedObservation.is_basket_product == False,
    NormalizedObservation.observed_at >= date_start
).all()
```

---

### 4.3 Add / Edit Alias

**מצב:** מקור חדש מציג "גזרים אורגניים" — לא ממופה.

**פעולה:**

```sql
-- הוספת alias ל-DB
INSERT INTO product_aliases
    (product_id, alias_text, alias_text_normalized, confidence, created_by)
VALUES
    (13, 'גזרים אורגניים', 'גזרים אורגניים', 0.95, 'agent');
```

**תוצאה:** בריצה הבאה, ה-NormalizerEngine טוען את ה-alias החדש ומנרמל נכון.

---

### 4.4 Add Normalizer Rule

**מצב:** מקור חדש מציג מחיר ל-100 גרם (לא לק"ג).

```sql
INSERT INTO normalizer_rules
    (normalizer_profile_id, rule_kind, match_type, match_pattern,
     replacement_value, priority, notes, created_by)
VALUES
    (3, 'price_correction', 'exact', 'SRC009',
     '{"multiply_by": 10, "reason": "price per 100g"}',
     5, 'משק זינגר — מחיר ל-100 גרם', 'admin');
```

---

## 5. Reprocessing — עיבוד מחדש של Raw

כאשר מתווסף alias/rule חדש, ניתן לעבד מחדש raw היסטורי:

```python
def reprocess_source_observations(
    source_id: int,
    from_date: date,
    to_date: date
) -> ReprocessResult:
    """
    1. טוען raw_extracted_items לתאריך נתון
    2. מריץ NormalizerEngine עם rules נוכחיים
    3. מסמן observations ישנים כ-'superseded' (לא מוחק)
    4. שומר observations חדשים
    5. לוג ב-audit_log
    
    ניתן להפעיל מממשק admin / agent CLI
    """
```

---

## 6. Python API — NormalizerEngine

```python
# normalizer/engine.py

class NormalizerEngine:
    def __init__(self, db_session: Session):
        self.db = db_session
        self._ruleset_cache: dict[int, NormalizerRuleSet] = {}
    
    def normalize_item(
        self,
        item: RawExtractedItem,
        source: Source
    ) -> NormalizedObservation | None:
        """
        מריץ את כל שלבי הנרמול על פריט גולמי אחד.
        מחזיר None אם הפריט unresolvable.
        """
        ruleset = self._get_ruleset(source.id)
        
        product_match = self.resolve_product(item.raw_product_name, ruleset)
        if not product_match:
            self._mark_unresolvable(item, 'no_product_match')
            return None
        
        unit_resolution = self.resolve_unit(
            item.raw_unit_text, item.raw_price_text,
            item.raw_quantity_text, product_match.product, ruleset
        )
        
        price_resolution = self.resolve_price(
            item.raw_price_text, unit_resolution, ruleset
        )
        if price_resolution is None:
            self._mark_unresolvable(item, 'no_price')
            return None
        
        confidence = self.calculate_confidence(
            product_match, unit_resolution, price_resolution, source
        )
        
        observation = NormalizedObservation(
            source_id=source.id,
            source_fetch_run_id=item.source_fetch_run_id,
            raw_extracted_item_id=item.id,
            product_id=self._get_canonical_product_id(product_match.product_id),
            market_scope=source.market_scope,
            sales_channel=source.sales_channel,
            is_benchmark=(source.market_scope == 'benchmark'),
            is_basket_product=product_match.product.is_basket_product,
            is_organic_claimed=self.resolve_organic_flag(item, source, ruleset),
            price_amount=price_resolution.price_amount,
            currency_code='ILS',
            display_unit_id=unit_resolution.display_unit_id,
            normalized_price_value=price_resolution.normalized_price_value,
            normalized_unit_id=unit_resolution.normalized_unit_id,
            normalization_method=unit_resolution.method,
            confidence_score=confidence,
            observed_at=item.extracted_at,
        )
        
        flag_status, flag_reason = self.apply_observation_flags(
            observation, source, ruleset
        )
        observation.flag_status = flag_status
        observation.flag_reason = flag_reason
        
        return observation
    
    def _get_ruleset(self, source_id: int) -> NormalizerRuleSet:
        if source_id not in self._ruleset_cache:
            self._ruleset_cache[source_id] = self._load_ruleset(source_id)
        return self._ruleset_cache[source_id]
    
    def normalize_batch(
        self,
        items: list[RawExtractedItem],
        source: Source
    ) -> BatchResult:
        """עיבוד batch; מחזיר stats ורשימת observations."""
```

---

## 7. Admin UI — מסכי Normalizer

### 7.1 מסך Aliases

```
┌──────────────────────────────────────────────────────────┐
│ Product Aliases                          [+ Add Alias]   │
├──────────┬──────────────────┬──────────┬───────────────  │
│ Alias    │ Product          │ Source   │ Confidence │ Ac │
├──────────┼──────────────────┼──────────┼────────────┼────┤
│ עגבניה   │ עגבנייה (PRD001) │ global   │ 1.00       │ ✓  │
│ עגבניות  │ עגבנייה (PRD001) │ global   │ 1.00       │ ✓  │
│ גזרים...  │ גזר (PRD013)    │ SRC009   │ 0.95       │ ✓  │
└──────────┴──────────────────┴──────────┴────────────┴────┘
[Edit] [Deactivate]
```

### 7.2 מסך Normalizer Rules

```
┌──────────────────────────────────────────────────────────────┐
│ Normalizer Rules — SRC002 (סבתא יהודית)   [+ Add Rule]      │
├─────────┬──────────────┬──────────────┬──────────┬──────────  │
│ Priority│ Kind         │ Pattern      │ Value    │ Active    │
├─────────┼──────────────┼──────────────┼──────────┼────────── │
│ 5       │ product_alias│ ^עגבניה.*$   │ PRD001   │ ✓        │
│ 10      │ unit_map     │ ק"ג          │ kg       │ ✓        │
│ 20      │ organic_flag │ אורגני       │ true     │ ✓        │
└─────────┴──────────────┴──────────────┴──────────┴───────────┘
```

### 7.3 מסך Product Merges

```
┌──────────────────────────────────────────────────────────────┐
│ Product Merges                            [+ New Merge]      │
├──────────────────────┬─────────────────────┬─────────────────┤
│ Source Product       │ Target Product      │ Created By     │
├──────────────────────┼─────────────────────┼─────────────────┤
│ חסה ראש (PRD031)     │ חסה (PRD008)         │ admin          │
└──────────────────────┴─────────────────────┴─────────────────┘
```

---

## 8. תהליך עבודה מומלץ — Agent Mode

כאשר agent מזהה בעיית normalization:

```
1. agent מריץ: SELECT * FROM raw_extracted_items WHERE extraction_status='unresolvable' LIMIT 50;
2. agent מנתח את raw_product_name הנפוצים שלא ממופים
3. agent מוסיף aliases:
   INSERT INTO product_aliases (product_id, alias_text, alias_text_normalized, confidence, created_by)
   VALUES (13, 'גזרים טריים', 'גזרים טריים', 0.9, 'agent');
4. agent רושם ב-audit_log:
   INSERT INTO audit_log (actor_name, action, entity_type, after_state, notes)
   VALUES ('agent', 'alias.add', 'product_alias', '{"product":"גזר","alias":"גזרים טריים"}', 'unresolvable fix');
5. agent מפעיל reprocess על raw של יום קודם
```

---

## 9. מגבלות V1

- אין UI חזותי לעריכת regex rules (רק הוספה ב-DB ישירות)
- אין version history ל-rules (רק created_at)
- אין test harness ב-UI (ניתן להריץ ב-CLI)
- Reprocessing מלא אינו אוטומטי — מופעל ידנית
