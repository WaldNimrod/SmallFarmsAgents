---
id: MEDIA_PROMPT_crop_icons_SFA-S003-P002-WP-UI-patch02_v1.0.0
from: team_100 (Chief System Architect / design support)
date: 2026-05-29
type: generation_prompts
wp: SFA-S003-P002-WP-UI-patch02 (Per-crop watercolor icons)
pipeline: External — team_00 runs these in the ChatGPT/Devora watercolor session
---

# Media Prompts — Per-Crop Watercolor Icons (70 crops)

## Shared style spec (all 70 icons)

| Field | Value |
|-------|-------|
| Dimensions | **512 × 512** (square icon slot; export as 400×400 WebP for `crops.icon_url`) |
| Format | WebP, sRGB, quality 80, target **≤50 KB each** |
| Text | **NONE inside image** — crop name is rendered by HTML |
| Background | **Transparent OR cream paper wash** (#f5f3ec) — flat or very light paper texture only |
| Style | Devora-line watercolor — loose transparent washes, visible pigment granulation, hand-drawn ink/pencil contour, authentic painted-on-paper feel |
| Subject | Single centered botanical specimen, botanically recognizable, icon-scale composition with ~10% clear margin on all edges |
| Forbidden | No text/numbers, no photographs, no 3D, no drop shadows, no vector-flat, no glossy AI-watercolor, no backgrounds with other objects |

**Master palette (from brand anchors):**
- Cream paper: `#f5f3ec`
- Earth brown (contours): `#5b483a`
- Olive green (leaves, plant body): `#6a8a3a`
- Tan-orange (roots, soil-tones): `#c46a3e`
- SFA leaf green: `#6f8a45` (deep `#4d6a2c`)
- SFA tomato: `#c24f2c` (deep `#8e3018`)
- SFA sun: `#d39a32`
- Dusty teal (water, air — sparingly): `#2d8a8c`

**Style anchors for this session (upload to ChatGPT project before generating):**
- `source_masters/watercolor_illustrations/radishes.png` — PRIMARY; match wash softness, paper grain, restraint
- `source_masters/watercolor_illustrations/lettuce.png` — leaf wash reference
- `source_masters/watercolor_illustrations/dill.png` — herb/fine-stem reference
- Brand logo basket — palette + ink-line reference

**Technical suffix (append to every prompt):**
`Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.`

---

## Prompt list — 70 crops

Format: `slug | name_he | name_en | <full generation prompt>`

---

### VEGETABLES (48)

1. `artichokes` | `ארטישוק` | `Artichokes` | Single artichoke head with two or three outer leaves, hand-painted in loose transparent watercolor washes. The layered, overlapping bracts rendered in muted olive green (#6a8a3a) and blue-grey, with visible pigment pooling darker at petal edges. Fine ink contour lines, warm earth-brown (#5b483a) accents on stem base. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

2. `arugula` | `רוקט` | `Arugula` | A small cluster of arugula leaves — deeply lobed, pointy edges — painted in loose watercolor in medium olive green (#6a8a3a) with slight yellow-green variation. Transparent washes show paper grain; fine pencil/ink contour hints at the characteristic leaf notches. One or two leaves slightly overlapping for natural feel. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

3. `beans` | `שעועית` | `Beans` | Two or three climbing bean pods hanging from a short stem, painted in warm leaf-green (#6f8a45) watercolor washes. The pods are plump and slightly curved; visible seed bumps inside. A small tendril curl in fine ink linework. Pigment granulation and paper texture visible. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

4. `beets` | `סלק` | `Beets` | One round beet root in deep crimson-purple watercolor wash with visible concentric bleed rings in the paint, taproot below, two or three leaves emerging from the top in olive green (#6a8a3a). Authentic loose washes, pigment pooling at edges. Earth-brown ink contour lines. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

5. `broccoli` | `ברוקולי` | `Broccoli` | A single broccoli head with tight florets painted in deep blue-green and olive green (#6a8a3a, #4d6a2c) watercolor washes, pale chunky stalk below. Loose, granular wash texture gives the floret cluster an organic, painted appearance. Fine ink contour at the stalk. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

6. `cabbage` | `כרוב` | `Cabbage` | A round cabbage head — outer leaves loosely wrapping a compact sphere — painted in cool blue-green and pale grey-green watercolor washes. The veined outer leaves show transparent layering; pigment pools at folded leaf edges. Earth-brown (#5b483a) fine ink contour. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

7. `carrots` | `גזר` | `Carrots` | Two carrots with lacy green tops, painted in warm tan-orange (#c46a3e) watercolor — one slightly in front of the other. The roots taper naturally; feathery carrot tops in olive green (#6a8a3a) with fine ink linework. Visible pigment granulation and paper wash. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

8. `cauliflower` | `כרובית` | `Cauliflower` | A single cauliflower head with off-white curd and pale green outer leaves loosely framing it. The curds painted in soft cream and warm grey watercolor washes with granulation; leaves in muted olive green (#6a8a3a). Fine pencil/ink contour at leaf edges. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

9. `celery` | `סלרי` | `Celery` | A small bunch of celery stalks with leafy tops — pale green ribbed stalks and fine feathery leaf clusters. Painted in pale and medium leaf-green (#6f8a45) watercolor washes with natural transparency; ink contour lines hint at the ribbed stalk texture. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

10. `chard` | `מנגולד` | `Chard` | Two or three chard leaves with bold stems — one red-stemmed, one yellow-stemmed — painted in loose watercolor. Stem in warm red or sun yellow (#d39a32); leaf blade in deep olive green (#4d6a2c) with transparent vein washes. Authentic pigment bleed at stem-to-blade junction. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

11. `chickpea` | `חומוס` | `Chickpea` | A small branch of chickpea plant: short feathery pinnate leaves and one or two round chickpea pods, each with a small beak tip. Painted in muted olive green (#6a8a3a) and pale tan (#c46a3e) watercolor washes. Fine ink contour, delicate and botanical in feel. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

12. `chicory` | `עולש` | `Chicory` | A compact chicory head (Belgian endive style): pale yellow-white tightly furled leaves with yellow-green tips, painted in soft cream and pale olive watercolor washes. The leaf layers show transparent overlapping washes; fine ink contour at leaf edges. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

13. `chinese-lantern` | `פיסאליס` | `Chinese Lantern` | A single Chinese Lantern (physalis) with its papery orange husk lantern, one husk slightly open revealing the round berry inside. Painted in warm tan-orange (#c46a3e) and sun yellow (#d39a32) watercolor washes on a fine ink skeleton. The translucent husk veining shown through transparent wash layers. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

14. `cress` | `גרגיר הנחלים` | `Cress` | A small mound of garden cress — tiny round leaves on slender stems, the characteristic peppery micro-herb look. Painted in fresh light green and medium olive green (#6f8a45) watercolor washes, with delicate fine-line ink stems. Soft, feathery cluster composition. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

15. `cucumbers` | `מלפפון` | `Cucumbers` | One full cucumber and a cut cross-section beside it. The whole cucumber painted in mid-green watercolor with slight ridged texture and tiny watercolor speckles for the bumpy skin. The cross-section shows pale green flesh with seed pockets in cream. Fine ink contour. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

16. `edamame` | `אדמאמה` | `Edamame` | A small branch with two or three plump edamame pods, slightly fuzzy-surfaced, in bright mid-green (#6f8a45) watercolor. One pod partially open or showing seed bumps. Fine ink contour lines follow the pod curves; soft leaf-green washes. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

17. `eggplant` | `חציל` | `Eggplant` | A single glossy eggplant — deep purple-brown watercolor wash with a subtle sheen implied by leaving a thin warm highlight area. The star-shaped green calyx painted in olive green (#6a8a3a) with ink linework. Pigment pools dark at bottom. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

18. `fava-bean` | `פול` | `Fava Bean` | Two plump fava bean pods, one split open to show the pale jade-green beans inside. Pods painted in muted leaf-green (#6f8a45) watercolor washes; interior cream-colored with soft green beans. Fine ink contour, visible paper grain. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

19. `fennel` | `שמר` | `Fennel` | A fennel bulb with feathery fronds rising above: the round white-green bulb painted in pale cream and soft green (#6f8a45) washes, the feathery tops in delicate fine-line olive green. The layered bulb sheath structure visible through transparent washes. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

20. `garlic` | `שום` | `Garlic` | A whole garlic bulb with papery wrapper layers and a short stem stub, one clove separated and resting beside it. Painted in soft cream and warm tan watercolor washes; the papery skin texture suggested by dry-brush and granulation effects. Earth-brown (#5b483a) ink contour. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

21. `ginger` | `זנגביל` | `Ginger` | A ginger root — the knobbly, irregular rhizome — painted in warm tan-cream watercolor (#c46a3e, pale) with bumpy surface texture implied by layered washes and dry-brush marks. A short fresh green sprout emerging from one node in olive green (#6a8a3a). Earth-brown ink contour. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

22. `jerusalem-artichokes` | `טופינמבור` | `Jerusalem Artichokes` | A cluster of two or three Jerusalem artichoke tubers — knobbly, elongated — in warm tan watercolor (#c46a3e) washes. The irregular bumpy forms rendered with layered washes and dry-brush texture. One small green leaf sprout on top. Fine earth-brown ink contour. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

23. `jicama` | `יחמה` | `Jicama` | A single jicama root — round, slightly flattened disc shape with tan papery skin and a short taproot — painted in warm cream and tan watercolor washes (#c46a3e, pale). Cross-section circle beside it showing crisp white flesh. The papery skin texture suggested by granular dry-brush wash. Earth-brown ink contour. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

24. `kale` | `קייל` | `Kale` | Two or three ruffled kale leaves — deeply crinkled, curly edges — painted in rich deep green (#4d6a2c) and olive green (#6a8a3a) watercolor washes with blue-green undertones. The curly leaf texture shown through layered transparent washes. Fine ink contour follows the ruffled edge. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

25. `kohlrabi` | `קולרבי` | `Kohlrabi` | A kohlrabi bulb — the swollen stem sphere with a few leaf stems radiating outward. Painted in pale blue-green or purple watercolor wash (two varieties present; use pale purple-grey or pale green). The smooth globe shows subtle wash gradation; leaf stems in olive green. Fine ink contour. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

26. `leeks` | `כרישה` | `Leeks` | Two leeks with white-to-light-green gradient from root to dark green tops. Painted in pale cream (root end) through olive green (#6a8a3a) (leaf ends) watercolor wash. The strappy flat leaves shown in loose ink lines; fine root tendrils at the base. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

27. `lettuce` | `חסה` | `Lettuce` | A fresh lettuce head — loose rosette of tender leaves — painted in light leaf-green (#6f8a45) and pale yellow-green watercolor washes. The overlapping leaves show transparent layering; soft rounded edges with slightly ruffled tips. Fine pencil/ink contour at leaf edges. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

28. `melons` | `מלון` | `Melons` | A whole melon with netted skin (cantaloupe type) and a wedge cut away revealing orange-yellow flesh and seeds inside. The skin painted in warm tan-cream (#c46a3e, pale) with fine netted texture from dry-brush; flesh in warm sun (#d39a32) and cream washes. Fine ink contour. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

29. `nz-spinach` | `תרד ניו זילנד` | `NZ Spinach` | A small branch of New Zealand spinach: thick, slightly succulent-looking triangular leaves on a short stem. Painted in mid-green watercolor (#6f8a45) washes with slightly waxy/thick quality to the wash. Fine ink contour with a hint of leaf surface texture. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

30. `okra` | `במיה` | `Okra` | One or two okra pods — the elongated, ridged, tapering pod — painted in medium olive green (#6a8a3a) watercolor with ribbed texture suggested by layered washes along the five ridges. A short stem stub in earth brown. Fine ink contour follows the tapering pod shape. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

31. `onions` | `בצל` | `Onions` | One whole onion with papery outer skin and a short dried stem, plus a small shallot or green sprout beside it. Painted in warm tan and pale gold watercolor washes with papery skin texture from dry-brush granulation. Earth-brown ink contour. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

32. `pac-choi` | `פאק צ׳וי` | `Pac Choi` | A pac choi (bok choy) head — broad white-green stalks fanning out with wide dark green leaf blades. Painted in pale cream-white (stalks, #f5f3ec tint) and deep olive green (#4d6a2c) watercolor washes. The stalk-to-blade transition shows transparent overlapping washes. Fine ink contour. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

33. `peas` | `אפונה` | `Peas` | A pea vine spray: two or three plump pea pods, one open showing bright green peas inside, with a curling tendril and small leaflets. Painted in mid-to-bright leaf-green (#6f8a45) watercolor washes; pea spheres inside in slightly lighter green with warm highlight. Fine ink linework for tendril. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

34. `peppers` | `פלפל` | `Peppers` | One whole bell pepper — slightly irregular, with a short stem and calyx — painted in warm tomato red (#c24f2c) or sun-yellow (#d39a32) watercolor wash (choose one warm hue). The pepper's facets and slight highlights shown through varied wash density. Olive green calyx in ink. Fine ink contour. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

35. `potato` | `תפוח אדמה` | `Potato` | Two potato tubers of slightly different shapes — knobby, oval — painted in pale tan and earth-brown (#c46a3e, pale) watercolor washes. The eye-spots on the skin suggested by small ink dots. One small green sprout at an eye. Granular, dry-brush surface texture. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

36. `radishes` | `צנון` | `Radishes` | Two radishes with leafy green tops — round, bright red-crimson roots with white tips — painted in loose watercolor wash matching the brand Devora anchor (radishes.png PRIMARY). Crimson-red (#c24f2c) root, white tip where pigment thins, olive green leaf tops. Authentic paper grain, granulation, transparent layers. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

37. `salad-mix` | `מיקס סלט` | `Salad Mix` | A loose casual arrangement of mixed salad greens — small leaf shapes of varied greens, reds, and bronze — painted in a light watercolor wash. Leaf shapes include small rounded, lobed, and pointy forms in pale green, olive, and russet-red tones. Relaxed, scattered composition suggesting fresh mixed leaves. Fine ink contour. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

38. `scallions` | `עירית ירוקה` | `Scallions` | A small bunch of three or four scallions tied loosely — the white bulb ends at the bottom, long green tubular tops extending upward. Painted in pale cream-white (bulb ends) through medium leaf-green (#6f8a45) watercolor. Thin ink contour lines follow each scallion stalk. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

39. `soybean` | `סויה` | `Soybean` | A short soybean branch with two or three fuzzy pods and a small pinnate leaf. Pods in pale green (#6f8a45) watercolor with a subtle fuzz texture from dry-brush. Small ink-outlined bean shapes show through the pod walls. Botanical, delicate composition. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

40. `spinach` | `תרד` | `Spinach` | Three or four spinach leaves — oval, dark green with light veins — painted in deep olive green (#4d6a2c) watercolor washes. The veining left lighter by wet-on-wet technique; slight surface sheen implied by wash gradation. Fine ink contour follows the leaf outline. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

41. `summer-squash` | `קישוא` | `Summer Squash` | One summer squash (zucchini-type) — elongated, mid-green with faint lighter stripe — and a small yellow pattypan beside it. Zucchini painted in mid-green (#6f8a45) washes with subtle stripe in lighter green; pattypan in sun yellow (#d39a32). Fine ink contour. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

42. `sunflower` | `חמנייה` | `Sunflower` | A single sunflower head — large round dark-brown seeded center disc surrounded by bright yellow petals — painted in warm sun (#d39a32) and earth-brown (#5b483a) watercolor washes. The petals show transparent layering with pigment pooling at base. A short stem with one leaf stub below. Fine ink contour. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

43. `sweet-corn` | `תירס` | `Sweet Corn` | An ear of sweet corn with husk partially peeled back to reveal golden yellow kernels. Husk painted in pale leaf-green (#6f8a45) washes; kernels in warm sun yellow (#d39a32) watercolor with individual kernel texture suggested by small rounded wash shapes. Silky tassels in fine ink lines. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

44. `sweet-potato` | `בטטה` | `Sweet Potato` | A single sweet potato — oval, plump, smooth skin in warm tan-to-rose watercolor (#c46a3e, warm rose-tan). The tapered ends and natural skin markings shown through layered washes and dry-brush. A small green leaf sprout at one end. Earth-brown ink contour. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

45. `tomatoes` | `עגבנייה` | `Tomatoes` | Two ripe tomatoes — one whole, one cut in half showing flesh and seeds — painted in the brand tomato red (#c24f2c, deep #8e3018) watercolor wash. The whole tomato's stem-end calyx in olive green (#6a8a3a); the cut half shows cream flesh and seed pockets. Visible pigment granulation and wash layering. Fine ink contour. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

46. `turnips` | `לפת` | `Turnips` | One turnip — round, white-to-purple two-tone root with green leafy top. Root painted in pale cream with a purple-rose watercolor wash at the shoulder; leafy tops in olive green (#6a8a3a). The two-tone root color shown through transparent layering. Fine ink contour. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

47. `wheat` | `חיטה` | `Wheat` | A small sheaf of three wheat stalks with full grain heads, tied loosely. Painted in warm sun-gold (#d39a32) and pale amber watercolor washes. The individual grain seeds in each head shown as small elongated forms. Dried, warm-toned, harvest feeling. Fine ink contour and stalk lines. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

48. `winter-squash` | `דלעת` | `Winter Squash` | A butternut or acorn squash — one whole, plump, with a short dried stem. Painted in warm tan-cream and orange watercolor washes (#c46a3e, warm amber). The squash's characteristic ribbed or smooth shape shown with subtle wash gradation. Fine ink contour. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

---

### HERBS (16)

49. `anise-hyssop` | `איזופ אניס` | `Anise Hyssop` | A short sprig of anise hyssop: a slender upright stem bearing a dense spike of tiny purple-lavender florets at the top, with two or three serrated oval leaves below. Painted in soft lavender-purple watercolor washes (dusty blue-teal undertones, #2d8a8c variant) and olive green (#6a8a3a) leaves. Fine ink contour, delicate botanical feel. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

50. `basil` | `בזיליקום` | `Basil` | A small basil sprig — a central stem with three or four fresh, slightly domed, ovate leaves in bright to medium green (#6f8a45). One leaf showing the slight sheen on its upper surface through a thin, warm-highlight-area in the wash. Fine ink contour follows the rounded leaf margins. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

51. `chives` | `עירית` | `Chives` | A small bundle of chive stems — slender, round, upright, medium green — with one open purple-pink pompom flower at the top of one stalk. Painted in medium olive green (#6a8a3a) thin washes for the hollow stems; the flower in soft lavender-pink. Fine ink line per stem, loose and botanical. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

52. `cilantro` | `כוסברה` | `Cilantro` | A short cilantro stem with its characteristic lacy, rounded, divided leaves and a tiny flat-topped flower cluster (umbel) at the tip. Painted in fresh light green (#6f8a45) watercolor; the intricate leaf lobes rendered with fine ink lines and loose wash. Delicate, airy composition. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

53. `dill` | `שמיר` | `Dill` | A dill sprig with delicate feathery needle-leaves and a small flat umbel at top, closely matching the Devora dill.png style anchor. Painted in fine-line olive green (#6a8a3a) washes — the feathery fronds rendered with dry-brush and fine ink marks, the umbel in pale cream-yellow. Light, airy, botanical. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

54. `hibiscus` | `היביסקוס` | `Hibiscus` | A single open hibiscus flower — five broad, slightly crumpled petals in deep rose-red or crimson watercolor wash (#c24f2c, wine-deep variant) with a prominent central stamen column. The petals show transparent layering and pigment bleeding at petal bases. A leaf or two below in olive green. Fine ink contour. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

55. `lemon-balm` | `מליסה` | `Lemon Balm` | A short lemon balm sprig with three or four crinkled, rounded, toothed leaves on a square stem. Painted in medium olive green (#6a8a3a) watercolor with slight yellow-green tint in the lighter areas. The leaf surface's textured appearance suggested by layered washes and fine veining in ink. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

56. `lemon-verbena` | `לואיזה` | `Lemon Verbena` | A lemon verbena sprig — narrow, pointed, slightly rough-textured leaves in whorls of three, a slender upright stem. Painted in fresh light olive green (#6f8a45) watercolor; the lance-shaped leaves show slight surface texture through layered washes. Fine ink contour follows the tapered leaf tips. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

57. `lovage` | `לבגה` | `Lovage` | A short lovage sprig — deeply divided, celery-like glossy dark green leaves on hollow stems. Painted in deep olive green (#4d6a2c) with ink contour lines emphasizing the leaf division. The leaf surface has a slight polish/sheen shown by leaving a thin lighter area in the wash. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

58. `mint` | `נענע` | `Mint` | A mint sprig — a central stem with pairs of rounded, serrated leaves in bright medium green (#6f8a45), the leaf surface slightly wrinkled. Painted in fresh mid-green watercolor washes with fine ink contour; one leaf slightly curled to add interest. The characteristic mint leaf texture shown through layered washes. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

59. `parsley` | `פטרוזיליה` | `Parsley` | A small parsley bunch — curly or flat-leaf variety — with three or four stems, closely matching the Devora parsley.png style anchor. Painted in medium-to-deep olive green (#6a8a3a, #4d6a2c) watercolor; the curly or pinnate leaflets rendered with loose ink marks and granular wash. Natural, botanical, no stiffness. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

60. `sage` | `מרווה` | `Sage` | A sage sprig with two or three velvety, elongated, grey-green leaves and a short stem. Painted in muted blue-grey-green watercolor washes (cooler olive, dusty teal undertone #2d8a8c, light) to convey the silvery-sage leaf color. The soft, slightly downy leaf surface suggested by soft-edged, granular washes. Fine ink contour. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

61. `sesame` | `שומשום` | `Sesame` | A short sesame plant stem with one or two open trumpet-shaped flowers (pale pink-white) and a small elongated seed pod beside it. Flowers painted in soft cream and pale pink watercolor; pod in warm tan (#c46a3e); leaves in olive green (#6a8a3a). Fine ink contour, botanical illustration feel. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

62. `tarragon` | `טרגון` | `Tarragon` | A tarragon sprig — narrow, lance-shaped, smooth dark green leaves arranged alternately along a slender stem. Painted in medium-to-deep olive green (#4d6a2c) fine washes; the slim, pointed leaves rendered with fine ink contour lines and minimal wash. Elegant, sparse, botanical. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

63. `thyme` | `טימין` | `Thyme` | A small thyme sprig — tiny, oval, grey-green leaves densely packed along wiry stems, with tiny pink-purple florets at the tip. Painted in muted olive-grey green watercolor; tiny ink-dotted flower heads in soft lavender. Compact, fine-textured, botanical. Fine ink contour. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

64. `turmeric` | `כורכום` | `Turmeric` | A turmeric rhizome — orange-fleshed, knobbly, similar to ginger but more compact and vivid orange — painted in warm deep orange (#c46a3e, warm saturated) watercolor wash with irregular knobbly surface. A cross-section disc beside it shows the intensely orange interior in a deeper wash. Fine earth-brown ink contour. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

---

### FRUITS (4)

65. `blackberry` | `פטל שחור` | `Blackberry` | A small blackberry branch with two or three ripe blackberry drupes — deep purple-black, segmented berry clusters — and two or three leaves with serrated edges. The ripe berries painted in deep purple-black watercolor washes (layered to build darkness); green leaves in olive green (#6a8a3a). Fine ink contour. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

66. `cherry-tomato` | `עגבנייה שרי` | `Cherry Tomato` | A small cluster of cherry tomatoes on a vine — four or five round, bright red spheres (#c24f2c) on a thin green vine with small leaves. Painted in the brand tomato red watercolor; the vine and leaves in olive green (#6a8a3a). The ripe tomatoes show visible wash layering with pigment pooling at the base of each sphere. Fine ink contour. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

67. `strawberry` | `תות שדה` | `Strawberry` | Two ripe strawberries with their leafy green calyx caps — one showing the red dimpled surface, one cut in half showing pale interior and seeds. Berries painted in warm red (#c24f2c) with the small seed-dots suggested by fine ink marks; the cut flesh in pale cream-pink. Calyx in olive green (#6a8a3a). Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

68. `watermelon` | `אבטיח` | `Watermelon` | A watermelon wedge showing the classic red-pink interior flesh, black seeds, and striped dark-and-light green rind. The flesh painted in warm pink-red watercolor (#c24f2c, diluted warm rose); seeds as small black ink marks; rind in pale green and deep green stripes. Fresh, summer feel. Fine ink contour. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

---

### FRUIT TREES (2)

69. `bay` | `דפנה` | `Bay` | Two or three bay laurel leaves — elongated oval, slightly leathery, dark glossy green — and a tiny cluster of small cream-colored flower buds. Leaves painted in deep olive green (#4d6a2c) washes with a subtle mid-rib vein left lighter. The slight glossy sheen implied by a thin warm highlight area in the wash. Fine ink contour. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

70. `oranges` | `תפוזים` | `Oranges` | One whole orange and a half-orange beside it showing the segmented interior. The whole orange painted in warm orange watercolor (#c46a3e, bright warm) with slight peel texture suggested by granular wash; the half-orange shows cream-white segments with sun-yellow (#d39a32) flesh. A small leaf with a stem above. Fine ink contour. Transparent background or cream paper wash (#f5f3ec), square 512×512 icon composition, centered specimen with ~10% clear margin, authentic watercolor on paper, no text, no 3D, sRGB.

---

## Coverage checklist — 70/70

| Category | Count | Crops |
|----------|------:|-------|
| Vegetables | 48 | artichokes, arugula, beans, beets, broccoli, cabbage, carrots, cauliflower, celery, chard, chickpea, chicory, chinese-lantern, cress, cucumbers, edamame, eggplant, fava-bean, fennel, garlic, ginger, jerusalem-artichokes, jicama, kale, kohlrabi, leeks, lettuce, melons, nz-spinach, okra, onions, pac-choi, peas, peppers, potato, radishes, salad-mix, scallions, soybean, spinach, summer-squash, sunflower, sweet-corn, sweet-potato, tomatoes, turnips, wheat, winter-squash |
| Herbs | 16 | anise-hyssop, basil, chives, cilantro, dill, hibiscus, lemon-balm, lemon-verbena, lovage, mint, parsley, sage, sesame, tarragon, thyme, turmeric |
| Fruits | 4 | blackberry, cherry-tomato, strawberry, watermelon |
| Fruit Trees | 2 | bay, oranges |
| **TOTAL** | **70** | ✅ 70/70 |

---

## Delivery instructions for team_00 / ChatGPT-Devora session

1. Open the existing ChatGPT project with the Devora watercolor masters uploaded.
2. Upload `source_masters/watercolor_illustrations/radishes.png` as the PRIMARY style anchor (if not already in project).
3. Generate crops in batches of 5–10; calibrate on the first batch (radishes, basil, tomatoes, carrots, dill) before proceeding.
4. For each crop, use the prompt exactly as written + append the shared technical suffix.
5. Output PNGs at 512×512 or larger; export/compress to WebP ≤50 KB for `crops.icon_url`.
6. Save each file as `sfa_delivery/public_assets/img/icons/crops/<slug>.webp`.
