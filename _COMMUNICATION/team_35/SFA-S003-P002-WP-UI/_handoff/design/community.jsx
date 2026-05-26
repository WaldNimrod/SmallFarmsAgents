/* community.jsx — feedback, suggestions, contributions UI.
   Includes:
   - CommunitySection — big block for the Hub home
   - ContributeStrip — inline strip for module pages (data correction CTA)
   - FeedbackFloating — small floating button visible everywhere
   - SuggestModuleCard — "suggest a new module" inline card
*/

// ─── Big section on the hub home ───────────────────────────────────────
function CommunitySection() {
  return (
    <section className="hub-section comm-section">
      <div className="hub-section__head">
        <span className="tier tier--lg tier--sun"><span className="tier__glyph">✺</span>קהילה</span>
        <h2 className="hub-section__title">המערכת הזו היא של כולנו.</h2>
        <p className="hub-section__lede">
          המחירים, הזנים, המספרים — כולם נאספים מהקהילה ועבור הקהילה.
          ככל שנתרום יותר, הכלים יהיו מדויקים יותר.
        </p>
      </div>

      <div className="comm-grid">
        <ContribCard
          tone="leaf"
          icon="✎"
          title="תרמו מידע"
          lede="יש לכם נתון על זן, יבול, או מחיר שלא מופיע? שלחו לנו ונכניס."
          cta="הוסיפו ערך"
        />
        <ContribCard
          tone="tomato"
          icon="◐"
          title="משהו לא מדויק?"
          lede="ראיתם נתון שגוי או שדה שצריך עדכון? תיקון לוקח דקה."
          cta="דווחו על שגיאה"
        />
        <ContribCard
          tone="sun"
          icon="💡"
          title="הציעו פיצ׳ר"
          lede="מה היה עוזר לכם בעבודה? איזה מסך חסר? איזה חישוב היה משנה?"
          cta="פיצ׳ר חדש"
        />
        <ContribCard
          tone="soil"
          icon="✦"
          title="הציעו מודול חדש"
          lede="יש כלי שהיה צריך להיות כאן? תארו את הצורך, נראה מי עוד צריך."
          cta="מודול חדש"
        />
      </div>

      {/* Community feed (sample submissions — shows that contributions are real) */}
      <div className="comm-feed">
        <div className="comm-feed__head">
          <h3>מה הציעו לאחרונה</h3>
          <a href="#">כל ההצעות →</a>
        </div>

        <FeedItem kind="suggest" name="ענת מ. · ‎ב הזרע 12" date="היום"
          text="צריך מודול שמחשב כמה אנשים יוצא להאכיל מסל שבועי בגדלים שונים. מקבל את זה הרבה."
          tag="חישוב סלים" upvotes={11}/>
        <FeedItem kind="correction" name="יואב ל. · ‎גליל" date="אתמול"
          text="עגבנייה תמר F1 — מחיר ממוצע 11.50 שבוע שעבר, לא 12.00. עדכנתי."
          tag="מחירון · עגבנייה" upvotes={4}/>
        <FeedItem kind="data" name="רחל ש. · ‎שרון" date="3 ימים"
          text="הוספתי 4 זנים של חסה לספר: קלוורי, תיבוק, ירוק בייבי, אלזיר. כולם DTM וזריעה מעודכנים."
          tag="ספר · חסה" upvotes={18}/>
        <FeedItem kind="suggest" name="דניאל ב. · ‎עמק חפר" date="שבוע"
          text="חבל שאין יומן רישום קצירות עם תזכורות. אני עושה את זה ב-WhatsApp לעצמי…"
          tag="יומן קציר" upvotes={9}/>
      </div>

      {/* Contribution stats */}
      <div className="comm-stats">
        <Stat big="247" sub="תיקונים החודש"/>
        <Stat big="34"  sub="הצעות פיצ׳ר פעילות"/>
        <Stat big="14"  sub="חוות תורמות נתונים"/>
        <Stat big="3"   sub="מודולים שהקהילה ביקשה"/>
      </div>

      <a href="https://wa.me/972547776770" className="comm-cta">
        <div className="comm-cta__icon">💬</div>
        <div className="comm-cta__body">
          <div className="comm-cta__h">צ׳אט פתוח · ‎WhatsApp</div>
          <div className="comm-cta__sub">קבוצת ה-SFA — חקלאים מקבלים תשובות מחברי קהילה אחרים. ‎87 חברים פעילים.</div>
        </div>
        <span className="comm-cta__arrow">←</span>
      </a>
    </section>
  );
}

function ContribCard({ tone, icon, title, lede, cta }) {
  return (
    <a href="#" className={`comm-card comm-card--${tone}`}>
      <span className="comm-card__icon">{icon}</span>
      <h4 className="comm-card__title">{title}</h4>
      <p className="comm-card__lede">{lede}</p>
      <span className="comm-card__cta">{cta} →</span>
    </a>
  );
}

function FeedItem({ kind, name, date, text, tag, upvotes }) {
  const kindMap = {
    suggest:    { glyph: '💡', label: 'הצעה',    color: 'sun' },
    correction: { glyph: '◐',  label: 'תיקון',   color: 'tomato' },
    data:       { glyph: '✎',  label: 'תרומה',   color: 'leaf' },
  };
  const k = kindMap[kind];
  return (
    <article className="feed-item">
      <div className={`feed-item__kind feed-item__kind--${k.color}`}>
        <span>{k.glyph}</span>
        <small>{k.label}</small>
      </div>
      <div className="feed-item__body">
        <div className="feed-item__head">
          <strong>{name}</strong>
          <span className="feed-item__date">{date}</span>
        </div>
        <p className="feed-item__text">{text}</p>
        <div className="feed-item__meta">
          <span className="pill pill--muted feed-item__tag">{tag}</span>
          <span className="feed-item__upvotes">▲ {upvotes}</span>
        </div>
      </div>
    </article>
  );
}

function Stat({ big, sub }) {
  return (
    <div className="comm-stat">
      <div className="comm-stat__big">{big}</div>
      <div className="comm-stat__sub">{sub}</div>
    </div>
  );
}

// ─── Inline "contribute data" strip — drop into market list & crop pages ──
function ContributeStrip({ context = 'מחירון', placeholder = 'יש לי נתון לתרום…' }) {
  return (
    <div className="contrib-strip">
      <div className="contrib-strip__head">
        <span className="contrib-strip__icon">✎</span>
        <div>
          <div className="contrib-strip__h">תורמים נתונים? לא חייבים להירשם.</div>
          <div className="contrib-strip__sub">{context} — כל תרומה נסקרת ידנית לפני שהיא נכנסת.</div>
        </div>
      </div>
      <div className="contrib-strip__input">
        <span>{placeholder}</span>
        <button>שלחו</button>
      </div>
      <div className="contrib-strip__quick">
        <button>מחיר שונה</button>
        <button>זן חסר</button>
        <button>שגיאה</button>
        <button>הצעה</button>
      </div>
    </div>
  );
}

// ─── Floating feedback button — appears on every module page ──────────
function FeedbackFloating({ context = 'דף זה' }) {
  return (
    <a href="#" className="fb-fab" title="פידבק">
      <span className="fb-fab__icon">💬</span>
      <span className="fb-fab__text">פידבק על {context}</span>
    </a>
  );
}

// ─── "Suggest a new module" full card ─────────────────────────────────
function SuggestModuleCard() {
  return (
    <div className="suggest-mod">
      <div className="suggest-mod__head">
        <span className="tier tier--sun"><span className="tier__glyph">+</span>הצעה</span>
        <h3>חסר כלי שצריך להיות כאן?</h3>
      </div>
      <p>תארו את הצורך בכמה משפטים. אם יש עוד 5 חקלאים שצריכים את זה — נבנה.</p>
      <textarea placeholder="למשל: ‎'כלי שמחשב כמה כסף לגבות על משלוח לפי מרחק ומשקל…'" />
      <div className="suggest-mod__row">
        <input type="text" placeholder="שם (אופציונלי)"/>
        <button>שלחו הצעה</button>
      </div>
      <p className="suggest-mod__hint">
        ⌐ הצעות פתוחות לקהילה — אחרים יכולים להצביע על מה שגם הם רוצים.
      </p>
    </div>
  );
}

Object.assign(window, {
  CommunitySection, ContribCard, FeedItem, Stat,
  ContributeStrip, FeedbackFloating, SuggestModuleCard,
});

// ─── CommunityShowcase — reference artboard showing all parts ─────────
function CommunityShowcase() {
  return (
    <div className="hub-shell">
      <header className="hub-bar">
        <button className="hub-bar__icon" aria-label="חזרה">←</button>
        <div className="hub-bar__title">
          <div className="hub-bar__name">רכיבי קהילה</div>
          <div className="hub-bar__sub">משוב · תרומה · הצעות · ‎ב-4 דרכים</div>
        </div>
      </header>

      <div style={{ padding: '18px 18px 0' }}>
        <p className="gj-eyebrow">CATALOG</p>
        <h2 className="hub-h1" style={{ fontSize: 28 }}>
          <span className="gj-underline">כל הדרכים</span> לתרום, לבקש ולהציע
        </h2>
        <p className="hub-lede" style={{ marginBottom: 20 }}>
          הקהילה היא הליבה. כל מסך במערכת מציע לפחות דרך אחת לתת/לקבל.
        </p>
      </div>

      <CommunitySection />

      <section style={{ padding: '18px' }}>
        <h3 style={{ fontFamily: 'var(--gj-font-head)', fontWeight: 700, fontSize: 17, margin: '0 0 8px' }}>
          רצועת תרומה — בכל דף מודול
        </h3>
        <ContributeStrip context="דוגמה · ‎הוסיפו ערך" placeholder="מחיר עגבנייה אצלי 11.50…"/>

        <h3 style={{ fontFamily: 'var(--gj-font-head)', fontWeight: 700, fontSize: 17, margin: '20px 0 8px' }}>
          טופס הצעת מודול
        </h3>
        <SuggestModuleCard />
      </section>
    </div>
  );
}

window.CommunityShowcase = CommunityShowcase;
