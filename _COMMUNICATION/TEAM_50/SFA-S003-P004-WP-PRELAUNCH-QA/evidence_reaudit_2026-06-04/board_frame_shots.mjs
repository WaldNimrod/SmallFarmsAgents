#!/usr/bin/env node
/** Board-A/B frame crops @ 1440 / 768 / 375 for design_pairs/. */
import { spawn, execSync } from 'node:child_process';
import { mkdirSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

function findChrome() {
  try {
    return execSync(`find "${process.env.HOME}/.cache/puppeteer" -name chrome-headless-shell -type f 2>/dev/null | sort -V | tail -1`, { encoding: 'utf8' }).trim();
  } catch {}
  return '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
}

const DESIGN_DIR = join(
  dirname(fileURLToPath(import.meta.url)),
  '../../../../_archive/SFA-S003-P004-WP-CB-UI-CLASSB/team_35/SFA-S003-P004-WP-CB-UI-CLASSB/HANDOFF/design'
);
const LOCAL = 'http://127.0.0.1:8767/';
const OUT = new URL('design_pairs/', import.meta.url).pathname;

const FRAMES = [
  { board: 'Board-A-Book-and-Calculator.html', label: 'book-entry', live: 'crop-book-entry' },
  { board: 'Board-A-Book-and-Calculator.html', label: 'crop-lettuce', live: 'crop-simple' },
  { board: 'Board-A-Book-and-Calculator.html', label: 'calc-page', live: 'calc' },
  { board: 'Board-B-Hub-Market-Search-Community-About-Account.html', label: 'hub-home', live: 'hub' },
  { board: 'Board-B-Hub-Market-Search-Community-About-Account.html', label: 'market-list', live: 'market-list' },
  { board: 'Board-B-Hub-Market-Search-Community-About-Account.html', label: 'market-detail', live: 'market-detail' },
  { board: 'Board-B-Hub-Market-Search-Community-About-Account.html', label: 'search-results', live: 'global-search-hit' },
  { board: 'Board-B-Hub-Market-Search-Community-About-Account.html', label: 'community', live: 'community' },
  { board: 'Board-B-Hub-Market-Search-Community-About-Account.html', label: 'about-tiers', live: 'about' },
  { board: 'Board-B-Hub-Market-Search-Community-About-Account.html', label: 'account', live: 'account' },
];

const VIEWS = [
  { name: 'desktop1440', w: 1440, h: 900, mobile: false },
  { name: 'tablet768', w: 768, h: 900, mobile: true },
  { name: 'mobile375', w: 375, h: 812, mobile: true },
];

async function main() {
  mkdirSync(OUT, { recursive: true });
  const chrome = findChrome();
  const port = 8768;
  const proc = spawn(chrome, ['--headless', '--disable-gpu', '--no-sandbox', `--remote-debugging-port=${port}`, '--hide-scrollbars'], { stdio: 'ignore' });
  await new Promise((r) => setTimeout(r, 1500));
  const manifest = [];
  try {
    for (const fr of FRAMES) {
      for (const vp of VIEWS) {
        const file = `board_${fr.label}_${vp.name}.png`;
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
        await send('Emulation.setDeviceMetricsOverride', { width: vp.w, height: vp.h, deviceScaleFactor: 1, mobile: vp.mobile });
        await send('Page.navigate', { url: LOCAL + fr.board });
        await new Promise((r) => setTimeout(r, 2500));
        await send('Runtime.evaluate', {
          expression: `(() => { const el=document.querySelector('[data-screen-label="${fr.label}"]'); if(el){el.scrollIntoView({block:'center'}); return true;} return false; })()`,
          returnByValue: true,
        });
        await new Promise((r) => setTimeout(r, 800));
        const clip = await send('Runtime.evaluate', {
          expression: `(() => { const el=document.querySelector('[data-screen-label="${fr.label}"]'); if(!el) return null; const r=el.getBoundingClientRect(); return JSON.stringify({x:r.x,y:r.y,width:Math.min(r.width,${vp.w - 20}),height:Math.min(r.height,${vp.h - 40})}); })()`,
          returnByValue: true,
        });
        let clipParams = { x: 0, y: 0, width: Math.min(1200, vp.w), height: Math.min(800, vp.h), scale: 1 };
        try {
          const v = JSON.parse(clip.result?.result?.value || 'null');
          if (v && v.width > 50) clipParams = { x: Math.max(0, v.x), y: Math.max(0, v.y), width: v.width, height: v.height, scale: 1 };
        } catch {}
        const cap = await send('Page.captureScreenshot', { format: 'png', clip: clipParams });
        const path = OUT + file;
        if (cap.result?.data) {
          writeFileSync(path, Buffer.from(cap.result.data, 'base64'));
          manifest.push({
            label: fr.label,
            board: fr.board,
            viewport: vp.name,
            board_path: path,
            live_pair: `../qa_probe/screenshots/${fr.live}_${vp.name}.png`,
          });
        }
        ws.close();
        await fetch(`http://127.0.0.1:${port}/json/close/${t.id}`).catch(() => {});
      }
    }
  } finally {
    proc.kill();
  }
  writeFileSync(OUT + 'design_pairs_manifest.json', JSON.stringify({ ts: new Date().toISOString(), pairs: manifest }, null, 2));
  console.log(`Wrote ${manifest.length} board frames`);
}

main().catch((e) => {
  console.error(e);
  process.exit(2);
});
