<?php
/**
 * rotation_hint.php — Rotation hint chip (component #23).
 *
 * Informational chip from botanical family. Not a calculator.
 * Gap = rotation_gap_seasons assumption (default 3).
 *
 * Variables:
 *   $family_name_he string — Hebrew family name (e.g. 'חסתיים')
 *   $family_lat     string — Latin family name (optional)
 *   $gap_seasons    int    — rotation gap (default 3)
 *
 * @see COMPONENTS-delta.md §23
 */
use SFA\Lib\Template;
$h = [Template::class, 'h'];

$family_name_he = (string)($family_name_he ?? '');
$family_lat     = (string)($family_lat ?? '');
$gap_seasons    = (int)($gap_seasons ?? 3);

if ($family_name_he === '') {
    return; // nothing to render without a family
}
?>
<div class="rothint">
  <span class="rothint__icon">⟳</span>
  <div>
    אל תעקבו אחרי <b><?= $h($family_name_he) ?></b> באותה ערוגה
    במשך <b data-assume-echo="rotation_gap_seasons"><?= $h((string)$gap_seasons) ?></b> עונות.
  </div>
  <?php if ($family_lat !== ''): ?>
  <span class="meta">family: <?= $h($family_lat) ?></span>
  <?php endif; ?>
</div>
