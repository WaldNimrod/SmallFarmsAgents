<?php
/**
 * crop_notes.php — Public knowledge notes (empty-state when none).
 *
 * SECURITY: This macro MUST ONLY receive notes that have already been
 * filtered for is_internal_farm_use_only === false. The controller
 * and/or book_crop.php MUST apply this filter before passing $notes.
 * Internal notes MUST NEVER reach this template.
 *
 * Variables expected from include scope:
 *   $notes (array) — public-only list, each entry:
 *     note_type  (string)
 *     body_text  (string)
 *     trust_tier (string, optional)
 *
 * When $notes is empty → renders empty-state paragraph.
 */
$h = fn(string $s): string => htmlspecialchars($s, ENT_QUOTES, 'UTF-8');

$notes = is_array($notes ?? null) ? $notes : [];

$NOTE_TYPE_LABELS = [
    'tip'       => 'טיפ',
    'warning'   => 'אזהרה',
    'general'   => 'כללי',
    'variety'   => 'זנים',
    'pest'      => 'מזיקים',
    'disease'   => 'מחלות',
    'nutrition' => 'תזונה',
];

if (empty($notes)): ?>
  <p class="cb-notes__empty muted">אין הערות ציבוריות זמינות לגידול זה.</p>
<?php else: ?>
  <div class="cb-notes__list">
    <?php foreach ($notes as $note):
        $type     = (string)($note['note_type']  ?? 'general');
        $body     = (string)($note['body_text']  ?? '');
        $tier     = (string)($note['trust_tier'] ?? '');
        $type_he  = $NOTE_TYPE_LABELS[$type] ?? $type;
        if ($body === '') continue;
        ?>
      <article class="cb-note cb-note--<?= $h($type) ?>">
        <?php if ($type_he !== '' && $type_he !== 'כללי'): ?>
          <span class="cb-note__type pill pill--soil"><?= $h($type_he) ?></span>
        <?php endif; ?>
        <p class="cb-note__body"><?= $h($body) ?></p>
        <?php if ($tier !== ''): ?>
          <small class="cb-note__tier muted"><?= $h($tier) ?></small>
        <?php endif; ?>
      </article>
    <?php endforeach; ?>
  </div>
<?php endif; ?>
