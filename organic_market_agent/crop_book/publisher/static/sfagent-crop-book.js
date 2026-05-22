/**
 * sfagent-crop-book.js — ספר גידולים SPA
 * Vanilla JS, ES2018 baseline, no external dependencies.
 * Filter semantics must mirror Flask /api/crops (views.py:234-304).
 */
(function () {
  'use strict';

  const ROOT = document.querySelector('.sfa-crop-book');
  if (!ROOT) return;

  let DATA = null;
  let currentCropId = null;

  // Season token map (mirrors views.py season_map + SEASON_TOKENS)
  const SEASON_MAP = {
    summer: ['קיץ', 'summer'],
    spring: ['אביב', 'spring'],
    winter: ['חורף', 'winter'],
    fall:   ['סתיו', 'fall', 'autumn'],
  };

  // ---------------------------------------------------------------------------
  // Bootstrap
  // ---------------------------------------------------------------------------

  fetch(window.CROP_BOOK_DATA_URL)
    .then(function (r) { return r.json(); })
    .then(function (data) {
      DATA = data;
      buildIndex();
      hookSearch();
      hookCategoryTabs();
      hookSeasonFilters();
      hookDtmSlider();
      window.addEventListener('hashchange', routeFromHash);
      routeFromHash();
    })
    .catch(function (err) {
      ROOT.innerHTML = '<p class="sfa-crop-book-error">שגיאה בטעינת ספר גידולים</p>';
      console.error('Crop book data fetch failed:', err);
    });

  // ---------------------------------------------------------------------------
  // Default variety selection (mirrors views.py:268-271)
  // ---------------------------------------------------------------------------

  function defaultVar(crop) {
    if (!crop.varieties || crop.varieties.length === 0) return null;
    var dv = crop.varieties.find(function (v) { return v.is_default; });
    return dv || crop.varieties[0];
  }

  // ---------------------------------------------------------------------------
  // Filter engine (mirrors views.py:234-304 exactly)
  // ---------------------------------------------------------------------------

  function filterCrops(opts) {
    var q        = (opts.q || '').trim().toLowerCase();
    var category = opts.category || '';
    var seasons  = opts.seasons  || [];
    var dtmMax   = opts.dtmMax   != null ? parseInt(opts.dtmMax, 10) : null;

    return DATA.crops.filter(function (crop) {
      // Category filter (views.py:252-253)
      if (category && category !== 'all' && crop.category !== category) return false;

      // Text search — ilike on name_he | name_en | scientific_name (views.py:255-262)
      if (q) {
        var inHe  = (crop.name_he  || '').toLowerCase().indexOf(q) !== -1;
        var inEn  = (crop.name_en  || '').toLowerCase().indexOf(q) !== -1;
        var inSci = (crop.scientific_name || '').toLowerCase().indexOf(q) !== -1;
        if (!inHe && !inEn && !inSci) return false;
      }

      var dv = defaultVar(crop);

      // DTM filter (views.py:273-279)
      if (dtmMax !== null && !isNaN(dtmMax)) {
        var dtm = dv ? dv.days_to_maturity : null;
        if (dtm === null || dtm === undefined || dtm > dtmMax) return false;
      }

      // Season filter — OR logic (views.py:282-299, PATCH01 getlist)
      if (seasons.length > 0) {
        var planting = (dv && dv.planting_season) ? dv.planting_season.toLowerCase() : '';
        var matchesAny = seasons.some(function (s) {
          var tokens = SEASON_MAP[s] || [s];
          return tokens.some(function (t) {
            return planting.indexOf(t.toLowerCase()) !== -1;
          });
        });
        if (!matchesAny) return false;
      }

      return true;
    });
  }

  // ---------------------------------------------------------------------------
  // Read current filter state from DOM
  // ---------------------------------------------------------------------------

  function currentFilters() {
    var qEl       = ROOT.querySelector('.sfa-cb-search');
    var catActive = ROOT.querySelector('.sfa-cb-category-tabs button.active');
    var seasonEls = ROOT.querySelectorAll('.sfa-cb-seasons input[type=checkbox]:checked');
    var dtmEl     = ROOT.querySelector('.sfa-cb-dtm');

    var seasons = [];
    seasonEls.forEach(function (el) { seasons.push(el.dataset.season); });

    var dtmMax = null;
    if (dtmEl) {
      var v = parseInt(dtmEl.value, 10);
      if (v < parseInt(dtmEl.max || '365', 10)) dtmMax = v;
    }

    return {
      q:        qEl  ? qEl.value  : '',
      category: catActive ? (catActive.dataset.cat || '') : '',
      seasons:  seasons,
      dtmMax:   dtmMax,
    };
  }

  // ---------------------------------------------------------------------------
  // Index / grid
  // ---------------------------------------------------------------------------

  function buildIndex() {
    renderGrid(filterCrops(currentFilters()));
  }

  function renderGrid(crops) {
    var grid = ROOT.querySelector('.sfa-cb-grid');
    if (!grid) return;

    if (crops.length === 0) {
      grid.innerHTML = '<p class="sfa-cb-empty">לא נמצאו גידולים</p>';
      return;
    }

    var catLabels = DATA.categories || {};
    grid.innerHTML = crops.map(function (crop) {
      var dv       = defaultVar(crop);
      var catLabel = catLabels[crop.category] || crop.category;
      var dtm      = dv ? dv.days_to_maturity : null;
      var dtmStr   = dtm != null ? dtm + ' ימים' : '';
      return (
        '<article class="sfa-cb-card" data-id="' + crop.id + '" role="button" tabindex="0">' +
          '<h3 class="sfa-cb-card-name">' + _esc(crop.name_he || '') + '</h3>' +
          (crop.name_en ? '<p class="sfa-cb-card-en">' + _esc(crop.name_en) + '</p>' : '') +
          '<span class="sfa-cb-cat-badge sfa-cat-' + _esc(crop.category) + '">' + _esc(catLabel) + '</span>' +
          (dtmStr ? '<span class="sfa-cb-dtm-badge">' + dtmStr + '</span>' : '') +
        '</article>'
      );
    }).join('');

    grid.querySelectorAll('.sfa-cb-card').forEach(function (card) {
      card.addEventListener('click', function () {
        window.location.hash = '#crop-' + card.dataset.id;
      });
      card.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          window.location.hash = '#crop-' + card.dataset.id;
        }
      });
    });
  }

  // ---------------------------------------------------------------------------
  // Hooks
  // ---------------------------------------------------------------------------

  function hookSearch() {
    var el = ROOT.querySelector('.sfa-cb-search');
    if (!el) return;
    el.addEventListener('input', function () { buildIndex(); });
  }

  function hookCategoryTabs() {
    ROOT.querySelectorAll('.sfa-cb-category-tabs button').forEach(function (btn) {
      btn.addEventListener('click', function () {
        ROOT.querySelectorAll('.sfa-cb-category-tabs button').forEach(function (b) {
          b.classList.remove('active');
        });
        btn.classList.add('active');
        buildIndex();
      });
    });
  }

  function hookSeasonFilters() {
    ROOT.querySelectorAll('.sfa-cb-seasons input[type=checkbox]').forEach(function (el) {
      el.addEventListener('change', function () { buildIndex(); });
    });
  }

  function hookDtmSlider() {
    var el = ROOT.querySelector('.sfa-cb-dtm');
    if (!el) return;
    var label = ROOT.querySelector('.sfa-cb-dtm-label');
    el.addEventListener('input', function () {
      if (label) {
        var v = parseInt(el.value, 10);
        label.textContent = v >= parseInt(el.max || '365', 10) ? 'הכל' : v + ' ימים';
      }
      buildIndex();
    });
  }

  // ---------------------------------------------------------------------------
  // Hash routing (AC-05)
  // ---------------------------------------------------------------------------

  function routeFromHash() {
    var hash = window.location.hash || '';
    var match = hash.match(/^#crop-(\d+)$/);
    if (match) {
      var id = parseInt(match[1], 10);
      var crop = DATA.crops.find(function (c) { return c.id === id; });
      if (crop) {
        currentCropId = id;
        showDetail(crop);
        return;
      }
    }
    showIndex();
  }

  function showIndex() {
    currentCropId = null;
    var detail = ROOT.querySelector('.sfa-cb-detail');
    var grid   = ROOT.querySelector('.sfa-cb-grid');
    if (detail) detail.hidden = true;
    if (grid)   grid.hidden   = false;
    buildIndex();
  }

  function showDetail(crop) {
    var detail = ROOT.querySelector('.sfa-cb-detail');
    var grid   = ROOT.querySelector('.sfa-cb-grid');
    if (!detail) return;
    if (grid) grid.hidden = true;
    detail.hidden = false;

    // Crop name
    var nameEl = detail.querySelector('.sfa-cb-crop-name');
    if (nameEl) nameEl.textContent = crop.name_he || '';

    // Populate all 8 tabs
    populateVarietiesTab(crop, detail);
    populateDescriptionTab(crop, detail);
    populateEconomicsTab(crop, detail);
    populateCareTab(crop, detail);
    populateEquipmentTab(crop, detail);
    populateSourcesTab(crop, detail);
    populateTimelineTab(crop, detail);
    populateFieldDataTab(crop, detail);

    // Activate first visible tab
    activateFirstTab(detail);
  }

  // ---------------------------------------------------------------------------
  // Tab population (AC-06)
  // ---------------------------------------------------------------------------

  function _tabSection(detail, key) {
    return detail.querySelector('.sfa-cb-tab[data-tab="' + key + '"]');
  }

  function _tabBtn(detail, key) {
    return detail.querySelector('.sfa-cb-tabs button[data-tab="' + key + '"]');
  }

  function populateVarietiesTab(crop, detail) {
    var sec = _tabSection(detail, 'varieties');
    if (!sec) return;
    if (!crop.varieties || crop.varieties.length === 0) {
      sec.innerHTML = '<p class="sfa-cb-placeholder">אין זנים</p>';
      return;
    }
    sec.innerHTML = crop.varieties.map(function (v) {
      var star = v.is_default ? '<span class="sfa-cb-star" title="זן ברירת מחדל">★</span>' : '';
      var graft = v.is_grafted ? '<span class="sfa-cb-badge">מורכב</span>' : '';
      return (
        '<div class="sfa-cb-variety">' +
          '<h4>' + star + _esc(v.name_he || v.name_en || '') + graft + '</h4>' +
          (v.planting_season ? '<p>עונה: ' + _esc(v.planting_season) + '</p>' : '') +
          (v.days_to_maturity != null ? '<p>ימים לבגרות: ' + v.days_to_maturity + '</p>' : '') +
          (v.avg_yield_per_bed_m != null ? '<p>תשואה: ' + v.avg_yield_per_bed_m + ' ' + _esc(v.harvest_unit || '') + '/מ״ר</p>' : '') +
          (v.documented_price != null ? '<p>מחיר: ' + v.documented_price + ' ₪/' + _esc(v.documented_price_unit || '') + '</p>' : '') +
        '</div>'
      );
    }).join('');
  }

  function populateDescriptionTab(crop, detail) {
    var sec = _tabSection(detail, 'description');
    if (!sec) return;
    if (!crop.description) {
      sec.innerHTML = '<p class="sfa-cb-placeholder">אין תיאור</p>';
    } else {
      // Trust description HTML (may contain entity tags)
      sec.innerHTML = '<div class="sfa-cb-desc">' + crop.description + '</div>';
      // Wire entity tag tooltips
      sec.querySelectorAll('.etag[data-etype][data-eid]').forEach(function (span) {
        _wireEntityTooltip(span);
      });
    }
  }

  function populateEconomicsTab(crop, detail) {
    var sec = _tabSection(detail, 'economics');
    if (!sec) return;
    var dv = defaultVar(crop);
    if (!dv) {
      sec.innerHTML = '<p class="sfa-cb-placeholder">אין נתוני כלכלה</p>';
      return;
    }
    var html = '<div class="sfa-cb-economics">';
    if (dv.documented_price != null) {
      html += '<p><strong>מחיר מתועד:</strong> ' + dv.documented_price + ' ₪/' + _esc(dv.documented_price_unit || '') + '</p>';
      if (dv.documented_price_source) {
        html += '<p class="sfa-cb-source">מקור: ' + _esc(dv.documented_price_source) + '</p>';
      }
    }
    if (dv.avg_yield_per_bed_m != null) {
      html += '<p><strong>תשואה ממוצעת:</strong> ' + dv.avg_yield_per_bed_m + ' ' + _esc(dv.harvest_unit || '') + '/מ״ר</p>';
    }
    if (dv.avg_revenue_per_bed_m != null) {
      html += '<p><strong>הכנסה ממוצעת:</strong> ' + dv.avg_revenue_per_bed_m + ' ₪/מ״ר</p>';
    }
    if (!dv.pricebook_product_id) {
      html += '<p class="sfa-cb-placeholder">אין מחיר מחירון</p>';
    }
    html += '</div>';
    sec.innerHTML = html;
  }

  function populateCareTab(crop, detail) {
    var sec = _tabSection(detail, 'care');
    if (!sec) return;
    var dv = defaultVar(crop);
    var html = '<div class="sfa-cb-care">';
    if (dv) {
      if (dv.planting_method) html += '<p><strong>שיטת שתילה:</strong> ' + _esc(dv.planting_method) + '</p>';
      if (dv.in_row_spacing_cm != null) html += '<p><strong>מרווח בשורה:</strong> ' + dv.in_row_spacing_cm + ' ס״מ</p>';
      if (dv.rows_per_bed != null) html += '<p><strong>שורות ב-BED:</strong> ' + dv.rows_per_bed + '</p>';
      if (dv.succession_interval_weeks != null) html += '<p><strong>מחזור זריעה:</strong> ' + dv.succession_interval_weeks + ' שבועות</p>';
    }
    if (html === '<div class="sfa-cb-care">') html += '<p class="sfa-cb-placeholder">אין נתוני טיפולים</p>';
    html += '</div>';
    sec.innerHTML = html;
  }

  function populateEquipmentTab(crop, detail) {
    var sec = _tabSection(detail, 'equipment');
    var btn = _tabBtn(detail, 'equipment');
    if (!sec) return;

    var hasSeeder = crop.varieties && crop.varieties.some(function (v) {
      return v.seeder || v.seeder_front_gear || v.seeder_rear_gear || v.seeder_roller_plate;
    });

    // AC-07: hide tab when no seeder data
    if (!hasSeeder) {
      sec.style.display   = 'none';
      if (btn) btn.style.display = 'none';
      return;
    }
    if (btn) btn.style.display = '';
    sec.style.display = '';

    var html = '<div class="sfa-cb-equipment">';
    crop.varieties.forEach(function (v) {
      if (!v.seeder && !v.seeder_front_gear && !v.seeder_rear_gear && !v.seeder_roller_plate) return;
      html += '<div class="sfa-cb-seeder-row">';
      html += '<h4>' + _esc(v.name_he || v.name_en || '') + '</h4>';
      if (v.seeder)             html += '<p>מזרע: '        + _esc(v.seeder) + '</p>';
      if (v.seeder_front_gear)  html += '<p>גלגל קדמי: '  + _esc(v.seeder_front_gear) + '</p>';
      if (v.seeder_rear_gear)   html += '<p>גלגל אחורי: ' + _esc(v.seeder_rear_gear) + '</p>';
      if (v.seeder_roller_plate) html += '<p>לוחית: '      + _esc(v.seeder_roller_plate) + '</p>';
      html += '</div>';
    });
    html += '</div>';
    sec.innerHTML = html;
  }

  function populateSourcesTab(crop, detail) {
    var sec = _tabSection(detail, 'sources');
    if (!sec) return;

    var allSources = [];
    (crop.varieties || []).forEach(function (v) {
      (v.source_values || []).forEach(function (sv) {
        allSources.push(sv);
      });
    });

    if (allSources.length === 0) {
      sec.innerHTML = '<p class="sfa-cb-placeholder">אין נתוני מקורות</p>';
      return;
    }
    var html = '<div class="sfa-cb-sources"><table class="sfa-cb-src-table">' +
      '<thead><tr><th>שדה</th><th>מקור</th><th>ערך</th><th>יחידה</th></tr></thead><tbody>';
    allSources.forEach(function (sv) {
      var val = sv.value_numeric != null ? sv.value_numeric : (sv.value_text || '—');
      html += '<tr><td>' + _esc(sv.field_name) + '</td><td>' + _esc(sv.source) +
        '</td><td>' + _esc(String(val)) + '</td><td>' + _esc(sv.unit || '') + '</td></tr>';
    });
    html += '</tbody></table></div>';
    sec.innerHTML = html;
  }

  function populateTimelineTab(crop, detail) {
    var sec = _tabSection(detail, 'timeline');
    if (!sec) return;

    var dv = defaultVar(crop);

    // AC-08: timeline ruler — default variety only, null→0, max(1, ceil(hw/7))
    // Mirrors views.py:195-197 exactly.
    var hwMax      = (dv && dv.harvest_window_max_days) ? dv.harvest_window_max_days : 0;
    var totalWeeks = Math.max(1, Math.ceil(hwMax / 7));

    var dtm     = (dv && dv.days_to_maturity) ? dv.days_to_maturity : 0;
    var ghTotal = (dv && dv.days_in_gh_total) ? dv.days_in_gh_total : 0;
    var totalDays = dtm + hwMax;

    var html = '<div class="sfa-cb-timeline">';

    // Ruler ticks — exactly totalWeeks (not +1)
    html += '<div class="sfa-cb-ruler" aria-label="ציר זמן">';
    for (var w = 1; w <= totalWeeks; w++) {
      html += '<span class="sfa-cb-ruler-tick" data-week="' + w + '">' + w + '</span>';
    }
    html += '</div>';

    // Phase bars
    if (totalDays > 0) {
      html += '<div class="sfa-cb-phases">';
      var pct = function (days) { return (100.0 * days / Math.max(totalDays, 1)).toFixed(1); };
      if (ghTotal > 0) {
        html += '<div class="sfa-cb-phase" style="width:' + pct(ghTotal) + '%;background:#78909c" title="הכנה / חממה (' + ghTotal + ' ימים)">הכנה</div>';
      }
      var growDays = dtm - ghTotal;
      if (growDays > 0) {
        html += '<div class="sfa-cb-phase" style="width:' + pct(growDays) + '%;background:#43a047" title="גידול (' + growDays + ' ימים)">גידול</div>';
      }
      if (hwMax > 0) {
        html += '<div class="sfa-cb-phase" style="width:' + pct(hwMax) + '%;background:#fb8c00" title="חלון קציר (' + hwMax + ' ימים)">קציר</div>';
      }
      html += '</div>';
    }
    html += '</div>';
    sec.innerHTML = html;
  }

  function populateFieldDataTab(crop, detail) {
    var sec = _tabSection(detail, 'field-data');
    if (!sec) return;
    var dv = defaultVar(crop);
    var html = '<div class="sfa-cb-field-data">';
    if (dv) {
      if (dv.days_to_germinate_gh != null) html += '<p>ימי נביטה בחממה: ' + dv.days_to_germinate_gh + '</p>';
      if (dv.days_in_gh_total != null)     html += '<p>סה״כ ימים בחממה: ' + dv.days_in_gh_total + '</p>';
      if (dv.notes) html += '<p>' + _esc(dv.notes) + '</p>';
    }
    var conversions = (DATA.conversions || []).filter(function (cv) { return cv.crop_id === crop.id; });
    if (conversions.length > 0) {
      html += '<table class="sfa-cb-conv-table"><thead><tr><th>מ</th><th>ל</th><th>מקדם</th></tr></thead><tbody>';
      conversions.forEach(function (cv) {
        html += '<tr><td>' + _esc(cv.source_unit) + '</td><td>' + _esc(cv.target_unit) +
          '</td><td>' + cv.conversion_factor + '</td></tr>';
      });
      html += '</tbody></table>';
    }
    if (html === '<div class="sfa-cb-field-data">') html += '<p class="sfa-cb-placeholder">אין נתוני שדה</p>';
    html += '</div>';
    sec.innerHTML = html;
  }

  // ---------------------------------------------------------------------------
  // Tab switching
  // ---------------------------------------------------------------------------

  function activateFirstTab(detail) {
    var firstVisible = null;
    detail.querySelectorAll('.sfa-cb-tabs button').forEach(function (btn) {
      if (!firstVisible && btn.style.display !== 'none') firstVisible = btn;
    });
    if (firstVisible) activateTab(detail, firstVisible.dataset.tab);

    detail.querySelectorAll('.sfa-cb-tabs button').forEach(function (btn) {
      btn.addEventListener('click', function () {
        activateTab(detail, btn.dataset.tab);
      });
    });
  }

  function activateTab(detail, key) {
    detail.querySelectorAll('.sfa-cb-tabs button').forEach(function (b) {
      b.classList.toggle('active', b.dataset.tab === key);
    });
    detail.querySelectorAll('.sfa-cb-tab').forEach(function (s) {
      s.hidden = s.dataset.tab !== key;
    });
  }

  // ---------------------------------------------------------------------------
  // Entity tag tooltips
  // ---------------------------------------------------------------------------

  function _wireEntityTooltip(span) {
    if (!DATA || !DATA.entity_registry) return;
    var etype    = span.dataset.etype;
    var eid      = span.dataset.eid;
    var entities = DATA.entity_registry.entities || {};
    var typeEnts = entities[etype] || {};
    var entity   = typeEnts[eid];
    if (!entity) return;
    var typeLabels = DATA.entity_registry.type_labels || {};
    var typeLabel  = typeLabels[etype] || etype;

    var tooltip = document.createElement('span');
    tooltip.className = 'sfa-cb-etag-tooltip';
    tooltip.textContent = entity.nameHe + ' (' + typeLabel + ')';
    tooltip.style.cssText = 'display:none;position:absolute;background:#333;color:#fff;padding:2px 6px;border-radius:3px;font-size:.8em;white-space:nowrap;z-index:100';

    span.style.position = 'relative';
    span.appendChild(tooltip);

    span.addEventListener('mouseenter', function () { tooltip.style.display = 'block'; });
    span.addEventListener('mouseleave', function () { tooltip.style.display = 'none'; });
  }

  // ---------------------------------------------------------------------------
  // Utilities
  // ---------------------------------------------------------------------------

  function _esc(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

})();
