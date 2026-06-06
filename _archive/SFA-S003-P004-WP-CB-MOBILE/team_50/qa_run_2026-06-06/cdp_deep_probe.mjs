#!/usr/bin/env node
/** WP-CB-MOBILE deep CDP probe — heights, DOM checks, interactions */
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
const OUT = new URL('.', import.meta.url).pathname;

const CHECKS = [
  {
    name: 'crop-simple-mobile',
    path: '/crop-book/lettuce/',
    vp: { w: 375, h: 812, mobile: true },
    js: `(() => {
      const h = document.documentElement.scrollHeight;
      const bodies = document.querySelectorAll('[data-crop-body], .crop-body, .cb-crop-body, main .crop-page');
      const hero = document.querySelector('.crop-hero, .cb-hero, [class*="hero"]');
      const heroRect = hero ? hero.getBoundingClientRect() : null;
      const title = document.querySelector('h1');
      const titleRect = title ? title.getBoundingClientRect() : null;
      const overlap = heroRect && titleRect ? (heroRect.bottom > titleRect.top + 5 && heroRect.top < titleRect.bottom) : null;
      const tokens = ['IL_general','IL_north','IL_center','IL_south','>seed<','>spring<'].filter(t => document.body.innerHTML.includes(t));
      const depthBtns = [...document.querySelectorAll('a,button')].filter(e => /פשוט|מלא|עמוק/.test(e.textContent||'')).map(e => e.textContent.trim().slice(0,20));
      const sections = document.querySelectorAll('section, [class*="section"]').length;
      return JSON.stringify({ scrollHeight: h, cropBodies: bodies.length, overlap, tokens, depthBtns: depthBtns.slice(0,6), sections });
    })()`,
  },
  {
    name: 'crop-full-mobile',
    path: '/crop-book/lettuce/?depth=full',
    vp: { w: 375, h: 812, mobile: true },
    js: `(() => {
      const fields = document.querySelectorAll('[class*="field"], [class*="datum"], .cb-field, .data-row').length;
      const cards = document.querySelectorAll('[class*="card"]').length;
      const dup = (document.body.innerText.match(/כל הנתונים/g)||[]).length;
      return JSON.stringify({ scrollHeight: document.documentElement.scrollHeight, fieldLike: fields, cards, dupAllData: dup });
    })()`,
  },
  {
    name: 'crop-deep-mobile',
    path: '/crop-book/lettuce/?depth=deep',
    vp: { w: 375, h: 812, mobile: true },
    js: `(() => {
      const text = document.body.innerText;
      const hasStorage = /אחסון|אחסון ושימור|שמירה/.test(text);
      const hasCompanions = /צמחים נלווים|לווי|שכנים/.test(text);
      const hasVariety = /זנים|טבלת זנים|variety/i.test(text);
      const hasRanges = /–|עד/.test(text);
      const pills = [...document.querySelectorAll('[class*="pill"],[class*="source"],[class*="badge"]')].filter(e => /^[A-Z]{2}$/.test((e.textContent||'').trim())).map(e => e.textContent.trim()).slice(0,10);
      return JSON.stringify({ scrollHeight: document.documentElement.scrollHeight, hasStorage, hasCompanions, hasVariety, hasRanges, pills });
    })()`,
  },
  {
    name: 'market-mobile',
    path: '/market/',
    vp: { w: 375, h: 812, mobile: true },
    js: `(() => {
      const chips = [...document.querySelectorAll('button,a,[class*="chip"]')].map(e => (e.textContent||'').trim()).filter(t => t.length < 20);
      const hasSalim = chips.some(t => t.includes('סלים'));
      const chipCount = chips.filter(t => ['הכל','ירקות','פירות','עלים','תבלינים','פטריות','נבטים','סלים','אגוזים','שמנים','דבש'].some(c => t.includes(c))).length;
      const tableActive = !!document.querySelector('table, [class*="table"][class*="active"], [aria-selected="true"]');
      const tableRows = document.querySelectorAll('table tbody tr, [class*="market"] tr').length;
      const disclaimer = document.querySelector('[class*="disclaimer"], [class*="notice"], details');
      const discCollapsed = disclaimer ? (disclaimer.open === false || disclaimer.getAttribute('open') === null) : null;
      return JSON.stringify({ scrollHeight: document.documentElement.scrollHeight, hasSalim, chipCount, tableRows, tableActive, discCollapsed, chips: chips.slice(0,15) });
    })()`,
  },
  {
    name: 'calc-mobile',
    path: '/calc/',
    vp: { w: 375, h: 812, mobile: true },
    js: `(() => {
      const goalBtns = [...document.querySelectorAll('button,[class*="goal"]')].filter(e => (e.textContent||'').length > 3 && (e.textContent||'').length < 40);
      const moreBtn = [...document.querySelectorAll('button,a')].find(e => /עוד מחשבונים|8/.test(e.textContent||''));
      return JSON.stringify({ goalBtnCount: goalBtns.length, hasMoreBtn: !!moreBtn, moreText: moreBtn?.textContent?.trim() });
    })()`,
  },
  {
    name: 'cropbook-list-mobile',
    path: '/crop-book/',
    vp: { w: 375, h: 812, mobile: true },
    js: `(() => {
      const cards = document.querySelectorAll('[class*="card"], article, li[class*="crop"]').length;
      const seasonFilter = [...document.querySelectorAll('button,select,a')].some(e => /עונה|בעונה|החודש/.test(e.textContent||''));
      const badges = [...document.querySelectorAll('[class*="badge"],[class*="season"]')].filter(e => /🌱|🪴/.test(e.textContent||e.innerHTML)).length;
      const thumbs = document.querySelectorAll('img[class*="thumb"], [class*="thumb"] img, .crop-card img').length;
      return JSON.stringify({ cards, seasonFilter, inSeasonBadges: badges, thumbs });
    })()`,
  },
  {
    name: 'hub-mobile',
    path: '/',
    vp: { w: 375, h: 812, mobile: true },
    js: `(() => {
      const moduleImgs = [...document.querySelectorAll('img')].filter(i => /module-/.test(i.src||'')).map(i => i.src.split('/').pop());
      const coming = [...document.querySelectorAll('[class*="coming"],[class*="soon"]')].length;
      const waLinks = [...document.querySelectorAll('a')].filter(a => /whatsapp|wa\.me/i.test(a.href||'')).length;
      const inlineForm = !!document.querySelector('form input, form textarea, [class*="suggest"] input');
      return JSON.stringify({ moduleImgs: moduleImgs.slice(0,6), comingBlocks: coming, waLinks, inlineForm });
    })()`,
  },
];

async function main() {
  const chrome = findChrome();
  const port = 9200 + Math.floor((Date.now() % 300));
  const proc = spawn(chrome, ['--headless','--disable-gpu','--no-sandbox',`--remote-debugging-port=${port}`,'--hide-scrollbars'], { stdio: 'ignore' });
  await new Promise(r => setTimeout(r, 1800));
  const results = [];
  try {
    for (const chk of CHECKS) {
      const url = BASE + chk.path + (chk.path.includes('?') ? '&' : '?') + 'cb=' + Date.now();
      const t = await (await fetch(`http://127.0.0.1:${port}/json/new?about:blank`, { method: 'PUT' })).json();
      const ws = new WebSocket(t.webSocketDebuggerUrl);
      let id = 0; const pend = {};
      ws.addEventListener('message', e => { const m = JSON.parse(e.data); if (m.id && pend[m.id]) pend[m.id](m); });
      await new Promise(r => ws.addEventListener('open', r));
      const send = (method, params = {}) => new Promise(res => { const i = ++id; pend[i] = res; ws.send(JSON.stringify({ id: i, method, params })); });
      await send('Page.enable'); await send('Runtime.enable');
      await send('Emulation.setDeviceMetricsOverride', { width: chk.vp.w, height: chk.vp.h, deviceScaleFactor: 1, mobile: chk.vp.mobile });
      await send('Page.navigate', { url });
      await new Promise(r => setTimeout(r, 3500));
      const ev = await send('Runtime.evaluate', { expression: chk.js, returnByValue: true });
      const data = ev.result?.result?.value ? JSON.parse(ev.result.result.value) : null;
      results.push({ name: chk.name, path: chk.path, data });
      ws.close();
      await fetch(`http://127.0.0.1:${port}/json/close/${t.id}`).catch(() => {});
    }
  } finally { proc.kill(); }
  const out = { ts: new Date().toISOString(), asset_v: '1780691715', results };
  writeFileSync(OUT + 'cdp_deep_result.json', JSON.stringify(out, null, 2));
  console.log(JSON.stringify(out, null, 2));
}
main().catch(e => { console.error(e); process.exit(2); });
