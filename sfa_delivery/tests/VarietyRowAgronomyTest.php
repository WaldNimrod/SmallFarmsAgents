<?php
declare(strict_types=1);

namespace SFA\Tests;

use PHPUnit\Framework\TestCase;

/**
 * VarietyRowAgronomyTest — AC-U3-04, AC-U3-08, AC-U3-09 per WP-UI-patch03.
 *
 * Tests the rewritten variety_row.php macro which now renders agronomic fields
 * from $variety['agronomy'] instead of unsourced product fields (color/taste/shape).
 *
 * Assertions:
 *   AC-U3-08: color/taste/shape/resistance labels are ABSENT.
 *   AC-U3-09: agronomic Hebrew labels ARE present (days_to_maturity etc.).
 *   AC-U3-04: cb-var__val--delta class appears on a value that differs from default.
 *
 * @runTestsInSeparateProcesses
 * @preserveGlobalState disabled
 */
final class VarietyRowAgronomyTest extends TestCase
{
    private string $macroPath;

    protected function setUp(): void
    {
        $this->macroPath = dirname(__DIR__) . '/templates/macros/variety_row.php';
        $this->assertFileExists($this->macroPath, 'variety_row.php must exist');
    }

    /**
     * AC-U3-09: renders agronomic Hebrew labels; AC-U3-08: no product labels.
     */
    public function testAgronomicLabelsPresent(): void
    {
        $html = $this->renderRow([
            'vslug'         => 'variety-1',
            'name_he'       => 'זן בדיקה',
            'breeding_type' => 'F1',
            'is_default'    => true,
            'dtm_days'      => 60,
            'agronomy'      => [
                'days_to_maturity'       => 60,
                'in_row_spacing_cm'      => 30,
                'rows_per_bed'           => 2,
                'soil_ph_target'         => 6.5,
                'yield_per_m2_kg'        => 3.2,
                'storage_life_days'      => 14,
                'harvest_window_max_days' => 10,
                'seeds_per_gram'         => 350,
            ],
            'agro_delta'    => [],
        ], 'arugula');

        // AC-U3-09: agronomic Hebrew labels present
        $this->assertStringContainsString('ימים להבשלה', $html, 'AC-U3-09: days_to_maturity label must be present');
        $this->assertStringContainsString('מרווח שורה', $html,  'AC-U3-09: in_row_spacing_cm label must be present');
        $this->assertStringContainsString('שורות/ערוגה', $html, 'AC-U3-09: rows_per_bed label must be present');
        $this->assertStringContainsString('pH קרקע', $html,     'AC-U3-09: soil_ph_target label must be present');
        $this->assertStringContainsString('יבול', $html,        'AC-U3-09: yield_per_m2_kg label must be present');
        $this->assertStringContainsString('חיי מדף', $html,     'AC-U3-09: storage_life_days label must be present');
        $this->assertStringContainsString('חלון קטיף', $html,   'AC-U3-09: harvest_window_max_days label must be present');
        $this->assertStringContainsString('זרעים/גרם', $html,   'AC-U3-09: seeds_per_gram label must be present');

        // AC-U3-08: NO color/taste/shape/resistance labels
        $this->assertStringNotContainsString('צבע',    $html, 'AC-U3-08: color label must NOT appear');
        $this->assertStringNotContainsString('צורה',   $html, 'AC-U3-08: shape label must NOT appear');
        $this->assertStringNotContainsString('טעם',    $html, 'AC-U3-08: taste label must NOT appear');
        $this->assertStringNotContainsString('עמידות', $html, 'AC-U3-08: resistance label must NOT appear');
    }

    /**
     * AC-U3-04: cb-var__val--delta present on a value that differs from default.
     */
    public function testDeltaClassOnDifferingVariety(): void
    {
        // Non-default variety with a different dtm value (field delta = true)
        $html = $this->renderRow([
            'vslug'         => 'variety-2',
            'name_he'       => 'זן מבדל',
            'breeding_type' => 'OP',
            'is_default'    => false,
            'dtm_days'      => 75, // differs from default (60)
            'agronomy'      => [
                'days_to_maturity'  => 75,
                'in_row_spacing_cm' => 30,
            ],
            'agro_delta'    => [
                'days_to_maturity'  => true,  // differs from default
                'in_row_spacing_cm' => false,
            ],
        ], 'arugula');

        $this->assertStringContainsString('cb-var__val--delta', $html,
            'AC-U3-04: cb-var__val--delta must appear on differing variety value');
    }

    /**
     * AC-U3-04: cb-var__val--delta is ABSENT on default variety (all-false deltas).
     */
    public function testNoDeltaClassOnDefaultVariety(): void
    {
        $html = $this->renderRow([
            'vslug'         => 'variety-1',
            'name_he'       => 'זן בסיס',
            'breeding_type' => 'F1',
            'is_default'    => true,
            'dtm_days'      => 60,
            'agronomy'      => [
                'days_to_maturity'  => 60,
                'in_row_spacing_cm' => 30,
            ],
            'agro_delta'    => [
                'days_to_maturity'  => false,
                'in_row_spacing_cm' => false,
            ],
        ], 'arugula');

        $this->assertStringNotContainsString('cb-var__val--delta', $html,
            'AC-U3-04: cb-var__val--delta must NOT appear on default variety');
    }

    /**
     * Absent agronomy fields are skipped — no perpetual "—" cells.
     */
    public function testAbsentFieldsSkipped(): void
    {
        // Only dtm_days provided, no agronomy at all
        $html = $this->renderRow([
            'vslug'      => 'variety-3',
            'name_he'    => 'זן ריק',
            'is_default' => true,
            'dtm_days'   => 45,
            'agronomy'   => [],
            'agro_delta' => [],
        ], 'arugula');

        // DTM should still appear (from dtm_days)
        $this->assertStringContainsString('ימים להבשלה', $html, 'DTM label must appear when dtm_days is set');
        // Storage / spacing should NOT appear (absent from agronomy)
        $this->assertStringNotContainsString('חיי מדף', $html, 'Absent storage_life_days must not render');
        $this->assertStringNotContainsString('מרווח שורה', $html, 'Absent spacing must not render');
    }

    /**
     * Render variety_row.php with the given $variety and $crop_slug, return HTML.
     *
     * @param array<string,mixed> $variety
     */
    private function renderRow(array $variety, string $crop_slug): string
    {
        ob_start();
        try {
            include $this->macroPath;
        } finally {
            $html = ob_get_clean();
        }
        return (string)$html;
    }
}
