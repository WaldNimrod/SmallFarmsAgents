/* ============================================================
   SFA Crop Book v1 — LOD300 interaction layer (vanilla)
   Maps 1:1 to "light JS for interactive calculators" (Slim4/PHP tier).
   ============================================================ */
(function () {
  'use strict';

  /* ── Assumption registry (mirrors assumptions.py defaults) ── */
  var A = {
    germination_rate: 0.90,
    oversow: 1.10,
    bed_width: 0.80,
    compost_N_pct: 0.015,
    application_efficiency: 0.50,
    std_bed_length_m: 30
  };

  var fmt = function (n, d) {
    if (!isFinite(n)) return '—';
    d = d == null ? 0 : d;
    return n.toLocaleString('he-IL', { minimumFractionDigits: d, maximumFractionDigits: d });
  };

  /* ── Calculator formulas, keyed by data-calc ── */
  var CALC = {
    // #1 seed quantity to buy
    seed: function (g, book) {
      var len = g.bed_len, sph = g.seeds_per_hole;
      var plants = (len * 100 / book.spacing) * book.rows * sph;
      var seeds = plants / A.germination_rate * A.oversow;
      var grams = seeds / book.seeds_per_gram;
      return {
        main: fmt(grams, 1), unit: 'גרם',
        formula: 'plants ' + fmt(plants) + ' / germ ' + Math.round(A.germination_rate * 100) + '% × oversow ' + A.oversow + ' ÷ ' + book.seeds_per_gram + ' seeds/g',
        extra: fmt(seeds) + ' זרעים · ' + fmt(plants) + ' צמחים'
      };
    },
    // #8 expected yield
    yield: function (g, book) {
      var kg = book.yield_per_m * g.bed_len;
      return { main: fmt(kg, 1), unit: 'ק״ג', formula: g.bed_len + ' m × ' + book.yield_per_m + ' kg/m' };
    },
    // #9 expected revenue
    revenue: function (g, book) {
      var kg = book.yield_per_m * g.area;
      var rev = kg * book.price;
      return { main: fmt(rev), unit: '₪', formula: fmt(kg, 0) + ' kg × ' + book.price + ' ₪/kg', extra: 'יבול ' + fmt(kg, 0) + ' ק״ג' };
    },
    // #10 plant population / layout
    pop: function (g, book) {
      var perM2 = (book.rows / A.bed_width) * (100 / book.spacing);
      return { main: fmt(perM2, 1), unit: 'צמ׳/מ״ר', formula: '(' + book.rows + ' rows / ' + A.bed_width + ' m) × (100 / ' + book.spacing + ' cm)', perM2: perM2 };
    },
    // #11 frost / planting window
    frost: function (g, book) {
      var off = book.hardiness_offset;
      var earliest = addDays(g.last_frost, -off);
      var latest = addDays(g.first_frost, -book.dtm);
      return { main: heDate(earliest), unit: '', formula: 'last_frost − ' + off + 'd … first_frost − DTM ' + book.dtm + 'd', extra: 'חלון שתילה עד ' + heDate(latest) };
    },
    // #12 fertilizer / compost
    fert: function (g, book) {
      var areaHa = g.area / 10000;
      var nKg = book.n * areaHa;
      var compostKg = nKg / (A.compost_N_pct * A.application_efficiency);
      return { main: fmt(compostKg, 0), unit: 'ק״ג קומפוסט', formula: 'N ' + fmt(nKg, 1) + ' kg ÷ (' + (A.compost_N_pct * 100) + '% × eff ' + A.application_efficiency + ')', extra: 'N ' + fmt(nKg, 1) + ' · P ' + fmt(book.p * areaHa, 1) + ' · K ' + fmt(book.k * areaHa, 1) + ' ק״ג' };
    }
  };

  function addDays(d, n) { var x = new Date(d.getTime()); x.setDate(x.getDate() + n); return x; }
  function heDate(d) { return d.getDate() + '/' + (d.getMonth() + 1); }

  function readBook(panel) {
    var book = {};
    panel.querySelectorAll('[data-book]').forEach(function (el) {
      var inp = el.querySelector('.bv__in');
      book[el.getAttribute('data-book')] = parseFloat(inp ? inp.value : el.getAttribute('data-val'));
    });
    // date book fields
    if (panel.dataset.lastFrost) book.last_frost = new Date(panel.dataset.lastFrost);
    return book;
  }

  function recompute(panel) {
    var kind = panel.getAttribute('data-calc');
    if (!CALC[kind] || panel.classList.contains('is-disabled')) return;
    var g = {};
    panel.querySelectorAll('[data-k]').forEach(function (el) {
      var v = el.value;
      g[el.getAttribute('data-k')] = el.type === 'date' ? new Date(v) : parseFloat(v);
    });
    var book = readBook(panel);
    if (kind === 'frost') { g.last_frost = new Date(panel.dataset.lastFrost); g.first_frost = new Date(panel.dataset.firstFrost); }

    var out;
    try { out = CALC[kind](g, book); } catch (e) { return; }
    var rEl = panel.querySelector('[data-result]');
    if (rEl) rEl.innerHTML = out.main + (out.unit ? ' <small>' + out.unit + '</small>' : '');
    var fEl = panel.querySelector('[data-formula]');
    if (fEl) fEl.textContent = out.formula;
    var eEl = panel.querySelector('[data-extra]');
    if (eEl && out.extra != null) eEl.textContent = out.extra;

    // #10 population grid render
    if (kind === 'pop') {
      var grid = panel.querySelector('[data-popgrid]');
      if (grid) {
        var cols = Math.max(2, Math.round(book.rows));
        var per = Math.min(48, Math.max(8, Math.round(out.perM2)));
        grid.style.gridTemplateColumns = 'repeat(' + cols + ', 1fr)';
        grid.innerHTML = '';
        for (var i = 0; i < cols * Math.ceil(per / cols); i++) grid.appendChild(document.createElement('i'));
      }
    }
  }

  function recomputeAll() {
    document.querySelectorAll('[data-calc]').forEach(recompute);
  }

  /* ── AssumptionField: expand / override / reset ── */
  function wireAssumptions() {
    document.querySelectorAll('.af').forEach(function (af) {
      var bar = af.querySelector('.af__bar');
      bar.addEventListener('click', function (e) {
        if (e.target.closest('.af__body')) return;
        af.classList.toggle('is-open');
      });
      var input = af.querySelector('[data-assume]');
      if (input) {
        var key = input.getAttribute('data-assume');
        var scale = parseFloat(input.getAttribute('data-scale') || '1');
        input.addEventListener('input', function () {
          var v = parseFloat(input.value);
          if (isFinite(v)) { A[key] = v * scale; updateAssumeChips(key, input.value, input); recomputeAll(); }
        });
        var reset = af.querySelector('[data-reset]');
        if (reset) reset.addEventListener('click', function () {
          input.value = reset.getAttribute('data-default');
          A[key] = parseFloat(reset.getAttribute('data-default')) * scale;
          updateAssumeChips(key, input.value, input);
          recomputeAll();
        });
      }
    });
  }
  function updateAssumeChips(key, display, input) {
    document.querySelectorAll('[data-assume-echo="' + key + '"]').forEach(function (el) {
      el.textContent = display + (input.getAttribute('data-suffix') || '');
    });
  }

  /* ── Calculator inputs ── */
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
      var scope = document.getElementById(sw.getAttribute('data-aud-switch'));
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
    });
  }

  /* ── Depth tabs (Simple / Full / Drill-down) ── */
  function wireDepths() {
    document.querySelectorAll('[data-depths]').forEach(function (tabs) {
      var scope = document.getElementById(tabs.getAttribute('data-depths'));
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

  /* ── Collapsible advanced filter (default closed) ── */
  function wireFilterCollapse() {
    document.querySelectorAll('[data-filter-toggle]').forEach(function (btn) {
      var box = document.getElementById(btn.getAttribute('data-filter-toggle'));
      btn.addEventListener('click', function () {
        var open = box.classList.toggle('is-open');
        btn.classList.toggle('is-open', open);
        btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      });
    });
  }

  /* ── Pagination (25/page default) ── */
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

  /* ── Collapsible topic sections (Full depth) ── */
  function wireTopics() {
    document.querySelectorAll('.topic__head').forEach(function (h) {
      h.addEventListener('click', function () { h.closest('.topic').classList.toggle('is-collapsed'); });
    });
  }

  /* ── Calculator module overlay (small calcs open over the page) ── */
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
  }

  /* ── Hebrew field dictionary — name + full explainer for every field ── */
  var FIELD_INFO = {
    days_to_maturity:      ['ימים להבשלה', 'מספר הימים מהזריעה או השתילה ועד תחילת הקציר. בסיס לכל חישובי התאריכים.', 'days_to_maturity'],
    harvest_window:        ['חלון קציר', 'כמה ימים נמשך הקציר מרגע ההבשלה הראשונה ועד סוף האיסוף.', 'harvest_window_max_days'],
    in_row_spacing_cm:     ['מרווח בשורה', 'המרחק בין צמח לצמח לאורך השורה, בסנטימטרים. קובע צפיפות וכמות זרעים.', 'in_row_spacing_cm'],
    rows_per_bed:          ['שורות בערוגה', 'כמה שורות צמחים נכנסות ברוחב ערוגה אחת (רוחב סטנדרטי 80 ס״מ).', 'rows_per_bed'],
    avg_yield_per_bed_m:   ['יבול ממוצע', 'קילוגרם תוצרת למטר ערוגה — ממוצע. בסיס לחישובי יבול, הכנסה ורווח.', 'avg_yield_per_bed_m'],
    documented_price:      ['מחיר מתועד', 'מחיר השוק האחרון שתועד, ליחידת המכירה (ק״ג / אגודה / יחידה).', 'documented_price'],
    planting_season:       ['עונת גידול', 'העונות שבהן מומלץ לזרוע או לשתול את הגידול בארץ.', 'planting_season'],
    planting_method:       ['שיטת שתילה', 'זריעה ישירה בשדה, או גידול שתיל במשתלה ואז שתילה — משפיע על לוח הזמנים.', 'planting_method'],
    frost_tolerance:       ['עמידות לקרה', 'רגישות הגידול לקרה: עמיד / חצי-עמיד / רגיש / רגיש מאוד. קובע את חלון השתילה.', 'frost_tolerance_class'],
    seeds_per_gram:        ['זרעים לגרם', 'כמה זרעים יש בגרם אחד — ממיר את מספר הצמחים לכמות זרעים לקנייה.', 'seeds_per_gram'],
    days_in_nursery_cell:  ['ימים במשתלה', 'כמה ימים השתיל גדל במשתלה לפני שתילה בשדה. נדרש לחישוב תאריך זריעה.', 'days_in_nursery_cell'],
    succession_interval:   ['מרווח זריעה הדרגתית', 'כל כמה שבועות לזרוע מנה חדשה, לקבלת קציר רציף לאורך העונה.', 'succession_interval_weeks'],
    nutrient_removal_N:    ['צריכת חנקן (N)', 'כמות החנקן שהגידול מוציא מהקרקע, ק״ג להקטר. בסיס לחישוב הדישון.', 'nutrient_removal_n_kg_ha'],
    family:                ['משפחה בוטנית', 'המשפחה הבוטנית של הגידול — בסיס לרמז מחזור הגידולים בערוגה.', 'family'],
    needs_summer_shade:    ['דורש הצללה בקיץ', 'ייחודי לאקלים הים-תיכוני: גידולים מסוימים (חסה, עלים ירוקים) זקוקים לרשת צל בחודשי הקיץ החמים — אחרת הם עולים לזרע או נכווים. שלוש רמות צל: 30% / 40% / 50% לפי רגישות הגידול. שדה ישראלי שאין במקורות זרים.', 'needs_summer_shade'],
    irrigation_type:       ['סוג השקיה', 'אופן ההשקיה — טפטוף (מספר קווים לערוגה) או ממטרות. שדה מוצע, נגזר ממבנה דף ה-JMF.', 'irrigation_type'],
    root_depth_class:      ['עומק שורשים', 'סיווג עומק בית השורשים (רדוד / בינוני / עמוק) + טווח ס״מ — קובע משטר השקיה. שדה מוצע מ-JMF.', 'root_depth_class'],
    sale_unit:             ['יחידת מכירה', 'היחידה הנמכרת בפועל: ראש / אגודה (מספר גבעולים) / ק״ג / יחידה. בסיס לחישובי מחיר והכנסה. שדה מוצע מ-JMF.', 'sale_unit'],
    labor_rate_harvest:    ['תפוקת קציר', 'כמה יחידות אדם אחד קוצר בשעה — בסיס לתכנון כוח אדם ועלות עבודה. שדה מוצע מ-JMF.', 'labor_rate_harvest_per_hour'],
    storage_days:          ['חיי מדף', 'כמה ימים ניתן לאחסן בחדר קירור (2°C) לפני מכירה. שדה מוצע מ-JMF.', 'storage_max_days'],
    common_pests:          ['מזיקים נפוצים', 'מזיקים ומחלות עיקריים + אמצעי הגנה (רשת אנטי-חרקים, מנהרות). שדה מוצע מ-JMF.', 'common_pests'],
    foliar_program:        ['הזנה עלוותית', 'תוכנית ריסוס עלוותי (בורון, אצות, תה קומפוסט) לחיזוק הצמח. שדה מוצע מ-JMF.', 'foliar_feeding_program'],
    dtm:                   ['ימים להבשלה', 'מספר הימים מזריעה/שתילה ועד תחילת הקציר.', 'days_to_maturity'],
    yield:                 ['יבול', 'קילוגרם תוצרת למטר ערוגה — ממוצע לזן.', 'avg_yield_per_bed_m'],
    spacing:               ['מרווח', 'המרחק בין צמח לצמח בשורה, ס״מ.', 'in_row_spacing_cm'],
    price:                 ['מחיר', 'מחיר השוק המתועד האחרון.', 'documented_price'],
    germination_rate:      ['אחוז נביטה', 'הנחת תכנון: שיעור הזרעים שינבטו. ברירת מחדל 90%.', 'germination_rate'],
    bed_width:             ['רוחב ערוגה', 'הנחת תכנון: רוחב ערוגה סטנדרטי. ברירת מחדל 80 ס״מ.', 'bed_width']
  };

  function injectFieldInfo() {
    document.querySelectorAll('[data-field]').forEach(function (el) {
      var info = FIELD_INFO[el.getAttribute('data-field')];
      if (!info) return;
      if (el.textContent.trim() === '') el.textContent = info[0];
      var f = document.createElement('span');
      f.className = 'finfo'; f.tabIndex = 0; f.innerHTML = 'ⓘ';
      var pop = document.createElement('span');
      pop.className = 'tip__pop';
      pop.innerHTML = '<b>' + info[0] + '</b>' + info[1] + '<span class="k">' + info[2] + '</span>';
      f.appendChild(pop);
      el.appendChild(f);
    });
  }

  /* ── Editable book value (#10 — user overrides, clearly marked) ── */
  function wireBookEdits() {
    document.querySelectorAll('.bv__in').forEach(function (inp) {
      var chip = inp.closest('.bv');
      var panel = inp.closest('[data-calc]');
      var orig = inp.getAttribute('data-orig') || inp.value;
      function sync() {
        chip.classList.toggle('is-overridden', parseFloat(inp.value) !== parseFloat(orig));
        chip.setAttribute('data-val', inp.value);
        if (panel) recompute(panel);
      }
      inp.addEventListener('input', sync);
      var restore = chip.querySelector('.bv__restore');
      if (restore) restore.addEventListener('click', function () { inp.value = orig; sync(); });
    });
  }

  /* ── Filter chips (multi-parameter search) + reset ── */
  function wireFilters() {
    document.querySelectorAll('.fchip').forEach(function (c) {
      c.addEventListener('click', function () {
        if (c.dataset.single) {
          c.parentNode.querySelectorAll('.fchip').forEach(function (s) { s.classList.remove('is-on'); });
          c.classList.add('is-on');
        } else { c.classList.toggle('is-on'); }
      });
    });
    document.querySelectorAll('[data-filter-reset]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var scope = btn.closest('.ftop') || document;
        scope.querySelectorAll('.fchip').forEach(function (c) {
          c.classList.toggle('is-on', c.hasAttribute('data-default-on'));
        });
        scope.querySelectorAll('.filters__search input, .fdate').forEach(function (i) { i.value = ''; });
        scope.querySelectorAll('.ftop__count b').forEach(function (cnt) { cnt.textContent = '66'; });
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
  });
})();
