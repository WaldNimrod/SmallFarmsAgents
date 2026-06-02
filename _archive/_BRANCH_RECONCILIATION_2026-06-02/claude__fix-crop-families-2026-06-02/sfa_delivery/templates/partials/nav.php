<?php
/**
 * nav.php — global persistent top bar (AC-U4-06)
 *
 * Included by _layout.php before the shell divs so it appears on EVERY page
 * regardless of mobile/desktop shell. Positioned sticky via hub.css.
 *
 * Variables (provided by _layout.php scope):
 *   $active  string  — active section key: 'home' | 'crop-book' | 'market' | 'calc'
 *
 * Primary bar links: בית (/) · ספר גידולים (/crop-book/) · שוק (/market/)
 * Disabled placeholder: קהילה (hidden until ready)
 * Secondary row (shown when $active === 'crop-book'):
 *   שאלות · משפחות · טבלה · כיסוי
 *
 * RTL. Mobile: collapses to a hamburger toggle below 900px.
 */
$active = $active ?? '';
?>
<nav id="sfa-topnav" class="sfa-nav" dir="rtl" aria-label="ניווט ראשי">
  <div class="sfa-nav__bar">
    <a class="sfa-nav__brand" href="/" aria-label="Small Farms Agents — דף הבית">
      <span class="sfa-nav__brand-mark"><?php include __DIR__ . '/../shell/_mark_svg.php'; ?></span>
      <span class="sfa-nav__brand-name">SFA</span>
    </a>

    <button class="sfa-nav__toggle" id="sfa-nav-toggle" aria-label="תפריט" aria-expanded="false" aria-controls="sfa-nav-links" type="button">
      <span class="sfa-nav__toggle-bar"></span>
      <span class="sfa-nav__toggle-bar"></span>
      <span class="sfa-nav__toggle-bar"></span>
    </button>

    <ul class="sfa-nav__links" id="sfa-nav-links" role="list">
      <li>
        <a class="sfa-nav__link<?= $active === 'home'      ? ' is-active' : '' ?>" href="/">בית</a>
      </li>
      <li>
        <a class="sfa-nav__link<?= $active === 'crop-book' ? ' is-active' : '' ?>" href="/crop-book/">ספר גידולים</a>
      </li>
      <li>
        <a class="sfa-nav__link<?= $active === 'market'    ? ' is-active' : '' ?>" href="/market/">שוק</a>
      </li>
      <li>
        <span class="sfa-nav__link sfa-nav__link--disabled" aria-disabled="true">קהילה <span class="sfa-nav__coming">בקרוב</span></span>
      </li>
    </ul>
  </div>

  <?php if ($active === 'crop-book'): ?>
  <div class="sfa-nav__sub" aria-label="תת-ניווט ספר גידולים">
    <ul class="sfa-nav__sublinks" role="list">
      <li><a class="sfa-nav__sublink" href="/crop-book/questions">שאלות</a></li>
      <li><a class="sfa-nav__sublink" href="/crop-book/family">משפחות</a></li>
      <li><a class="sfa-nav__sublink" href="/crop-book/table">טבלה</a></li>
      <li><a class="sfa-nav__sublink" href="/crop-book/cover-crops">כיסוי</a></li>
    </ul>
  </div>
  <?php endif; ?>
</nav>
<script>
(function() {
  var btn = document.getElementById('sfa-nav-toggle');
  var links = document.getElementById('sfa-nav-links');
  if (btn && links) {
    btn.addEventListener('click', function() {
      var open = btn.getAttribute('aria-expanded') === 'true';
      btn.setAttribute('aria-expanded', open ? 'false' : 'true');
      links.classList.toggle('is-open', !open);
    });
  }
})();
</script>
