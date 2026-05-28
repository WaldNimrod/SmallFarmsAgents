# תשובות לצוות 100 — Q&A לפני build

**מצוות 35 (עיצוב) ← צוות 100 (PM) ← צוות 110 (פיתוח)**
**תאריך:** 24.05.2026
**מענה ל:** בקשת הבהרות V200

---

## 1. STACK CHOICE — PHP/Twig על uPress

**אין בעיה.** ה-prototypes נכתבו כ-React+Babel כי זה הסטאק שלנו לעיצוב, **לא** כדרישת production. הם spec מצויר.

**מה מתורגם נקי 1:1:**
- כל ה-CSS (`system.css` + `T*-styles.css`) → העתקה ישירה. אין שורה אחת שדורשת JS.
- כל הרכיבים הסטטיים (Shell, Footer, SvcCard, ProjCard, PostCard, Bridge card, Hero variants, Story, Outcomes, Gallery) → Twig partials עם אותם data fields.
- מבנה ה-data ב-`T*-data.jsx` → ACF / CPT fields (ראו §3 ב-HANDOFF הראשי).

**מה דורש תרגום של state → URL/server:**

| Prototype state | Production solution |
|---|---|
| T1 variant switcher (A/B/C) | **לא בונים.** בחרנו Variant C → static. |
| T2 instance tabs | **לא בונים.** כל instance הוא URL נפרד `/services/{slug}`. |
| T3 project tabs | **לא בונים.** כל project הוא URL נפרד `/project/{slug}`. |
| T4 post tabs | **לא בונים.** כל post הוא URL נפרד `/blog/{slug}`. |
| T5 world filter (multi) | **URL params** — `?world=soil,know` → server filter → render. Optional progressive enhancement ב-JS עבור UX. |
| T5 view toggle (flow/grid) | **URL param** — `?view=flow` (default) או `?view=grid`. cookie אופציונלי. |
| T7 hero variant + unless placement | **לא בונים.** בחרנו: hero=`statement`, unless=`ribbon` → static. |
| T8 page switcher | **לא בונים.** /about, /about/heritage, /contact הם URLs נפרדים. |
| Contact form topic chips | **HTML checkboxes** עם CSS שגורם להם להיראות כ-chips. |
| WhatsApp + email links | **<a href>** רגיל. אין JS. |

**מסקנה:** הסטאק PHP/Twig הוא הבחירה הנכונה. ה-prototypes מציגים גם state-options שלא קיימים ב-production (כי הם כלי בחירת-עיצוב). הם נשארים archived ב-`_handoff/templates/` כ-reference, לא להעתקה.

---

## 2. tweaks-panel.jsx — DESIGN-ONLY

**לא לבנות.** ה-panel הוא admin tool של צוות 35 בלבד, ששירת אותנו בזמן בחירת הוריאנט הסופי. ב-production:

- **T1** — Variant C נעול, `data-bridge="seam"` נעול. אין panel.
- **T7** — Hero=`statement` נעול, Unless=`ribbon` נעול. אין panel.
- שאר ה-templates — אין tweaks מלכתחילה.

הקובץ `tweaks-panel.jsx` ניתן להתעלמות מוחלטת ב-`_handoff/templates/`. הוא קיים רק כדי שה-prototypes יעבדו מקומית לסקירה.

---

## 3. SSOT — ה-prototypes הם המקור הסופי

**אין Figma.** צוות 35 עובד ב-HTML+CSS+JSX ישירות (זה היתרון של העבודה איתנו — מה שאתם רואים הוא מה שיש). 

- **המקור היחיד:** קבצי `_handoff/templates/` + `_handoff/brand/` + `_handoff/components/`.
- **גרסה נעולה:** v1.0 · 24.05.2026 (אחרי אישור מנהל לכל 7 התבניות).
- **אם נמצא bug עיצוב בזמן הbuild:** פנייה אלינו (צוות 35) → תיקון ב-prototypes → re-handoff עם diff מסומן.

**ניהול גרסאות:** קבצי החבילה הם snapshot מוקפא. גרסה הבאה (אם תידרש) תיקרא **V200** עם changelog ברור.

---

## 4. TBC list — מה נמרוד צריך לסגור לפני go-live

הרשימה המלאה, מסומנת ב-priority:

### Blockers (חובה לפני go-live)

| # | מה | היכן בקוד | קריטיות |
|---|---|---|---|
| **Q-05** | שמות 3-5 מסעדות-עוגן להזכיר | T2 produce (`who.metaTBC`), T8 about (factrow) | גבוהה — מופיע ב-prototypes כ-"TBC · להוסיף 2-3 שמות" |
| **Q-NEW-03** | האם "Unless" כ-tagline סופי? | T7 ribbon, Footer, T8 heritage | גבוהה — הוא חוזר 4+ פעמים באתר |
| **Q-11** | היחס למיזו כברנד נפרד / sub-brand | T7 footer ("דיגיטל / מיזו"), T8 about | בינונית — משפיע על מיתוג של SFA + tiktrack |
| T-07 | קובץ הסל המקורי | חוסם T-04 (לוגו) | גבוהה — חוסם משפחת לוגו |
| T-12 | אישור coop-sharon כמיזם אמיתי | T3 instance "coop-sharon" | בינונית — אם לא יאושר, להחליף ב-CMS לפרויקט אחר |

### Important (טוב להיות לפני go-live)

| # | מה | היכן | קריטיות |
|---|---|---|---|
| **Q-02** | SFA — חינמי-מוצהר או חינמי-מסחרי? | T2 sfa (CTA, copy), T1 know | בינונית — משפיע על הקופי בפרק "מה תקבל" |
| **Q-03** | היכן נמרוד מלמד בקביעות? | T2 know (placeholders), T8 about | בינונית — מילוי ספציפי במקום generic |
| **Q-09** | מתודולוגיות market garden — מתועדות? | T2 consulting-agro | נמוכה — להחליף "tbc" בקישור למסמך/ספר |
| **Q-10** | מתודולוגיות תכנון גידול — מתועדות? | T2 consulting-agro | נמוכה — אותו דבר |

### Closed (לתיעוד)

- ✅ **T-09** — WhatsApp `wa.me/972547776770` · 054-7776770 (סגור 24.05.2026)
- ✅ **T-06** — Bridge card (סגור 23.05.2026)
- ✅ **T-08** — "ידע" → "ייעוץ והוראה" UI (סגור)
- ✅ **T-10** — `/about/heritage` (סגור — T8)
- ✅ **T-11** — TAXONOMY v3.4 (סגור)

### Not-blockers (אחרי go-live)

- T-01 BOOM A/B · T7 — בסשן עיצוב נוסף
- T-02 Mobile screens · Stage 5
- T-03 איורי רקע · Stage 6
- T-04 משפחת לוגו · Stage 6
- T-05 ייבוא WP · יבוצע בזמן ה-build

**איך לתכנן P004:** רוב ה-Q* הם **תוכן ספציפי**, לא החלטות עיצוב. אם נמרוד יתן את התשובות תוך זמן ה-build, אתם פשוט מעדכנים strings ב-CMS. אם לא — TBC markers נשארים ב-staging, לא ב-production.

---

## סיכום ל-P004

| נושא | פעולה |
|---|---|
| Stack | ✅ PHP/Twig — אישור. אין blockers. |
| tweaks-panel | ❌ לא לבנות. |
| SSOT | ✅ קבצי `_handoff/` הם המקור. |
| TBC | 4 blockers (Q-05, Q-NEW-03, Q-11, T-07) + 4 important (Q-02/03/09/10) — צריכים לחזור לנמרוד דרך צוות 100. |

**מתקדמים על T7 במקביל — מאושר.** כשתסיימו את ה-skeleton של T7, נעשה review משותף לפני T1-T8.

— צוות 35
