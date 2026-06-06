#!/usr/bin/env node
/**
 * Pre-launch CDP deep probe — bbox, console, styles, network (read-only).
 */
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
  for (const p of [
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/usr/bin/chromium',
    '/usr/bin/google-chrome',
  ]) {
    try {
      execSync(`test -x "${p}"`);
      return p;
    } catch {}
  }
  throw new Error('No Chrome binary found');
}

const BASE = 'https://sfa.nimrod.bio';
const OUT = new URL('.', import.meta.url).pathname;
const cfg = JSON.parse(
  readFileSync(OUT + 'prelaunch_qa_probe.json', 'utf8')
);
const VP = { name: 'desktop1440', w: 1440, h: 900 };

const PROBE_JS = `(() => {
  const dir = document.documentElement.dir || document.body?.dir || '';
  const body = document.body;
  const cs = body ? getComputedStyle(body) : null;
  const bg = cs ? cs.backgroundColor : '';
  const ff = cs ? cs.fontFamily : '';
  const offenders = [];
  const sel = ['.sh__mark', '.sh__mark svg', '.cb-paths .mod-card', 'svg use', '.mod-card__art'];
  for (const s of sel) {
    document.querySelectorAll(s).forEach((el, i) => {
      const r = el.getBoundingClientRect();
      if (r.width > innerWidth * 0.55 || r.height > innerHeight * 0.45 || (s.includes('mod-card') && r.height > 220)) {
        offenders.push({ sel: s, i, w: Math.round(r.width), h: Math.round(r.height), tag: el.tagName });
      }
    });
  }
  const visibleText = (body?.innerText || '').slice(0, 50000);
  const leak = ['direct_seed','half_hardy','yield_per_bed_m','family:variety','undefined','[object'].filter(t => visibleText.includes(t));
  const sh = document.querySelector('.sh');
  return JSON.stringify({
    dir, bg, ff,
    sw: document.documentElement.scrollWidth,
    cw: document.documentElement.clientWidth,
    offenders,
    leak,
    shLen: sh ? sh.outerHTML.length : 0,
    shHash: sh ? sh.outerHTML.length + ':' + (sh.querySelector('.sh__mark')?.getBoundingClientRect().width || 0) : 0
  });
})()`;

async function main() {
  const chrome = findChrome();
  const port = 9100 + Math.floor((Date.now() % 500));
  const proc = spawn(chrome, [
    '--headless', '--disable-gpu', '--no-sandbox',
    `--remote-debugging-port=${port}`,
    '--hide-scrollbars',
  ], { stdio: 'ignore' });
  await new Promise((r) => setTimeout(r, 1800));

  const consoleErrors = [];
  const networkFailed = [];
  const results = [];

  try {
    for (const pg of cfg.pages) {
      const url = BASE.replace(/\/$/, '') + pg.path + (pg.path.includes('?') ? '&' : '?') + 'nc=' + Date.now();
      const t = await (await fetch(`http://127.0.0.1:${port}/json/new?about:blank`, { method: 'PUT' })).json();
      const ws = new WebSocket(t.webSocketDebuggerUrl);
      let id = 0;
      const pend = {};
      const pageErrors = [];
      const pageNet = [];
      ws.addEventListener('message', (e) => {
        const m = JSON.parse(e.data);
        if (m.method === 'Log.entryAdded' && m.params?.entry?.level === 'error') {
          pageErrors.push(m.params.entry.text || JSON.stringify(m.params.entry));
        }
        if (m.method === 'Network.loadingFailed') {
          pageNet.push(m.params);
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
      await send('Network.enable');
      await send('Emulation.setDeviceMetricsOverride', {
        width: VP.w,
        height: VP.h,
        deviceScaleFactor: 1,
        mobile: false,
      });
      await send('Page.navigate', { url });
      await new Promise((r) => setTimeout(r, 3500));
      const ev = await send('Runtime.evaluate', { expression: PROBE_JS, returnByValue: true });
      const v = ev.result?.result?.value ? JSON.parse(ev.result.result.value) : null;
      results.push({
        page: pg.name,
        path: pg.path,
        probe: v,
        consoleErrors: [...pageErrors],
        networkFailed: pageNet.map((n) => n.requestId || n.errorText).slice(0, 5),
      });
      consoleErrors.push(...pageErrors.map((e) => ({ page: pg.name, e })));
      networkFailed.push(...pageNet.map((n) => ({ page: pg.name, n })));
      ws.close();
      await fetch(`http://127.0.0.1:${port}/json/close/${t.id}`).catch(() => {});
    }
  } finally {
    proc.kill();
  }

  const summary = {
    ts: new Date().toISOString(),
    viewport: VP,
    pages: results.length,
    overflow_pages: results.filter((r) => r.probe && r.probe.sw > r.probe.cw + 1).map((r) => r.page),
    bbox_offenders: results.filter((r) => r.probe?.offenders?.length).map((r) => ({
      page: r.page,
      offenders: r.probe.offenders,
    })),
    visible_leaks: results.filter((r) => r.probe?.leak?.length).map((r) => ({
      page: r.page,
      leak: r.probe.leak,
    })),
    console_error_pages: [...new Set(consoleErrors.map((x) => x.page))],
    sh_shell_hashes: results.map((r) => ({ page: r.page, shHash: r.probe?.shHash })),
  };

  mkdirSync(OUT + 'cdp_deep', { recursive: true });
  writeFileSync(OUT + 'cdp_deep/cdp_deep_result.json', JSON.stringify({ summary, results, consoleErrors, networkFailed }, null, 2));
  console.log(JSON.stringify(summary, null, 2));
}

main().catch((e) => {
  console.error('FATAL', e);
  process.exit(2);
});
