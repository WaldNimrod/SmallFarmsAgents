<?php
/**
 * module_card.php — COMPONENTS.md §3
 *
 * Required vars (passed in via include scope):
 *   $module — array with keys:
 *     slug, name_he, tier (open|beta|coming|paid|custom),
 *     tier_color (leaf|sun|paper|soil|tomato),
 *     sub_he, stat_he, href,
 *     icon_svg (trusted HTML) or icon_id (referencing icons.svg),
 *     data_tier (defaults to tier — drives dimming)
 *
 * BEM contract: .mod-card, .mod-card--{color}, .mod-card--{tier},
 *   .mod-card__art, .mod-card__icon, .mod-card__body,
 *   .mod-card__head, .mod-card__name, .mod-card__sub, .mod-card__stat
 *   plus data-tier attribute. Embeds .tier (tier_badge.php).
 */
$module = $module ?? [];
$slug       = (string)($module['slug']       ?? '');
$name_he    = (string)($module['name_he']    ?? '');
$tier       = (string)($module['tier']       ?? 'open');
$color      = (string)($module['tier_color'] ?? 'leaf');
$sub_he     = (string)($module['sub_he']     ?? '');
$stat_he    = (string)($module['stat_he']    ?? '');
$href       = (string)($module['href']       ?? '#');
$icon_svg   = (string)($module['icon_svg']   ?? '');
$icon_id    = (string)($module['icon_id']    ?? '');
$hero_url   = (string)($module['hero_url']   ?? '');
$data_tier  = (string)($module['data_tier']  ?? $tier);

// Fallback: if icon_svg not provided but icon_id is, build a <use> ref to icons.svg sprite.
if ($icon_svg === '' && $icon_id !== '') {
    $icon_id_esc = htmlspecialchars($icon_id, ENT_QUOTES, 'UTF-8');
    // Sprite is inlined by _layout.php; reference by fragment only (cross-browser-safe).
    $icon_svg = '<svg aria-hidden="true" viewBox="0 0 24 24"><use href="#' . $icon_id_esc . '"></use></svg>';
}
?>
<a class="mod-card mod-card--<?= htmlspecialchars($color, ENT_QUOTES, 'UTF-8') ?> mod-card--<?= htmlspecialchars($tier, ENT_QUOTES, 'UTF-8') ?>" href="<?= htmlspecialchars($href, ENT_QUOTES, 'UTF-8') ?>" data-tier="<?= htmlspecialchars($data_tier, ENT_QUOTES, 'UTF-8') ?>">
  <div class="mod-card__art">
    <?php if ($hero_url !== ''): ?>
      <img class="mod-card__hero" src="<?= htmlspecialchars($hero_url, ENT_QUOTES, 'UTF-8') ?>" alt="" loading="lazy" decoding="async">
    <?php endif; ?>
    <div class="mod-card__icon">
      <?= $icon_svg /* trusted */ ?>
    </div>
  </div>
  <div class="mod-card__body">
    <div class="mod-card__head">
      <h3 class="mod-card__name"><?= htmlspecialchars($name_he, ENT_QUOTES, 'UTF-8') ?></h3>
      <?php
        // Embed tier_badge — pass $tier; default size sm.
        $size = 'sm';
        include __DIR__ . '/tier_badge.php';
      ?>
    </div>
    <p class="mod-card__sub"><?= htmlspecialchars($sub_he, ENT_QUOTES, 'UTF-8') ?></p>
    <p class="mod-card__stat"><?= htmlspecialchars($stat_he, ENT_QUOTES, 'UTF-8') ?></p>
  </div>
</a>
