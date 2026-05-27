<?php
/**
 * hub_home.php — Hub home page (route: /)
 *
 * Mandate §3 contract: emits .gj-shell + .gj-header__row + .gj-mark + .gj-title +
 *   .gj-sub + .gj-body + .gj-foot + .gj-foot__dot (all provided by shell/mobile.php
 *   via _layout.php), plus per-module .mod-card + .mod-card--{color} +
 *   .mod-card--{tier} + .tier + .tier--{color} + .tier__glyph (emitted by
 *   macros/module_card.php → macros/tier_badge.php).
 *
 * Architecture note (deviation from mandate § "include shell/mobile.php"):
 *   This codebase renders pages via Template::render('_layout', compact($content)).
 *   _layout.php includes BOTH shell/mobile.php AND shell/desktop.php — visibility
 *   swap is pure CSS (≥900px). Therefore the page itself does NOT include shells;
 *   it produces the body content only. Same convention as every other page in
 *   templates/pages/*.php (R1 build, verified pre-write).
 *
 * Variables consumed (provided by HubController::home):
 *   $modules  array  — list of module dicts from MODULES_REGISTRY.yaml.modules
 *                      (8 entries; each has id, name_he, sub, tier, color, stat,
 *                      route, icon)
 *   $tiers    array  — tier metadata (label_he, color, description_he per tier key)
 *
 * Shell variables set:
 *   $page_title   = 'SFA'
 *   $page_sub     = 'חקלאות קטנה'
 *   $active       = 'home'        — drives desktop sidebar highlight
 *   $stats        = ['crop_count' => …, 'product_count' => …]  (best-effort
 *                   derived from $modules[].stat_count when available)
 *
 * Module-registry → module_card field mapping (YAML keys → macro keys):
 *   id          → slug
 *   name_he     → name_he   (identity)
 *   tier        → tier      (identity)
 *   color       → tier_color
 *   sub         → sub_he
 *   stat        → stat_he
 *   route       → href
 *   icon        → icon_id (prefixed with "icon-" + fallback for unknown sprites)
 */
use SFA\Lib\Template;

$h = [Template::class, 'h'];

// Sprite ids defined by B7 in public_assets/img/icons.svg:
// icon-leaf, icon-seedling, icon-tomato, icon-lettuce, icon-cucumber,
// icon-pepper, icon-eggplant, icon-carrot, icon-onion, icon-zucchini.
// Map YAML icon keys to existing sprite ids; unknown keys fall back to icon-leaf.
$icon_sprite_map = [
    'tomato'     => 'icon-tomato',
    'lettuce'    => 'icon-lettuce',
    'cucumber'   => 'icon-cucumber',
    'carrot'     => 'icon-carrot',
    'pepper'     => 'icon-pepper',
    'onion'      => 'icon-onion',
    'basil'      => 'icon-leaf',
    'strawberry' => 'icon-tomato',
    'eggplant'   => 'icon-eggplant',
    'zucchini'   => 'icon-zucchini',
    'seedling'   => 'icon-seedling',
    'leaf'       => 'icon-leaf',
];

$modules_in = is_array($modules ?? null) ? $modules : [];

// Derive lightweight stats for the desktop sidebar from the module registry.
$crop_count    = 0;
$product_count = 0;
foreach ($modules_in as $m) {
    if (($m['id'] ?? '') === 'crop-book') {
        $crop_count = (int)($m['stat_count'] ?? 0);
    }
    if (($m['id'] ?? '') === 'market') {
        $product_count = (int)($m['stat_count'] ?? 0);
    }
}

$page_title = 'SFA';
$page_sub   = 'חקלאות קטנה';
$active     = 'home';
$stats      = [
    'crop_count'    => $crop_count,
    'product_count' => $product_count,
];

ob_start();
?>
<section class="mod-grid" aria-label="כלי SFA">
  <?php foreach ($modules_in as $m):
      $icon_key = (string)($m['icon'] ?? '');
      $icon_id  = $icon_sprite_map[$icon_key] ?? 'icon-leaf';
      $module = [
          'slug'       => (string)($m['id']      ?? ''),
          'name_he'    => (string)($m['name_he'] ?? ''),
          'tier'       => (string)($m['tier']    ?? 'open'),
          'tier_color' => (string)($m['color']   ?? 'leaf'),
          'sub_he'     => (string)($m['sub']     ?? ''),
          'stat_he'    => (string)($m['stat']    ?? ''),
          // Strip legacy /sfa/ URL prefix (MODULES_REGISTRY.yaml predates subdomain split — DECISION_SFA-S003-P003)
          // + remap /book/ → /crop-book/ (LOD400 LV-S-2: canonical URL contract is /crop-book/*)
          'href'       => str_replace('/book/', '/crop-book/', preg_replace('#^/sfa/#', '/', (string)($m['route'] ?? '#'))),
          'icon_id'    => $icon_id,
      ];
      include __DIR__ . '/../macros/module_card.php';
  endforeach; ?>
</section>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title', 'page_sub', 'active', 'stats'));
