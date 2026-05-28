# HANDOFF · Claude Code 110 — בניית האתר nimrod.bio

**מצוות 35 (עיצוב) ← צוות 110 (פיתוח)**
**תאריך:** 24.05.2026
**גרסה:** v1.0
**מבוסס על:** Stage 0–3 LOCKED.

קובץ זה הוא נקודת-הכניסה היחידה לצוות 110. כל מה שאתם צריכים לבנות את האתר נמצא כאן, או מקושר מכאן.

---

## 1. מה זה האתר

**nimrod.bio** — אתר אישי/עסקי של נמרוד ולד. ארגון תלת-זרועי תחת שם אחד (חוקר-מבצע יחיד שעובד על שלוש זרועות מקושרות):
- **אדמה** — חממה הידרופונית, תוצרת למסעדות, BCS שירותי שטח.
- **ייעוץ והוראה** — ייעוץ ל-4 חממות, סדנאות, market garden.
- **דיגיטל** — SFA (חינמי, קהילתי), קואופרטיב חממות בשרון, tiktrack.

**הליבה האידאית:** *"שורש אחד, שלוש זרועות."* + *"העולם הוא כזה — אלא אם כן."* (Unless · tagline).

**הייחוד הוויזואלי:** ארבעת **הגשרים** בין העולמות — לא הענפים עצמם. עיצוב חייב לתת בולטות לקישוריות.

---

## 2. ארכיטקטורה — 7 תבניות

| Template | URL pattern | מה זה | קובץ design |
|---|---|---|---|
| **T1** | `/world/{soil\|know\|code}` | עמוד עולם (אדמה/ייעוץ/דיגיטל) | `T1 World - אדמה.html` |
| **T2** | `/services/{slug}` | עמוד פעילות בודדת | `T2 Services.html` |
| **T3** | `/project/{slug}` | עמוד פרויקט/מיזם בודד | `T3 Project.html` |
| **T4** | `/blog/{slug}` | פוסט בודד | `T4 Post.html` |
| **T5** | `/blog` | אינדקס בלוג | `T5 Blog.html` |
| **T7** | `/` | דף בית | `T7 Home.html` |
| **T8** | `/about` · `/about/heritage` · `/contact` | דפים סטטיים | `T8 Static.html` |

**T6 (Portfolio) — לא קיים.** הוסר במכוון ב-Sitemap v3.1. פרויקטים נגישים דרך T1 (לפי עולם) או T7 (נבחרים).

---

## 3. סטאק טכני מומלץ (לבחירת צוות 110)

**הצעה ראשית: WordPress + custom theme.**
- האתר הקיים הוא WordPress, ויש ארכיון פוסטים שלא יועבר בידיים — ראו §10.
- WordPress מתאים גם לדפים סטטיים (T8), בלוג מובנה (T4/T5), ו-custom post types ל-services + projects.

**מבנה Custom Post Types נדרש:**
```
CPT: service
  fields:
    - slug              (string, unique)
    - title_he          (string)
    - tagline           (string)
    - lede              (text)
    - worlds            (array, 1-3 from [soil|know|code])
    - service_type      (enum: service|system|background)
    - stage             (enum: seed|seeking-partners|pilot|live|legacy)
    - is_free           (boolean)
    - cta_label         (string)
    - cta_whatsapp_href (url)
    - linked_projects   (array of project slugs)
    - related_posts     (array of post slugs)
    - sections          (acf/repeater: who, how, what)
    - meta_strip        (acf/repeater: key/value)
    - hero_image        (image)

CPT: project
  fields:
    - slug              (string, unique)
    - title_he          (string)
    - name_tbc          (boolean — show TBC marker)
    - scope             (enum: client-case | own-venture)
    - stage             (enum: seed | seeking-partners | pilot | live | legacy)
    - worlds            (array, 1-3)
    - year              (string — accepts ranges like "2014-2023")
    - location          (string)
    - duration          (string)
    - summary           (text)
    - story             (rich text, 3-6 paragraphs)
    - linked_services   (array of service slugs, optional — only for client-case)
    - outcomes          (acf/repeater: number, label, description)
    - gallery           (array of images)
    - more_projects_ids (array, computed or curated)
    - seeking_note      (text — only if stage=seeking-partners)
    - legacy_of         (text — only if stage=legacy)
```

**תיוג cross-cutting:**
- **world** — taxonomy "world" עם 3 terms: soil, know, code. שייך ל-service + project + post.
- **flow_style** — taxonomy עבור פוסטים (lead/wide/tall/typo/feature/quote/brief) — קובע layout ב-T5.

**Frontend:** PHP/Twig (WordPress native) או Next.js עם REST/GraphQL. צוות 110 לבחור.

**Build pipeline:**
- CSS — system.css הוא הליבה. הוסיפו עוד stylesheets מודולריים לכל template.
- JS — minimal. React only if needed (T5 filtering, T7 hero tweaks). vanilla הוא בסדר.

---

## 4. נכסים — מה לרשת מקבצי העיצוב

### CSS — Design tokens
**מקור אמת:** `brand/system.css` (v3.3 LOCKED). מועתק as-is.

הטוקנים הקריטיים:
```css
/* Worlds */
--w-soil-deep: #3a5220;   --w-soil: #6a8a3a;
--w-know-deep: #9a4f2b;   --w-know: #c46a3e;
--w-code-deep: #1f5e60;   --w-code: #2d8a8c;
--spark:       #d23a2e;   --spark-ink: #8a2820;

/* Paper system */
--paper:   #f5f3ec;       --paper-2: #eef0e0;       --paper-3: #e3e6cf;
--ink:     #1f1e1c;       --ink-soft: #5b483a;
--line:    rgba(31,30,28,.12);

/* Spacing/radii */
--radius-s: 4px;   --radius-m: 10px;   --radius-l: 18px;   --radius-pill: 100px;

/* Type */
--font-serif: "Frank Ruhl Libre", serif;
--font-sans:  "Assistant", sans-serif;
--font-mono:  "JetBrains Mono", monospace;
```

**כללי-זהב:**
1. אדום spark **רק** בטקסט-מסומן, badge "seeking-partners", ו-"Unless". **לא בלוגו**. ≤5 שימושים ל-viewport.
2. כל world עם משפחת-צבעים משלו. **אסור לערבב** מחוץ ל-Bridge cards.
3. paper-color תמיד הרקע הראשי. ink-color תמיד הטקסט הראשי. שום white pure ושום black pure.

### Fonts (Google Fonts)
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Frank+Ruhl+Libre:wght@500;700;900&family=Assistant:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
```

### תמונות
**מצב נוכחי:** placeholders מסומנים `data-cap="TBD · …"`. הוחלפו ב-Stage 6 (T-03 פתוח · ראה `_handoff/01-PROMPT-watercolor-backgrounds.md`).

**מבנה מומלץ:**
```
/public/img/
  bg-soil@{1x,2x}.{png,jpg,svg}
  bg-know@{1x,2x}.{png,jpg,svg}
  bg-code@{1x,2x}.{png,jpg,svg}
  bg-blog@{1x,2x}.{png,jpg,svg}
  bg-about@{1x,2x}.{png,jpg,svg}
  /uploads/                       (WordPress media library)
  /baskets/                        (מהמשפחת לוגו T-04)
```

### Iconography
מינימליסטי. SVG inline בלבד (לא ספריית icon-font). דוגמאות מ-design files:
- `home-icon` (Shell): SVG path inline
- `whatsapp-icon`: SVG path inline (לא תמונה של "WA")
- `share-icons` (T4 aside): copy/whatsapp/email

**אסור:** Font Awesome / Material Icons / Iconify.

---

## 5. רכיבי-UI שצריך לבנות (component inventory)

| רכיב | מקור CSS | תיאור | קריטיות |
|---|---|---|---|
| `Shell` (nav + footer) | `T1-styles.css` `.shell-nav` `.shell-foot` | מוטמע בכל עמוד. 3 עולמות + בית + bg + about + contact | חובה |
| `WC` (world chip) | `T1-styles.css` `.wc` | תג צבעוני קטן לכל עולם, fill + ghost variants | חובה |
| `Bridge card` | `T1-styles.css` + Components v3 doc | כרטיס פעילות בין 2 עולמות, signal=seam locked | חובה |
| `SvcCard` (service card) | `T1-styles.css` `.svc-card` | כרטיס פעילות לעולם בודד | חובה |
| `ProjCard` (project card) | `T1-styles.css` `.proj-card` | כרטיס פרויקט | חובה |
| `PostCard` / `PostTile` / `PostFlowItem` | `T5-styles.css` | 3 וריאנטים: list, grid, editorial-flow | חובה |
| `Stage stamp` | `T3-styles.css` `.stage-stamp` | תווית stage (live/legacy/seeking/pilot/concept) | חובה |
| `Anchor card` | `T1-styles.css` `.anchor-card` | כרטיס עוגן double-width (חממה ב-T1) | חובה |
| `SeekingRibbon` + `LegacyRibbon` | `T3-styles.css` | באנרים לעמודי פרויקט | חובה |
| `HeritageStrip` | `T2-styles.css` `.heritage-strip` | באנר עם קישור ל-/about/heritage (T2 produce) | חובה |
| `StoryBlock` | `T3-styles.css` `.story` | טקסט קריא ארוך עם drop-cap | חובה |
| `ThreeColBlock` | `T2-styles.css` `.three-col` | who/how/what — 3 טורים | חובה |
| `Outcomes` (metric tiles) | `T3-styles.css` `.outcomes` | 4 tiles עם מספר גדול | חובה |
| `Gallery` | `T3-styles.css` `.gallery` | grid תמונות בגדלים שונים | חובה |
| `Final CTA` | `T2-styles.css` `.final-cta` | סוף-עמוד CTA עם 2 כפתורים (טופס + WhatsApp) | חובה |
| `FilterChip` | `T5-styles.css` `.filter-chip` | פילטר world מרובה-בחירה בבלוג | חובה |
| `Breadcrumb` | `T2-styles.css` `.breadcrumb` | פירורי לחם | חובה |
| `SecHead` (section header) | `T1-styles.css` `.s-eyebrow`+`.s-title` | מבנה אחיד לכל סקציה | חובה |
| `MediaItem` (T8 about · מדיה) | `T8-styles.css` `.media-item` | פריט בכרטיס "במדיה" — סוג + outlet + כותרת | בינוני |
| `JourneyTimeline` | `T8-styles.css` `.journey` | timeline אנכי לעמוד about | בינוני |
| `ValueTile` | `T8-styles.css` `.value-tile` | tile עיקרון בעמוד about | בינוני |

---

## 6. תבניות (Pages) — Specs

### T7 · Home — דף הבית

**Hero גלובלי:** `statement` (משפט גדול + ER diagram). **Unless placement:** `ribbon` (רצועה כהה באמצע).

**Sections:**
1. Hero — משפט "פיזיקה, אקולוגיה, קוד וחקלאות — אותה מערכת. שלוש זרועות, 3× חיבורים." + SVG diagram + meta row (3 facts)
2. §01 העולמות — 3 כרטיסים גדולים בצבעי-עולם (כל אחד מקושר ל-T1)
3. §02 פרויקטים — grid 1-large + 2-small (mix client-case + own-venture, כולל seeking-partners עם stamp)
4. **Unless ribbon** (full-width ink-black) — בין projects ל-posts
5. §03 מהבלוג — 4 פוסטים אחרונים (square aspect)
6. Final CTA — 2 paths (contact + SFA join)

**Data sources:**
- 3 worlds — static
- featured projects — 3 selected (configurable מ-CMS)
- recent posts — `BLOG_POSTS.slice(0,4)` order by date desc

### T1 · World page (אדמה / ייעוץ / דיגיטל)

**Variant נעול:** C (נסיוני · strata + recursion). Bridge signal: **seam**.

**Sections (לפי Sitemap §05):**
1. Hero — `אדמה` ענקי עם 3 הדהודים דהויים (echo) מאחור · gloss · intro
2. §01 ליבה — lattice עם anchor כהה במרכז (חממה) + 4 lat-side cards של שאר services
3. CDIP mini-diagram (3 circles + 3× point)
4. §02 גשרים — 3 Bridge cards (signal=seam)
5. §03 פרויקטים — 3 ProjCards עם rotations עדינים
6. §04 פוסטים — 2 columns

**Data sources:**
- כל service/project/post שיש לו ה-world בתגיות שלו (1-3 worlds possible)
- ה-anchor service (חממה) מוגדר ב-CMS כ-`is_anchor_for_world: soil`

### T2 · Services — עמוד פעילות

**Sections:**
1. Breadcrumb (בית › עולם › פעילות)
2. Hero — single (1 world) או bridge (2 worlds, עם stripe + seam)
3. **Heritage Strip** — רק ל-`produce` service (קישור ל-`/about/heritage`)
4. Meta strip (4 facts)
5. §01-03 — three-col (למי / איך עובדים / מה תקבל)
6. **SFA-specific:** Origin flow (3 numbered steps) — רק ל-`sfa`
7. §04 פרויקטים שהשתמשו ב-service
8. §05 פוסטים קשורים
9. Final CTA — 2 כפתורים: form + WhatsApp (`wa.me/972547776770`)

**Per-instance variations:**
| service | bridge? | CTA primary | CTA hint |
|---|---|---|---|
| produce | לא · soil only | "הצעת מחיר" (know color) | "תגובה תוך 48 שעות" |
| consulting-hydro | כן · soil×know | "הצעת מחיר" (know color) | "פגישת היכרות חינם" |
| sfa | כן · soil×code | "הצטרף לקהילה" (code color) | "ללא תשלום" |

### T3 · Project page

**Sections (תלוי scope+stage):**
1. Breadcrumb
2. **Stage-specific ribbon:**
   - `seeking-partners` → seeking ribbon (spark border + pulsing dot)
   - `legacy` → warm soil ribbon
   - `live` → אין ribbon נוסף
3. Hero — story title + summary + meta row + image with stage stamp overlay
4. §01 הסיפור — 3-6 פסקאות, drop-cap
5. §02 פעילויות שהפעילו — רק ל-`client-case` (`linked_services` array)
   - או §02 קשור · מיזמים אחרים — ל-`own-venture` (`relatedVentures` array)
6. §03 תוצאות (`outcomes` 4 tiles) או "התוכנית" (לפרויקט עם stage=seeking-partners)
7. §04 גלריה
8. §05 פרויקטים נוספים — filter: shared world
9. **Optional seeking CTA** — רק ל-`stage=seeking-partners`

### T4 · Post page

**Layout:** 3 columns — gutter | body (62ch) | aside (240px sticky).

**Sections:**
1. Breadcrumb (בית › בלוג › כותרת)
2. Hero — meta row + title + subtitle + author block + hero image 21:9
3. Body — full HTML article עם drop-cap, h2 עם num, blockquote, pullquote (incl. spark variant), entity-links inline
4. Aside (sticky) — ToC + Share buttons + Related entities (links to T2/T3)
5. Related posts — bottom band on paper-2

**Entity-link styling:** `<a class="entity-link [world]">` — תחתון 2px בצבע world.

### T5 · Blog index

**Header:** "בלוג" ענקי + lede + סטטיסטיקות

**Filter bar (sticky):** 3 world chips (multi-select) + view toggle (flow/grid) + ספירה דינמית + reset

**Views:**
- **`flow` (default)** — editorial 6-col grid, `auto-flow: dense`. **flowStyle per post:**
  - `lead` — span 6, horizontal
  - `wide` — span 4, image-left
  - `tall` — span 2 col × 2 row, vertical
  - `typo` — span 3, dark bg, no image
  - `quote` — span 3, pull-quote on paper-2
  - `feature` — span 3, standard
  - `brief` — span 2, compact
- **`grid`** — uniform 3-col, featured post on top, then equal cards

**Empty state:** "אין פוסטים תחת הסינון הנוכחי. נקה סינון →"

### T8 · Static pages

**3 דפים בקובץ אחד (state-based):** about · heritage · contact

**About:**
1. Hero קומפקטי — avatar 56px + שם + h1 בינונית + lede
2. Gallery row — 5 תמונות של נמרוד בעבודה (4/5 ratio)
3. Factrow (4 facts)
4. §01 הסיפור — 5 פסקאות, narrative prose עם pullquote
5. §02 מסע — journey timeline אנכי (6 events, world-colored dots)
6. §03 CDIP thesis (2 cols)
7. §04 עקרונות (3 value tiles)
8. §05 במדיה (grid 2-col, 4 media kinds: press/podcast/talk/write)
9. Contact teaser

**Heritage:** (סוגר T-10 — לינק מ-`produce` service)
1. Hero — stamp "מהשורש · הסיפור המלא" + h1 "הגינה של נמרוד" + meta row + image 21:9
2. Body 64ch — 6 כותרות, drop-cap, blockquote, 2 pullquotes, entity-links לכל הקישורים החיים שיוצאים מהמורשת
3. Heritage end card — קישור חזרה ל-`produce`

**Contact:**
1. Hero — "דבר איתי" + lede
2. Body 2-col:
   - Form: name + email + phone (opt) + topic chips (multi-select world-colored) + textarea + submit
   - Side: response time card + WhatsApp card (`wa.me/972547776770`) + email direct + activity area

---

## 7. תפריט עליון (Shell) — חוזה

```html
<nav class="shell-nav">
  <div class="shell-nav-inner">
    <a href="/" class="shell-mark">
      נימרוד ולד<small>nimrod.bio</small>
    </a>
    <div class="shell-links">
      <!-- Home icon (no border) -->
      <a href="/" class="nav-home" aria-label="בית">
        <svg>…</svg>
      </a>
      <!-- 3 worlds group (borderless, dot before each) -->
      <div class="nav-worlds">
        <a href="/world/soil" class="nav-world soil [is-active]">אדמה</a>
        <a href="/world/know" class="nav-world know">ייעוץ והוראה</a>
        <a href="/world/code" class="nav-world code">דיגיטל</a>
      </div>
      <!-- Vertical separator -->
      <span class="nav-sep"></span>
      <!-- Secondary nav (smaller, muted) -->
      <div class="nav-secondary">
        <a href="/blog">בלוג</a>
        <a href="/about">על נמרוד</a>
      </div>
      <!-- Contact — styled identically to secondary -->
      <a href="/contact" class="contact">צור קשר</a>
    </div>
  </div>
</nav>
```

**הערה קריטית:** "ידע" בטקסונומיה הפנימית (slug=`know`) → UI label "ייעוץ והוראה". אסור להחליף slug.

---

## 8. Footer — חוזה

4 עמודות:
1. Brand block — שם + tagline ("שורש אחד, שלושה עולמות. *Unless* בספארק")
2. עולמות — 3 קישורים (כולל "ייעוץ והוראה · ידע" שני קטן)
3. תוכן — בלוג + על נמרוד
4. קשר — אימייל ישיר + /contact

Bottom row: copyright + Unless quote ("העולם הוא כזה — *אלא אם כן*" בספארק).

רקע ink-color, טקסט paper. רוחב full-bleed, padding 64px top.

---

## 9. Accessibility, RTL, performance

### RTL
- `<html dir="rtl" lang="he">`
- **כל ה-CSS משתמש ב-logical properties:**
  - `inset-inline-start/end` במקום `left/right`
  - `margin-inline-start/end`
  - `padding-inline-start/end`
  - `border-inline-start/end`
- **חריגים:** `linear-gradient(to left, …)` — `to inline-end` לא תמיד נתמך, השתמש ב-`to left`/`to right` בכוונה לפי direction.

### A11y
- כל תמונה צריכה `alt` משמעותי (לא TBD).
- WCAG AA contrast לכל טקסט מעל background.
- כל interactive עם `:focus-visible` ברור (ב-system.css יש default).
- Forms: כל input עם `<label>` קשור.
- skip-to-content בראש העמוד.

### Performance
- Images: lazy loading בכל מקום מתחת ל-fold. `loading="lazy"`.
- Fonts: `display: swap`.
- CSS critical inline ב-T7 (Home). שאר העמודים — defer.
- אסור JS-heavy. דף הבית בלי JS לא חייב להישבר.

---

## 10. T-05 · WordPress migration (שייך לכם)

**מצב:** נמרוד מעריך ~50 פוסטים שכן עוברים (לא 480 שיש בארכיון). העברה היא אחריות צוות 110.

**מה לקבל ממנו:**
1. WordPress XML export (Tools → Export → All)
2. רשימת slugs ל-keep (או triage interface)

**מה לעשות בעת הייבוא:**
1. Map כל post → world-tags (soil/know/code, מרובה אפשרי)
2. Map כל post → flow_style (lead/wide/tall/typo/quote/feature/brief)
3. Slugs — לשמר את הקיימים (להוסיף 301 redirects אם המבנה השתנה)
4. תמונות — להעביר ל-`/public/uploads/`

**Data shape ל-post:**
```yaml
- id: post-back-to-mud
  title: "חזרה לבוץ — על למה הגינה נסגרה, ולמה אני שותל שוב"
  date_iso: "2026-03-19"
  excerpt: "לא חזרה, מטמורפוזה. שורש אחד, שלוש זרועות. Unless."
  worlds: [soil, know, code]
  tags: [מנפסט, מורשת, CDIP]
  read_time: "14 דק׳"
  flow_style: lead
  featured: true
  image: /uploads/back-to-mud.jpg
  body: <full HTML>
  related_entities:
    - { kind: "פעילות · גשר", title: "ייעוץ · תכנון חממה", href: "/services/consulting-hydro" }
    - { kind: "מיזם · own-venture", title: "הגינה של נמרוד", href: "/project/hagina-shel-nimrod" }
  toc:
    - { id: open, label: "פתיחה" }
    - …
```

**הקריטריון לכלול פוסט:** נמרוד מסמן בידיים. אם אין החלטה — אל תייבא.

---

## 11. תכולת קבצי העיצוב — כלם בתוך `_handoff/`

כל הקבצים זמינים **בתוך החבילה הזו**, self-contained. אין צורך לחזור לפרויקט המקור.

```
_handoff/                                ← אתם נמצאים פה
├── 00-HANDOFF-claude-code-110.md        ← הקובץ הזה
├── 01-PROMPT-watercolor-backgrounds.md  ← T-03
├── 02-PROMPT-logo-family.md             ← T-04
├── SESSION_HANDOFF.md                   ← session log + tickets
├── README.md                            ← אינדקס
│
├── brand/                               ← מקור-אמת לעיצוב
│   ├── system.css                       ← CSS tokens (LOCKED v3.3)
│   ├── TAXONOMY-v3.4-LOCKED.md          ← Source of truth on entities
│   ├── voice.md                         ← Tone of voice
│   ├── typography.md
│   ├── site-context-2026-05-v2.md       ← Brand canon
│   └── HANDOFF-Stage3.md                ← Previous stage summary
│
├── components/                          ← מקור-אמת לרכיבים
│   ├── Foundations.html                 ← Tokens reference page
│   ├── Components.html                  ← v2 atoms
│   └── Components v3 - Bridge.html      ← v3 Bridge (T-06 closed)
│
└── templates/                           ← 7 התבניות
    ├── T1 World - אדמה.html  +  T1-styles.css  +  T1-data.jsx  +  T1-variants.jsx
    ├── T2 Services.html      +  T2-styles.css  +  T2-data.jsx  +  T2-instances.jsx
    ├── T3 Project.html       +  T3-styles.css  +  T3-data.jsx  +  T3-instances.jsx
    ├── T4 Post.html          +  T4-styles.css
    ├── T5 Blog.html          +  T5-styles.css
    ├── T4-T5-data.jsx                   ← shared blog data
    ├── T7 Home.html          +  T7-styles.css
    ├── T8 Static.html        +  T8-styles.css
    └── tweaks-panel.jsx                 ← Tweaks framework
```

**איך לקרוא:** הקבצים הם **prototypes ב-React+Babel inline + CSS חיצוני**. ה-data structures + visual logic בכולם משקפים את החוזה שצריך להתקיים ב-WordPress production. אתם לא ממירים את ה-React — אתם משתמשים בהם כ-spec מצויר.

**הרצת prototype:** פתח כל `templates/T*.html` ישירות בדפדפן. עובד offline (חוץ מ-CDN ל-React+Babel+Google Fonts).

---

## 12. Tickets פתוחים שאתם תפגשו

| # | מה | מי אחראי | משפיע עליכם? |
|---|---|---|---|
| T-01 | BOOM A/B variant ב-T7 | צוות 35 בסשן עתידי | לא חוסם — בנו T7 כפי שהוא |
| T-02 | Mobile screens | Stage 5 (צוות 35) | החלק שלכם — responsive חייב לעבוד מ-T7 ראשית |
| T-03 | איורי רקע צבעי-מים | מנוע איורים | placeholders נשמרים עד אישור |
| T-04 | משפחת לוגו | מנוע איורים | לוגו זמני נשאר עד אישור |
| T-05 | ייבוא ארכיון WordPress | **צוות 110 (אתם)** | חובה לבצע במהלך הבנייה |
| T-07 | קובץ הסל המקורי | נמרוד | חוסם T-04 אבל לא אתכם |
| T-12 | אישור coop-sharon | נמרוד | אם לא יאושר — להחליף project ב-CMS |
| Q-02/03/05/09/10/11/NEW-03 | תוכן ספציפי | נמרוד | TBC markers בקוד — לקראת השקה |

---

## 13. Definition of Done לצוות 110

✅ כל 7 התבניות עובדות עם content אמיתי (לא placeholders)
✅ Shell + Footer עקביים בכל עמוד
✅ Bridge signal=seam פעיל גלובלית
✅ World filters עובדים ב-T5
✅ Flow + Grid views עובדים ב-T5
✅ פילוח תוכן לפי world עובד דרך כל המערכת
✅ WordPress XML imported, ~50 פוסטים מועברים עם world-tags
✅ Mobile responsive עד 360px wide
✅ WCAG AA contrast עובר ב-Lighthouse
✅ Performance score >85 ב-Lighthouse
✅ RTL נקי, ללא bugs ויזואליים
✅ כל form עם validation + error states
✅ WhatsApp links עובדים ל-`wa.me/972547776770`
✅ T-05 (ייבוא תוכן) מאושר ע"י נמרוד
✅ Lighthouse SEO score 100

---

## 14. נקודת-קשר לצוות 110

**שאלות עיצוב** → חזרה לצוות 35 (קובץ זה ולא ישירות לנמרוד)
**שאלות תוכן** → ישירות לנמרוד עם CC לצוות 35
**שאלות טכניות שלכם** → פנימי לצוות 110

**עדכוני סטטוס** → בקובץ זה תחת §13 (Definition of Done) — סמנו ✅ כשמסיימים.

**אם משהו בעיצוב נראה לא הגיוני — שאלו לפני שתחליטו לעשות אחרת.** הקבצים האלה עברו אישור מנהל אחרי איטרציה ארוכה. סטייה ללא דיון = שינוי חוזה.

---

## 15. עיתוי ועדיפויות

**שלב 1 (1-2 שבועות):**
- Bootstrap WordPress + theme structure
- system.css + tokens
- Shell + Footer
- T7 (Home) — דף הבית הוא המבחן הראשון של החוזה

**שלב 2 (2-3 שבועות):**
- T1 (3 worlds)
- T2 (services CPT + 3 dummy instances)
- T3 (projects CPT + 3 dummy instances)
- Bridge cards system

**שלב 3 (1-2 שבועות):**
- T4 + T5 (blog)
- T8 (static)
- Forms + WhatsApp integration

**שלב 4 (1 שבוע):**
- T-05 (WordPress XML import) — בעבודה משותפת עם נמרוד
- Polish + bug fixing
- Mobile QA

**סיום:** 6-8 שבועות. אם זה לא מסתדר — חזרו לצוות 35.

---

**חתימת סוף Handoff.**
*"שורש אחד, שלוש זרועות."* — בנו בהתאם.
