<?php
/**
 * Mobile shell — .gj-shell per COMPONENTS.md §1.1.
 * Visibility swap to desktop happens via CSS media query (≥900px) in desktop-extras.css.
 *
 * Variables (provided by _layout.php / page templates):
 *   $page_title  string  — header title
 *   $page_sub    string  — header subtitle
 *   $body_html   string  — page body HTML (escaped by page template)
 *   $back_url    ?string — optional back-arrow URL
 *   $tabs        ?array  — optional [['label'=>'…','href'=>'/…','active'=>bool], …]
 *   $status      string  — fresh|aging|stale|error (footer dot color)
 *   $foot_text   string  — footer caption
 */
?>
<div class="gj-shell">
  <header class="gj-header gj-header--plain">
    <div class="gj-header__row">
      <?php if (!empty($back_url)): ?>
        <a class="gj-iconbtn" aria-label="חזרה" href="<?= htmlspecialchars((string)$back_url, ENT_QUOTES, 'UTF-8') ?>">←</a>
      <?php endif; ?>
      <span class="gj-mark"><?php include __DIR__ . '/_mark_svg.php'; ?></span>
      <div class="gj-header__title">
        <div class="gj-title"><?= htmlspecialchars((string)($page_title ?? 'SFA'), ENT_QUOTES, 'UTF-8') ?></div>
        <div class="gj-sub"><?= htmlspecialchars((string)($page_sub ?? 'חקלאות קטנה'), ENT_QUOTES, 'UTF-8') ?></div>
      </div>
      <a class="gj-iconbtn" aria-label="חיפוש" href="/search">⌕</a>
    </div>
    <?php if (!empty($tabs) && is_array($tabs)): ?>
      <nav class="gj-tabs" role="tablist">
        <?php foreach ($tabs as $tab): ?>
          <a class="gj-tab<?= !empty($tab['active']) ? ' is-active' : '' ?>"
             href="<?= htmlspecialchars((string)($tab['href'] ?? '#'), ENT_QUOTES, 'UTF-8') ?>"
             role="tab"
             aria-selected="<?= !empty($tab['active']) ? 'true' : 'false' ?>"><?= htmlspecialchars((string)($tab['label'] ?? ''), ENT_QUOTES, 'UTF-8') ?></a>
        <?php endforeach; ?>
      </nav>
    <?php endif; ?>
  </header>
  <main class="gj-body">
    <?= $body_html ?? '' ?>
  </main>
  <footer class="gj-foot">
    <span class="gj-foot__dot" style="background: var(--status-<?= htmlspecialchars((string)($status ?? 'fresh'), ENT_QUOTES, 'UTF-8') ?>)"></span>
    <span><?= htmlspecialchars((string)($foot_text ?? ('עודכן ' . date('H:i'))), ENT_QUOTES, 'UTF-8') ?></span>
  </footer>
</div>
