<?php $tier = $tier ?? 'open'; ?>
<span class="tier-badge tier-<?= htmlspecialchars($tier, ENT_QUOTES, 'UTF-8') ?>"><?= htmlspecialchars($label ?? $tier, ENT_QUOTES, 'UTF-8') ?></span>
