<?php
declare(strict_types=1);

namespace SFA\Lib;

/**
 * FieldRegistry — Hebrew field label + alias resolver for Crop Book v1 (WP-CB-1).
 *
 * Implements the FIM §1 canonical resolver so the UI is immune to the
 * field_policy↔canon naming drift (F-CB1-UI-01).
 *
 * Read order for a concept: canonical key → original key → alias siblings.
 * First hit wins.
 *
 * @see FIELD_INTERFACE_MAP_v1.0.0.md §1
 */
final class FieldRegistry
{
    /**
     * Bidirectional alias map — mirrors calculator_meta.FIELD_ALIASES.
     * Key = old/design name → value = canonical name.
     *
     * @var array<string,string>
     */
    private const CANON = [
        'in_row_spacing_cm'    => 'spacing_in_row_cm',
        'avg_yield_per_bed_m'  => 'yield_per_bed_m',
        'documented_price'     => 'price_documented',
        'seeds_per_gram'       => 'seeds_per_g',
        'frost_tolerance'      => 'frost_tolerance_class',
        'days_in_nursery_cell' => 'days_in_nursery',
        'succession_interval'  => 'succession_interval_weeks',
        'nutrient_removal_N'   => 'nutrient_removal_n_kg_per_ha',
        'planting_season'      => 'sowing_months',
        'dtm'                  => 'days_to_maturity',
        'yield'                => 'yield_per_bed_m',
        'price'                => 'price_documented',
        'spacing'              => 'spacing_in_row_cm',
        // WP-CB-MIG2 aliases (AC-05 / AC-09 / D-MIG2-1 / D-MIG2-2)
        'sale_unit'            => 'harvest_unit',   // alias: sale_unit → existing harvest_unit attr
        'seeder_model'         => 'seeder',          // alias: seeder_model → existing seeder column
    ];

    /**
     * Hebrew label dictionary (label, explainer, layer).
     * layer: EN=enrichment, AT=attribute, ID=identity, DERIVE=computed.
     *
     * @var array<string, array{0:string, 1:string, 2:string}>
     */
    private const LABELS = [
        'days_to_maturity'           => ['ימים להבשלה', 'מספר הימים מהזריעה/שתילה עד תחילת הקציר.', 'EN'],
        'harvest_window_max_days'    => ['חלון קציר', 'כמה ימים נמשך הקציר מרגע ההבשלה הראשונה.', 'EN'],
        'harvest_window_min_days'    => ['חלון קציר מינ׳', 'תחילת חלון הקציר — ימים מהזריעה.', 'EN'],
        'spacing_in_row_cm'          => ['מרווח בשורה', 'המרחק בין צמח לצמח לאורך השורה, ס״מ.', 'EN'],
        'in_row_spacing_cm'          => ['מרווח בשורה', 'המרחק בין צמח לצמח לאורך השורה, ס״מ.', 'EN'],
        'rows_per_bed'               => ['שורות בערוגה', 'כמה שורות צמחים נכנסות ברוחב ערוגה אחת (80 ס״מ).', 'EN'],
        'seeds_per_g'                => ['זרעים לגרם', 'כמה זרעים יש בגרם אחד — ממיר מספר צמחים לכמות זרעים.', 'EN'],
        'seeds_per_gram'             => ['זרעים לגרם', 'כמה זרעים יש בגרם אחד.', 'EN'],
        'yield_per_bed_m'            => ['יבול ממוצע למ׳', 'קילוגרם תוצרת למטר ערוגה — ממוצע.', 'EN'],
        'avg_yield_per_bed_m'        => ['יבול ממוצע למ׳', 'קילוגרם תוצרת למטר ערוגה — ממוצע.', 'EN'],
        'price_documented'           => ['מחיר מתועד', 'מחיר השוק האחרון שתועד, ליחידת המכירה.', 'EN'],
        'documented_price'           => ['מחיר מתועד', 'מחיר השוק האחרון שתועד.', 'EN'],
        'sowing_months'              => ['חודשי זריעה', 'החודשים שבהם מומלץ לזרוע — 1=ינואר … 12=דצמבר.', 'AT'],
        'transplant_months'          => ['חודשי שתילה', 'החודשים שבהם מומלץ לשתול שתיל.', 'AT'],
        'planting_method'            => ['שיטת שתילה', 'זריעה ישירה בשדה, גידול שתיל, או שניהם.', 'AT'],
        'frost_tolerance_class'      => ['עמידות לקרה', 'סיווג: hardy / half_hardy / tender / very_tender.', 'AT'],
        'frost_tolerance'            => ['עמידות לקרה', 'סיווג עמידות לקרה.', 'AT'],
        'days_in_nursery'            => ['ימים במשתלה', 'כמה ימים השתיל גדל במשתלה לפני שתילה בשדה.', 'EN'],
        'days_in_nursery_cell'       => ['ימים במשתלה', 'כמה ימים השתיל גדל במשתלה לפני שתילה בשדה.', 'EN'],
        'succession_interval_weeks'  => ['מרווח רצף', 'כל כמה שבועות לזרוע מנה חדשה לקציר רציף.', 'EN'],
        'succession_interval'        => ['מרווח רצף', 'כל כמה שבועות לזרוע מנה חדשה לקציר רציף.', 'EN'],
        'nutrient_removal_n_kg_per_ha' => ['צריכת חנקן (N)', 'כמות החנקן שהגידול מוציא, ק״ג לדונם.', 'EN'],
        'nutrient_removal_N'         => ['צריכת חנקן (N)', 'כמות החנקן שהגידול מוציא.', 'EN'],
        'family'                     => ['משפחה בוטנית', 'המשפחה הבוטנית — בסיס לרמז מחזור הגידולים.', 'ID'],
        'needs_summer_shade'         => ['הצללה בקיץ', 'גידולים מסוימים זקוקים לרשת צל בקיץ. שלוש רמות: 30%/40%/50%.', 'AT'],
        'irrigation_type'            => ['סוג השקיה', 'אופן ההשקיה — טפטוף או ממטרות. שדה מוצע.', 'AT'],
        'drip_lines_per_bed'         => ['קווי טפטוף לערוגה', 'מספר קווי טפטוף לערוגה אחת.', 'EN'],
        'root_depth_class'           => ['עומק שורשים', 'עומק בית השורשים: רדוד/בינוני/עמוק. שדה מוצע.', 'AT'],
        'sale_unit'                  => ['יחידת מכירה', 'היחידה הנמכרת: ראש/אגודה/ק״ג/יחידה. שדה מוצע.', 'AT'],
        'harvest_unit_default'       => ['יחידת קציר', 'יחידת הקציר/מכירה כברירת מחדל.', 'ID'],
        // WP-CB-MIG2 — 7 newly-wired proposed fields (AC-09)
        'seeder_settings'            => ['הגדרות זרעיה', 'תיאור כולל של הגדרות גלגל/גלגלון/הנעה לזרעיה.', 'ID'],
        'common_pests'               => ['מזיקים נפוצים', 'רשימת המזיקים הנפוצים לגידול זה (מקור: JMF).', 'AT'],
        'foliar_feeding_program'     => ['תוכנית דשון עלי', 'תיאור תוכנית הדשון העלי (ביופסטיצידים וכד׳).', 'AT'],
        'labor_rate_harvest'         => ['קצב קציר', 'יחידות קציר לשעת עבודה (יח׳/שעה).', 'EN'],
        'labor_rate_wash'            => ['קצב שטיפה', 'יחידות שטיפה לשעת עבודה (יח׳/שעה).', 'EN'],
        'plantings_per_season'       => ['שתילות עונה', 'מספר מחזורי גידול בעונה אחת.', 'EN'],
        'harvest_weeks_span'         => ['ספן קציר', 'משך תקופת הקציר בשבועות.', 'EN'],
    ];

    /**
     * Resolve a field name to its canonical form.
     * resolve('avg_yield_per_bed_m') → 'yield_per_bed_m'
     * resolve('yield_per_bed_m')     → 'yield_per_bed_m'  (already canonical)
     */
    public static function resolve(string $name): string
    {
        return self::CANON[$name] ?? $name;
    }

    /**
     * Look up a value in a crop enrichment array, trying canonical → original → alias siblings.
     * Returns the first non-null/non-empty hit, or null if all miss.
     *
     * @param array<string,mixed> $enrichment  flat key→value array
     * @param string              $name         any name (design/old/canonical)
     * @return mixed|null
     */
    public static function read(array $enrichment, string $name): mixed
    {
        $canonical = self::resolve($name);

        // canonical key
        if (isset($enrichment[$canonical]) && $enrichment[$canonical] !== '') {
            return $enrichment[$canonical];
        }
        // original (old) key
        if ($canonical !== $name && isset($enrichment[$name]) && $enrichment[$name] !== '') {
            return $enrichment[$name];
        }
        // alias siblings: any other alias that maps to the same canonical
        foreach (self::CANON as $alias => $target) {
            if ($target === $canonical && $alias !== $name) {
                if (isset($enrichment[$alias]) && $enrichment[$alias] !== '') {
                    return $enrichment[$alias];
                }
            }
        }
        return null;
    }

    /**
     * Return [label_he, explainer_he] for a field name.
     * Falls back to [field_name, ''] when not in dictionary.
     *
     * @return array{0:string,1:string}
     */
    public static function label(string $name): array
    {
        $canonical = self::resolve($name);
        if (isset(self::LABELS[$canonical])) {
            return [self::LABELS[$canonical][0], self::LABELS[$canonical][1]];
        }
        if (isset(self::LABELS[$name])) {
            return [self::LABELS[$name][0], self::LABELS[$name][1]];
        }
        return [$name, ''];
    }

    /**
     * Check if a field is a "proposed" (WP-CB-MIG2) field with no live data yet.
     * Covers the 6 previously listed + 7 newly-wired fields (AC-09 / WI-8).
     */
    public static function isProposed(string $name): bool
    {
        $proposed = [
            // Pre-existing proposed fields (6)
            'needs_summer_shade',
            'irrigation_type',
            'root_depth_class',
            'unit_size',
            'sale_unit',
            'drip_lines_per_bed',
            // WP-CB-MIG2 newly-wired proposed fields (7)
            'seeder_settings',
            'common_pests',
            'foliar_feeding_program',
            'labor_rate_harvest',
            'labor_rate_wash',
            'plantings_per_season',
            'harvest_weeks_span',
        ];
        return in_array(self::resolve($name), $proposed, true)
            || in_array($name, $proposed, true);
    }

    /**
     * Return all canonical names and their labels (for building registries).
     *
     * @return array<string, array{0:string,1:string}>
     */
    public static function allLabels(): array
    {
        $out = [];
        foreach (self::LABELS as $k => $v) {
            $out[$k] = [$v[0], $v[1]];
        }
        return $out;
    }

    /**
     * Enum-value → Hebrew label map.
     * Keyed by canonical field name → [raw_value => hebrew_label].
     *
     * Source of truth: book_entry.php lines ~168,177 (the existing
     * filter-bar select options) plus sensible Hebrew for all other
     * coded enums exposed in crop pages.
     *
     * @var array<string, array<string,string>>
     */
    private const ENUM_LABELS = [
        // planting_method (AC: direct_seed→זריעה ישירה, transplant→שתיל, both→שניהם)
        'planting_method' => [
            'direct_seed' => 'זריעה ישירה',
            'transplant'  => 'שתיל',
            'both'        => 'שניהם',
            'direct'      => 'זריעה ישירה',
        ],
        // frost_tolerance_class (AC: hardy/half_hardy/tender/very_tender)
        'frost_tolerance_class' => [
            'hardy'       => 'עמיד',
            'half_hardy'  => 'חצי-עמיד',
            'tender'      => 'רגיש',
            'very_tender' => 'רגיש מאוד',
        ],
        // frost_tolerance — alias to same map
        'frost_tolerance' => [
            'hardy'       => 'עמיד',
            'half_hardy'  => 'חצי-עמיד',
            'tender'      => 'רגיש',
            'very_tender' => 'רגיש מאוד',
        ],
        // irrigation_type
        'irrigation_type' => [
            'drip'      => 'טפטוף',
            'sprinkler' => 'ממטרות',
            'flood'     => 'הצפה',
            'overhead'  => 'מעל-ראש',
            'none'      => 'ללא השקיה',
        ],
        // root_depth_class
        'root_depth_class' => [
            'shallow' => 'רדוד',
            'medium'  => 'בינוני',
            'deep'    => 'עמוק',
        ],
        // needs_summer_shade (boolean-ish or pct string)
        'needs_summer_shade' => [
            'true'  => 'כן',
            'false' => 'לא',
            '0'     => 'לא',
            '1'     => 'כן',
            '30%'   => 'כן — 30%',
            '40%'   => 'כן — 40%',
            '50%'   => 'כן — 50%',
        ],
        // activity_type (calendar)
        'activity_type' => [
            'seed'       => 'זריעה ישירה',
            'transplant' => 'שתילה',
            'sow'        => 'זריעה',
        ],
        // growth_cycle
        'growth_cycle' => [
            'annual'    => 'חד-שנתי',
            'biennial'  => 'דו-שנתי',
            'perennial' => 'רב-שנתי',
        ],
        // category
        'category' => [
            'vegetables'        => 'ירקות',
            'herbs'             => 'עשבי תיבול',
            'fruits'            => 'פירות',
            'legumes'           => 'קטניות',
            'grains'            => 'דגנים',
            'flowers'           => 'פרחים',
            'roots'             => 'שורשים',
            'brassicas'         => 'כרוביים',
            'alliums'           => 'בצליים',
            'cucurbits'         => 'דלועיים',
            'solanums'          => 'סולניים',
            'fruiting_vegetables' => 'ירקות פרי',
            'leafy_greens'      => 'ירוקי עלים',
            'root_vegetables'   => 'ירקות שורש',
            // WI-3 / D-3 additions — proposed defaults, pending team_35 confirm (LOD §4 Q2)
            'legumes_fresh'     => 'קטניות טריות',
            'eggs'              => 'ביצים',
            'baskets'           => 'סלים',
        ],
    ];

    /**
     * Map a stored enum value to its Hebrew label.
     *
     * enumLabel('planting_method', 'direct_seed') → 'זריעה ישירה'
     * enumLabel('frost_tolerance_class', 'half_hardy') → 'חצי-עמיד'
     *
     * Falls back to the raw $value if not mapped (so nothing breaks).
     * Also resolves field aliases before lookup (e.g. frost_tolerance → frost_tolerance_class).
     *
     * @param string $field  any field name (canonical or alias)
     * @param string $value  raw stored value
     * @return string        Hebrew label or original value when not mapped
     */
    public static function enumLabel(string $field, string $value): string
    {
        $canonical = self::resolve($field);
        $map = self::ENUM_LABELS[$canonical] ?? (self::ENUM_LABELS[$field] ?? null);
        if ($map === null) {
            return $value;
        }
        return $map[strtolower($value)] ?? ($map[$value] ?? $value);
    }

    /**
     * Format a numeric value for display: integer when whole, otherwise ≤2 significant
     * decimals, strip trailing zeros. Non-numeric values are returned as-is.
     *
     * Examples:
     *   59.043478 → '59'
     *   30.000000 → '30'
     *    8.000000 → '8'
     *    2.100000 → '2.1'
     *    0.500000 → '0.5'
     *
     * @param mixed $value  the raw stored value
     * @return string       formatted display string
     */
    public static function fmtNumber(mixed $value, string $unit = ''): string
    {
        if ($value === null || $value === '') {
            return (string)$value;
        }
        if (!is_numeric($value)) {
            return (string)$value;
        }
        $f = (float)$value;
        // WI-7 Q3: stored values are per-hectare; display unit is per-dunam (÷10).
        if (strtolower($unit) === 'kg_per_ha') {
            $f = $f / 10.0;
        }
        // Discrete units have no fractional meaning — render as a rounded integer so a
        // computed median like 59.043478 days shows as "59" (Board-A fidelity; LOD §1 D-1).
        if (in_array(strtolower($unit), ['days', 'count'], true)) {
            return (string)(int)round($f);
        }
        // Integer when whole (handles 30.000000, 8.000000, etc.)
        if (fmod($f, 1.0) === 0.0) {
            return (string)(int)$f;
        }
        // ≤2 significant decimal digits, strip trailing zeros.
        // Use 2 decimal places and rtrim trailing zeros + dot.
        $formatted = rtrim(rtrim(number_format($f, 2, '.', ''), '0'), '.');
        return $formatted;
    }

    /**
     * Unit-token → Hebrew label map.
     * Used by value renderers to emit a single Hebrew unit alongside each numeric value.
     *
     * Unknown tokens are returned as-is (never crash).
     * 'count' returns '' (bare number, no unit label).
     *
     * @param string $unit  raw unit token (e.g. 'cm', 'days', 'kg_per_ha')
     * @return string       Hebrew unit string, or '' to omit
     */
    public static function unitLabel(string $unit): string
    {
        // WI-2 / D-2: canonical unit-token → Hebrew map.
        // Cover all units from organic_market_agent/crop_book/canon/field_registry.py.
        // Q3 (kg_per_ha dunam vs hectare): default to ק״ג/הקטר until team_35 confirms
        // that stored values are already per-dunam (avoid silent 10× error — LOD §4 Q3).
        static $MAP = [
            'cm'              => 'ס״מ',
            'days'            => 'ימ׳',
            'weeks'           => 'שבועות',
            'count'           => '',           // omit — bare number
            'kg'              => 'ק״ג',
            'kg_per_bed_m'    => 'ק״ג/מ׳',
            'kg_per_ha'       => 'ק״ג/דונם',
            'kg_per_dunam'    => 'ק״ג/דונם',
            '°C'              => '°C',
            'celsius'         => '°C',
            'pct'             => '%',
            '%'               => '%',
            'pH'              => 'pH',
            'ph'              => 'pH',
            'seeds_per_g'     => 'זרעים/גר׳',
            'seeds/g'         => 'זרעים/גר׳',
            'units_per_hr'    => 'יח׳/שעה',
            'units/hr'        => 'יח׳/שעה',
            'months'          => 'חודשים',
            'g'               => 'גר׳',
            'kg/m'            => 'ק״ג/מ׳',
            'ק״ג/מ׳'          => 'ק״ג/מ׳',
            // WP-FINAL-QA: live market product units (products.unit) — must render Hebrew
            // on the ₪ "בשוק" chip (book index card + crop page). Tokens from the live
            // products table: kg / bunch / unit / basket_{small,medium,large}.
            'bunch'           => 'צרור',
            'unit'            => 'יחידה',
            'each'            => 'יחידה',
            'head'            => 'ראש',
            'bundle'          => 'אגודה',
            'basket'          => 'סל',
            'basket_small'    => 'סל קטן',
            'basket_medium'   => 'סל בינוני',
            'basket_large'    => 'סל גדול',
        ];
        if ($unit === '') {
            return '';
        }
        return $MAP[$unit] ?? $MAP[strtolower($unit)] ?? $unit;
    }
}
