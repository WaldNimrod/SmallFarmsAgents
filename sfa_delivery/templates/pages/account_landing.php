<?php
/**
 * account_landing.php — Route /account — Class B v2
 *
 * WP-CB-UI-CLASSB §2.8 — Board-B frames `account` / `account-profile`.
 * Components: .acct-wrap, .acct-card, .acct-empty (§42),
 *             .acct-profile, .acct-prof-head, .setgroup, .setrow (+--danger).
 *
 * LOD400 §9.2: UI shell only + "בקרוב" labels.
 * No auth backend. No functional submit. Stable nav hook.
 * All inputs + buttons carry aria-disabled / "בקרוב" to signal not-yet status.
 */
use SFA\Lib\Template;

$h = [Template::class, 'h'];

$page_title = 'חשבון';
$page_sub   = 'SFA · חשבון';
$active     = 'account';

ob_start();
?>
<div class="acct-wrap">

  <?php /* Login card (logged-out state) */ ?>
  <div class="acct-card">
    <div class="acct-card__mark">
      <svg aria-hidden="true"><use href="#sfa-logo"/></svg>
    </div>
    <h1>ברוכים הבאים ל-SFA</h1>
    <p>ספר הגידולים והמחירון פתוחים לגמרי — ללא הרשמה. חשבון יפתח גישה לכלים מתקדמים בקרוב.</p>

    <div class="acct-field">
      <label for="acct-email">דוא"ל</label>
      <input type="email" id="acct-email" name="email" placeholder="your@email.com"
             autocomplete="email" aria-describedby="acct-soon-msg" disabled aria-disabled="true">
    </div>
    <div class="acct-field">
      <label for="acct-pw">סיסמה</label>
      <input type="password" id="acct-pw" name="password" placeholder="••••••••"
             autocomplete="current-password" disabled aria-disabled="true">
    </div>

    <button class="acct-btn" type="button" disabled aria-disabled="true" id="acct-soon-msg">
      כניסה — בקרוב
    </button>

    <div class="acct-soon" aria-label="מידע על מצב הכלי">
      ⏳ מערכת החשבונות בפיתוח — <strong>בקרוב</strong>
    </div>

    <p class="acct-alt">
      לשיתוף-פעולה: <a href="/community">דברו עם הקהילה</a>
    </p>
  </div>

  <?php /* Open-core empty state */ ?>
  <div class="acct-empty" style="margin-top:16px">
    <div class="acct-empty__ic" aria-hidden="true">🌿</div>
    <div>
      <b>הכלים הפתוחים — חינמיים לגמרי</b>
      <p>ספר גידולים, מחירון שוק ומחשבון שדה פתוחים לכולם ללא הרשמה.</p>
    </div>
  </div>

  <?php /* Static profile shell (account-profile frame) — all fields show "בקרוב" */ ?>
  <div class="acct-profile" style="margin-top:32px">

    <div class="acct-prof-head">
      <div class="acct-prof-head__av" aria-hidden="true">?</div>
      <div>
        <div class="acct-prof-head__name">לא מחובר</div>
        <div class="acct-prof-head__sub">חשבון · בקרוב</div>
      </div>
      <button class="acct-prof-head__edit" type="button" disabled aria-disabled="true">
        עריכה — בקרוב
      </button>
    </div>

    <div class="setgroup">
      <div class="setgroup__lbl">פרופיל</div>
      <div class="setrow">
        <div class="setrow__ic" aria-hidden="true">👤</div>
        <div class="setrow__t">שם<small>בקרוב</small></div>
        <span class="setrow__val">—</span>
        <span class="setrow__chev">›</span>
      </div>
      <div class="setrow">
        <div class="setrow__ic" aria-hidden="true">📧</div>
        <div class="setrow__t">דוא"ל<small>בקרוב</small></div>
        <span class="setrow__val">—</span>
        <span class="setrow__chev">›</span>
      </div>
      <div class="setrow">
        <div class="setrow__ic" aria-hidden="true">📍</div>
        <div class="setrow__t">אזור<small>בקרוב</small></div>
        <span class="setrow__val">—</span>
        <span class="setrow__chev">›</span>
      </div>
    </div>

    <div class="setgroup">
      <div class="setgroup__lbl">מודולים</div>
      <a class="setrow" href="/crop-book/">
        <div class="setrow__ic" aria-hidden="true">▤</div>
        <div class="setrow__t">ספר גידולים<small>פתוח · ללא הרשמה</small></div>
        <span class="setrow__val pill pill--leaf" style="font-size:10px">פעיל</span>
        <span class="setrow__chev">›</span>
      </a>
      <a class="setrow" href="/market/">
        <div class="setrow__ic" aria-hidden="true">₪</div>
        <div class="setrow__t">מחירון<small>פתוח · ללא הרשמה</small></div>
        <span class="setrow__val pill pill--tomato" style="font-size:10px">פעיל</span>
        <span class="setrow__chev">›</span>
      </a>
      <div class="setrow">
        <div class="setrow__ic" aria-hidden="true">🌾</div>
        <div class="setrow__t">כלים מתקדמים<small>בקרוב · מנוי</small></div>
        <span class="setrow__val" style="font-size:10px;color:var(--gj-ink-soft)">בקרוב</span>
        <span class="setrow__chev">›</span>
      </div>
    </div>

    <div class="setgroup">
      <div class="setgroup__lbl">מערכת</div>
      <a class="setrow" href="/about">
        <div class="setrow__ic" aria-hidden="true">ℹ</div>
        <div class="setrow__t">על SFA</div>
        <span class="setrow__chev">›</span>
      </a>
      <a class="setrow" href="/community">
        <div class="setrow__ic" aria-hidden="true">💬</div>
        <div class="setrow__t">קהילה</div>
        <span class="setrow__chev">›</span>
      </a>
      <div class="setrow setrow--danger">
        <div class="setrow__ic" aria-hidden="true">🚪</div>
        <div class="setrow__t">התנתק<small>בקרוב</small></div>
        <span class="setrow__chev">›</span>
      </div>
    </div>

  </div><!-- /acct-profile -->

</div><!-- /acct-wrap -->
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title', 'page_sub', 'active'));
