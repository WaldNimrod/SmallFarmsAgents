#!/usr/bin/env node
import { spawn, execSync } from 'node:child_process';
import { mkdirSync, writeFileSync } from 'node:fs';

function findChrome() {
  try {
    return execSync(`find "${process.env.HOME}/.cache/puppeteer" -name chrome-headless-shell -type f 2>/dev/null | sort -V | tail -1`, { encoding: 'utf8' }).trim();
  } catch {}
  return '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
}

const FRAMES = [
  { board: 'Board-A-Book-and-Calculator.html', label: 'book-entry', file: 'board_book-entry_desktop1440.png' },
  { board: 'Board-A-Book-and-Calculator.html', label: 'calc-page', file: 'board_calc-page_desktop1440.png' },
  { board: 'Board-B-Hub-Market-Search-Community-About-Account.html', label: 'hub-home', file: 'board_hub-home_desktop1440.png' },
  { board: 'Board-B-Hub-Market-Search-Community-About-Account.html', label: 'market-list', file: 'board_market-list_desktop1440.png' },
  { board: 'Board-B-Hub-Market-Search-Community-About-Account.html', label: 'community', file: 'board_community_desktop1440.png' },
];

const OUT = new URL('design_pairs/', import.meta.url).pathname;
const LOCAL = 'http://127.0.0.1:8767/';

async function main() {
  mkdirSync(OUT, { recursive: true });
  const chrome = findChrome();
  const port = 9300;
  const proc = spawn(chrome, ['--headless', '--disable-gpu', '--no-sandbox', `--remote-debugging-port=${port}`, '--window-size=1440,900'], { stdio: 'ignore' });
  await new Promise((r) => setTimeout(r, 1500));
  const manifest = [];
  try {
    for (const fr of FRAMES) {
      const url = LOCAL + fr.board + '#';
      const t = await (await fetch(`http://127.0.0.1:${port}/json/new?about:blank`, { method: 'PUT' })).json();
      const ws = new WebSocket(t.webSocketDebuggerUrl);
      let id = 0; const pend = {};
      ws.addEventListener('message', (e) => { const m = JSON.parse(e.data); if (m.id && pend[m.id]) pend[m.id](m); });
      await new Promise((r) => ws.addEventListener('open', r));
      const send = (method, params = {}) => new Promise((res) => { const i = ++id; pend[i] = res; ws.send(JSON.stringify({ id: i, method, params })); });
      await send('Page.enable');
      await send('Emulation.setDeviceMetricsOverride', { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false });
      await send('Page.navigate', { url: LOCAL + fr.board });
      await new Promise((r) => setTimeout(r, 2500));
      await send('Runtime.evaluate', {
        expression: `(() => { const el=document.querySelector('[data-screen-label="${fr.label}"]'); if(el){el.scrollIntoView({block:'center'}); return true;} return false; })()`,
        returnByValue: true,
      });
      await new Promise((r) => setTimeout(r, 800));
      const clip = await send('Runtime.evaluate', {
        expression: `(() => { const el=document.querySelector('[data-screen-label="${fr.label}"]'); if(!el) return null; const r=el.getBoundingClientRect(); return JSON.stringify({x:r.x,y:r.y,width:Math.min(r.width,1400),height:Math.min(r.height,900)}); })()`,
        returnByValue: true,
      });
      let clipParams = { x: 0, y: 0, width: 1200, height: 800, scale: 1 };
      try {
        const v = JSON.parse(clip.result?.result?.value || 'null');
        if (v && v.width > 50) clipParams = { x: Math.max(0, v.x), y: Math.max(0, v.y), width: v.width, height: v.height, scale: 1 };
      } catch {}
      const cap = await send('Page.captureScreenshot', { format: 'png', clip: clipParams });
      const path = OUT + fr.file;
      if (cap.result?.data) {
        writeFileSync(path, Buffer.from(cap.result.data, 'base64'));
        manifest.push({ label: fr.label, board: fr.board, path, live_pair: `../qa_probe/screenshots/${fr.label.replace('book-entry','crop-book-entry').replace('hub-home','hub').replace('market-list','market-list').replace('calc-page','calc').replace('community','community')}_desktop1440.png` });
      }
      ws.close();
      await fetch(`http://127.0.0.1:${port}/json/close/${t.id}`).catch(() => {});
    }
  } finally { proc.kill(); }
  writeFileSync(OUT + 'design_pairs_manifest.json', JSON.stringify(manifest, null, 2));
  console.log(JSON.stringify(manifest, null, 2));
}

main().catch((e) => { console.error(e); process.exit(2); });
