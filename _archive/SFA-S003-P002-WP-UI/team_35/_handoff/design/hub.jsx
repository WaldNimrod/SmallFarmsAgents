/* hub.jsx — Module Hub home + tier badge + module cards.
   This replaces the old GJ_Home. Other screens (GJ_MarketList,
   GJ_CropDetail, etc.) still work as before. */

// ─── Tier badge ────────────────────────────────────────────────────────
function TierBadge({ tier, size = 'sm' }) {
  const t = window.TIERS[tier];
  if (!t) return null;
  const tone = t.color;
  return (
    <span className={`tier tier--${tone} tier--${size}`}>
      {tier === 'paid'   && <span className="tier__glyph">★</span>}
      {tier === 'custom' && <span className="tier__glyph">✎</span>}
      {tier === 'beta'   && <span className="tier__glyph">β</span>}
      {tier === 'coming' && <span className="tier__glyph">⏳</span>}
      {tier === 'open'   && <span className="tier__glyph">●</span>}
      {t.label}
    </span>
  );
}

// ─── Module thumb (square art slot + name) ─────────────────────────────
function ModuleThumb({ m }) {
  return (
    <a className={`mod-card mod-card--${m.color} mod-card--${m.tier}`} href={m.href} data-tier={m.tier}>
      <div className="mod-card__art">
        <window.ImagePrompt id={`thumb-${m.id}`} ratio="1/1" tone={m.color}
          title={m.name}
          prompt={window.PROMPTS[m.thumb]}
          hint="1:1 thumb"
        />
        <div className="mod-card__icon">
          <window.CropIcon kind={m.icon} size={42}/>
        </div>
      </div>
      <div className="mod-card__body">
        <div className="mod-card__head">
          <h3 className="mod-card__name">{m.name}</h3>
          <TierBadge tier={m.tier}/>
        </div>
        <p className="mod-card__sub">{m.sub}</p>
        <p className="mod-card__stat">{m.stat}</p>
      </div>
    </a>
  );
}

// ─── HUB · Home (replaces GJ_Home) ─────────────────────────────────────
function HubHome() {
  const open   = window.MODULES.filter(m => m.tier === 'open');
  const beta   = window.MODULES.filter(m => m.tier === 'beta');
  const coming = window.MODULES.filter(m => m.tier === 'coming');
  const paid   = window.MODULES.filter(m => m.tier === 'paid');
  const custom = window.MODULES.filter(m => m.tier === 'custom');

  return (
    <div className="hub-shell">
      {/* ─── Top brand bar ─── */}
      <header className="hub-bar">
        <div className="hub-bar__mark"><HubMark/></div>
        <div className="hub-bar__title">
          <div className="hub-bar__name">SFA</div>
          <div className="hub-bar__sub">חקלאות קטנה · כלים פתוחים</div>
        </div>
        <button className="hub-bar__icon" aria-label="חיפוש">⌕</button>
        <button className="hub-bar__icon" aria-label="תפריט">☰</button>
      </header>

      {/* ─── Hero ─── */}
      <section className="hub-hero">
        <div className="hub-hero__art">
          <window.ImagePrompt id="hub-hero" ratio="16/9" tone="leaf"
            title="רקע הירו לעמוד הבית"
            prompt={window.PROMPTS.module_hub}
            hint="ייוצר ב-Midjourney / SDXL"
          />
        </div>
        <div className="hub-hero__copy">
          <p className="gj-eyebrow">SFA · ‎נימרוד.bio</p>
          <h1 className="hub-h1">
            כלים גדולים<br/>
            <span className="gj-underline">לחוות קטנות.</span>
          </h1>
          <p className="hub-lede">
            מערכת קהילתית שנבנית בהדרגה. כלים לקהילה לתמיד —
            כלים מתקדמים לחוות פעילות, וכלים שנבנה בדיוק לחווה שלך.
            המערכת זו התרומה לקהילה — והזמנה לעבוד יחד.
          </p>
        </div>
      </section>

      {/* ─── Tier 1 · open community ─── */}
      <section className="hub-section">
        <div className="hub-section__head">
          <TierBadge tier="open" size="lg"/>
          <h2 className="hub-section__title">כלים לקהילה</h2>
          <p className="hub-section__lede">נתונים פתוחים, מצרפיים, בלי הרשמה. תרומה לקהילה החקלאית הקטנה.</p>
        </div>
        <div className="mod-grid">
          {open.map(m => <ModuleThumb key={m.id} m={m}/>)}
          {beta.map(m => <ModuleThumb key={m.id} m={m}/>)}
        </div>
      </section>

      {/* ─── Tier 3 · paid ─── */}
      <section className="hub-section">
        <div className="hub-section__head">
          <TierBadge tier="paid" size="lg"/>
          <h2 className="hub-section__title">כלים מתקדמים</h2>
          <p className="hub-section__lede">לחוות פעילות — יכולות תפעוליות מורחבות. תמחור הוגן לפי גודל.</p>
        </div>
        <div className="mod-grid">
          {paid.map(m => <ModuleThumb key={m.id} m={m}/>)}
        </div>
      </section>

      {/* ─── Tier 2 · custom build (showcase + CTA) ─── */}
      <section className="hub-section hub-section--custom">
        <div className="hub-section__head">
          <TierBadge tier="custom" size="lg"/>
          <h2 className="hub-section__title">בדיוק לחווה שלך</h2>
          <p className="hub-section__lede">דוגמאות ממשה ממה שבנינו לחקלאים אחרים. אינטגרציות, אוטומציות, מסכים יעודיים על המערכת הקיימת.</p>
        </div>
        <div className="mod-grid">
          {custom.map(m => <ModuleThumb key={m.id} m={m}/>)}
        </div>

        {/* Coming soon block */}
        {coming.length > 0 && (
          <>
            <div className="hub-section__head" style={{ marginTop: 24 }}>
              <TierBadge tier="coming" size="lg"/>
              <h2 className="hub-section__title">בקרוב</h2>
            </div>
            <div className="mod-grid">
              {coming.map(m => <ModuleThumb key={m.id} m={m}/>)}
            </div>
          </>
        )}

        {/* CTA card */}
        <a className="contact-card" href="https://wa.me/972547776770" target="_blank">
          <div className="contact-card__art">
            <window.ImagePrompt id="hub-contact" ratio="16/9" tone="soil"
              title="רקע פנייה לפיתוח אישי"
              prompt={window.PROMPTS.contact}
              hint="ניתן להחליף בתמונה אמיתית"
            />
          </div>
          <div className="contact-card__body">
            <span className="gj-eyebrow">צריך משהו שאין כאן?</span>
            <h3 className="contact-card__h">דברו איתי, נתפור משהו יחד.</h3>
            <p className="contact-card__lede">
              אם יש לך חווה קטנה ויש משימה שחוזרת בכל יום — סביר שאפשר לעשות לה כלי קטן.
              נכנס לשיחה, נציע גישה, ואם זה מתאים נבנה בדיוק לחווה שלך.
            </p>
            <span className="contact-card__cta">WhatsApp · 054-7776770 →</span>
          </div>
        </a>
      </section>

      {/* COMMUNITY section is shown on a separate artboard (H4) to keep this one fast */}

      {/* ─── Footer ─── */}
      <footer className="hub-foot">
        <div className="hub-foot__row">
          <span className="hub-foot__dot"/>
          <span>עודכן הבוקר · 14 מקורות פעילים</span>
          <span style={{ opacity: .4 }}>·</span>
          <span>SFA · ‎nimrod.bio</span>
        </div>
        <div className="hub-foot__motto">קטן זה יפה · לאט זה שפוי</div>
      </footer>
    </div>
  );
}

function HubMark() {
  return (
    <svg viewBox="0 0 40 40" width="36" height="36" aria-hidden="true">
      <circle cx="20" cy="20" r="16" fill="#f3ede0"/>
      <path d="M20 13 Q14 17 14 24 Q20 23 22 17 Q22 13 20 13 Z" fill="#6f8a45"/>
      <path d="M20 13 Q26 17 26 24 Q20 23 18 17 Q18 13 20 13 Z" fill="#9bb172"/>
      <path d="M20 13 L20 30" stroke="#4d6a2c" strokeWidth="1.4"/>
    </svg>
  );
}

// ─── HUB · Tiers explainer (one full page on the 3-tier model) ────────
function HubTiers() {
  const tiers = ['open', 'beta', 'paid', 'custom', 'coming'];
  return (
    <div className="hub-shell">
      <header className="hub-bar">
        <button className="hub-bar__icon" aria-label="חזרה">←</button>
        <div className="hub-bar__title">
          <div className="hub-bar__name">איך זה עובד?</div>
          <div className="hub-bar__sub">3 רמות + הזמנות אישיות</div>
        </div>
      </header>

      <section className="hub-tiers-intro">
        <p className="gj-eyebrow">המבנה</p>
        <h1 className="hub-h1">
          קודם כל — <span className="gj-underline">לתת.</span>
        </h1>
        <p className="hub-lede">
          רוב הכלים פתוחים, חינמיים ובלי הרשמה. זו תרומה לקהילה החקלאית הקטנה.
          חלק מהמודולים מורחבים לחוות פעילות שצריכות יותר. וחלק נבנים בהזמנה — לפי הצורך.
        </p>
      </section>

      <div className="hub-tier-list">
        {tiers.map((t, i) => {
          const def = window.TIERS[t];
          const count = window.MODULES.filter(m => m.tier === t).length;
          return (
            <div key={t} className="hub-tier-row">
              <div className="hub-tier-row__num">{String(i+1).padStart(2,'0')}</div>
              <div className="hub-tier-row__body">
                <TierBadge tier={t} size="lg"/>
                <p className="hub-tier-row__desc">{def.description}</p>
                <div className="hub-tier-row__count">{count} מודולים</div>
              </div>
            </div>
          );
        })}
      </div>

      <a className="contact-card" href="#" style={{ marginTop: 20 }}>
        <div className="contact-card__art">
          <window.ImagePrompt id="tiers-contact" ratio="16/9" tone="soil"
            title="רקע ליצירת קשר"
            prompt={window.PROMPTS.contact}/>
        </div>
        <div className="contact-card__body">
          <span className="gj-eyebrow">לא בטוח/ה איזו רמה?</span>
          <h3 className="contact-card__h">בואו נדבר.</h3>
          <p className="contact-card__lede">שיחה של 15 דקות בוואטסאפ, נבין מה תרצו ונציע משהו.</p>
          <span className="contact-card__cta">WhatsApp →</span>
        </div>
      </a>
    </div>
  );
}

// ─── HUB · Calculator module (sample new module — illustrates pattern) ─
function HubCalculator() {
  return (
    <div className="gj-shell">
      <header className="gj-header">
        <div className="gj-header__row">
          <button className="gj-iconbtn">←</button>
          <div className="gj-header__title">
            <div className="gj-title">מחשבון לחקלאי</div>
            <div className="gj-sub">תכנון רווחיות · גרסת בטא</div>
          </div>
          <TierBadge tier="beta"/>
        </div>
      </header>

      <main className="gj-body">
        <div style={{ marginBottom: 14 }}>
          <window.ImagePrompt id="calc-hero" ratio="16/9" tone="sun"
            title="רקע למחשבון"
            prompt={window.PROMPTS.hero_calc}
            hint="ניתן להחליף בתמונה אמיתית"/>
        </div>

        <p className="gj-eyebrow">03 · מחשבון</p>
        <h2 className="gj-h2">כמה ירוויחו <span className="gj-underline">3 ערוגות עגבניות?</span></h2>
        <p className="gj-lede gj-lede--sm">
          תכנון רווחיות לפי גידול, שטח, יבול ומחיר שוק נוכחי מתוך המחירון.
        </p>

        <div className="calc-form">
          <CalcField label="גידול" value="עגבנייה · תמר F1"/>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
            <CalcField label="ערוגות" value="3 · ‎60 מ״ר"/>
            <CalcField label="מרווח" value="50×50 ס״מ"/>
          </div>
          <CalcField label="יבול צפוי" value="552 ק״ג (9.2 ק״ג/מ״ר)" hint="מבוסס על הספר"/>
          <CalcField label="מחיר שוק" value="12.40 ₪/ק״ג" hint="מתוך מחירון · 7 ימים"/>
        </div>

        <div className="calc-result">
          <div className="calc-result__label">הכנסה צפויה</div>
          <div className="calc-result__big">6,845 <small>₪</small></div>
          <div className="calc-result__sub">לפני הוצאות · ‎10–14 שבועות</div>
        </div>

        <a href="#" className="gj-crosslink">
          <div className="gj-crosslink__body">
            <div className="gj-crosslink__big" style={{ fontSize: 16 }}>פתח את הגידול בספר</div>
            <div className="gj-crosslink__sub">זנים · עונת שתילה · ‎טיפולים</div>
          </div>
          <span className="gj-crosslink__cta">פתח →</span>
        </a>

        <div className="calc-feedback">
          <p style={{ margin: '0 0 6px', fontSize: 12, color: 'var(--gj-ink-soft)' }}>
            <strong style={{ color: 'var(--gj-ink)' }}>בטא · ‎פתוח לפידבק.</strong> משהו לא מדויק? משהו חסר? נשמח לדעת.
          </p>
          <a href="#" style={{ fontSize: 11, color: 'var(--gj-leaf-deep)', fontWeight: 700 }}>שלחו פידבק בוואטסאפ →</a>
        </div>
      </main>

      <footer className="gj-foot">
        <span className="gj-foot__dot" style={{ background: '#d39a32' }}/>
        <span>גרסת בטא · ‎ייתכנו שינויים</span>
      </footer>
    </div>
  );
}

function CalcField({ label, value, hint }) {
  return (
    <label className="calc-field">
      <div className="calc-field__label">{label}</div>
      <div className="calc-field__value">{value}</div>
      {hint && <div className="calc-field__hint">{hint}</div>}
    </label>
  );
}

Object.assign(window, { HubHome, HubTiers, HubCalculator, TierBadge, ModuleThumb, HubMark });
