<?php
declare(strict_types=1);

namespace SFA\Lib;

/**
 * CropArt — single source of truth for the crop→watercolor mapping.
 *
 * The watercolor PNGs (public_assets/img/crops/wc-*.png) are the SFA visual
 * identity (team_35 Step-2). This map resolves a crop/product slug to its
 * watercolor file, with singular + plural DB-slug aliases and the
 * WP-CB-UI-FIDELITY identity batch. Returns null for an unmapped slug so
 * callers fall back to the line-glyph icon (honest: never a wrong picture).
 *
 * Used by the crop-book list, the crop page, and (WP-CB-UI-MOCKUP-FIDELITY)
 * the market grid so a product card shows the same watercolor as its crop.
 */
final class CropArt
{
    /** @var array<string,string> slug → wc-*.png filename */
    public const MAP = [
        // ── original singular keys (14 masters) ──────────────────────────────
        'basil'      => 'wc-basil.png',
        'beet'       => 'wc-beet.png',
        'broccoli'   => 'wc-broccoli.png',
        'bush-bean'  => 'wc-bush-bean.png',
        'cabbage'    => 'wc-cabbage.png',
        'carrot'     => 'wc-carrot.png',
        'chard'      => 'wc-chard.png',
        'cucumber'   => 'wc-cucumber.png',
        'dill'       => 'wc-dill.png',
        'eggplant'   => 'wc-eggplant.png',
        'fennel'     => 'wc-fennel.png',
        'garlic'     => 'wc-garlic.png',
        'ginger'     => 'wc-ginger.png',
        'kale'       => 'wc-kale.png',
        'leek'       => 'wc-leek.png',
        'lettuce'    => 'wc-lettuce.png',
        'melon'      => 'wc-melon.png',
        'onion'      => 'wc-onion.png',
        'parsley'    => 'wc-parsley.png',
        'pea'        => 'wc-pea.png',
        'pepper'     => 'wc-pepper.png',
        'pole-bean'  => 'wc-pole-bean.png',
        'radish'     => 'wc-radish.png',
        'scallion'   => 'wc-scallion.png',
        'spinach'    => 'wc-spinach.png',
        'tomato'     => 'wc-tomato.png',
        'turmeric'   => 'wc-turmeric.png',
        'zucchini'   => 'wc-zucchini.png',
        // ── plural DB-slug aliases (patch01 recovery) ────────────────────────
        'carrots'                      => 'wc-carrot.png',
        'tomatoes'                     => 'wc-tomato.png',
        'cucumbers'                    => 'wc-cucumber.png',
        'onions'                       => 'wc-onion.png',
        'peppers'                      => 'wc-pepper.png',
        'peas'                         => 'wc-pea.png',
        'beets'                        => 'wc-beet.png',
        'radishes'                     => 'wc-radish.png',
        'melons'                       => 'wc-melon.png',
        'leeks'                        => 'wc-leek.png',
        'cherry-tomato'                => 'wc-tomato.png',
        'summer-squash'                => 'wc-zucchini.png',
        'onions-scallions'             => 'wc-scallion.png',
        'beans-default-pole-climbing-' => 'wc-pole-bean.png',
        // production DB slugs that were falling back to the line-glyph icon
        'scallions'                    => 'wc-scallion.png',
        'salad-mix'                    => 'wc-lettuce-salad-mix.png',
        'pac-choi'                     => 'wc-pac-choi-bok-choy.png',
        'bush-pole'                    => 'wc-bush-bean.png',
        'corn'                         => 'wc-sweet-corn.png',
        // ── 43 watercolor identity slugs (WP-CB-UI-FIDELITY batch) ──────────
        'anise-hyssop'                => 'wc-anise-hyssop.png',
        'artichokes'                  => 'wc-artichokes.png',
        'arugula'                     => 'wc-arugula.png',
        'bay'                         => 'wc-bay.png',
        'beans-default-pole-climbing' => 'wc-beans-default-pole-climbing.png',
        'blackberry'                  => 'wc-blackberry.png',
        'cauliflower'                 => 'wc-cauliflower.png',
        'celery'                      => 'wc-celery.png',
        'chickpea'                    => 'wc-chickpea.png',
        'chicory'                     => 'wc-chicory.png',
        'chinese-lantern'             => 'wc-chinese-lantern.png',
        'chives'                      => 'wc-chives.png',
        'cilantro'                    => 'wc-cilantro.png',
        'cress'                       => 'wc-cress.png',
        'edamame'                     => 'wc-edamame.png',
        'fava-bean'                   => 'wc-fava-bean.png',
        'hibiscus'                    => 'wc-hibiscus.png',
        'jerusalem-artichokes'        => 'wc-jerusalem-artichokes.png',
        'jicama'                      => 'wc-jicama.png',
        'kohlrabi'                    => 'wc-kohlrabi.png',
        'lemon-balm'                  => 'wc-lemon-balm.png',
        'lemon-verbena'               => 'wc-lemon-verbena.png',
        'lettuce-salad-mix'           => 'wc-lettuce-salad-mix.png',
        'lovage'                      => 'wc-lovage.png',
        'mint'                        => 'wc-mint.png',
        'new-zealand-spinach'         => 'wc-new-zealand-spinach.png',
        'okra'                        => 'wc-okra.png',
        'oranges'                     => 'wc-oranges.png',
        'pac-choi-bok-choy'           => 'wc-pac-choi-bok-choy.png',
        'potato'                      => 'wc-potato.png',
        'sage'                        => 'wc-sage.png',
        'sesame'                      => 'wc-sesame.png',
        'soybean'                     => 'wc-soybean.png',
        'strawberry'                  => 'wc-strawberry.png',
        'sunflower'                   => 'wc-sunflower.png',
        'sweet-corn'                  => 'wc-sweet-corn.png',
        'sweet-potato'                => 'wc-sweet-potato.png',
        'tarragon'                    => 'wc-tarragon.png',
        'thyme'                       => 'wc-thyme.png',
        'turnips'                     => 'wc-turnips.png',
        'watermelon'                  => 'wc-watermelon.png',
        'wheat'                       => 'wc-wheat.png',
        'winter-squash'               => 'wc-winter-squash.png',
    ];

    /** Resolve a slug to its watercolor filename, or null when unmapped. */
    public static function file(string $slug): ?string
    {
        return self::MAP[$slug] ?? null;
    }
}
