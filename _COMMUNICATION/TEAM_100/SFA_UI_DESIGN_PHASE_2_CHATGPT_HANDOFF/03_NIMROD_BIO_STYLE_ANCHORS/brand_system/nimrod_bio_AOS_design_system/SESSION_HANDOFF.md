# Nimrod.bio / AOS — Session Handoff

**עדכון:** 23.05.2026 · **Stage 3 הושלם במלואו** · 7 תבניות + Bridge component + TAXONOMY v3.4
**הסשן הבא:** Stage 4 (ארכיון WordPress · T-05) או Stage 5 (Mobile · T-02)
**קובץ פתיחה:** `T7 Home.html` (סקירה מקיפה) · אז `SESSION_HANDOFF.md` · אז `brand/TAXONOMY-v3.4-LOCKED.md`

---

## איפה אנחנו בתהליך

| Stage | תיאור | סטטוס |
|---|---|---|
| 0 | Foundations | ✅ נעול 11.05.2026 |
| 1 | Components | ✅ נעול 11.05.2026 |
| 1.5 | Taxonomy + book context | ✅ נעול 15.05.2026 |
| **2** | **Sitemap v3.1 (entities + wireframes)** | **✅ נעול 23.05.2026** |
| **3** | **T1 · World page (אדמה)** | **✅ אושר 23.05.2026 · Variant C + Bridge=תפר** |
| **3** | **T2 · Services page (3 instances)** | **✅ אושר 23.05.2026 · produce + consulting-hydro + sfa** |
| **3** | **T3 · Project page (3 instances)** | **✅ אושר 23.05.2026 · client-case + own-venture/seeking + own-venture/legacy** |
| **3** | **T4 · Post page (2 instances)** | **✅ אושר 23.05.2026 · מנפסט + מקרה** |
| **3** | **T5 · Blog index** | **✅ אושר 23.05.2026 · זרימה נועזת + גריד** |
| **3** | **T7 · Home page** | **✅ אושר 23.05.2026 · Hero=statement, Unless=ribbon** |
| **3** | **T8 · Static (about + heritage + contact)** | **✅ אושר 23.05.2026 · סוגר T-10** |
| **3** | **Components v3 · Bridge card** | **✅ אושר 23.05.2026 · סוגר T-06** |
| **3** | **TAXONOMY v3.4** | **✅ נעול 23.05.2026 · client-case / own-venture / legacy / seeking-partners** |
| 4 | ארכיון WordPress (T-05) | 🟡 הבא בתור |
| 5 | Mobile screens (T-02) | ⏳ |
| 6 | משפחת לוגו + איורי מים (T-03/04) | ⏳ |

## החלטות נעולות (v3.1 · 23.05.2026)

| ציר | החלטה |
|---|---|
| Entity EN | `services` |
| Entity HE | **פעילות** |
| Project scope | **`client-case`** (פרויקט שעשינו ללקוח) / **`own-venture`** (מיזם שלנו) · *מעודכן 23.05.2026; מבטל linked-to-services / portfolio-only* |
| Project stage | `seed` · `seeking-partners` (חדש) · `pilot` · `live` · `legacy` (לא "archived" — מורשת, לא סיום) |
| Worlds | אדמה · ידע · דיגיטל (3 קבועים) |
| Bridges | 4 — שטחי-שאילתה, לא ישויות |
| Templates | 7 (T6/Portfolio נמחק) |
| Blog | קטגוריה אחת: "בלוג". תיוג צולב = world-tags + free tags |
| ניווט עליון | בית + 3 עולמות + בלוג + על נמרוד + צור קשר (label "ידע"→"ייעוץ והוראה") |
| תיק עבודות | **לא בניווט.** סקציה ב-T7 (Home) + במידת הצורך ב-T1 (World). פרויקטים בודדים = /project/{slug} |

## קבצים מאושרים

| קובץ | סטטוס | תאריך |
|---|---|---|
| `PROCESS.md` | APPROVED | 11.05.2026 |
| `brand/voice.md` v2 | APPROVED | 15.05.2026 |
| `brand/typography.md` | APPROVED | קודם |
| `brand/system.css` v3.3 | APPROVED | 22.05.2026 |
| `brand/TAXONOMY-v3.3-LOCKED.md` | APPROVED | 23.05.2026 |
| `brand/site-context-2026-05-v2.md` | CANONICAL (team_100) | 15.05.2026 |
| `brand/CLAUDE-CODE-BRIEF.md` | LIVING DOC | 13.05.2026 |
| `brand/BASKETS-brief.md` | LIVING DOC | 13.05.2026 |
| `brand/HANDOFF-Stage3.md` | **NEW · לסשן הבא** | 23.05.2026 |
| `Foundations.html` | APPROVED | 11.05.2026 |
| `Components.html` v2 | APPROVED | 11.05.2026 |
| `Sitemap.html` v3.1 | APPROVED | 23.05.2026 |
| `T1 World - אדמה.html` | **APPROVED · v1.0 · Variant C + seam** | 23.05.2026 |
| `T1-styles.css` · `T1-data.jsx` · `T1-variants.jsx` | support files for T1 | 23.05.2026 |
| `T2 Services.html` | **APPROVED · v1.0 · 3 instances (produce/hydro/sfa)** | 23.05.2026 |
| `T2-styles.css` · `T2-data.jsx` · `T2-instances.jsx` | support files for T2 | 23.05.2026 |
| `T3 Project.html` | **APPROVED · v1.1 · 3 instances** | 23.05.2026 |
| `T3-styles.css` · `T3-data.jsx` · `T3-instances.jsx` | support files for T3 | 23.05.2026 |
| `T4 Post.html` | **APPROVED · v1.0 · 2 instances** | 23.05.2026 |
| `T4-styles.css` · `T4-T5-data.jsx` | support files for T4 + T5 | 23.05.2026 |
| `T5 Blog.html` | **APPROVED · v1.0 · 2 views** | 23.05.2026 |
| `T5-styles.css` | support file for T5 | 23.05.2026 |
| `T7 Home.html` | **APPROVED · v1.0 · Hero=statement + Unless=ribbon** | 23.05.2026 |
| `T7-styles.css` | support file for T7 | 23.05.2026 |
| `T8 Static.html` | **APPROVED · v1.1 · about + heritage + contact** | 23.05.2026 |
| `T8-styles.css` | support file for T8 | 23.05.2026 |
| `Components v3 - Bridge.html` | **APPROVED · v1.0 · sub-component T-06 closed** | 23.05.2026 |
| `brand/TAXONOMY-v3.4-LOCKED.md` | **LOCKED · 23.05.2026 · מבטל v3.3** | 23.05.2026 |
| `Taxonomy Audit.html` v2 | LIVING DOC | 13.05.2026 |
| `Nimrod DS v2.html` | ARCHIVED | קודם |
| `Components v1.html` | SUPERSEDED | 11.05.2026 |
| `Sitemap v1.html` · `Sitemap v2.html` | SUPERSEDED | 22.05.2026 |
| `brand/TAXONOMY-v3.1-amendment.md` | SUPERSEDED | 13.05.2026 |

## Tickets פתוחים

- **T-01** BOOM A/B בדף הבית · Stage 3 בסשנים הבאים
- **T-02** ~~Mobile screens~~ · ✅ **סגור 25.05.2026** · `_handoff/04-MOBILE-spec.md`
- **T-03** איורי מים: 3 סלים + 6-8 איורים · Stage 6 · תלוי בלוגו
- **T-04** משפחת לוגו · Stage 6
- **T-05** ארכיון WordPress · עשרות פוסטים · **Stage 4 · הבא בתור**
- **T-06** ~~Bridge card component~~ · ✅ **סגור 23.05.2026** · `Components v3 - Bridge.html`
- **T-07** קובץ הסל המקורי · ממתין למנהל
- **T-08** ~~"ידע" → "ייעוץ והוראה"~~ · ✅ **סגור 23.05.2026** · יושם בכל ה-Shell + TAXONOMY v3.4
- **T-09** ~~WhatsApp~~ · ✅ **סגור 24.05.2026** · `wa.me/972547776770` · 054-7776770
- **T-10** ~~`#about/heritage`~~ · ✅ **סגור 23.05.2026** · T8 Static.html · עמוד heritage מלא
- **T-11** ~~TAXONOMY v3.4~~ · ✅ **סגור 23.05.2026** · `brand/TAXONOMY-v3.4-LOCKED.md`
- **T-12** coop-sharon · אישור שזה כיוון מיזם אמיתי, או החלפה
- **T-13** [NEW · 24.05.2026] **חבילת Handoff מוכנה** ב-`_handoff/`: prompts לאיורים (T-03) + לוגו (T-04) + handoff מלא לצוות 110
- **Q-02 / Q-03 / Q-05 / Q-09 / Q-10 / Q-11 / Q-NEW-03** — שאלות תוכן ל-nimrod-book, לא חוסמות

## הקשר בקצרה (קבוע)

נימרוד ולד — חוות "הגינה של נמרוד" נסגרה ב-2023, וכעת המותג עובר **מטמורפוזה**: שורש אחד + 3 עולמות + 4 גשרים — **אדמה** (תוצרת, חממה, BCS, משתלה) · **ידע** (3 ערוצי ייעוץ + הוראה) · **דיגיטל / מיזו** (SFA חינמי-קהילתי, tiktrack בפיתוח).

**הייחוד הוא הגשרים** — לא העולמות.

**התזה:** "העולם הוא כזה — אלא אם כן." Unless (tagline) · CDIP (תזה מאחדת). Recursion/BOOM = direction, definitions UNVERIFIED.

---
