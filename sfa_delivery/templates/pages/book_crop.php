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

use SFA\Lib\FieldRegistry;

$crop = $crop ?? [];

$page_title = (string)($crop['name_he'] ?? 'גידול');
$page_sub   = (string)($crop['name_lat'] ?? ($crop['en_name'] ?? ($crop['scientific_name'] ?? '')));
$active     = 'crop-book';
$back_url   = '/crop-book/';

// WP-CB-1 data (passed by controller; safe defaults for backward-compat)
$depth            = (string)($depth            ?? 'simple');
$cb1_fields       = is_array($cb1_fields       ?? null) ? $cb1_fields       : [];
$attributes       = is_array($attributes       ?? null) ? $attributes       : [];
$is_complete      = (bool)($is_complete        ?? false);
$wc_art           = $wc_art                    ?? null;
$family_name_he   = (string)($family_name_he   ?? '');
$assumptions_reg  = is_array($assumptions      ?? null) ? $assumptions      : [];
// WP-CB-MOBILE Stage 2 (Deep depth) — safe defaults for backward-compat with
// partial renders (e.g. CropCardIconTest) that don't pass these controller vars.
$variety_ranges   = is_array($variety_ranges   ?? null) ? $variety_ranges   : [];
$source_classes   = is_array($source_classes   ?? null) ? $source_classes   : [];
$variety_count    = (int)($variety_count       ?? (is_array($crop['varieties'] ?? null) ? count($crop['varieties']) : 0));

// Helper: render prov_value inline without Template::partial dependency
$pv = function(string $field_name) use ($cb1_fields, $h, $crop): string {
    $field = $cb1_fields[$field_name] ?? ['value_best'=>null,'field_state'=>'MISSING','field_name'=>$field_name,'unit'=>''];
    $state = strtoupper((string)($field['field_state'] ?? 'MISSING'));
    $value = $field['value_best'] ?? null;
    $unit  = (string)($field['unit'] ?? '');
    $slug  = (string)($crop['slug'] ?? '');
    $fn    = $h;
    if ($state === 'PROPOSED') {
        return '<span class="proposed-tag">מוצע</span>';
    }
    if ($state === 'MISSING' || $value === null || $value === '') {
        $ri = '<a class="reqinfo" href="#" data-field="' . $fn($field_name) . '" data-crop="' . $fn($slug) . '">◐ בקשו נתון</a>';
        return '<span class="val--missing">—</span> ' . $ri;
    }
    // WI-1: apply number formatting for numeric fields; WI-2: map unit token to Hebrew.
    // For numeric values, fmtNumber() formats them; for enum/text, enumLabel() translates.
    if (is_numeric($value)) {
        $display  = \SFA\Lib\FieldRegistry::fmtNumber($value, $unit);
        $unit_he  = \SFA\Lib\FieldRegistry::unitLabel($unit);
    } else {
        // Translate enum values to Hebrew before display (V02 fix).
        $display  = \SFA\Lib\FieldRegistry::enumLabel($field_name, (string)$value);
        $unit_he  = \SFA\Lib\FieldRegistry::unitLabel($unit);
    }
    $unit_html = ($unit_he !== '') ? '<small> ' . $fn($unit_he) . '</small>' : '';
    if ($state === 'UNVALIDATED') {
        $conf = isset($field['confidence_score']) ? round((float)$field['confidence_score'] * 100) . '%' : '';
        $tip  = 'מקור: ' . $fn((string)($field['winning_source_class'] ?? '')) . ($conf !== '' ? ' · ביטחון ' . $conf : '');
        return '<span class="tip">' . $fn($display) . $unit_html . '<span class="ast" title="' . $fn($tip) . '">*</span><span class="tip__pop"><b>ערך לא מאומת</b>' . $fn($tip) . '</span></span>';
    }
    return '<span class="pv-validated">' . $fn($display) . $unit_html . '</span>';
};

// WP-CB-MOBILE Stage 2 — plain value (no reqinfo link / asterisk markup) for the
// Simple .ess strip + .keylist. Returns the formatted Hebrew value, or '—' when
// the field is missing/proposed. Numeric → fmtNumber; enum → enumLabel.
$pvPlain = function(string $field_name) use ($cb1_fields): string {
    $field = $cb1_fields[$field_name] ?? null;
    if ($field === null) { return '—'; }
    $state = strtoupper((string)($field['field_state'] ?? 'MISSING'));
    $value = $field['value_best'] ?? null;
    if ($state === 'PROPOSED' || $state === 'MISSING' || $value === null || $value === '' || $value === []) {
        return '—';
    }
    $unit = (string)($field['unit'] ?? '');
    if (is_numeric($value)) {
        return \SFA\Lib\FieldRegistry::fmtNumber($value, $unit);
    }
    return \SFA\Lib\FieldRegistry::enumLabel($field_name, (string)$value);
};

// Month chip helper (for sowing_months int[] array)
$monthChips = function($months) use ($h): string {
    static $mn = ['','ינ׳','פב׳','מר׳','אפ׳','מא׳','יו׳','יל׳','אוג','ספ׳','אוק','נו׳','דצ׳'];
    if (!is_array($months) || empty($months)) return '<span class="val--missing">—</span>';
    $out = '<div class="month-chips">';
    foreach ($months as $m) {
        $mi = (int)$m;
        if ($mi >= 1 && $mi <= 12) {
            $out .= '<span class="mchip">' . $h($mn[$mi]) . '</span>';
        }
    }
    return $out . '</div>';
};

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
// Stable copy of the public-notes array. Some payload macros (e.g. crop_storage.php)
// historically used a local $notes inside the shared include scope; capturing
// $public_notes here makes the general-notes filters below immune to any such clobber.
$public_notes = $notes;

// WP-CB-MOBILE dedup: the legacy in-page anchor nav ($sections + nav.cb-section-nav)
// and the standalone legacy `cb-section` / `cb-vars` body blocks were removed — the
// Simple/Full/Deep depth panels (#depth-content) are now the single source of the
// crop body. Calendar lives in Simple; the 17 enrichment fields in Full/Deep topics;
// varieties in the Deep .vtable; agronomy/harvest/storage/companions + general notes
// migrated into the Deep panel; the crop description into the .crophero lede.

ob_start();
?>
<div class="cb-crop-detail" data-crop-slug="<?= $h($slug) ?>">

  <!-- ══ WP-CB-1: Crop Hero + Depth Tabs ════════════════════════════ -->
  <?php
  $state_class = $is_complete ? 'statebadge--complete' : 'statebadge--partial';
  $state_label = $is_complete ? '✓ נתונים מלאים' : '! נתונים חלקיים';
  // Watercolor art or emoji fallback
  $art_html_v1 = '';
  if ($wc_art !== null) {
      $art_html_v1 = '<img src="/public_assets/img/crops/' . $h($wc_art) . '" alt="' . $h($name_he) . '" loading="lazy">';
  } else {
      // emoji fallback by crop category
      $emojis = ['tomato'=>'🍅','cucumber'=>'🥒','pepper'=>'🌶','zucchini'=>'🥬','lettuce'=>'🥬','carrot'=>'🥕','basil'=>'🌿'];
      $emoji  = $emojis[$icon_slug] ?? '🌱';
      $art_html_v1 = '<span class="veg" aria-hidden="true">' . $emoji . '</span>';
  }
  ?>
  <?php
  // WP-CB-MOBILE Stage 2 (FIX 2a' · depth control in the HEADER, not in-body).
  // Compact 3-way icon segmented control: פשוט ◔ · מלא ▤ · העמקה ⌖. The active
  // mode shows its Hebrew label (CSS: .sh__depths button.is-active span). Reuses
  // the same data-depths/data-depth hooks crop-book-v1.js wireDepths() drives, so
  // switching is client-side; ?depth= still server-renders the initial state.
  $depth_modes = [
      ['key'=>'simple', 'g'=>'◔', 'label'=>'פשוט'],
      ['key'=>'full',   'g'=>'▤', 'label'=>'מלא'],
      ['key'=>'deep',   'g'=>'⌖', 'label'=>'העמקה'],
  ];
  ?>
  <div class="cb-crop-toolbar">
    <div class="sh__depths" data-depths="depth-content" role="tablist" aria-label="עומק תצוגה">
      <?php foreach ($depth_modes as $dm): ?>
      <button type="button"
        data-depth="<?= $h($dm['key']) ?>"
        class="<?= $depth === $dm['key'] ? 'is-active' : '' ?>"
        role="tab"
        aria-selected="<?= $depth === $dm['key'] ? 'true' : 'false' ?>"
        title="<?= $h($dm['label']) ?>"
      ><span class="g" aria-hidden="true"><?= $dm['g'] ?></span><span><?= $h($dm['label']) ?></span></button>
      <?php endforeach; ?>
    </div>
  </div>

  <section class="crophero" id="identity">
    <div class="crophero__art"><?= $art_html_v1 ?></div>
    <div>
      <?php
      // Latin/family breadcrumb — forced LTR (Latin + variety count read L→R).
      $bc_bits = [];
      if ($name_lat !== '') { $bc_bits[] = $name_lat; }
      if ($family && ($family['name_he'] ?? '') !== '') { $bc_bits[] = (string)$family['name_he']; }
      if ($variety_count > 0) { $bc_bits[] = $variety_count . ' זנים'; }
      ?>
      <?php if (!empty($bc_bits)): ?>
      <div class="crophero__bc" dir="ltr" style="unicode-bidi:isolate"><?= $h(implode(' · ', $bc_bits)) ?></div>
      <?php endif; ?>
      <h1><span class="gj-underline"><?= $h($name_he) ?></span></h1>
      <?php if ($name_lat !== ''): ?>
        <p class="crophero__sci"><em><?= $h($name_lat) ?></em></p>
      <?php endif; ?>
      <?php /* WP-CB-MOBILE dedup: crop description migrated here from the
               removed .cb-crop-lede hero remnant, so it shows at all depths. */ ?>
      <?php if ($desc_he !== ''): ?>
        <p class="crophero__lede"><?= $h($desc_he) ?></p>
      <?php endif; ?>
    </div>
    <div class="crophero__state">
      <span class="statebadge <?= $state_class ?>">
        <span class="d"></span><?= $state_label ?>
      </span>
    </div>
  </section>

  <div id="depth-content">

    <!-- ── SIMPLE depth (gardener-focused, genuinely minimal) ──
         essentials strip → calendar → one key value per topic. NO full stat
         block / per-field dump (WP-CB-MOBILE §4 — Simple ⊂ Full ⊂ Deep). -->
    <div data-depth-view="simple"<?= $depth !== 'simple' ? ' style="display:none"' : '' ?>>
      <?php
      // Essentials a home gardener needs: spacing · DTM · water · method.
      // Built from the cparam icon vocabulary shared with the entry cards.
      $space_v  = $pvPlain('spacing_in_row_cm');
      $dtm_v    = $pvPlain('days_to_maturity');
      $method_v = $pvPlain('planting_method');
      $irr_v    = $pvPlain('irrigation_type');
      ?>
      <div class="ess">
        <span class="cparam cparam--space"><span class="g" aria-hidden="true">⇲</span><span class="num" dir="ltr"><?= $h($space_v) ?></span><small>מרווח ס״מ</small></span>
        <span class="cparam cparam--dtm"><span class="g" aria-hidden="true">⏳</span><span class="num" dir="ltr"><?= $h($dtm_v) ?></span><small>ימים לקטיף</small></span>
        <?php if ($irr_v !== '—'): ?>
        <span class="cparam cparam--water"><span class="g" aria-hidden="true">💧</span><?= $h($irr_v) ?><small>השקיה</small></span>
        <?php endif; ?>
        <?php if ($method_v !== '—'): ?>
        <span class="cparam cparam--method"><span class="g" aria-hidden="true">🌱</span><?= $h($method_v) ?></span>
        <?php endif; ?>
      </div>

      <!-- seasons → planting calendar (reuse the Stage-1 .pcal macro as-is) -->
      <?php if (!empty($calendar)): ?>
        <?php include __DIR__ . '/../macros/crop_calendar.php'; ?>
      <?php endif; ?>

      <!-- one key value per topic (no per-field dump) -->
      <h3 class="gj-h3">העיקר, לפי נושא</h3>
      <?php
      // Each row picks the single headline datum for its topic; '—' when absent.
      $key_rows = [
          ['ic'=>'🌱', 'color'=>'var(--t-nursery)', 'k'=>'משתלה', 'field'=>'days_in_nursery',          'unit'=>'ימ׳ במשתלה'],
          ['ic'=>'🌿', 'color'=>'var(--t-grow)',    'k'=>'גידול', 'field'=>'days_to_maturity',         'unit'=>'ימים להבשלה'],
          ['ic'=>'🧺', 'color'=>'var(--t-harvest)', 'k'=>'קציר',  'field'=>'harvest_window_max_days',   'unit'=>'ימי חלון קציר'],
          ['ic'=>'⚖', 'color'=>'var(--t-yield)',   'k'=>'יבול',  'field'=>'yield_per_bed_m',           'unit'=>'ק״ג/מ׳'],
      ];
      ?>
      <div class="keylist">
        <?php foreach ($key_rows as $kr):
          $kv = $pvPlain($kr['field']);
        ?>
        <div class="keyrow">
          <span class="ic" aria-hidden="true" style="background:<?= $kr['color'] ?>"><?= $kr['ic'] ?></span>
          <span class="k"><?= $h($kr['k']) ?></span>
          <span class="v"><?php if ($kv === '—'): ?><span class="val--missing">—</span><?php else: ?><span class="num" dir="ltr"><?= $h($kv) ?></span> <small><?= $h($kr['unit']) ?></small><?php endif; ?></span>
        </div>
        <?php endforeach; ?>
      </div>

      <p class="muted simple-more">רוצים את כל הנתונים? עברו ל<b>מלא</b> · להשוואת זנים ומקורות — <b>העמקה</b>.</p>

      <!-- Rotation hint -->
      <?php if ($family_name_he !== ''):
        $family_lat = (string)($family['slug'] ?? '');
        include __DIR__ . '/../macros/rotation_hint.php';
      endif; ?>
    </div>

    <?php
    // Shared 17-field topic taxonomy for Full + Deep (Simple ⊂ Full ⊂ Deep).
    // Fields (17): spacing_in_row_cm, rows_per_bed, nutrient_removal_n_kg_per_ha,
    // planting_method, days_in_nursery, seeds_per_g, sowing_months,
    // irrigation_type, root_depth_class, common_pests, foliar_feeding_program,
    // days_to_maturity, harvest_window_max_days, succession_interval_weeks,
    // frost_tolerance_class, yield_per_bed_m, price_documented.
    // Topic taxonomy MUST stay in strict parity (membership + order) with the
    // canon SSoT organic_market_agent/crop_book/canon/topics.py (13 topics,
    // AC-02 / test_crop_topics.py::test_php_parity). The 5 field-less topics
    // (varieties/equipment/bedprep/care/storage) are listed for canon parity but
    // skipped at render time by crop_topics.php (`if (empty($topic['fields']))`),
    // so no empty cards appear. `varieties` is surfaced via the Deep variety table.
    $topics = [
      ['key'=>'varieties',  'icon'=>'🌿', 'label'=>'זנים',            'class'=>'grow',    'fields'=>[]],
      ['key'=>'spacing',    'icon'=>'📏', 'label'=>'מרווח ופריסה',   'class'=>'grow',    'fields'=>['spacing_in_row_cm','rows_per_bed']],
      ['key'=>'equipment',  'icon'=>'⚙',  'label'=>'ציוד וכיוונון',   'class'=>'grow',    'fields'=>[]],
      ['key'=>'soil',       'icon'=>'🪱', 'label'=>'קרקע ודישון',    'class'=>'inputs',  'fields'=>['nutrient_removal_n_kg_per_ha']],
      ['key'=>'bedprep',    'icon'=>'🌾', 'label'=>'הכנת ערוגה',      'class'=>'grow',    'fields'=>[]],
      ['key'=>'sowing',     'icon'=>'🌱', 'label'=>'משתלה / שתילה',  'class'=>'nursery', 'fields'=>['planting_method','days_in_nursery','seeds_per_g','sowing_months']],
      ['key'=>'irrigation', 'icon'=>'💧', 'label'=>'השקיה ושורשים',  'class'=>'grow',    'fields'=>['irrigation_type','root_depth_class']],
      ['key'=>'care',       'icon'=>'✋', 'label'=>'טיפוח ועישוב',    'class'=>'grow',    'fields'=>[]],
      ['key'=>'pest',       'icon'=>'🐛', 'label'=>'מזיקים ומחלות',  'class'=>'pest',    'fields'=>['common_pests','foliar_feeding_program']],
      ['key'=>'harvest',    'icon'=>'🥬', 'label'=>'קציר',           'class'=>'harvest', 'fields'=>['days_to_maturity','harvest_window_max_days']],
      ['key'=>'storage',    'icon'=>'❄',  'label'=>'שטיפה ואחסון',    'class'=>'harvest', 'fields'=>[]],
      ['key'=>'succession', 'icon'=>'🔁', 'label'=>'רצף ועמידות',    'class'=>'yield',   'fields'=>['succession_interval_weeks','frost_tolerance_class']],
      ['key'=>'yield_inc',  'icon'=>'💰', 'label'=>'יבול והכנסה',    'class'=>'yield',   'fields'=>['yield_per_bed_m','price_documented']],
    ];
    ?>

    <!-- ── FULL depth (topic overview + every field by topic) ── -->
    <div data-depth-view="full"<?= $depth !== 'full' ? ' style="display:none"' : '' ?>>
      <!-- topic overview: one headline value per topic group -->
      <h3 class="gj-h3">סקירה לפי נושא</h3>
      <div class="tsum">
        <div class="tcard tcard--nursery">
          <div class="tcard__head"><span class="tcard__ic" aria-hidden="true">🌱</span><span class="tcard__t">משתלה</span></div>
          <div class="tcard__rows">
            <div class="tcard__row"><span class="k">שיטה</span><span class="v"><?= $pv('planting_method') ?></span></div>
            <div class="tcard__row"><span class="k">במשתלה</span><span class="v"><?= $pv('days_in_nursery') ?></span></div>
          </div>
        </div>
        <div class="tcard tcard--grow">
          <div class="tcard__head"><span class="tcard__ic" aria-hidden="true">🌿</span><span class="tcard__t">גידול</span></div>
          <div class="tcard__rows">
            <div class="tcard__row"><span class="k">מרווח בשורה</span><span class="v"><?= $pv('spacing_in_row_cm') ?></span></div>
            <div class="tcard__row"><span class="k">להבשלה</span><span class="v"><?= $pv('days_to_maturity') ?></span></div>
          </div>
        </div>
        <div class="tcard tcard--yield">
          <div class="tcard__head"><span class="tcard__ic" aria-hidden="true">⚖</span><span class="tcard__t">יבול</span></div>
          <div class="tcard__rows">
            <div class="tcard__row"><span class="k">ק״ג/מ׳</span><span class="v"><?= $pv('yield_per_bed_m') ?></span></div>
            <div class="tcard__row"><span class="k">מחיר</span><span class="v"><?= $pv('price_documented') ?></span></div>
          </div>
        </div>
      </div>

      <h3 class="gj-h3">כל הנתונים</h3>
      <?php
      $is_deep = false;
      include __DIR__ . '/../macros/crop_topics.php';
      ?>

      <?php
      // WP-CB-MOBILE dedup: general public notes migrated here from the removed
      // legacy `notes` section. crop_topics.php only surfaces pest_disease /
      // irrigation note types (in the pest topic), so the remaining public note
      // types (general/tip/warning/nutrition/…) would otherwise be lost. Render
      // them via the same crop_notes.php macro, scoped to the non-pest types.
      $general_notes = array_values(array_filter($public_notes, static function ($n) {
          return !in_array((string)($n['note_type'] ?? ''), ['pest_disease', 'irrigation'], true);
      }));
      if (!empty($general_notes)):
      ?>
      <h3 class="gj-h3">הערות</h3>
      <div class="cb-block">
        <?php
        // crop_notes.php reads $notes from include scope — swap in the filtered
        // general set for the render, then restore the page-level $notes (the
        // Deep panel's crop_topics.php still needs the full list for its pest topic).
        $notes_all = $notes; $notes = $general_notes;
        include __DIR__ . '/../macros/crop_notes.php';
        $notes = $public_notes;
        ?>
      </div>
      <?php endif; ?>
    </div>

    <!-- ── DEEP depth (Full topics + per-datum range + EX/PR/WR sources
         + variety comparison table + source-sheet topic) ── -->
    <div data-depth-view="deep"<?= $depth !== 'deep' ? ' style="display:none"' : '' ?>>
      <p class="gj-lede deep-lede">כמו «מלא» — אך לכל נתון נפתחים <b>הטווח בין הזנים</b> ו<b>המקורות</b>.</p>

      <?php
      $is_deep = true;
      include __DIR__ . '/../macros/crop_topics.php';
      ?>

      <div class="cb-block">
        <h3 class="gj-h3">השוואת זנים</h3>
        <?php if (empty($varieties)): ?>
          <p class="muted">אין זנים מתועדים לגידול זה.</p>
        <?php else: ?>
        <div class="vtable-wrap">
          <table class="vtable">
            <thead>
              <tr>
                <th>זן</th>
                <th>ימים להבשלה</th>
                <th>מרווח (ס״מ)</th>
                <th>יבול (ק״ג/מ׳)</th>
              </tr>
            </thead>
            <tbody>
              <?php foreach ($varieties as $v):
                $isDefault = !empty($v['is_default']);
                $agro = is_array($v['agronomy'] ?? null) ? $v['agronomy'] : [];
              ?>
              <tr class="<?= $isDefault ? 'v-default' : '' ?>">
                <td><span class="v-name"><?= $h((string)($v['name_he'] ?? ($v['name'] ?? ''))) ?>
                  <?php if ($isDefault): ?><span class="star" aria-hidden="true">★</span><?php endif; ?>
                </span></td>
                <?php
                  $_dtm  = $agro['days_to_maturity'] ?? ($v['dtm_days'] ?? null);
                  $_spc  = $agro['in_row_spacing_cm'] ?? ($agro['spacing_in_row_cm'] ?? null);
                  $_yld  = $agro['avg_yield_per_bed_m'] ?? ($agro['yield_per_bed_m'] ?? null);
                ?>
                <td class="num" dir="ltr"><?= $h($_dtm !== null ? \SFA\Lib\FieldRegistry::fmtNumber($_dtm, 'days') : '—') ?></td>
                <td class="num" dir="ltr"><?= $h($_spc !== null ? \SFA\Lib\FieldRegistry::fmtNumber($_spc) : '—') ?></td>
                <td class="num" dir="ltr"><?= $h($_yld !== null ? \SFA\Lib\FieldRegistry::fmtNumber($_yld) : '—') ?></td>
              </tr>
              <?php endforeach; ?>
            </tbody>
            <?php if (count($varieties) > 1): ?>
            <tfoot>
              <tr><td colspan="4"><span class="avg-lbl">ממוצע כל הזנים</span></td></tr>
            </tfoot>
            <?php endif; ?>
          </table>
        </div>
        <?php endif; ?>
      </div>

      <!-- Source-sheet topic: provenance for the key field (kept; honest data) -->
      <h3 class="gj-h3">מקורות — ימים להבשלה</h3>
      <div class="cb-block">
        <?php
        $prov_sources = [];
        if (!empty($enrichment['days_to_maturity'])) {
            $r = $enrichment['days_to_maturity'];
            $prov_sources[] = [
                'source_class' => strtoupper((string)($r['winning_source_class'] ?? 'WR')),
                'source_name'  => 'מקור ראשי',
                'value'        => (string)($r['value_best'] ?? '—'),
                'unit'         => 'ימים',
                'confidence_score' => (float)($r['confidence_score'] ?? 0.0),
                'is_winner'    => true,
            ];
        }
        $field_name = 'days_to_maturity';
        $label_he   = 'ימים להבשלה';
        $sources    = $prov_sources;
        include __DIR__ . '/../macros/prov_table.php';
        ?>
      </div>

      <!-- Source trust hierarchy (EX > PR > WR) — explains how the governing value is chosen -->
      <div class="emptybox srchier">
        <span class="emptybox__ic" aria-hidden="true">⛓</span>
        <div>
          <b>היררכיית מקורות</b>
          <p>EX (מומחה) · PR (מקצועי) · WR (רשת). הערך הקובע נבחר לפי דירוג אמון — EX קודם ל-PR, ו-PR קודם ל-WR.</p>
        </div>
      </div>

      <?php
      // WP-CB-MOBILE dedup: the payload-driven sections (agronomy rollup, harvest,
      // storage, companions) previously lived in standalone legacy `cb-section`
      // blocks below #depth-content. Their data ($crop['agronomy'|'harvest'|
      // 'storage'|'companions']) is NOT part of the $cb1_fields enrichment set the
      // depth topics render, so to avoid content loss they are migrated here into
      // Deep (the most-complete view). Each macro self-guards on empty, and each
      // block is gated on !empty() so no empty cards appear.
      ?>
      <?php if (!empty($agronomy)): ?>
      <div class="cb-block">
        <h3 class="gj-h3">אגרונומיה</h3>
        <?php include __DIR__ . '/../macros/crop_agronomy.php'; ?>
      </div>
      <?php endif; ?>

      <?php if (!empty($harvest)): ?>
      <div class="cb-block">
        <h3 class="gj-h3">קטיף ויבול</h3>
        <?php include __DIR__ . '/../macros/crop_harvest.php'; ?>
      </div>
      <?php endif; ?>

      <?php if (!empty($storage)): ?>
      <div class="cb-block">
        <h3 class="gj-h3">אחסון לאחר קטיף</h3>
        <?php include __DIR__ . '/../macros/crop_storage.php'; ?>
      </div>
      <?php endif; ?>

      <?php if (!empty($companions)): ?>
      <div class="cb-block">
        <h3 class="gj-h3">ליווי גידולים</h3>
        <?php include __DIR__ . '/../macros/crop_companions.php'; ?>
      </div>
      <?php endif; ?>

      <?php
      // General public notes (non-pest types) — also surfaced in Deep so the
      // deepest view is a superset of Full. Same swap technique as Full.
      $general_notes_deep = array_values(array_filter($public_notes, static function ($n) {
          return !in_array((string)($n['note_type'] ?? ''), ['pest_disease', 'irrigation'], true);
      }));
      if (!empty($general_notes_deep)):
      ?>
      <div class="cb-block">
        <h3 class="gj-h3">הערות</h3>
        <?php
        $notes_all = $notes; $notes = $general_notes_deep;
        include __DIR__ . '/../macros/crop_notes.php';
        $notes = $public_notes;
        ?>
      </div>
      <?php endif; ?>
    </div>

  </div><!-- #depth-content -->

  <!-- Calculator modal overlay (yield, #8) -->
  <?php
  $yf  = $cb1_fields['yield_per_bed_m'] ?? ['value_best'=>null,'field_state'=>'MISSING','field_name'=>'yield_per_bed_m','unit'=>'ק״ג/מ׳'];
  $yState = strtoupper((string)($yf['field_state'] ?? 'MISSING'));
  $yVal = (string)($yf['value_best'] ?? '');
  $yDisabled = ($yState === 'MISSING');
  $stdLen = (int)(($assumptions_reg['std_bed_length_m']['default'] ?? 30));
  $serverYield = $yDisabled ? '—' : (is_numeric($yVal) ? number_format((float)$yVal * $stdLen, 1) : '—');
  ?>
  <div class="calcmodal" id="modal-calc-yield">
    <div class="calcmodal__overlay" data-calc-close></div>
    <div class="calcmodal__card">
      <div class="calcmodal__head">
        <span class="gj-eyebrow">מחשבון 8</span>
        <span class="calcmodal__title">יבול צפוי</span>
        <button class="calcmodal__close" data-calc-close type="button" aria-label="סגור">✕</button>
      </div>
      <div class="calcmodal__body">
        <div class="cv<?= $yDisabled ? ' is-disabled' : '' ?>" data-calc="yield">
          <div class="cv__head">
            <span class="cv__no">8</span>
            <div class="cv__title">יבול צפוי<small>expected yield</small></div>
            <span class="tier tier--leaf cv__aud">● שני הקהלים</span>
          </div>
          <div class="cv__body">
            <?php if ($yDisabled): ?>
            <div class="cv__disabled">
              <span class="ic">🔒</span>
              <div><h5>חסר נתון: יבול למ׳</h5>
              <a class="reqinfo" href="#" data-field="yield_per_bed_m" data-crop="<?= $h($slug) ?>">◐ בקשו נתון</a></div>
            </div>
            <?php else: ?>
            <div class="cv__uses">ערכי ספר</div>
            <div class="bvrow">
              <span class="bv<?= $yState === 'UNVALIDATED' ? ' bv--ast' : '' ?>"
                    data-book="yield_per_m" data-val="<?= $h($yVal) ?>">
                <span data-field="yield_per_bed_m">יבול/מ׳</span>
                <b><?= $h($yVal) ?></b><small> ק״ג</small>
                <a class="bv__link" href="/crop-book/<?= $h($slug) ?>/?depth=full">↗ ספר</a>
                <?= $yState === 'UNVALIDATED' ? '<span class="ast" title="ערך לא מאומת">*</span>' : '' ?>
              </span>
            </div>
            <div class="cv__uses">קלט שלך</div>
            <div class="cv__inputs">
              <label class="ipt">
                <label>אורך ערוגה</label>
                <span class="ipt__box">
                  <input type="number" data-k="bed_len" value="<?= $h((string)$stdLen) ?>" min="1"/>
                  <span class="u">מ׳</span>
                </span>
              </label>
            </div>
            <div class="cv__result">
              <span class="lbl">יבול צפוי</span>
              <span class="big" data-result><?= $h($serverYield) ?> <small>ק״ג</small></span>
            </div>
            <div class="cv__formula" data-formula><?= $h($stdLen . ' m × ' . $yVal . ' kg/m') ?></div>
            <div data-extra></div>
            <?php endif; ?>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- ══ END WP-CB-1 ════════════════════════════════════════════════ -->

  <?php
  /* WP-CB-MOBILE dedup: the legacy .cb-crop-lede + .cb-crop-hero__meta hero
     remnants, the .cb-section-nav in-page anchor nav, and the standalone
     #identity-facts cb-section were removed. The crop description now renders in
     the .crophero lede; family/DTM in the hero breadcrumb; identity facts via the
     Full/Deep topic fields. Timeline + market crosslink (below) are NOT legacy
     duplicates and are preserved. */
  ?>

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

  <?php
  /* WP-CB-MOBILE dedup: the legacy standalone cb-section blocks (calendar,
     agronomy, harvest, storage, companions, notes) and the cb-vars variety grid
     were removed — they duplicated the depth panels. Their content now lives in
     #depth-content: calendar in Simple (.pcal); the enrichment fields in Full/Deep
     topics; varieties in the Deep .vtable (with full per-variety detail still on
     each variety page); agronomy/harvest/storage/companions + general public notes
     migrated into the Deep panel; the description into the .crophero lede. */
  ?>

  <?php
  $context          = 'book.' . $slug;
  $context_label_he = 'ספר · ' . $name_he;
  include __DIR__ . '/../macros/contrib_strip.php';
  ?>

  <!-- WP-CB-MOBILE Stage 2 — CTA foot (data-completion, primary/loud). -->
  <div class="cta">
    <div class="cta__card cta--data">
      <h3>מגדלים <?= $h($name_he) ?>? עזרו לדייק</h3>
      <p>ידע מהשטח משפר את הספר לכולם — תרמו נתון או ניסיון, וזה יידלק לכל המגדלים.</p>
      <a class="cta__btn" href="/community">◐ תרמו נתון ›</a>
    </div>
  </div>

</div><!-- /.cb-crop-detail -->
<?php
$content = ob_get_clean();
// Re-assert nav key: section macros are include'd into this scope inside the ob_*
// buffer above and could shadow page-level vars (e.g. crop_calendar's month loop).
// Guarantee _layout/nav receives the correct active section regardless.
$active = 'crop-book';
echo Template::render('_layout', compact('content', 'page_title', 'page_sub', 'active', 'back_url'));
