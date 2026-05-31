<?php
/**
 * audience_switch.php — Cards ⇄ Table audience toggle (component #21).
 *
 * Variables:
 *   $active_view  string — 'cards'|'table' (default 'cards')
 *   $scope_id     string — id of the target element to show/hide (default 'audience-scope')
 *
 * @see COMPONENTS-delta.md §21
 */
use SFA\Lib\Template;
$h = [Template::class, 'h'];

$active_view = (string)($active_view ?? 'cards');
$scope_id    = (string)($scope_id   ?? 'audience-scope');
?>
<div class="aud" data-aud-switch="<?= $h($scope_id) ?>">
  <button
    class="aud__opt is-cards<?= $active_view === 'cards' ? ' is-active' : '' ?>"
    data-view="cards" type="button"
  >▦ כרטיסים<small>גנן/לומד</small></button>
  <button
    class="aud__opt is-table<?= $active_view === 'table' ? ' is-active' : '' ?>"
    data-view="table" type="button"
  >▤ טבלה<small>חקלאי</small></button>
</div>
