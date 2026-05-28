# Nimrod.bio — Typography

## מקור

האתר nimrod.bio בנוי על WordPress + Elementor (תמת hello-elementor). בבדיקה של מחלקות ה־CSS באתר החי, גוף הטקסט העברי משתמש ב־**Assistant** (Google Fonts) — זוהי ברירת המחדל הנפוצה באתרי Elementor בעברית, והיא תואמת את האופי הקריא־ללא־יומרות של האתר.

### Fallback stack מומלץ

```css
font-family: "Assistant", "Heebo", system-ui, -apple-system, "Segoe UI", sans-serif;
```

- **Assistant** — הפונט הראשי. נקי, ידידותי, נטול קישוטים, תומך היטב בעברית ולטינית.
- **Heebo** — fallback קרוב; גם הוא Google Font עברי מוסקיילי לעברית.
- **system-ui** — כדי שעד שהפונט נטען, הדף ייראה סביר.

### Import

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
```

---

## סקאלה טיפוגרפית

| שימוש            | משקל | גודל    | שורה   | הערות                              |
| ---------------- | ---- | ------- | ------ | ---------------------------------- |
| Display / Hero   | 700  | 56–72px | 1.05   | לכותרות עמוד בודדות                |
| H1 / Page title  | 700  | 40px    | 1.15   | ראשי עמוד                          |
| H2 / Section     | 600  | 28px    | 1.25   | מחלק מקטעים                        |
| H3 / Card title  | 600  | 20px    | 1.3    | שם שירות, שם פוסט                  |
| Body             | 400  | 17px    | 1.65   | ברירת מחדל. נדיב, נושם             |
| Body small       | 400  | 14px    | 1.55   | מטא־דאטה, תאריכים                  |
| Quote / Manifest | 300  | 22–26px | 1.5    | ציטוטים, משפטי ערך                 |
| Button / UI      | 600  | 15–16px | 1      | קצר, ממוקד                         |

## Pairing

אין פונט שני. גם כותרות וגם גוף על Assistant — ההבדל נעשה ע"י משקל וגודל. זה תואם את אופי המותג (מינימליסטי, לא פלקטיבי). אם יש צורך בניגוד, אפשר להוסיף מונוספייס בצניעות לקטעי קוד/פרטים טכניים:

```css
font-family: "JetBrains Mono", ui-monospace, Menlo, monospace;
```

## כללי RTL

- `direction: rtl` על `<html>` הראשי.
- `text-wrap: pretty` על כותרות, `text-wrap: balance` על מניפסטים קצרים.
- הימנע מ־justify על טקסט ארוך בעברית — מייצר "רודפים" של רווחים.
