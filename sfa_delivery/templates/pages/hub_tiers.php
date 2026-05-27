<?php
/**
 * hub_tiers.php — Tier explainer page (route: /about)
 *
 * Mandate §3 contract: emits .gj-shell + .gj-body (provided by shell/mobile.php
 *   via _layout.php) plus .hub-tiers-intro + .hub-tier-list + .tier + .tier--lg +
 *   .tier--{leaf|sun|paper|soil|tomato} + .tier__glyph (the last 4 via
 *   macros/tier_badge.php with $size = 'lg').
 *
 * Architecture note: see hub_home.php header — _layout.php includes both shells,
 *   so the page renders body content only.
 *
 * Variables consumed (provided by HubController::tiers):
 *   $tiers  array  — tier metadata from MODULES_REGISTRY.yaml.tiers; map keyed by
 *                    tier id with label_he, short_he, color, description_he.
 *
 * Shell variables set:
 *   $page_title = 'מה זה SFA'
 *   $page_sub   = 'איך הכלים מסודרים'
 *   $active     = 'home'
 *   $back_url   = '/'
 */
use SFA\Lib\Template;

$h = [Template::class, 'h'];

// Display order — open → beta → coming → paid → custom.
$tier_order = ['open', 'beta', 'coming', 'paid', 'custom'];

// Page-side fallback copy if the YAML registry is missing description_he for a
// given tier. The YAML SSoT remains the registry; this is a safety net only.
$fallback_copy = [
    'open'   => 'הכלים הפתוחים — לכולם, ללא הרשמה. ספר גידולים, מחירון, מחשבון.',
    'beta'   => 'בטא — בפיתוח פעיל. משוב במייל / וואטסאפ.',
    'coming' => 'בקרוב — מתוכנן, לא זמין עדיין.',
    'paid'   => 'כלים מתקדמים — מנהל לקוחות, מעקב יבול. למודל מנוי.',
    'custom' => 'בדיוק לחווה שלך — חיבור Tend, יומן שדה, אינטגרציות. דברו איתנו.',
];

$tiers_in = is_array($tiers ?? null) ? $tiers : [];

$page_title = 'מה זה SFA';
$page_sub   = 'איך הכלים מסודרים';
$active     = 'home';
$back_url   = '/';

ob_start();
?>
<div class="hub-tiers-intro">
  <h2 class="gj-h2">איך SFA בנוי</h2>
  <p class="gj-lede">חמש שכבות של כלים — מהקהילתי הפתוח ועד לבדיוק-בשבילך.</p>
</div>
<ul class="hub-tier-list">
  <?php foreach ($tier_order as $tier_key):
      $entry  = $tiers_in[$tier_key] ?? [];
      $copy   = (string)($entry['description_he'] ?? $fallback_copy[$tier_key] ?? '');
  ?>
    <li class="hub-tier-row">
      <?php
        $tier = $tier_key;
        $size = 'lg';
        include __DIR__ . '/../macros/tier_badge.php';
      ?>
      <p class="hub-tier-row__desc"><?= $h($copy) ?>
        <?php if ($tier_key === 'custom'): ?>
          <a href="https://wa.me/972547776770?text=<?= rawurlencode('בדיוק לחווה שלי — דברו איתי') ?>">דברו איתנו</a>.
        <?php endif; ?>
      </p>
    </li>
  <?php endforeach; ?>
</ul>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title', 'page_sub', 'active', 'back_url'));
