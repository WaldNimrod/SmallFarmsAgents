/* art-prompts.jsx — ImagePrompt slot: visual placeholder + art-direction
   prompt for an external image-generation engine.
   Renders a tinted box with the prompt text + copy button + image-slot
   integration so a user can drop a real image in. */

function ImagePrompt({
  id,            // stable id for image-slot persistence
  tone = 'leaf', // visual tint of the placeholder
  ratio = '16/9',
  height,        // explicit height in px (overrides ratio)
  prompt,        // the art direction string (Hebrew or English)
  title = 'רקע',
  hint,          // small caption shown under prompt
  enableSlot = false,  // expensive — only enable on a few opt-in slots
}) {
  const map = {
    leaf:   '#a3b97a',
    tomato: '#e89a78',
    sun:    '#e8c468',
    soil:   '#b8916a',
    sky:    '#a8bcc6',
    paper:  '#d5cab0',
  };
  const tint = map[tone] || map.leaf;

  const wrapStyle = {
    position: 'relative',
    width: '100%',
    aspectRatio: height ? undefined : ratio,
    height: height || undefined,
    background: `linear-gradient(135deg, ${tint} 0%, ${tint}cc 100%)`,
    borderRadius: 12,
    overflow: 'hidden',
    border: `1px dashed color-mix(in oklch, ${tint} 60%, black)`,
  };

  const copy = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (navigator.clipboard) navigator.clipboard.writeText(prompt);
  };

  return (
    <div style={wrapStyle}>
      {/* Real image slot — opt-in, expensive (custom-element + localStorage per instance) */}
      {id && enableSlot && (
        <image-slot
          id={id}
          shape="rect"
          radius="0"
          style={{ position: 'absolute', inset: 0, zIndex: 1, opacity: 0.001, pointerEvents: 'auto' }}
          placeholder=""
        ></image-slot>
      )}

      {/* Visual prompt UI on top of tint */}
      <div style={{
        position: 'relative', zIndex: 2,
        height: '100%', padding: '10px 12px',
        display: 'flex', flexDirection: 'column', justifyContent: 'space-between',
        pointerEvents: 'none',
        background: 'linear-gradient(180deg, rgba(255,255,255,.06), rgba(0,0,0,.06))',
        color: 'rgba(20, 15, 10, .85)',
      }}>
        <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', gap: 8 }}>
          <div>
            <div style={{ fontFamily: '"JetBrains Mono", monospace', fontSize: 9, letterSpacing: '.1em', textTransform: 'uppercase', opacity: .75, marginBottom: 2 }}>
              IMG · prompt for AI gen
            </div>
            <div style={{ fontFamily: '"Frank Ruhl Libre", serif', fontWeight: 700, fontSize: 13, lineHeight: 1.1 }}>{title}</div>
          </div>
          <button onClick={copy} style={{
            pointerEvents: 'auto',
            appearance: 'none', border: '1px solid rgba(0,0,0,.3)',
            background: 'rgba(255,255,255,.4)',
            padding: '3px 8px', borderRadius: 99,
            fontFamily: 'inherit', fontSize: 10, fontWeight: 700,
            cursor: 'pointer', color: 'inherit',
          }}>העתק פרומפט</button>
        </div>

        <div style={{
          fontFamily: 'system-ui, sans-serif', fontSize: 11, lineHeight: 1.4,
          maxHeight: '70%', overflow: 'auto', direction: 'rtl',
          background: 'rgba(255,255,255,.35)', borderRadius: 6, padding: '6px 8px',
          fontFeatureSettings: '"liga" 0',
          pointerEvents: 'auto',
        }}>
          {prompt}
        </div>

        {hint && (
          <div style={{ fontFamily: '"JetBrains Mono", monospace', fontSize: 9, opacity: .7, marginTop: 4 }}>
            ↳ {hint}
          </div>
        )}
      </div>
    </div>
  );
}

// Library of named prompts (reused across mockups + library)
const PROMPTS = {
  hero_market: 'איור בסגנון אקוורל חם וסגנון nimrod.bio. מבט-על על שולחן עץ מחוספס פרושים עליו ירקות שורש: גזרים, סלק, בצל, צלפים, צרורות פטרוזיליה. אור בוקר רך מהצד הימני, צללים ארוכים וחמימים. פלטה: טראקוטה אדמדמה, ירוק זית, חרדל-זהב, קרם נייר. דחיסות גבוהה במרכז, שוליים בהירים יותר. ללא טקסט. 16:9.',
  hero_book:   'איור בסגנון אקוורל חם וסגנון nimrod.bio. שדה חקלאות אקולוגית קטנה בפרדס חנה — שורות גידול ירוקות-עמוקות בעוקבות-עוקבות, ערפל בוקר עדין, מעט שמש מבצבצת בקצה השמאל-עליון. שתי דמויות מטושטשות בעבודת שדה ברקע. פלטה: ירוק עמוק, כחול-אפור ערפילי, צהוב חמאתי. תחושת "קטן זה יפה, לאט זה שפוי". ללא טקסט. 16:9.',
  hero_calc:   'איור בסגנון אקוורל חם וסגנון nimrod.bio. שולחן עבודה כפרי — מחברת מקופלת עם רישומי עיפרון של מספרים וערוגות, סרגל עץ ישן, ספל קפה, מגוון זרעים בכפיות כפולות מעוצבים בצורת רכוז דאטה. פלטה: חום-קקאו, ירוק זית, קרם, מעט תכלת. רגוע, מתמטי-יד. ללא טקסט. 16:9.',
  module_hub:  'איור בסגנון אקוורל חם וסגנון nimrod.bio. מבט מלמעלה על שולחן עבודה של חקלאי-מתכנן — מפת ערוגות צבועה ביד, סרגל, פרוסות תפוז, גזיר עיתון, צרור מרווה. אווירה של "סדנת מחקר ביתית". פלטה: קרם דהוי, ירוק זית, חמרה-טראקוטה, צל-כחול. ללא טקסט. 16:9.',
  module_thumb_book:  'איור אקוורל קטן וריבועי. צרור ירוקים — חסה, בזיליקום, פטרוזיליה — בצרור קצר. פלטה ירוקה רכה עם רקע קרם נייר. ללא טקסט. 1:1.',
  module_thumb_market:'איור אקוורל קטן וריבועי. שלושה גזרים על קופסת עץ קטנה, מבט מהצד. פלטה כתום-טראקוטה עם רקע קרם נייר. ללא טקסט. 1:1.',
  module_thumb_calc:  'איור אקוורל קטן וריבועי. מחברת חוט-ספירלי פתוחה עם רישומי דמויות-ערוגות וחישובים בעט עפרון. פלטה חום-קקאו עם רקע קרם. ללא טקסט. 1:1.',
  module_thumb_plan:  'איור אקוורל קטן וריבועי. לוח שנה חקלאי עם איקונים של ירקות, סימוני סהר ושמש. פלטה ירוק-זית עם רקע קרם. ללא טקסט. 1:1.',
  module_thumb_clients:'איור אקוורל קטן וריבועי. ספל קפה ומשקפיים על דפים — לקוחות-נאמנים. פלטה חום-קפה עם רקע קרם. ללא טקסט. 1:1.',
  module_thumb_inv:   'איור אקוורל קטן וריבועי. ארגז עץ עם תוצרת מגוונת — תות, עגבנייה, סלרי. פלטה אדומה-ירוקה עם רקע קרם. ללא טקסט. 1:1.',
  module_thumb_tend:  'איור אקוורל קטן וריבועי. דף קווי אקסל-מעוצב-יד עם מספרים, חיבור צינור-משאבה דקורטיבי. פלטה אפור-תכלת עם רקע קרם. ללא טקסט. 1:1.',
  module_thumb_field: 'איור אקוורל קטן וריבועי. כלי עבודה — מעדר ויד-חופרת — מונחים על אדמה. פלטה חום-אדמה עם רקע קרם. ללא טקסט. 1:1.',
  crop_hero:  'איור אקוורל גדול של עגבנייה אדומה-בוערת בודדת, סגנון ספר טבע ילדים-מבוגרים, רקע נייר מעט מצהיב, צל קל תחת הירק. פלטה אדום-עגבנייה עמוק עם ירוק עלים. ללא טקסט. 4:3.',
  bg_paper:   'טקסטורת רקע: נייר עתיק קרם עם סיבים עדינים וכתמי דהוי קלים. ללא איורים. 16:9. אורגני, מעט גרגירי.',
  contact:    'איור אקוורל חם. שני אנשים יושבים על ספסל-עץ פשוט מול חממה קטנה, שיחה ידידותית. פלטה אדמה-ירוק-חמאה. ללא טקסט. 16:9.',
};

Object.assign(window, { ImagePrompt, PROMPTS });
