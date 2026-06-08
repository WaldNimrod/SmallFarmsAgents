<?php
/**
 * hub_calc.php — Yield calculator page (route: /calc)
 *
 * Mandate §3 contract: emits .gj-shell (via _layout.php → shell/mobile.php) +
 *   .tier.tier--sun (via macros/tier_badge.php with tier=beta which maps to the
 *   sun color in COMPONENTS.md §2 tier_map) + .tier__glyph + .tier--lg +
 *   .gj-crosslink (via macros/crosslink.php).
 *
 * Behavior 4 wiring: data-calc-form on <form>, data-calc-input on each input,
 *   data-calc-output on each <output>. sfa.js Behavior 4 binds 'input' events
 *   to recompute yield * area = total_yield, total_yield * price = total_revenue.
 *
 * Architecture note: see hub_home.php header — _layout.php includes both shells,
 *   so the page renders body content only.
 *
 * Variables consumed (provided by HubController::calc):
 *   $contact  array  — whatsapp number + label from MODULES_REGISTRY.yaml.contact
 *
 * Shell variables set:
 *   $page_title = 'מחשבון יבול'
 *   $page_sub   = 'בטא · בפיתוח'
 *   $active     = 'calc'
 *   $back_url   = '/'
 */
use SFA\Lib\Template;

$h = [Template::class, 'h'];

$contact_in = is_array($contact ?? null) ? $contact : [];
$wa_number  = preg_replace('/\D+/', '', (string)($contact_in['whatsapp'] ?? '972547776770'));
$wa_href    = 'https://wa.me/' . $wa_number . '?text=' . rawurlencode('פיצ׳ר מחשבון — רוצה יותר');

$page_title = 'מחשבון יבול';
$page_sub   = 'בטא · בפיתוח';
$active     = 'calc';
$back_url   = '/';

ob_start();
?>
<div class="hub-calc">
  <header class="hub-calc__head">
    <?php
      $tier = 'beta';
      $size = 'lg';
      include __DIR__ . '/../macros/tier_badge.php';
    ?>
    <h1 class="gj-h1">מחשבון יבול</h1>
    <p class="gj-lede">חישוב משוער של פוטנציאל יבול וערך כלכלי לפי שטח + גידול.</p>
  </header>

  <form class="hub-calc__form" data-calc-form>
    <fieldset class="dt-calc-field">
      <legend>יבול צפוי (ק״ג/מ״ר)</legend>
      <div class="dt-calc-row">
        <input type="number" data-calc-input="yield" value="9.2" step="0.1" min="0" aria-label="יבול לפי מ״ר"/>
        <span class="dt-calc-unit">ק״ג/מ״ר</span>
      </div>
      <small>טווח בספר: 5.5–11.4. ערך ברירת מחדל = ממוצע הזן.</small>
    </fieldset>

    <fieldset class="dt-calc-field">
      <legend>שטח (מ״ר)</legend>
      <div class="dt-calc-row">
        <input type="number" data-calc-input="area" value="100" step="1" min="0" aria-label="שטח גידול"/>
        <span class="dt-calc-unit">מ״ר</span>
      </div>
    </fieldset>

    <fieldset class="dt-calc-field">
      <legend>מחיר ליחידה</legend>
      <div class="dt-calc-row">
        <input type="number" data-calc-input="price" value="12.40" step="0.01" min="0" aria-label="מחיר לק״ג"/>
        <span class="dt-calc-unit">₪/ק״ג</span>
      </div>
    </fieldset>

    <div class="hub-calc__results">
      <div>
        <span>יבול כולל</span>
        <output data-calc-output="total-yield">920.0 ק״ג</output>
      </div>
      <div>
        <span>הכנסה כוללת</span>
        <output data-calc-output="total-revenue">₪ 11408</output>
      </div>
    </div>
  </form>

  <?php
    $href       = $wa_href;
    $art_html   = '<svg class="gi" aria-hidden="true"><use href="#i-chat"/></svg>';
    $big_text   = 'רוצים תכונות נוספות?';
    $small_unit = '';
    $sub_text   = 'תכנון רב-עונתי, חישוב עומק, ROI מלא';
    $direction  = '';
    include __DIR__ . '/../macros/crosslink.php';
  ?>
</div>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title', 'page_sub', 'active', 'back_url'));
