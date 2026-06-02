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

  /* price-graph time-range selector (visual segmented control) */
  function wireRangeSel() {
    document.querySelectorAll('.rangesel').forEach(function (sel) {
      sel.querySelectorAll('button').forEach(function (b) {
        b.addEventListener('click', function () {
          sel.querySelectorAll('button').forEach(function (x) { x.classList.remove('is-active'); });
          b.classList.add('is-active');
        });
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function () { wireReqChips(); wireRangeSel(); });
})();
