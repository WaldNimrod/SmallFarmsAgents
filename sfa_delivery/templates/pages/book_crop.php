<?php
/**
 * book_crop.php — Route /crop-book/{slug} (CB5 / D4)
 *
 * Mandate §3 (route 10): `.gj-shell` + `.crop-detail__head` `.crop-detail__h1`
 *   `.crop-detail__sci` `.crop-vars__list` `.crop-vars__row` (per variety).
 *
 * Per LOD400 v1.0.3 §0.5: COMPONENTS.md class names verbatim — `.cb-crop-hero`
 *   / `.cb-var` BEM family is the SSoT. Mapping documented in BUILD_REPORT §7.
 *
 * SECURITY: knowledge_notes filtered through is_internal_farm_use_only=TRUE
 *   (data_layer_inventory §E.5) — internal notes MUST NOT render on public site.
 *
 * Variables expected from controller:
 *   $crop array — keys:
 *     'slug', 'name_he', 'name_lat' (or 'scientific_name' fallback), 'en_name' (optional),
 *     'icon_slug' (sprite id without `icon-` prefix; defaults to 'leaf'),
 *     'description_he' (lede),
 *     'family' (optional ['slug','name_he']),
 *     'timeline' (optional ['prep_pct','grow_pct','harv_pct','harv_days','week_labels'?]),
 *     'market_link' (optional ['slug','price_current','source_count']),
 *     'varieties' (array — items conform to variety_row macro contract),
 *     'knowledge_notes' (optional array — each ['title_he','text_he','kind'?,'source_label_he'?,'is_internal_farm_use_only'?])
 */
use SFA\Lib\Template;
$h = [Template::class, 'h'];

$crop = $crop ?? [];

$page_title = (string)($crop['name_he'] ?? 'גידול');
$page_sub   = (string)($crop['name_lat'] ?? ($crop['en_name'] ?? ($crop['scientific_name'] ?? '')));
$active     = 'crop-book';
$back_url   = '/crop-book/';

$slug      = (string)($crop['slug']      ?? '');
$icon_slug = (string)($crop['icon_slug'] ?? 'leaf');
$name_he   = (string)($crop['name_he']   ?? '');
$name_lat  = (string)($crop['name_lat']  ?? ($crop['scientific_name'] ?? ''));
$desc_he   = (string)($crop['description_he'] ?? '');
$family    = is_array($crop['family'] ?? null) ? $crop['family'] : null;
$varieties = is_array($crop['varieties'] ?? null) ? $crop['varieties'] : [];

ob_start();
?>
<section class="cb-crop-hero">
  <nav class="cb-crop-hero__breadcrumb">
    <a href="/crop-book/">ספר גידולים</a><span>›</span>
    <?php if ($family): ?>
      <a href="/crop-book/family/<?= $h((string)($family['slug'] ?? '')) ?>"><?= $h((string)($family['name_he'] ?? '')) ?></a><span>›</span>
    <?php endif; ?>
    <strong><?= $h($name_he) ?></strong>
  </nav>

  <div class="cb-crop-hero__head">
    <span class="cb-crop-hero__icon" aria-hidden="true">
      <svg viewBox="0 0 24 24"><use href="#icon-<?= $h($icon_slug) ?>"></use></svg>
    </span>
    <div>
      <h1 class="cb-crop-hero__h"><?= $h($name_he) ?></h1>
      <?php if ($name_lat !== ''): ?>
        <p class="cb-crop-hero__sci"><em><?= $h($name_lat) ?></em></p>
      <?php endif; ?>
    </div>
  </div>

  <?php if ($desc_he !== ''): ?>
    <p class="cb-crop-hero__lede"><?= $h($desc_he) ?></p>
  <?php endif; ?>

  <?php if (!empty($crop['family_tag_he']) || !empty($crop['dtm_days'])): ?>
    <div class="cb-crop-hero__meta">
      <?php if (!empty($crop['family_tag_he'])): ?>
        <span class="pill pill--soil"><?= $h((string)$crop['family_tag_he']) ?></span>
      <?php endif; ?>
      <?php
        $dtm = $crop['dtm_days'] ?? null;
        if ($dtm !== null && $dtm !== '' && (int)$dtm !== -32768): ?>
        <span class="pill pill--muted"><?= (int)$dtm ?> ימים</span>
      <?php endif; ?>
    </div>
  <?php endif; ?>
</section>

<?php
// Timeline — only render when controller supplies the segment percentages.
if (!empty($crop['timeline']) && is_array($crop['timeline'])):
    $prep_pct    = (float)($crop['timeline']['prep_pct'] ?? 0);
    $grow_pct    = (float)($crop['timeline']['grow_pct'] ?? 0);
    $harv_pct    = (float)($crop['timeline']['harv_pct'] ?? 0);
    $harv_days   = (int)  ($crop['timeline']['harv_days'] ?? 0);
    $week_labels = isset($crop['timeline']['week_labels']) && is_array($crop['timeline']['week_labels'])
                   ? $crop['timeline']['week_labels'] : [];
    include __DIR__ . '/../macros/timeline_bar.php';
endif;
?>

<?php
// Cross-link to market — only when a matching pricebook product exists.
if (!empty($crop['market_link']) && is_array($crop['market_link'])):
    $ml = $crop['market_link'];
    $href       = '/market/' . (string)($ml['slug'] ?? '');
    $art_html   = '<svg viewBox="0 0 24 24" aria-hidden="true"><use href="#icon-' . htmlspecialchars($icon_slug, ENT_QUOTES, 'UTF-8') . '"></use></svg>';
    $big_text   = number_format((float)($ml['price_current'] ?? 0), 2);
    $small_unit = '₪/ק״ג';
    $sub_text   = 'מחיר שוק נוכחי · ' . (int)($ml['source_count'] ?? 0) . ' מקורות';
    $direction  = 'book-to-market';
    include __DIR__ . '/../macros/crosslink.php';
endif;
?>

<section class="cb-vars">
  <div class="cb-vars-head">
    <h3>זנים <small>(<?= (int)count($varieties) ?>)</small></h3>
  </div>
  <?php if (empty($varieties)): ?>
    <p class="cb-qhint">אין עדיין זנים מתועדים לגידול זה.</p>
  <?php else: ?>
    <div class="cb-vars__list">
      <?php foreach ($varieties as $variety):
        $crop_slug = $slug;
        include __DIR__ . '/../macros/variety_row.php';
      endforeach; ?>
    </div>
  <?php endif; ?>
</section>

<?php
// Knowledge notes — MANDATORY filter on is_internal_farm_use_only.
// Public site MUST NEVER render internal-only notes (data inventory §E.5 licensing hard-gate).
if (!empty($crop['knowledge_notes']) && is_array($crop['knowledge_notes'])):
    $public_notes = array_values(array_filter(
        $crop['knowledge_notes'],
        fn ($n) => is_array($n) && empty($n['is_internal_farm_use_only'])
    ));
    if (!empty($public_notes)): ?>
        <section class="cb-notes">
          <h2 class="cb-notes__h">הערות ידע</h2>
          <?php foreach ($public_notes as $note):
              $kind = (string)($note['kind'] ?? 'general');
              ?>
              <article class="cb-note cb-note--<?= $h($kind) ?>">
                <h4 class="cb-note__h"><?= $h((string)($note['title_he'] ?? '')) ?></h4>
                <p class="cb-note__body"><?= $h((string)($note['text_he'] ?? '')) ?></p>
                <?php if (!empty($note['source_label_he'])): ?>
                  <small class="cb-note__src">— <?= $h((string)$note['source_label_he']) ?></small>
                <?php endif; ?>
              </article>
          <?php endforeach; ?>
        </section>
    <?php endif;
endif; ?>

<?php
$context          = 'book.' . $slug;
$context_label_he = 'ספר · ' . $name_he;
include __DIR__ . '/../macros/contrib_strip.php';
?>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title', 'page_sub', 'active', 'back_url'));
