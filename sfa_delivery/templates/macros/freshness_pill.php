<?php
/**
 * freshness_pill.php — classb §34 (.fresh)
 *
 * Required vars (passed in via include scope):
 *   $freshness_days  int|null  — days since last price report (null = no data)
 *
 * Freshness thresholds (LOD400 §9a — LOCKED by team_00):
 *   ≤3  → .fresh--fresh  (leaf)   — "טרי"
 *   4–7 → .fresh--aging  (sun)    — "מתעדכן"
 *   >7 or null → .fresh--stale (tomato) — "ישן" / "אין דיווח"
 */
$_fd = isset($freshness_days) ? $freshness_days : null;
$_fd = $_fd !== null ? (int)$_fd : null;

if ($_fd === null) {
    $_cls  = 'fresh--stale';
    $_lbl  = 'אין דיווח';
} elseif ($_fd <= 3) {
    $_cls  = 'fresh--fresh';
    $_lbl  = $_fd === 0 ? 'טרי · עודכן היום' : ($_fd === 1 ? 'טרי · עודכן אתמול' : 'טרי · לפני ' . $_fd . ' ימים');
} elseif ($_fd <= 7) {
    $_cls  = 'fresh--aging';
    $_lbl  = 'מתעדכן · לפני ' . $_fd . ' ימים';
} else {
    $_cls  = 'fresh--stale';
    $_lbl  = 'ישן · לפני ' . $_fd . ' ימים';
}
?>
<span class="fresh <?= htmlspecialchars($_cls, ENT_QUOTES, 'UTF-8') ?>"><?= htmlspecialchars($_lbl, ENT_QUOTES, 'UTF-8') ?></span>
