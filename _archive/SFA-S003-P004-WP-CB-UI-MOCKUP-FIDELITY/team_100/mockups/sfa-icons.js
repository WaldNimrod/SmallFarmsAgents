/* ============================================================
   SFA UI Redesign — shared icon sprite (line glyphs) · v2
   DSX-1: replaces all emoji. Monochrome, inherits currentColor.
   fill/stroke are baked as ATTRIBUTES on every <symbol> so the
   glyphs render as outlines in every engine (no CSS-inherit
   reliance). Use: <svg class="gi"><use href="#i-sprout"></use></svg>
   ============================================================ */
(function () {
  var A = 'fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"';
  function sym(id, body){ return '<symbol id="'+id+'" viewBox="0 0 24 24" '+A+'>'+body+'</symbol>'; }
  var SPRITE =
  '<svg xmlns="http://www.w3.org/2000/svg" style="position:absolute;width:0;height:0;overflow:hidden" aria-hidden="true" focusable="false">' +
  sym('i-sprout','<path d="M12 20v-7"/><path d="M12 13C12 10 9.5 8 6.5 8C6.5 11 9 13 12 13Z"/><path d="M12 12C12 9 14.5 6.5 17.5 6.5C17.5 9.5 15 12 12 12Z"/>') +
  sym('i-seedling','<path d="M8 21h8"/><path d="M12 21v-6"/><path d="M12 15C9 15 7 13 7 10C10 10 12 12 12 15Z"/><path d="M12 14C12 11.4 14 9.5 16.5 9.5C16.5 12 14.5 14 12 14Z"/>') +
  sym('i-drop','<path d="M12 3c3.5 4.5 6 7.3 6 10.5a6 6 0 0 1-12 0C6 10.3 8.5 7.5 12 3Z"/>') +
  sym('i-shield','<path d="M12 3l7 2.5v6c0 4.5-3 7.8-7 9-4-1.2-7-4.5-7-9v-6L12 3Z"/><path d="M9 12l2 2 4-4"/>') +
  sym('i-companions','<circle cx="9" cy="12" r="4.3"/><circle cx="15" cy="12" r="4.3"/>') +
  sym('i-box','<path d="M12 3l8 4v10l-8 4-8-4V7Z"/><path d="M4 7l8 4 8-4"/><path d="M12 11v10"/>') +
  sym('i-tractor','<circle cx="7" cy="17" r="3"/><circle cx="17.5" cy="17.5" r="2.5"/><path d="M4 14V9h6l2 4h3"/><path d="M12 13h5v2"/>') +
  sym('i-bulb','<path d="M9.5 18h5"/><path d="M10 21h4"/><path d="M7.5 14a6 6 0 1 1 9 0c-.8.8-1.5 1.6-1.5 3h-6c0-1.4-.7-2.2-1.5-3Z"/>') +
  sym('i-journal','<path d="M6 4h12v16H7a1 1 0 0 1-1-1V4Z"/><path d="M6 16h12"/><path d="M9.5 8h5"/>') +
  sym('i-receipt','<path d="M6 3h12v18l-2-1.3L13.5 21 12 19.7 10.5 21 8 19.7 6 21Z"/><path d="M9 8h6"/><path d="M9 12h6"/>') +
  sym('i-scale','<path d="M12 4v16"/><path d="M8 21h8"/><path d="M5 7h14"/><path d="M5 7l-2.5 5h5L5 7Z"/><path d="M19 7l-2.5 5h5L19 7Z"/><circle cx="12" cy="4" r="1.2"/>') +
  sym('i-leaf','<path d="M4 20c0-9 7-15 16-15 0 9-6 15-15 15"/><path d="M5 19C9 13 13 10 18 9"/>') +
  sym('i-snow','<path d="M12 2v20"/><path d="M3 7l18 10"/><path d="M21 7L3 17"/><path d="M9.5 4.5 12 7l2.5-2.5M9.5 19.5 12 17l2.5 2.5"/>') +
  sym('i-calendar','<rect x="4" y="5" width="16" height="15" rx="2"/><path d="M4 9.5h16"/><path d="M8 3v4"/><path d="M16 3v4"/>') +
  sym('i-repeat','<path d="M4 9a5 5 0 0 1 5-5h7"/><path d="M13 1l3 3-3 3"/><path d="M20 15a5 5 0 0 1-5 5H8"/><path d="M11 23l-3-3 3-3"/>') +
  sym('i-basket','<path d="M5 9h14l-1.2 9.5a2 2 0 0 1-2 1.5H8.2a2 2 0 0 1-2-1.5L5 9Z"/><path d="M9 9l3-5"/><path d="M15 9l-3-5"/><path d="M10 13v3"/><path d="M14 13v3"/>') +
  sym('i-chart','<path d="M4 20h16"/><rect x="6" y="12" width="3" height="7"/><rect x="11" y="7" width="3" height="12"/><rect x="16" y="14" width="3" height="5"/>') +
  sym('i-compost','<path d="M4 13a8 8 0 0 1 16 0"/><path d="M3 13h18l-1.3 6H4.3L3 13Z"/><path d="M12 13c0-2.5 2-4.5 4.5-4.5"/>') +
  sym('i-grid','<rect x="4" y="4" width="7" height="7" rx="1"/><rect x="13" y="4" width="7" height="7" rx="1"/><rect x="4" y="13" width="7" height="7" rx="1"/><rect x="13" y="13" width="7" height="7" rx="1"/>') +
  sym('i-rows','<rect x="4" y="6" width="16" height="3.6" rx="1"/><rect x="4" y="14.4" width="16" height="3.6" rx="1"/>') +
  sym('i-book','<path d="M12 6C10 4.5 7 4 4 4v14c3 0 6 .5 8 2 2-1.5 5-2 8-2V4c-3 0-6 .5-8 2Z"/><path d="M12 6v14"/>') +
  sym('i-cap','<path d="M12 4 2 9l10 5 10-5-10-5Z"/><path d="M6 11v5c0 1.5 2.7 3 6 3s6-1.5 6-3v-5"/><path d="M22 9v5"/>') +
  sym('i-gear','<circle cx="12" cy="12" r="3.2"/><path d="M12 2v3M12 19v3M22 12h-3M5 12H2M18.4 5.6l-2.1 2.1M7.7 16.3l-2.1 2.1M18.4 18.4l-2.1-2.1M7.7 7.7 5.6 5.6"/>') +
  sym('i-download','<path d="M12 4v11"/><path d="M8 11l4 4 4-4"/><path d="M5 20h14"/>') +
  sym('i-shekel','<path d="M6 18V6h6a3 3 0 0 1 3 3v3"/><path d="M18 6v12h-6a3 3 0 0 1-3-3V9"/>') +
  sym('i-info','<circle cx="12" cy="12" r="9"/><path d="M12 11v5"/><path d="M12 8h.01"/>') +
  sym('i-flame','<path d="M12 3c1.5 3 5 5 5 9a5 5 0 0 1-10 0c0-1.6.7-2.7 1.7-3.3.3 1 1 1.8 1.9 2.1C10.5 7.9 11.5 5.9 12 3Z"/>') +
  '</svg>';
  function inject() {
    if (document.getElementById('sfa-icon-sprite')) return;
    var d = document.createElement('div');
    d.id = 'sfa-icon-sprite';
    d.style.cssText = 'position:absolute;width:0;height:0;overflow:hidden';
    d.innerHTML = SPRITE;
    document.body.insertBefore(d, document.body.firstChild);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', inject);
  else inject();
})();
