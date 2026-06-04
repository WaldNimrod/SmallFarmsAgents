#!/usr/bin/env node
/**
 * gen_crop_icons.mjs — generate watercolor crop masters via Gemini 2.5 Flash Image ("Nano Banana").
 *
 * Style-anchored: each call sends an EXISTING served master (wc-tomato.png) as a style reference
 * image + a per-crop prompt, so the whole set stays visually consistent with the Devora masters.
 *
 * ZERO npm deps (Node 18+ global fetch). Reads the key from env GEMINI_API_KEY.
 *
 * USAGE:
 *   GEMINI_API_KEY=...  node scripts/gen_crop_icons.mjs            # generate all missing crops
 *   GEMINI_API_KEY=...  node scripts/gen_crop_icons.mjs okra mint  # only these slugs
 *   node scripts/gen_crop_icons.mjs --list                        # print the target list, no API
 *
 * OUTPUT: full-res PNGs → _COMMUNICATION/team_35/SFA-S003-P004-WP-CB-1/CROP_ART_MASTERS/incoming/<slug>_gen.png
 *   Review, promote good ones to masters/wc-<slug>.png, then:
 *     scripts/wc_derivatives.sh           # builds 720px served derivatives → sfa_delivery/public_assets/img/crops/
 *   and add the slug→wc-<slug>.png pair to WC_ART (controller) + $wc_art_map (book_entry.php).
 *
 * MODEL: gemini-2.5-flash-image  (a.k.a. Nano Banana). If the API rejects the model id, try
 *   gemini-2.5-flash-image-preview — print the error body to see the available id.
 */
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const ANCHOR = join(ROOT, 'sfa_delivery/public_assets/img/crops/wc-tomato.png'); // served master = style ref
const OUT_DIR = join(ROOT, '_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-1/CROP_ART_MASTERS/incoming');
const MODEL = process.env.GEMINI_MODEL || 'gemini-2.5-flash-image';

// 43 crops with no watercolor master (slug → display name + optional botanical hint for a clean icon).
const CROPS = {
  'anise-hyssop': 'anise hyssop — upright herb with violet flower spikes and green leaves',
  'artichokes': 'globe artichoke — single green-purple flower bud',
  'arugula': 'arugula / rocket — cluster of lobed green leaves',
  'bay': 'bay laurel — a few glossy dark-green bay leaves',
  'beans-default-pole-climbing': 'pole bean — green climbing bean pods on a vine',
  'blackberry': 'blackberries — a cluster of dark ripe berries with a leaf',
  'cauliflower': 'cauliflower — white head with green leaves',
  'celery': 'celery — bunch of pale-green ribbed stalks with leaves',
  'chickpea': 'chickpea — green pods and a few beige chickpeas',
  'chicory': 'chicory — leafy green head with a blue flower',
  'chinese-lantern': 'chinese lantern — orange papery lantern husk',
  'chives': 'chives — slender green stalks with a purple pompom flower',
  'cilantro': 'cilantro / coriander — bright-green feathery leaves',
  'cress': 'garden cress — tiny round green leaves',
  'edamame': 'edamame — fuzzy green soybean pods',
  'fava-bean': 'fava / broad bean — large green pods',
  'hibiscus': 'roselle hibiscus — red calyx flower',
  'jerusalem-artichokes': 'jerusalem artichoke — knobbly tan tuber',
  'jicama': 'jicama — round tan root bulb',
  'kohlrabi': 'kohlrabi — pale-green bulb with leaf stalks',
  'lemon-balm': 'lemon balm — heart-shaped green herb leaves',
  'lemon-verbena': 'lemon verbena — narrow pointed green leaves',
  'lettuce-salad-mix': 'salad mix — a loose blend of small lettuce leaves',
  'lovage': 'lovage — tall celery-like green leaves',
  'mint': 'mint — a sprig of green mint leaves',
  'new-zealand-spinach': 'New Zealand spinach — thick triangular green leaves',
  'okra': 'okra — green ridged seed pods',
  'oranges': 'orange — a ripe orange with a leaf',
  'pac-choi-bok-choy': 'bok choy / pac choi — white stalks with dark-green leaves',
  'potato': 'potato — a couple of tan potatoes',
  'sage': 'sage — soft grey-green oval herb leaves',
  'sesame': 'sesame — seed pods on a stalk with small leaves',
  'soybean': 'soybean — green soybean pods on a stem',
  'strawberry': 'strawberry — a red strawberry with a green calyx',
  'sunflower': 'sunflower — a single yellow sunflower head',
  'sweet-corn': 'sweet corn — an ear of yellow corn with husk',
  'sweet-potato': 'sweet potato — an orange-tan tuber',
  'tarragon': 'tarragon — slender pointed green herb leaves',
  'thyme': 'thyme — tiny-leaved green herb sprigs',
  'turnips': 'turnip — white-and-purple round root with leaves',
  'watermelon': 'watermelon — a round green-striped melon (whole)',
  'wheat': 'wheat — a few golden wheat stalks with grain heads',
  'winter-squash': 'winter squash — a tan butternut squash',
};

const PROMPT = (desc) =>
  `Generate a botanical watercolor illustration of ${desc}. ` +
  `Match the EXACT style of the attached reference image: loose hand-painted watercolor, ` +
  `soft sage-and-leaf-green palette with natural accent colors, gentle brush texture, ` +
  `a single centered subject on a plain off-white/transparent paper background, no text, no border, ` +
  `no drop shadow, square framing, suitable as a ~512px crop icon.`;

function args() {
  const a = process.argv.slice(2);
  return { list: a.includes('--list'), only: a.filter((x) => !x.startsWith('--')) };
}

async function genOne(slug, desc, anchorB64) {
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent?key=${process.env.GEMINI_API_KEY}`;
  const body = {
    contents: [{ parts: [
      { text: PROMPT(desc) },
      { inline_data: { mime_type: 'image/png', data: anchorB64 } },
    ] }],
    generationConfig: { responseModalities: ['IMAGE'] },
  };
  const res = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  if (!res.ok) throw new Error(`${slug}: HTTP ${res.status} — ${(await res.text()).slice(0, 300)}`);
  const json = await res.json();
  const parts = json?.candidates?.[0]?.content?.parts || [];
  const img = parts.find((p) => p.inline_data?.data || p.inlineData?.data);
  const data = img?.inline_data?.data || img?.inlineData?.data;
  if (!data) throw new Error(`${slug}: no image in response — ${JSON.stringify(json).slice(0, 300)}`);
  const out = join(OUT_DIR, `${slug}_gen.png`);
  writeFileSync(out, Buffer.from(data, 'base64'));
  return out;
}

(async () => {
  const { list, only } = args();
  const targets = (only.length ? only : Object.keys(CROPS)).filter((s) => CROPS[s]);
  if (list) { console.log(targets.join('\n')); console.log(`\n${targets.length} crops`); return; }
  if (!process.env.GEMINI_API_KEY) { console.error('Set GEMINI_API_KEY (get one free at https://aistudio.google.com/apikey)'); process.exit(1); }
  if (!existsSync(ANCHOR)) { console.error(`Style anchor missing: ${ANCHOR}`); process.exit(1); }
  mkdirSync(OUT_DIR, { recursive: true });
  const anchorB64 = readFileSync(ANCHOR).toString('base64');
  let ok = 0, fail = 0;
  for (const slug of targets) {
    try { const out = await genOne(slug, CROPS[slug], anchorB64); console.log(`✓ ${slug} → ${out}`); ok++; }
    catch (e) { console.error(`✗ ${e.message}`); fail++; }
  }
  console.log(`\nDone: ${ok} generated, ${fail} failed → review in incoming/, promote to masters/wc-<slug>.png, run scripts/wc_derivatives.sh, wire slugs.`);
})();
