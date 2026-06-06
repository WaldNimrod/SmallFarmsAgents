#!/usr/bin/env node
/** Re-audit CDP deep probe — acca9b2 @ ?v=1780576560 (production TLS, no cert bypass). */
import { spawn, execSync } from 'node:child_process';
import { mkdirSync, writeFileSync, readFileSync } from 'node:fs';

function findChrome() {
  try {
    const home = process.env.HOME;
    const out = execSync(
      `find "${home}/.cache/puppeteer" -name chrome-headless-shell -type f 2>/dev/null | sort -V | tail -1`,
      { encoding: 'utf8' }
    ).trim();
    if (out) return out;
  } catch {}
  return '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
}

const BASE = 'https://sfa.nimrod.bio';
const V = '1780576560';
const OUT = new URL('.', import.meta.url).pathname;
const cfg = JSON.parse(readFileSync(OUT + 'prelaunch_reaudit_probe.json', 'utf8'));

const VIEWPORTS = [
  { name: 'desktop1440', w: 1440, h: 900, mobile: false },
  { name: 'tablet768', w: 768, h: 900, mobile: true },
  { name: 'mobile375', w: 375, h: 812, mobile: true },
];

const PROBE_JS = `(() => {
  const dir = document.documentElement.dir || document.body?.dir || '';
  const body = document.body;
  const cs = body ? getComputedStyle(body) : null;
  const bg = cs ? cs.backgroundColor : '';
  const offenders = [];
  const sel = ['.sh__mark', '.sh__mark svg', '.cb-paths .mod-card', '.mod-card__art', '.crophero__art img', '.cards-grid .crop-card'];
  for (const s of sel) {
    document.querySelectorAll(s).forEach((el, i) => {
      const r = el.getBoundingClientRect();
      if (r.width > innerWidth * 0.55 || r.height > innerHeight * 0.45 || (s.includes('mod-card') && r.height > 220)) {
        offenders.push({ sel: s, i, w: Math.round(r.width), h: Math.round(r.height), tag: el.tagName });
      }
    });
  }
  const visibleText = (body?.innerText || '').slice(0, 80000);
  const leak = ['direct_seed','half_hardy','yield_per_bed_m','family:variety','undefined','[object',
    'root_vegetables','leafy_greens','legumes_fresh',' cm ',' days ',' weeks ',' count ']
    .filter(t => visibleText.includes(t));
  const engUnits = (visibleText.match(/\\b(cm|days|weeks|count)\\b/g) || []).length;
  const rawDecimals = (visibleText.match(/\\d+\\.\\d{4,}/g) || []).slice(0, 8);
  const h1s = [...document.querySelectorAll('h1')].map(e => e.textContent.trim());
  const cropHeroes = document.querySelectorAll('.crophero').length;
  const wcImgs = document.querySelectorAll('img[src*="wc-"], img.wc-art').length;
  const glyphCards = document.querySelectorAll('.crop-card .crop-glyph, .srch-hit .crop-glyph').length;
  const modcards = document.querySelectorAll('.modcard').length;
  const calcLive = document.querySelectorAll('[data-calc]').length;
  const chips = [...document.querySelectorAll('.mkt-cats button, .mkt-cats a, .chip')].map(e => e.textContent.trim()).slice(0, 12);
  const engChips = chips.filter(t => /[a-z_]{6,}/.test(t));
  return JSON.stringify({
    dir, bg, offenders, leak, engUnits, rawDecimals, h1s, cropHeroes, wcImgs, glyphCards,
    modcards, calcLive, chips: chips.slice(0, 8), engChips,
    sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth
  });
})()`;

async function main() {
  const chrome = findChrome();
  const port = 9200 + Math.floor((Date.now() % 300));
  const proc = spawn(chrome, [
    '--headless', '--disable-gpu', '--no-sandbox',
    `--remote-debugging-port=${port}`,
    '--hide-scrollbars',
  ], { stdio: 'ignore' });
  await new Promise((r) => setTimeout(r, 1800));

  const consoleErrors = [];
  const results = [];

  try {
    for (const vp of VIEWPORTS) {
      for (const pg of cfg.pages) {
        const url = BASE.replace(/\/$/, '') + pg.path;
        const t = await (await fetch(`http://127.0.0.1:${port}/json/new?about:blank`, { method: 'PUT' })).json();
        const ws = new WebSocket(t.webSocketDebuggerUrl);
        let id = 0;
        const pend = {};
        const pageErrors = [];
        ws.addEventListener('message', (e) => {
          const m = JSON.parse(e.data);
          if (m.method === 'Log.entryAdded' && m.params?.entry?.level === 'error') {
            pageErrors.push(m.params.entry.text || JSON.stringify(m.params.entry));
          }
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
        await send('Runtime.enable');
        await send('Log.enable');
        await send('Emulation.setDeviceMetricsOverride', {
          width: vp.w, height: vp.h, deviceScaleFactor: 1, mobile: vp.mobile,
        });
        await send('Page.navigate', { url });
        await new Promise((r) => setTimeout(r, 3500));
        const ev = await send('Runtime.evaluate', { expression: PROBE_JS, returnByValue: true });
        const v = ev.result?.result?.value ? JSON.parse(ev.result.result.value) : null;
        const overflow = v ? v.sw > v.cw + 1 : true;
        results.push({
          viewport: vp.name,
          page: pg.name,
          path: pg.path,
          overflow,
          probe: v,
          consoleErrors: [...pageErrors],
        });
        consoleErrors.push(...pageErrors.map((e) => ({ page: pg.name, vp: vp.name, e })));
        ws.close();
        await fetch(`http://127.0.0.1:${port}/json/close/${t.id}`).catch(() => {});
      }
    }
  } finally {
    proc.kill();
  }

  const entryHeights = results.find((r) => r.page === 'crop-book-entry' && r.viewport === 'desktop1440');
  const summary = {
    ts: new Date().toISOString(),
    live_sha: 'acca9b2',
    served_v: V,
    overflow: results.filter((r) => r.overflow).map((r) => `${r.page}@${r.viewport}`),
    bbox_offenders: results.filter((r) => r.probe?.offenders?.length).map((r) => ({
      page: r.page, vp: r.viewport, offenders: r.probe.offenders,
    })),
    visible_leaks: results.filter((r) => r.probe?.leak?.length).map((r) => ({
      page: r.page, vp: r.viewport, leak: r.probe.leak,
    })),
    eng_units_visible: results.filter((r) => r.probe?.engUnits > 0).map((r) => ({
      page: r.page, vp: r.viewport, count: r.probe.engUnits,
    })),
    raw_decimals: results.filter((r) => r.probe?.rawDecimals?.length).map((r) => ({
      page: r.page, samples: r.probe.rawDecimals,
    })),
    double_h1_crop: results.filter((r) => r.page.startsWith('crop-') && r.probe?.h1s?.length > 1),
    console_error_pages: [...new Set(consoleErrors.map((x) => `${x.page}@${x.vp}`))],
    calc_modules_desktop: results.find((r) => r.page === 'calc' && r.viewport === 'desktop1440')?.probe,
    market_chips: results.find((r) => r.page === 'market-list' && r.viewport === 'desktop1440')?.probe?.chips,
    market_eng_chips: results.find((r) => r.page === 'market-list' && r.viewport === 'desktop1440')?.probe?.engChips,
  };

  mkdirSync(OUT + 'cdp_deep', { recursive: true });
  writeFileSync(OUT + 'cdp_deep/cdp_deep_result.json', JSON.stringify({ summary, results, consoleErrors }, null, 2));
  console.log(JSON.stringify(summary, null, 2));
}

main().catch((e) => {
  console.error('FATAL', e);
  process.exit(2);
});
