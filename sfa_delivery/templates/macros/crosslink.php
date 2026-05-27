<?php
/**
 * crosslink.php — COMPONENTS.md §4
 *
 * Required vars (passed in via include scope):
 *   $href       — destination URL
 *   $art_html   — trusted HTML for the icon/thumb slot
 *   $big_text   — large headline text
 *   $small_unit — small unit text rendered next to $big_text
 *   $sub_text   — secondary line
 *   $direction  — (optional) 'book-to-market' (default) | 'market-to-book'
 *                 'market-to-book' applies the .gj-crosslink--soil modifier.
 *
 * BEM contract: .gj-crosslink, .gj-crosslink--soil, .gj-crosslink__art,
 *   .gj-crosslink__body, .gj-crosslink__big, .gj-crosslink__sub,
 *   .gj-crosslink__cta
 */
$href       = (string)($href       ?? '/');
$art_html   = (string)($art_html   ?? '');
$big_text   = (string)($big_text   ?? '');
$small_unit = (string)($small_unit ?? '');
$sub_text   = (string)($sub_text   ?? '');
$direction  = (string)($direction  ?? 'book-to-market');

$is_soil = ($direction === 'market-to-book');
?>
<a href="<?= htmlspecialchars($href, ENT_QUOTES, 'UTF-8') ?>" class="gj-crosslink<?= $is_soil ? ' gj-crosslink--soil' : '' ?>">
  <div class="gj-crosslink__art"><?= $art_html /* trusted */ ?></div>
  <div class="gj-crosslink__body">
    <div class="gj-crosslink__big"><?= htmlspecialchars($big_text, ENT_QUOTES, 'UTF-8') ?> <small><?= htmlspecialchars($small_unit, ENT_QUOTES, 'UTF-8') ?></small></div>
    <div class="gj-crosslink__sub"><?= htmlspecialchars($sub_text, ENT_QUOTES, 'UTF-8') ?></div>
  </div>
  <span class="gj-crosslink__cta">פתח →</span>
</a>
