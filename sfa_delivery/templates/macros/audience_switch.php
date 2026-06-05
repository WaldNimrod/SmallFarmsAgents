<?php
/**
 * audience_switch.php — Cards ⇄ Table audience toggle (component #21).
 *
 * Variables:
 *   $active_view  string — 'cards'|'table' (default 'cards')
 *   $scope_id     string — id of the target element to show/hide (default 'audience-scope')
 *   $persist_key  string — optional localStorage key; when set the JS remembers
 *                          the user's cards⇄table choice across visits (D1).
 *
 * @see COMPONENTS-delta.md §21
 */
use SFA\Lib\Template;
$h = [Template::class, 'h'];

$active_view = (string)($active_view ?? 'cards');
$scope_id    = (string)($scope_id   ?? 'audience-scope');
$persist_key = isset($persist_key) ? (string)$persist_key : '';
?>
<div class="aud" data-aud-switch="<?= $h($scope_id) ?>"<?= $persist_key !== '' ? ' data-aud-persist="' . $h($persist_key) . '"' : '' ?>>
  <button
    class="aud__opt is-cards<?= $active_view === 'cards' ? ' is-active' : '' ?>"
    data-view="cards" type="button"
  >▦ כרטיסים<small>גנן/לומד</small></button>
  <button
    class="aud__opt is-table<?= $active_view === 'table' ? ' is-active' : '' ?>"
    data-view="table" type="button"
  >▤ טבלה<small>חקלאי</small></button>
</div>
