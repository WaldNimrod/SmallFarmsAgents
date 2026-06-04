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

// 43 crops with no watercolor master. {SUBJECT} lines verbatim from the Devora session recipe (API v1.0.0).
const CROPS = {
  'anise-hyssop': 'flowering anise hyssop spires with purple watercolor blooms',
  'artichokes': 'two artichoke globes with open scales and thistle details',
  'arugula': 'jagged arugula (rocket) leaves in a loose wash',
  'bay': 'a small branch of laurel bay leaves, single and clustered',
  'beans-default-pole-climbing': 'climbing pole beans with pods and tendrils wrapping a support line',
  'blackberry': 'a bramble branch with ripening blackberries and thorny leaves',
  'cauliflower': 'a dense cauliflower head partially shaded by its green outer leaves',
  'celery': 'ribbed celery stalks rising from a base with bushy pale green leaves',
  'chickpea': 'a chickpea plant section showing pods, fine leaves, and small flowers',
  'chicory': 'blue chicory flowers on thin stems with basal leaves',
  'chinese-lantern': 'papery orange-red calyxes of a chinese lantern plant on a thin stem',
  'chives': 'chive leaves and purple flowering globes with thin stalks',
  'cilantro': 'delicate, feathery cilantro leaves and thin stems',
  'cress': 'small cress leaves on delicate stems in a clump',
  'edamame': 'green edamame (soybean) pods clustered on a stem with leaves',
  'fava-bean': 'large fava bean pods, some whole and one open revealing beans inside',
  'hibiscus': 'a single, large hibiscus flower with natural, earthy tan-red petals and stamens',
  'jerusalem-artichokes': 'knobby jerusalem artichoke tubers with thin roots and plant base',
  'jicama': 'a large jicama root, whole, showing its distinct smooth skin and texture',
  'kohlrabi': 'kohlrabi bulbs, one purple and one green, with leaves rising from the top',
  'lemon-balm': 'crinkled lemon balm leaves in a loose cluster',
  'lemon-verbena': 'long, pointed lemon verbena leaves on a slight stem',
  'lettuce-salad-mix': 'a loose, varied mixture of diverse salad lettuce leaves and textures',
  'lovage': 'upright lovage stalks and jagged green leaves',
  'mint': 'vibrant, loosely washed mint leaves on square stems',
  'new-zealand-spinach': 'fleshy, triangular leaves of new zealand spinach spreading on a vine',
  'okra': 'okra pods and a single hibiscus-like cream flower with a dark center',
  'oranges': 'two oranges with natural, muted rinds, one with a leaf attached',
  'pac-choi-bok-choy': 'pac choi with white stems and dark green spoon-shaped leaves',
  'potato': 'potato tubers, whole, as a biological study with fine roots',
  'sage': 'a small cluster of woody stems with fuzzy, oblong sage leaves',
  'sesame': 'a sesame plant section showing leaf axils and upright seed pods',
  'soybean': 'a mature soybean plant stalk with small pods and leaves',
  'strawberry': 'strawberries on a vine, showing natural, earthy red fruit and flowers',
  'sunflower': 'a sunflower head with muted yellow petals and a textured brown seed center',
  'sweet-corn': 'ears of sweet corn with some husks removed, showing irregular kernels',
  'sweet-potato': 'long sweet potato tubers, whole, with a piece of trailing vine',
  'tarragon': 'elegant, simple leaves on the thin stems of French tarragon',
  'thyme': 'small, woody thyme branches with tiny, dense leaves',
  'turnips': 'turnips, one white with a purple top, showing natural roots and leaves',
  'watermelon': 'a whole, round watermelon with natural, muted green stripes',
  'wheat': 'several heads of mature, golden wheat with awns and leaves',
  'winter-squash': 'a variety of winter squashes, whole, with natural rinds and stems',
};

// Devora Series Icon Recipe (API v1.0.0) — verbatim prompt template from the originating Gemini session.
// Drift fixes baked in: floating subject, 35-45% frame area, off-center, feathered edges, no border/fill.
const PROMPT = (subject) =>
  `A solitary, off-center biological watercolor study of ${subject}, rendered on a raw, textured cream ` +
  `watercolor paper surface. The style is loose, observational, and semi-abstract, with transparent, ` +
  `wet-on-wet washes bleeding into feathered, undefined edges that fade to nothing into the paper. The palette ` +
  `is muted and natural, prioritizing olive greens, earth browns, tan-oranges, and dusty teals, strictly ` +
  `avoiding pure bright reds or synthetic pigments. Visible granulation and water blooms are present. The ` +
  `composition must have significant quiet, empty space; the subject is small (occupying only 35–45% of the ` +
  `frame area) and placed away from the dead center, floating in paper with no hard rectangular edges, frames, ` +
  `borders, or filled background colors — all painted edges fade completely to blank nothingness so the image ` +
  `composites cleanly under multiply. Subtle, light pencil under-drawing is occasionally visible. Lighting is ` +
  `soft, ambient daylight. NO bright primary red (any red stays earth/tan-red #c46a3e), NO centering, NO ` +
  `filling the frame, NO text, NO logos, NO 3D, NO vector, NO glossy finish, NO drop shadow, NO solid ` +
  `background, NO borders. Match the loose feathering, granulation, earthy palette and pencil line of the ` +
  `attached Devora reference images — especially the radishes. Same hand, same paper.`;

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
    // Recipe §5: 1:1 square (other ratios encourage frame-filling/centering); low temp = faithful to refs.
    generationConfig: { responseModalities: ['IMAGE'], temperature: 0.3, imageConfig: { aspectRatio: '1:1' } },
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
