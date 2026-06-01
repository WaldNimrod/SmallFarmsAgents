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
        'nutrient_removal_n_kg_per_ha' => ['צריכת חנקן (N)', 'כמות החנקן שהגידול מוציא, ק״ג להקטר.', 'EN'],
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
}
