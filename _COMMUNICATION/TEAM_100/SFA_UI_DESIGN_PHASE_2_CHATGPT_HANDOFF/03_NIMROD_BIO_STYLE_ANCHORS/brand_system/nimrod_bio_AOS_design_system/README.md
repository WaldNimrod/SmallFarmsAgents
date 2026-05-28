# _handoff/ — חבילת מסירה מלאה

תיקייה זו מכילה את **כל** מה שצריך — self-contained. אין צורך לחזור לפרויקט המקור.

## תוכן

```
_handoff/
├── 00-HANDOFF-claude-code-110.md         ← נקודת כניסה לצוות 110
├── 01-PROMPT-watercolor-backgrounds.md   ← prompt לאיורים (T-03) · עדכן ל-3 רזולוציות (ראה 04)
├── 02-PROMPT-logo-family.md              ← prompt ללוגו (T-04)
├── 03-RESPONSE-team100-V200.md           ← תשובות ל-Q&A של P004
├── 04-MOBILE-spec.md                     ← Mobile responsive (סוגר T-02)
├── SESSION_HANDOFF.md                    ← קונטקסט סשן + tickets פתוחים
├── README.md                              ← הקובץ הזה
│
├── brand/                                ← מקור-אמת לעיצוב
│   ├── system.css                        ← CSS tokens (LOCKED v3.3)
│   ├── TAXONOMY-v3.4-LOCKED.md           ← entities, scope, stage, worlds
│   ├── TAXONOMY-v3.3-LOCKED.md           ← (היסטוריה — superseded)
│   ├── voice.md                          ← Tone of voice
│   ├── typography.md                     ← Typography spec
│   ├── site-context-2026-05-v2.md        ← Brand & worldview canon
│   └── HANDOFF-Stage3.md                 ← תקציר Stage 3
│
├── components/                           ← רכיבי עיצוב
│   ├── Foundations.html                  ← Tokens reference page
│   ├── Components.html                   ← v2 atoms (LOCKED)
│   └── Components v3 - Bridge.html       ← v3 Bridge card (T-06 closed)
│
└── templates/                            ← 7 התבניות, prototypes ב-React+CSS
    ├── T1 World - אדמה.html              ← T1 prototype
    ├── T1-styles.css
    ├── T1-data.jsx
    ├── T1-variants.jsx
    ├── T2 Services.html                  ← T2 (3 instances)
    ├── T2-styles.css
    ├── T2-data.jsx
    ├── T2-instances.jsx
    ├── T3 Project.html                   ← T3 (3 instances)
    ├── T3-styles.css
    ├── T3-data.jsx
    ├── T3-instances.jsx
    ├── T4 Post.html                      ← T4 (2 instances)
    ├── T4-styles.css
    ├── T5 Blog.html                      ← T5 (flow + grid)
    ├── T5-styles.css
    ├── T4-T5-data.jsx                    ← shared blog data
    ├── T7 Home.html                      ← T7 (dataset + tweaks)
    ├── T7-styles.css
    ├── T8 Static.html                    ← T8 (about + heritage + contact)
    ├── T8-styles.css
    └── tweaks-panel.jsx                  ← Tweaks framework (T7)
```

## נקודות-כניסה לפי תפקיד

| תפקיד | פתח את |
|---|---|
| **צוות 110 / פיתוח** | `00-HANDOFF-claude-code-110.md` |
| **מנוע ייצור איורים (T-03)** | `01-PROMPT-watercolor-backgrounds.md` |
| **מנוע ייצור לוגו (T-04)** | `02-PROMPT-logo-family.md` |
| **לסקירת prototype** | פתח כל `templates/T*.html` בדפדפן — self-contained |

## הקבצים פועלים-בעצמם

כל קובץ HTML ב-`templates/` עובד באופן עצמאי כשפותחים אותו מקומית — הוא מקושר ל-`../brand/system.css` ולקבצים שלו. אין תלות באינטרנט (חוץ מ-React+Babel+Google Fonts CDN).

## תלויות פתוחות (לא חוסמות את ה-build)

| Ticket | מה | בעלים |
|---|---|---|
| T-01 | BOOM A/B variant ב-T7 | צוות 35 |
| **T-02** | ✅ סגור — `04-MOBILE-spec.md` | — |
| T-03 | איורי צבעי-מים (5 איורים) | מנוע · prompt מצורף |
| T-04 | משפחת לוגו | מנוע · prompt מצורף · ממתין ל-T-07 |
| **T-05** | **ייבוא ארכיון WordPress** | **צוות 110** |
| T-07 | קובץ הסל המקורי | נמרוד |
| T-09 | ✅ סגור — WhatsApp `wa.me/972547776770` | — |
| T-12 | אישור coop-sharon | נמרוד |
| Q-02/03/05/09/10/11 | תוכן ספציפי (TBC markers בקוד) | נמרוד |

## גרסה

חבילה זו תואמת **Stage 3 סוף סשן 23-24.05.2026**. כל החלטות עיצוב נעולות. לשינויים — חזרה לצוות 35.
