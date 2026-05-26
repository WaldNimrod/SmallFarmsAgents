<div class="price-card">
  <strong><?= htmlspecialchars((string)($product['hebrew_name'] ?? ''), ENT_QUOTES, 'UTF-8') ?></strong>
  <span><?= htmlspecialchars((string)($product['last_price'] ?? '—'), ENT_QUOTES, 'UTF-8') ?> ₪</span>
</div>
