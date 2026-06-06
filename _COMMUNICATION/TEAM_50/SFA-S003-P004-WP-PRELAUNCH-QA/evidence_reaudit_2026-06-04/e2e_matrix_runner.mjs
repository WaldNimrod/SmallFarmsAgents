#!/usr/bin/env node
/** E2E interaction matrix — acca9b2 cache-bust. */
import { spawn, execSync } from 'node:child_process';
import { mkdirSync, writeFileSync } from 'node:fs';

function findChrome() {
  try {
    const out = execSync(
      `find "${process.env.HOME}/.cache/puppeteer" -name chrome-headless-shell -type f 2>/dev/null | sort -V | tail -1`,
      { encoding: 'utf8' }
    ).trim();
    if (out) return out;
  } catch {}
  return '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
}

const BASE = 'https://sfa.nimrod.bio';
const V = '1780576560';
const OUT = new URL('.', import.meta.url).pathname + 'e2e_matrix/';

const CHECKS = [
  { id: 'shell_logo_href', url: `/crop-book/?v=${V}`, js: `document.querySelector('.sh__mark')?.closest('a')?.getAttribute('href') || document.querySelector('a.sh__mark')?.getAttribute('href')`, expect: '/' },
  { id: 'hub_field_log_disabled', url: `/?v=${V}`, js: `(() => { const t=[...document.querySelectorAll('.modtile')].find(e=>e.textContent.includes('יומן השדה')); return t ? {tag:t.tagName, aria:t.getAttribute('aria-disabled')} : null; })()`, expect: { tag: 'DIV', aria: 'true' } },
  { id: 'crop_entry_card_heights', url: `/crop-book/?v=${V}`, js: `JSON.stringify([...document.querySelectorAll('.cb-paths .mod-card')].map(e=>Math.round(e.getBoundingClientRect().height)))` },
  { id: 'crop_grid_card_width', url: `/crop-book/?v=${V}`, js: `JSON.stringify([...document.querySelectorAll('.cards-grid .crop-card')].slice(0,4).map(e=>Math.round(e.getBoundingClientRect().width)))` },
  { id: 'crop_lettuce_single_h1', url: `/crop-book/lettuce/?depth=simple&v=${V}`, js: `document.querySelectorAll('h1').length`, expect_max: 1 },
  { id: 'market_range_disabled', url: `/market/prd017?v=${V}`, js: `JSON.stringify([...document.querySelectorAll('.rangesel button, .phist__range button, button')].filter(b=>/90|שנה/.test(b.textContent)).map(b=>({t:b.textContent, dis:b.disabled})))` },
  { id: 'calc_export_csv', url: `/calc/?v=${V}`, js: `[...document.querySelectorAll('a')].some(a=>a.href.includes('/calc/export.csv'))`, expect: true },
  { id: 'calc_modcards', url: `/calc/?v=${V}`, js: `({ total: document.querySelectorAll('.modcard').length, live: document.querySelectorAll('[data-calc]').length, spacing: !!document.querySelector('.spacing-viz, .plant-spacing, [data-calc="spacing"]') })` },
  { id: 'search_nomatch_reqinfo', url: `/search?q=zzznomatch190&v=${V}`, js: `document.querySelector('.reqinfo')?.getAttribute('href')`, expect: '/community' },
];

async function runCheck(chrome, port, check) {
  const url = BASE + check.url;
  const t = await (await fetch(`http://127.0.0.1:${port}/json/new?about:blank`, { method: 'PUT' })).json();
  const ws = new WebSocket(t.webSocketDebuggerUrl);
  let id = 0;
  const pend = {};
  ws.addEventListener('message', (e) => {
    const m = JSON.parse(e.data);
    if (m.id && pend[m.id]) pend[m.id](m);
  });
  await new Promise((r) => ws.addEventListener('open', r));
  const send = (method, params = {}) =>
    new Promise((res) => {
      const i = ++id;
      pend[i] = res;
      ws.send(JSON.stringify({ id: i, method, params }));
    });
  await send('Page.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false });
  await send('Page.navigate', { url });
  await new Promise((r) => setTimeout(r, 3500));
  const ev = await send('Runtime.evaluate', { expression: check.js, returnByValue: true, awaitPromise: true });
  let val = ev.result?.result?.value;
  if (typeof val === 'string' && (val.startsWith('{') || val.startsWith('['))) {
    try { val = JSON.parse(val); } catch {}
  }
  ws.close();
  await fetch(`http://127.0.0.1:${port}/json/close/${t.id}`).catch(() => {});

  let pass = true;
  let note = '';
  if (check.expect !== undefined) {
    pass = JSON.stringify(val) === JSON.stringify(check.expect);
    note = `expected ${JSON.stringify(check.expect)} got ${JSON.stringify(val)}`;
  } else if (check.expect_max !== undefined) {
    pass = Number(val) <= check.expect_max;
    note = `h1 count=${val}`;
  } else if (check.id === 'crop_entry_card_heights') {
    const heights = Array.isArray(val) ? val : JSON.parse(String(val || '[]'));
    pass = heights.length === 4 && heights.every((h) => h < 200);
    note = `heights=${JSON.stringify(heights)}`;
  } else if (check.id === 'crop_grid_card_width') {
    const widths = Array.isArray(val) ? val : JSON.parse(String(val || '[]'));
    pass = widths.length >= 3 && widths.every((w) => w >= 140 && w <= 220);
    note = `widths=${JSON.stringify(widths)}`;
  } else if (check.id === 'market_range_disabled') {
    const buttons = Array.isArray(val) ? val : [];
    pass = buttons.some((b) => /90|שנה/.test(b.t) && b.dis);
    note = JSON.stringify(buttons);
  } else if (check.id === 'calc_modcards') {
    pass = val && val.total >= 14 && val.live >= 6;
    note = JSON.stringify(val);
  }
  return { id: check.id, pass, note, val };
}

async function main() {
  const chrome = findChrome();
  const port = 9150 + Math.floor((Date.now() % 200));
  const proc = spawn(chrome, ['--headless', '--disable-gpu', '--no-sandbox', `--remote-debugging-port=${port}`], { stdio: 'ignore' });
  await new Promise((r) => setTimeout(r, 1800));
  const rows = [];
  try {
    for (const ch of CHECKS) rows.push(await runCheck(chrome, port, ch));
  } finally {
    proc.kill();
  }
  mkdirSync(OUT, { recursive: true });
  const summary = { ts: new Date().toISOString(), v: V, failures: rows.filter((r) => !r.pass).map((r) => r.id), rows };
  writeFileSync(OUT + 'e2e_matrix_cdp.json', JSON.stringify(summary, null, 2));
  console.log(JSON.stringify(summary, null, 2));
}

main().catch((e) => {
  console.error(e);
  process.exit(2);
});
