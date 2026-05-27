// sfa.js — Small Farms Agents UI behaviors
// Vanilla JS (ES2017+), no framework, no build step. Target: modern browsers.
// Behaviors:
//   1. Accordion <details> persistence (sessionStorage)
//   2. Contrib-strip CTA enhancement (target=_blank, rel=noopener, click flag)
//   3. Pro-table sort via [data-sort] headers
//   4. Calculator live recompute on [data-calc-form]
(function () {
  'use strict';

  // ── Behavior 1: accordion persistence (preserved) ─────────────────────
  function initAccordion() {
    var key = 'sfa-open-details';
    var details = document.querySelectorAll('details');
    if (!details.length) return;
    try {
      var saved = JSON.parse(sessionStorage.getItem(key) || '[]');
      details.forEach(function (el, idx) {
        if (saved.indexOf(idx) !== -1) el.open = true;
        el.addEventListener('toggle', function () {
          var open = [];
          details.forEach(function (d, i) { if (d.open) open.push(i); });
          sessionStorage.setItem(key, JSON.stringify(open));
        });
      });
    } catch (e) {
      // best-effort UI persistence
    }
  }

  // ── Behavior 2: contrib-strip WhatsApp CTA enhancement ────────────────
  function initContribAnalytics() {
    var ctas = document.querySelectorAll('a.contrib-strip__cta');
    ctas.forEach(function (a) {
      if (!a.getAttribute('target')) a.setAttribute('target', '_blank');
      var rel = (a.getAttribute('rel') || '').split(/\s+/).filter(Boolean);
      if (rel.indexOf('noopener') === -1) rel.push('noopener');
      if (rel.indexOf('noreferrer') === -1) rel.push('noreferrer');
      a.setAttribute('rel', rel.join(' '));
      a.addEventListener('click', function () {
        a.setAttribute('data-clicked', 'true');
      });
    });
  }

  // ── Behavior 3: pro-table sort via [data-sort] ───────────────────────
  function initTableSort() {
    document.querySelectorAll('th[data-sort]').forEach(function (th) {
      th.style.cursor = 'pointer';
      th.addEventListener('click', function () {
        var table = th.closest('table');
        if (!table) return;
        var tbody = table.tBodies[0];
        if (!tbody) return;
        var rows = Array.from(tbody.rows);
        var idx = Array.from(th.parentElement.children).indexOf(th);
        var asc = th.getAttribute('aria-sort') !== 'ascending';
        rows.sort(function (a, b) {
          var ac = a.cells[idx], bc = b.cells[idx];
          var av = ac ? ac.textContent.trim() : '';
          var bv = bc ? bc.textContent.trim() : '';
          var an = parseFloat(av.replace(/[^\d.\-]/g, ''));
          var bn = parseFloat(bv.replace(/[^\d.\-]/g, ''));
          if (!isNaN(an) && !isNaN(bn)) return asc ? an - bn : bn - an;
          return asc ? av.localeCompare(bv, 'he') : bv.localeCompare(av, 'he');
        });
        // Clear aria-sort on sibling ths
        var headerRow = th.parentElement;
        Array.from(headerRow.children).forEach(function (t) { t.removeAttribute('aria-sort'); });
        th.setAttribute('aria-sort', asc ? 'ascending' : 'descending');
        rows.forEach(function (r) { tbody.appendChild(r); });
      });
    });
  }

  // ── Behavior 4: calculator live recompute ────────────────────────────
  function initCalc() {
    var form = document.querySelector('[data-calc-form]');
    if (!form) return;
    function recompute() {
      var y = parseFloat((form.querySelector('[data-calc-input="yield"]') || {}).value) || 0;
      var a = parseFloat((form.querySelector('[data-calc-input="area"]') || {}).value) || 0;
      var p = parseFloat((form.querySelector('[data-calc-input="price"]') || {}).value) || 0;
      var totalYield = y * a;
      var totalRevenue = totalYield * p;
      var outY = form.querySelector('[data-calc-output="total-yield"]');
      var outR = form.querySelector('[data-calc-output="total-revenue"]');
      if (outY) outY.textContent = totalYield.toFixed(1) + ' ק"ג';
      if (outR) outR.textContent = '₪ ' + totalRevenue.toFixed(0);
    }
    form.querySelectorAll('[data-calc-input]').forEach(function (i) {
      i.addEventListener('input', recompute);
    });
    recompute();
  }

  // ── Bootstrap ────────────────────────────────────────────────────────
  function boot() {
    initAccordion();
    initContribAnalytics();
    initTableSort();
    initCalc();
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
