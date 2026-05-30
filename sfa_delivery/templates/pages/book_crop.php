<?php
/**
 * book_crop.php — Route /crop-book/{slug}
 *
 * WP-UI-patch04: Full-width central panel (AC-U4-08), species-first section order (AC-U4-03),
 * all rich payload sections surfaced (AC-U4-04), varieties LAST.
 *
 * Section order:
 *   (1) Hero + Identity
 *   (2) Planting calendar
 *   (3) Agronomy (crop-level rollup)
 *   (4) Harvest & yield
 *   (5) Storage
 *   (6) Companions
 *   (7) Notes (public only — empty-state when none)
 *   (8) Varieties (patch03 grid) — LAST
 *
 * SECURITY: knowledge notes / notes array filtered to public-only before
 *   reaching this template. Internal notes MUST NEVER render (AC-U4-05).
 *
 * Variables from controller:
 *   $crop     — full merged array (payload_json merged in)
 *   $varieties — variety rows with agronomy + agro_delta (patch03)
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
$icon_url  = (string)($crop['icon_url']  ?? '');
$name_he   = (string)($crop['name_he']   ?? '');
$name_lat  = (string)($crop['name_lat']  ?? ($crop['scientific_name'] ?? ''));
$desc_he   = (string)($crop['description_he'] ?? '');
$family    = is_array($crop['family'] ?? null) ? $crop['family'] : null;
$varieties = is_array($crop['varieties'] ?? null) ? $crop['varieties'] : [];

// Payload sections — each may be absent / empty.
$identity   = is_array($crop['identity']   ?? null) ? $crop['identity']   : [];
$calendar   = is_array($crop['calendar']   ?? null) ? $crop['calendar']   : [];
$agronomy   = is_array($crop['agronomy']   ?? null) ? $crop['agronomy']   : [];
$harvest    = is_array($crop['harvest']    ?? null) ? $crop['harvest']    : [];
$storage    = is_array($crop['storage']    ?? null) ? $crop['storage']    : [];
$companions = is_array($crop['companions'] ?? null) ? $crop['companions'] : [];

// Notes — public-only (AC-U4-05: internal notes MUST NOT render).
// Controller may supply either 'notes' (new payload key) or 'knowledge_notes' (legacy key).
$raw_notes = $crop['notes'] ?? ($crop['knowledge_notes'] ?? []);
$raw_notes = is_array($raw_notes) ? $raw_notes : [];
// Strict public-only filter — remove any note with is_internal_farm_use_only truthy.
// Maps legacy knowledge_notes shape ({title_he,text_he,kind,is_internal_farm_use_only})
// and new payload shape ({note_type, body_text, trust_tier}) into a normalised array.
$notes = [];
foreach ($raw_notes as $n) {
    if (!is_array($n)) continue;
    if (!empty($n['is_internal_farm_use_only'])) continue; // hard-gate internal notes
    // Normalise to new payload shape if it looks like a legacy knowledge_notes entry.
    if (!isset($n['body_text']) && isset($n['text_he'])) {
        $n['body_text']  = (string)$n['text_he'];
        $n['note_type']  = (string)($n['kind'] ?? 'general');
        $n['trust_tier'] = '';
    }
    $notes[] = $n;
}

// Build section anchors list for the sticky in-page nav.
// Only include sections that have data.
$sections = [];
$sections[] = ['id' => 'identity',  'label' => 'מינים'];
if (!empty($calendar))   $sections[] = ['id' => 'calendar',   'label' => 'לוח שנה'];
if (!empty($agronomy))   $sections[] = ['id' => 'agronomy',   'label' => 'אגרונומיה'];
if (!empty($harvest))    $sections[] = ['id' => 'harvest',    'label' => 'קטיף ויבול'];
if (!empty($storage))    $sections[] = ['id' => 'storage',    'label' => 'אחסון'];
if (!empty($companions)) $sections[] = ['id' => 'companions', 'label' => 'ליווי גידולים'];
$sections[] = ['id' => 'notes',     'label' => 'הערות'];
if (!empty($varieties))  $sections[] = ['id' => 'varieties',  'label' => 'זנים (' . count($varieties) . ')'];

ob_start();
?>
<div class="cb-crop-detail">

  <!-- ── Hero ───────────────────────────────────────────────────── -->
  <section class="cb-crop-hero" id="identity">
    <nav class="cb-crop-hero__breadcrumb" aria-label="נתיב ניווט">
      <a href="/crop-book/">ספר גידולים</a><span aria-hidden="true">›</span>
      <?php if ($family): ?>
        <a href="/crop-book/family/<?= $h((string)($family['slug'] ?? '')) ?>"><?= $h((string)($family['name_he'] ?? '')) ?></a><span aria-hidden="true">›</span>
      <?php endif; ?>
      <strong><?= $h($name_he) ?></strong>
    </nav>

    <div class="cb-crop-hero__head">
      <?php if ($icon_url !== ''): ?>
        <img class="crop-card__art cb-crop-hero__art" src="<?= $h($icon_url) ?>"
             loading="lazy" decoding="async"
             alt="<?= $h($name_he) ?>">
      <?php else: ?>
        <span class="cb-crop-hero__icon" aria-hidden="true">
          <svg viewBox="0 0 24 24"><use href="#icon-<?= $h($icon_slug) ?>"></use></svg>
        </span>
      <?php endif; ?>
      <div>
        <h1 class="cb-crop-hero__h"><?= $h($name_he) ?></h1>
        <?php if ($name_lat !== ''): ?>
          <p class="cb-crop-hero__sci"><em><?= $h($name_lat) ?></em></p>
        <?php endif; ?>
      </div>
    </div>

    <?php /* Always emit lede hook for deterministic grep. */ ?>
    <p class="cb-crop-hero__lede">
      <?php if ($desc_he !== ''): ?>
        <?= $h($desc_he) ?>
      <?php else: ?>
        <span class="muted">תיאור הגידול יתווסף בקרוב.</span>
      <?php endif; ?>
    </p>

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

  <!-- ── Sticky in-page section anchor nav ─────────────────────── -->
  <?php if (count($sections) > 1): ?>
  <nav class="cb-section-nav" aria-label="מקטעים בדף">
    <ul class="cb-section-nav__list" role="list">
      <?php foreach ($sections as $sec): ?>
        <li class="cb-section-nav__item">
          <a class="cb-section-nav__link" href="#<?= $h($sec['id']) ?>"><?= $h($sec['label']) ?></a>
        </li>
      <?php endforeach; ?>
    </ul>
  </nav>
  <?php endif; ?>

  <!-- ── Identity facts ─────────────────────────────────────────── -->
  <?php
  // Show identity section when there is at least one metadata field beyond the hero.
  $has_identity = !empty($identity) || !empty($crop['category']) || !empty($crop['growth_cycle']) || $family !== null;
  if ($has_identity):
  ?>
  <section class="cb-section" id="identity-facts">
    <div class="cb-section__head">
      <h2 class="cb-section__title">פרטי הגידול</h2>
    </div>
    <div class="cb-section__body">
      <?php include __DIR__ . '/../macros/crop_identity.php'; ?>
    </div>
  </section>
  <?php endif; ?>

  <!-- ── Timeline (optional, patch03 carry-over) ───────────────── -->
  <?php
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

  <!-- ── Cross-link to market ──────────────────────────────────── -->
  <?php
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

  <!-- ── (2) Planting calendar ──────────────────────────────────── -->
  <?php if (!empty($calendar)): ?>
  <section class="cb-section" id="calendar">
    <div class="cb-section__head">
      <h2 class="cb-section__title">לוח שנה לזריעה ושתילה</h2>
    </div>
    <div class="cb-section__body">
      <?php include __DIR__ . '/../macros/crop_calendar.php'; ?>
    </div>
  </section>
  <?php endif; ?>

  <!-- ── (3) Agronomy ───────────────────────────────────────────── -->
  <?php if (!empty($agronomy)): ?>
  <section class="cb-section" id="agronomy">
    <div class="cb-section__head">
      <h2 class="cb-section__title">אגרונומיה</h2>
    </div>
    <div class="cb-section__body">
      <?php include __DIR__ . '/../macros/crop_agronomy.php'; ?>
    </div>
  </section>
  <?php endif; ?>

  <!-- ── (4) Harvest & yield ────────────────────────────────────── -->
  <?php if (!empty($harvest)): ?>
  <section class="cb-section" id="harvest">
    <div class="cb-section__head">
      <h2 class="cb-section__title">קטיף ויבול</h2>
    </div>
    <div class="cb-section__body">
      <?php include __DIR__ . '/../macros/crop_harvest.php'; ?>
    </div>
  </section>
  <?php endif; ?>

  <!-- ── (5) Storage ────────────────────────────────────────────── -->
  <?php if (!empty($storage)): ?>
  <section class="cb-section" id="storage">
    <div class="cb-section__head">
      <h2 class="cb-section__title">אחסון לאחר קטיף</h2>
    </div>
    <div class="cb-section__body">
      <?php include __DIR__ . '/../macros/crop_storage.php'; ?>
    </div>
  </section>
  <?php endif; ?>

  <!-- ── (6) Companions ─────────────────────────────────────────── -->
  <?php if (!empty($companions)): ?>
  <section class="cb-section" id="companions">
    <div class="cb-section__head">
      <h2 class="cb-section__title">ליווי גידולים</h2>
    </div>
    <div class="cb-section__body">
      <?php include __DIR__ . '/../macros/crop_companions.php'; ?>
    </div>
  </section>
  <?php endif; ?>

  <!-- ── (7) Notes (always rendered; empty-state when no public notes) ── -->
  <section class="cb-section" id="notes">
    <div class="cb-section__head">
      <h2 class="cb-section__title">הערות</h2>
    </div>
    <div class="cb-section__body">
      <?php include __DIR__ . '/../macros/crop_notes.php'; ?>
    </div>
  </section>

  <!-- ── (8) Varieties — LAST ───────────────────────────────────── -->
  <section class="cb-vars" id="varieties">
    <div class="cb-vars-head">
      <h2 class="cb-section__title">זנים <small>(<?= (int)count($varieties) ?>)</small></h2>
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
  $context          = 'book.' . $slug;
  $context_label_he = 'ספר · ' . $name_he;
  include __DIR__ . '/../macros/contrib_strip.php';
  ?>

</div><!-- /.cb-crop-detail -->
<?php
$content = ob_get_clean();
// Re-assert nav key: section macros are include'd into this scope inside the ob_*
// buffer above and could shadow page-level vars (e.g. crop_calendar's month loop).
// Guarantee _layout/nav receives the correct active section regardless.
$active = 'crop-book';
echo Template::render('_layout', compact('content', 'page_title', 'page_sub', 'active', 'back_url'));
