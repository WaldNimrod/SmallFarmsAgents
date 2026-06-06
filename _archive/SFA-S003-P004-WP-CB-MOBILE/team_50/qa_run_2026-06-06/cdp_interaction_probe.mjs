#!/usr/bin/env node
import { spawn, execSync } from 'node:child_process';
import { writeFileSync } from 'node:fs';

function findChrome() {
  try {
    return execSync(`find "${process.env.HOME}/.cache/puppeteer" -name chrome-headless-shell -type f 2>/dev/null | sort -V | tail -1`, { encoding: 'utf8' }).trim();
  } catch { return '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'; }
}

const BASE = 'https://sfa.nimrod.bio';
const OUT = new URL('.', import.meta.url).pathname;

async function cdpSession(port, vp, url, steps) {
  const t = await (await fetch(`http://127.0.0.1:${port}/json/new?about:blank`, { method: 'PUT' })).json();
  const ws = new WebSocket(t.webSocketDebuggerUrl);
  let id = 0; const pend = {};
  ws.addEventListener('message', e => { const m = JSON.parse(e.data); if (m.id && pend[m.id]) pend[m.id](m); });
  await new Promise(r => ws.addEventListener('open', r));
  const send = (method, params = {}) => new Promise(res => { const i = ++id; pend[i] = res; ws.send(JSON.stringify({ id: i, method, params })); });
  await send('Page.enable'); await send('Runtime.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: vp.w, height: vp.h, deviceScaleFactor: 1, mobile: vp.mobile });
  await send('Page.navigate', { url });
  await new Promise(r => setTimeout(r, 3500));
  const out = [];
  for (const step of steps) {
    const ev = await send('Runtime.evaluate', { expression: step, returnByValue: true, awaitPromise: true });
    const raw = ev.result?.result?.value;
    out.push(typeof raw === 'string' ? JSON.parse(raw) : raw ?? null);
  }
  ws.close();
  await fetch(`http://127.0.0.1:${port}/json/close/${t.id}`).catch(() => {});
  return out;
}

async function main() {
  const chrome = findChrome();
  const port = 9300 + Math.floor((Date.now() % 200));
  const proc = spawn(chrome, ['--headless','--disable-gpu','--no-sandbox',`--remote-debugging-port=${port}`,'--hide-scrollbars'], { stdio: 'ignore' });
  await new Promise(r => setTimeout(r, 1800));
  const vp = { w: 375, h: 812, mobile: true };
  const results = {};
  try {
    // Hero bbox — crop simple
    const [hero] = await cdpSession(port, vp, BASE + '/crop-book/lettuce/?cb=' + Date.now(), [`(() => {
      const pick = sel => { const el = document.querySelector(sel); if (!el) return null; const r = el.getBoundingClientRect(); return { sel, top: Math.round(r.top), bottom: Math.round(r.bottom), left: Math.round(r.left), right: Math.round(r.right), w: Math.round(r.width), h: Math.round(r.height) }; };
      const candidates = ['.cb-hero__art','.crop-hero__icon','.sh__mark','[class*="hero"] img','[class*="hero"] svg','.cb-hero','h1','.cb-hero__title'];
      const boxes = candidates.map(pick).filter(Boolean);
      const h1 = document.querySelector('h1');
      const art = document.querySelector('[class*="hero"] [class*="art"], [class*="hero"] img, .sh__mark, [class*="watercolor"]');
      const artR = art?.getBoundingClientRect();
      const h1R = h1?.getBoundingClientRect();
      const collide = artR && h1R ? !(artR.bottom < h1R.top - 2 || artR.top > h1R.bottom + 2 || artR.right < h1R.left || artR.left > h1R.right) : null;
      return JSON.stringify({ boxes, collide, title: h1?.textContent?.trim() });
    })()`]);
    results.cropHero = hero;

    // Market disclaimer expand
    const [mktBefore, mktAfter] = await cdpSession(port, vp, BASE + '/market/?cb=' + Date.now(), [
      `(() => { const d = document.querySelector('details, [class*="disclaimer"]'); return JSON.stringify({ hasDetails: !!d, open: d?.open, textLen: (d?.textContent||'').length }); })()`,
      `(() => {
        const d = document.querySelector('details') || [...document.querySelectorAll('button,a')].find(e => /הבהרה|שימו לב|disclaimer/i.test(e.textContent||''))?.closest('details,[class*="disclaimer"]');
        if (d && d.tagName === 'DETAILS') { d.open = true; }
        else { const btn = [...document.querySelectorAll('button,a,summary')].find(e => /הבהרה|שימו לב|קרא/i.test(e.textContent||'')); btn?.click(); }
        return JSON.stringify({ open: d?.open, visible: (d?.textContent||'').slice(0,120) });
      })()`,
    ]);
    results.marketDisclaimer = { before: mktBefore, afterClick: mktAfter };

    // Calc בפיתוח — click "עוד מחשבונים" then each goal
    const [calcGoals] = await cdpSession(port, vp, BASE + '/calc/?cb=' + Date.now(), [`(async () => {
      const more = [...document.querySelectorAll('button,a')].find(e => /עוד מחשבונים/.test(e.textContent||''));
      if (more) more.click();
      await new Promise(r => setTimeout(r, 400));
      const goals = [...document.querySelectorAll('button')].filter(e => {
        const t = (e.textContent||'').trim();
        return t.length > 4 && t.length < 35 && !/חשב|ברירת|עוד|שלח|ברירת מחדל/.test(t);
      });
      const names = [...new Set(goals.map(g => (g.textContent||'').trim()))].slice(0, 14);
      const out = [];
      for (const name of names) {
        const g = [...document.querySelectorAll('button')].find(b => (b.textContent||'').trim() === name);
        if (!g) continue;
        g.click();
        await new Promise(r => setTimeout(r, 250));
        const crop = document.querySelector('select');
        if (crop && crop.options.length > 1) { crop.value = crop.options[1].value; crop.dispatchEvent(new Event('change', {bubbles:true})); }
        await new Promise(r => setTimeout(r, 200));
        const calcBtn = [...document.querySelectorAll('button')].find(b => (b.textContent||'').includes('חשב'));
        calcBtn?.click();
        await new Promise(r => setTimeout(r, 600));
        const resultEl = document.querySelector('[class*="result"],[class*="output"],[class*="session"],main');
        const txt = (resultEl?.innerText || document.body.innerText).slice(0, 2000);
        out.push({ goal: name.slice(0,30), notice: txt.includes('בפיתוח'), snippet: txt.slice(0,80) });
      }
      return { total: out.length, goals: out };
    })()`]);
    results.calcGoals = calcGoals;

    // Depth switch simple → full
    const [depthSwitch] = await cdpSession(port, vp, BASE + '/crop-book/lettuce/?cb=' + Date.now(), [`(() => {
      const full = [...document.querySelectorAll('a,button')].find(e => (e.textContent||'').includes('מלא'));
      const before = document.documentElement.scrollHeight;
      full?.click();
      return JSON.stringify({ clicked: !!full, beforeH: before });
    })()`]);
    // need navigation wait - do separate
    results.depthSwitchClick = depthSwitch;

    const [afterFull] = await cdpSession(port, vp, BASE + '/crop-book/lettuce/?depth=full&cb=' + Date.now(), [`(() => JSON.stringify({ scrollHeight: document.documentElement.scrollHeight, url: location.href, fieldSections: document.querySelectorAll('h2,h3,[class*="section-title"]').length }))()`]);
    results.afterFullNav = afterFull;

    // Companions Hebrew on deep
    const [deepText] = await cdpSession(port, vp, BASE + '/crop-book/lettuce/?depth=deep&cb=' + Date.now(), [`(() => {
      const t = document.body.innerText;
      const idx = t.indexOf('לווי');
      const slice = idx >= 0 ? t.slice(idx, idx+200) : t.slice(0,500);
      const companions = /צמחים נלווים|שכנים טובים|לווי/.test(t);
      const fieldCount = [...document.querySelectorAll('h3, h4, [class*="field-label"], dt')].map(e => e.textContent.trim()).filter(Boolean).length;
      return JSON.stringify({ companions, fieldCount, sample: slice.slice(0,150) });
    })()`]);
    results.deepCompanions = deepText;

  } finally { proc.kill(); }
  writeFileSync(OUT + 'cdp_interaction_result.json', JSON.stringify({ ts: new Date().toISOString(), results }, null, 2));
  console.log(JSON.stringify({ ts: new Date().toISOString(), results }, null, 2));
}
main().catch(e => { console.error(e); process.exit(2); });
