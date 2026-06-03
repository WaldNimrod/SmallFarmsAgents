/* ============================================================
   SFA — Class B interaction layer (vanilla, light)
   Complements cropbook-v1.js. Only the new surfaces' bits.
   ============================================================ */
(function () {
  'use strict';

  /* request/suggest chips (community) — single-select within a group */
  function wireReqChips() {
    document.querySelectorAll('.reqcard__chips').forEach(function (group) {
      group.querySelectorAll('.reqchip').forEach(function (c) {
        c.addEventListener('click', function () {
          group.querySelectorAll('.reqchip').forEach(function (x) { x.classList.remove('is-on'); });
          c.classList.add('is-on');
        });
      });
    });
  }

  /* market category chips reuse .fchip wiring from cropbook-v1.js — nothing to add */

  /* price-graph time-range selector (visual segmented control) + live API fetch */
  function wireRangeSel() {
    document.querySelectorAll('.rangesel').forEach(function (rangesel) {
      var pgraph = rangesel.closest('[data-slug]');
      var slug   = pgraph ? pgraph.getAttribute('data-slug') : null;

      rangesel.querySelectorAll('button:not([disabled])').forEach(function (b) {
        b.addEventListener('click', function () {
          rangesel.querySelectorAll('button').forEach(function (x) { x.classList.remove('is-active'); });
          b.classList.add('is-active');

          // Update graph title
          var days = parseInt(b.getAttribute('data-days') || '28', 10);
          var titleEl = pgraph ? pgraph.querySelector('.pgraph__title') : null;
          if (titleEl) {
            titleEl.textContent = 'מחיר — ' + days + ' ימים אחרונים';
          }

          // Fetch updated history from API (M-1: window.fetchHistory binding)
          if (slug && window.fetchHistory) {
            window.fetchHistory(slug, days, pgraph);
          }
        });
      });
    });
  }

  /**
   * Fetch price history for a product and redraw the SVG path.
   * Exposed as window.fetchHistory so the crop-book market cross-link can call it.
   *
   * @param {string} slug    — product slug
   * @param {number} days    — number of days (7 or 28)
   * @param {Element} pgraph — .pgraph container element (or null for page-wide lookup)
   */
  window.fetchHistory = function (slug, days, pgraph) {
    if (!slug) return;
    var container = pgraph || document.querySelector('.pgraph[data-slug="' + slug + '"]');
    if (!container) return;
    var svg = container.querySelector('.pgraph__svg');
    if (!svg) return;

    fetch('/market/' + encodeURIComponent(slug) + '/history?days=' + days, {
      headers: { 'Accept': 'application/json' }
    }).then(function (r) { return r.ok ? r.json() : null; })
      .then(function (rows) {
        if (!rows || !rows.length) return;
        // Build SVG path from returned rows [{price_date, price, ...}]
        var prices  = rows.map(function (r) { return parseFloat(r.price) || 0; });
        var pmin    = Math.min.apply(null, prices);
        var pmax    = Math.max.apply(null, prices);
        var prange  = Math.max(pmax - pmin, 0.01);
        var svgW    = parseFloat(svg.getAttribute('viewBox').split(' ')[2]) || 360;
        var svgH    = parseFloat(svg.getAttribute('viewBox').split(' ')[3]) || 80;
        var n       = rows.length;
        var pts     = prices.map(function (p, i) {
          var x = n > 1 ? Math.round(i / (n - 1) * svgW * 10) / 10 : svgW / 2;
          var y = Math.round((svgH - ((p - pmin) / prange) * (svgH - 16) - 8) * 10) / 10;
          return x + ',' + y;
        });
        var first = pts[0], last = pts[pts.length - 1];
        var lastX = last.split(',')[0];
        var line  = 'M ' + pts.join(' L ');
        var area  = 'M ' + first.split(',')[0] + ',' + svgH + ' L ' + pts.join(' L ') + ' L ' + lastX + ',' + svgH + ' Z';
        var lineEl = svg.querySelector('.pgraph__line');
        var areaEl = svg.querySelector('.pgraph__area');
        if (lineEl) lineEl.setAttribute('d', line);
        if (areaEl) areaEl.setAttribute('d', area);
      })
      .catch(function () { /* silent — graph stays at last rendered state */ });
  };

  document.addEventListener('DOMContentLoaded', function () { wireReqChips(); wireRangeSel(); });
})();
