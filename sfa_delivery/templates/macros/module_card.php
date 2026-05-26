<article class="module-card">
  <h3><?= htmlspecialchars($module['name_he'] ?? '', ENT_QUOTES, 'UTF-8') ?></h3>
  <p><?= htmlspecialchars($module['sub'] ?? '', ENT_QUOTES, 'UTF-8') ?></p>
  <a href="<?= htmlspecialchars($module['route_runtime'] ?? '/', ENT_QUOTES, 'UTF-8') ?>">למודול</a>
</article>
