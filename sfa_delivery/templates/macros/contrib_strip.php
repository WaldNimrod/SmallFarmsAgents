<?php
/**
 * contrib_strip.php — COMPONENTS.md §8
 *
 * Per LOD400 v1.0.2 §0 LV-S-1: public community WRITES are forbidden in this WP.
 * This macro renders the visual contract from §8 but routes the form action to
 * a WhatsApp wa.me link instead of /wp-json/sfa/v1/contribute (which is NOT
 * wired in this stack). Presentation-only — no backend POST endpoint.
 *
 * Required vars (passed in via include scope):
 *   $context          — string, e.g., "market.tomato"
 *   $context_label_he — string, e.g., "מחירון · ‎עגבנייה"
 *
 * BEM contract: .contrib-strip, .contrib-strip__head, .contrib-strip__icon,
 *   .contrib-strip__h, .contrib-strip__sub, .contrib-strip__input,
 *   .contrib-strip__cta, .contrib-strip__quick, .contrib-strip__chip
 */
$context          = (string)($context          ?? '');
$context_label_he = (string)($context_label_he ?? '');
$wa_phone         = '972547776770';

$wa_link = function (string $prefix) use ($wa_phone, $context_label_he): string {
    return 'https://wa.me/' . $wa_phone . '?text=' . urlencode($prefix . ' — ' . $context_label_he);
};
?>
<aside class="contrib-strip" data-context="<?= htmlspecialchars($context, ENT_QUOTES, 'UTF-8') ?>">
  <div class="contrib-strip__head">
    <span class="contrib-strip__icon">✎</span>
    <div>
      <div class="contrib-strip__h">תורמים נתונים? לא חייבים להירשם.</div>
      <div class="contrib-strip__sub"><?= htmlspecialchars($context_label_he, ENT_QUOTES, 'UTF-8') ?> — כל תרומה נסקרת ידנית.</div>
    </div>
  </div>
  <div class="contrib-strip__input">
    <a class="contrib-strip__cta" href="<?= htmlspecialchars($wa_link('תרומת נתונים'), ENT_QUOTES, 'UTF-8') ?>" target="_blank" rel="noopener"><svg class="gi" aria-hidden="true"><use href="#i-chat"/></svg> שלחו בוואטסאפ</a>
  </div>
  <div class="contrib-strip__quick" role="group">
    <a class="contrib-strip__chip" href="<?= htmlspecialchars($wa_link('מחיר שונה'), ENT_QUOTES, 'UTF-8') ?>" target="_blank" rel="noopener">מחיר שונה</a>
    <a class="contrib-strip__chip" href="<?= htmlspecialchars($wa_link('זן חסר'), ENT_QUOTES, 'UTF-8') ?>" target="_blank" rel="noopener">זן חסר</a>
    <a class="contrib-strip__chip" href="<?= htmlspecialchars($wa_link('שגיאה'), ENT_QUOTES, 'UTF-8') ?>" target="_blank" rel="noopener">שגיאה</a>
    <a class="contrib-strip__chip" href="<?= htmlspecialchars($wa_link('הצעה'), ENT_QUOTES, 'UTF-8') ?>" target="_blank" rel="noopener">הצעה</a>
  </div>
</aside>
