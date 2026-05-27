<?php
/**
 * Desktop shell — .dt-shell per COMPONENTS.md §1.2.
 * Visibility swap from mobile happens via CSS media query (≥900px) in desktop-extras.css.
 *
 * Variables (provided by _layout.php / page templates):
 *   $page_title  string  — top-bar h1
 *   $page_sub    ?string — top-bar subtitle (optional)
 *   $body_html   string  — page body HTML
 *   $active      string  — active nav key: 'home' | 'crop-book' | 'market' | 'calc'
 *   $stats       array   — ['crop_count' => int, 'product_count' => int, 'contrib_count' => int, 'source_count' => int]
 */
$active        = $active ?? '';
$stats         = $stats  ?? [];
$crop_count    = (int)($stats['crop_count']    ?? 66);
$product_count = (int)($stats['product_count'] ?? 30);
$contrib_count = (int)($stats['contrib_count'] ?? 0);
$source_count  = (int)($stats['source_count']  ?? 25);
?>
<div class="dt-shell">
  <aside class="dt-side">
    <div class="dt-side__brand">
      <span class="dt-side__brand-mark"><?php include __DIR__ . '/_mark_svg.php'; ?></span>
      <div class="dt-side__name">SFA</div>
    </div>

    <form id="dt-search-form" class="dt-side__search-form" action="/search" method="get" role="search">
      <input class="dt-side__search" type="search" name="q" placeholder="חיפוש…" aria-label="חיפוש"/>
    </form>

    <nav class="dt-nav" aria-label="ניווט ראשי">

      <details class="dt-acc" open>
        <summary>
          <span class="tier tier--leaf"><span class="tier__glyph">●</span>כלים לקהילה</span>
          <span class="dt-acc__chev">▾</span>
        </summary>
        <a class="<?= $active === 'home'      ? 'is-active' : '' ?>" href="/">דף הבית</a>
        <a class="<?= $active === 'crop-book' ? 'is-active' : '' ?>" href="/crop-book/">ספר גידולים <span class="dt-nav__count"><?= $crop_count ?></span></a>
        <a class="<?= $active === 'market'    ? 'is-active' : '' ?>" href="/market/">מחירון <span class="dt-nav__count"><?= $product_count ?></span></a>
        <a class="<?= $active === 'calc'      ? 'is-active' : '' ?>" href="/calc">מחשבון <span class="pill pill--code dt-nav__pill">β</span></a>
      </details>

      <details class="dt-acc">
        <summary>
          <span class="tier tier--soil"><span class="tier__glyph">★</span>כלים מתקדמים</span>
          <span class="dt-acc__chev">▾</span>
        </summary>
        <a class="dt-nav__disabled" aria-disabled="true">ניהול לקוחות <span class="pill pill--muted">בקרוב</span></a>
        <a class="dt-nav__disabled" aria-disabled="true">מעקב יבול <span class="pill pill--muted">בקרוב</span></a>
      </details>

      <details class="dt-acc">
        <summary>
          <span class="tier tier--tomato"><span class="tier__glyph">✎</span>בדיוק לחווה שלך</span>
          <span class="dt-acc__chev">▾</span>
        </summary>
        <a class="dt-nav__disabled" aria-disabled="true">חיבור Tend <span class="pill pill--muted">בקרוב</span></a>
        <a class="dt-nav__disabled" aria-disabled="true">יומן שדה <span class="pill pill--muted">בקרוב</span></a>
        <a class="dt-nav__cta" href="https://wa.me/972547776770">+ הציעו כלי חדש</a>
      </details>

      <details class="dt-acc dt-acc--comm" open>
        <summary>
          <span class="tier tier--sun"><span class="tier__glyph">✺</span>קהילה</span>
          <span class="dt-acc__chev">▾</span>
        </summary>
        <div class="dt-side__stats">
          <div><strong><?= $contrib_count ?></strong><span>תיקונים</span></div>
          <div><strong><?= $source_count ?></strong><span>מקורות</span></div>
        </div>
        <div class="dt-side__contrib">
          <a class="dt-side__crow" href="https://wa.me/972547776770?text=תרומת+ידע">✎ תרמו ידע</a>
          <a class="dt-side__crow" href="https://wa.me/972547776770?text=דיווח+שגיאה">◐ דווחו על שגיאה</a>
          <a class="dt-side__crow" href="https://wa.me/972547776770?text=הצעת+פיצ׳ר">💡 הציעו פיצ׳ר</a>
        </div>
        <a class="dt-side__wa" href="https://wa.me/972547776770">💬 WhatsApp · ‎צ׳אט פתוח</a>
      </details>

    </nav>
  </aside>

  <main class="dt-main">
    <header class="dt-topbar">
      <div>
        <h1 class="dt-topbar__h"><?= htmlspecialchars((string)($page_title ?? 'SFA'), ENT_QUOTES, 'UTF-8') ?></h1>
        <?php if (!empty($page_sub)): ?>
          <p class="dt-topbar__sub"><?= htmlspecialchars((string)$page_sub, ENT_QUOTES, 'UTF-8') ?></p>
        <?php endif; ?>
      </div>
      <div class="dt-topbar__tools">
        <a class="dt-topbar__contrib" href="https://wa.me/972547776770?text=תרומת+ידע">+ תרמו ידע</a>
      </div>
    </header>
    <div class="dt-content">
      <?= $body_html ?? '' ?>
    </div>
  </main>
</div>
