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
// Devora style references — radish is PRIMARY (per IMAGEPROMPT brief / PROMPT_SERIES_v1). Attach all.
const REFS = [
  'sfa_delivery/public_assets/img/crops/wc-radish.png',   // primary
  'sfa_delivery/public_assets/img/crops/wc-lettuce.png',
  'sfa_delivery/public_assets/img/crops/wc-dill.png',
  'sfa_delivery/public_assets/img/crops/wc-parsley.png',
].map((p) => join(ROOT, p));
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

// Authoritative Devora style (IMAGEPROMPT_wc-tomato-cucumber + PROMPT_SERIES_v1 standing rules).
// NOTE: if the Gemini session returns a refined recipe (REQUEST_TO_GEMINI_crop-icon-recipe), replace this.
const PROMPT = (desc) =>
  `Real watercolor study of ${desc}, on cream paper (#f5f3ec). ` +
  `Washed olive-green (#6a8a3a), earth-brown (#5b483a) and tan-orange (#c46a3e) pigment, ` +
  `dusty teal (#2d8a8c) sparingly; warm-brown faint hand-drawn line, undefined feathered edges, ` +
  `visible paper texture and pigment pooling, a faint pencil under-drawing showing. ` +
  `Loose, gentle, semi-abstract, off-center with quiet empty paper around it. Hand-painted, slightly imperfect. ` +
  `NO text, no numbers, no logo, no outline-clean vector, no digital gradient, no glossy look, no drop shadow, ` +
  `not symmetrical, NO BRIGHT RED (any red stays tan-red #c46a3e). ` +
  `Match the wash, palette, paper texture and pencil/ink line of the attached reference images — ` +
  `especially the radishes. Same hand, same paper. PNG with transparent/near-cream ground, square framing.`;

function args() {
  const a = process.argv.slice(2);
  return { list: a.includes('--list'), only: a.filter((x) => !x.startsWith('--')) };
}

async function genOne(slug, desc, refsB64) {
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent?key=${process.env.GEMINI_API_KEY}`;
  const body = {
    contents: [{ parts: [
      { text: PROMPT(desc) },
      ...refsB64.map((data) => ({ inline_data: { mime_type: 'image/png', data } })),
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
  const refs = REFS.filter((p) => existsSync(p));
  if (!refs.length) { console.error(`No Devora reference images found under ${REFS[0]}`); process.exit(1); }
  mkdirSync(OUT_DIR, { recursive: true });
  const refsB64 = refs.map((p) => readFileSync(p).toString('base64'));
  console.log(`Refs attached: ${refs.length} (primary: ${refs[0].split('/').pop()})  ·  model: ${MODEL}`);
  let ok = 0, fail = 0;
  for (const slug of targets) {
    try { const out = await genOne(slug, CROPS[slug], refsB64); console.log(`✓ ${slug} → ${out}`); ok++; }
    catch (e) { console.error(`✗ ${e.message}`); fail++; }
  }
  console.log(`\nDone: ${ok} generated, ${fail} failed → review in incoming/, promote to masters/wc-<slug>.png, run scripts/wc_derivatives.sh, wire slugs.`);
})();
