/* ============================================================
   SFA Crop Book v1 — interaction layer (vanilla ES5-ish)
   Ported from team_35 LOD300 cropbook-v1.js.
   Mirrors calculator formulas from calculators.py (AC-11).
   WP-CB-1 · 2026-05-31
   ============================================================ */
(function () {
  'use strict';

  /* ── Assumption registry (mirrors assumptions.py ASSUMPTIONS defaults) ── */
  var A = {
    germination_rate: 0.90,
    oversow:          1.10,
    bed_width:        0.80,
    compost_N_pct:    0.015,
    application_efficiency: 0.50,
    std_bed_length_m: 30,
    rotation_gap_seasons: 3
  };

  var fmt = function (n, d) {
    if (n == null || !isFinite(n)) return '—';
    d = (d == null) ? 0 : d;
    return Number(n).toLocaleString('he-IL', { minimumFractionDigits: d, maximumFractionDigits: d });
  };

  /* ── Calculator formulas — keyed by data-calc.
     These MUST stay in parity with calculators.py (AC-11).
     Operand names resolved through FIELD_ALIASES before passing to CALC.
     ── */
  var CALC = {
    /* #1 seed quantity to buy (audience=B)
       seeds = plants / germination_rate × oversow
       grams = seeds / seeds_per_gram
       plants = (bed_len_cm / spacing_cm) × rows × seeds_per_hole */
    seed: function (g, book) {
      var len      = parseFloat(g.bed_len) || 0;
      var sph      = parseFloat(g.seeds_per_hole) || 1;
      var spacing  = parseFloat(book.spacing) || 1;
      var rows     = parseFloat(book.rows) || 1;
      var spg      = parseFloat(book.seeds_per_gram) || 1;
      var plants   = (len * 100 / spacing) * rows * sph;
      var seeds    = plants / A.germination_rate * A.oversow;
      var grams    = seeds / spg;
      return {
        main:    fmt(grams, 1),
        unit:    'גרם',
        formula: 'plants ' + fmt(plants) + ' / germ ' + Math.round(A.germination_rate * 100) + '% × oversow ' + A.oversow + ' ÷ ' + spg + ' seeds/g',
        extra:   fmt(seeds) + ' זרעים · ' + fmt(plants) + ' צמחים'
      };
    },

    /* #7 beds needed (audience=F)
       beds = target_kg / (yield_per_m × std_bed_length_m) */
    beds: function (g, book) {
      var target   = parseFloat(g.target_kg) || 0;
      var yieldM   = parseFloat(book.yield_per_m) || 1;
      var bedLen   = A.std_bed_length_m;
      var beds     = target / (yieldM * bedLen);
      return {
        main:    fmt(beds, 1),
        unit:    'ערוגות',
        formula: target + ' kg ÷ (' + yieldM + ' kg/m × ' + bedLen + ' m/bed)'
      };
    },

    /* #8 expected yield (audience=B)
       kg = yield_per_m × bed_len */
    yield: function (g, book) {
      var len    = parseFloat(g.bed_len) || 0;
      var yieldM = parseFloat(book.yield_per_m) || 0;
      var kg     = yieldM * len;
      return {
        main:    fmt(kg, 1),
        unit:    'ק״ג',
        formula: len + ' m × ' + yieldM + ' kg/m'
      };
    },

    /* #9 expected revenue (audience=F)
       revenue = yield_per_m × area × price */
    revenue: function (g, book) {
      var area   = parseFloat(g.area) || 0;
      var yieldM = parseFloat(book.yield_per_m) || 0;
      var price  = parseFloat(book.price) || 0;
      var kg     = yieldM * area;
      var rev    = kg * price;
      return {
        main:    fmt(rev),
        unit:    '₪',
        formula: fmt(kg, 0) + ' kg × ' + price + ' ₪/kg',
        extra:   'יבול ' + fmt(kg, 0) + ' ק״ג'
      };
    },

    /* #10 plant population / spacing layout (audience=B)
       per_m2 = (rows / bed_width) × (100 / spacing_cm) */
    pop: function (g, book) {
      var rows    = parseFloat(book.rows) || 1;
      var spacing = parseFloat(book.spacing) || 1;
      var bw      = A.bed_width;
      var perM2   = (rows / bw) * (100 / spacing);
      return {
        main:    fmt(perM2, 1),
        unit:    'צמ׳/מ״ר',
        formula: '(' + rows + ' rows / ' + bw + ' m) × (100 / ' + spacing + ' cm)',
        perM2:   perM2
      };
    },

    /* #12 fertiliser / compost need (audience=F)
       n_kg_ha = nutrient_removal_n_kg_per_ha
       compost_kg = (n_kg_ha × area_ha) / (compost_N_pct × application_efficiency) */
    fert: function (g, book) {
      var areaSqm  = parseFloat(g.area_m2) || 0;
      var areaHa   = areaSqm / 10000;
      var n        = parseFloat(book.n) || 0;
      var p        = parseFloat(book.p) || 0;
      var k        = parseFloat(book.k) || 0;
      var nKg      = n * areaHa;
      var compost  = nKg / (A.compost_N_pct * A.application_efficiency);
      return {
        main:    fmt(compost, 0),
        unit:    'ק״ג קומפוסט',
        formula: 'N ' + fmt(nKg, 1) + ' kg ÷ (' + (A.compost_N_pct * 100) + '% × eff ' + A.application_efficiency + ')',
        extra:   'N ' + fmt(nKg, 1) + ' · P ' + fmt(p * areaHa, 1) + ' · K ' + fmt(k * areaHa, 1) + ' ק״ג'
      };
    }
  };

  function readBook(panel) {
    var book = {};
    panel.querySelectorAll('[data-book]').forEach(function (el) {
      var inp = el.querySelector('.bv__in');
      book[el.getAttribute('data-book')] = parseFloat(inp ? inp.value : el.getAttribute('data-val'));
    });
    return book;
  }

  function recompute(panel) {
    var kind = panel.getAttribute('data-calc');
    if (!CALC[kind] || panel.classList.contains('is-disabled')) return;
    var g = {};
    panel.querySelectorAll('[data-k]').forEach(function (el) {
      g[el.getAttribute('data-k')] = el.value;
    });
    var book = readBook(panel);
    var out;
    try { out = CALC[kind](g, book); } catch (e) { return; }
    var rEl = panel.querySelector('[data-result]');
    if (rEl) rEl.innerHTML = out.main + (out.unit ? ' <small>' + out.unit + '</small>' : '');
    var fEl = panel.querySelector('[data-formula]');
    if (fEl) fEl.textContent = out.formula || '';
    var eEl = panel.querySelector('[data-extra]');
    if (eEl && out.extra != null) eEl.textContent = out.extra;
    /* #10 population grid */
    if (kind === 'pop' && out.perM2 != null) {
      var grid = panel.querySelector('[data-popgrid]');
      if (grid) {
        var cols = Math.max(2, Math.round(book.rows || 2));
        var per  = Math.min(48, Math.max(8, Math.round(out.perM2)));
        grid.style.gridTemplateColumns = 'repeat(' + cols + ', 1fr)';
        grid.innerHTML = '';
        for (var i = 0; i < cols * Math.ceil(per / cols); i++) {
          grid.appendChild(document.createElement('i'));
        }
      }
    }
    /* propagate * to any calc that consumed an unvalidated value */
    propagateAst(panel);
  }

  function recomputeAll() {
    document.querySelectorAll('[data-calc]').forEach(recompute);
  }

  function propagateAst(panel) {
    /* if any book chip is .bv--ast, add * to result */
    var hasAst = panel.querySelector('.bv--ast');
    var rEl    = panel.querySelector('[data-result]');
    if (rEl && hasAst) {
      var existing = rEl.querySelector('.ast');
      if (!existing) {
        var s = document.createElement('span');
        s.className = 'ast'; s.title = 'ערך לא מאומת — מבוסס על מקורות בעלי ביטחון נמוך';
        s.textContent = '*';
        rEl.appendChild(s);
      }
    }
  }

  /* ── AssumptionField: expand / override / reset ── */
  function wireAssumptions() {
    document.querySelectorAll('.af').forEach(function (af) {
      var bar = af.querySelector('.af__bar');
      if (!bar) return;
      bar.addEventListener('click', function (e) {
        if (e.target.closest && e.target.closest('.af__body')) return;
        af.classList.toggle('is-open');
      });
      var input = af.querySelector('[data-assume]');
      if (input) {
        var key   = input.getAttribute('data-assume');
        var scale = parseFloat(input.getAttribute('data-scale') || '1');
        input.addEventListener('input', function () {
          var v = parseFloat(input.value);
          if (isFinite(v)) {
            A[key] = v * scale;
            updateAssumeEchos(key, input.value, input);
            recomputeAll();
          }
        });
        var reset = af.querySelector('[data-reset]');
        if (reset) {
          reset.addEventListener('click', function () {
            input.value = reset.getAttribute('data-default');
            A[key] = parseFloat(reset.getAttribute('data-default')) * scale;
            updateAssumeEchos(key, input.value, input);
            recomputeAll();
          });
        }
      }
    });
  }

  function updateAssumeEchos(key, display, input) {
    var suffix = (input && input.getAttribute('data-suffix')) || '';
    document.querySelectorAll('[data-assume-echo="' + key + '"]').forEach(function (el) {
      el.textContent = display + suffix;
    });
  }

  /* ── Calculator input wiring ── */
  function wireCalcs() {
    document.querySelectorAll('[data-calc]').forEach(function (panel) {
      panel.querySelectorAll('[data-k]').forEach(function (el) {
        el.addEventListener('input', function () { recompute(panel); });
        el.addEventListener('change', function () { recompute(panel); });
      });
    });
    recomputeAll();
  }

  /* ── Audience switch (Cards ⇄ Table) ── */
  function wireAudience() {
    document.querySelectorAll('[data-aud-switch]').forEach(function (sw) {
      var scopeId = sw.getAttribute('data-aud-switch');
      var scope   = scopeId ? document.getElementById(scopeId) : null;
      sw.querySelectorAll('.aud__opt').forEach(function (opt) {
        opt.addEventListener('click', function () {
          sw.querySelectorAll('.aud__opt').forEach(function (o) { o.classList.remove('is-active'); });
          opt.classList.add('is-active');
          var view = opt.getAttribute('data-view');
          if (!scope) return;
          scope.querySelectorAll('[data-aud-view]').forEach(function (v) {
            v.style.display = v.getAttribute('data-aud-view') === view ? '' : 'none';
          });
        });
      });
      /* apply default: show cards, hide table */
      if (scope) {
        scope.querySelectorAll('[data-aud-view="table"]').forEach(function (v) { v.style.display = 'none'; });
      }
    });
  }

  /* ── Depth tabs (Simple / Full / Drill-down) ── */
  function wireDepths() {
    document.querySelectorAll('[data-depths]').forEach(function (tabs) {
      var scopeId = tabs.getAttribute('data-depths');
      var scope   = scopeId ? document.getElementById(scopeId) : null;
      tabs.querySelectorAll('button').forEach(function (b) {
        b.addEventListener('click', function () {
          tabs.querySelectorAll('button').forEach(function (x) { x.classList.remove('is-active'); });
          b.classList.add('is-active');
          var d = b.getAttribute('data-depth');
          if (!scope) return;
          scope.querySelectorAll('[data-depth-view]').forEach(function (v) {
            v.style.display = v.getAttribute('data-depth-view') === d ? '' : 'none';
          });
        });
      });
    });
  }

  /* ── Advanced filter panel toggle ── */
  function wireFilterCollapse() {
    document.querySelectorAll('[data-filter-toggle]').forEach(function (btn) {
      var box = document.getElementById(btn.getAttribute('data-filter-toggle'));
      if (!box) return;
      btn.addEventListener('click', function () {
        var open = box.classList.toggle('is-open');
        btn.classList.toggle('is-open', open);
        btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      });
    });
  }

  /* ── Filter chips (single = radio within group; multi = toggle) ── */
  function wireFilters() {
    document.querySelectorAll('.fchip').forEach(function (c) {
      c.addEventListener('click', function () {
        if (c.dataset.single) {
          c.parentNode.querySelectorAll('.fchip').forEach(function (s) { s.classList.remove('is-on'); });
          c.classList.add('is-on');
        } else {
          c.classList.toggle('is-on');
        }
      });
    });
    document.querySelectorAll('[data-filter-reset]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var sc = btn.closest('.ftop') || document;
        sc.querySelectorAll('.fchip').forEach(function (c) {
          c.classList.toggle('is-on', c.hasAttribute('data-default-on'));
        });
        sc.querySelectorAll('.filters__search input, .fdate').forEach(function (i) { i.value = ''; });
      });
    });
  }

  /* ── Collapsible topic sections (Full depth) ── */
  function wireTopics() {
    document.querySelectorAll('.topic__head').forEach(function (h) {
      h.addEventListener('click', function () {
        h.closest('.topic').classList.toggle('is-collapsed');
      });
    });
  }

  /* ── Calculator modal overlay ── */
  function wireCalcModals() {
    document.querySelectorAll('[data-calc-open]').forEach(function (btn) {
      if (btn.classList.contains('is-disabled')) return;
      var modal = document.getElementById(btn.getAttribute('data-calc-open'));
      if (!modal) return;
      btn.addEventListener('click', function () { modal.classList.add('is-open'); });
      modal.querySelectorAll('[data-calc-close], .calcmodal__overlay').forEach(function (c) {
        c.addEventListener('click', function () { modal.classList.remove('is-open'); });
      });
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        document.querySelectorAll('.calcmodal.is-open').forEach(function (m) { m.classList.remove('is-open'); });
      }
    });
  }

  /* ── Editable book values (user overrides, clearly marked) ── */
  function wireBookEdits() {
    document.querySelectorAll('.bv__in').forEach(function (inp) {
      var chip  = inp.closest('.bv');
      var panel = inp.closest('[data-calc]');
      var orig  = inp.getAttribute('data-orig') || inp.value;
      function sync() {
        chip.classList.toggle('is-overridden', parseFloat(inp.value) !== parseFloat(orig));
        chip.setAttribute('data-val', inp.value);
        if (panel) recompute(panel);
      }
      inp.addEventListener('input', sync);
      var restore = chip ? chip.querySelector('.bv__restore') : null;
      if (restore) {
        restore.addEventListener('click', function () { inp.value = orig; sync(); });
      }
    });
  }

  /* ── Hebrew field dictionary (mirrors cropbook-v1.js FIELD_INFO) ── */
  var FIELD_INFO = {
    days_to_maturity:          ['ימים להבשלה',          'מספר הימים מהזריעה או השתילה ועד תחילת הקציר.',                                            'days_to_maturity'],
    harvest_window:            ['חלון קציר',             'כמה ימים נמשך הקציר מרגע ההבשלה הראשונה.',                                                 'harvest_window_max_days'],
    in_row_spacing_cm:         ['מרווח בשורה',           'המרחק בין צמח לצמח לאורך השורה, ס״מ.',                                                    'spacing_in_row_cm'],
    spacing_in_row_cm:         ['מרווח בשורה',           'המרחק בין צמח לצמח לאורך השורה, ס״מ.',                                                    'spacing_in_row_cm'],
    rows_per_bed:              ['שורות בערוגה',          'כמה שורות נכנסות ברוחב ערוגה אחת (80 ס״מ).',                                              'rows_per_bed'],
    avg_yield_per_bed_m:       ['יבול ממוצע למ׳',       'קילוגרם תוצרת למטר ערוגה — ממוצע.',                                                       'yield_per_bed_m'],
    yield_per_bed_m:           ['יבול ממוצע למ׳',       'קילוגרם תוצרת למטר ערוגה — ממוצע.',                                                       'yield_per_bed_m'],
    documented_price:          ['מחיר מתועד',            'מחיר השוק האחרון שתועד.',                                                                   'price_documented'],
    price_documented:          ['מחיר מתועד',            'מחיר השוק האחרון שתועד.',                                                                   'price_documented'],
    planting_season:           ['עונת גידול',            'העונות שבהן מומלץ לזרוע או לשתול.',                                                        'sowing_months'],
    sowing_months:             ['חודשי זריעה',           'החודשים שבהם מומלץ לזרוע — 1=ינואר … 12=דצמבר.',                                          'sowing_months'],
    planting_method:           ['שיטת שתילה',            'זריעה ישירה, גידול שתיל, או שניהם.',                                                       'planting_method'],
    frost_tolerance:           ['עמידות לקרה',           'סיווג: עמיד / חצי-עמיד / רגיש / רגיש מאוד.',                                              'frost_tolerance_class'],
    frost_tolerance_class:     ['עמידות לקרה',           'סיווג: עמיד / חצי-עמיד / רגיש / רגיש מאוד.',                                              'frost_tolerance_class'],
    seeds_per_gram:            ['זרעים לגרם',            'כמה זרעים יש בגרם אחד.',                                                                   'seeds_per_g'],
    seeds_per_g:               ['זרעים לגרם',            'כמה זרעים יש בגרם אחד.',                                                                   'seeds_per_g'],
    days_in_nursery:           ['ימים במשתלה',           'כמה ימים השתיל גדל במשתלה לפני שתילה.',                                                   'days_in_nursery'],
    days_in_nursery_cell:      ['ימים במשתלה',           'כמה ימים השתיל גדל במשתלה לפני שתילה.',                                                   'days_in_nursery'],
    succession_interval:       ['מרווח רצף',             'כל כמה שבועות לזרוע מנה חדשה לקציר רציף.',                                               'succession_interval_weeks'],
    succession_interval_weeks: ['מרווח רצף',             'כל כמה שבועות לזרוע מנה חדשה לקציר רציף.',                                               'succession_interval_weeks'],
    nutrient_removal_N:        ['צריכת חנקן (N)',        'כמות החנקן שהגידול מוציא, ק״ג להקטר.',                                                    'nutrient_removal_n_kg_per_ha'],
    nutrient_removal_n_kg_per_ha: ['צריכת חנקן (N)',    'כמות החנקן שהגידול מוציא, ק״ג להקטר.',                                                    'nutrient_removal_n_kg_per_ha'],
    family:                    ['משפחה בוטנית',          'המשפחה הבוטנית — בסיס לרמז מחזור הגידולים.',                                              'family'],
    needs_summer_shade:        ['הצללה בקיץ',            'גידולים מסוימים זקוקים לרשת צל בקיץ. שלוש רמות: 30% / 40% / 50%.',                       'needs_summer_shade'],
    irrigation_type:           ['סוג השקיה',             'אופן ההשקיה — טפטוף, ממטרות. שדה מוצע.',                                                 'irrigation_type'],
    root_depth_class:          ['עומק שורשים',           'סיווג עומק: רדוד / בינוני / עמוק. שדה מוצע.',                                             'root_depth_class'],
    germination_rate:          ['אחוז נביטה',            'הנחת תכנון: שיעור הזרעים שינבטו. ברירת מחדל 90%.',                                        'germination_rate'],
    bed_width:                 ['רוחב ערוגה',            'הנחת תכנון: רוחב ערוגה. ברירת מחדל 80 ס״מ.',                                              'bed_width']
  };

  function injectFieldInfo() {
    document.querySelectorAll('[data-field]').forEach(function (el) {
      var info = FIELD_INFO[el.getAttribute('data-field')];
      if (!info) return;
      if (el.textContent.trim() === '') el.textContent = info[0];
      var f = document.createElement('span');
      f.className = 'finfo'; f.tabIndex = 0; f.setAttribute('aria-label', 'מידע על שדה');
      f.textContent = 'ⓘ';
      var pop = document.createElement('span');
      pop.className = 'tip__pop';
      // V02 fix: omit raw canonical key (<span class="k">) from farmer-facing tooltip.
      // The key is an implementation detail; farmers see Hebrew label + explainer only.
      pop.innerHTML = '<b>' + info[0] + '</b>' + info[1];
      f.appendChild(pop);
      el.appendChild(f);
    });
  }

  /* ── Pagination (client-side, 25/page default) ── */
  function wirePagination() {
    document.querySelectorAll('[data-pager]').forEach(function (pager) {
      pager.querySelectorAll('.pager__pg').forEach(function (b) {
        b.addEventListener('click', function () {
          pager.querySelectorAll('.pager__pg').forEach(function (x) { x.classList.remove('is-active'); });
          b.classList.add('is-active');
        });
      });
    });
  }

  /* ── request-info CTA (POST /api/v1/contribute) ── */
  function wireReqInfo() {
    document.querySelectorAll('.reqinfo[data-field]').forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        var payload = {
          kind:       'request-info',
          field_name: btn.getAttribute('data-field') || '',
          crop_slug:  btn.getAttribute('data-crop')  || (document.body.getAttribute('data-crop-slug') || '')
        };
        fetch('/api/v1/contribute', {
          method:  'POST',
          headers: { 'Content-Type': 'application/json' },
          body:    JSON.stringify(payload)
        }).catch(function () { /* silent — lightweight funnel */ });
        btn.textContent = '✓ בקשה נשלחה';
        btn.style.pointerEvents = 'none';
      });
    });
  }

  /* ── Expose CALC for testing (parity fixture) ── */
  if (typeof window !== 'undefined') {
    window.SFA_CALC       = CALC;
    window.SFA_ASSUMPTIONS = A;
  }

  /* WP-CB-1-patch01: calculator-plan export — append the live plan (context strip +
     summary rows) to /calc/export.{csv,pdf} as query params so the server renders it. */
  function wireCalcExport() {
    var btns = document.querySelectorAll('[data-calc-export]');
    if (!btns.length) return;
    function planQuery() {
      var p = [];
      function add(k, v) { if (v !== null && v !== undefined && String(v) !== '' && String(v) !== '—') p.push(encodeURIComponent(k) + '=' + encodeURIComponent(v)); }
      var cropSel = document.querySelector('[data-k="crop_slug"]');
      if (cropSel) {
        var opt = cropSel.options ? cropSel.options[cropSel.selectedIndex] : null;
        add('crop', opt ? (opt.text || cropSel.value) : cropSel.value);
      }
      var beds = document.querySelector('[data-k="num_beds"]');
      if (beds) add('beds', beds.value);
      var td = document.querySelector('[data-k="target_date"]');
      if (td) add('target_date', td.value);
      var sum = { 'יבול כולל': '[data-summary-yield]', 'הכנסה כוללת': '[data-summary-revenue]', 'קומפוסט': '[data-summary-compost]' };
      Object.keys(sum).forEach(function (label) {
        var el = document.querySelector(sum[label]);
        if (el) add('rows[' + label + ']', (el.textContent || '').trim());
      });
      return p.join('&');
    }
    btns.forEach(function (b) {
      b.addEventListener('click', function (e) {
        var base = b.getAttribute('href');
        var q = planQuery();
        b.setAttribute('href', q ? base + '?' + q : base);
        // let the browser follow the (now param-laden) href; CSV downloads, PDF opens print view
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    wireAssumptions();
    wireCalcs();
    wireBookEdits();
    wireFilters();
    injectFieldInfo();
    wireAudience();
    wireDepths();
    wireFilterCollapse();
    wirePagination();
    wireTopics();
    wireCalcModals();
    wireReqInfo();
    wireCalcExport();
  });
})();
