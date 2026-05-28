/* garden-journal.jsx — LOD300 direction "Garden Journal".
   Warm, illustrative, nimrod.bio-aligned. Uses watercolor SVG library. */

const GJ_PRODUCTS = [
  { name: 'עגבנייה', kind: 'tomato',     unit: 'ק"ג', avg: 12.40, med: 12.00, min: 9.5,  max: 16.0, sources: 6, n: 24, delta: '−4%' },
  { name: 'מלפפון',  kind: 'cucumber',   unit: 'ק"ג', avg: 9.20,  med: 9.00,  min: 7.0,  max: 12.0, sources: 5, n: 18, delta: '+1%' },
  { name: 'חסה',     kind: 'lettuce',    unit: 'יח׳', avg: 6.80,  med: 7.00,  min: 5.0,  max: 9.0,  sources: 4, n: 14, delta: '+2%' },
  { name: 'גזר',     kind: 'carrot',     unit: 'ק"ג', avg: 8.10,  med: 8.00,  min: 6.5,  max: 10.0, sources: 4, n: 11, delta: '0%'  },
  { name: 'פלפל אדום', kind: 'pepper',   unit: 'ק"ג', avg: 18.50, med: 18.00, min: 14.0, max: 24.0, sources: 5, n: 16, delta: '+6%' },
  { name: 'בצל יבש', kind: 'onion',      unit: 'ק"ג', avg: 5.40,  med: 5.00,  min: 4.0,  max: 7.5,  sources: 3, n: 9,  delta: '−2%' },
];

const GJ_CROPS = [
  { name: 'עגבנייה', en: 'Tomato',   kind: 'tomato',   cat: 'ירקות', dtm: 70, season: 'אביב·קיץ' },
  { name: 'חסה',     en: 'Lettuce',  kind: 'lettuce',  cat: 'עלים',  dtm: 45, season: 'סתיו·חורף' },
  { name: 'מלפפון',  en: 'Cucumber', kind: 'cucumber', cat: 'ירקות', dtm: 55, season: 'אביב' },
  { name: 'פלפל',    en: 'Pepper',   kind: 'pepper',   cat: 'ירקות', dtm: 95, season: 'קיץ' },
  { name: 'בזיליקום',en: 'Basil',    kind: 'basil',    cat: 'תיבול', dtm: 35, season: 'אביב' },
  { name: 'גזר',     en: 'Carrot',   kind: 'carrot',   cat: 'ירקות', dtm: 80, season: 'חורף' },
  { name: 'תות',     en: 'Strawberry', kind: 'strawberry', cat: 'פירות', dtm: 120, season: 'אביב' },
  { name: 'בצל',     en: 'Onion',    kind: 'onion',    cat: 'ירקות', dtm: 110, season: 'חורף' },
];

const PMIN = 4, PMAX = 24;

// ─── Shared garden-journal shell ───────────────────────────────────────
function GJShell({ children, mod = 'market', title, sub, fresh = 'עודכן הבוקר', sources = '14 מקורות', back = false, headerTone, hideTabs = false }) {
  return (
    <div className="gj-shell">
      <header className="gj-header gj-header--plain">
        <div className="gj-header__row">
          {back ? (
            <button className="gj-iconbtn" aria-label="חזרה">←</button>
          ) : (
            <div className="gj-mark"><GJMark/></div>
          )}
          <div className="gj-header__title">
            <div className="gj-title">{title}</div>
            <div className="gj-sub">{sub}</div>
          </div>
          <button className="gj-iconbtn" aria-label="חיפוש">⌕</button>
        </div>

        {!hideTabs && (
          <nav className="gj-tabs" role="tablist">
            <button className={`gj-tab ${mod === 'market' ? 'is-active' : ''}`}>מחירון</button>
            <button className={`gj-tab ${mod === 'book' ? 'is-active' : ''}`}>ספר גידולים</button>
          </nav>
        )}
      </header>

      <main className="gj-body">{children}</main>

      <footer className="gj-foot">
        <span className="gj-foot__dot"/>
        <span>{fresh}</span>
        {sources && <><span className="gj-foot__sep">·</span><span>{sources}</span></>}
        <span style={{ marginInlineStart: 'auto', opacity: .6 }}>SFA</span>
      </footer>
    </div>
  );
}

function GJMark() {
  return (
    <svg viewBox="0 0 40 40" width="36" height="36" aria-hidden="true">
      <g filter="url(#wc)">
        <circle cx="20" cy="20" r="14" fill="#f3ede0"/>
      </g>
      <g filter="url(#wc-rough)">
        <path d="M20 14 Q14 18 14 25 Q20 24 22 18 Q22 14 20 14 Z" fill="url(#wc-leaf)"/>
        <path d="M20 14 Q26 18 26 25 Q20 24 18 18 Q18 14 20 14 Z" fill="url(#wc-leaf-soft)"/>
        <path d="M20 14 L20 30" stroke="#506c34" strokeWidth="1.2"/>
      </g>
    </svg>
  );
}

// ═══════════════════════════════════════════════════════════════════════
// J1 · Home
// ═══════════════════════════════════════════════════════════════════════
function GJ_Home() {
  // NOTE: full home is now HubHome (in hub.jsx). This kept as a simpler variant
  // showing what the Crop-Book-only landing inside an embedded shell looks like.
  return (
    <GJShell mod="market" title="חקלאות קטנה" sub="שני כלים לחקלאים קטנים">
      <div className="gj-hero gj-hero--single">
        <window.ImagePrompt id="gj-home-hero" ratio="16/9" tone="leaf"
          title="רקע עליון"
          prompt={window.PROMPTS.hero_book}
          hint="להחלפה בתמונה אמיתית"/>
        <div className="gj-hero__copy" style={{ marginTop: 14 }}>
          <p className="gj-eyebrow">SFA · נימרוד.bio</p>
          <h1 className="gj-h1">
            לִמְצוֹא מָחִיר.<br/>
            <span className="gj-h1__accent">לְהָבִין גִּדּוּל.</span>
          </h1>
          <p className="gj-lede">
            כלי קטן לחוות קטנות. נתוני מחיר מנורמלים, ספר גידולים פתוח —
            בלי גלגלי שיווק, בלי הבטחות גדולות.
          </p>
        </div>
      </div>

      <a href="#" className="gj-card gj-card--market">
        <div className="gj-card__art"><window.Tomato size={64}/></div>
        <div className="gj-card__body">
          <span className="gj-card__eyebrow">01 · מחירון</span>
          <h3 className="gj-card__title">מדד מחירים</h3>
          <p className="gj-card__meta">30 מוצרים · 14 מקורות · ממוצע 7 ימים</p>
        </div>
        <span className="gj-card__arrow">←</span>
      </a>

      <a href="#" className="gj-card gj-card--book">
        <div className="gj-card__art"><window.Basil size={64}/></div>
        <div className="gj-card__body">
          <span className="gj-card__eyebrow">02 · ספר גידולים</span>
          <h3 className="gj-card__title">אינדקס פתוח</h3>
          <p className="gj-card__meta">66 גידולים · 242 זנים · 8 משפחות</p>
        </div>
        <span className="gj-card__arrow">←</span>
      </a>

      <div className="gj-stripe">
        <p>קטן זה יפה · לאט זה שפוי</p>
      </div>

      <section className="gj-section">
        <div className="gj-section__head">
          <h4 className="gj-section__title">השבוע בשטח</h4>
          <span className="gj-section__hint">3 הצצות</span>
        </div>
        <div className="gj-glance">
          <GJ_Glance kind="tomato" name="עגבנייה" sub="ק״ג · ‎−4%" big="12.40"/>
          <GJ_Glance kind="lettuce" name="חסה"    sub="עכשיו בעונה" big="חורף"/>
          <GJ_Glance kind="basil"   name="בזיליקום" sub="35 ימים DTM" big="מהיר"/>
        </div>
      </section>

      <p className="gj-privacy">
        🔒 נתונים מצרפיים · ללא חשיפת חוות בודדת · ‎412 ערכים מנורמלים · 94% פתרון
      </p>
    </GJShell>
  );
}

function GJ_Glance({ kind, name, sub, big }) {
  return (
    <div className="gj-glance__item">
      <div className="gj-glance__art"><window.CropIcon kind={kind} size={42}/></div>
      <div className="gj-glance__name">{name}</div>
      <div className="gj-glance__big">{big}</div>
      <div className="gj-glance__sub">{sub}</div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════
// J2 · Market list
// ═══════════════════════════════════════════════════════════════════════
function GJ_MarketList() {
  return (
    <GJShell mod="market" title="מדד מחירים" sub="הקציר של השבוע" headerTone="tomato" fresh="עודכן ‎14:32">
      <window.MarketDisclaimer />

      <div className="gj-page-head">
        <p className="gj-eyebrow">01 · מחירון</p>
        <h2 className="gj-h2">הקציר של <span className="gj-underline">השבוע</span></h2>
        <p className="gj-lede gj-lede--sm">
          ממוצע מתגלגל של 7 ימים. לחיצה על מוצר → גידול בספר.
        </p>
      </div>

      <div className="gj-chips">
        <span className="gj-chip is-active">הכל</span>
        <span className="gj-chip">🌱 מגדלים</span>
        <span className="gj-chip">🏪 חנויות</span>
        <span className="gj-chip">🏬 רשתות</span>
      </div>

      <div className="gj-list">
        {GJ_PRODUCTS.map((p, i) => <GJ_Row key={i} p={p}/>)}
      </div>

      <div className="gj-transparency">
        <h4>שקיפות</h4>
        <p>המספרים נאספים מהקהילה. הם משרתים אתכםן עד כמה שיהיו מדויקים — לא יותר, לא פחות.</p>
        <button>פתח מצב צינור הנירמול ↓</button>
      </div>

      <window.ContributeStrip context="מחירון · תרמת נתונים" placeholder="אצלי עגבנייה עולה 9.50 — אתמול…"/>
    </GJShell>
  );
}

function GJ_Row({ p }) {
  const startPct = ((p.min - PMIN) / (PMAX - PMIN)) * 100;
  const widthPct = ((p.max - p.min) / (PMAX - PMIN)) * 100;
  const down = p.delta.startsWith('−'), up = p.delta.startsWith('+');
  return (
    <a className="gj-row" href="#">
      <div className="gj-row__art"><window.CropIcon kind={p.kind} size={48}/></div>
      <div className="gj-row__body">
        <div className="gj-row__name">{p.name}</div>
        <div className="gj-row__meta">{p.unit} · {p.sources} מקורות · {p.n} תצפיות</div>
        <div className="gj-row__bar">
          <div className="gj-row__bar-fill" style={{ insetInlineEnd: `${startPct}%`, inlineSize: `${Math.max(widthPct, 4)}%` }}/>
        </div>
        <div className="gj-row__range">{p.min.toFixed(2)} – {p.max.toFixed(2)} ₪</div>
      </div>
      <div className="gj-row__price">
        <div className="gj-row__big">{p.avg.toFixed(2)}</div>
        <div className="gj-row__cur">₪</div>
        <div className={`gj-row__delta ${down ? 'is-down' : up ? 'is-up' : ''}`}>{p.delta}</div>
      </div>
    </a>
  );
}

// ═══════════════════════════════════════════════════════════════════════
// J3 · Crop book grid
// ═══════════════════════════════════════════════════════════════════════
function GJ_BookGrid() {
  return (
    <GJShell mod="book" title="ספר גידולים" sub="אינדקס פתוח · 66 גידולים" headerTone="leaf" fresh="snapshot · ‎13.05.26" sources="Tend · JMF">
      <div className="gj-page-head">
        <p className="gj-eyebrow">02 · ספר</p>
        <h2 className="gj-h2">מה לגדל <span className="gj-underline">השבוע</span>?</h2>
        <p className="gj-lede gj-lede--sm">סנן לפי משפחה, עונה ומשך זמן עד בגרות.</p>
      </div>

      <div className="gj-search">
        <span>⌕</span>
        <span className="gj-search__placeholder">עגבנייה, חסה, בזיליקום…</span>
      </div>

      <div className="gj-chips">
        <span className="gj-chip is-active gj-chip--leaf">הכל</span>
        <span className="gj-chip">ירקות</span>
        <span className="gj-chip">עלים</span>
        <span className="gj-chip">תיבול</span>
        <span className="gj-chip">קטניות</span>
        <span className="gj-chip">פירות</span>
        <span className="gj-chip">דגנים</span>
      </div>

      <div className="gj-slider">
        <span className="gj-slider__label">ימים לבגרות</span>
        <div className="gj-slider__track">
          <div className="gj-slider__fill" style={{ insetInlineEnd: 0, width: '62%' }}/>
          <div className="gj-slider__knob" style={{ insetInlineEnd: '62%' }}/>
        </div>
        <span className="gj-slider__value">≤ 90</span>
      </div>

      <div className="gj-grid">
        {GJ_CROPS.map((c, i) => <GJ_CropCard key={i} c={c}/>)}
      </div>

      <a href="#" className="gj-morelink">עוד 58 גידולים →</a>
    </GJShell>
  );
}

function GJ_CropCard({ c }) {
  return (
    <a className="gj-cropcard" href="#">
      <div className="gj-cropcard__art">
        <div className="gj-cropcard__icon"><window.CropIcon kind={c.kind} size={56}/></div>
      </div>
      <div className="gj-cropcard__body">
        <div className="gj-cropcard__name">{c.name}</div>
        <div className="gj-cropcard__en">{c.en}</div>
        <div className="gj-cropcard__meta">
          <span className="gj-tag">{c.cat}</span>
          <span className="gj-cropcard__dtm">{c.dtm}<small>ימים</small></span>
        </div>
      </div>
    </a>
  );
}

// ═══════════════════════════════════════════════════════════════════════
// J4 · Crop detail
// ═══════════════════════════════════════════════════════════════════════
function GJ_CropDetail() {
  return (
    <GJShell mod="book" title="חזרה לספר" sub="" headerTone="leaf" back hideTabs fresh="" sources="">
      <article className="gj-article">
        <div className="gj-article__head">
          <span className="gj-eyebrow">ירקות · משפחה Solanaceae</span>
          <h1 className="gj-h1 gj-h1--xl">
            <span className="gj-underline">עגבנייה</span>
          </h1>
          <p className="gj-sci">Solanum lycopersicum</p>
        </div>
        <div className="gj-article__art">
          <window.Tomato size={110}/>
        </div>
      </article>

      <a href="#" className="gj-crosslink">
        <div className="gj-crosslink__art"><window.Tomato size={48}/></div>
        <div className="gj-crosslink__body">
          <div className="gj-crosslink__big">12.40 <small>₪/ק״ג</small></div>
          <div className="gj-crosslink__sub">מחיר שוק נוכחי · ‎6 מקורות · ‎−4% משבוע</div>
        </div>
        <span className="gj-crosslink__cta">פתח →</span>
      </a>

      <nav className="gj-ctabs">
        <button className="is-active">זנים</button>
        <button>תיאור</button>
        <button>כלכלה</button>
        <button>טיפולים</button>
        <button>ציר זמן</button>
        <button>מקורות</button>
      </nav>

      <section className="gj-variety">
        <div className="gj-variety__head">
          <span className="gj-variety__star">★</span>
          <h3>תמר F1</h3>
          <span className="gj-tag gj-tag--code">מורכב</span>
        </div>
        <p className="gj-variety__lede">
          זן ברירת מחדל. שולי הכנסה גבוהים, שיווק יציב בחוות קטנות בשרון.
        </p>
        <dl className="gj-kv">
          <div><dt>עונת שתילה</dt><dd>פברואר–אפריל</dd></div>
          <div><dt>ימים לבגרות</dt><dd>68</dd></div>
          <div><dt>תשואה ל-מ״ר</dt><dd>9.2 ק״ג</dd></div>
          <div><dt>מחיר מתועד</dt><dd>11.50 ₪/ק״ג</dd></div>
        </dl>
      </section>

      <section className="gj-timeline">
        <h4>חיי הגידול</h4>
        <div className="gj-timeline__bar">
          <div className="gj-timeline__seg gj-timeline__seg--prep" style={{ width: '14%' }}>הכנה</div>
          <div className="gj-timeline__seg gj-timeline__seg--grow" style={{ width: '56%' }}>גידול</div>
          <div className="gj-timeline__seg gj-timeline__seg--harv" style={{ width: '30%' }}>קציר</div>
        </div>
        <div className="gj-timeline__ruler"><span>שבוע 1</span><span>שבוע 6</span><span>שבוע 12</span></div>
      </section>

      <section className="gj-sources">
        <h4 className="gj-sources__h">מקורות</h4>
        <ul>
          <li><strong>Tend CSV</strong><span>12 שדות</span></li>
          <li><strong>JMF XLSX</strong><span>4 שדות</span></li>
          <li><strong>נימרוד</strong><span>1 override</span></li>
        </ul>
      </section>

      <window.ContributeStrip context="ספר גידולים · עגבנייה" placeholder="זן חדש, תיקון, תצפית מהשדה…"/>

    </GJShell>
  );
}

// ═══════════════════════════════════════════════════════════════════════
// J5 · Market detail
// ═══════════════════════════════════════════════════════════════════════
function GJ_MarketDetail() {
  return (
    <GJShell mod="market" title="חזרה למחירון" sub="" headerTone="tomato" back hideTabs fresh="" sources="">
      <article className="gj-article">
        <div className="gj-article__head">
          <span className="gj-eyebrow">מחיר שוק · 7 ימים</span>
          <h1 className="gj-h1 gj-h1--xl"><span className="gj-underline">עגבנייה</span></h1>
          <p className="gj-sci">ק״ג · מחיר מנורמל</p>
        </div>
        <div className="gj-article__art"><window.Tomato size={110}/></div>
      </article>

      <div className="gj-pricebig">
        <span className="gj-pricebig__big">12.40</span>
        <span className="gj-pricebig__cur">₪</span>
        <span className="gj-pricebig__lbl">ממוצע</span>
        <span className="gj-pricebig__med">חציון 12.00 · ‎−4%</span>
      </div>

      <div className="gj-stats">
        <div><dt>טווח</dt><dd>9.50–16.00</dd></div>
        <div><dt>סטיית תקן</dt><dd>1.82</dd></div>
        <div><dt>מקורות</dt><dd>6 ●●●●●●</dd></div>
        <div><dt>תצפיות</dt><dd>24</dd></div>
      </div>

      <a href="#" className="gj-crosslink gj-crosslink--soil">
        <div className="gj-crosslink__art"><window.Tomato size={56}/></div>
        <div className="gj-crosslink__body">
          <div className="gj-crosslink__big" style={{ fontSize: 17 }}>פרטי הגידול בספר</div>
          <div className="gj-crosslink__sub">זנים · עונת שתילה · ‎DTM · ציר זמן</div>
        </div>
        <span className="gj-crosslink__cta">פתח →</span>
      </a>

      <section className="gj-sources">
        <h4 className="gj-sources__h">מקורות נתונים</h4>
        <p style={{ fontSize: 12, color: 'var(--ink-soft)', margin: '0 0 8px' }}>
          🔒 פרטיות: ‎4 מגדלים אנונימיים · 2 חנויות מקומיות. ללא חשיפת חווה בודדת.
        </p>
        <ul>
          <li><strong>מגדלים</strong><span>4 · 7 ימים</span></li>
          <li><strong>חנויות</strong><span>2 · 7 ימים</span></li>
        </ul>
      </section>
    </GJShell>
  );
}

// ═══════════════════════════════════════════════════════════════════════
// Asset library
// ═══════════════════════════════════════════════════════════════════════
function GJ_Library() {
  const icons = [
    ['Tomato',     'tomato'],     ['Lettuce',   'lettuce'],
    ['Cucumber',   'cucumber'],   ['Carrot',    'carrot'],
    ['Pepper',     'pepper'],     ['Onion',     'onion'],
    ['Basil',      'basil'],      ['Strawberry','strawberry'],
  ];
  const promptGroups = [
    {
      title: 'Heroes · רקעי גיבור',
      ratio: '16/9',
      items: [
        { name: 'מודול הב — דף בית',     tone: 'leaf',   key: 'module_hub' },
        { name: 'מחירון — תוצרת שורש',   tone: 'tomato', key: 'hero_market' },
        { name: 'ספר גידולים — שדה',     tone: 'leaf',   key: 'hero_book' },
        { name: 'מחשבון — שולחן רישום',  tone: 'sun',    key: 'hero_calc' },
        { name: 'פנייה — שני אנשים',     tone: 'soil',   key: 'contact' },
        { name: 'עגבנייה — גיבור',       tone: 'tomato', key: 'crop_hero' },
      ],
    },
    {
      title: 'Module thumbs · 1:1',
      ratio: '1/1',
      items: [
        { name: 'ספר',         tone: 'leaf',   key: 'module_thumb_book' },
        { name: 'מחירון',      tone: 'tomato', key: 'module_thumb_market' },
        { name: 'מחשבון',      tone: 'sun',    key: 'module_thumb_calc' },
        { name: 'תכנון עונה',  tone: 'leaf',   key: 'module_thumb_plan' },
        { name: 'לקוחות',      tone: 'soil',   key: 'module_thumb_clients' },
        { name: 'יבול',        tone: 'tomato', key: 'module_thumb_inv' },
        { name: 'Tend',        tone: 'soil',   key: 'module_thumb_tend' },
        { name: 'יומן שדה',    tone: 'leaf',   key: 'module_thumb_field' },
      ],
    },
  ];

  return (
    <div style={{ padding: '24px 28px', direction: 'rtl', background: 'var(--gj-paper)', overflow: 'auto', width: '100%', height: '100%' }}>
      <span className="gj-eyebrow">00 · LIBRARY</span>
      <h1 style={{ fontFamily: 'Frank Ruhl Libre, serif', fontSize: 30, fontWeight: 700, margin: '6px 0 6px', lineHeight: 1.1 }}>
        <span className="gj-underline">מילון</span> — אייקונים + פרומפטים לרקעים
      </h1>
      <p style={{ maxWidth: 720, color: 'var(--gj-ink-soft)', fontSize: 14, marginBottom: 24, lineHeight: 1.55 }}>
        אייקוני הירקות הם SVG מקומיים — מהירים, מותאמים, ברוח Costalita.art. הרקעים והגיבורים הם <strong>פרומפטים</strong> שיוזרמו לכלי AI חיצוני
        (Midjourney/SDXL) — כדי לקבל איור עם פירוט גבוה. כל סלוט מאפשר גרירת תמונה אמיתית במקום הפלייסהולדר.
      </p>

      <h2 style={{ fontFamily: 'Frank Ruhl Libre', fontWeight: 700, fontSize: 22, margin: '0 0 12px', borderBottom: '1px dashed var(--gj-line)', paddingBottom: 8 }}>
        אייקוני ירקות · SVG מקומי
      </h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 28 }}>
        {icons.map(([label, kind]) => (
          <div key={kind} style={{ background: 'var(--gj-paper-2)', borderRadius: 12, padding: 16, textAlign: 'center' }}>
            <window.CropIcon kind={kind} size={84}/>
            <div style={{ fontFamily: 'Frank Ruhl Libre', fontWeight: 600, fontSize: 14, marginTop: 6 }}>{label}</div>
            <div style={{ fontFamily: 'JetBrains Mono', fontSize: 10, color: 'var(--gj-ink-soft)', marginTop: 2 }}>kind="{kind}"</div>
          </div>
        ))}
      </div>

      {promptGroups.map(g => (
        <React.Fragment key={g.title}>
          <h2 style={{ fontFamily: 'Frank Ruhl Libre', fontWeight: 700, fontSize: 22, margin: '0 0 12px', borderBottom: '1px dashed var(--gj-line)', paddingBottom: 8 }}>
            {g.title}
          </h2>
          <div style={{
            display: 'grid',
            gridTemplateColumns: g.ratio === '1/1' ? 'repeat(4, 1fr)' : 'repeat(2, 1fr)',
            gap: 14, marginBottom: 28,
          }}>
            {g.items.map(it => (
              <window.ImagePrompt
                key={it.key}
                id={`lib-${it.key}`}
                tone={it.tone}
                ratio={g.ratio}
                title={it.name}
                prompt={window.PROMPTS[it.key]}
                hint={`PROMPTS.${it.key}`}
              />
            ))}
          </div>
        </React.Fragment>
      ))}

      <div style={{ padding: 14, background: 'var(--gj-paper-2)', borderRadius: 12, fontSize: 12, color: 'var(--gj-ink-soft)', fontFamily: 'JetBrains Mono', lineHeight: 1.55 }}>
        <strong style={{ color: 'var(--gj-ink)', fontFamily: 'Frank Ruhl Libre', fontWeight: 700, fontSize: 15 }}>הערות מימוש:</strong>{' '}
        כל פרומפט יוצר תמונה ב-1:1 או 16:9. סגנון אחיד — Costalita.art / nimrod.bio: אקוורל חם, רקע נייר קרם, פלטה ירוק-זית + טראקוטה + חמאה. ללא טקסט בתוך התמונה. ניתן לגרור תמונה אמיתית לתוך כל סלוט וה-image-slot ישמור אותה.
      </div>
    </div>
  );
}

Object.assign(window, {
  GJ_Home, GJ_MarketList, GJ_BookGrid, GJ_CropDetail, GJ_MarketDetail, GJ_Library,
});
