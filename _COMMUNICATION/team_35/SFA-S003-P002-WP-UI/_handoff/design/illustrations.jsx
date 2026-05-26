/* illustrations.jsx — watercolor SVG library, lightweight build.
   Approach: layered translucent gradient fills + slightly off-register
   strokes + ONE shared SVG <filter> for hero washes only.
   No per-icon feDisplacementMap (kills performance at scale). */

function WatercolorDefs() {
  return (
    <svg width="0" height="0" style={{ position: 'absolute' }} aria-hidden="true">
      <defs>
        {/* Single soft-blur filter (cheap) — used only on big background washes */}
        <filter id="wc-blur" x="-5%" y="-5%" width="110%" height="110%">
          <feGaussianBlur stdDeviation="1.2"/>
        </filter>

        {/* gradients (warm farm palette, mirrors nimrod.bio illustrations) */}
        <radialGradient id="wc-tomato" cx="40%" cy="35%" r="65%">
          <stop offset="0"   stopColor="#ea7b4d"/>
          <stop offset=".6"  stopColor="#c24f2c"/>
          <stop offset="1"   stopColor="#8e3018"/>
        </radialGradient>
        <radialGradient id="wc-leaf" cx="40%" cy="35%" r="65%">
          <stop offset="0"   stopColor="#9bb172"/>
          <stop offset=".7"  stopColor="#6f8a45"/>
          <stop offset="1"   stopColor="#4d6a2c"/>
        </radialGradient>
        <radialGradient id="wc-leaf-soft" cx="40%" cy="35%" r="65%">
          <stop offset="0"   stopColor="#b8c98a"/>
          <stop offset="1"   stopColor="#7c9a52"/>
        </radialGradient>
        <radialGradient id="wc-carrot" cx="40%" cy="35%" r="65%">
          <stop offset="0"   stopColor="#e89a4a"/>
          <stop offset=".6"  stopColor="#c87024"/>
          <stop offset="1"   stopColor="#8e4a18"/>
        </radialGradient>
        <radialGradient id="wc-pepper" cx="40%" cy="35%" r="65%">
          <stop offset="0"   stopColor="#e25346"/>
          <stop offset=".7"  stopColor="#b32a1e"/>
          <stop offset="1"   stopColor="#7a1a14"/>
        </radialGradient>
        <radialGradient id="wc-onion" cx="40%" cy="35%" r="65%">
          <stop offset="0"   stopColor="#d4a368"/>
          <stop offset=".7"  stopColor="#a07640"/>
          <stop offset="1"   stopColor="#6c4a24"/>
        </radialGradient>
        <radialGradient id="wc-sun" cx="50%" cy="40%" r="65%">
          <stop offset="0"   stopColor="#f6dc8a"/>
          <stop offset=".7"  stopColor="#e2b23a"/>
          <stop offset="1"   stopColor="#a87616"/>
        </radialGradient>
        <radialGradient id="wc-soil" cx="50%" cy="30%" r="80%">
          <stop offset="0"   stopColor="#a67844"/>
          <stop offset="1"   stopColor="#6e4a24"/>
        </radialGradient>

        {/* generic "bleed" gradient for washes — overlaid with low opacity */}
        <radialGradient id="wc-bleed" cx="50%" cy="50%" r="50%">
          <stop offset="0"   stopColor="white"  stopOpacity=".25"/>
          <stop offset=".7"  stopColor="white"  stopOpacity="0"/>
          <stop offset="1"   stopColor="black"  stopOpacity=".1"/>
        </radialGradient>
      </defs>
    </svg>
  );
}

/* ─── Wash blob (used in cropcard bg + crosslinks) ──────────────────── */
function Wash({ color, w = 200, h = 120, opacity = .35, seed = 1 }) {
  return (
    <svg viewBox={`0 0 ${w} ${h}`} width={w} height={h} aria-hidden="true" style={{ display: 'block' }}>
      <g opacity={opacity} filter="url(#wc-blur)">
        <ellipse cx={w/2}     cy={h/2}     rx={w*0.42} ry={h*0.42} fill={color}/>
        <ellipse cx={w*0.62}  cy={h*0.55}  rx={w*0.28} ry={h*0.3}  fill={color} opacity=".6"/>
        <ellipse cx={w*0.36}  cy={h*0.4}   rx={w*0.18} ry={h*0.2}  fill={color} opacity=".5"/>
      </g>
    </svg>
  );
}

/* ─── Tomato ───────────────────────────────────────────────────────── */
function Tomato({ size = 60 }) {
  return (
    <svg viewBox="0 0 60 60" width={size} height={size} aria-hidden="true">
      <g transform="translate(30 34)">
        <circle r="20" fill="url(#wc-tomato)"/>
        <circle r="20" fill="url(#wc-bleed)"/>
        <ellipse cx="-5" cy="-8" rx="6" ry="4" fill="#fff" opacity=".28"/>
      </g>
      {/* leaves */}
      <g transform="translate(30 14)">
        <path d="M-9 1 Q-5 -5 0 -2 Q5 -5 9 1 Q5 4 0 3 Q-5 4 -9 1 Z" fill="url(#wc-leaf)"/>
        <path d="M0 -1 L0 6" stroke="#4d6a2c" strokeWidth="1.3" strokeLinecap="round"/>
        <path d="M-5 0 L-6 -3" stroke="#4d6a2c" strokeWidth="1" strokeLinecap="round"/>
        <path d="M5 0 L6 -3" stroke="#4d6a2c" strokeWidth="1" strokeLinecap="round"/>
      </g>
    </svg>
  );
}

/* ─── Lettuce ──────────────────────────────────────────────────────── */
function Lettuce({ size = 60 }) {
  return (
    <svg viewBox="0 0 60 60" width={size} height={size} aria-hidden="true">
      <g transform="translate(30 36)">
        <ellipse rx="22" ry="14" fill="url(#wc-leaf-soft)"/>
        <ellipse cx="-3" cy="-7" rx="14" ry="10" fill="url(#wc-leaf)" opacity=".9"/>
        <ellipse cx="7"  cy="-3" rx="10" ry="8"  fill="url(#wc-leaf)" opacity=".75"/>
        <ellipse cx="-10" cy="-1" rx="8" ry="6"  fill="url(#wc-leaf-soft)" opacity=".9"/>
        <ellipse rx="20" ry="13" fill="url(#wc-bleed)"/>
      </g>
      <g stroke="#4d6a2c" strokeWidth=".8" opacity=".55" fill="none" strokeLinecap="round">
        <path d="M30 23 Q30 32 30 42"/>
        <path d="M21 32 Q23 36 27 40"/>
        <path d="M39 32 Q37 36 33 40"/>
      </g>
    </svg>
  );
}

/* ─── Carrot ───────────────────────────────────────────────────────── */
function Carrot({ size = 60 }) {
  return (
    <svg viewBox="0 0 60 60" width={size} height={size} aria-hidden="true">
      <g transform="translate(30 32)">
        <path d="M-8 -4 Q-10 18 0 22 Q10 18 8 -4 Q4 -6 0 -5 Q-4 -6 -8 -4 Z" fill="url(#wc-carrot)"/>
        <path d="M-7 -3 Q-9 17 0 20 Q9 17 7 -3 Z" fill="url(#wc-bleed)"/>
      </g>
      <g stroke="#8e4a18" strokeWidth=".55" opacity=".55" fill="none">
        <path d="M26.5 32 L28 48"/>
        <path d="M30 32 L30 50"/>
        <path d="M33.5 32 L32 48"/>
      </g>
      <g transform="translate(30 18)">
        <path d="M0 8 Q-2 -2 -8 -6 Q-4 4 0 8 Z" fill="url(#wc-leaf)"/>
        <path d="M0 8 Q2 -2 8 -6 Q4 4 0 8 Z" fill="url(#wc-leaf)"/>
        <path d="M0 8 Q0 -3 0 -10 Q2 -2 1 8 Z" fill="url(#wc-leaf-soft)"/>
      </g>
    </svg>
  );
}

/* ─── Pepper ───────────────────────────────────────────────────────── */
function Pepper({ size = 60 }) {
  return (
    <svg viewBox="0 0 60 60" width={size} height={size} aria-hidden="true">
      <g transform="translate(30 35)">
        <path d="M-13 -5 Q-15 12 -4 16 Q5 18 11 12 Q15 4 13 -6 Q7 -2 0 -2 Q-7 -2 -13 -5 Z" fill="url(#wc-pepper)"/>
        <path d="M-12 -4 Q-14 11 -4 15 Q5 17 10 11 Q14 4 12 -5 Z" fill="url(#wc-bleed)"/>
        <ellipse cx="-5" cy="-1" rx="3" ry="6" fill="#fff" opacity=".22"/>
      </g>
      <g transform="translate(30 19)">
        <ellipse rx="5" ry="2.5" fill="url(#wc-leaf)"/>
        <path d="M0 0 L0 -6" stroke="#4d6a2c" strokeWidth="1.6" strokeLinecap="round"/>
      </g>
    </svg>
  );
}

/* ─── Onion ────────────────────────────────────────────────────────── */
function Onion({ size = 60 }) {
  return (
    <svg viewBox="0 0 60 60" width={size} height={size} aria-hidden="true">
      <g transform="translate(30 36)">
        <path d="M-12 -4 Q-14 12 0 16 Q14 12 12 -4 Q8 -10 0 -10 Q-8 -10 -12 -4 Z" fill="url(#wc-onion)"/>
        <path d="M-11 -3 Q-13 11 0 15 Q13 11 11 -3 Z" fill="url(#wc-bleed)"/>
      </g>
      <g stroke="#6e4a24" strokeWidth=".5" opacity=".5" fill="none">
        <path d="M20 32 Q30 38 40 32"/>
        <path d="M22 38 Q30 44 38 38"/>
      </g>
      <g stroke="#4d6a2c" strokeWidth="1.3" strokeLinecap="round" fill="none">
        <path d="M28 22 Q26 14 22 8"/>
        <path d="M30 22 L30 6"/>
        <path d="M32 22 Q34 14 38 8"/>
      </g>
    </svg>
  );
}

/* ─── Cucumber ─────────────────────────────────────────────────────── */
function Cucumber({ size = 60 }) {
  return (
    <svg viewBox="0 0 60 60" width={size} height={size} aria-hidden="true">
      <g transform="translate(30 32) rotate(-22)">
        <rect x="-22" y="-7" width="44" height="14" rx="7" fill="url(#wc-leaf-soft)"/>
        <rect x="-22" y="-7" width="44" height="14" rx="7" fill="url(#wc-bleed)"/>
        <rect x="-22" y="-7" width="44" height="5" rx="2.5" fill="url(#wc-leaf)" opacity=".45"/>
      </g>
      <g fill="#4d6a2c" opacity=".55">
        {[0,1,2,3,4,5].map(i => <circle key={i} cx={15 + i*5.5} cy={32 - i*2} r=".9"/>)}
      </g>
    </svg>
  );
}

/* ─── Basil ────────────────────────────────────────────────────────── */
function Basil({ size = 60 }) {
  return (
    <svg viewBox="0 0 60 60" width={size} height={size} aria-hidden="true">
      <path d="M30 50 Q30 30 30 14" stroke="#4d6a2c" strokeWidth="1.4" fill="none"/>
      <ellipse cx="22" cy="36" rx="6" ry="9" fill="url(#wc-leaf)"        transform="rotate(-30 22 36)"/>
      <ellipse cx="38" cy="32" rx="6" ry="9" fill="url(#wc-leaf-soft)"   transform="rotate(30 38 32)"/>
      <ellipse cx="24" cy="22" rx="5" ry="8" fill="url(#wc-leaf)"        transform="rotate(-20 24 22)"/>
      <ellipse cx="36" cy="18" rx="5" ry="8" fill="url(#wc-leaf-soft)"   transform="rotate(20 36 18)"/>
      <ellipse cx="30" cy="12" rx="4" ry="6" fill="url(#wc-leaf)"/>
    </svg>
  );
}

/* ─── Strawberry ───────────────────────────────────────────────────── */
function Strawberry({ size = 60 }) {
  return (
    <svg viewBox="0 0 60 60" width={size} height={size} aria-hidden="true">
      <g transform="translate(30 36)">
        <path d="M-14 -6 Q-12 16 0 20 Q12 16 14 -6 Q6 -8 0 -6 Q-6 -8 -14 -6 Z" fill="url(#wc-tomato)"/>
        <path d="M-13 -5 Q-11 15 0 19 Q11 15 13 -5 Z" fill="url(#wc-bleed)"/>
      </g>
      <g fill="#f6e89a" opacity=".85">
        {[[-6,-2],[2,0],[8,4],[-2,6],[-8,8],[4,10],[-4,14],[6,14]].map(([x,y],i) =>
          <ellipse key={i} cx={30+x} cy={34+y} rx=".7" ry="1.1" transform={`rotate(${i*30} ${30+x} ${34+y})`}/>)}
      </g>
      <g transform="translate(30 18)">
        <path d="M-8 0 L-2 4 L0 -3 L2 4 L8 0 L4 6 L-4 6 Z" fill="url(#wc-leaf)"/>
      </g>
    </svg>
  );
}

/* ─── Sun ──────────────────────────────────────────────────────────── */
function Sun({ size = 80 }) {
  return (
    <svg viewBox="0 0 80 80" width={size} height={size} aria-hidden="true">
      <circle cx="40" cy="40" r="20" fill="url(#wc-sun)"/>
      <circle cx="40" cy="40" r="20" fill="url(#wc-bleed)"/>
      <g stroke="#a87616" strokeWidth="1.6" strokeLinecap="round" opacity=".75">
        {[0,45,90,135,180,225,270,315].map(d => {
          const r1 = 22, r2 = 32;
          const a = (d * Math.PI) / 180;
          return <line key={d} x1={40 + r1*Math.cos(a)} y1={40 + r1*Math.sin(a)} x2={40 + r2*Math.cos(a)} y2={40 + r2*Math.sin(a)}/>;
        })}
      </g>
    </svg>
  );
}

/* ─── Soil patch ───────────────────────────────────────────────────── */
function SoilPatch({ w = 390, h = 80 }) {
  return (
    <svg viewBox={`0 0 ${w} ${h}`} width={w} height={h} aria-hidden="true" style={{ display: 'block' }}>
      <path d={`M0 ${h*0.45} Q${w*0.2} ${h*0.2} ${w*0.4} ${h*0.45} Q${w*0.6} ${h*0.7} ${w*0.8} ${h*0.45} Q${w} ${h*0.2} ${w} ${h*0.6} L${w} ${h} L0 ${h} Z`} fill="url(#wc-soil)" opacity=".7"/>
      <g stroke="#4d6a2c" strokeWidth="1.2" strokeLinecap="round" fill="none">
        {[0.15, 0.32, 0.55, 0.72, 0.88].map((p, i) => (
          <g key={i} transform={`translate(${w*p} ${h*0.45})`}>
            <path d="M0 0 L0 -14"/>
            <path d="M0 -8 Q-4 -10 -6 -14"/>
            <path d="M0 -8 Q4 -10 6 -14"/>
          </g>
        ))}
      </g>
    </svg>
  );
}

/* ─── Corner sprig ─────────────────────────────────────────────────── */
function CornerSprig({ size = 80, flip = false }) {
  return (
    <svg viewBox="0 0 80 80" width={size} height={size} aria-hidden="true" style={{ transform: flip ? 'scaleX(-1)' : 'none' }}>
      <path d="M10 70 Q30 50 50 30 Q60 18 70 12" stroke="#4d6a2c" strokeWidth="1.6" fill="none" opacity=".7"/>
      <ellipse cx="22" cy="58" rx="5" ry="8" fill="url(#wc-leaf)"      opacity=".75" transform="rotate(40 22 58)"/>
      <ellipse cx="36" cy="42" rx="5" ry="8" fill="url(#wc-leaf-soft)" opacity=".75" transform="rotate(40 36 42)"/>
      <ellipse cx="52" cy="24" rx="4" ry="6" fill="url(#wc-leaf)"      opacity=".75" transform="rotate(50 52 24)"/>
    </svg>
  );
}

/* ─── Header wash → DEPRECATED (replaced by ImagePrompt slots).
   Kept as no-op shim so older calls don't crash. */
function HeaderWash() { return null; }

/* ─── Picker ───────────────────────────────────────────────────────── */
const CROP_ICON = {
  tomato: Tomato, lettuce: Lettuce, cucumber: Cucumber, carrot: Carrot,
  pepper: Pepper, onion: Onion, basil: Basil, strawberry: Strawberry,
};
function CropIcon({ kind, size = 56 }) {
  const C = CROP_ICON[kind] || Lettuce;
  return <C size={size}/>;
}

Object.assign(window, {
  WatercolorDefs, Wash,
  Tomato, Lettuce, Cucumber, Carrot, Pepper, Onion, Basil, Strawberry,
  Sun, SoilPatch, CornerSprig, HeaderWash, CropIcon,
});
