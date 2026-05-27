<?php
/**
 * community.php — Community page (route: /community)
 *
 * Mandate §3 contract: emits .gj-shell + .contact-card + .contact-card__icon +
 *   .contact-card__h + .contact-card__lede + .contact-card__cta +
 *   .contact-card__sub (WhatsApp link, NO form per LOD400 v1.0.2 §0 LV-S-1).
 *   Also emits .community + .community__feed + .community__feed-h +
 *   .community__tiers + .community__tiers-h + .hub-tier-list, plus
 *   .feed-item (via macros/feed_item.php) and .tier (via macros/tier_badge.php).
 *
 * LV-S-1 binding (LOD400 §0): Community page has NO form element (no input
 *   posting back to the server). Public community writes are forbidden in
 *   this WP. WhatsApp CTA + contact-card pattern only.
 *
 * Architecture note: _layout.php includes both shell/mobile.php and
 *   shell/desktop.php (visibility swap is pure CSS). The page emits body
 *   content only.
 *
 * Variables consumed (provided by controller):
 *   $feed_items  array  — optional list of community feed items. Each entry has:
 *                          kind, author_he, region_he, date_he, text_he,
 *                          tag_he, upvotes. Passed to macros/feed_item.php.
 *
 * Shell variables set:
 *   $page_title = 'קהילה'
 *   $page_sub   = 'WhatsApp · ‎צ׳אט פתוח'
 *   $active     = 'community'
 */
use SFA\Lib\Template;

$h = [Template::class, 'h'];

$feed_items_in = is_array($feed_items ?? null) ? $feed_items : [];

$page_title = 'קהילה';
$page_sub   = 'WhatsApp · ‎צ׳אט פתוח';
$active     = 'community';

ob_start();
?>
<section class="community">
  <article class="contact-card">
    <div class="contact-card__icon">💬</div>
    <h1 class="contact-card__h">קהילת SFA — בוואטסאפ</h1>
    <p class="contact-card__lede">SFA נבנה ומתפתח בקהילה פתוחה של חקלאים קטנים. תרומה, שאלה, דיווח על שגיאה, או רק להגיד שלום — הצ׳אט פתוח.</p>
    <a href="https://wa.me/972547776770" class="contact-card__cta" target="_blank" rel="noopener">
      פתח צ׳אט בוואטסאפ →
    </a>
    <p class="contact-card__sub">המספר: 054-7776770 · ניתן גם להוסיף לרשימת אנשי קשר.</p>
  </article>

  <?php if (!empty($feed_items_in)): ?>
    <section class="community__feed">
      <h2 class="community__feed-h">פעילות קהילה אחרונה</h2>
      <?php foreach ($feed_items_in as $item):
        $kind      = (string)($item['kind']      ?? 'data');
        $author_he = (string)($item['author_he'] ?? '');
        $region_he = (string)($item['region_he'] ?? '');
        $date_he   = (string)($item['date_he']   ?? '');
        $text_he   = (string)($item['text_he']   ?? '');
        $tag_he    = (string)($item['tag_he']    ?? '');
        $upvotes   = (int)   ($item['upvotes']   ?? 0);
        include __DIR__ . '/../macros/feed_item.php';
      endforeach; ?>
    </section>
  <?php endif; ?>

  <section class="community__tiers">
    <h2 class="community__tiers-h">מבנה הכלים</h2>
    <ul class="hub-tier-list">
      <li>
        <?php $tier = 'open'; $size = 'sm'; include __DIR__ . '/../macros/tier_badge.php'; ?>
        כלים פתוחים — חינמיים, ללא הרשמה
      </li>
      <li>
        <?php $tier = 'beta'; $size = 'sm'; include __DIR__ . '/../macros/tier_badge.php'; ?>
        בטא — בפיתוח, ניסיוני
      </li>
      <li>
        <?php $tier = 'paid'; $size = 'sm'; include __DIR__ . '/../macros/tier_badge.php'; ?>
        מתקדם — מנוי
      </li>
      <li>
        <?php $tier = 'custom'; $size = 'sm'; include __DIR__ . '/../macros/tier_badge.php'; ?>
        מותאם — שיתוף-פעולה ישיר
      </li>
    </ul>
  </section>
</section>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title', 'page_sub', 'active'));
