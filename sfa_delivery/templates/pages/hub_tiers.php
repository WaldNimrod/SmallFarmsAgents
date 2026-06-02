<?php
/**
 * hub_tiers.php — Route /about — Class B v2
 *
 * WP-CB-UI-CLASSB — Board-B frame `about-tiers`.
 * Components: .tier-hero (§41), .tier-list, .tier-row (+--leaf/sun/paper/soil/tomato).
 *
 * Data contract (HubController::tiers):
 *   $tiers — MODULES_REGISTRY.yaml.tiers (keyed by tier id)
 */
use SFA\Lib\Template;

$h = [Template::class, 'h'];

// Display order — open → beta → coming → paid → custom
$tier_order = ['open', 'beta', 'coming', 'paid', 'custom'];

// Color modifiers per tier
$tier_colors = [
    'open'   => 'leaf',
    'beta'   => 'sun',
    'coming' => 'paper',
    'paid'   => 'soil',
    'custom' => 'tomato',
];

// Tier examples
$tier_examples = [
    'open'   => ['title' => 'ספר גידולים', 'sub' => 'מחירון שוק'],
    'beta'   => ['title' => 'מחשבון שדה', 'sub' => 'ניסיוני'],
    'coming' => ['title' => 'יומן שדה', 'sub' => 'בפיתוח'],
    'paid'   => ['title' => 'מנהל לקוחות', 'sub' => 'מנוי'],
    'custom' => ['title' => 'חיבור Tend', 'sub' => 'בדיוק לחווה'],
];

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

ob_start();
?>
<div style="max-width:800px;margin:0 auto;padding:20px clamp(16px,3vw,28px)">

  <div class="tier-hero">
    <h1>חמש שכבות של כלים</h1>
    <p>מהקהילתי הפתוח ועד לבדיוק-בשבילך — כל שכבה בנויה על הקודמת. רוב הכלים חינמיים לגמרי.</p>
  </div>

  <div class="tier-list">
    <?php foreach ($tier_order as $tier_key):
      $entry  = $tiers_in[$tier_key] ?? [];
      $color  = $tier_colors[$tier_key] ?? 'leaf';
      $copy   = (string)($entry['description_he'] ?? $fallback_copy[$tier_key] ?? '');
      $label  = (string)($entry['label_he'] ?? $tier_key);
      $eg     = $tier_examples[$tier_key] ?? [];
    ?>
    <div class="tier-row tier-row--<?= $h($color) ?>">
      <div class="tier-row__badge">
        <?php $tier = $tier_key; $size = 'lg'; include __DIR__ . '/../macros/tier_badge.php'; ?>
        <span class="tier-row__badge-en en"><?= strtoupper($tier_key) ?></span>
      </div>
      <div class="tier-row__txt">
        <h3><?= $h($label) ?></h3>
        <p><?= $h($copy) ?>
          <?php if ($tier_key === 'custom'): ?>
            <a href="https://wa.me/972547776770?text=<?= rawurlencode('בדיוק לחווה שלי — דברו איתי') ?>">דברו איתנו ←</a>
          <?php endif; ?>
        </p>
      </div>
      <?php if (!empty($eg)): ?>
      <div class="tier-row__eg">
        <b><?= $h($eg['title']) ?></b>
        <?= $h($eg['sub']) ?>
      </div>
      <?php endif; ?>
    </div>
    <?php endforeach; ?>
  </div>

  <div style="margin-top:28px;text-align:center;font-size:13.5px;color:var(--gj-ink-soft)">
    שאלות? <a href="/community" style="color:var(--gj-leaf-deep);font-weight:700">דברו עם הקהילה</a>
    או <a href="https://wa.me/972547776770" target="_blank" rel="noopener" style="color:var(--gj-leaf-deep);font-weight:700">בוואטסאפ</a>.
  </div>

</div>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title', 'page_sub', 'active'));
