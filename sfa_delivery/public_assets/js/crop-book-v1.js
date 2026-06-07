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

    /* #2 transplants / seedlings needed (audience=B)
       plants = round((bed_len_cm / spacing_cm) × rows)  — mirrors calculators.py transplants_needed */
    transplants: function (g, book) {
      var len     = parseFloat(g.bed_len) || 0;
      var spacing = parseFloat(book.spacing) || 1;
      var rows    = parseFloat(book.rows) || 1;
      var plants  = Math.round((len * 100 / spacing) * rows);
      return {
        main:    fmt(plants),
        unit:    'שתילים',
        formula: '(' + len + ' m × 100 ÷ ' + spacing + ' cm) × ' + rows + ' שורות'
      };
    },

    /* #14 seed / input cost (audience=F) — mirrors calculators.py seed_input_cost
       cost = grams × ₪/g   OR   ceil(grams / grams_per_pack) × pack_price */
    seed_cost: function (g, book) {
      var grams = parseFloat(g.grams) || 0;
      var perG  = parseFloat(g.seed_price_per_g);
      var packP = parseFloat(g.pack_price);
      var gPack = parseFloat(g.grams_per_pack);
      var cost, packs = null, formula;
      if (isFinite(perG)) {
        cost = grams * perG;
        formula = fmt(grams, 1) + ' g × ' + perG + ' ₪/g';
      } else if (isFinite(packP) && isFinite(gPack) && gPack > 0) {
        packs = Math.ceil(grams / gPack);
        cost = packs * packP;
        formula = '⌈' + fmt(grams, 1) + ' ÷ ' + gPack + '⌉ = ' + packs + ' חב׳ × ' + packP + ' ₪';
      } else {
        return { ok: false };   // no pricing mode supplied
      }
      return {
        main:    fmt(cost, 2),
        unit:    '₪',
        formula: formula,
        extra:   packs != null ? ('≈ ' + packs + ' חבילות') : ''
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

    /* #9 expected revenue (audience=F) — QUANTITY-FIRST (team_00 / QA F-01):
       yield (ק״ג) is the HEADLINE; ₪ value is a secondary, illustrative line (price-list). */
    revenue: function (g, book) {
      var area   = parseFloat(g.area) || 0;
      var yieldM = parseFloat(book.yield_per_m) || 0;
      var price  = parseFloat(book.price) || 0;
      var kg     = yieldM * area;
      var rev    = kg * price;
      return {
        main:    fmt(kg, 0),
        unit:    'ק״ג',
        formula: fmt(yieldM, 1) + ' ק״ג/מ׳ × ' + fmt(area, 0) + ' מ׳',
        extra:   price > 0 ? ('שווי משוער ' + fmt(rev) + ' ₪ · מדד השוק · להמחשה') : ''
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

  /* ══════════════════════════════════════════════════════════════
     WP-CB-CALC Phase B — DATE ENGINE.
     Date-only arithmetic mirroring calculators.py (date + timedelta).
     NO timezone math: parse/compute in UTC, display dd/mm/yyyy — avoids
     DST/off-by-one. MUST stay in parity with calculators.py (AC-11).
     Exposed as window.SFA_DATEC for the parity fixture.
     ══════════════════════════════════════════════════════════════ */
  var DATEC = {
    DAY: 86400000,
    parse: function (s) {                 // 'YYYY-MM-DD' -> UTC ms (date-only) | null
      if (s == null) return null;
      var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(s).trim());
      return m ? Date.UTC(+m[1], +m[2] - 1, +m[3]) : null;
    },
    addDays: function (ms, n) { return ms + n * this.DAY; },
    fmt: function (ms) {                   // UTC ms -> 'dd/mm/yyyy'
      if (ms == null) return '';
      var d = new Date(ms);
      return ('0' + d.getUTCDate()).slice(-2) + '/' +
             ('0' + (d.getUTCMonth() + 1)).slice(-2) + '/' + d.getUTCFullYear();
    },
    isTransplant: function (pm) {          // mirrors calculators.py _is_transplant (+ 'both')
      pm = String(pm == null ? '' : pm).toLowerCase();
      return pm.indexOf('transplant') === 0 || pm.indexOf('greenhouse') === 0 || pm === 'both';
    },
    /* #4 sowing_date_from_harvest */
    sowDate: function (targetHarvest, dtm, plantingMethod, daysInNursery) {
      var t = this.parse(targetHarvest);
      if (t == null || dtm == null) return null;
      if (this.isTransplant(plantingMethod) && daysInNursery != null) {
        var sow = this.addDays(t, -(dtm + daysInNursery));
        return { sow: sow, fieldSet: this.addDays(sow, daysInNursery) };
      }
      return { sow: this.addDays(t, -dtm), fieldSet: null };  // direct-seed default
    },
    /* #5 harvest_window_from_sowing */
    harvestWindow: function (sow, dtm, hwMax, plantingMethod, daysInNursery) {
      var s = this.parse(sow);
      if (s == null || dtm == null || hwMax == null) return null;
      var nursery = (this.isTransplant(plantingMethod) && daysInNursery != null) ? daysInNursery : 0;
      var start = this.addDays(s, nursery + dtm);
      return { start: start, end: this.addDays(start, hwMax) };
    },
    /* #6 succession_schedule — interval DERIVED round(harvest_window_max_days/7) per team_00 decision */
    succession: function (firstSow, hwMax, opts) {
      var f = this.parse(firstSow);
      if (f == null || hwMax == null) return null;
      var weeks = Math.round(hwMax / 7); if (weeks < 1) weeks = 1;
      var step = weeks * 7, out = [];
      opts = opts || {};
      if (opts.count != null) {
        var n = Math.max(0, Math.min(60, Math.floor(opts.count)));
        for (var i = 0; i < n; i++) out.push(this.addDays(f, i * step));
      } else if (opts.seasonEnd != null) {
        var end = this.parse(opts.seasonEnd); if (end == null) return null;
        for (var k = 0; k <= 60; k++) {
          var d = this.addDays(f, k * step);
          if (d > end) break;
          out.push(d);
        }
      } else { return null; }
      return { intervalWeeks: weeks, dates: out };
    }
  };
  if (typeof window !== 'undefined') window.SFA_DATEC = DATEC;

  /* #13 crop comparison — QUANTITY-FIRST basket ranking (team_00 reframe of
     calculators.py crop_profit_comparison: rank by yield/m, value/m secondary;
     NO profit/margin). Pure: ranks a basket of slugs against the numeric book map.
     Exposed as window.SFA_COMPARE for the parity fixture. */
  function rankBasket(slugs, bookMap) {
    var rows = [];
    (slugs || []).forEach(function (slug) {
      var b = (bookMap && bookMap[slug]) || {};
      var y = parseFloat(b.yield_per_bed_m != null ? b.yield_per_bed_m : b.avg_yield_per_bed_m);
      if (!isFinite(y) || y <= 0) return;            // exclude missing-yield (not zeroed)
      var price = parseFloat(b.price_documented != null ? b.price_documented : b.documented_price);
      rows.push({ slug: slug, yieldPerM: y, valuePerM: isFinite(price) ? y * price : null });
    });
    rows.sort(function (a, c) { return c.yieldPerM - a.yieldPerM; });   // quantity desc (primary)
    return rows;
  }
  if (typeof window !== 'undefined') window.SFA_COMPARE = rankBasket;

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
    if (eEl) eEl.textContent = (out.extra != null ? out.extra : '');   // clear stale extra across goals
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

  /* ── Audience switch (Cards ⇄ Table) ──
     WP-CB-MOBILE D1: optional `data-aud-persist="<key>"` on the switch enables
     localStorage persistence of the user's chosen view. When present, the saved
     view (if any) is applied on load — otherwise the server-rendered default is
     kept (market default = table). The crop-book list omits the attribute and
     keeps its server cards default + no persistence. */
  function wireAudience() {
    document.querySelectorAll('[data-aud-switch]').forEach(function (sw) {
      var scopeId    = sw.getAttribute('data-aud-switch');
      var scope      = scopeId ? document.getElementById(scopeId) : null;
      var persistKey = sw.getAttribute('data-aud-persist');

      function applyView(view) {
        sw.querySelectorAll('.aud__opt').forEach(function (o) {
          o.classList.toggle('is-active', o.getAttribute('data-view') === view);
        });
        if (!scope) return;
        scope.querySelectorAll('[data-aud-view]').forEach(function (v) {
          v.style.display = v.getAttribute('data-aud-view') === view ? '' : 'none';
        });
      }

      sw.querySelectorAll('.aud__opt').forEach(function (opt) {
        opt.addEventListener('click', function () {
          var view = opt.getAttribute('data-view');
          applyView(view);
          if (persistKey) {
            try { localStorage.setItem(persistKey, view); } catch (e) {}
          }
        });
      });

      /* Initial view: persisted choice (if any + persistence enabled) wins;
         otherwise honor the server-rendered active option, falling back to cards. */
      var initial = null;
      if (persistKey) {
        try { initial = localStorage.getItem(persistKey); } catch (e) {}
      }
      if (initial !== 'cards' && initial !== 'table') {
        var act = sw.querySelector('.aud__opt.is-active');
        initial = act ? act.getAttribute('data-view') : 'cards';
      }
      applyView(initial);
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
          /* WP-CB-MOBILE Stage 2: depth switch resets scroll to the top so the
             reader starts from the hero/essentials of the newly-chosen depth. */
          try {
            window.scrollTo({ top: 0, behavior: 'auto' });
          } catch (e) {
            window.scrollTo(0, 0);
          }
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

  /* ══════════════════════════════════════════════════════════════
     WP-CB-MOBILE FIX 6 — "define the question" builder + session.
     Reuses the EXISTING CALC registry + recompute() above (no math is
     duplicated). The builder configures the hidden #qb-engine [data-calc]
     panel, dispatches input → recompute(), then reads [data-result] and
     surfaces it as .qb-answer + .qb-break, accumulating into .qb-session
     (sessionStorage, per-device for v1 per team_100 decision).
     ══════════════════════════════════════════════════════════════ */

  /* book field_name → engine data-book key (mirrors calc_dash BOOK_ALIAS) */
  var QB_BOOK_ALIAS = {
    spacing_in_row_cm: 'spacing', in_row_spacing_cm: 'spacing',
    rows_per_bed: 'rows',
    seeds_per_g: 'seeds_per_gram', seeds_per_gram: 'seeds_per_gram',
    yield_per_bed_m: 'yield_per_m', avg_yield_per_bed_m: 'yield_per_m',
    price_documented: 'price', documented_price: 'price',
    nutrient_removal_n_kg_per_ha: 'n', nutrient_removal_N: 'n',
    nutrient_removal_p_kg_per_ha: 'p',
    nutrient_removal_k_kg_per_ha: 'k'
  };

  var QB_STORE_KEY = 'sfa_calc_session_v1';

  function qbReadSession() {
    try { return JSON.parse(sessionStorage.getItem(QB_STORE_KEY) || '[]') || []; }
    catch (e) { return []; }
  }
  function qbWriteSession(list) {
    try { sessionStorage.setItem(QB_STORE_KEY, JSON.stringify(list)); } catch (e) {}
  }

  function wireQuestionBuilder() {
    var scope = document.getElementById('calc-scope');
    if (!scope) return;
    var engine = document.getElementById('qb-engine');

    var goals = {};
    try { (JSON.parse(scope.getAttribute('data-calc-goals') || '[]') || []).forEach(function (g) { goals[g.key] = g; }); }
    catch (e) { goals = {}; }

    var state = {
      goal:   'seed',
      basis:  'area',
      anchor: 'target'
    };

    var goalGrid  = document.getElementById('qb-goal');
    var moreSel   = document.getElementById('qb-more');
    var cropSel   = document.getElementById('qb-crop');
    var basisGrp  = document.getElementById('qb-basis');
    var anchorGrp = document.getElementById('qb-anchor');
    var echo      = document.getElementById('qb-echo');

    function basisInputs() { return scope.querySelectorAll('[data-basis-input]'); }
    function anchorInputs() { return scope.querySelectorAll('[data-anchor-input]'); }

    /* a goal's basis is mostly user-choosable, but "beds for target yield"
       forces the target-kg input regardless of the basis chips. */
    function effectiveBasisInput() {
      var g = goals[state.goal] || {};
      if (g.basis === 'target') return 'target';
      return state.basis;
    }

    function showBasisInput() {
      var want = effectiveBasisInput();
      basisInputs().forEach(function (el) {
        el.style.display = el.getAttribute('data-basis-input') === want ? '' : 'none';
      });
      // when a goal forces target, dim the basis chip group (informational)
      var g = goals[state.goal] || {};
      if (basisGrp) basisGrp.style.opacity = (g.basis === 'target') ? '0.5' : '';
    }
    function showAnchorInput() {
      anchorInputs().forEach(function (el) {
        el.style.display = el.getAttribute('data-anchor-input') === state.anchor ? '' : 'none';
      });
    }
    /* goal-specific extra inputs (succession count, seed-cost price, …) — shown per chosen goal */
    function showGoalInput() {
      scope.querySelectorAll('[data-goal-input]').forEach(function (el) {
        el.style.display = el.getAttribute('data-goal-input') === state.goal ? '' : 'none';
      });
    }

    function cropName() {
      if (!cropSel) return '';
      var opt = cropSel.options[cropSel.selectedIndex];
      return opt ? (opt.text || '') : '';
    }

    function basisPhrase() {
      var inp = scope.querySelector('[data-basis-input="' + effectiveBasisInput() + '"]:not([style*="display: none"])');
      var num = inp ? (inp.querySelector('input') || {}).value : '';
      var map = { area: 'שטח', beds: 'מס׳ ערוגות', seedlings: 'מס׳ שתילים', target: 'יעד יבול' };
      var lbl = map[effectiveBasisInput()] || '';
      return lbl + (num ? ' ' + num : '');
    }

    function updateEcho() {
      if (!echo) return;
      var g = goals[state.goal] || {};
      var cn = cropName();
      echo.innerHTML = 'השאלה שלך: אחשב <b>' + (g.label || '') + '</b> עבור <b>' +
        (cn || '—') + '</b>, לפי <b>' + basisPhrase() + '</b>.';
    }

    /* configure + run the hidden engine for the current goal; returns
       { main, unit, ok } where ok=false means no live math (soon). */
    /* date-anchor input value ('YYYY-MM-DD') for the goal's anchor */
    function dateInputVal(anchorKind) {
      var k = anchorKind === 'sow' ? 'sow_date' : 'target_date';
      var el = scope.querySelector('[data-k="' + k + '"]');
      return el ? (el.value || '') : '';
    }
    /* first finite numeric among the given book field names */
    function bookNum(book) {
      for (var i = 1; i < arguments.length; i++) {
        var v = parseFloat(book[arguments[i]]);
        if (isFinite(v)) return v;
      }
      return null;
    }
    /* WP-CB-CALC Phase B-now: date goals via SFA_DATEC + the time-anchor + date book-fields */
    function runDateGoal(g, book, txt) {
      var D = window.SFA_DATEC; if (!D) return { ok: false, reason: 'soon' };
      var dtm     = bookNum(book, 'days_to_maturity');
      var hwMax   = bookNum(book, 'harvest_window_max_days');
      var nursery = bookNum(book, 'days_in_nursery', 'days_in_nursery_cell');
      var pm      = (txt && txt.planting_method) || '';
      if (g.kind === 'sow_date') {
        var target = dateInputVal('target');
        if (!target)     return { ok: false, reason: 'input', need: 'תאריך יעד לקטיף' };
        if (dtm == null) return { ok: false, reason: 'nodata' };
        var r = D.sowDate(target, dtm, pm, nursery);
        if (!r) return { ok: false, reason: 'nodata' };
        return { ok: true, type: 'date', date: D.fmt(r.sow), goal: g,
          anchorText: 'יעד ' + D.fmt(D.parse(target)) + ' − ' + dtm + ' ימי הבשלה' +
            (D.isTransplant(pm) && nursery != null ? ' − ' + nursery + ' ימי משתלה' : ' (זריעה ישירה)') };
      }
      if (g.kind === 'harvest') {
        var sow = dateInputVal('sow');
        if (!sow)                       return { ok: false, reason: 'input', need: 'תאריך זריעה' };
        if (dtm == null || hwMax == null) return { ok: false, reason: 'nodata' };
        var h = D.harvestWindow(sow, dtm, hwMax, pm, nursery);
        if (!h) return { ok: false, reason: 'nodata' };
        return { ok: true, type: 'range', start: D.fmt(h.start), end: D.fmt(h.end), goal: g,
          anchorText: 'זריעה ' + D.fmt(D.parse(sow)) + ' + ' + dtm + ' ימים · חלון ' + hwMax + ' ימים' };
      }
      if (g.kind === 'succession') {
        var first = dateInputVal('sow');
        if (!first)        return { ok: false, reason: 'input', need: 'תאריך זריעה ראשונה' };
        if (hwMax == null) return { ok: false, reason: 'nodata' };
        var cntEl = scope.querySelector('[data-k="succ_count"]');
        var cnt = cntEl ? parseInt(cntEl.value, 10) : 5;
        if (!isFinite(cnt) || cnt < 1) cnt = 5;
        var sc = D.succession(first, hwMax, { count: cnt });
        if (!sc || !sc.dates.length) return { ok: false, reason: 'nodata' };
        var fmtd = sc.dates.map(function (ms) { return D.fmt(ms); });
        return { ok: true, type: 'list', dates: fmtd, goal: g,
          anchorText: 'מ-' + D.fmt(D.parse(first)) + ' · כל ' + sc.intervalWeeks + ' שבועות · ' + fmtd.length + ' מחזורים' };
      }
      return { ok: false, reason: 'soon' };   // nursery/frost wired in later slices
    }

    function runEngine() {
      var g = goals[state.goal] || {};
      if (g.soon) return { ok: false, reason: 'soon' };

      var slug0 = cropSel ? cropSel.value : '';
      if (g.shape === 'date' || g.shape === 'range' || g.shape === 'list') {
        var bookD = (window.SFA_CROP_BOOK     && slug0) ? (window.SFA_CROP_BOOK[slug0]     || {}) : {};
        var txtD  = (window.SFA_CROP_BOOK_TXT && slug0) ? (window.SFA_CROP_BOOK_TXT[slug0] || {}) : {};
        return runDateGoal(g, bookD, txtD);
      }
      if (!g.kind || !engine) return { ok: false, reason: 'soon' };

      // 1 · push book values for the selected crop into the engine chips.
      var slug = cropSel ? cropSel.value : '';
      var bookData = (window.SFA_CROP_BOOK && slug) ? (window.SFA_CROP_BOOK[slug] || {}) : {};
      var flat = {};
      Object.keys(bookData).forEach(function (fn) {
        var key = QB_BOOK_ALIAS[fn];
        if (key) { var v = parseFloat(bookData[fn]); if (isFinite(v)) flat[key] = v; }
      });
      engine.querySelectorAll('[data-book]').forEach(function (el) {
        var k = el.getAttribute('data-book');
        if (flat[k] != null) el.setAttribute('data-val', flat[k]);
      });

      // 2 · map the chosen basis number onto the operand(s) the CALC reads.
      var basisInp = scope.querySelector('[data-basis-input="' + effectiveBasisInput() + '"] input');
      var basisVal = basisInp ? parseFloat(basisInp.value) : NaN;
      var std = (window.SFA_ASSUMPTIONS && window.SFA_ASSUMPTIONS.std_bed_length_m) || 30;
      // area in running-metres of bed; if basis=beds, area = beds × std bed length.
      var meters = isFinite(basisVal) ? basisVal : 0;
      if (effectiveBasisInput() === 'beds') meters = basisVal * std;
      function setK(k, v) { var el = engine.querySelector('[data-k="' + k + '"]'); if (el) el.value = v; }
      setK('bed_len', meters);
      setK('area', meters);
      setK('area_m2', meters);
      if (effectiveBasisInput() === 'target' && isFinite(basisVal)) setK('target_kg', basisVal);

      // 3 · set the kind + recompute via the EXISTING engine, then read result.
      engine.setAttribute('data-calc', g.kind);
      recompute(engine);
      var rEl = engine.querySelector('[data-result]');
      var main = rEl ? (rEl.textContent || '').replace(/\s+/g, ' ').trim() : '';
      // strip the trailing unit word recompute() appended (we re-add g.runit)
      return { ok: true, type: 'scalar', main: main, unit: g.runit || '', goal: g };
    }

    function breakRow(k, v, src) {
      return '<div class="qb-break__row"><span class="k">' + k +
        '</span><span><span class="v num" dir="ltr" style="unicode-bidi:isolate">' + v +
        '</span> <span class="src dir-ltr">' + src + '</span></span></div>';
    }

    function renderBreakdown(g) {
      var box = document.getElementById('qb-break');
      if (!box) return;
      var rows = '';
      var basisLbl = { area: 'שטח לגידול', beds: 'מספר ערוגות', seedlings: 'מספר שתילים', target: 'יעד יבול' }[effectiveBasisInput()] || 'בסיס';
      var basisInp = scope.querySelector('[data-basis-input="' + effectiveBasisInput() + '"] input');
      rows += breakRow(basisLbl, basisInp ? basisInp.value : '—', 'קלט');
      var slug = cropSel ? cropSel.value : '';
      var bookData = (window.SFA_CROP_BOOK && slug) ? (window.SFA_CROP_BOOK[slug] || {}) : {};
      var bookLabels = {
        rows_per_bed: 'שורות לערוגה', spacing_in_row_cm: 'מרווח בשורה',
        seeds_per_g: 'זרעים לגרם', yield_per_bed_m: 'יבול למ׳',
        price_documented: 'מחיר מתועד', nutrient_removal_n_kg_per_ha: 'צריכת חנקן',
        days_to_maturity: 'ימים להבשלה', harvest_window_max_days: 'חלון קטיף (ימים)'
      };
      Object.keys(bookData).forEach(function (fn) {
        if (bookLabels[fn] != null) rows += breakRow(bookLabels[fn], bookData[fn], 'ספר');
      });
      var A = window.SFA_ASSUMPTIONS || {};
      if (g.kind === 'seed') {
        rows += breakRow('שיעור נביטה', Math.round((A.germination_rate || 0.9) * 100) + '%', 'הנחה');
        rows += breakRow('תוספת ביטחון', '+' + Math.round(((A.oversow || 1.1) - 1) * 100) + '%', 'הנחה');
      }
      box.innerHTML = rows;
    }

    function renderSession() {
      var list = qbReadSession();
      var box = document.getElementById('qb-session');
      var rowsEl = document.getElementById('qb-session-rows');
      var badge = document.getElementById('qb-session-badge');
      if (!box || !rowsEl) return;
      if (!list.length) { box.hidden = true; return; }
      box.hidden = false;
      if (badge) badge.textContent = list.length + ' חישובים · נשמר';
      rowsEl.innerHTML = list.map(function (r, i) {
        var cur = (i === list.length - 1) ? ' is-current' : '';
        return '<div class="qb-session__row' + cur + '"><span class="k"><b>' +
          r.label + '</b>' + r.sub + '</span><span class="v">' + r.value + '</span></div>';
      }).join('');
    }

    function pushSession(entry) {
      var list = qbReadSession();
      list.push(entry);
      if (list.length > 30) list = list.slice(-30);
      qbWriteSession(list);
      renderSession();
    }

    function showResult() {
      var g = goals[state.goal] || {};
      var soonBox = document.getElementById('qb-soon');
      var answer  = document.getElementById('qb-answer');
      var breakBox = document.getElementById('qb-break');
      var qEl = document.getElementById('qb-result-q');
      var cn = cropName();
      if (qEl) qEl.textContent = [g.label, cn, basisPhrase()].filter(Boolean).join(' · ');

      var out = runEngine();
      var lbl = document.getElementById('qb-answer-lbl');
      var big = document.getElementById('qb-answer-big');

      if (!out.ok && out.reason === 'input') {
        // missing a date the user must enter — prompt, don't fabricate or say "coming soon"
        if (soonBox) soonBox.hidden = true;
        if (answer) answer.hidden = false;
        if (lbl) lbl.textContent = g.rlabel || 'תוצאה';
        if (big) big.innerHTML = '<div style="font-size:16px;color:var(--gj-ink-soft)">↑ הזינו <b>' +
          (out.need || 'תאריך') + '</b> בשלב «עוגן זמן» ולחצו «חשב».</div>';
        if (breakBox) breakBox.hidden = true;
        scope.setAttribute('data-calc-state', 'result');
        renderSession();
        try { window.scrollTo(0, 0); } catch (e) {}
        return;
      }
      if (!out.ok) {
        // soon (not built) OR nodata (no book data for this crop) — honest, no fabricated number
        if (soonBox) {
          soonBox.hidden = false;
          var nm = document.getElementById('qb-soon-name');
          if (nm) nm.textContent = out.reason === 'nodata'
            ? ('«' + (g.label || '') + '» לגידול זה')
            : ('«' + (g.label || '') + '»');
        }
        if (answer) answer.hidden = true;
        if (breakBox) breakBox.hidden = true;
        scope.setAttribute('data-calc-state', 'result');
        renderSession();
        try { window.scrollTo(0, 0); } catch (e) {}
        return;
      }

      if (soonBox) soonBox.hidden = true;
      if (answer) answer.hidden = false;
      if (breakBox) breakBox.hidden = false;
      if (lbl) lbl.textContent = g.rlabel || 'תוצאה';

      var ltr = function (s) { return '<span dir="ltr" style="unicode-bidi:isolate">' + s + '</span>'; };
      var anchorLine = out.anchorText
        ? '<div style="font-size:13px;color:var(--gj-ink-soft);font-weight:400;margin-top:6px">' + out.anchorText + '</div>' : '';
      var sessionVal;
      if (out.type === 'date') {
        if (big) big.innerHTML = ltr(out.date) + anchorLine;
        sessionVal = out.date;
      } else if (out.type === 'range') {
        if (big) big.innerHTML = ltr(out.start + ' – ' + out.end) + anchorLine;
        sessionVal = out.start + '–' + out.end;
      } else if (out.type === 'list') {
        var items = out.dates.map(function (d, i) {
          return '<div style="display:flex;gap:8px;align-items:center;font-size:16px;margin:3px 0">' +
            '<b style="min-width:1.6em">' + (i + 1) + '.</b> ' + ltr(d) + '</div>';
        }).join('');
        if (big) big.innerHTML = items + anchorLine;
        sessionVal = out.dates.length + ' זריעות מ-' + out.dates[0];
      } else {
        // scalar — recompute() wrote "<value> <small>unit</small>" into [data-result];
        // surface [data-extra] as a secondary line (e.g. #9 revenue's ₪ value — quantity-first, QA F-01).
        var rEl = engine.querySelector('[data-result]');
        var exEl = engine.querySelector('[data-extra]');
        var exTxt = exEl ? (exEl.textContent || '').trim() : '';
        var secLine = exTxt
          ? '<div style="font-size:13px;color:var(--gj-ink-soft);font-weight:400;margin-top:6px">' + exTxt + '</div>' : '';
        if (big) big.innerHTML = (rEl ? rEl.innerHTML : (out.main || '—')) + secLine;
        sessionVal = (rEl ? (rEl.textContent || '').replace(/\s+/g, ' ').trim() : out.main) || '—';
      }

      renderBreakdown(g);

      pushSession({
        label: g.rlabel || g.label,
        sub:   [cn, basisPhrase()].filter(Boolean).join(' · '),
        value: sessionVal
      });

      scope.setAttribute('data-calc-state', 'result');
      try { window.scrollTo(0, 0); } catch (e) {}
    }

    /* ── single-select chip groups ── */
    function wireGroup(grp, attr, onPick) {
      if (!grp) return;
      grp.addEventListener('click', function (e) {
        var b = e.target.closest('button');
        if (!b) return;
        grp.querySelectorAll('button').forEach(function (x) { x.classList.remove('is-on'); });
        b.classList.add('is-on');
        onPick(b.getAttribute(attr));
      });
    }

    wireGroup(goalGrid, 'data-goal', function (v) {
      state.goal = v;
      if (moreSel) moreSel.value = '';   // primary pick clears the dropdown
      showBasisInput(); showGoalInput(); updateEcho();
    });
    wireGroup(basisGrp, 'data-basis', function (v) { state.basis = v; showBasisInput(); updateEcho(); });
    wireGroup(anchorGrp, 'data-anchor', function (v) { state.anchor = v; showAnchorInput(); updateEcho(); });

    if (moreSel) {
      moreSel.addEventListener('change', function () {
        if (!moreSel.value) return;
        state.goal = moreSel.value;
        if (goalGrid) goalGrid.querySelectorAll('button').forEach(function (x) { x.classList.remove('is-on'); });
        showBasisInput(); showGoalInput(); updateEcho();
      });
    }
    if (cropSel) cropSel.addEventListener('change', updateEcho);
    scope.querySelectorAll('[data-basis-input] input, [data-anchor-input] input').forEach(function (el) {
      el.addEventListener('input', updateEcho);
    });

    var go = document.getElementById('qb-go');
    if (go) go.addEventListener('click', showResult);
    var back = document.getElementById('qb-back');
    if (back) back.addEventListener('click', function () {
      scope.setAttribute('data-calc-state', 'ask');
      try { window.scrollTo(0, 0); } catch (e) {}
    });

    /* ── assumptions editor: open the EXISTING AssumptionField block ── */
    var assumEdit = document.getElementById('qb-assum-edit');
    var assumEditor = document.getElementById('qb-assum-editor');
    if (assumEdit && assumEditor) {
      assumEdit.addEventListener('click', function () {
        var open = assumEditor.hidden;
        assumEditor.hidden = !open;
        assumEdit.setAttribute('aria-expanded', open ? 'true' : 'false');
        if (open) try { assumEditor.scrollIntoView({ behavior: 'smooth', block: 'nearest' }); } catch (e) {}
      });
    }

    /* ── export = WHOLE session → existing /calc/print + /calc/export.csv ── */
    function exportHref(base) {
      var list = qbReadSession();
      var p = [];
      list.forEach(function (r, i) {
        var label = (i + 1) + '. ' + r.label + (r.sub ? ' (' + r.sub + ')' : '');
        p.push('rows[' + encodeURIComponent(label) + ']=' + encodeURIComponent(r.value));
      });
      return p.length ? base + '?' + p.join('&') : base;
    }
    ['qb-export-pdf', 'qb-export-csv'].forEach(function (id) {
      var a = document.getElementById(id);
      if (!a) return;
      var base = a.getAttribute('href');
      a.addEventListener('click', function () { a.setAttribute('href', exportHref(base)); });
    });

    /* ── sensible default anchor dates so date goals compute out of the box ── */
    (function setDateDefaults() {
      function iso(d) { return d.toISOString().slice(0, 10); }
      var now = new Date();
      var sEl = scope.querySelector('[data-k="sow_date"]');
      var tEl = scope.querySelector('[data-k="target_date"]');
      if (sEl && !sEl.value) sEl.value = iso(now);
      if (tEl && !tEl.value) tEl.value = iso(new Date(now.getTime() + 90 * 86400000));
    })();

    /* ── deep-link ?state=result + initial paint ── */
    showBasisInput(); showAnchorInput(); showGoalInput(); updateEcho(); renderSession();
    try {
      var params = new URLSearchParams(location.search);
      if (params.get('state') === 'result') scope.setAttribute('data-calc-state', 'result');
    } catch (e) {}
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
    wireQuestionBuilder();
  });
})();
