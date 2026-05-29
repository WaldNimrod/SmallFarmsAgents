<?php
/**
 * crop_section.php — Reusable section wrapper for crop detail page.
 *
 * Variables expected from include scope:
 *   $section_id      (string) — anchor id, e.g. 'calendar'
 *   $section_title   (string) — Hebrew heading text
 *   $section_content (string) — pre-rendered inner HTML
 *   $section_icon    (string) optional — emoji or short glyph for the section
 *
 * BEM: .cb-section, .cb-section__head, .cb-section__title, .cb-section__body
 */
$section_id      = (string)($section_id      ?? '');
$section_title   = (string)($section_title   ?? '');
$section_content = (string)($section_content ?? '');
$section_icon    = (string)($section_icon    ?? '');
?>
<section class="cb-section" id="<?= htmlspecialchars($section_id, ENT_QUOTES, 'UTF-8') ?>">
  <div class="cb-section__head">
    <h2 class="cb-section__title">
      <?php if ($section_icon !== ''): ?><span class="cb-section__icon" aria-hidden="true"><?= htmlspecialchars($section_icon, ENT_QUOTES, 'UTF-8') ?></span><?php endif; ?>
      <?= htmlspecialchars($section_title, ENT_QUOTES, 'UTF-8') ?>
    </h2>
  </div>
  <div class="cb-section__body">
    <?= $section_content ?>
  </div>
</section>
