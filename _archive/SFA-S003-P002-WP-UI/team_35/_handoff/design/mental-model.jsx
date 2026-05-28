/* mental-model.jsx — system overview diagram artboard */

function MentalModel() {
  // Layout shows: WP page → SFA template (no nimrod.bio chrome) → 2 modules + cross-links + shared data
  return (
    <div className="mental" style={{ direction: 'rtl' }}>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 14, marginBottom: 6 }}>
        <span style={{ fontFamily: 'JetBrains Mono', fontSize: 11, letterSpacing: '.1em', textTransform: 'uppercase', color: 'var(--w-know-deep)' }}>01 · מנטל מודל</span>
        <span style={{ fontFamily: 'JetBrains Mono', fontSize: 11, color: 'var(--ink-soft)' }}>system overview</span>
      </div>
      <h1 style={{ fontFamily: 'Frank Ruhl Libre, serif', fontSize: 36, fontWeight: 700, margin: '0 0 4px', letterSpacing: '-.01em' }}>
        מערכת אחת, שני מודולים — <span className="underline-spark">בלי המסגרת של nimrod.bio</span>
      </h1>
      <p style={{ maxWidth: 720, color: 'var(--ink-soft)', fontSize: 15, lineHeight: 1.55, margin: '0 0 24px' }}>
        אותה סביבת WordPress, אותם shortcodes שכבר חיים בפרודקשן. מה שמשתנה: ה-template — חילוץ מהמסגרת של nimrod.bio
        וקבלת shell עצמאי שהוא ה-home של הכלי. שני המודולים יושבים תחת כותרת אחת, מתחלפים בלשונית, וחוצים מידע ביניהם.
      </p>

      <svg viewBox="0 0 880 400" style={{ width: '100%', maxWidth: 880, display: 'block', fontFamily: 'Assistant, sans-serif' }}>
        {/* WP page outer */}
        <rect x="10" y="10" width="860" height="380" fill="none" stroke="#b8b3a0" strokeDasharray="4 4" rx="12"/>
        <text x="858" y="30" textAnchor="end" fontSize="11" fontFamily="JetBrains Mono" fill="#8b8772" letterSpacing=".05em">WORDPRESS PAGE · /sfa/</text>

        {/* SFA template shell */}
        <rect x="40" y="50" width="800" height="320" fill="var(--paper)" stroke="var(--ink)" strokeWidth="1.5" rx="14"/>
        <text x="836" y="72" textAnchor="end" fontSize="11" fontFamily="JetBrains Mono" fill="var(--ink-soft)" letterSpacing=".05em">SFA TEMPLATE · standalone shell</text>

        {/* Header strip */}
        <rect x="40" y="50" width="800" height="36" fill="var(--paper-2)" stroke="var(--line)" rx="14"/>
        <rect x="40" y="76" width="800" height="10" fill="var(--paper-2)" stroke="none"/>
        <circle cx="64" cy="68" r="9" fill="var(--w-soil-deep)"/>
        <text x="84" y="72" fontSize="13" fontWeight="700" fontFamily="Frank Ruhl Libre">SFA — סוכני חוות קטנות</text>

        {/* Module tabs */}
        <rect x="60" y="100" width="200" height="34" rx="20" fill="var(--paper-2)"/>
        <rect x="64" y="104" width="96"  height="26" rx="18" fill="var(--paper)" stroke="var(--w-know)" strokeWidth="1.5"/>
        <circle cx="76" cy="117" r="3" fill="var(--w-know-deep)"/>
        <text x="84" y="121" fontSize="12" fontWeight="700">מחירון</text>
        <circle cx="174" cy="117" r="3" fill="var(--w-soil)"/>
        <text x="182" y="121" fontSize="12" fontWeight="600" fill="var(--ink-soft)">ספר גידולים</text>

        {/* Module A : Market */}
        <rect x="80" y="158" width="340" height="170" rx="12"
              fill="color-mix(in oklch, var(--w-know) 7%, var(--paper))"
              stroke="var(--w-know)" strokeWidth="1.5"/>
        <text x="100" y="184" fontSize="13" fontWeight="700" fill="var(--w-know-deep)" fontFamily="Frank Ruhl Libre">מדד מחירים · ממשק המחירון</text>
        <text x="100" y="200" fontSize="10" fontFamily="JetBrains Mono" fill="var(--ink-soft)">[sfagent_market_report]</text>
        <text x="100" y="222" fontSize="11" fill="var(--ink)">· רשימת מוצרים · ממוצע · חציון</text>
        <text x="100" y="238" fontSize="11" fill="var(--ink)">· טווח · סטיית תקן · ספירת מקורות</text>
        <text x="100" y="254" fontSize="11" fill="var(--ink)">· סינון מקור (מגדלים/חנויות/רשתות)</text>
        <text x="100" y="270" fontSize="11" fill="var(--ink)">· dq-box שקיפות + פרטיות</text>
        <text x="100" y="294" fontSize="10" fontFamily="JetBrains Mono" fill="var(--w-know-deep)">~ 30 מוצרים · 7-day rolling avg</text>

        {/* Module B : Crop book */}
        <rect x="460" y="158" width="340" height="170" rx="12"
              fill="color-mix(in oklch, var(--w-soil) 7%, var(--paper))"
              stroke="var(--w-soil)" strokeWidth="1.5"/>
        <text x="480" y="184" fontSize="13" fontWeight="700" fill="var(--w-soil-deep)" fontFamily="Frank Ruhl Libre">ספר גידולים</text>
        <text x="480" y="200" fontSize="10" fontFamily="JetBrains Mono" fill="var(--ink-soft)">[sfagent_crop_book]</text>
        <text x="480" y="222" fontSize="11" fill="var(--ink)">· גריד גידולים · קטגוריות · עונה · DTM</text>
        <text x="480" y="238" fontSize="11" fill="var(--ink)">· 8 לשוניות לכל גידול</text>
        <text x="480" y="254" fontSize="11" fill="var(--ink)">· ציר זמן · זנים · ציוד · מקורות</text>
        <text x="480" y="270" fontSize="11" fill="var(--ink)">· entity-tooltips באוצר מונחים</text>
        <text x="480" y="294" fontSize="10" fontFamily="JetBrains Mono" fill="var(--w-soil-deep)">66 crops · 242 varieties (snapshot)</text>

        {/* Cross-link arrows */}
        <path d="M 420 215 C 440 210 440 210 460 215" stroke="var(--w-know-deep)" strokeWidth="1.5" fill="none" markerEnd="url(#arr-know)"/>
        <path d="M 460 260 C 440 265 440 265 420 260" stroke="var(--w-soil-deep)" strokeWidth="1.5" fill="none" markerEnd="url(#arr-soil)"/>
        <text x="440" y="206" textAnchor="middle" fontSize="9" fontFamily="JetBrains Mono" fill="var(--w-know-deep)">crop→price</text>
        <text x="440" y="278" textAnchor="middle" fontSize="9" fontFamily="JetBrains Mono" fill="var(--w-soil-deep)">price→crop</text>

        <defs>
          <marker id="arr-know" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">
            <path d="M0 0 L 6 3 L 0 6 z" fill="var(--w-know-deep)"/>
          </marker>
          <marker id="arr-soil" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">
            <path d="M0 0 L 6 3 L 0 6 z" fill="var(--w-soil-deep)"/>
          </marker>
        </defs>

        {/* Footer */}
        <rect x="40" y="332" width="800" height="38" fill="var(--paper-2)" stroke="var(--line)" rx="14"/>
        <rect x="40" y="332" width="800" height="10" fill="var(--paper-2)" stroke="none"/>
        <circle cx="64" cy="352" r="4" fill="var(--w-soil)"/>
        <text x="76" y="356" fontSize="11" fontFamily="JetBrains Mono" fill="var(--ink-soft)">עודכן לפני 2 שעות · 14 מקורות · SFA v0.1</text>
      </svg>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 16, marginTop: 24 }}>
        <Principle num="01" title="כותרת אחת, שני שערים">
          ה-shell מארח את שני המודולים תחת זהות אחת. החלפה ב-tab — לא ב-URL חדש — שומרת על תחושת אפליקציה אחת.
        </Principle>
        <Principle num="02" title="חוצה מידע">
          גידול בספר → מצביע על מחיר השוק שלו. מוצר במחירון → מצביע על הגידול בספר. הקישור הוא העיקר.
        </Principle>
        <Principle num="03" title="נטול מסגרת nimrod.bio">
          אין header של האתר, אין footer של Elementor, אין hero של החקלאי. רק הכלי. ה-shortcode-ים נשארים זהים.
        </Principle>
      </div>

      <div style={{ marginTop: 20, padding: 14, background: 'var(--paper-2)', borderRadius: 12, fontSize: 12, color: 'var(--ink-soft)', fontFamily: 'JetBrains Mono' }}>
        <strong style={{ color: 'var(--ink)' }}>הערות מימוש (לא מחייב):</strong> &nbsp;
        ה-shell יכול להיות (א) page-template בתמת flatsome-child שמטעין רק את ה-2 shortcodes זה לצד זה,
        או (ב) shortcode-של-shortcodes <code style={{ background: 'var(--paper)', padding: '0 4px', borderRadius: 3 }}>[sfagent_app]</code> שמכיל את שניהם.
        החלטה זו תופיע ב-LOD400.
      </div>
    </div>
  );
}

function Principle({ num, title, children }) {
  return (
    <div style={{ borderTop: '2px solid var(--ink)', paddingTop: 10 }}>
      <div style={{ fontFamily: 'JetBrains Mono', fontSize: 10, color: 'var(--w-know-deep)', letterSpacing: '.08em', marginBottom: 4 }}>{num}</div>
      <h4 style={{ fontFamily: 'Frank Ruhl Libre', fontWeight: 700, fontSize: 17, margin: '0 0 6px' }}>{title}</h4>
      <p style={{ fontSize: 13, lineHeight: 1.5, margin: 0, color: 'var(--ink-soft)' }}>{children}</p>
    </div>
  );
}

Object.assign(window, { MentalModel });
