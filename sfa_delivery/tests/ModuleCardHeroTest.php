<?php
declare(strict_types=1);

namespace SFA\Tests;

use PHPUnit\Framework\TestCase;

/**
 * ModuleCardHeroTest — AC-13, AC-14 per LOD400_spec §4.
 *
 * Renders templates/macros/module_card.php in a buffered PHP include
 * and asserts the hero <img> is present/absent based on $module['hero_url'].
 *
 * This avoids a full Slim route hit and tests the macro in isolation.
 * A stub tier_badge.php is not needed because module_card.php includes it
 * via __DIR__ — we must create a minimal tier_badge.php stub in the test
 * fixture directory, OR rely on the real one. The real file exists in
 * templates/macros/tier_badge.php, so the include resolves correctly.
 */
final class ModuleCardHeroTest extends TestCase
{
    private string $macroPath;

    protected function setUp(): void
    {
        $this->macroPath = dirname(__DIR__) . '/templates/macros/module_card.php';
        $this->assertFileExists($this->macroPath, 'module_card.php must exist');
    }

    /**
     * AC-13: when hero_url is set, the output contains
     * <img class="mod-card__hero"> with the specified src.
     */
    public function testHeroImgEmittedWhenHeroUrlSet(): void
    {
        $heroUrl = 'https://sfa.nimrod.bio/public_assets/img/heroes/crop-book.webp';
        $html    = $this->renderCard(['hero_url' => $heroUrl]);

        $this->assertStringContainsString('class="mod-card__hero"', $html, 'AC-13: .mod-card__hero img must be present');
        $this->assertStringContainsString(htmlspecialchars($heroUrl, ENT_QUOTES, 'UTF-8'), $html, 'AC-13: hero src must match');
        $this->assertStringContainsString('<img', $html, 'AC-13: must be an img element');
    }

    /**
     * AC-14: when hero_url is NOT set, no .mod-card__hero element is emitted.
     */
    public function testHeroImgAbsentWhenHeroUrlUnset(): void
    {
        $html = $this->renderCard([]);
        $this->assertStringNotContainsString('mod-card__hero', $html, 'AC-14: .mod-card__hero must not appear when hero_url is unset');
    }

    /**
     * AC-14: empty string hero_url treated the same as unset.
     */
    public function testHeroImgAbsentWhenHeroUrlEmpty(): void
    {
        $html = $this->renderCard(['hero_url' => '']);
        $this->assertStringNotContainsString('mod-card__hero', $html, 'AC-14: .mod-card__hero must not appear for empty hero_url');
    }

    /**
     * Smoke: card renders at all (contains .mod-card class).
     */
    public function testCardRendersBasicStructure(): void
    {
        $html = $this->renderCard(['slug' => 'crop-book', 'name_he' => 'ספר גידולים', 'tier' => 'open', 'tier_color' => 'leaf']);
        $this->assertStringContainsString('mod-card', $html);
    }

    // ── Render helper ────────────────────────────────────────────────────────

    /**
     * Renders module_card.php with the given $module array and returns the
     * buffered output as a string.
     *
     * @param array<string,mixed> $moduleOverrides
     */
    private function renderCard(array $moduleOverrides): string
    {
        $module = array_merge([
            'slug'       => 'test-module',
            'name_he'    => 'מודול בדיקה',
            'tier'       => 'open',
            'tier_color' => 'leaf',
            'sub_he'     => 'תיאור',
            'stat_he'    => '0',
            'href'       => '/test/',
            'icon_svg'   => '<svg></svg>',
            'icon_id'    => '',
        ], $moduleOverrides);

        ob_start();
        try {
            // tier_badge.php is included relative to __DIR__ inside module_card.php.
            // It is the real macro file; include it as-is (it only reads $tier/$size).
            include $this->macroPath;
        } finally {
            $html = ob_get_clean();
        }
        return (string)$html;
    }
}
