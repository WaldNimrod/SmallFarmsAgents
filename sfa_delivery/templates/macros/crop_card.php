<div class="crop-card">
  <strong><?= htmlspecialchars((string)($crop['hebrew_name'] ?? ''), ENT_QUOTES, 'UTF-8') ?></strong>
  <a href="/crop-book/<?= htmlspecialchars((string)($crop['slug'] ?? ''), ENT_QUOTES, 'UTF-8') ?>">פרטים</a>
</div>
