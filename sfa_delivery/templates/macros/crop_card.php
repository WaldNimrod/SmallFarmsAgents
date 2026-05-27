<?php
/**
 * crop_card.php — COMPONENTS.md §6
 *
 * Required vars (passed in via include scope):
 *   $crop — array with keys:
 *     slug, name_he, en_name, family_tag_he, dtm_days, icon_svg (trusted)
 *
 * BEM contract: .gj-cropcard, .gj-cropcard__art, .gj-cropcard__icon,
 *   .gj-cropcard__body, .gj-cropcard__name, .gj-cropcard__en,
 *   .gj-cropcard__meta, .gj-tag, .gj-cropcard__dtm
 */
$crop = $crop ?? [];
$slug          = (string)($crop['slug']          ?? '');
$name_he       = (string)($crop['name_he']       ?? '');
$en_name       = (string)($crop['en_name']       ?? '');
$family_tag_he = (string)($crop['family_tag_he'] ?? '');
$dtm_days      = $crop['dtm_days'] ?? null;
$icon_svg      = (string)($crop['icon_svg']      ?? '');
?>
<a class="gj-cropcard" href="/crop-book/<?= htmlspecialchars($slug, ENT_QUOTES, 'UTF-8') ?>">
  <div class="gj-cropcard__art">
    <div class="gj-cropcard__icon"><?= $icon_svg /* trusted */ ?></div>
  </div>
  <div class="gj-cropcard__body">
    <div class="gj-cropcard__name"><?= htmlspecialchars($name_he, ENT_QUOTES, 'UTF-8') ?></div>
    <div class="gj-cropcard__en"><?= htmlspecialchars($en_name, ENT_QUOTES, 'UTF-8') ?></div>
    <div class="gj-cropcard__meta">
      <span class="gj-tag"><?= htmlspecialchars($family_tag_he, ENT_QUOTES, 'UTF-8') ?></span>
      <?php if (!empty($dtm_days) && (int)$dtm_days !== -32768): ?>
        <span class="gj-cropcard__dtm"><?= (int)$dtm_days ?><small>ימים</small></span>
      <?php endif; ?>
    </div>
  </div>
</a>
