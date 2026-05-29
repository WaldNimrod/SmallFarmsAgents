<?php
/**
 * crop_companions.php — Companion planting matrix.
 *
 * Variables expected from include scope:
 *   $companions (array) — list of entries, each:
 *     slug          (string) — partner crop slug (for link)
 *     name_he       (string) — partner crop Hebrew name
 *     compatibility (string) — 'beneficial' | 'antagonistic'
 *     notes         (string, optional)
 *
 * Beneficial companions → "טובים לשילוב" (green)
 * Antagonistic companions → "להימנע" (red)
 * Partner names link to /crop-book/{slug}
 */
$h = fn(string $s): string => htmlspecialchars($s, ENT_QUOTES, 'UTF-8');

$companions = is_array($companions ?? null) ? $companions : [];

$beneficial   = array_values(array_filter($companions, fn($c) => ($c['compatibility'] ?? '') === 'beneficial'));
$antagonistic = array_values(array_filter($companions, fn($c) => ($c['compatibility'] ?? '') === 'antagonistic'));

if (empty($companions)): ?>
  <p class="muted">אין נתוני ליווי גידולים זמינים.</p>
<?php else: ?>
  <div class="cb-companions">
    <?php if (!empty($beneficial)): ?>
      <div class="cb-companions__group cb-companions__group--good">
        <h3 class="cb-companions__group-title">
          <span class="cb-companions__dot cb-companions__dot--good" aria-hidden="true"></span>
          טובים לשילוב
        </h3>
        <ul class="cb-companions__list">
          <?php foreach ($beneficial as $c):
              $pSlug   = (string)($c['slug']    ?? '');
              $pName   = (string)($c['name_he'] ?? '');
              $pNotes  = (string)($c['notes']   ?? '');
              ?>
            <li class="cb-companions__item">
              <?php if ($pSlug !== ''): ?>
                <a href="/crop-book/<?= $h($pSlug) ?>" class="cb-companions__crop-link"><?= $h($pName) ?></a>
              <?php else: ?>
                <span><?= $h($pName) ?></span>
              <?php endif; ?>
              <?php if ($pNotes !== ''): ?>
                <span class="cb-companions__notes"><?= $h($pNotes) ?></span>
              <?php endif; ?>
            </li>
          <?php endforeach; ?>
        </ul>
      </div>
    <?php endif; ?>

    <?php if (!empty($antagonistic)): ?>
      <div class="cb-companions__group cb-companions__group--avoid">
        <h3 class="cb-companions__group-title">
          <span class="cb-companions__dot cb-companions__dot--avoid" aria-hidden="true"></span>
          להימנע
        </h3>
        <ul class="cb-companions__list">
          <?php foreach ($antagonistic as $c):
              $pSlug   = (string)($c['slug']    ?? '');
              $pName   = (string)($c['name_he'] ?? '');
              $pNotes  = (string)($c['notes']   ?? '');
              ?>
            <li class="cb-companions__item">
              <?php if ($pSlug !== ''): ?>
                <a href="/crop-book/<?= $h($pSlug) ?>" class="cb-companions__crop-link"><?= $h($pName) ?></a>
              <?php else: ?>
                <span><?= $h($pName) ?></span>
              <?php endif; ?>
              <?php if ($pNotes !== ''): ?>
                <span class="cb-companions__notes"><?= $h($pNotes) ?></span>
              <?php endif; ?>
            </li>
          <?php endforeach; ?>
        </ul>
      </div>
    <?php endif; ?>
  </div>
<?php endif; ?>
