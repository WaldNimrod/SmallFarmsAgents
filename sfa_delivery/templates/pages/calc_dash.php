<?php
/**
 * calc_dash.php — Calculator page (/calc/) — WP-CB-MOBILE FIX 6 rebuild.
 *
 * "Define the question" builder. One scope (#calc-scope[data-calc-state]) with
 * two states: ASK (question builder) and RESULT (answer + session + export).
 *
 * Compute REUSES the existing client-side CALC registry in crop-book-v1.js
 * (window.SFA_CALC) — no math is duplicated here. The builder configures a
 * hidden [data-calc] engine panel, dispatches `input` to trigger the existing
 * recompute(), reads the rendered result, and surfaces it as .qb-answer +
 * .qb-break, accumulating each calculation into .qb-session (sessionStorage).
 *
 * Only 6 of the 14 calculators have client-side CALC math implemented
 * (seed/beds/yield/revenue/pop/fert). The other 8 are exposed in the builder
 * but flagged "בקרוב" (no fabricated result) — see CALC_GOALS data-soon below.
 *
 * Assumptions are edited via the EXISTING AssumptionField editor
 * (macros/assumption_field.php) — opened from .qb-assum (primary entry point).
 *
 * Export = the WHOLE session: the session rows are posted to the existing
 * /calc/print + /calc/export.csv endpoints as rows[label]=value (HubController
 * already accepts arbitrary rows[] pairs).
 *
 * Variables from controller:
 *   $crop_list         array  — [{slug, name_he}]
 *   $crop_book_values  array  — {slug: {field_name: value_best}}
 *
 * @see _COMMUNICATION/team_35/.../design_files/surface-calc.html
 * @see _COMMUNICATION/team_100/.../LOD400_team10_mobile-build_2026-06-05_v1.0.0.md §3 row 5
 */
use SFA\Lib\Template;
use SFA\Controllers\AssumptionsController;

$h = [Template::class, 'h'];

$page_title = 'מחשבון';
$page_sub   = 'תכנון גידולים · הגדרת השאלה';
$active     = 'calc';
$back_url   = '/';

$assumptions = AssumptionsController::getAssumptions();

// V03: crop list for the picker + book values for JS calc binding.
$crop_list        = is_array($crop_list        ?? null) ? $crop_list        : [];
$crop_book_values = is_array($crop_book_values ?? null) ? $crop_book_values : [];
// WP-CB-CALC: categorical (text) book values — separate channel from the numeric SFA_CROP_BOOK
// (the JS numeric flatten drops non-numerics). Carries planting_method + frost_tolerance_class.
$crop_book_text   = is_array($crop_book_text   ?? null) ? $crop_book_text   : [];

/**
 * Goal catalog — the 14 calculators mapped to the existing CALC[kind] registry.
 * `kind` !== '' && not `soon` => computes live via window.SFA_CALC[kind].
 * `soon` => UI exposes it (catalog completeness) but no client math exists yet;
 *           the builder shows a "בקרוב" notice instead of fabricating a number.
 *
 *  primary[] renders as the 6 .qb-goal--grid buttons.
 *  more[]    renders as the .qb-more <select> (the other 8).
 */
// WP-CB-CALC: 'shape' = result render type (per team_35 mockup mapping); 'anchor' = date-engine input.
// 'soon'=>false ⇒ the client has live math for this goal (scalar via CALC[kind]; date via SFA_DATEC).
$CALC_GOALS = [
    // id, key, label, icon, kind, soon, basis, rlabel, runit, shape, anchor
    'seed'        => ['id'=>1,  'label'=>'זרעים לקנות',   'ic'=>'🌱', 'kind'=>'seed',    'soon'=>false, 'basis'=>'area',     'rlabel'=>'כמות לקנייה',  'runit'=>'גרם',        'shape'=>'scalar', 'anchor'=>''],
    'sow_date'    => ['id'=>4,  'label'=>'תאריך זריעה',   'ic'=>'📅', 'kind'=>'sow_date','soon'=>false, 'basis'=>'area',     'rlabel'=>'תאריך זריעה',  'runit'=>'',          'shape'=>'date',   'anchor'=>'target'],
    'yield'       => ['id'=>8,  'label'=>'יבול צפוי',     'ic'=>'⚖', 'kind'=>'yield',   'soon'=>false, 'basis'=>'area',     'rlabel'=>'יבול צפוי',    'runit'=>'ק״ג',       'shape'=>'scalar', 'anchor'=>''],
    'revenue'     => ['id'=>9,  'label'=>'הכנסה צפויה',   'ic'=>'₪', 'kind'=>'revenue', 'soon'=>false, 'basis'=>'area',     'rlabel'=>'הכנסה צפויה',  'runit'=>'₪',         'shape'=>'scalar', 'anchor'=>''],
    'transplants' => ['id'=>2,  'label'=>'כמות שתילים',   'ic'=>'🪴', 'kind'=>'transplants','soon'=>false, 'basis'=>'area',  'rlabel'=>'כמות שתילים',  'runit'=>'שתילים',    'shape'=>'scalar', 'anchor'=>''],
    'pop'         => ['id'=>10, 'label'=>'צפיפות שתילה',  'ic'=>'▦', 'kind'=>'pop',     'soon'=>false, 'basis'=>'area',     'rlabel'=>'צפיפות',       'runit'=>'צמ׳/מ״ר',   'shape'=>'scalar', 'anchor'=>''],
    // ── dropdown (9) ──
    'harvest'     => ['id'=>5,  'label'=>'חלון קטיף',     'ic'=>'🧺', 'kind'=>'harvest', 'soon'=>false, 'basis'=>'area',     'rlabel'=>'חלון קטיף',    'runit'=>'',          'shape'=>'range',  'anchor'=>'sow'],
    'frost'       => ['id'=>11, 'label'=>'חלון קרה',      'ic'=>'❄', 'kind'=>'',        'soon'=>true,  'basis'=>'area',     'rlabel'=>'חלון שתילה',   'runit'=>'',          'shape'=>'range',  'anchor'=>'region'],
    'fert'        => ['id'=>12, 'label'=>'כמות דישון',    'ic'=>'🪱', 'kind'=>'fert',    'soon'=>false, 'basis'=>'area',     'rlabel'=>'קומפוסט',      'runit'=>'ק״ג קומפוסט','shape'=>'scalar', 'anchor'=>''],
    'water'       => ['id'=>0,  'label'=>'צריכת מים',     'ic'=>'💧', 'kind'=>'',        'soon'=>true,  'basis'=>'area',     'rlabel'=>'צריכת מים',    'runit'=>'',          'shape'=>'nodata', 'anchor'=>''],
    'profit'      => ['id'=>13, 'label'=>'השוואת גידולים','ic'=>'📊', 'kind'=>'',        'soon'=>true,  'basis'=>'beds',     'rlabel'=>'השוואה',       'runit'=>'ק״ג/מ׳',    'shape'=>'rank',   'anchor'=>''],
    'beds'        => ['id'=>7,  'label'=>'ערוגות ליעד',   'ic'=>'▤', 'kind'=>'beds',    'soon'=>false, 'basis'=>'target',   'rlabel'=>'ערוגות נדרשות', 'runit'=>'ערוגות',   'shape'=>'scalar', 'anchor'=>''],
    'seed_cost'   => ['id'=>14, 'label'=>'עלות זרעים',    'ic'=>'🧾', 'kind'=>'seed_cost','soon'=>false, 'basis'=>'area',     'rlabel'=>'עלות זרעים',   'runit'=>'₪',         'shape'=>'scalar', 'anchor'=>''],
    'succession'  => ['id'=>6,  'label'=>'רצף גידולים',   'ic'=>'🔁', 'kind'=>'succession','soon'=>false, 'basis'=>'area',     'rlabel'=>'לוח רצף',      'runit'=>'',          'shape'=>'list',   'anchor'=>'sow'],
    'nursery'     => ['id'=>3,  'label'=>'ימי משתלה',     'ic'=>'🌿', 'kind'=>'',        'soon'=>true,  'basis'=>'seedlings','rlabel'=>'מגשי משתלה',   'runit'=>'',          'shape'=>'scalardate','anchor'=>'fieldset'],
];
$primary_keys = ['seed', 'sow_date', 'yield', 'revenue', 'transplants', 'pop'];
$more_keys    = ['harvest', 'frost', 'fert', 'water', 'profit', 'beds', 'seed_cost', 'succession', 'nursery'];

$default_goal = 'seed';
$default_goal_def = $CALC_GOALS[$default_goal];

// Assumptions surfaced on the result (germination % + safety margin / oversow).
$germPct  = (string)round((float)($assumptions['germination_rate']['default'] ?? 0.90) * 100);
$oversow  = (float)($assumptions['oversow']['default'] ?? 1.10);
$oversowPct = '+' . (string)round(($oversow - 1) * 100) . '%';

ob_start();
?>
<div class="sh__body" id="calc-scope" data-calc-state="ask"
     data-calc-goals='<?= $h(json_encode(array_map(static function ($k, $g) {
        return [
            'key'   => $k,
            'label' => $g['label'],
            'kind'  => $g['kind'],
            'soon'  => (bool)$g['soon'],
            'basis' => $g['basis'],
            'rlabel'=> $g['rlabel'],
            'runit' => $g['runit'],
            'shape' => $g['shape'] ?? 'scalar',
            'anchor'=> $g['anchor'] ?? '',
        ];
     }, array_keys($CALC_GOALS), $CALC_GOALS), JSON_UNESCAPED_UNICODE | JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT)) ?>'>
  <h1 class="gj-h1" style="font-size:23px">מחשבון התכנון</h1>

  <!-- ░░ ASK ░░ -->
  <div class="qb-ask">
    <div class="qb-intro">
      <span class="qb-intro__ic">🧮</span>
      <div>
        <h2>מה נחשב היום?</h2>
        <p>בוחרים <b style="color:var(--gj-code-deep)">מה</b> רוצים לדעת ו<b style="color:var(--gj-code-deep)">לפי מה</b>, ולוחצים «חשב». אפשר לחשב כמה דברים — הסשן שומר הכול.</p>
      </div>
    </div>

    <div class="qb">
      <!-- Step 1 — what to calculate -->
      <div class="qb__step">
        <div class="qb__steplbl"><span class="qb__stepno">1</span><h3>מה תרצו לחשב?</h3><span class="opt">15 מטרות</span></div>
        <div class="qb-goal qb-goal--grid" id="qb-goal">
          <?php foreach ($primary_keys as $gk): $g = $CALC_GOALS[$gk]; ?>
          <button type="button" data-goal="<?= $h($gk) ?>"<?= $gk === $default_goal ? ' class="is-on"' : '' ?>>
            <span class="g"><?= $h($g['ic']) ?></span><?= $h($g['label']) ?>
          </button>
          <?php endforeach; ?>
        </div>
        <div class="qb-more">
          <select aria-label="עוד מחשבונים" id="qb-more">
            <option value="">עוד מחשבונים… (9)</option>
            <?php foreach ($more_keys as $gk): $g = $CALC_GOALS[$gk]; ?>
            <option value="<?= $h($gk) ?>"><?= $h($g['label']) ?></option>
            <?php endforeach; ?>
          </select>
        </div>
      </div>

      <!-- Step 2 — crop -->
      <div class="qb__step">
        <div class="qb__steplbl"><span class="qb__stepno">2</span><h3>עבור איזה גידול?</h3></div>
        <label class="ipt" style="max-width:240px">
          <label>גידול</label>
          <span class="ipt__box">
            <select data-k="crop_slug" aria-label="בחר גידול" id="qb-crop">
              <option value="">בחר גידול…</option>
              <?php foreach ($crop_list as $crop_opt): ?>
              <option value="<?= $h((string)($crop_opt['slug'] ?? '')) ?>"><?= $h((string)($crop_opt['name_he'] ?? '')) ?></option>
              <?php endforeach; ?>
            </select>
          </span>
        </label>
      </div>

      <!-- Step 3 — basis -->
      <div class="qb__step">
        <div class="qb__steplbl"><span class="qb__stepno">3</span><h3>לפי מה לחשב כמות?</h3><span class="opt">בחירה</span></div>
        <div class="qb-basis" id="qb-basis">
          <button type="button" data-basis="area" class="is-on">לפי שטח</button>
          <button type="button" data-basis="beds">מס׳ ערוגות</button>
          <button type="button" data-basis="seedlings">מס׳ שתילים</button>
        </div>
        <div class="qb-row" id="qb-basis-row">
          <!-- basis input — swapped by JS per the chosen basis -->
          <label class="ipt" data-basis-input="area">
            <label>שטח לגידול</label>
            <span class="ipt__box"><input type="number" data-k="area" value="30" min="1"/><span class="u">מ׳</span></span>
          </label>
          <label class="ipt" data-basis-input="beds" style="display:none">
            <label>מספר ערוגות</label>
            <span class="ipt__box"><input type="number" data-k="num_beds" value="10" min="1"/><span class="u">ערוגות</span></span>
          </label>
          <label class="ipt" data-basis-input="seedlings" style="display:none">
            <label>מספר שתילים</label>
            <span class="ipt__box"><input type="number" data-k="num_seedlings" value="100" min="1"/><span class="u">שתילים</span></span>
          </label>
          <!-- target-kg input — only for the "beds for target yield" goal -->
          <label class="ipt" data-basis-input="target" style="display:none">
            <label>יעד יבול</label>
            <span class="ipt__box"><input type="number" data-k="target_kg" value="100" min="1"/><span class="u">ק״ג</span></span>
          </label>
        </div>
      </div>

      <!-- Step 4 — time anchor (optional) -->
      <div class="qb__step">
        <div class="qb__steplbl"><span class="qb__stepno">4</span><h3>עוגן זמן</h3><span class="opt">רשות</span></div>
        <div class="qb-basis" id="qb-anchor">
          <button type="button" data-anchor="target" class="is-on">תאריך יעד</button>
          <button type="button" data-anchor="sow">תאריך זריעה</button>
          <button type="button" data-anchor="now">עכשיו</button>
        </div>
        <div class="qb-row" id="qb-anchor-row">
          <label class="ipt" data-anchor-input="target">
            <label>תאריך יעד לקטיף</label>
            <span class="ipt__box"><input type="date" data-k="target_date"/><span class="u">📅</span></span>
          </label>
          <label class="ipt" data-anchor-input="sow" style="display:none">
            <label>תאריך זריעה</label>
            <span class="ipt__box"><input type="date" data-k="sow_date"/><span class="u">📅</span></span>
          </label>
        </div>
      </div>

      <!-- goal-specific extra inputs — shown by JS per the chosen goal (data-goal-input) -->
      <div class="qb-row" id="qb-goal-inputs">
        <label class="ipt" data-goal-input="succession" style="display:none">
          <label>מספר מחזורי זריעה</label>
          <span class="ipt__box"><input type="number" data-k="succ_count" value="5" min="1" max="60"/><span class="u">מחזורים</span></span>
        </label>
        <span data-goal-input="seed_cost" style="display:none">
          <label class="ipt" style="max-width:170px">
            <label>מחיר זרעים</label>
            <span class="ipt__box"><input type="number" data-k="seed_price_per_g" step="0.01" min="0" placeholder="0.15"/><span class="u">₪/גרם</span></span>
          </label>
          <span class="u" style="align-self:center">או</span>
          <label class="ipt" style="max-width:160px">
            <label>מחיר חבילה</label>
            <span class="ipt__box"><input type="number" data-k="pack_price" step="0.5" min="0" placeholder="מחיר"/><span class="u">₪</span></span>
          </label>
          <label class="ipt" style="max-width:150px">
            <label>גרם בחבילה</label>
            <span class="ipt__box"><input type="number" data-k="grams_per_pack" step="0.5" min="0" placeholder="גרם"/><span class="u">גרם</span></span>
          </label>
        </span>
      </div>

      <div class="qb__echo" id="qb-echo">השאלה שלך: אחשב <b><?= $h($default_goal_def['label']) ?></b> עבור <b>—</b>, לפי <b>שטח</b>.</div>
      <button class="qb__go" type="button" id="qb-go">חשב ›</button>
    </div>
  </div>

  <!-- ░░ RESULT ░░ -->
  <div class="qb-result">
    <div class="qb-result__head">
      <button class="qb-result__back" type="button" id="qb-back">‹ שאלה חדשה</button>
      <span class="qb-result__q" id="qb-result-q"></span>
    </div>

    <!-- session — accumulated, saved (sessionStorage, per-device for v1) -->
    <div class="qb-session" id="qb-session" hidden>
      <div class="qb-session__head">
        <span>💾</span><h4>תוצאות הסשן</h4>
        <span class="badge" id="qb-session-badge">0 חישובים · נשמר</span>
      </div>
      <div id="qb-session-rows"></div>
    </div>

    <!-- a soon/unavailable goal renders this notice instead of a fabricated number -->
    <div class="qb-soon" id="qb-soon" hidden style="border:1px solid color-mix(in oklch, var(--gj-sun) 28%, var(--gj-paper));background:color-mix(in oklch, var(--gj-sun) 9%, var(--gj-paper));border-radius:var(--gj-r-l);padding:16px;margin-bottom:12px">
      <b style="font-family:var(--gj-font-head);font-size:15px;display:block;margin-bottom:4px">מחשבון זה בפיתוח</b>
      <p style="font-size:13px;color:var(--gj-ink-soft);margin:0 0 10px;line-height:1.5">המחשבון <span id="qb-soon-name"></span> ידלק כשנתוני הספר הדרושים יושלמו. נשמח שתבקשו אותו.</p>
      <a class="qb-assum__edit" href="https://wa.me/972547776770?text=בקשת+מחשבון+SFA" target="_blank" rel="noopener" style="display:inline-block;text-decoration:none">← בקשו מחשבון זה</a>
    </div>

    <div class="qb-answer" id="qb-answer">
      <div class="qb-answer__lbl" id="qb-answer-lbl">תוצאה</div>
      <div class="qb-answer__big" id="qb-answer-big">—</div>
    </div>

    <div class="qb-break" id="qb-break"><!-- breakdown rows injected by JS --></div>

    <!-- editable base assumptions — opens the EXISTING AssumptionField editor -->
    <div class="qb-assum">
      <span class="ic">◇</span>
      <div class="qb-assum__txt">
        <b>הנחות יסוד בשימוש</b>
        <span>נביטה <?= $h($germPct) ?>% · ביטחון <?= $h($oversowPct) ?> — ניתן לדייק</span>
      </div>
      <button class="qb-assum__edit" type="button" id="qb-assum-edit" aria-expanded="false" aria-controls="qb-assum-editor">✎ ערוך הנחות</button>
    </div>

    <!-- AssumptionField editors (the EXISTING macro) — toggled open by .qb-assum__edit -->
    <div class="cb-block" id="qb-assum-editor" hidden style="margin-bottom:12px">
      <h3>הנחות תכנון</h3>
      <?php
      $assumption_keys_to_show = ['germination_rate', 'oversow', 'bed_width', 'std_bed_length_m', 'compost_N_pct', 'application_efficiency'];
      foreach ($assumption_keys_to_show as $akey):
          $assump        = $assumptions[$akey] ?? [];
          $key           = $akey;
          $assumption    = $assump;
          $display_value = (string)($assump['default'] ?? '');
          $display_unit  = (string)($assump['unit']    ?? '');
          if ($display_unit === 'fraction') { $display_value = (string)round((float)$display_value * 100); $display_unit = '%'; $data_scale = 0.01; }
          else { $data_scale = 1; }
          include __DIR__ . '/../macros/assumption_field.php';
      endforeach;
      ?>
    </div>

    <!-- export = WHOLE session -->
    <div class="calc-export" style="margin:0">
      <h4>הורדת כל הסשן</h4>
      <p>כל החישובים יחד — קובץ אחד לשיתוף או הדפסה.</p>
      <div class="calc-export__btns" style="grid-template-columns:1fr 1fr">
        <a class="calc-export__btn" id="qb-export-pdf" href="/calc/print" target="_blank" rel="noopener">⤓ PDF · הסשן</a>
        <a class="calc-export__btn calc-export__btn--ghost" id="qb-export-csv" href="/calc/export.csv">⤓ CSV · הסשן</a>
      </div>
    </div>
  </div>

  <!-- ── Hidden compute engine: reuses the EXISTING CALC[kind] recompute().
       The builder writes data-calc + [data-k]/[data-book] here, dispatches
       `input`, then reads [data-result]. No math is duplicated. ── -->
  <div id="qb-engine" data-calc="" style="display:none" aria-hidden="true">
    <span class="bv" data-book="spacing" data-val="0"></span>
    <span class="bv" data-book="rows" data-val="0"></span>
    <span class="bv" data-book="seeds_per_gram" data-val="0"></span>
    <span class="bv" data-book="yield_per_m" data-val="0"></span>
    <span class="bv" data-book="price" data-val="0"></span>
    <span class="bv" data-book="n" data-val="0"></span>
    <span class="bv" data-book="p" data-val="0"></span>
    <span class="bv" data-book="k" data-val="0"></span>
    <input type="hidden" data-k="bed_len" value="30"/>
    <input type="hidden" data-k="seeds_per_hole" value="1"/>
    <input type="hidden" data-k="target_kg" value="100"/>
    <input type="hidden" data-k="area" value="300"/>
    <input type="hidden" data-k="area_m2" value="300"/>
    <input type="hidden" data-k="seed_price_per_g" value=""/>
    <input type="hidden" data-k="pack_price" value=""/>
    <input type="hidden" data-k="grams_per_pack" value=""/>
    <span data-result></span><span data-formula></span><span data-extra></span>
  </div>
</div>

<?php if (!empty($crop_book_values)): ?>
<script>
window.SFA_CROP_BOOK = <?= json_encode($crop_book_values, JSON_UNESCAPED_UNICODE | JSON_HEX_TAG | JSON_HEX_AMP) ?>;
</script>
<?php endif; ?>
<?php if (!empty($crop_book_text)): ?>
<script>
window.SFA_CROP_BOOK_TXT = <?= json_encode($crop_book_text, JSON_UNESCAPED_UNICODE | JSON_HEX_TAG | JSON_HEX_AMP) ?>;
</script>
<?php endif; ?>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title', 'page_sub', 'active', 'back_url'));
