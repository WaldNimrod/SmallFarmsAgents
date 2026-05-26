/* desktop.jsx — desktop variants (1200×800) for the key screens.
   Layout: app sidebar + main content + community rail. */

function DesktopShell({ children, active = 'hub', title, sub }) {
  return (
    <div className="dt-shell">
      <aside className="dt-side">
        <div className="dt-side__brand">
          <window.HubMark/>
          <div>
            <div className="dt-side__name">SFA</div>
            <div className="dt-side__tag">חקלאות קטנה</div>
          </div>
        </div>

        <input type="search" placeholder="חיפוש בכל המערכת…" className="dt-side__search"/>

        <nav className="dt-nav">
          {/* Tier 1 — open community (default expanded) */}
          <details className="dt-acc" open>
            <summary>
              <span className="tier tier--leaf"><span className="tier__glyph">●</span>כלים לקהילה</span>
              <span className="dt-acc__chev">▾</span>
            </summary>
            <a className={active === 'hub'    ? 'is-active' : ''} href="#">דף הבית</a>
            <a className={active === 'book'   ? 'is-active' : ''} href="#">ספר גידולים <span className="dt-nav__count">66</span></a>
            <a className={active === 'market' ? 'is-active' : ''} href="#">מחירון <span className="dt-nav__count">30</span></a>
            <a className={active === 'calc'   ? 'is-active' : ''} href="#">מחשבון <span className="pill pill--code dt-nav__pill">β</span></a>
          </details>

          {/* Tier 3 — paid */}
          <details className="dt-acc">
            <summary>
              <span className="tier tier--soil"><span className="tier__glyph">★</span>כלים מתקדמים</span>
              <span className="dt-acc__chev">▾</span>
            </summary>
            <a href="#">תכנון עונה <span className="pill pill--muted dt-nav__pill">בקרוב</span></a>
            <a href="#">ניהול לקוחות <span className="pill pill--soil dt-nav__pill">₪</span></a>
            <a href="#">מעקב יבול ומלאי <span className="pill pill--soil dt-nav__pill">₪</span></a>
          </details>

          {/* Tier 2 — custom */}
          <details className="dt-acc">
            <summary>
              <span className="tier tier--tomato"><span className="tier__glyph">✎</span>בדיוק לחווה שלך</span>
              <span className="dt-acc__chev">▾</span>
            </summary>
            <a href="#">חיבור Tend</a>
            <a href="#">יומן שדה</a>
            <a className="dt-nav__cta" href="https://wa.me/972547776770">+ הציעו כלי חדש</a>
          </details>

          {/* Community — collapsible side panel */}
          <details className="dt-acc dt-acc--comm" open>
            <summary>
              <span className="tier tier--sun"><span className="tier__glyph">✺</span>קהילה</span>
              <span className="dt-acc__chev">▾</span>
            </summary>

            <div className="dt-side__stats">
              <div><strong>247</strong><span>תיקונים</span></div>
              <div><strong>34</strong><span>הצעות</span></div>
              <div><strong>87</strong><span>חברים</span></div>
            </div>

            <div className="dt-side__contrib">
              <a href="#" className="dt-side__crow">✎ תרמו ידע</a>
              <a href="#" className="dt-side__crow">◐ דווחו על שגיאה</a>
              <a href="#" className="dt-side__crow">💡 הציעו פיצ׳ר</a>
              <a href="#" className="dt-side__crow">✦ הציעו מודול</a>
            </div>

            <div className="dt-side__feedh">פעילות אחרונה</div>
            <window.FeedItem kind="data" name="רחל ש." date="3ש'" text="4 זנים של חסה נוספו" tag="חסה" upvotes={18}/>
            <window.FeedItem kind="correction" name="יואב ל." date="היום" text="עגבנייה — 11.50 ₪" tag="עגבנייה" upvotes={4}/>
            <window.FeedItem kind="suggest" name="דניאל ב." date="שבוע" text="יומן רישום קצירות" tag="פיצ׳ר" upvotes={9}/>
            <a href="#" className="dt-side__more">כל ההצעות →</a>

            <a href="https://wa.me/972547776770" className="dt-side__wa">
              💬 WhatsApp · ‎צ׳אט פתוח
            </a>
          </details>
        </nav>

        <footer className="dt-side__foot">
          <div className="hub-foot__motto" style={{ fontSize: 12, color: 'var(--gj-soil-deep)' }}>קטן זה יפה</div>
          <div style={{ fontSize: 10, color: 'var(--gj-ink-soft)', fontFamily: 'JetBrains Mono' }}>SFA · ‎nimrod.bio</div>
        </footer>
      </aside>

      <main className="dt-main">
        <header className="dt-topbar">
          <div>
            <h1 className="dt-topbar__h">{title}</h1>
            {sub && <p className="dt-topbar__sub">{sub}</p>}
          </div>
          <div className="dt-topbar__tools">
            <button className="dt-topbar__contrib">+ תרמו ידע</button>
            <button className="dt-topbar__login">היכנס / הירשם</button>
          </div>
        </header>
        <div className="dt-content">{children}</div>
      </main>
    </div>
  );
}

// ─── Desktop · Hub ────────────────────────────────────────────────────
function Desktop_Hub() {
  return (
    <DesktopShell active="hub" title="כלים גדולים לחוות קטנות" sub="מערכת אחת · ‎8 מודולים · ‎3 רמות · ‎בנייה הדרגתית">
      <section className="dt-hub-hero">
        <div className="dt-hub-hero__copy">
          <p className="gj-eyebrow">SFA · ‎nimrod.bio</p>
          <h2 className="dt-hub-hero__h">
            <span className="gj-underline">קטן זה יפה.</span><br/>
            לאט זה שפוי.
          </h2>
          <p className="dt-hub-hero__lede">
            מערכת קהילתית פתוחה, בנייה הדרגתית. כלים לקהילה לתמיד — כלים מתקדמים לחוות פעילות, וכלים שנבנים בדיוק לחווה שלך.
          </p>
          <div className="dt-hub-hero__ctas">
            <a className="dt-btn dt-btn--primary" href="#">פתחו את הספר</a>
            <a className="dt-btn dt-btn--ghost" href="#">איך זה עובד? →</a>
          </div>
        </div>
        <div className="dt-hub-hero__art">
          <window.ImagePrompt id="dt-hub-hero" ratio="16/9" tone="leaf"
            title="גיבור דסקטופ"
            prompt={window.PROMPTS.module_hub}/>
        </div>
      </section>

      <section className="dt-section">
        <header className="dt-section__head">
          <window.TierBadge tier="open" size="lg"/>
          <h3>כלים לקהילה</h3>
          <p>פתוח, חינמי, ללא הרשמה.</p>
        </header>
        <div className="dt-modgrid">
          {window.MODULES.filter(m => m.tier === 'open' || m.tier === 'beta').map(m =>
            <window.ModuleThumb key={m.id} m={m}/>
          )}
        </div>
      </section>

      <section className="dt-section">
        <header className="dt-section__head">
          <window.TierBadge tier="paid" size="lg"/>
          <h3>כלים מתקדמים</h3>
          <p>לחוות פעילות שצריכות יותר.</p>
        </header>
        <div className="dt-modgrid">
          {window.MODULES.filter(m => m.tier === 'paid').map(m =>
            <window.ModuleThumb key={m.id} m={m}/>
          )}
        </div>
      </section>

      <section className="dt-section">
        <header className="dt-section__head">
          <window.TierBadge tier="custom" size="lg"/>
          <h3>בדיוק לחווה שלך</h3>
          <p>אינטגרציות וכלים מותאמים אישית.</p>
        </header>
        <div className="dt-modgrid">
          {window.MODULES.filter(m => m.tier === 'custom').map(m =>
            <window.ModuleThumb key={m.id} m={m}/>
          )}
        </div>
        <a href="https://wa.me/972547776770" className="dt-suggest">
          <strong>+ הציעו כלי חדש</strong>
          <span>שיחה של 15 דקות → הצעה. ‎WhatsApp 054-7776770</span>
        </a>
      </section>
    </DesktopShell>
  );
}

// ─── Desktop · Crop book pro table ───────────────────────────────────
function Desktop_CropBookProTable() {
  const rows = [
    { name: 'עגבנייה',  fam: 'סולנציאות',  vars: 22, dtm: '60–78', yield: '5.5–11.4', price: 12.40, season: 'אביב·קיץ', context: 'חממה+שדה' },
    { name: 'פלפל',     fam: 'סולנציאות',  vars: 12, dtm: '80–110', yield: '4.5–9.0', price: 18.50, season: 'קיץ',     context: 'חממה' },
    { name: 'חציל',     fam: 'סולנציאות',  vars: 7,  dtm: '75–90', yield: '4.0–7.5',  price: 14.20, season: 'קיץ',     context: 'חממה+שדה' },
    { name: 'מלפפון',   fam: 'דלועיים',   vars: 14, dtm: '50–60', yield: '8.0–14.0', price: 9.20,  season: 'אביב',    context: 'חממה+שדה' },
    { name: 'דלעת',     fam: 'דלועיים',   vars: 9,  dtm: '90–120', yield: '7.0–12.0', price: 7.50, season: 'סתיו',    context: 'שדה' },
    { name: 'חסה',      fam: 'מורכבים',   vars: 18, dtm: '35–55', yield: '2.5–4.2',  price: 6.80,  season: 'סתיו·חורף', context: 'שדה+חממה' },
    { name: 'גזר',      fam: 'סוככיים',   vars: 11, dtm: '70–90', yield: '6.5–11.0', price: 8.10,  season: 'חורף',    context: 'שדה' },
    { name: 'פטרוזיליה', fam: 'סוככיים',   vars: 5,  dtm: '45–60', yield: '1.0–1.8',  price: 14.00, season: 'כל השנה', context: 'שדה+חממה' },
    { name: 'בזיליקום',  fam: 'שפתניים',   vars: 8,  dtm: '30–40', yield: '0.9–1.4',  price: 24.00, season: 'אביב·קיץ', context: 'חממה' },
    { name: 'בצל',      fam: 'שושניים',   vars: 9,  dtm: '90–120', yield: '5.5–9.0', price: 5.40,  season: 'חורף·אביב', context: 'שדה' },
    { name: 'שום',      fam: 'שושניים',   vars: 6,  dtm: '180–240', yield: '0.8–1.5', price: 32.00, season: 'סתיו→קיץ', context: 'שדה' },
    { name: 'תות',      fam: 'ורדיים',     vars: 11, dtm: '90–120', yield: '0.4–0.9', price: 22.00, season: 'חורף·אביב', context: 'חממה' },
  ];
  return (
    <DesktopShell active="book" title="ספר גידולים · תצוגה מקצועית" sub="66 גידולים · ‎242 זנים · ‎לסנן, למיין, ליצא ל-CSV">
      {/* Path picker reminder */}
      <div className="dt-path-tabs">
        <a className="dt-path-tab is-active" href="#">▦ טבלה</a>
        <a className="dt-path-tab" href="#">? שאלות מנחות</a>
        <a className="dt-path-tab" href="#"><window.CropIcon kind="tomato" size={16}/> משפחה</a>
        <a className="dt-path-tab" href="#">⌕ חיפוש מתקדם</a>
      </div>

      {/* Filters bar */}
      <div className="dt-filters">
        <input type="search" placeholder="חיפוש שם / מילת מפתח…" className="dt-filters__search"/>
        <select><option>כל המשפחות</option><option>סולנציאות</option><option>דלועיים</option></select>
        <select><option>כל העונות</option><option>אביב</option><option>קיץ</option></select>
        <select><option>כל הקונטקסטים</option><option>חממה</option><option>שדה</option></select>
        <span className="dt-filters__results">{rows.length} מתוך 66</span>
        <button>יצוא CSV</button>
      </div>

      <div className="dt-table">
        <div className="dt-table__head">
          <span>שם</span>
          <span>משפחה</span>
          <span>זנים ↓</span>
          <span>DTM</span>
          <span>יבול ק״ג/מ״ר</span>
          <span>מחיר שוק</span>
          <span>עונה</span>
          <span>קונטקסט</span>
        </div>
        {rows.map((r, i) => (
          <a key={i} className="dt-table__row" href="#">
            <span className="dt-table__name">
              <window.CropIcon kind={({עגבנייה:'tomato',פלפל:'pepper',חציל:'pepper',מלפפון:'cucumber',דלעת:'cucumber',חסה:'lettuce',גזר:'carrot',פטרוזיליה:'basil',בזיליקום:'basil',בצל:'onion',שום:'onion',תות:'strawberry'})[r.name] || 'lettuce'} size={28}/>
              <strong>{r.name}</strong>
            </span>
            <span>{r.fam}</span>
            <span className="dt-table__num">{r.vars}</span>
            <span className="dt-table__num">{r.dtm}</span>
            <span className="dt-table__num">{r.yield}</span>
            <span className="dt-table__num dt-table__num--accent">{r.price.toFixed(2)} ₪</span>
            <span style={{ fontSize: 11 }}>{r.season}</span>
            <span style={{ fontSize: 11 }}>{r.context}</span>
          </a>
        ))}
      </div>

      <p style={{ textAlign: 'center', marginTop: 12, fontSize: 12, color: 'var(--gj-ink-soft)' }}>
        מציג 12 מתוך 66. <a href="#" style={{ color: 'var(--gj-leaf-deep)', fontWeight: 700 }}>טען עוד →</a>
      </p>
    </DesktopShell>
  );
}

// ─── Desktop · Market ────────────────────────────────────────────────
function Desktop_Market() {
  const items = [
    { name: 'עגבנייה',  kind: 'tomato',   unit: 'ק״ג', avg: 12.40, med: 12.00, min: 9.5,  max: 16.0, sources: 6, n: 24, delta: '−4%' },
    { name: 'פלפל אדום', kind: 'pepper',   unit: 'ק״ג', avg: 18.50, med: 18.00, min: 14.0, max: 24.0, sources: 5, n: 16, delta: '+6%' },
    { name: 'מלפפון',   kind: 'cucumber', unit: 'ק״ג', avg: 9.20,  med: 9.00,  min: 7.0,  max: 12.0, sources: 5, n: 18, delta: '+1%' },
    { name: 'חסה',      kind: 'lettuce',  unit: 'יח׳', avg: 6.80,  med: 7.00,  min: 5.0,  max: 9.0,  sources: 4, n: 14, delta: '+2%' },
    { name: 'גזר',      kind: 'carrot',   unit: 'ק״ג', avg: 8.10,  med: 8.00,  min: 6.5,  max: 10.0, sources: 4, n: 11, delta: '0%' },
    { name: 'בצל',      kind: 'onion',    unit: 'ק״ג', avg: 5.40,  med: 5.00,  min: 4.0,  max: 7.5,  sources: 3, n: 9,  delta: '−2%' },
    { name: 'בזיליקום',  kind: 'basil',    unit: 'ק״ג', avg: 24.00, med: 23.00, min: 18.0, max: 30.0, sources: 4, n: 8,  delta: '+8%' },
    { name: 'תות',      kind: 'strawberry', unit: 'ק״ג', avg: 22.00, med: 22.00, min: 18.0, max: 28.0, sources: 5, n: 13, delta: '−3%' },
  ];
  return (
    <DesktopShell active="market" title="מחירון · ‎מדד מחירי תוצרת" sub="ממוצע 7 ימים · ‎14 מקורות · ‎עודכן 14:32">
      <window.MarketDisclaimerFull />

      <div className="dt-filters">
        <div className="gj-chips" style={{ margin: 0, gap: 6 }}>
          <span className="gj-chip is-active">הכל</span>
          <span className="gj-chip">🌱 מגדלים</span>
          <span className="gj-chip">🏪 חנויות</span>
          <span className="gj-chip">🏬 רשתות</span>
        </div>
        <select><option>מיין: שם א-ת</option><option>מחיר עולה</option><option>מחיר יורד</option><option>שינוי</option></select>
        <span className="dt-filters__results">{items.length} מוצרים</span>
        <button>יצוא CSV</button>
      </div>

      <div className="dt-mkt-grid">
        {items.map((p, i) => {
          const PMIN = 4, PMAX = 30;
          const startPct = ((p.min - PMIN) / (PMAX - PMIN)) * 100;
          const widthPct = ((p.max - p.min) / (PMAX - PMIN)) * 100;
          const down = p.delta.startsWith('−');
          const up = p.delta.startsWith('+');
          return (
            <a key={i} className="dt-mkt-card" href="#">
              <div className="dt-mkt-card__art"><window.CropIcon kind={p.kind} size={56}/></div>
              <div className="dt-mkt-card__body">
                <h4>{p.name}</h4>
                <div className="dt-mkt-card__meta">{p.unit} · {p.sources} מקורות · {p.n} תצפיות</div>
                <div className="dt-mkt-card__bar">
                  <div className="dt-mkt-card__bar-fill" style={{ insetInlineEnd: `${startPct}%`, inlineSize: `${Math.max(widthPct, 4)}%` }}/>
                </div>
                <div className="dt-mkt-card__range">{p.min.toFixed(2)} – {p.max.toFixed(2)} ₪</div>
              </div>
              <div className="dt-mkt-card__price">
                <div className="dt-mkt-card__big">{p.avg.toFixed(2)}</div>
                <div className="dt-mkt-card__cur">₪/{p.unit}</div>
                <div className={`dt-mkt-card__delta ${down ? 'is-down' : up ? 'is-up' : ''}`}>{p.delta}</div>
              </div>
            </a>
          );
        })}
      </div>
    </DesktopShell>
  );
}

// ─── Market disclaimer (mobile + desktop variants) ────────────────────
function MarketDisclaimer() {
  return (
    <div className="mk-disclaimer">
      <div className="mk-disclaimer__head">
        <span className="mk-disclaimer__icon">ⓘ</span>
        <h4 className="mk-disclaimer__h">מה זה? מאיפה זה? למה זה?</h4>
      </div>
      <ul className="mk-disclaimer__list">
        <li><strong>מה:</strong> ממוצעים מתגלגלים של מחירי תוצרת חקלאית טרייה — 7 ימים אחרונים.</li>
        <li><strong>מאיפה:</strong> סוכני סריקה ציבוריים של mezoo + תרומות חקלאים. ‎מצרפי, אנונימי.</li>
        <li><strong>למה:</strong> כלי שיווקי קהילתי. הוכחה שאפשר ידע פתוח גם בשוק החקלאי הקטן.</li>
        <li><strong>לא:</strong> לא הצעה מסחרית, לא קביעת מחיר, לא חוות-דעת. ‎הקשר אינדיקטיבי בלבד.</li>
      </ul>
      <a href="#" className="mk-disclaimer__cta">קראו עוד על המתודולוגיה →</a>
    </div>
  );
}

function MarketDisclaimerFull() {
  return (
    <div className="mk-disclaimer" style={{ borderInlineStartWidth: 6 }}>
      <div className="mk-disclaimer__head">
        <span className="mk-disclaimer__icon">ⓘ</span>
        <h4 className="mk-disclaimer__h">מה זה ומה לא — קראו לפני שמשתמשים</h4>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
        <ul className="mk-disclaimer__list">
          <li><strong>המקור:</strong> סוכני סריקה ציבוריים של mezoo · ‎תרומות מחקלאי הקהילה.</li>
          <li><strong>המתודה:</strong> ממוצע מתגלגל של 7 ימים, נורמליזציה ליחידות, סינון חריגים.</li>
          <li><strong>הפרטיות:</strong> מצרפיות מלאה — לעולם לא מחיר ברמת חווה בודדת.</li>
          <li><strong>העדכניות:</strong> נסרק יומי. סף "stale" — 3 ימים מאז העדכון האחרון.</li>
        </ul>
        <ul className="mk-disclaimer__list">
          <li><strong>למה אנחנו עושים את זה:</strong> זה בעיקר כלי <em>שיווקי</em> — הוכחת יכולות של SFA, ודרך לחבר את הקהילה.</li>
          <li><strong>לא הצעה מסחרית:</strong> זה לא אומר שום דבר על המחיר שאתם <em>תקבלו</em> או <em>תשלמו</em>.</li>
          <li><strong>לא תחליף ל-Tend / חשבונית-ירוקה:</strong> זה לא יומן הכנסות, לא דף לקוחות.</li>
          <li><strong>טעות?</strong> דווחו לנו — נתקן באותו יום.</li>
        </ul>
      </div>
      <a href="#" className="mk-disclaimer__cta">קראו עוד על המתודולוגיה →</a>
    </div>
  );
}

Object.assign(window, {
  DesktopShell, Desktop_Hub, Desktop_CropBookProTable, Desktop_Market,
  MarketDisclaimer, MarketDisclaimerFull,
});
