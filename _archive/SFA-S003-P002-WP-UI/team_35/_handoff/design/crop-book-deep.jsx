/* crop-book-deep.jsx — Crop Book as a knowledge base.
   The book is FOUNDATIONAL — it powers every other module.
   Multiple entry paths:
     CB_Entry        - master landing with 4 question-based entries
     CB_QuestionView - "what to grow now / spring / winter / quick" grid
     CB_FamilyTree   - by botanical family
     CB_ProTable     - full professional table (desktop-friendly)
     CB_Search       - advanced search with chips + range sliders
     CB_CropFull     - single crop page with variety hierarchy
     CB_Variety      - single variety page (deep)
*/

const FAMILIES = [
  { id: 'sol', name: 'סולנציאות', en: 'Solanaceae', crops: ['עגבנייה','פלפל','חציל','תפו״א'], color: 'tomato', icon: 'tomato' },
  { id: 'cuc', name: 'דלועיים',   en: 'Cucurbitaceae', crops: ['מלפפון','דלעת','קישוא','אבטיח'], color: 'leaf', icon: 'cucumber' },
  { id: 'bra', name: 'מצליבים',   en: 'Brassicaceae', crops: ['כרוב','ברוקולי','קולרבי','צנון'], color: 'sun', icon: 'lettuce' },
  { id: 'fab', name: 'קטניות',    en: 'Fabaceae', crops: ['שעועית','אפונה','חומוס','עדשים'], color: 'leaf', icon: 'basil' },
  { id: 'api', name: 'סוככיים',   en: 'Apiaceae', crops: ['גזר','פטרוזיליה','כוסברה','שמיר'], color: 'sun', icon: 'carrot' },
  { id: 'ast', name: 'מורכבים',   en: 'Asteraceae', crops: ['חסה','חסה זקופה','חמנייה','ארטישוק'], color: 'leaf', icon: 'lettuce' },
  { id: 'all', name: 'שושניים',   en: 'Amaryllidaceae', crops: ['בצל','שום','בצל ירוק','כרישה'], color: 'soil', icon: 'onion' },
  { id: 'lam', name: 'שפתניים',   en: 'Lamiaceae', crops: ['בזיליקום','נענע','מרווה','רוזמרין'], color: 'leaf', icon: 'basil' },
];

const CB_QUESTIONS = [
  { q: 'מה לגדל עכשיו?',     sub: 'מאי 2026 · ‎חתימת אביב', count: 14, season: 'אביב' },
  { q: 'מה מהיר?',            sub: 'DTM ≤ 50 ימים',           count: 11, season: 'מהיר' },
  { q: 'מה הכי רווחי?',       sub: 'לפי מחיר/יבול/שטח',       count: 8,  season: 'רווחי' },
  { q: 'מה מתאים לחממה?',     sub: 'מבוקר טמפ׳ ולחות',         count: 22, season: 'חממה' },
  { q: 'מה מתאים לשטח פתוח?', sub: 'עמיד למזג אוויר',          count: 38, season: 'שדה' },
  { q: 'מה לגדל בחורף?',      sub: 'דצמבר–פברואר',             count: 17, season: 'חורף' },
  { q: 'מה לגדל בקיץ?',       sub: 'יוני–אוגוסט · ‎חום',       count: 19, season: 'קיץ' },
  { q: 'מה חוסך עבודה?',      sub: 'תחזוקה נמוכה',             count: 9,  season: 'low-work' },
];

const TOMATO_VARIETIES = [
  { id: 'tamar',    name: 'תמר F1',     hybrid: true,  dtm: 68, color: 'אדום', shape: 'אשכולי', resistance: 'TYLCV', yield: 9.2, taste: 4, default: true },
  { id: 'shari',    name: 'שרי תאיה',   hybrid: false, dtm: 60, color: 'אדום', shape: 'דובדבן',  resistance: '—',     yield: 5.8, taste: 5, default: false },
  { id: 'beef',     name: 'ביף F1',     hybrid: true,  dtm: 78, color: 'אדום', shape: 'בקר',     resistance: 'ToMV',   yield: 11.4, taste: 3, default: false },
  { id: 'black',    name: 'שחור קרים',  hybrid: false, dtm: 75, color: 'שחור', shape: 'מורשת',   resistance: '—',      yield: 6.0, taste: 5, default: false },
  { id: 'green',    name: 'זברה ירוקה', hybrid: false, dtm: 78, color: 'ירוק', shape: 'מורשת',   resistance: '—',      yield: 5.5, taste: 5, default: false },
  { id: 'roma',     name: 'רומא',       hybrid: false, dtm: 72, color: 'אדום', shape: 'אגס',     resistance: '—',      yield: 7.8, taste: 4, default: false },
];

// ═══════════════════════════════════════════════════════════════════════
// CB_Entry — master landing inside crop-book module
// ═══════════════════════════════════════════════════════════════════════
function CB_Entry() {
  return (
    <div className="gj-shell">
      <header className="gj-header gj-header--plain">
        <div className="gj-header__row">
          <button className="gj-iconbtn">←</button>
          <div className="gj-header__title">
            <div className="gj-title">ספר גידולים</div>
            <div className="gj-sub">בסיס ידע · 66 גידולים · ‎242 זנים</div>
          </div>
          <button className="gj-iconbtn">⌕</button>
        </div>
      </header>

      <main className="gj-body cb-entry">
        <p className="gj-eyebrow">02 · ספר גידולים</p>
        <h2 className="gj-h2">בסיס הידע<br/><span className="gj-underline">של החקלאות הקטנה.</span></h2>
        <p className="gj-lede gj-lede--sm">
          לא "מה לגדל עכשיו". <em>מתי ואיך</em> לגדל כל גידול. סבא המידע של כל הכלים האחרים.
        </p>

        <h3 className="cb-section-h">איך להתחיל?</h3>
        <div className="cb-paths">
          <a className="cb-path cb-path--ask" href="#">
            <div className="cb-path__icon">?</div>
            <div>
              <div className="cb-path__name">שאלות מנחות</div>
              <div className="cb-path__sub">מה לגדל עכשיו · במהירות · בחממה · בחורף · ‎8 כניסות</div>
            </div>
            <span className="cb-path__arrow">←</span>
          </a>
          <a className="cb-path cb-path--family" href="#">
            <div className="cb-path__icon"><window.CropIcon kind="tomato" size={28}/></div>
            <div>
              <div className="cb-path__name">לפי משפחה צמחית</div>
              <div className="cb-path__sub">סולנציאות · דלועיים · מצליבים · ‎8 משפחות</div>
            </div>
            <span className="cb-path__arrow">←</span>
          </a>
          <a className="cb-path cb-path--table" href="#">
            <div className="cb-path__icon">▦</div>
            <div>
              <div className="cb-path__name">תצוגה מקצועית · טבלה</div>
              <div className="cb-path__sub">כל הגידולים והזנים, כל הנתונים — לסינון ומיון</div>
            </div>
            <span className="cb-path__arrow">←</span>
          </a>
          <a className="cb-path cb-path--search" href="#">
            <div className="cb-path__icon">⌕</div>
            <div>
              <div className="cb-path__name">חיפוש מתקדם</div>
              <div className="cb-path__sub">DTM · עונה · עמידות · יבול · שיקול שיווקי</div>
            </div>
            <span className="cb-path__arrow">←</span>
          </a>
        </div>

        <h3 className="cb-section-h">מה הכי נצפה השבוע</h3>
        <div className="cb-trending">
          {['עגבנייה','חסה','בזיליקום','מלפפון','גזר'].map(name => (
            <a key={name} className="cb-trend" href="#">
              <window.CropIcon kind={({עגבנייה:'tomato',חסה:'lettuce',בזיליקום:'basil',מלפפון:'cucumber',גזר:'carrot'})[name]} size={36}/>
              <span>{name}</span>
            </a>
          ))}
        </div>

        <window.ContributeStrip context="ספר · ‎תרמו ידע" placeholder="זן חסר? מקור חדש? תיקון?"/>
      </main>

      <footer className="gj-foot">
        <span className="gj-foot__dot"/>
        <span>snapshot 13.05.26 · Tend · JMF · נימרוד</span>
      </footer>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════
// CB_QuestionView — "what to grow" question grid
// ═══════════════════════════════════════════════════════════════════════
function CB_QuestionView() {
  return (
    <div className="gj-shell">
      <header className="gj-header gj-header--plain">
        <div className="gj-header__row">
          <button className="gj-iconbtn">←</button>
          <div className="gj-header__title">
            <div className="gj-title">שאלות מנחות</div>
            <div className="gj-sub">מצא לפי צורך, לא לפי שם</div>
          </div>
        </div>
      </header>
      <main className="gj-body">
        <p className="gj-eyebrow">ספר · מסלול א׳</p>
        <h2 className="gj-h2">מאיפה <span className="gj-underline">להתחיל?</span></h2>
        <p className="gj-lede gj-lede--sm">8 שאלות נפוצות → רשימת גידולים מותאמת.</p>

        <div className="cb-qgrid">
          {CB_QUESTIONS.map((q, i) => (
            <a key={i} className="cb-qcard" href="#">
              <div className="cb-qcard__num">{String(i+1).padStart(2,'0')}</div>
              <h3 className="cb-qcard__q">{q.q}</h3>
              <p className="cb-qcard__sub">{q.sub}</p>
              <div className="cb-qcard__count">{q.count} <small>גידולים</small></div>
            </a>
          ))}
        </div>

        <div className="cb-qhint">
          <strong>טיפ:</strong> אם לא מצאת שאלה — לחץ על חיפוש מתקדם וסנן לפי קריטריונים.
        </div>
      </main>
      <footer className="gj-foot"><span className="gj-foot__dot"/><span>8 כניסות נפוצות · ‎אוחזק בשטח</span></footer>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════
// CB_FamilyTree — by botanical family
// ═══════════════════════════════════════════════════════════════════════
function CB_FamilyTree() {
  return (
    <div className="gj-shell">
      <header className="gj-header gj-header--plain">
        <div className="gj-header__row">
          <button className="gj-iconbtn">←</button>
          <div className="gj-header__title">
            <div className="gj-title">לפי משפחה צמחית</div>
            <div className="gj-sub">חשובה לרוטציה ולמחלות</div>
          </div>
        </div>
      </header>
      <main className="gj-body">
        <p className="gj-eyebrow">ספר · מסלול ב׳</p>
        <h2 className="gj-h2"><span className="gj-underline">משפחה</span> צמחית = רוטציה</h2>
        <p className="gj-lede gj-lede--sm">
          לא שותלים שני גידולים מאותה משפחה ברציפות באותה ערוגה. הספר מציג את המבנה הביולוגי שיעזור לכם לתכנן.
        </p>

        <div className="cb-fam-list">
          {FAMILIES.map(f => (
            <a key={f.id} className={`cb-fam cb-fam--${f.color}`} href="#">
              <div className="cb-fam__head">
                <window.CropIcon kind={f.icon} size={42}/>
                <div>
                  <div className="cb-fam__he">{f.name}</div>
                  <div className="cb-fam__en">{f.en}</div>
                </div>
                <span className="cb-fam__count">{f.crops.length}</span>
              </div>
              <div className="cb-fam__crops">
                {f.crops.map((c,i) => <span key={i} className="pill pill--muted">{c}</span>)}
              </div>
            </a>
          ))}
        </div>
      </main>
      <footer className="gj-foot"><span className="gj-foot__dot"/><span>8 משפחות · ‎66 גידולים</span></footer>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════
// CB_ProTable — full table (mobile preview; full version in desktop.jsx)
// ═══════════════════════════════════════════════════════════════════════
function CB_ProTable() {
  const rows = [
    { name: 'עגבנייה', fam: 'סולנציאות', vars: 22, dtm: '60–78', yield: '5.5–11.4', price: 12.40, season: 'אביב·קיץ' },
    { name: 'מלפפון',  fam: 'דלועיים',  vars: 14, dtm: '50–60', yield: '8.0–14.0', price: 9.20,  season: 'אביב' },
    { name: 'חסה',     fam: 'מורכבים',  vars: 18, dtm: '35–55', yield: '2.5–4.2',  price: 6.80,  season: 'סתיו·חורף' },
    { name: 'פלפל',    fam: 'סולנציאות', vars: 12, dtm: '80–110', yield: '4.5–9.0', price: 18.50, season: 'קיץ' },
    { name: 'גזר',     fam: 'סוככיים',  vars: 11, dtm: '70–90', yield: '6.5–11.0', price: 8.10,  season: 'חורף' },
    { name: 'בצל',     fam: 'שושניים',  vars: 9,  dtm: '90–120', yield: '5.5–9.0', price: 5.40,  season: 'חורף·אביב' },
    { name: 'בזיליקום',fam: 'שפתניים',  vars: 8,  dtm: '30–40', yield: '0.9–1.4',  price: 24.00, season: 'אביב·קיץ' },
  ];
  return (
    <div className="gj-shell">
      <header className="gj-header gj-header--plain">
        <div className="gj-header__row">
          <button className="gj-iconbtn">←</button>
          <div className="gj-header__title">
            <div className="gj-title">תצוגה מקצועית</div>
            <div className="gj-sub">טבלה מלאה · ‎בדסקטופ זה רחב יותר</div>
          </div>
          <button className="gj-iconbtn">⇅</button>
        </div>
      </header>
      <main className="gj-body" style={{ padding: '12px 0 80px' }}>
        <div style={{ padding: '0 16px 12px' }}>
          <p className="gj-eyebrow">ספר · מסלול ג׳</p>
          <h2 className="gj-h2"><span className="gj-underline">כל הנתונים</span> בטבלה אחת</h2>
        </div>

        <div className="cb-table">
          <div className="cb-table__head">
            <span>שם</span>
            <span>משפ׳</span>
            <span>זנים</span>
            <span>DTM</span>
            <span>יבול</span>
            <span>שוק</span>
          </div>
          {rows.map((r, i) => (
            <a key={i} className="cb-table__row" href="#">
              <span className="cb-table__name">{r.name}</span>
              <span className="cb-table__fam">{r.fam}</span>
              <span className="cb-table__num">{r.vars}</span>
              <span className="cb-table__num">{r.dtm}</span>
              <span className="cb-table__num">{r.yield}</span>
              <span className="cb-table__num cb-table__num--accent">{r.price.toFixed(2)}</span>
            </a>
          ))}
        </div>

        <div style={{ padding: '14px 16px', fontSize: 11, color: 'var(--gj-ink-soft)', textAlign: 'center' }}>
          7 מתוך 66 · <a href="#" style={{ color: 'var(--gj-leaf-deep)', fontWeight: 700 }}>טען את כל הטבלה →</a>
        </div>
      </main>
      <footer className="gj-foot"><span className="gj-foot__dot"/><span>snapshot · ‎יצוא ל-CSV אפשרי</span></footer>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════
// CB_Search — advanced search/filter
// ═══════════════════════════════════════════════════════════════════════
function CB_Search() {
  return (
    <div className="gj-shell">
      <header className="gj-header gj-header--plain">
        <div className="gj-header__row">
          <button className="gj-iconbtn">←</button>
          <div className="gj-header__title">
            <div className="gj-title">חיפוש מתקדם</div>
            <div className="gj-sub">לפי DTM, עונה, יבול…</div>
          </div>
        </div>
      </header>
      <main className="gj-body">
        <p className="gj-eyebrow">ספר · מסלול ד׳</p>
        <h2 className="gj-h2">סנן <span className="gj-underline">לפי קריטריון</span></h2>

        <div className="cb-search-form">
          <fieldset>
            <legend>שם / מילת מפתח</legend>
            <input type="search" placeholder="עגבנייה, F1, שרי, מורשת…"/>
          </fieldset>

          <fieldset>
            <legend>משפחה</legend>
            <div className="cb-chip-row">
              <span className="gj-chip is-active gj-chip--leaf">הכל</span>
              {FAMILIES.slice(0,5).map(f => <span key={f.id} className="gj-chip">{f.name}</span>)}
            </div>
          </fieldset>

          <fieldset>
            <legend>עונת שתילה</legend>
            <div className="cb-chip-row">
              {['אביב','קיץ','סתיו','חורף'].map(s => <span key={s} className="gj-chip">{s}</span>)}
            </div>
          </fieldset>

          <fieldset>
            <legend>ימים לבגרות (DTM)</legend>
            <div className="cb-range">
              <div className="cb-range__bar"><div className="cb-range__fill" style={{ insetInlineEnd: '20%', width: '50%' }}/></div>
              <div className="cb-range__labels"><span>30</span><span>180 ימים</span></div>
              <div className="cb-range__current">40 – 90 ימים</div>
            </div>
          </fieldset>

          <fieldset>
            <legend>קונטקסט גידול</legend>
            <div className="cb-chip-row">
              <span className="gj-chip">שדה פתוח</span>
              <span className="gj-chip">חממה</span>
              <span className="gj-chip">בית רשת</span>
            </div>
          </fieldset>

          <fieldset>
            <legend>שיקול שיווקי</legend>
            <div className="cb-chip-row">
              <span className="gj-chip">מחיר שוק ≥ ₪10</span>
              <span className="gj-chip">יבול ≥ 5 ק״ג/מ״ר</span>
              <span className="gj-chip">DTM ≤ 60</span>
            </div>
          </fieldset>
        </div>

        <button className="cb-search-submit">
          הצג <strong>23</strong> תוצאות
        </button>

        <p className="cb-search-tip">
          💡 הקריטריונים מצטרפים כ-AND. השאר ריק כדי להתעלם.
        </p>
      </main>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════
// CB_CropFull — single crop with VARIETY hierarchy
// ═══════════════════════════════════════════════════════════════════════
function CB_CropFull() {
  return (
    <div className="gj-shell">
      <header className="gj-header gj-header--plain">
        <div className="gj-header__row">
          <button className="gj-iconbtn">←</button>
          <div className="gj-header__title">
            <div className="gj-title">עגבנייה</div>
            <div className="gj-sub">‏Solanum lycopersicum · ‎סולנציאות</div>
          </div>
          <button className="gj-iconbtn">⌕</button>
        </div>
      </header>

      <main className="gj-body">
        <article className="cb-crop-hero">
          <window.Tomato size={70}/>
          <div>
            <div className="cb-crop-hero__breadcrumb">
              <a href="#">ספר</a> <span>›</span> <a href="#">סולנציאות</a> <span>›</span> <strong>עגבנייה</strong>
            </div>
            <h1 className="cb-crop-hero__h"><span className="gj-underline">עגבנייה</span></h1>
            <p className="cb-crop-hero__meta">22 זנים · ‎70 ימים DTM ממוצע · ‎12.40 ₪/ק״ג שוק</p>
          </div>
        </article>

        <window.CrossLinkMarket />

        <nav className="cb-deep-tabs">
          <button className="is-active">סקירה</button>
          <button>22 זנים</button>
          <button>גידול</button>
          <button>מחלות</button>
          <button>קציר</button>
          <button>שיווק</button>
          <button>מקורות</button>
        </nav>

        <section className="cb-deep-section">
          <h3>סקירה כללית</h3>
          <p>
            עגבנייה היא הגידול המוביל בחוות קטנות בארץ. שולי הכנסה גבוהים יחסית, אבל רגישה למחלות (TYLCV, נמטודות).
            הזנים מתחלקים לאשכוליים, דובדבן (cherry), בקר (beef), מורשת. הבחירה משפיעה על שיווק (סלים? חנויות?).
          </p>
          <dl className="cb-spec-grid">
            <div><dt>שם בעברית</dt><dd>עגבנייה</dd></div>
            <div><dt>שם מדעי</dt><dd><em>Solanum lycopersicum</em></dd></div>
            <div><dt>משפחה</dt><dd>סולנציאות</dd></div>
            <div><dt>DTM</dt><dd>60–78 ימים</dd></div>
            <div><dt>יבול</dt><dd>5.5–11.4 ק״ג/מ״ר</dd></div>
            <div><dt>עונה</dt><dd>אביב · קיץ</dd></div>
            <div><dt>מרווח שתילה</dt><dd>50 × 50 ס״מ</dd></div>
            <div><dt>חממה?</dt><dd>מומלץ — שליטה במחלות</dd></div>
          </dl>
        </section>

        <section className="cb-deep-section">
          <div className="cb-vars-head">
            <h3>זנים <small>· ‎22</small></h3>
            <div className="cb-vars-sort">
              <span>סדר:</span>
              <button className="is-active">ברירת מחדל</button>
              <button>טעם</button>
              <button>יבול</button>
              <button>DTM</button>
            </div>
          </div>
          {TOMATO_VARIETIES.map(v => <VarietyRow key={v.id} v={v}/>)}
          <a href="#" className="cb-vars-more">+ 16 זנים נוספים</a>
        </section>

        <window.ContributeStrip context="עגבנייה · ‎ספר" placeholder="זן חסר? נתון מדוייק יותר?"/>
      </main>
    </div>
  );
}

function VarietyRow({ v }) {
  return (
    <a className="cb-var" href="#">
      <div className="cb-var__head">
        {v.default && <span className="cb-var__star">★</span>}
        <h4>{v.name}</h4>
        {v.hybrid && <span className="pill pill--code">F1 · מורכב</span>}
        {!v.hybrid && <span className="pill pill--muted">מורשת</span>}
      </div>
      <div className="cb-var__grid">
        <span><small>DTM</small>{v.dtm}</span>
        <span><small>יבול</small>{v.yield} <em>ק״ג/מ״ר</em></span>
        <span><small>צבע</small>{v.color}</span>
        <span><small>צורה</small>{v.shape}</span>
        <span><small>טעם</small>{'★'.repeat(v.taste)}<em style={{ opacity:.3 }}>{'★'.repeat(5-v.taste)}</em></span>
        <span><small>עמידות</small>{v.resistance}</span>
      </div>
    </a>
  );
}

// inline cross-link to market
function CrossLinkMarket() {
  return (
    <a href="#" className="gj-crosslink" style={{ margin: '0 0 14px' }}>
      <div className="gj-crosslink__art"><window.Tomato size={48}/></div>
      <div className="gj-crosslink__body">
        <div className="gj-crosslink__big">12.40 <small>₪/ק״ג שוק</small></div>
        <div className="gj-crosslink__sub">ממוצע 7 ימים · ‎6 מקורות · ‎−4% משבוע</div>
      </div>
      <span className="gj-crosslink__cta">פתח →</span>
    </a>
  );
}

Object.assign(window, {
  CB_Entry, CB_QuestionView, CB_FamilyTree, CB_ProTable, CB_Search, CB_CropFull,
  CrossLinkMarket, FAMILIES, CB_QUESTIONS, TOMATO_VARIETIES,
});
