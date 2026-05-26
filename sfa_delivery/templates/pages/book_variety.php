<?php
use SFA\Lib\Template;
$h = fn($v) => htmlspecialchars((string)($v ?? ''), ENT_QUOTES, 'UTF-8');
$page_title = (string)($variety['name'] ?? 'זן');
$is_default = !empty($variety['is_default']);

// Field labels — Hebrew, matching crop-book design language
$field_labels = [
    'name_en'                  => 'שם באנגלית',
    'days_to_maturity'         => 'ימים לבגרות',
    'harvest_window_min_days'  => 'חלון קציר (מינ׳ ימים)',
    'harvest_window_max_days'  => 'חלון קציר (מקס׳ ימים)',
    'in_row_spacing_cm'        => 'מרווח בשורה (ס״מ)',
    'planting_method'          => 'שיטת שתילה',
    'planting_season'          => 'עונת שתילה',
    'harvest_unit'             => 'יחידת קציר',
    'documented_price'         => 'מחיר מתועד',
    'documented_price_unit'    => 'יחידת מחיר',
    'documented_price_source'  => 'מקור מחיר',
    'notes'                    => 'הערות',
];

ob_start();
?>
<section class="crop-variety">
  <nav class="breadcrumb">
    <a href="/crop-book/">ספר גידולים</a>
    &nbsp;›&nbsp;
    <a href="/crop-book/<?= $h($crop['slug']) ?>"><?= $h($crop['hebrew_name']) ?></a>
    &nbsp;›&nbsp;
    <strong><?= $h($variety['name']) ?></strong>
  </nav>

  <header>
    <h1>
      <?= $h($variety['name']) ?>
      <?php if ($is_default): ?><small style="color:var(--gj-leaf-deep); font-size:14px; margin-inline-start:8px;">· ברירת מחדל</small><?php endif; ?>
    </h1>
    <p class="muted">
      גידול: <a href="/crop-book/<?= $h($crop['slug']) ?>"><?= $h($crop['hebrew_name']) ?></a>
      <?php if (!empty($crop['scientific_name'])): ?>
        &nbsp;·&nbsp; <em><?= $h($crop['scientific_name']) ?></em>
      <?php endif; ?>
    </p>
  </header>

  <dl class="variety-fields">
    <?php $any_field = false; foreach ($field_labels as $key => $label):
        $val = $variety[$key] ?? null;
        if ($val === null || $val === '' || $val === false) continue;
        $any_field = true;
    ?>
      <dt><?= $h($label) ?></dt>
      <dd><?= $h($val) ?></dd>
    <?php endforeach; ?>
    <?php if (!$any_field): ?>
      <dt>—</dt>
      <dd>אין מידע מפורט עדיין על זן זה.</dd>
    <?php endif; ?>
  </dl>

  <p class="back-link"><a href="/crop-book/<?= $h($crop['slug']) ?>">← חזרה ל<?= $h($crop['hebrew_name']) ?></a></p>
</section>

<style>
  .crop-variety { max-width: 720px; margin: 0 auto; padding: 16px; }
  .crop-variety .breadcrumb { font-size: 14px; color: var(--gj-ink-soft); margin-bottom: 12px; }
  .crop-variety .breadcrumb a { color: var(--gj-leaf-deep); text-decoration: none; }
  .crop-variety header h1 { font-family: var(--gj-font-head); font-weight: 700; font-size: 26px; margin: 0 0 4px; }
  .crop-variety .muted { color: var(--gj-ink-soft); font-size: 14px; margin: 0 0 24px; }
  .crop-variety .muted a { color: var(--gj-leaf-deep); }
  .variety-fields { display: grid; grid-template-columns: max-content 1fr; gap: 8px 16px; padding: 16px; background: var(--gj-paper-2); border-radius: 8px; }
  .variety-fields dt { color: var(--gj-ink-soft); font-weight: 500; font-size: 14px; }
  .variety-fields dd { margin: 0; font-weight: 500; font-size: 15px; }
  .back-link { margin-top: 24px; }
  .back-link a { color: var(--gj-leaf-deep); text-decoration: none; min-height: 44px; display: inline-block; padding: 10px 0; }
</style>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title'));
