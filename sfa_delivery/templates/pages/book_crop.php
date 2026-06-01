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
    if ($state === 'UNVALIDATED') {
        $conf = isset($field['confidence_score']) ? round((float)$field['confidence_score'] * 100) . '%' : '';
        $tip  = 'מקור: ' . $fn((string)($field['winning_source_class'] ?? '')) . ($conf !== '' ? ' · ביטחון ' . $conf : '');
        return '<span class="tip">' . $fn((string)$value) . ($unit ? '<small> ' . $fn($unit) . '</small>' : '') . '<span class="ast" title="' . $fn($tip) . '">*</span><span class="tip__pop"><b>ערך לא מאומת</b>' . $fn($tip) . '</span></span>';
    }
    return '<span class="pv-validated">' . $fn((string)$value) . ($unit ? '<small> ' . $fn($unit) . '</small>' : '') . '</span>';
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
  <section class="crophero">
    <div class="crophero__art"><?= $art_html_v1 ?></div>
    <div>
      <div class="crophero__bc">
        <a href="/crop-book/">ספר גידולים</a>
        <?php if ($family): ?> › <a href="/crop-book/family/"><?= $h((string)($family['name_he'] ?? '')) ?></a><?php endif; ?>
        › <strong><?= $h($name_he) ?></strong>
      </div>
      <h1><?= $h($name_he) ?></h1>
      <?php if ($name_lat !== ''): ?>
        <p class="crophero__sci"><em><?= $h($name_lat) ?></em></p>
      <?php endif; ?>
    </div>
    <div class="crophero__state">
      <span class="statebadge <?= $state_class ?>">
        <span class="d"></span><?= $state_label ?>
      </span>
    </div>
  </section>

  <?php
  $active_depth = $depth;
  $scope_id = 'depth-content';
  include __DIR__ . '/../macros/depth_tabs.php';
  ?>

  <div id="depth-content">

    <!-- ── SIMPLE depth ── -->
    <div data-depth-view="simple"<?= $depth !== 'simple' ? ' style="display:none"' : '' ?>>
      <!-- Headline values -->
      <div class="headvals">
        <?php
        $hv_fields = [
            ['key'=>'days_to_maturity', 'label'=>'ימים להבשלה', 'unit'=>'ימ׳'],
            ['key'=>'yield_per_bed_m',  'label'=>'יבול / מ׳',    'unit'=>'ק״ג'],
            ['key'=>'spacing_in_row_cm','label'=>'מרווח',         'unit'=>'ס״מ'],
            ['key'=>'price_documented', 'label'=>'מחיר',          'unit'=>'₪'],
        ];
        foreach ($hv_fields as $hvf):
        ?>
        <div class="hv">
          <div class="hv__lbl" data-field="<?= $h($hvf['key']) ?>"><?= $h($hvf['label']) ?></div>
          <div class="hv__val"><?= $pv($hvf['key']) ?></div>
        </div>
        <?php endforeach; ?>
      </div>

      <!-- Topic summary grid -->
      <div class="tsum">
        <div class="tcard tcard--nursery">
          <div class="tcard__head"><span class="tcard__ic">🌱</span><span class="tcard__t">זריעה/שתילה</span></div>
          <div class="tcard__rows">
            <div class="tcard__row"><span class="k">שיטה</span><span class="v"><?= $pv('planting_method') ?></span></div>
            <div class="tcard__row"><span class="k">במשתלה</span><span class="v"><?= $pv('days_in_nursery') ?><small> ימ׳</small></span></div>
          </div>
        </div>
        <div class="tcard tcard--grow">
          <div class="tcard__head"><span class="tcard__ic">📏</span><span class="tcard__t">מרווח ופריסה</span></div>
          <div class="tcard__rows">
            <div class="tcard__row"><span class="k">שורות</span><span class="v"><?= $pv('rows_per_bed') ?></span></div>
            <div class="tcard__row"><span class="k">מרווח בשורה</span><span class="v"><?= $pv('spacing_in_row_cm') ?><small> ס״מ</small></span></div>
          </div>
        </div>
        <div class="tcard tcard--harvest">
          <div class="tcard__head"><span class="tcard__ic">🌡</span><span class="tcard__t">אקלים</span></div>
          <div class="tcard__rows">
            <div class="tcard__row"><span class="k">עמידות קרה</span><span class="v"><?= $pv('frost_tolerance_class') ?></span></div>
          </div>
        </div>
        <div class="tcard tcard--yield">
          <div class="tcard__head"><span class="tcard__ic">📅</span><span class="tcard__t">רצף</span></div>
          <div class="tcard__rows">
            <div class="tcard__row"><span class="k">מרווח רצף</span><span class="v"><?= $pv('succession_interval_weeks') ?><small> שבועות</small></span></div>
          </div>
        </div>
      </div>

      <!-- Yield calculator button -->
      <div class="calcbtns mt12">
        <?php
        $yieldField = $cb1_fields['yield_per_bed_m'] ?? ['field_state'=>'MISSING'];
        $yieldState = strtoupper((string)($yieldField['field_state'] ?? 'MISSING'));
        $yieldDisabled = ($yieldState === 'MISSING') ? ' is-disabled' : '';
        ?>
        <button class="calcbtn<?= $yieldDisabled ?>"
          type="button"
          <?= $yieldDisabled === '' ? 'data-calc-open="modal-calc-yield"' : '' ?>
        >
          <span class="calcbtn__no">8</span>
          מחשבון יבול
          <span class="calcbtn__arrow"><?= $yieldDisabled ? '🔒' : '↗' ?></span>
        </button>
      </div>

      <!-- Rotation hint -->
      <?php if ($family_name_he !== ''):
        $family_lat = (string)($family['slug'] ?? '');
        include __DIR__ . '/../macros/rotation_hint.php';
      endif; ?>
    </div>

    <!-- ── FULL depth ── -->
    <div data-depth-view="full"<?= $depth !== 'full' ? ' style="display:none"' : '' ?>>
      <?php
      // 13-topic taxonomy organized display
      $topics = [
        ['key'=>'varieties',  'icon'=>'🌿', 'label'=>'זנים',            'class'=>'grow',    'fields'=>[]],
        ['key'=>'spacing',    'icon'=>'📏', 'label'=>'מרווח ופריסה',    'class'=>'grow',    'fields'=>['spacing_in_row_cm','rows_per_bed']],
        ['key'=>'equipment',  'icon'=>'⚙',  'label'=>'ציוד וכיוונון',   'class'=>'grow',    'fields'=>[]],
        ['key'=>'soil',       'icon'=>'🪱', 'label'=>'קרקע ודישון',     'class'=>'inputs',  'fields'=>['nutrient_removal_n_kg_per_ha']],
        ['key'=>'bedprep',    'icon'=>'🌾', 'label'=>'הכנת ערוגה',      'class'=>'grow',    'fields'=>[]],
        ['key'=>'sowing',     'icon'=>'🌱', 'label'=>'זריעה/שתילה',     'class'=>'nursery', 'fields'=>['planting_method','days_in_nursery','seeds_per_g','sowing_months']],
        ['key'=>'irrigation', 'icon'=>'💧', 'label'=>'השקיה',            'class'=>'grow',    'fields'=>['irrigation_type','root_depth_class']],
        ['key'=>'care',       'icon'=>'✋', 'label'=>'טיפוח ועישוב',    'class'=>'grow',    'fields'=>[]],
        ['key'=>'pest',       'icon'=>'🐛', 'label'=>'מזיקים ומחלות',   'class'=>'pest',    'fields'=>[]],
        ['key'=>'harvest',    'icon'=>'🥬', 'label'=>'קציר',             'class'=>'harvest', 'fields'=>['days_to_maturity','harvest_window_max_days']],
        ['key'=>'storage',    'icon'=>'❄',  'label'=>'שטיפה ואחסון',    'class'=>'harvest', 'fields'=>[]],
        ['key'=>'succession', 'icon'=>'🔁', 'label'=>'רצף וחברה',       'class'=>'yield',   'fields'=>['succession_interval_weeks','frost_tolerance_class']],
        ['key'=>'yield_inc',  'icon'=>'💰', 'label'=>'יבול/הכנסה',      'class'=>'yield',   'fields'=>['yield_per_bed_m','price_documented']],
      ];
      foreach ($topics as $topic):
        if (empty($topic['fields'])) continue; // skip topics with no fields mapped yet
      ?>
      <div class="topic topic--<?= $h($topic['class']) ?>">
        <div class="topic__head">
          <span class="topic__ic"><?= $topic['icon'] ?></span>
          <div class="topic__t"><?= $h($topic['label']) ?></div>
          <span class="topic__chev">▾</span>
        </div>
        <div class="topic__body">
          <dl class="fieldgrid">
            <?php foreach ($topic['fields'] as $fn):
              [$lbl_he,] = \SFA\Lib\FieldRegistry::label($fn);
              $isProposed = \SFA\Lib\FieldRegistry::isProposed($fn);
            ?>
            <div class="fg">
              <dt data-field="<?= $h($fn) ?>"><?= $h($lbl_he) ?>
                <?php if ($isProposed): ?><span class="proposed-tag">מוצע</span><?php endif; ?>
              </dt>
              <dd>
                <?php if ($isProposed): ?>
                  <span class="proposed-tag">טרם הוגדר</span>
                <?php elseif ($fn === 'sowing_months'):
                  $months = $cb1_fields['sowing_months']['value_best'] ?? null;
                  echo $monthChips($months);
                else:
                  echo $pv($fn);
                endif; ?>
              </dd>
            </div>
            <?php endforeach; ?>
          </dl>
        </div>
      </div>
      <?php endforeach; ?>
    </div>

    <!-- ── DRILL depth ── -->
    <div data-depth-view="drill"<?= $depth !== 'drill' ? ' style="display:none"' : '' ?>>
      <div class="cb-block">
        <h3>השוואת זנים</h3>
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
                  <?php if ($isDefault): ?><span class="star">★</span><?php endif; ?>
                </span></td>
                <td><?= $h((string)($agro['days_to_maturity'] ?? ($v['dtm_days'] ?? '—'))) ?></td>
                <td><?= $h((string)($agro['in_row_spacing_cm'] ?? ($agro['spacing_in_row_cm'] ?? '—'))) ?></td>
                <td><?= $h((string)($agro['avg_yield_per_bed_m'] ?? ($agro['yield_per_bed_m'] ?? '—'))) ?></td>
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

      <!-- Provenance table for key fields -->
      <div class="cb-block">
        <h3>מקורות — ימים להבשלה</h3>
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

  <!-- ── Hero (legacy) ───────────────────────────────────────────── -->
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
