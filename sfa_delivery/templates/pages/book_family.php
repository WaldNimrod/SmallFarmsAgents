<?php
/**
 * book_family.php — Route /crop-book/family (CB2)
 *
 * Mandate §3 (route 7): `.gj-shell` family taxonomy list.
 * COMPONENTS.md (via crop-book-deep.css L113–137): `.cb-fam-list` + `.cb-fam` BEM (LOD400 §0.5 wins).
 *
 * Variables expected from controller:
 *   $families array — each item: [
 *     'slug', 'name_he', 'name_lat' (or 'name_en'), 'crop_count' (or 'total'),
 *     'color_tag' (optional — one of 'tomato'|'sun'|'soil'|'leaf'),
 *     'crops' (optional array of ['slug','name_he'])
 *   ]
 */
use SFA\Lib\Template;
$h = [Template::class, 'h'];

$page_title = 'משפחות בוטניות';
$page_sub   = 'ספר גידולים';
$active     = 'crop-book';
$back_url   = '/crop-book/';

$families = $families ?? [];

ob_start();
?>
<section class="cb-families">
  <h2 class="cb-section-h">משפחות בוטניות</h2>

  <?php if (empty($families)): ?>
    <p class="cb-qhint">משפחות יוצגו לאחר ייבוא נתוני העונה.</p>
  <?php else: ?>
    <ul class="cb-fam-list">
      <?php foreach ($families as $family):
        $slug       = (string)($family['slug']       ?? '');
        $name_he    = (string)($family['name_he']    ?? '');
        $name_lat   = (string)($family['name_lat']   ?? ($family['name_en'] ?? ''));
        $crop_count = (int)   ($family['crop_count'] ?? ($family['total']   ?? 0));
        $color_tag  = (string)($family['color_tag']  ?? '');
        $color_cls  = in_array($color_tag, ['tomato','sun','soil','leaf'], true)
                      ? ' cb-fam--' . $color_tag
                      : '';
        $crops      = is_array($family['crops'] ?? null) ? $family['crops'] : [];
      ?>
        <li class="cb-fam<?= $color_cls ?>">
          <a class="cb-fam__head" href="/crop-book/family/<?= $h($slug) ?>">
            <span>
              <span class="cb-fam__he"><?= $h($name_he) ?></span>
              <?php if ($name_lat !== ''): ?>
                <span class="cb-fam__en"><?= $h($name_lat) ?></span>
              <?php endif; ?>
            </span>
            <span class="cb-fam__count"><?= (int)$crop_count ?> גידולים</span>
          </a>
          <?php if (!empty($crops)): ?>
            <div class="cb-fam__crops">
              <?php foreach ($crops as $c): ?>
                <a class="pill pill--muted" href="/crop-book/<?= $h((string)($c['slug'] ?? '')) ?>"><?= $h((string)($c['name_he'] ?? '')) ?></a>
              <?php endforeach; ?>
            </div>
          <?php endif; ?>
        </li>
      <?php endforeach; ?>
    </ul>
  <?php endif; ?>

  <?php
  $context          = 'book.family';
  $context_label_he = 'ספר · משפחות בוטניות';
  include __DIR__ . '/../macros/contrib_strip.php';
  ?>
</section>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title', 'page_sub', 'active', 'back_url'));
