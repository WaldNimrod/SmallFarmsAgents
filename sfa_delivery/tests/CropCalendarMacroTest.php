<?php
declare(strict_types=1);

namespace SFA\Tests;

use PHPUnit\Framework\TestCase;

/**
 * CropCalendarMacroTest — AC-U4-10: render test for crop_calendar.php macro.
 *
 * Verifies:
 *   - Active months get the cb-calendar__month--active class.
 *   - Inactive months do NOT get the active class.
 *   - Activity-type Hebrew labels appear.
 *   - Empty calendar renders the empty-state element.
 *   - Notes appear when supplied.
 *
 * @runTestsInSeparateProcesses
 * @preserveGlobalState disabled
 */
final class CropCalendarMacroTest extends TestCase
{
    private string $macroPath;

    protected function setUp(): void
    {
        $this->macroPath = dirname(__DIR__) . '/templates/macros/crop_calendar.php';
        $this->assertFileExists($this->macroPath, 'crop_calendar.php must exist');
    }

    /**
     * Active months get the --active modifier; inactive months do not.
     */
    public function testActiveMonthsHighlighted(): void
    {
        // months[0]=Jan, [1]=Feb, [2]=Mar active; rest inactive.
        $months = array_fill(0, 12, false);
        $months[0] = true;
        $months[1] = true;
        $months[2] = true;

        $html = $this->render([
            [
                'activity_type' => 'seed',
                'season'        => 'spring',
                'region'        => '',
                'months'        => $months,
                'notes'         => '',
            ],
        ]);

        // Three active month cells
        $activeCount = substr_count($html, 'cb-calendar__month--active');
        $this->assertSame(3, $activeCount, 'Exactly 3 active month cells expected');

        // Total of 12 month cells
        $totalMonths = substr_count($html, 'cb-calendar__month');
        // Each active cell has TWO occurrences of the class token in the class attribute
        // ("cb-calendar__month cb-calendar__month--active"), so total = 12 base + 3 active = 15
        $this->assertGreaterThanOrEqual(12, $totalMonths, 'At least 12 month cells total');
    }

    /**
     * Activity-type Hebrew label is rendered.
     */
    public function testActivityLabelRendered(): void
    {
        $html = $this->render([
            [
                'activity_type' => 'transplant',
                'season'        => 'summer',
                'region'        => '',
                'months'        => array_fill(0, 12, false),
                'notes'         => '',
            ],
        ]);

        $this->assertStringContainsString('שתילה', $html, 'Hebrew label for transplant must appear');
    }

    /**
     * Empty calendar renders the empty-state element.
     */
    public function testEmptyCalendarRendersEmptyState(): void
    {
        $html = $this->render([]);

        $this->assertStringContainsString('cb-calendar__empty', $html, 'Empty calendar must render the empty-state class');
    }

    /**
     * Notes text appears when supplied.
     */
    public function testNotesAppear(): void
    {
        $html = $this->render([
            [
                'activity_type' => 'seed',
                'season'        => 'winter',
                'region'        => 'IL_north',
                'months'        => array_fill(0, 12, false),
                'notes'         => 'זריעה תחת כיסוי בלבד',
            ],
        ]);

        $this->assertStringContainsString('זריעה תחת כיסוי בלבד', $html, 'Notes text must appear');
        $this->assertStringContainsString('צפון', $html, 'Zone region code must render its Hebrew label');
        $this->assertStringNotContainsString('IL_north', $html, 'Raw region code must never leak to the page');
    }

    /**
     * The generic default region (IL_general) renders its Hebrew label and the
     * raw token never leaks (mobile defect #2 — WP-CB-MOBILE v4 FIX 2 maps it
     * to "כל הארץ" rather than suppressing it).
     */
    public function testGenericRegionMapped(): void
    {
        $html = $this->render([
            [
                'activity_type' => 'seed',
                'season'        => 'spring',
                'region'        => 'IL_general',
                'months'        => array_fill(0, 12, false),
                'notes'         => '',
            ],
        ]);

        $this->assertStringNotContainsString('IL_general', $html, 'Generic region token must not leak raw');
        $this->assertStringContainsString('כל הארץ', $html, 'IL_general must render its Hebrew label');
    }

    /**
     * An unknown region code is suppressed rather than leaked raw.
     */
    public function testUnknownRegionSuppressed(): void
    {
        $html = $this->render([
            [
                'activity_type' => 'seed',
                'season'        => 'spring',
                'region'        => 'IL_unmapped_zone',
                'months'        => array_fill(0, 12, false),
                'notes'         => '',
            ],
        ]);

        $this->assertStringNotContainsString('IL_unmapped_zone', $html, 'Unknown region code must not leak raw');
        $this->assertStringNotContainsString('cb-calendar__region', $html, 'No region chip for an unmapped code');
    }

    /**
     * Seed activity label renders as "זריעה ישירה".
     */
    public function testSeedActivityLabel(): void
    {
        $html = $this->render([
            [
                'activity_type' => 'seed',
                'season'        => 'spring',
                'region'        => '',
                'months'        => array_fill(0, 12, false),
                'notes'         => '',
            ],
        ]);

        $this->assertStringContainsString('זריעה ישירה', $html, 'Hebrew label for seed activity must appear');
    }

    /**
     * Render crop_calendar.php with $calendar variable, return HTML string.
     *
     * @param list<array<string,mixed>> $calendar
     */
    private function render(array $calendar): string
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
