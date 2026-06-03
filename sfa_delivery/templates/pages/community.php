<?php
/**
 * community.php — Route /community — Class B v2
 *
 * WP-CB-UI-CLASSB — Board-B frame `community`.
 * FEED-LESS per LOD400 §9.1 + MINOR F-06 (ignoring B-delta feed line).
 * Components: .comm-wrap, .comm-banner, .comm-manifest, .reqcard, .reqchip,
 *             .comm-collab.
 *
 * Data contract (HubController::community):
 *   $contact — Modules::all()['contact'] (optional)
 *
 * MINOR F-03: .reqchip chips map to kind=request-info in POST body
 *   (the only kind AssumptionsController::contribute accepts). No new endpoint.
 */
use SFA\Lib\Template;

$h = [Template::class, 'h'];

$contact = is_array($contact ?? null) ? $contact : [];
$wa_num  = (string)($contact['whatsapp'] ?? '972547776770');
$wa_link = 'https://wa.me/' . preg_replace('/\D/', '', $wa_num);

$page_title = 'קהילה';
$page_sub   = 'קהילה פתוחה';
$active     = 'community';

ob_start();
?>
<div class="comm-wrap">

  <?php /* Banner art — warm wash strip (Board-B L807: contact.webp) */ ?>
  <?php
  /* Only render the .comm-banner box when an image actually exists — no bare beige box. */
  $banner_candidates = [
      '/public_assets/img/contact.webp'        => __DIR__ . '/../../public_assets/img/contact.webp',
      '/public_assets/img/heroes/clients.webp' => __DIR__ . '/../../public_assets/img/heroes/clients.webp',
  ];
  $banner_img = null;
  foreach ($banner_candidates as $url => $path) {
      if (file_exists($path)) { $banner_img = $url; break; }
  }
  ?>
  <?php if ($banner_img !== null): ?>
  <div class="comm-banner" aria-hidden="true">
    <img src="<?= $h($banner_img) ?>" alt="" loading="lazy" decoding="async">
  </div>
  <?php endif; ?>

  <?php /* Manifesto */ ?>
  <div class="comm-manifest">
    <span class="gj-eyebrow">קהילה פתוחה</span>
    <h2>חקלאות מקומית — <em>ידע משותף</em></h2>
    <p>
      SFA נבנה על ניסיון שדה קהילתי ומחקר AI מתקדם.
      <b>כל נתון — מחיר, מינון, מועד — מגיע מחקלאים אמיתיים</b> ומוחזר לקהילה בחינם.
    </p>
    <p>
      אתם יכולים לתרום מחיר שוק, לשאול שאלה, להציע גידול חדש, או לדווח על שגיאה.
      כל תרומה קטנה מחזקת את הבסיס לכולם.
    </p>
  </div>

  <?php /* Request / suggest card — low-friction (MINOR F-03: all chips → kind=request-info) */ ?>
  <div class="reqcard">
    <h3>שאלה, הצעה, או דיווח?</h3>
    <p>בחרו נושא ושלחו הודעה קצרה — נחזור אליכם בוואטסאפ.</p>
    <div class="reqcard__chips" role="group" aria-label="סוג פנייה">
      <?php
      /* All chips map to kind=request-info — MINOR F-03 */
      $chips = [
          ['label' => '❓ שאלה', 'val' => 'question'],
          ['label' => '💰 דיווח מחיר', 'val' => 'price-report'],
          ['label' => '🌱 הצעת גידול', 'val' => 'crop-suggest'],
          ['label' => '🐛 דיווח שגיאה', 'val' => 'bug-report'],
          ['label' => '🤝 שיתוף-פעולה', 'val' => 'collab'],
      ];
      foreach ($chips as $i => $chip):
      ?>
      <button class="reqchip<?= $i === 0 ? ' is-on' : '' ?>"
              type="button"
              data-chip-val="<?= $h($chip['val']) ?>"
              data-field-name="<?= $h($chip['val']) ?>"><?= $h($chip['label']) ?></button>
      <?php endforeach; ?>
    </div>
    <form class="reqcard__field" action="/api/v1/contribute" method="post"
          onsubmit="(function(f){
            var chips = f.closest('.reqcard').querySelectorAll('.reqchip.is-on');
            var k = document.createElement('input');
            k.type='hidden'; k.name='kind'; k.value='request-info';
            f.appendChild(k);
            var fn = document.createElement('input');
            fn.type='hidden'; fn.name='field_name';
            fn.value = chips.length ? chips[0].dataset.fieldName : 'general';
            f.appendChild(fn);
          })(this)">
      <input type="text" name="message" placeholder="הודעה קצרה…" aria-label="הודעה" required>
      <button class="reqcard__send" type="submit">שלח</button>
    </form>
    <p style="font-size:11.5px;color:var(--gj-ink-soft);margin-top:10px">
      כל הפניות מוצפנות ואנונימיות. לא נדרשת הרשמה.
    </p>
  </div>

  <?php /* WhatsApp collab line */ ?>
  <div class="comm-collab">
    <span>מעדיפים ליצור קשר ישירות?</span>
    <a href="<?= $h($wa_link) ?>" target="_blank" rel="noopener">פתחו צ׳אט בוואטסאפ ←</a>
  </div>

</div>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title', 'page_sub', 'active'));
