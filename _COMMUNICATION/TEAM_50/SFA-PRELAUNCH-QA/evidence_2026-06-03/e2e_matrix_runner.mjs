#!/usr/bin/env node
/** E2E matrix checks via CDP (navigation + DOM probes). */
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
const OUT = new URL('.', import.meta.url).pathname + 'e2e_matrix/';

const CHECKS = [
  {
    id: 'shell_logo_href',
    url: '/crop-book/',
    js: `document.querySelector('.sh__mark')?.closest('a')?.getAttribute('href') || document.querySelector('a.sh__mark')?.getAttribute('href')`,
    expect: '/',
  },
  {
    id: 'hub_field_log_disabled',
    url: '/',
    js: `(() => { const t=[...document.querySelectorAll('.modtile')].find(e=>e.textContent.includes('יומן השדה')); return t ? {tag:t.tagName, aria:t.getAttribute('aria-disabled'), href:t.getAttribute('href')} : null; })()`,
    expect: { tag: 'DIV', aria: 'true' },
  },
  {
    id: 'hub_whatsapp_cta',
    url: '/',
    js: `[...document.querySelectorAll('a')].filter(a=>a.href&&a.href.includes('wa.me')).length`,
    expect_min: 1,
  },
  {
    id: 'crop_entry_card_heights',
    url: '/crop-book/',
    js: `JSON.stringify([...document.querySelectorAll('.cb-paths .mod-card')].map(e=>Math.round(e.getBoundingClientRect().height)))`,
  },
  {
    id: 'market_range_disabled',
    url: '/market/prd017',
    js: `JSON.stringify([...document.querySelectorAll('.rangesel button, .phist__range button, button')].filter(b=>/90|שנה/.test(b.textContent)).map(b=>({t:b.textContent, dis:b.disabled, cls:b.className})))`,
  },
  {
    id: 'search_nomatch_reqinfo_href',
    url: '/search?q=zzznomatch190',
    js: `document.querySelector('.reqinfo')?.getAttribute('href')`,
    expect: '/community',
  },
  {
    id: 'community_footer_aria',
    url: '/community',
    js: `document.querySelector('.sh__foot [aria-current="page"]')?.textContent?.trim() || 'missing'`,
    expect_contains: 'קהילה',
  },
  {
    id: 'calc_export_csv',
    url: '/calc/',
    js: `[...document.querySelectorAll('a')].some(a=>a.href.includes('/calc/export.csv'))`,
    expect: true,
  },
  {
    id: 'calc_modcards',
    url: '/calc/',
    js: `({ total: document.querySelectorAll('.modcard').length, disabled: document.querySelectorAll('.modcard--disabled').length, live: document.querySelectorAll('[data-calc]').length })`,
  },
];

async function runCheck(chrome, port, check) {
  const url = BASE + check.url + '?nc=' + Date.now();
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
  } else if (check.expect_min !== undefined) {
    pass = Number(val) >= check.expect_min;
  } else if (check.expect_contains) {
    pass = String(val).includes(check.expect_contains);
  } else if (check.id === 'crop_entry_card_heights') {
    const heights = Array.isArray(val) ? val : JSON.parse(String(val || '[]'));
    pass = heights.length === 4 && heights.every((h) => h < 200);
    note = `heights=${JSON.stringify(heights)}`;
  } else if (check.id === 'market_range_disabled') {
    const buttons = Array.isArray(val) ? val : [];
    pass = buttons.some((b) => /90|שנה/.test(b.t) && (b.dis || String(b.cls).includes('disabled')));
    note = JSON.stringify(buttons);
  }
  return { id: check.id, url: check.url, pass, val, note };
}

async function main() {
  mkdirSync(OUT, { recursive: true });
  const chrome = findChrome();
  const port = 9200 + Math.floor((Date.now() % 200));
  const proc = spawn(chrome, ['--headless', '--disable-gpu', '--no-sandbox', `--remote-debugging-port=${port}`], { stdio: 'ignore' });
  await new Promise((r) => setTimeout(r, 1800));
  const results = [];
  try {
    for (const c of CHECKS) results.push(await runCheck(chrome, port, c));
  } finally {
    proc.kill();
  }
  writeFileSync(OUT + 'e2e_matrix_cdp.json', JSON.stringify({ results }, null, 2));
  console.log(JSON.stringify(results, null, 2));
}

main().catch((e) => { console.error(e); process.exit(2); });
