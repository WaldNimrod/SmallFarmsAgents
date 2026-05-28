/* primitives.jsx — shared shell + bits used across wireframes and mockups */

// ─── SFA mark (no images per brief — inline SVG only) ────────────────────────
function Mark({ size = 28, tone = 'soil' }) {
  const color = tone === 'know' ? 'var(--w-know-deep)' : 'var(--w-soil-deep)';
  return (
    <svg viewBox="0 0 32 32" width={size} height={size} aria-hidden="true">
      {/* concentric arcs — recursion echo from DS */}
      <circle cx="16" cy="16" r="14" fill="none" stroke={color} strokeWidth="1.2" opacity=".25"/>
      <circle cx="16" cy="16" r="10" fill="none" stroke={color} strokeWidth="1.2" opacity=".5"/>
      <circle cx="16" cy="16" r="6"  fill={color}/>
      {/* sprout */}
      <path d="M16 13 q-3 -1 -4 -4 q3 0 4 4 z" fill="var(--paper)"/>
      <path d="M16 14 q3 -1 4 -4 q-3 0 -4 4 z" fill="var(--paper)"/>
    </svg>
  );
}

// ─── Module Shell — header / tabs / body / footer ───────────────────────────
function Shell({ module: mod = 'market', title = 'SFA', subtitle = 'small farms agents', stale = false, fresh = 'עודכן לפני 2 שעות', sources = '7 מקורות', children, footer = true, hideTabs = false, version = 'v0.1', icon = '⌕' }) {
  return (
    <div className="sfa-shell">
      <div className="sfa-h">
        <span className="sfa-h__mark"><Mark tone={mod === 'market' ? 'know' : 'soil'}/></span>
        <div>
          <div className="sfa-h__title">{title}</div>
          <div className="sfa-h__sub">{subtitle}</div>
        </div>
        <span className="sfa-h__spacer"/>
        <span className="sfa-h__icon" title="חיפוש">{icon}</span>
      </div>

      {!hideTabs && (
        <nav className="sfa-tabs" role="tablist" aria-label="עבור בין מודולים">
          <button className={`sfa-tabs__btn ${mod === 'market' ? 'is-active' : ''}`} data-mod="market"><span className="dot"/>מדד מחירים</button>
          <button className={`sfa-tabs__btn ${mod === 'book'   ? 'is-active' : ''}`} data-mod="book"><span className="dot"/>ספר גידולים</button>
        </nav>
      )}

      <div className="sfa-body">{children}</div>

      {footer && (
        <div className="sfa-foot">
          <span className="dot" style={{ background: stale ? '#c47b2e' : 'var(--w-soil)' }}/>
          <span>{stale ? 'עשוי שלא להיות עדכני' : fresh}</span>
          <span className="sfa-foot__sep">·</span>
          <span>{sources}</span>
          <span className="sfa-foot__sep">·</span>
          <span style={{ marginInlineStart: 'auto' }}>SFA {version}</span>
        </div>
      )}
    </div>
  );
}

// ─── Small reusable bits ─────────────────────────────────────────────────────
function Pill({ tone = 'muted', children }) {
  return <span className={`pill pill--${tone}`}>{children}</span>;
}

function FreshDot({ state = 'fresh' }) {
  const map = { fresh: 'var(--w-soil)', stale: '#c47b2e', error: 'var(--spark)' };
  return <span style={{ display: 'inline-block', width: 8, height: 8, borderRadius: 99, background: map[state], marginInlineEnd: 6 }}/>;
}

// Search bar
function SearchBar({ placeholder = 'חיפוש...', value = '', tone = 'know' }) {
  return (
    <label style={{
      display: 'flex', alignItems: 'center', gap: 8,
      padding: '10px 12px',
      background: 'var(--paper)',
      border: '1px solid var(--line)',
      borderRadius: 'var(--radius-pill)',
      marginBottom: 10,
      fontSize: 14
    }}>
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ color: 'var(--ink-soft)', flex: 'none' }}><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>
      <span style={{ color: value ? 'var(--ink)' : 'var(--ink-soft)', flex: 1 }}>{value || placeholder}</span>
      {value && <span className="pill pill--muted" style={{ fontSize: 10 }}>{value.length}</span>}
    </label>
  );
}

// Chip strip
function ChipStrip({ items, active, tone = 'know' }) {
  return (
    <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 12 }}>
      {items.map((it, i) => (
        <button key={i} className={`pill ${active === it ? `pill--${tone}` : 'pill--muted'}`}
          style={{ border: 'none', cursor: 'pointer', fontFamily: 'inherit', padding: '5px 11px', fontSize: 12 }}>
          {it}
        </button>
      ))}
    </div>
  );
}

// Section heading inside body
function SectionTitle({ children, small }) {
  return (
    <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, margin: '4px 0 8px' }}>
      <h3 style={{ margin: 0, fontFamily: 'Frank Ruhl Libre, serif', fontWeight: 600, fontSize: 17, lineHeight: 1.15 }}>{children}</h3>
      {small && <span style={{ fontFamily: 'JetBrains Mono', fontSize: 10, color: 'var(--ink-soft)', textTransform: 'uppercase', letterSpacing: '.08em' }}>{small}</span>}
    </div>
  );
}

// Cross-link CTA — appears in both module details to link to the other
function CrossLink({ from = 'crop', label, sub }) {
  // from='crop' → CTA to market; from='market' → CTA to crop book
  const tone = from === 'crop' ? 'know' : 'soil';
  const arrow = '↗';
  return (
    <a href="#" style={{
      display: 'flex', alignItems: 'center', gap: 10,
      padding: '10px 12px',
      border: `1px solid color-mix(in oklch, var(--w-${tone}) 30%, var(--paper))`,
      background: `color-mix(in oklch, var(--w-${tone}) 6%, var(--paper))`,
      borderRadius: 'var(--radius-m)',
      textDecoration: 'none', color: 'var(--ink)',
      marginBottom: 10,
    }}>
      <span style={{
        width: 26, height: 26, borderRadius: 99,
        background: `var(--w-${tone})`, color: '#fff',
        display: 'grid', placeItems: 'center', fontSize: 13, flex: 'none'
      }}>{arrow}</span>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontWeight: 600, fontSize: 13, lineHeight: 1.2 }}>{label}</div>
        {sub && <div style={{ fontSize: 11, color: 'var(--ink-soft)', marginTop: 2 }}>{sub}</div>}
      </div>
      <span style={{ color: `var(--w-${tone}-deep)`, fontWeight: 700, fontSize: 13 }}>פתח</span>
    </a>
  );
}

// Export to window for cross-file use
Object.assign(window, { Mark, Shell, Pill, FreshDot, SearchBar, ChipStrip, SectionTitle, CrossLink });
