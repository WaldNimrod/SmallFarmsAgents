<?php
/**
 * calc_dash.php — Calculator dashboard (/calc/) — WP-CB-1.
 *
 * Dashboard of connected calculator modules (#1→#14).
 * Shared dark context strip feeds every module.
 * Modules are grouped by topic.
 * Sticky summary + PDF/CSV export hooks (stubs).
 *
 * Architecture: one calculator = one module (data-calc key).
 * Same module embeds standalone in crop pages via .calcmodal.
 *
 * Variables from controller:
 *   $contact  array — contact info (from HubController)
 *
 * @see COMPONENTS-delta.md §29
 * @see TEMPLATES-delta.md §1 (route /calc/)
 */
use SFA\Lib\Template;
use SFA\Controllers\AssumptionsController;

$h = [Template::class, 'h'];

$page_title = 'מחשבון';
$page_sub   = 'תכנון גידולים · 14 מודולים';
$active     = 'calc';
$back_url   = '/';

$assumptions = AssumptionsController::getAssumptions();
$germRate    = (float)($assumptions['germination_rate']['default'] ?? 0.90);
$bedWidth    = (float)($assumptions['bed_width']['default']        ?? 0.80);
$stdLen      = (float)($assumptions['std_bed_length_m']['default'] ?? 30);
$oversow     = (float)($assumptions['oversow']['default']          ?? 1.10);
$compostN    = (float)($assumptions['compost_N_pct']['default']    ?? 0.015);
$appEff      = (float)($assumptions['application_efficiency']['default'] ?? 0.50);

ob_start();
?>
<div class="calc-page">
  <div class="calc-main">
    <header style="margin-bottom:4px">
      <div class="gj-eyebrow" style="font-family:var(--gj-font-mono);font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--gj-sun-deep);margin-bottom:6px;">מחשבון</div>
      <h1 class="gj-h1">לוח מחשבונים</h1>
      <p class="gj-lede">14 מחשבוני תכנון — זרעים, לוחות זמנים, יבול, הכנסה ודישון.</p>
    </header>

    <!-- Shared context strip -->
    <div class="calc-context">
      <label class="ipt">
        <label>גידול</label>
        <span class="ipt__box">
          <select data-k="crop_slug" aria-label="בחר גידול">
            <option value="">בחר גידול…</option>
          </select>
        </span>
      </label>
      <label class="ipt">
        <label>מספר ערוגות</label>
        <span class="ipt__box">
          <input type="number" data-k="num_beds" value="10" min="1"/>
          <span class="u">ערוגות</span>
        </span>
      </label>
      <label class="ipt">
        <label>תאריך יעד</label>
        <span class="ipt__box">
          <input type="date" data-k="target_date"/>
        </span>
      </label>
      <div class="calc-context__tag">
        <b>SSoT:</b> ערכי הספר נשלפים מהגידול שנבחר. שנה הנחות דרך ◇ הנחה.
      </div>
    </div>

    <!-- ── Group 1: זרעים וזריעה ── -->
    <div class="dash-group">
      <span class="dash-group__ic" style="background:var(--gj-leaf-deep)">🌱</span>
      <b>זרעים וזריעה</b>
      <span>מחשבונים 1–3</span>
    </div>
    <div class="calc-dash">

      <!-- Module #1: seed quantity -->
      <div class="modcard" data-calc="seed">
        <div class="modcard__head">
          <span class="modcard__no">1</span>
          <span class="modcard__t">כמות זרעים לקנייה</span>
          <span class="modcard__feed">→ מ-3</span>
        </div>
        <div class="modcard__body">
          <div class="modcard__src">
            קלט: <b>מרווח בשורה, שורות, זרעים/גרם</b>
          </div>
          <div class="cv__inputs" style="grid-template-columns:1fr 1fr">
            <label class="ipt"><label>אורך ערוגה</label>
              <span class="ipt__box"><input type="number" data-k="bed_len" value="30" min="1"/><span class="u">מ׳</span></span></label>
            <label class="ipt"><label>זרעים לחור</label>
              <span class="ipt__box"><input type="number" data-k="seeds_per_hole" value="1" min="1"/></span></label>
          </div>
          <div class="modcard__res" data-result>—<small> גרם</small></div>
          <div class="cv__formula" data-formula style="font-size:9px;direction:ltr"></div>
          <div data-extra style="font-size:10px;color:var(--gj-ink-soft)"></div>
        </div>
      </div>

      <!-- Module #8: expected yield -->
      <div class="modcard" data-calc="yield">
        <div class="modcard__head">
          <span class="modcard__no">8</span>
          <span class="modcard__t">יבול צפוי</span>
          <span class="modcard__feed to-sum">→ סיכום</span>
        </div>
        <div class="modcard__body">
          <div class="modcard__src">קלט: <b>יבול/מ׳</b></div>
          <div class="cv__inputs" style="grid-template-columns:1fr">
            <label class="ipt"><label>אורך ערוגה</label>
              <span class="ipt__box"><input type="number" data-k="bed_len" value="30" min="1"/><span class="u">מ׳</span></span></label>
          </div>
          <div class="modcard__res" data-result>—<small> ק״ג</small></div>
          <div class="cv__formula" data-formula style="font-size:9px;direction:ltr"></div>
        </div>
      </div>

      <!-- Module #10: plant population -->
      <div class="modcard" data-calc="pop">
        <div class="modcard__head">
          <span class="modcard__no">10</span>
          <span class="modcard__t">צפיפות צמחים</span>
        </div>
        <div class="modcard__body">
          <div class="modcard__src">קלט: <b>מרווח, שורות</b></div>
          <div class="modcard__res" data-result>—<small> צמ׳/מ״ר</small></div>
          <div class="cv__formula" data-formula style="font-size:9px;direction:ltr"></div>
          <div class="popgrid" data-popgrid style="grid-template-columns:repeat(4,1fr);max-width:200px"></div>
        </div>
      </div>

    </div>

    <!-- ── Group 2: יבול והכנסה ── -->
    <div class="dash-group">
      <span class="dash-group__ic" style="background:var(--gj-sun-deep)">💰</span>
      <b>יבול והכנסה</b>
      <span>מחשבונים 7, 9, 13</span>
    </div>
    <div class="calc-dash">

      <!-- Module #9: revenue -->
      <div class="modcard" data-calc="revenue">
        <div class="modcard__head">
          <span class="modcard__no">9</span>
          <span class="modcard__t">הכנסה צפויה</span>
          <span class="modcard__feed to-sum">→ סיכום</span>
        </div>
        <div class="modcard__body">
          <div class="modcard__src">קלט: <b>יבול/מ׳, מחיר</b></div>
          <div class="cv__inputs" style="grid-template-columns:1fr">
            <label class="ipt"><label>שטח</label>
              <span class="ipt__box"><input type="number" data-k="area" value="300" min="1"/><span class="u">מ׳</span></span></label>
          </div>
          <div class="modcard__res" data-result>—<small> ₪</small></div>
          <div class="cv__formula" data-formula style="font-size:9px;direction:ltr"></div>
        </div>
      </div>

    </div>

    <!-- ── Group 3: דישון ── -->
    <div class="dash-group">
      <span class="dash-group__ic" style="background:var(--gj-soil-deep)">🪱</span>
      <b>דישון</b>
      <span>מחשבון 12</span>
    </div>
    <div class="calc-dash">

      <!-- Module #12: fertiliser -->
      <div class="modcard" data-calc="fert">
        <div class="modcard__head">
          <span class="modcard__no">12</span>
          <span class="modcard__t">כמות קומפוסט</span>
        </div>
        <div class="modcard__body">
          <div class="modcard__src">קלט: <b>צריכת N, שטח</b></div>
          <div class="cv__inputs" style="grid-template-columns:1fr">
            <label class="ipt"><label>שטח</label>
              <span class="ipt__box"><input type="number" data-k="area_m2" value="300" min="1"/><span class="u">מ״ר</span></span></label>
          </div>
          <div class="modcard__res" data-result>—<small> ק״ג קומפוסט</small></div>
          <div class="cv__formula" data-formula style="font-size:9px;direction:ltr"></div>
          <div data-extra style="font-size:10px;color:var(--gj-ink-soft)"></div>
        </div>
      </div>

    </div>

    <!-- Assumptions section -->
    <div class="cb-block" style="margin-top:18px">
      <h3>הנחות תכנון</h3>
      <?php
      $assumption_keys_to_show = ['germination_rate', 'bed_width', 'oversow', 'std_bed_length_m', 'compost_N_pct', 'application_efficiency'];
      foreach ($assumption_keys_to_show as $key):
        $assump       = $assumptions[$key] ?? [];
        $display_value = (string)($assump['default'] ?? '');
        $display_unit  = (string)($assump['unit']    ?? '');
        if ($display_unit === 'fraction') { $display_value = (string)round((float)$display_value * 100); $display_unit = '%'; $data_scale = 0.01; }
        else { $data_scale = 1; }
        include __DIR__ . '/../macros/assumption_field.php';
      endforeach;
      ?>
    </div>
  </div>

  <!-- Sticky rail: summary + export -->
  <div class="calc-rail">
    <div class="calc-summary">
      <h4>סיכום תכנון</h4>
      <div class="calc-summary__row">
        <span>יבול כולל</span><b data-summary-yield>—</b>
      </div>
      <div class="calc-summary__row">
        <span>הכנסה כוללת</span><b data-summary-revenue>—</b>
      </div>
      <div class="calc-summary__row">
        <span>קומפוסט</span><b data-summary-compost>—</b>
      </div>
      <div class="calc-summary__row is-total">
        <span>סיכום יבול</span><b>—</b>
      </div>
    </div>
    <div class="calc-export">
      <h4>יצוא תכנון</h4>
      <p>שמרו, שתפו, ייבאו.</p>
      <div class="calc-export__btns">
        <a class="calc-export__btn" href="/calc/export.pdf" data-calc-export="pdf" target="_blank" rel="noopener">⬇ PDF</a>
        <a class="calc-export__btn calc-export__btn--ghost" href="/calc/export.csv" data-calc-export="csv">⬇ CSV</a>
      </div>
    </div>
  </div>
</div>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title', 'page_sub', 'active', 'back_url'));
