#!/usr/bin/env node
/** WP-CB-CALC LIVE functional probe — production /calc/ (Team 50, 2026-06-08) */
import { spawn, execSync } from 'node:child_process';
import { writeFileSync, mkdirSync } from 'node:fs';

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

const BASE = 'https://sfa.nimrod.bio/calc/';
const OUT = new URL('.', import.meta.url).pathname;

const PROBE_JS = `(async function(){
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const consoleErrors = [];
  const orig = console.error;
  console.error = function(){ consoleErrors.push([].slice.call(arguments).join(' ')); orig.apply(console, arguments); };

  const scope = document.getElementById('calc-scope');
  const goals = JSON.parse(scope.getAttribute('data-calc-goals') || '[]');
  const goalCount = goals.length;
  const header15 = !!document.body.innerText.includes('15 מטרות');
  const noProfitLabel = !document.body.innerText.includes('רווח גולמי');
  const hasCompareLabel = goals.some(g => (g.label || '').includes('השוואת גידולים'));
  const liveKinds = goals.filter(g => !g.soon && g.kind).map(g => g.kind).sort();

  function pickGoal(key) {
    const btn = document.querySelector('[data-goal="' + key + '"]');
    if (btn) { btn.click(); return; }
    const sel = document.getElementById('qb-more');
    if (sel) { sel.value = key; sel.dispatchEvent(new Event('change', { bubbles: true })); }
  }
  function setCrop(slug) {
    const sel = document.getElementById('qb-crop');
    if (sel) { sel.value = slug; sel.dispatchEvent(new Event('change', { bubbles: true })); }
  }
  function setBasis(b) {
    const grp = document.getElementById('qb-basis');
    const btn = grp && grp.querySelector('[data-basis="' + b + '"]');
    if (btn) btn.click();
  }
  function setVal(k, v) {
    const el = document.querySelector('[data-k="' + k + '"]');
    if (el) { el.value = v; el.dispatchEvent(new Event('input', { bubbles: true })); }
  }
  function clickCalc() {
    document.getElementById('qb-go').click();
    return sleep(400);
  }
  function bigText() {
    const el = document.getElementById('qb-answer-big');
    return el ? el.innerText.replace(/\\s+/g, ' ').trim() : '';
  }
  function bigHtml() {
    return document.getElementById('qb-answer-big')?.innerHTML || '';
  }
  function soonVisible() {
    const box = document.getElementById('qb-soon');
    return box && !box.hidden;
  }

  // Wait for frost regions async load
  for (let i = 0; i < 30 && !(window.SFA_FROST_REGIONS && window.SFA_FROST_REGIONS.regions); i++) {
    await sleep(200);
  }

  const checks = {};
  const regSel0 = document.getElementById('qb-region');
  checks.regionDefaultCoastal = regSel0 ? regSel0.value === 'coastal' : false;
  checks.regionCount = regSel0 ? Math.max(0, regSel0.options.length - 1) : 0;

  // Production slugs differ from branch QA fixtures (tomatoes not tomato, etc.)
  const CROP = {
    rich: 'tomatoes',       // transplant + dtm + hw + yield
    nodata: 'artichokes',   // no days_to_maturity on prod book
    revenue: 'carrots',     // yield + price_documented
    compare: ['tomatoes', 'cucumbers', 'peppers'],
  };

  // #4 sow_date — tomatoes transplant
  pickGoal('sow_date');
  setCrop(CROP.rich);
  setVal('target_date', '2026-09-15');
  await clickCalc();
  checks.sowDateTomato = bigText();
  checks.sowDateOk = /\\d{2}\\/\\d{2}\\/\\d{4}/.test(checks.sowDateTomato);

  // back to ask
  document.getElementById('qb-back')?.click();
  await sleep(300);

  // #5 harvest
  pickGoal('harvest');
  setCrop(CROP.rich);
  setVal('sow_date', '2026-05-12');
  await clickCalc();
  checks.harvestRangeTomato = bigText();
  checks.harvestOk = checks.harvestRangeTomato.includes('–');

  document.getElementById('qb-back')?.click();
  await sleep(300);

  // nodata crop (no dtm in prod book)
  pickGoal('sow_date');
  setCrop(CROP.nodata);
  await clickCalc();
  checks.potatoNodata = soonVisible();

  document.getElementById('qb-back')?.click();
  await sleep(300);

  // #6 succession
  pickGoal('succession');
  setCrop(CROP.rich);
  setVal('sow_date', '2026-03-01');
  setVal('succ_count', '4');
  await clickCalc();
  const succHtml = bigHtml();
  checks.successionDates = (succHtml.match(/\\d{2}\\/\\d{2}\\/\\d{4}/g) || []);
  checks.successionOk = checks.successionDates.length >= 4;

  document.getElementById('qb-back')?.click();
  await sleep(300);

  // #14 seed_cost with price
  pickGoal('seed_cost');
  setCrop(CROP.rich);
  setVal('seed_price_per_g', '0.001');
  await clickCalc();
  checks.seedCostWithPrice = bigText();

  document.getElementById('qb-back')?.click();
  await sleep(300);

  // #14 without price
  pickGoal('seed_cost');
  setCrop(CROP.rich);
  setVal('seed_price_per_g', '');
  await clickCalc();
  checks.seedCostNoPrice = bigText().slice(0, 20);
  checks.seedCostHonestNoFabrication = !/\\d+\\.\\d+\\s*₪/.test(bigText()) || bigText().includes('—');

  document.getElementById('qb-back')?.click();
  await sleep(300);

  // #11 frost coastal
  pickGoal('frost');
  setCrop(CROP.rich);
  setVal('region', 'coastal');
  await clickCalc();
  checks.frostCoastalNote = bigText().includes('ללא קרה משמעותית');

  document.getElementById('qb-back')?.click();
  await sleep(300);

  // #11 frost inland (judean_hills or similar)
  pickGoal('frost');
  setCrop(CROP.rich);
  const regions = (window.SFA_FROST_REGIONS && window.SFA_FROST_REGIONS.regions) || [];
  const inland = regions.find(r => !r.frost_free) || regions[1];
  if (inland) setVal('region', inland.key);
  await clickCalc();
  checks.frostRangeJudean = bigText();
  checks.frostRangeOk = checks.frostRangeJudean.includes('–');

  document.getElementById('qb-back')?.click();
  await sleep(300);

  // #3 nursery
  pickGoal('nursery');
  setCrop(CROP.rich);
  setBasis('seedlings');
  setVal('num_seedlings', '480');
  setVal('field_set_date', '2026-04-15');
  await clickCalc();
  const nurTxt = bigText();
  checks.nurseryTrays = parseInt((nurTxt.match(/(\\d+)\\s*מגש/) || [])[1] || '0', 10);
  checks.nurseryTraySow = (nurTxt.match(/\\d{2}\\/\\d{2}\\/\\d{4}/) || [])[0] || '';
  checks.nurseryOk = checks.nurseryTrays > 0 && !!checks.nurseryTraySow;

  document.getElementById('qb-back')?.click();
  await sleep(300);

  // #9 revenue F-01 (needs price_documented — carrots on prod)
  pickGoal('revenue');
  setCrop(CROP.revenue);
  setBasis('area');
  setVal('area', '30');
  await clickCalc();
  checks.revenueHtml = bigHtml();
  checks.revenuePrimaryKg = (bigText().match(/[\\d,.]+\\s*ק״ג/) || [])[0] || '';
  checks.revenueSecondaryLine = bigText().includes('מדד השוק') && bigText().includes('להמחשה');

  document.getElementById('qb-back')?.click();
  await sleep(300);

  // #13 compare — goal key is profit in PHP; basket attrs use compare (known quirk)
  pickGoal('profit');
  await sleep(200);
  // Manually populate basket via internal state if UI hidden
  const basketSlugs = CROP.compare.filter(s =>
    [...document.querySelectorAll('#qb-basket-add option')].some(o => o.value === s));
  const addSel = document.getElementById('qb-basket-add');
  if (addSel && basketSlugs.length >= 2) {
    for (const slug of basketSlugs) {
      addSel.value = slug;
      addSel.dispatchEvent(new Event('change', { bubbles: true }));
      await sleep(80);
    }
  }
  await clickCalc();
  const rankTxt = bigText();
  checks.compareRank = rankTxt;
  checks.compareOk = rankTxt.includes('ק״ג/מ׳') && /1\\s/.test(rankTxt) && rankTxt.includes('2');
  checks.compareCropHidden = document.querySelector('[data-goal-hide="compare"]')?.style.display === 'none';

  document.getElementById('qb-back')?.click();
  await sleep(300);

  // transplants scalar
  pickGoal('transplants');
  setCrop(CROP.rich);
  setBasis('area');
  setVal('area', '30');
  await clickCalc();
  checks.transplants = bigText();

  document.getElementById('qb-back')?.click();
  await sleep(300);

  // water #0 soon
  pickGoal('water');
  await clickCalc();
  checks.waterSoon = soonVisible();

  document.getElementById('qb-back')?.click();
  await sleep(300);

  // assumptions editor
  const assumBtn = document.getElementById('qb-assum-edit');
  if (assumBtn) assumBtn.click();
  await sleep(200);
  checks.assumptionsEditorOpens = !document.getElementById('qb-assum-editor')?.hidden;

  // session + export after one more calc
  pickGoal('seed');
  setCrop(CROP.rich);
  await clickCalc();
  const sessionRows = document.querySelectorAll('#qb-session-rows .qb-session__row').length;
  checks.exportRowsPopulated = sessionRows > 0;
  const csv = document.getElementById('qb-export-csv');
  if (csv) {
    csv.click();
    checks.exportHrefHasRows = (csv.getAttribute('href') || '').includes('rows%5B');
  }

  // SFA_DATEC live
  checks.sfaDatecLive = typeof window.SFA_DATEC === 'object' && typeof window.SFA_DATEC.fmt === 'function';

  return {
    base: location.href,
    ts: new Date().toISOString(),
    validator: 'Cursor / Composer (non-Claude)',
    consoleErrors,
    checks: {
      goalCount, header15, noProfitLabel, hasCompareLabel, liveKinds,
      ...checks
    }
  };
})()`;

async function main() {
  mkdirSync(OUT, { recursive: true });
  const chrome = findChrome();
  const port = 9300 + Math.floor((Date.now() % 200));
  const proc = spawn(chrome, [
    '--headless', '--disable-gpu', '--no-sandbox',
    `--remote-debugging-port=${port}`,
  ], { stdio: 'ignore' });
  await new Promise((r) => setTimeout(r, 1800));

  const consoleErrors = [];
  let result = null;
  try {
    const url = BASE + '?nc=' + Date.now();
    const t = await (await fetch(`http://127.0.0.1:${port}/json/new?about:blank`, { method: 'PUT' })).json();
    const ws = new WebSocket(t.webSocketDebuggerUrl);
    let id = 0;
    const pend = {};
    ws.addEventListener('message', (e) => {
      const m = JSON.parse(e.data);
      if (m.method === 'Runtime.consoleAPICalled' && m.params?.type === 'error') {
        consoleErrors.push(m.params.args?.map((a) => a.value || a.description || '').join(' ') || 'error');
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
    await send('Runtime.enable');
    await send('Log.enable');
    await send('Page.enable');
    await send('Emulation.setDeviceMetricsOverride', { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false });
    await send('Page.navigate', { url });
    await new Promise((r) => setTimeout(r, 4500));
    const ev = await send('Runtime.evaluate', { expression: PROBE_JS, returnByValue: true, awaitPromise: true });
    result = ev.result?.result?.value;
    if (result) result.consoleErrors = [...new Set([...(result.consoleErrors || []), ...consoleErrors])];
    ws.close();
    await fetch(`http://127.0.0.1:${port}/json/close/${t.id}`).catch(() => {});
  } finally {
    proc.kill();
  }

  const c = result?.checks || {};
  const fail = [];
  if (c.goalCount !== 15) fail.push('goalCount');
  if (!c.header15) fail.push('header15');
  if (!c.noProfitLabel) fail.push('noProfitLabel');
  if (!c.sowDateOk) fail.push('sowDate');
  if (!c.harvestOk) fail.push('harvest');
  if (!c.potatoNodata) fail.push('potatoNodata');
  if (!c.successionOk) fail.push('succession');
  if (!c.frostCoastalNote) fail.push('frostCoastal');
  if (!c.frostRangeOk) fail.push('frostRange');
  if (!c.nurseryOk) fail.push('nursery');
  if (!c.revenueSecondaryLine) fail.push('revenueF01');
  if (!c.compareOk) fail.push('compare');
  if (!c.regionDefaultCoastal && c.regionCount >= 5) fail.push('regionDefault');
  if (!c.waterSoon) fail.push('waterSoon');
  if (!c.sfaDatecLive) fail.push('SFA_DATEC');
  if ((result?.consoleErrors || []).length) fail.push('consoleErrors');

  const summary = {
    ...result,
    deploy: { url: BASE, assets_v: '1780865050', main: '2f31d89' },
    verdict: fail.length === 0 ? 'PASS' : 'FAIL',
    failures: fail,
  };
  writeFileSync(OUT + 'functional_probe_live.json', JSON.stringify(summary, null, 2));
  console.log(JSON.stringify(summary, null, 2));
  process.exit(fail.length ? 1 : 0);
}

main().catch((e) => { console.error(e); process.exit(2); });
