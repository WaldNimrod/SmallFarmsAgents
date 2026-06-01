<?php
/**
 * depth_tabs.php — Depth tabs for the crop page (component #22).
 *
 * Simple / Full / Drill-down toggle. One route; depth is a query param.
 * Emits [data-depths] + [data-depth-view] structure for crop-book-v1.js.
 *
 * Variables:
 *   $active_depth  string — 'simple'|'full'|'drill' (default 'simple')
 *   $scope_id      string — id of the scoped element (default 'depth-content')
 *
 * @see COMPONENTS-delta.md §22
 */
use SFA\Lib\Template;
$h = [Template::class, 'h'];

$active_depth = (string)($active_depth ?? 'simple');
$scope_id     = (string)($scope_id     ?? 'depth-content');

$tabs = [
    ['key' => 'simple', 'label' => 'פשוט',      'sub' => 'ראשי'],
    ['key' => 'full',   'label' => 'מלא',        'sub' => 'כל השדות'],
    ['key' => 'drill',  'label' => 'העמקה',      'sub' => 'מקורות'],
];
?>
<div class="depths" data-depths="<?= $h($scope_id) ?>" role="tablist">
  <?php foreach ($tabs as $tab): ?>
  <button
    type="button"
    data-depth="<?= $h($tab['key']) ?>"
    class="<?= $active_depth === $tab['key'] ? 'is-active' : '' ?>"
    role="tab"
    aria-selected="<?= $active_depth === $tab['key'] ? 'true' : 'false' ?>"
  ><?= $h($tab['label']) ?><small><?= $h($tab['sub']) ?></small></button>
  <?php endforeach; ?>
</div>
