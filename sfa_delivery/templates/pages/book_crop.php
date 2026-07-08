<?php
/**
 * book_crop.php — Route /crop-book/{slug} — WP-CB-UI-REDESIGN (WI-4, centerpiece)
 *
 * Rebuilt from team_35 crop_card mockup. Retires the Simple/Full/Deep depth
 * switch for the mockup's UNIVERSAL DRILL-DOWN: a sticky lifecycle spine
 * (מתי → איך → טיפול → יבול) over <details class="topic"> cards that show KEY
 * data closed and DEPTH open. Two-level knowledge affordance (ⓘ hover tip L1 →
 * "ידע SFA" modal L2). Card data is wired to the real crop model; gaps render
 * as honest empty-states (never fabricated). Public-only notes (AC-U4-05).
 *
 * Controller contract (CropBookViewController::detail): crop{}, varieties[],
 * cb1_fields{field→{value_best,unit,field_state,winning_source_class}},
 * variety_ranges{field→{min,max,count}}, wc_art, related[], market via
 * crop.market_link, $depth (ignored by the universal layout; kept 200 for
 * back-compat ?depth= links).
 */
use SFA\Lib\Template;

$h = [Template::class, 'h'];

$crop      = is_array($crop ?? null) ? $crop : [];
$cb        = is_array($cb1_fields ?? null) ? $cb1_fields : [];
$ranges    = is_array($variety_ranges ?? null) ? $variety_ranges : [];
$related   = is_array($related ?? null) ? $related : [];
$wc_art    = $wc_art ?? null;

$name_he  = (string)($crop['name_he'] ?? ($crop['hebrew_name'] ?? 'גידול'));
$name_lat = (string)($crop['name_lat'] ?? ($crop['scientific_name'] ?? ''));
$slug     = (string)($crop['slug'] ?? '');
$fam_he   = (string)($crop['family_tag_he'] ?? ($crop['family_name_he'] ?? ''));
$variety_count = (int)($variety_count ?? count((array)($crop['varieties'] ?? [])));
$desc     = trim((string)($crop['description_he'] ?? ($crop['description'] ?? '')));

$page_title = $name_he;
$page_sub   = 'ספר גידולים';
$active     = 'crop-book';

// ── field helpers (honest: null when absent; never fabricate) ──
$nf = static function ($v): string {
    $s = number_format((float)$v, 1, '.', '');
    return rtrim(rtrim($s, '0'), '.');
};
$fval = static function (string $k) use ($cb) {
    $v = $cb[$k]['value_best'] ?? null;
    return ($v === null || $v === '') ? null : $v;
};
$fstate = static fn (string $k) => strtoupper((string)($cb[$k]['field_state'] ?? 'MISSING'));
// "min–max" across varieties when ≥2 differ, else the single best value.
$frange = static function (string $k) use ($cb, $ranges, $nf) {
    $r = $ranges[$k] ?? null;
    $rmin = is_array($r) ? ($r['min'] ?? null) : null;
    $rmax = is_array($r) ? ($r['max'] ?? null) : null;
    // Render "min–max" only when BOTH ends are present (else a missing side
    // produced a stray "–80"); otherwise fall through to the single best value.
    if (is_array($r) && (int)($r['count'] ?? 0) >= 2
        && $rmin !== null && $rmin !== '' && $rmax !== null && $rmax !== ''
        && (float)$rmin !== (float)$rmax) {
        return $nf($rmin) . '–' . $nf($rmax);
    }
    $v = $cb[$k]['value_best'] ?? null;
    return ($v === null || $v === '') ? null : $nf($v);
};
// provenance cue class for a field (drives the .pv-validated dot etc.)
$pcue = static function (string $k) use ($fstate): string {
    return match ($fstate($k)) {
        'VALIDATED'   => 'pv-validated',
        'UNVALIDATED', 'UNKNOWN' => 'pv-unvalidated',
        default       => 'pv-missing',
    };
};
// months list (sowing/transplant) — tolerates array | JSON-string | value_list.
$months = static function (string $k) use ($cb): array {
    $v = $cb[$k]['value_best'] ?? ($cb[$k]['value_list'] ?? null);
    if (is_string($v) && $v !== '') { $d = json_decode($v, true); $v = is_array($d) ? $d : []; }
    return is_array($v) ? array_values(array_filter(array_map('intval', $v), fn ($m) => $m >= 1 && $m <= 12)) : [];
};

$dtm_range = $frange('days_to_maturity') ?? (($crop['dtm_days'] ?? null) ? $nf($crop['dtm_days']) : null);
$spacing   = $frange('spacing_in_row_cm');
$rows_bed  = $fval('rows_per_bed');
$yield_m   = $frange('yield_per_bed_m');
$nursery   = $frange('days_in_nursery');
$seeds_g   = $fval('seeds_per_g');
$harvest_w = $frange('harvest_window_max_days');
$germ_days = $frange('germination_days');
$pmethod   = $fval('planting_method');
$frost     = $fval('frost_tolerance_class');
$sowM      = $months('sowing_months');
$transM    = $months('transplant_months');

// plants per bed-metre = (100 / spacing) × rows  (computed, honest formula)
$plants_m = null;
$sp1 = $fval('spacing_in_row_cm');
if ($sp1 !== null && (float)$sp1 > 0 && $rows_bed !== null && (float)$rows_bed > 0) {
    $plants_m = $nf((100 / (float)$sp1) * (float)$rows_bed);
}

// harvest months derived from (transplant ∪ sowing) + dtm (honest derivation)
$harvestM = [];
$dtmNum = (float)($fval('days_to_maturity') ?? ($crop['dtm_days'] ?? 0));
if ($dtmNum > 0) {
    foreach (($transM ?: $sowM) as $m) {
        $harvestM[] = (($m - 1 + (int)round($dtmNum / 30)) % 12) + 1;
    }
    $harvestM = array_values(array_unique($harvestM));
}

$MON = ['ינו','פבר','מרץ','אפר','מאי','יוני','יולי','אוג','ספט','אוק','נוב','דצמ'];
$MON_FULL = ['ינואר','פברואר','מרץ','אפריל','מאי','יוני','יולי','אוגוסט','ספטמבר','אוקטובר','נובמבר','דצמבר'];
$nowMonth = (int)date('n');
$canSowNow = in_array($nowMonth, array_merge($sowM, $transM), true);
$has_calendar = !empty($sowM) || !empty($transM) || !empty($harvestM);

// market chip
$mlink = is_array($crop['market_link'] ?? null) ? $crop['market_link'] : null;
// WP-FINAL-QA: live ₪ chip unit in Hebrew (kg→ק״ג, bunch→צרור, unit→יחידה); fall back to ק״ג.
$mlUnit = ($mlink && (string)($mlink['unit_he'] ?? '') !== '') ? (string)$mlink['unit_he'] : 'ק״ג';

// WP-CB-MARKET-RANGES: estimated market range (multi-engine research aggregate).
// The flat price_* fields ARE the PRIMARY basis — organic for most crops (SFA teaches
// organic growing), conventional for dried-form crops like hibiscus, where $mestNote
// clarifies the basis. Shown only when no live product price exists — a live price wins.
$mest        = is_array($crop['market_estimate'] ?? null) ? $crop['market_estimate'] : null;
$mestHas     = $mest !== null && (float)($mest['price_min'] ?? 0) > 0;
$mestNote    = $mest ? trim((string)($mest['note'] ?? '')) : '';
$mestPrimary = $mest ? (string)($mest['primary'] ?? 'organic') : 'organic';
$mestConv    = ($mest && is_array($mest['conventional'] ?? null)) ? $mest['conventional'] : null;
// Range formatter: "₪min" or "₪min–max" (trailing-zero-trimmed via $nf).
$mestRange = static function (array $x) use ($nf): string {
    $lo = (float)($x['price_min'] ?? 0);
    $hi = (float)($x['price_max'] ?? $lo);
    return '₪' . $nf($lo) . ($hi > $lo ? '–' . $nf($hi) : '');
};

// public notes (rich payload) — body_text list (honest, public-only)
$pub_notes = array_values(array_filter((array)($crop['notes'] ?? []), static fn ($n) => is_array($n) && !empty($n['body_text']) && empty($n['is_internal_farm_use_only'])));

// storage + companions (real payload sections)
$storage    = is_array($crop['storage'] ?? null) ? $crop['storage'] : [];
$companions = array_values(array_filter((array)($crop['companions'] ?? []), 'is_array'));
$comp_good  = array_filter($companions, static fn ($c) => ($c['compatibility'] ?? '') === 'beneficial');
$comp_bad   = array_filter($companions, static fn ($c) => ($c['compatibility'] ?? '') === 'antagonistic');

$frost_lbl = ['hardy'=>'עמיד לקרה','half_hardy'=>'חצי-עמיד','semi_hardy'=>'חצי-עמיד','tender'=>'רגיש לקרה','very_tender'=>'רגיש מאוד'];
$pm_lbl    = ['transplant'=>'שתילה ממשתלה','direct_seed'=>'זריעה ישירה','direct'=>'זריעה ישירה'];

// knowledge ⓘ helper — emits the two-level affordance (hover tip → modal)
$qm = static function (string $title, string $short, string $rich = '') use ($h): string {
    $d = $rich !== '' ? ' data-d="' . $h($rich) . '"' : '';
    return '<a class="qm" role="button" tabindex="0" data-t="' . $h($title) . '" data-s="' . $h($short) . '"' . $d . '>ⓘ</a>';
};

// ── WP-CB-CONTENT: multi-source narrative prose (Normal=canonical / Deep=per-source) ──
// Normal mode shows OUR consolidated canonical; Deep (?depth=deep) adds the full text per
// source with attribution. Absent content_type → honest empty-state preserved (never fabricated).
$is_deep = (string)($depth ?? '') === 'deep';
$content = is_array($crop_content ?? null) ? $crop_content : [];
$SRC_PILL = [
    'EX' => ['ex', 'EX · מומחה'],   'NI' => ['ex', 'NI · מקור מנומק'],
    'PR' => ['pr', 'PR · מקצועי'],  'WR' => ['wr', 'WR · רשת'],
    'OP' => ['wr', 'OP · שטח'],     'MK' => ['wr', 'MK · שוק'],
    'WB' => ['wr', 'WB · רשת'],     'UC' => ['wr', 'UC · קהילה'],
];
// Canonical body for a content_type (escaped, newlines → <br>); '' when absent.
$cbody = static function (string $ct) use ($content, $h): string {
    $md = trim((string)($content[$ct]['canonical'] ?? ''));
    return $md === '' ? '' : nl2br($h($md));
};
// Deep per-source block for a content_type — only when ?depth=deep AND sources exist.
$csrc = static function (string $ct) use ($content, $is_deep, $h, $SRC_PILL): string {
    if (!$is_deep) { return ''; }
    $srcs = $content[$ct]['sources'] ?? [];
    if (!is_array($srcs) || $srcs === []) { return ''; }
    $out = '<div class="kf"><b>ידע SFA · הטקסט המלא לפי מקור</b>';
    foreach ($srcs as $s) {
        $cls  = strtoupper((string)($s['source_class'] ?? ''));
        $pill = $SRC_PILL[$cls] ?? ['wr', $cls];
        $lbl  = (string)($s['source_label'] ?? '');
        $url  = trim((string)($s['source_url'] ?? ''));
        $body = nl2br($h((string)($s['raw_text_md'] ?? '')));
        $out .= '<div class="treat"><span class="srcline">'
              . '<span class="srcpill srcpill--' . $pill[0] . '">' . $h($pill[1]) . '</span>';
        if ($lbl !== '') { $out .= '<span class="sp">' . $h($lbl) . '</span>'; }
        if ($url !== '') { $out .= ' <a href="' . $h($url) . '" rel="nofollow noopener" target="_blank">מקור ←</a>'; }
        $out .= '</span><span>' . $body . '</span></div>';
    }
    return $out . '</div>';
};

ob_start();
?>
<div class="cb-crop-detail wrap">

  <!-- breadcrumb (right) · calculator button (left end) -->
  <div class="pagebar">
    <div class="bc"><a href="/crop-book/">ספר גידולים</a><?php if ($fam_he !== ''): ?> › <a href="/crop-book/family"><?= $h($fam_he) ?></a><?php endif; ?> › <b><?= $h($name_he) ?></b></div>
    <a class="btn btn--leaf calcbtn" href="/calc/?crop=<?= $h(rawurlencode($name_he)) ?>"><svg class="gi" aria-hidden="true"><use href="#i-scale"/></svg> מחשבון לגידול זה ←</a>
  </div>

  <!-- HERO -->
  <section class="hero">
    <div class="hero__art">
      <?php if ($wc_art): ?>
        <img src="/public_assets/img/crops/<?= $h($wc_art) ?>" alt="<?= $h($name_he) ?>" loading="eager" decoding="async">
      <?php else: ?>
        <span class="cc__icon" aria-hidden="true"><svg class="gi"><use href="#icon-<?= $h((string)($crop['icon_slug'] ?? 'leaf')) ?>"/></svg></span>
      <?php endif; ?>
    </div>
    <div>
      <h1 class="hero__name"><?= $h($name_he) ?></h1>
      <div class="hero__latin"><?php if ($name_lat !== ''): ?><span dir="ltr"><?= $h($name_lat) ?></span><?php endif; ?><?php if ($fam_he !== ''): ?> · משפחת <?= $h($fam_he) ?><?php endif; ?><?php if ($variety_count > 0): ?> · <span class="num"><?= $variety_count ?></span> זנים<?php endif; ?></div>

      <?php if ($desc !== ''): ?>
        <p class="hero__sum"><?= $h($desc) ?></p>
        <?php if (($sd = $csrc('story')) !== ''): ?><?= $sd ?><?php endif; ?>
      <?php else: ?>
        <p class="hero__sum muted">תיאור הגידול עדיין לא פורסם — יתווסף עם מודל התוכן. בינתיים, הנתונים החקלאיים למטה.</p>
      <?php endif; ?>

      <div class="hero__row">
        <?php if ($canSowNow): ?>
          <span class="pill pill--now"><svg class="gi" aria-hidden="true"><use href="#i-sprout"/></svg> אפשר לשתול עכשיו · <?= $h($MON_FULL[$nowMonth - 1]) ?></span>
        <?php endif; ?>
        <?php if ($frost !== null && isset($frost_lbl[(string)$frost])): ?>
          <span class="tag"><svg class="gi" aria-hidden="true"><use href="#i-snow"/></svg> <?= $h($frost_lbl[(string)$frost]) ?></span>
        <?php endif; ?>
        <?php if ($mlink && (float)($mlink['price_current'] ?? 0) > 0): ?>
          <a class="mktchip" href="/market/<?= $h((string)($mlink['slug'] ?? $slug)) ?>"><svg class="gi" aria-hidden="true"><use href="#i-shekel"/></svg> בשוק היום: <span class="num">₪<?= $h($nf($mlink['price_current'])) ?></span>/<?= $h($mlUnit) ?> ←</a>
        <?php elseif ($mestHas): ?>
          <span class="mktchip mktchip--est"<?= $mestNote !== '' ? ' title="' . $h($mestNote) . '"' : '' ?>><svg class="gi" aria-hidden="true"><use href="#i-shekel"/></svg> מחיר מוערך: <span class="num"><?= $h($mestRange($mest)) ?></span><?php if (($mu = (string)($mest['unit'] ?? '')) !== ''): ?>/<?= $h($mu) ?><?php endif; ?><?php if ((float)($mest['price_median'] ?? 0) > 0): ?> · חציון <span class="num">₪<?= $h($nf($mest['price_median'])) ?></span><?php endif; ?></span>
        <?php endif; ?>
      </div>

      <div class="glance">
        <?php if ($dtm_range !== null): ?><div><b class="num"><?= $h($dtm_range) ?></b><span>ימים להבשלה</span></div><?php endif; ?>
        <?php if ($spacing !== null): ?><div><b class="num"><?= $h($spacing) ?></b><span>מרווח בשורה (ס״מ)</span></div><?php endif; ?>
        <?php if ($plants_m !== null): ?><div><b class="num">~<?= $h($plants_m) ?></b><span>צמחים למטר ערוגה</span></div><?php endif; ?>
        <?php if ($yield_m !== null): ?><div><b class="num"><?= $h($yield_m) ?></b><span>ק״ג / מ׳ ערוגה</span></div><?php endif; ?>
      </div>
    </div>
  </section>

  <!-- lifecycle spine -->
  <nav class="stagenav" aria-label="שלבי הגידול">
    <ul>
      <li><a href="#s1"><span class="n">1</span> מתי לשתול</a></li>
      <li><a href="#s2"><span class="n">2</span> איך לשתול</a></li>
      <li><a href="#s3"><span class="n">3</span> טיפול לאורך העונה</a></li>
      <li><a href="#s4"><span class="n">4</span> יבול צפוי</a></li>
    </ul>
  </nav>

  <!-- STAGE 1 · מתי -->
  <section class="stage" id="s1">
    <div class="stage__head"><span class="stage__n">1</span><span class="stage__t">מתי לשתול<small>חלון הזריעה, השתילה והקציר לאורך השנה</small></span></div>
    <?php if ($has_calendar): ?>
      <div class="cal__grid">
        <span class="rl"></span>
        <?php foreach ($MON as $m): ?><span class="mh"><?= $h($m) ?></span><?php endforeach; ?>
        <?php
          $rows_cal = [];
          if (!empty($sowM))     { $rows_cal[] = ['זריעה', 'sow',   $sowM]; }
          if (!empty($transM))   { $rows_cal[] = ['שתילה', 'trans', $transM]; }
          if (!empty($harvestM)) { $rows_cal[] = ['קציר',  'harv',  $harvestM]; }
          foreach ($rows_cal as [$label, $cls, $set]):
        ?>
          <span class="rl"><?= $h($label) ?></span>
          <?php for ($m = 1; $m <= 12; $m++): ?>
            <span class="cal__cell<?= in_array($m, $set, true) ? ' ' . $cls : '' ?>"></span>
          <?php endfor; ?>
        <?php endforeach; ?>
      </div>
      <div class="cal__legend">
        <?php if (!empty($sowM)): ?><span><i style="background:var(--gj-leaf-soft)"></i>זריעה במשתלה</span><?php endif; ?>
        <?php if (!empty($transM)): ?><span><i style="background:var(--gj-leaf)"></i>שתילה לשדה</span><?php endif; ?>
        <?php if (!empty($harvestM)): ?><span><i style="background:var(--gj-sun)"></i>קציר (מוערך מימי ההבשלה)</span><?php endif; ?>
      </div>
    <?php else: ?>
      <div class="note">עדיין אין נתוני לוח זריעה/שתילה לגידול זה — <a href="/community">עזרו להשלים</a>.</div>
    <?php endif; ?>
  </section>

  <!-- STAGE 2 · איך -->
  <section class="stage" id="s2">
    <div class="stage__head"><span class="stage__n">2</span><span class="stage__t">איך לשתול<small>גידול השתילים במשתלה, ואז השתילה בשדה — לחצו להרחבה</small></span></div>

    <?php $nurseryKey = ($nursery !== null) ? '<b>שתילה ממשתלה</b> · ' . $h($nursery) . ' ימים' : ($pmethod !== null && isset($pm_lbl[(string)$pmethod]) ? '<b>' . $h($pm_lbl[(string)$pmethod]) . '</b>' : '<span class="muted">נתוני משתלה חסרים</span>'); ?>
    <details class="topic"<?= ($nursery !== null) ? ' open' : '' ?>>
      <summary><span class="topic__ic"><svg class="gi" aria-hidden="true"><use href="#i-sprout"/></svg></span><span class="topic__t">גידול שתילים</span><span class="topic__key"><?= $nurseryKey ?></span><span class="chev">▾</span></summary>
      <div class="topic__body">
        <div class="drill">▾ עומק נוסף</div>
        <dl class="dl">
          <?php if ($pmethod !== null && isset($pm_lbl[(string)$pmethod])): ?><div><dt>שיטת ריבוי <?= $qm('שיטת ריבוי', 'האם זורעים ישירות בשדה או מגדלים שתיל במשתלה ומעבירים.') ?></dt><dd><?= $h($pm_lbl[(string)$pmethod]) ?></dd></div><?php endif; ?>
          <?php if ($nursery !== null): ?><div><dt>ימים במשתלה <?= $qm('ימים במשתלה', 'מספר הימים מהזריעה עד שהשתיל מוכן לשדה.', 'rich-nursery') ?></dt><dd><span class="num"><?= $h($nursery) ?></span><span class="u">ימים</span></dd></div><?php endif; ?>
          <?php if ($germ_days !== null): ?><div><dt>ימים לנביטה <?= $qm('ימים לנביטה', 'מהזריעה עד הופעת הנבט.') ?></dt><dd><span class="num"><?= $h($germ_days) ?></span><span class="u">ימים</span></dd></div><?php endif; ?>
          <?php if ($seeds_g !== null): ?><div><dt>זרעים לגרם <?= $qm('זרעים לגרם', 'להמרת משקל זרעים לכמות שתילים.') ?></dt><dd><span class="num">~<?= $h($nf($seeds_g)) ?></span></dd></div><?php endif; ?>
        </dl>
        <?php if ($nursery === null && $pmethod === null && $germ_days === null && $seeds_g === null): ?>
          <p class="muted">נתוני גידול שתילים יתווספו עם השלמת המידע. <a href="/community">תרמו נתון ←</a></p>
        <?php endif; ?>
      </div>
    </details>

    <?php $fieldKey = ($spacing !== null) ? '<b>מרווח ' . $h($spacing) . ' ס״מ</b>' . ($rows_bed !== null ? ' · ' . $h($nf($rows_bed)) . ' שורות' : '') . ($plants_m !== null ? ' · ~' . $h($plants_m) . ' צמ׳/מ׳' : '') : '<span class="muted">נתוני מרווח חסרים</span>'; ?>
    <details class="topic"<?= ($spacing !== null) ? ' open' : '' ?>>
      <summary><span class="topic__ic"><svg class="gi" aria-hidden="true"><use href="#i-seedling"/></svg></span><span class="topic__t">שתילה בשדה</span><span class="topic__key"><?= $fieldKey ?></span><span class="chev">▾</span></summary>
      <div class="topic__body">
        <div class="drill">▾ עומק נוסף</div>
        <?php if ($spacing !== null && $rows_bed !== null): ?>
          <div class="spaceviz">
            <div class="big"><?= $h($spacing) ?><small>מרווח בשורה (ס״מ) <?= $qm('מרווח בשורה', 'המרחק בין שתיל לשתיל לאורך השורה — המספר שקובע את הצפיפות בפועל.', 'rich-spacing') ?></small></div>
            <span class="arrow">×</span>
            <div class="big"><?= $h($nf($rows_bed)) ?><small>שורות בערוגה</small></div>
            <?php if ($plants_m !== null): ?><span class="arrow">=</span><div class="big">~<?= $h($plants_m) ?><small>צמחים למטר ערוגה <?= $qm('צמחים למטר ערוגה', 'מחושב מהמרווח ומספר השורות.', 'rich-plantsm') ?></small></div><?php endif; ?>
          </div>
          <div class="formula"><b>איך חושב «צמחים למטר»:</b> (100 ÷ מרווח בשורה) × מס׳ שורות → (100÷<?= $h($nf($sp1)) ?>)×<?= $h($nf($rows_bed)) ?> ≈ <?= $h((string)$plants_m) ?></div>
        <?php else: ?>
          <p class="muted">נתוני מרווח ושורות יתווספו עם השלמת המידע. <a href="/community">תרמו נתון ←</a></p>
        <?php endif; ?>
        <?php $dtmR = $ranges['days_to_maturity'] ?? null; if (is_array($dtmR) && (int)($dtmR['count'] ?? 0) >= 2 && (float)$dtmR['min'] !== (float)$dtmR['max']): ?>
          <div class="srcline">טווח בין הזנים (ימים להבשלה): <span class="rng"><?= $h($nf($dtmR['min']) . '–' . $nf($dtmR['max'])) ?></span></div>
        <?php endif; ?>
      </div>
    </details>
  </section>

  <!-- STAGE 3 · טיפול -->
  <section class="stage" id="s3">
    <div class="stage__head"><span class="stage__n">3</span><span class="stage__t">טיפול לאורך העונה<small>לחצו על כל נושא להרחבה</small></span></div>

    <?php $waterBody = $cbody('care_watering'); ?>
    <details class="topic">
      <summary><span class="topic__ic"><svg class="gi" aria-hidden="true"><use href="#i-drop"/></svg></span><span class="topic__t">השקיה</span><span class="topic__key<?= $waterBody === '' ? ' muted' : '' ?>"><?= $waterBody === '' ? 'הנחיות מפורטות — בקרוב' : 'מדריך SFA' ?></span><span class="chev">▾</span></summary>
      <div class="topic__body"><div class="drill">▾ עומק נוסף</div>
        <?php if ($waterBody !== ''): ?>
          <p><?= $waterBody ?></p>
          <?= $csrc('care_watering') ?>
        <?php else: ?>
          <p class="muted">המלצות השקיה מפורטות (קצב, שיטה, מועדים) יתווספו עם מודל התוכן. ככלל — השקיה סדירה, הימנעות מהרטבת עלווה לצמצום מחלות. <a href="/community">תרמו ידע מהשטח ←</a></p>
        <?php endif; ?>
      </div>
    </details>

    <?php $fertBody = $cbody('care_fertilizing'); ?>
    <details class="topic">
      <summary><span class="topic__ic"><svg class="gi" aria-hidden="true"><use href="#i-compost"/></svg></span><span class="topic__t">דישון וקומפוסט</span><span class="topic__key<?= $fertBody === '' ? ' muted' : '' ?>"><?= $fertBody === '' ? 'דישון אורגני' : 'מדריך SFA' ?></span><span class="chev">▾</span></summary>
      <div class="topic__body">
        <div class="drill">▾ עומק נוסף</div>
        <?php if ($fertBody !== ''): ?>
          <p><?= $fertBody ?></p>
          <?= $csrc('care_fertilizing') ?>
        <?php else: ?>
          <p class="muted">הנחיות דישון כמותיות יתווספו עם מודל התוכן.</p>
        <?php endif; ?>
        <div class="organic"><svg class="gi" aria-hidden="true"><use href="#i-leaf"/></svg> <b>גידול אורגני:</b> בסיס הדישון — קומפוסט בשל בהכנת הערוגה (≈ 4–6 ק״ג/מ״ר כלל אצבע), בתוספת קומפוסט מועשר/דישון עלי אורגני לאורך העונה. ערכים מדויקים לגידול זה יתווספו עם נתוני התשומות.</div>
      </div>
    </details>

    <?php $pestBody = $cbody('care_pests'); $hasPest = $pestBody !== '' || !empty($pub_notes); ?>
    <details class="topic"<?= !empty($pub_notes) ? ' open' : '' ?>>
      <summary><span class="topic__ic"><svg class="gi" aria-hidden="true"><use href="#i-shield"/></svg></span><span class="topic__t">מזיקים ומחלות</span><span class="topic__key<?= $hasPest ? '' : ' muted' ?>"><?php
        if ($pestBody !== '' && !empty($pub_notes)) { echo 'מדריך SFA · <span class="num">' . count($pub_notes) . '</span> הערות קהילה'; }
        elseif ($pestBody !== '') { echo 'מדריך SFA'; }
        elseif (!empty($pub_notes)) { echo '<span class="num">' . count($pub_notes) . '</span> הערות קהילה'; }
        else { echo 'בקרוב'; }
      ?></span><span class="chev">▾</span></summary>
      <div class="topic__body cb-notes">
        <div class="drill">▾ עומק נוסף</div>
        <?php if ($pestBody !== ''): ?>
          <p><?= $pestBody ?></p>
          <?= $csrc('care_pests') ?>
        <?php endif; ?>
        <?php foreach ($pub_notes as $n): ?>
          <div class="treat"><b><?= $h(((string)($n['note_type'] ?? '') === 'pest_disease') ? 'מזיק/מחלה' : 'טיפ') ?>:</b><span><?= $h((string)$n['body_text']) ?><?php if (!empty($n['trust_tier'])): ?> <span class="sp"><?= $h((string)$n['trust_tier']) ?></span><?php endif; ?></span></div>
        <?php endforeach; ?>
        <?php if (!$hasPest): ?>
          <p class="muted">מדריך מזיקים ומחלות לגידול זה יתווסף עם מודל התוכן. <a href="/community">תרמו ניסיון שדה ←</a></p>
        <?php endif; ?>
      </div>
    </details>

    <details class="topic"<?= !empty($companions) ? ' open' : '' ?>>
      <summary><span class="topic__ic"><svg class="gi" aria-hidden="true"><use href="#i-companions"/></svg></span><span class="topic__t">חברה בערוגה</span><span class="topic__key"><?php if (!empty($comp_good)): ?>טוב: <?= $h(implode(', ', array_map(fn ($c) => (string)($c['name_he'] ?? ''), array_slice(array_values($comp_good), 0, 3)))) ?><?php else: ?><span class="muted">בקרוב</span><?php endif; ?></span><span class="chev">▾</span></summary>
      <div class="topic__body cb-companions compa">
        <div class="drill">▾ עומק נוסף</div>
        <?php if (!empty($companions)): ?>
          <?php if (!empty($comp_good)): ?><p class="good" style="margin:0 0 8px"><b>שכנים טובים:</b> <?php $g = []; foreach ($comp_good as $c) { $g[] = '<a href="/crop-book/' . $h((string)($c['slug'] ?? '')) . '/">' . $h((string)($c['name_he'] ?? '')) . '</a>'; } echo implode(' · ', $g); ?></p><?php endif; ?>
          <?php if (!empty($comp_bad)): ?><p class="bad" style="margin:0"><b>הימנעו לצד:</b> <?php $b = []; foreach ($comp_bad as $c) { $b[] = '<a href="/crop-book/' . $h((string)($c['slug'] ?? '')) . '/">' . $h((string)($c['name_he'] ?? '')) . '</a>' . (!empty($c['notes']) ? ' (' . $h((string)$c['notes']) . ')' : ''); } echo implode(' · ', $b); ?></p><?php endif; ?>
        <?php else: ?>
          <p class="muted">נתוני שכנוּת בערוגה יתווספו עם השלמת המידע.</p>
        <?php endif; ?>
      </div>
    </details>
  </section>

  <!-- STAGE 4 · יבול -->
  <section class="stage" id="s4">
    <div class="stage__head"><span class="stage__n">4</span><span class="stage__t">יבול צפוי<small>כמה יוצא, מתי, ובכמה — לחצו להרחבה</small></span></div>

    <details class="topic"<?= ($yield_m !== null) ? ' open' : '' ?>>
      <summary><span class="topic__ic"><svg class="gi" aria-hidden="true"><use href="#i-box"/></svg></span><span class="topic__t">יבול</span><span class="topic__key"><?php if ($yield_m !== null): ?><b><?= $h($yield_m) ?> ק״ג/מ׳ ערוגה</b><?php else: ?><span class="muted">נתוני יבול חסרים</span><?php endif; ?><?php if ($harvest_w !== null): ?> · חלון קציר <?= $h($harvest_w) ?> ימ׳<?php endif; ?></span><span class="chev">▾</span></summary>
      <div class="topic__body">
        <div class="drill">▾ עומק נוסף</div>
        <?php if ($yield_m !== null || $harvest_w !== null): ?>
          <dl class="dl">
            <?php if ($yield_m !== null): ?><div><dt><span class="<?= $pcue('yield_per_bed_m') ?>"></span>יבול למטר ערוגה <?= $qm('יבול למטר ערוגה', 'משקל פרי ממוצע למטר אורך של ערוגה.', 'rich-yield') ?></dt><dd><span class="num"><?= $h($yield_m) ?></span><span class="u">ק״ג</span></dd></div><?php endif; ?>
            <?php if ($harvest_w !== null): ?><div><dt>חלון קציר</dt><dd><span class="num"><?= $h($harvest_w) ?></span><span class="u">ימים</span></dd></div><?php endif; ?>
          </dl>
        <?php else: ?>
          <p class="muted">נתוני יבול יתווספו עם השלמת המידע. <a href="/community">תרמו נתון ←</a></p>
        <?php endif; ?>
      </div>
    </details>

    <?php if ($mlink && (float)($mlink['price_current'] ?? 0) > 0): ?>
    <details class="topic">
      <summary><span class="topic__ic"><svg class="gi" aria-hidden="true"><use href="#i-shekel"/></svg></span><span class="topic__t">הכנסה ושוק</span><span class="topic__key"><b><span class="num">₪<?= $h($nf($mlink['price_current'])) ?></span>/<?= $h($mlUnit) ?></b> · ממדד השוק</span><span class="chev">▾</span></summary>
      <div class="topic__body">
        <div class="drill">▾ עומק נוסף</div>
        <div class="profit">
          <div><div class="muted" style="font-size:13px">מחיר נוכחי במדד השוק הקהילתי</div><div class="profit__big"><span class="num">₪<?= $h($nf($mlink['price_current'])) ?></span> / <?= $h($mlUnit) ?></div></div>
          <div style="flex:1"></div>
          <a class="btn btn--leaf" href="/calc/?crop=<?= $h(rawurlencode($name_he)) ?>"><svg class="gi" aria-hidden="true"><use href="#i-scale"/></svg> חשב לכמות היעד שלי ←</a>
        </div>
        <div class="srcline">מתוך מדד השוק הקהילתי · <a href="/market/<?= $h((string)($mlink['slug'] ?? $slug)) ?>">למחירון המלא ←</a></div>
      </div>
    </details>
    <?php elseif ($mestHas): ?>
    <details class="topic">
      <summary><span class="topic__ic"><svg class="gi" aria-hidden="true"><use href="#i-shekel"/></svg></span><span class="topic__t">הכנסה ושוק</span><span class="topic__key"><b><span class="num"><?= $h($mestRange($mest)) ?></span><?php if (($mu = (string)($mest['unit'] ?? '')) !== ''): ?>/<?= $h($mu) ?><?php endif; ?></b> · מחיר מוערך</span><span class="chev">▾</span></summary>
      <div class="topic__body">
        <div class="drill">▾ עומק נוסף</div>
        <div class="profit">
          <div>
            <div class="muted" style="font-size:13px">מחיר מוערך<?= $mestPrimary === 'organic' ? ' · תוצרת אורגנית' : '' ?></div>
            <div class="profit__big"><span class="num"><?= $h($mestRange($mest)) ?></span><?php if (($mu = (string)($mest['unit'] ?? '')) !== ''): ?> / <?= $h($mu) ?><?php endif; ?></div>
            <?php if ((float)($mest['price_median'] ?? 0) > 0): ?><div class="muted" style="font-size:13px">חציון <span class="num">₪<?= $h($nf($mest['price_median'])) ?></span></div><?php endif; ?>
          </div>
          <div style="flex:1"></div>
          <a class="btn btn--leaf" href="/calc/?crop=<?= $h(rawurlencode($name_he)) ?>"><svg class="gi" aria-hidden="true"><use href="#i-scale"/></svg> חשב לכמות היעד שלי ←</a>
        </div>
        <?php if ($mestPrimary === 'organic' && $mestConv && (float)($mestConv['price_min'] ?? 0) > 0): ?>
          <div class="srcline">תוצרת רגילה (לא אורגנית): <span class="num"><?= $h($mestRange($mestConv)) ?></span><?php if (($cu = (string)($mestConv['unit'] ?? '')) !== ''): ?>/<?= $h($cu) ?><?php endif; ?></div>
        <?php endif; ?>
        <?php if ($mestNote !== ''): ?>
          <div class="srcline muted"><?= $h($mestNote) ?></div>
        <?php endif; ?>
        <div class="srcline">אומדן ממחקר שוק רב-מקורי<?php if (($ao = (string)($mest['as_of'] ?? '')) !== ''): ?> · עדכון <?= $h($ao) ?><?php endif; ?> · אינו מחיר מכירה</div>
      </div>
    </details>
    <?php endif; ?>

    <?php if (!empty($storage)): ?>
    <details class="topic">
      <summary><span class="topic__ic"><svg class="gi" aria-hidden="true"><use href="#i-snow"/></svg></span><span class="topic__t">אחסון</span><span class="topic__key"><?php
        $sk = [];
        if (isset($storage['temp']['min'], $storage['temp']['max'])) { $sk[] = '<b><span class="num">' . $h($nf($storage['temp']['min'])) . '–' . $h($nf($storage['temp']['max'])) . '°C</span></b>'; }
        if (isset($storage['life_days']['min'], $storage['life_days']['max'])) { $sk[] = 'חיי מדף <span class="num">' . $h($nf($storage['life_days']['min'])) . '–' . $h($nf($storage['life_days']['max'])) . '</span> ימים'; }
        echo $sk ? implode(' · ', $sk) : '<span class="muted">פרטי אחסון</span>';
      ?></span><span class="chev">▾</span></summary>
      <div class="topic__body cb-storage">
        <div class="drill">▾ עומק נוסף</div>
        <dl class="dl">
          <?php if (isset($storage['temp']['min'], $storage['temp']['max'])): ?><div><dt>טמפרטורה</dt><dd><span class="num"><?= $h($nf($storage['temp']['min']) . '–' . $nf($storage['temp']['max'])) ?></span><span class="u">°C</span></dd></div><?php endif; ?>
          <?php if (isset($storage['life_days']['min'], $storage['life_days']['max'])): ?><div><dt>חיי מדף</dt><dd><span class="num"><?= $h($nf($storage['life_days']['min']) . '–' . $nf($storage['life_days']['max'])) ?></span><span class="u">ימים</span></dd></div><?php endif; ?>
        </dl>
        <?php if (!empty($storage['notes'])): ?><p style="margin:8px 0 0"><?= $h((string)$storage['notes']) ?></p><?php endif; ?>
      </div>
    </details>
    <?php endif; ?>
  </section>

  <!-- contribute CTA -->
  <section class="contrib">
    <span class="contrib__ic" aria-hidden="true"><svg class="gi"><use href="#i-leaf"/></svg></span>
    <div class="t"><b>מצאתם נתון חסר או שגוי ב<?= $h($name_he) ?>?</b><p>הספר נבנה מניסיון הקהילה. עזרו לנו להשלים — זה לוקח דקה.</p></div>
    <span class="sp"></span>
    <a class="btn btn--primary" href="/community">✎ תרמו מידע על <?= $h($name_he) ?> ←</a>
  </section>

  <?php if (!empty($related)): ?>
  <section>
    <div class="eyebrow" style="margin-bottom:10px">גידולים קרובים · אותה משפחה</div>
    <div class="relrow">
      <?php foreach ($related as $r): $rslug = (string)($r['slug'] ?? ''); ?>
        <a class="relcard" href="/crop-book/<?= $h($rslug) ?>/">
          <div class="ph"><?php $rwc = \SFA\Lib\CropArt::file($rslug); if ($rwc !== null): ?><img src="/public_assets/img/crops/<?= $h($rwc) ?>" alt="" loading="lazy" decoding="async"><?php else: ?><span class="cc__icon" aria-hidden="true"><svg class="gi"><use href="#icon-leaf"/></svg></span><?php endif; ?></div>
          <div class="nm"><?= $h((string)($r['name_he'] ?? '')) ?></div>
          <?php if (!empty($r['fam_he'])): ?><span class="tag" style="margin-top:6px"><?= $h((string)$r['fam_he']) ?></span><?php endif; ?>
        </a>
      <?php endforeach; ?>
    </div>
  </section>
  <?php endif; ?>

</div><!-- /cb-crop-detail -->

<!-- knowledge modal (ⓘ L1 tip → L2 "ידע SFA" modal) -->
<div class="modal" id="kmodal" hidden>
  <div class="modal__bg" data-close></div>
  <div class="modal__card">
    <button class="modal__x" data-close aria-label="סגירה">✕</button>
    <div class="eyebrow">ידע SFA</div>
    <h3 id="kmt">—</h3>
    <div id="kmb"></div>
  </div>
</div>
<script>
(function(){
  var KB = {
    'rich-spacing':'<p>המרחק בין שתיל לשתיל לאורך השורה. זהו המספר המעשי שקובע כמה צמחים ייכנסו בערוגה — לא «צמחים למ״ר», שהוא נגזרת סטטיסטית.</p><div class="kf"><b>בחישוב:</b> צמחים למטר ערוגה = (100 ÷ מרווח בשורה) × מספר שורות.</div>',
    'rich-plantsm':'<p>מספר הצמחים שייכנסו במטר אורך של ערוגה, לפי המרווח ומספר השורות.</p><div class="kf"><b>הנוסחה:</b> (100 ÷ מרווח בשורה) × מספר שורות בערוגה.</div>',
    'rich-nursery':'<p>מספר הימים מהזריעה במשתלה ועד שהשתיל מוכן להעברה לשדה.</p><div class="kf"><b>למה זה חשוב:</b> קובע מתי להתחיל לזרוע במשתלה כדי לעמוד ביעד השתילה בשדה.</div>',
    'rich-yield':'<p>משקל הפרי הממוצע הצפוי למטר ערוגה בתנאי גידול תקינים.</p><div class="kf"><b>בחישוב:</b> יבול לערוגה = יבול למטר × אורך הערוגה. בסיס לחישובי הכנסה.</div>'
  };
  var modal=document.getElementById('kmodal'), kmt=document.getElementById('kmt'), kmb=document.getElementById('kmb');
  if(!modal) return;
  function openModal(q){
    kmt.textContent=q.getAttribute('data-t')||'הסבר';
    var d=q.getAttribute('data-d');
    kmb.innerHTML=(d&&KB[d])?KB[d]:('<p>'+(q.getAttribute('data-s')||'')+'</p><div class="kf">הסבר מורחב + נוסחת החישוב + מקור — יתווספו עם מודל התוכן.</div>');
    modal.hidden=false;
  }
  modal.addEventListener('click',function(e){ if(e.target.hasAttribute('data-close')) modal.hidden=true; });
  document.addEventListener('keydown',function(e){ if(e.key==='Escape') modal.hidden=true; });
  var tip=document.createElement('div'); tip.className='ktip'; tip.hidden=true; document.body.appendChild(tip);
  var curQ=null, hideT=null;
  function showTip(q){ clearTimeout(hideT); curQ=q;
    tip.innerHTML='<b>'+(q.getAttribute('data-t')||'')+'</b>'+(q.getAttribute('data-s')||'')+'<span class="more">להרחבה במודול ידע ←</span>';
    var r=q.getBoundingClientRect(); tip.hidden=false;
    tip.style.top=(window.scrollY+r.bottom+8)+'px';
    tip.style.left=Math.max(10,r.left+r.width/2-124)+'px';
  }
  function hideSoon(){ hideT=setTimeout(function(){tip.hidden=true;},250); }
  tip.addEventListener('mouseenter',function(){clearTimeout(hideT);});
  tip.addEventListener('mouseleave',hideSoon);
  tip.addEventListener('click',function(e){ if(e.target.classList.contains('more')&&curQ){ openModal(curQ); tip.hidden=true; }});
  document.querySelectorAll('.qm').forEach(function(q){
    q.addEventListener('mouseenter',function(){showTip(q);});
    q.addEventListener('mouseleave',hideSoon);
    q.addEventListener('click',function(e){ e.preventDefault(); openModal(q); });
    q.addEventListener('keydown',function(e){ if(e.key==='Enter'||e.key===' '){ e.preventDefault(); openModal(q);} });
  });
})();
</script>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title', 'page_sub', 'active'));
