/* desktop-extras.jsx — remaining desktop variants needed for handoff completeness */

// ═══════════════════════════════════════════════════════════════════════
// D · Crop Detail (full)
// ═══════════════════════════════════════════════════════════════════════
function Desktop_CropDetail() {
  return (
    <window.DesktopShell active="book" title="עגבנייה" sub="Solanum lycopersicum · ‎סולנציאות · ‎22 זנים">
      <div className="dt-path-tabs">
        <a className="dt-path-tab" href="#">← חזרה לטבלה</a>
        <a className="dt-path-tab" href="#">סולנציאות</a>
        <a className="dt-path-tab is-active" href="#">עגבנייה</a>
      </div>

      <article className="dt-crop">
        <aside className="dt-crop__side">
          <div className="dt-crop__art">
            <window.ImagePrompt id="dt-crop-tomato-hero" ratio="1/1" tone="tomato"
              title="גיבור עגבנייה"
              prompt={window.PROMPTS.crop_hero}/>
          </div>
          <window.CrossLinkMarket />
          <div className="dt-crop__quickfacts">
            <h4>עובדות מהירות</h4>
            <dl className="cb-spec-grid">
              <div><dt>משפחה</dt><dd>סולנציאות</dd></div>
              <div><dt>DTM</dt><dd>60–78 ימים</dd></div>
              <div><dt>יבול</dt><dd>5.5–11.4 ק״ג/מ״ר</dd></div>
              <div><dt>עונה</dt><dd>אביב · קיץ</dd></div>
              <div><dt>מרווח</dt><dd>50×50 ס״מ</dd></div>
              <div><dt>חממה</dt><dd>מומלץ</dd></div>
            </dl>
          </div>
        </aside>

        <div className="dt-crop__main">
          <header className="dt-crop__head">
            <div className="cb-crop-hero__breadcrumb">
              <a href="#">ספר</a> <span>›</span> <a href="#">סולנציאות</a> <span>›</span> <strong>עגבנייה</strong>
            </div>
            <h1>
              <span className="gj-underline">עגבנייה</span>
            </h1>
            <p className="dt-crop__sci"><em>Solanum lycopersicum</em></p>
          </header>

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
            <h3>סקירה</h3>
            <p>
              עגבנייה היא הגידול המוביל בחוות קטנות בארץ. שולי הכנסה גבוהים יחסית למ״ר,
              אבל רגישה למחלות (TYLCV, נמטודות). הזנים מתחלקים לאשכוליים, דובדבן (cherry),
              בקר (beef), ומורשת. הבחירה משפיעה ישירות על אסטרטגיית השיווק — סלי תוצרת מעדיפים
              גוון של זנים, חנויות מבקשות אחידות, ורשתות דורשות נפח.
            </p>
            <p>
              העגבנייה היא צמח חם — לא נשתל לפני שטמפ׳ הקרקע עוברת 14°C. שתילה מוקדמת מדי
              מובילה לעיכוב בצמיחה ולפגיעות לרוחות. הקציר מתחיל בערך 60–78 ימים אחרי שתילה
              ונמשך 6–10 שבועות.
            </p>
          </section>

          <section className="cb-deep-section">
            <div className="cb-vars-head">
              <h3>22 זנים</h3>
              <div className="cb-vars-sort">
                <span>סדר:</span>
                <button className="is-active">ברירת מחדל</button>
                <button>טעם</button>
                <button>יבול</button>
                <button>DTM</button>
              </div>
            </div>
            <div className="dt-vars-grid">
              {window.TOMATO_VARIETIES.map(v => <VarietyCardDesktop key={v.id} v={v}/>)}
            </div>
            <a href="#" className="cb-vars-more">+ 16 זנים נוספים</a>
          </section>

          <section className="cb-deep-section">
            <h3>ציר זמן · ‎ברירת מחדל (תמר F1)</h3>
            <div className="dt-timeline">
              <div className="dt-timeline__bar">
                <div className="dt-timeline__seg dt-timeline__seg--prep" style={{ width: '14%' }}>הכנה · ‎12 ימים</div>
                <div className="dt-timeline__seg dt-timeline__seg--grow" style={{ width: '56%' }}>גידול · ‎48 ימים עד פריחה</div>
                <div className="dt-timeline__seg dt-timeline__seg--harv" style={{ width: '30%' }}>קציר · ‎28 ימים</div>
              </div>
              <div className="dt-timeline__ruler">
                <span>שבוע 1</span>
                <span>שבוע 4</span>
                <span>שבוע 8</span>
                <span>שבוע 12</span>
              </div>
            </div>
          </section>

          <window.ContributeStrip context="עגבנייה · ‎ספר" placeholder="זן חסר? נתון מדוייק יותר?"/>
        </div>
      </article>
    </window.DesktopShell>
  );
}

function VarietyCardDesktop({ v }) {
  return (
    <a className="dt-var" href="#">
      <div className="dt-var__head">
        {v.default && <span className="cb-var__star">★</span>}
        <h4>{v.name}</h4>
        {v.hybrid ? <span className="pill pill--code">F1</span> : <span className="pill pill--muted">מורשת</span>}
      </div>
      <div className="dt-var__rows">
        <span><small>DTM</small>{v.dtm}</span>
        <span><small>יבול</small>{v.yield}</span>
        <span><small>צבע</small>{v.color}</span>
        <span><small>צורה</small>{v.shape}</span>
        <span><small>טעם</small>{'★'.repeat(v.taste)}</span>
        <span><small>עמידות</small>{v.resistance}</span>
      </div>
    </a>
  );
}

// ═══════════════════════════════════════════════════════════════════════
// D · Market Detail
// ═══════════════════════════════════════════════════════════════════════
function Desktop_MarketDetail() {
  return (
    <window.DesktopShell active="market" title="עגבנייה · ‎ק״ג" sub="מחיר ממוצע, התפלגות, מגמה — מתוך מחירון SFA">
      <div className="dt-path-tabs">
        <a className="dt-path-tab" href="#">← חזרה למחירון</a>
      </div>

      <div className="dt-mkdetail">
        <div className="dt-mkdetail__hero">
          <div className="dt-mkdetail__art">
            <window.Tomato size={140}/>
          </div>
          <div className="dt-mkdetail__head">
            <p className="gj-eyebrow">מחיר שוק · ‎7 ימים אחרונים</p>
            <h2><span className="gj-underline">עגבנייה</span></h2>
            <p className="dt-crop__sci">Tomato · קילו · מנורמל</p>
            <a href="#" className="dt-mkdetail__crosslink">↗ פתח גידול בספר</a>
          </div>
          <div className="dt-mkdetail__bignumber">
            <div className="dt-mkdetail__big">12.40</div>
            <div className="dt-mkdetail__cur">₪/ק״ג</div>
            <div className="dt-mkdetail__lbl">ממוצע</div>
            <div className="dt-mkdetail__delta is-down">−4% משבוע</div>
          </div>
        </div>

        <window.MarketDisclaimerFull />

        <section className="dt-mkdetail__stats">
          <h3>סטטיסטיקה</h3>
          <div className="dt-statgrid">
            <Stat2 lbl="חציון"    big="12.00" sub="₪/ק״ג"/>
            <Stat2 lbl="טווח"      big="9.50 – 16.00" sub="₪"/>
            <Stat2 lbl="סטיית תקן" big="1.82" sub="₪"/>
            <Stat2 lbl="מקורות"    big="6"     sub="●●●●●●"/>
            <Stat2 lbl="תצפיות"    big="24"    sub="ב-7 ימים"/>
            <Stat2 lbl="עדכון אחרון" big="14:32" sub="היום"/>
          </div>
        </section>

        <section className="dt-mkdetail__chart">
          <h3>מגמה (4 שבועות)</h3>
          <DummyChart />
          <p className="dt-mkdetail__chartfoot">
            ⓘ תרשים אינדיקטיבי. הנתונים מצרפיים — לא מייצגים חווה ספציפית.
          </p>
        </section>

        <window.ContributeStrip context="מחירון · ‎עגבנייה" placeholder="אצלי 10.80, יום ראשון…"/>
      </div>
    </window.DesktopShell>
  );
}

function Stat2({ lbl, big, sub }) {
  return (
    <div className="dt-stat">
      <div className="dt-stat__lbl">{lbl}</div>
      <div className="dt-stat__big">{big}</div>
      <div className="dt-stat__sub">{sub}</div>
    </div>
  );
}

function DummyChart() {
  // Simple inline SVG line chart
  const pts = [11.8, 12.6, 13.2, 12.9, 13.1, 12.8, 12.5, 12.7, 12.4, 12.1, 11.9, 12.3, 12.4, 12.40];
  const w = 800, h = 200, pad = 30;
  const min = 11, max = 14;
  const xstep = (w - pad * 2) / (pts.length - 1);
  const path = pts.map((p, i) => `${i === 0 ? 'M' : 'L'} ${pad + i * xstep} ${pad + (1 - (p - min) / (max - min)) * (h - pad * 2)}`).join(' ');
  return (
    <svg viewBox={`0 0 ${w} ${h}`} style={{ width: '100%', height: 200, display: 'block' }}>
      {/* grid */}
      {[0, 1, 2, 3].map(i => (
        <line key={i} x1={pad} x2={w - pad} y1={pad + i * ((h - pad * 2) / 3)} y2={pad + i * ((h - pad * 2) / 3)} stroke="#ddd2b2" strokeDasharray="2 4"/>
      ))}
      <path d={`${path} L ${w - pad} ${h - pad} L ${pad} ${h - pad} Z`} fill="url(#wc-tomato)" opacity=".15"/>
      <path d={path} stroke="#8e3018" strokeWidth="2" fill="none"/>
      {pts.map((p, i) => (
        <circle key={i} cx={pad + i * xstep} cy={pad + (1 - (p - min) / (max - min)) * (h - pad * 2)} r="3" fill="#8e3018"/>
      ))}
      {/* axis labels */}
      <text x={pad} y={h - 6} fontSize="11" fontFamily="JetBrains Mono" fill="#776a4d">לפני 4 שבועות</text>
      <text x={w - pad} y={h - 6} textAnchor="end" fontSize="11" fontFamily="JetBrains Mono" fill="#776a4d">היום</text>
    </svg>
  );
}

// ═══════════════════════════════════════════════════════════════════════
// D · Calculator (desktop)
// ═══════════════════════════════════════════════════════════════════════
function Desktop_Calculator() {
  return (
    <window.DesktopShell active="calc" title="מחשבון לחקלאי · ‎גרסת בטא" sub="תכנון רווחיות לפי שטח, גידול, יבול ומחיר שוק.">
      <div className="dt-calc">
        <div className="dt-calc__form">
          <header>
            <window.TierBadge tier="beta" size="lg"/>
            <p className="gj-eyebrow">תכנון רווחיות</p>
            <h2 className="dt-calc__h">
              כמה ירוויחו <span className="gj-underline">3 ערוגות עגבניות?</span>
            </h2>
            <p className="hub-lede">
              מבוסס נתונים מהספר (יבול ממוצע, DTM) ומהמחירון (מחיר שוק מתגלגל).
              כל הערכים ניתנים להחלפה.
            </p>
          </header>

          <fieldset className="dt-calc-field">
            <legend>גידול ראשי</legend>
            <select><option>עגבנייה · תמר F1 (ברירת מחדל)</option></select>
          </fieldset>

          <div className="dt-calc-row">
            <fieldset className="dt-calc-field">
              <legend>מספר ערוגות</legend>
              <input type="number" defaultValue={3}/>
            </fieldset>
            <fieldset className="dt-calc-field">
              <legend>אורך ערוגה (מ׳)</legend>
              <input type="number" defaultValue={10}/>
            </fieldset>
            <fieldset className="dt-calc-field">
              <legend>רוחב (מ׳)</legend>
              <input type="number" defaultValue={2}/>
            </fieldset>
          </div>

          <fieldset className="dt-calc-field">
            <legend>שטח כולל</legend>
            <div className="dt-calc-readonly">60 מ״ר</div>
          </fieldset>

          <fieldset className="dt-calc-field">
            <legend>יבול צפוי (מהספר)</legend>
            <div className="dt-calc-row">
              <input type="number" defaultValue={9.2} step={0.1}/>
              <span className="dt-calc-unit">ק״ג/מ״ר</span>
              <button className="dt-calc-help">↗ ספר</button>
            </div>
            <small>טווח בספר: 5.5–11.4 ק״ג/מ״ר. ‎ערך ברירת מחדל = ממוצע זן.</small>
          </fieldset>

          <fieldset className="dt-calc-field">
            <legend>מחיר שוק (מהמחירון)</legend>
            <div className="dt-calc-row">
              <input type="number" defaultValue={12.40} step={0.10}/>
              <span className="dt-calc-unit">₪/ק״ג</span>
              <button className="dt-calc-help">↗ מחירון</button>
            </div>
            <small>ממוצע מתגלגל 7 ימים, מנורמל. ‎−4% משבוע שעבר.</small>
          </fieldset>

          <fieldset className="dt-calc-field">
            <legend>הוצאות משוערות</legend>
            <div className="dt-calc-readonly dt-calc-readonly--soft">לא הוזנו — תוסיפו ב-מחשבון מתקדם (בקרוב)</div>
          </fieldset>
        </div>

        <aside className="dt-calc__results">
          <div className="dt-calc__resultcard">
            <div className="dt-calc__resultlbl">יבול צפוי</div>
            <div className="dt-calc__resultbig">552 <small>ק״ג</small></div>
            <div className="dt-calc__resultsub">60 מ״ר × 9.2 ק״ג/מ״ר</div>
          </div>
          <div className="dt-calc__resultcard dt-calc__resultcard--big">
            <div className="dt-calc__resultlbl">הכנסה צפויה</div>
            <div className="dt-calc__resultbig">6,845 <small>₪</small></div>
            <div className="dt-calc__resultsub">552 ק״ג × 12.40 ₪</div>
          </div>
          <div className="dt-calc__resultcard">
            <div className="dt-calc__resultlbl">משך זמן</div>
            <div className="dt-calc__resultbig">10–14 <small>שבועות</small></div>
            <div className="dt-calc__resultsub">68 ימי DTM + תקופת קציר</div>
          </div>

          <div className="dt-calc__sensitivity">
            <h4>רגישות</h4>
            <p>אם מחיר השוק יירד 10% → הכנסה <strong>6,160 ₪</strong>.</p>
            <p>אם היבול יהיה נמוך ב-15% → הכנסה <strong>5,818 ₪</strong>.</p>
          </div>

          <div className="dt-calc__feedback">
            <p>בטא · ‎עוזרים לכיול. ראיתם נתון שגוי?</p>
            <a href="#">פתחו פידבק →</a>
          </div>
        </aside>
      </div>
    </window.DesktopShell>
  );
}

// ═══════════════════════════════════════════════════════════════════════
// D · Tiers Explainer (desktop)
// ═══════════════════════════════════════════════════════════════════════
function Desktop_Tiers() {
  const tiers = ['open', 'paid', 'custom'];
  return (
    <window.DesktopShell active="hub" title="איך זה עובד?" sub="3 רמות · ‎הזמנות אישיות · ‎קוד פתוח לקהילה">
      <section className="dt-tiers-intro">
        <p className="gj-eyebrow">המבנה</p>
        <h2 className="dt-hub-hero__h">
          קודם כל — <span className="gj-underline">לתת.</span>
        </h2>
        <p className="hub-lede" style={{ maxWidth: '60ch' }}>
          רוב הכלים פתוחים, חינמיים ובלי הרשמה. זו תרומה לקהילה החקלאית הקטנה.
          חלק מהמודולים מורחבים לחוות פעילות שצריכות יותר. וחלק נבנים בהזמנה — לפי הצורך.
        </p>
      </section>

      <div className="dt-tier-grid">
        {tiers.map((t, i) => {
          const def = window.TIERS[t];
          const mods = window.MODULES.filter(m => m.tier === t);
          return (
            <div key={t} className={`dt-tier-card dt-tier-card--${def.color}`}>
              <div className="dt-tier-card__num">{String(i+1).padStart(2,'0')}</div>
              <window.TierBadge tier={t} size="lg"/>
              <h3>{def.label}</h3>
              <p>{def.description}</p>
              <div className="dt-tier-card__mods">
                {mods.map(m => (
                  <a key={m.id} href={m.href} className="dt-tier-card__mod">
                    <window.CropIcon kind={m.icon} size={28}/>
                    <span>{m.name}</span>
                  </a>
                ))}
              </div>
              <div className="dt-tier-card__count">
                {mods.length} מודולים
              </div>
            </div>
          );
        })}
      </div>

      <a href="https://wa.me/972547776770" className="dt-suggest" style={{ marginTop: 22 }}>
        <strong>+ לא מצאתם מה שאתם צריכים?</strong>
        <span>נדבר בוואטסאפ 15 דקות, ונראה אם נבנה עבורכם. ‎054-7776770</span>
      </a>
    </window.DesktopShell>
  );
}

// ═══════════════════════════════════════════════════════════════════════
// D · States (empty, loading, error, stale)
// ═══════════════════════════════════════════════════════════════════════
function Desktop_States() {
  return (
    <window.DesktopShell active="hub" title="מצבי קצה — Loading · ‎Empty · ‎Stale · ‎Error" sub="לכל המודולים. קטלוג למימוש.">
      <div className="dt-states-grid">
        <StateCard tone="leaf" h="Loading · ‎טעינה ראשונה">
          <div className="dt-skeleton" style={{ height: 16, width: '60%', marginBottom: 10 }}/>
          <div className="dt-skeleton" style={{ height: 14, width: '40%', marginBottom: 14 }}/>
          {[0,1,2].map(i => <div key={i} className="dt-skeleton" style={{ height: 60, marginBottom: 8 }}/>)}
        </StateCard>

        <StateCard tone="sun" h="Stale · ‎נתונים ישנים">
          <div style={{ padding: 12, background: '#fde9d4', borderRadius: 10, borderInlineStart: '4px solid #c47b2e' }}>
            <strong>⚠ הנתונים עשויים שלא להיות עדכניים</strong>
            <p style={{ margin: '4px 0 0', fontSize: 12 }}>מעל 3 ימים מאז העדכון האחרון. ‎נסה שוב מאוחר יותר.</p>
          </div>
        </StateCard>

        <StateCard tone="tomato" h="Empty · ‎אין תוצאות">
          <div style={{ textAlign: 'center', padding: 24 }}>
            <div style={{ fontSize: 32, marginBottom: 8 }}>◌</div>
            <strong>לא נמצאו גידולים</strong>
            <p style={{ fontSize: 12, color: 'var(--gj-ink-soft)', margin: '4px 0 12px' }}>נסו לאפס פילטרים או לחפש משהו אחר.</p>
            <button className="dt-btn dt-btn--ghost" style={{ padding: '6px 14px', fontSize: 12 }}>↺ אפס פילטרים</button>
          </div>
        </StateCard>

        <StateCard tone="tomato" h="Error · ‎שגיאת טעינה">
          <div style={{ textAlign: 'center', padding: 24, color: '#c43a2e' }}>
            <div style={{ fontSize: 32, marginBottom: 8 }}>✕</div>
            <strong>שגיאה בטעינת הנתונים</strong>
            <p style={{ fontSize: 12, margin: '4px 0 12px', color: 'inherit' }}>הסוכן לא הצליח להתחבר. נסו שוב.</p>
            <button className="dt-btn dt-btn--primary" style={{ padding: '6px 14px', fontSize: 12 }}>↻ נסה שוב</button>
          </div>
        </StateCard>

        <StateCard tone="leaf" h="Pending publish · ‎ממתין לפרסום">
          <div style={{ textAlign: 'center', padding: 24, color: 'var(--gj-ink-soft)' }}>
            <strong style={{ color: 'var(--gj-ink)' }}>ספר גידולים — בטעינה</strong>
            <p style={{ fontSize: 11, margin: '4px 0', fontFamily: '"JetBrains Mono", monospace' }}>sfagent_crop_book_manifest_of_urls_url empty</p>
            <p style={{ fontSize: 12, margin: '8px 0 0' }}>ה-mu-plugin מציג placeholder עד שה-publish הראשון רץ.</p>
          </div>
        </StateCard>

        <StateCard tone="sun" h="Offline · ‎ללא חיבור">
          <div style={{ textAlign: 'center', padding: 24 }}>
            <div style={{ fontSize: 32, marginBottom: 8 }}>⊘</div>
            <strong>אין חיבור</strong>
            <p style={{ fontSize: 12, color: 'var(--gj-ink-soft)', margin: '4px 0' }}>אנחנו עובדים בלי חיבור — חלק מהמידע יזמין שוב כשתתחברו.</p>
          </div>
        </StateCard>
      </div>
    </window.DesktopShell>
  );
}

function StateCard({ tone = 'leaf', h, children }) {
  return (
    <div className={`dt-statecard dt-statecard--${tone}`}>
      <div className="dt-statecard__head">{h}</div>
      <div className="dt-statecard__body">{children}</div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════
// D · Global Search Results
// ═══════════════════════════════════════════════════════════════════════
function Desktop_Search() {
  return (
    <window.DesktopShell active="hub" title="חיפוש: ‘עגבנייה’" sub="14 תוצאות מ-3 מודולים">
      <div className="dt-search">
        <div className="dt-search__bar">
          <input type="search" defaultValue="עגבנייה" />
          <button>חפש</button>
        </div>
        <div className="dt-search__chips">
          <span className="gj-chip is-active">הכל · 14</span>
          <span className="gj-chip">ספר · 1 גידול + 22 זנים</span>
          <span className="gj-chip">מחירון · 1 מוצר</span>
          <span className="gj-chip">קהילה · 8 הצעות</span>
        </div>

        <section className="dt-search__group">
          <h3>ספר גידולים</h3>
          <a href="#" className="dt-search__row dt-search__row--book">
            <window.Tomato size={48}/>
            <div>
              <div className="dt-search__name">עגבנייה <em>· Solanum lycopersicum</em></div>
              <div className="dt-search__meta">סולנציאות · ‎22 זנים · ‎DTM 60–78</div>
            </div>
            <span className="pill pill--soil">גידול</span>
          </a>
          <a href="#" className="dt-search__row">
            <span className="dt-search__icon">◐</span>
            <div>
              <div className="dt-search__name">תמר F1</div>
              <div className="dt-search__meta">זן עגבנייה · ‎ברירת מחדל · ‎יבול 9.2 ק״ג/מ״ר</div>
            </div>
            <span className="pill pill--code">זן · F1</span>
          </a>
          <a href="#" className="dt-search__row">
            <span className="dt-search__icon">◐</span>
            <div>
              <div className="dt-search__name">שרי תאיה</div>
              <div className="dt-search__meta">זן עגבנייה דובדבן · ‎DTM 60</div>
            </div>
            <span className="pill pill--muted">זן · מורשת</span>
          </a>
          <a href="#" className="dt-search__more">22 זנים · ‎הצג את כולם →</a>
        </section>

        <section className="dt-search__group">
          <h3>מחירון</h3>
          <a href="#" className="dt-search__row dt-search__row--market">
            <window.Tomato size={48}/>
            <div>
              <div className="dt-search__name">עגבנייה <em>· ק״ג</em></div>
              <div className="dt-search__meta">12.40 ₪ ממוצע · ‎−4% משבוע · ‎6 מקורות</div>
            </div>
            <span className="pill pill--know">מוצר</span>
          </a>
        </section>

        <section className="dt-search__group">
          <h3>קהילה</h3>
          <a href="#" className="dt-search__row">
            <span className="dt-search__icon" style={{ background: 'color-mix(in oklch, var(--gj-tomato) 16%, var(--gj-paper))' }}>◐</span>
            <div>
              <div className="dt-search__name">תיקון מחיר עגבנייה</div>
              <div className="dt-search__meta">יואב ל. · ‎גליל · ‎אתמול · ‎4 הצבעות</div>
            </div>
            <span className="pill pill--muted">תיקון</span>
          </a>
          <a href="#" className="dt-search__row">
            <span className="dt-search__icon" style={{ background: 'color-mix(in oklch, var(--gj-sun) 28%, var(--gj-paper))' }}>💡</span>
            <div>
              <div className="dt-search__name">להוסיף תחזית מזג אוויר לעגבנייה</div>
              <div className="dt-search__meta">דניאל ב. · ‎שבוע · ‎11 הצבעות</div>
            </div>
            <span className="pill pill--muted">פיצ׳ר</span>
          </a>
          <a href="#" className="dt-search__more">8 פריטי קהילה · ‎הצג את כולם →</a>
        </section>
      </div>
    </window.DesktopShell>
  );
}

// ═══════════════════════════════════════════════════════════════════════
// D · Community (full page)
// ═══════════════════════════════════════════════════════════════════════
function Desktop_Community() {
  return (
    <window.DesktopShell active="hub" title="קהילה" sub="זו המערכת של כולנו — תרומות, הצעות, פידבק">
      <window.CommunitySection />
    </window.DesktopShell>
  );
}

Object.assign(window, {
  Desktop_CropDetail, Desktop_MarketDetail, Desktop_Calculator,
  Desktop_Tiers, Desktop_States, Desktop_Search, Desktop_Community,
  VarietyCardDesktop, Stat2, DummyChart, StateCard,
});
