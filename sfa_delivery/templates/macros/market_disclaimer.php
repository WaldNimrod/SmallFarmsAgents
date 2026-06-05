<?php
/**
 * market_disclaimer.php — COMPONENTS.md §10 / classb §33
 *
 * CRITICAL: copy is LOCKED by team_00. Must remain verbatim.
 * BEM class updated: .mk-disclaimer → .mkt-disc (classb.css §33, MINOR F-01).
 * No input variables — static block.
 *
 * BEM contract: .mkt-disc, .mkt-disc__ic, .mkt-disc__head, .mkt-disc__list
 *
 * $compact (bool, optional) — if true, uses a shorter single-column layout
 *   suitable for the market detail sidebar. Default false.
 * $collapsible (bool, optional) — WP-CB-MOBILE FIX 3: render as a
 *   <details class="mkt-disc"> that is CLOSED by default (the top note was too
 *   tall on mobile). The LOCKED מה/מאיפה/למה/לא copy is preserved verbatim.
 *   The static <aside> variant is kept for the detail sidebar. Default false.
 */
$compact     = isset($compact) && $compact === true;
$collapsible = isset($collapsible) && $collapsible === true;
?>
<?php if ($collapsible): ?>
<details class="mkt-disc<?= $compact ? ' mkt-disc--compact' : '' ?>">
  <summary>
    <span class="mkt-disc__ic" aria-hidden="true">ⓘ</span>
    <span class="mkt-disc__head">מה זה? מאיפה זה? למה זה?</span>
    <span class="chev" aria-hidden="true">▾</span>
  </summary>
  <ul class="mkt-disc__list">
    <li><b>מה:</b> ממוצעים מתגלגלים של מחירי תוצרת חקלאית טרייה — 7 ימים אחרונים.</li>
    <li><b>מאיפה:</b> סוכני סריקה ציבוריים של mezoo + תרומות חקלאים. ‎מצרפי, אנונימי.</li>
    <li><b>למה:</b> כלי שיווקי קהילתי. הוכחה שאפשר ידע פתוח גם בשוק החקלאי המקומי.</li>
    <li><b>לא:</b> לא הצעה מסחרית, לא קביעת מחיר, לא חוות-דעת. הקשר אינדיקטיבי בלבד.</li>
  </ul>
</details>
<?php else: ?>
<aside class="mkt-disc<?= $compact ? ' mkt-disc--compact' : '' ?>">
  <div class="mkt-disc__ic" aria-hidden="true">ⓘ</div>
  <div class="mkt-disc__head">מה זה? מאיפה זה? למה זה?</div>
  <ul class="mkt-disc__list">
    <li><b>מה:</b> ממוצעים מתגלגלים של מחירי תוצרת חקלאית טרייה — 7 ימים אחרונים.</li>
    <li><b>מאיפה:</b> סוכני סריקה ציבוריים של mezoo + תרומות חקלאים. ‎מצרפי, אנונימי.</li>
    <li><b>למה:</b> כלי שיווקי קהילתי. הוכחה שאפשר ידע פתוח גם בשוק החקלאי המקומי.</li>
    <li><b>לא:</b> לא הצעה מסחרית, לא קביעת מחיר, לא חוות-דעת. הקשר אינדיקטיבי בלבד.</li>
  </ul>
</aside>
<?php endif; ?>
