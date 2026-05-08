/**
 * crop_book.js — ספר גידולים client-side JS
 * - Tab switching (Bootstrap 5 handles natively)
 * - Category filter (client-side card show/hide + API fetch)
 * - Search filter (debounced, fetches /api/crops)
 * - Entity tag hover tooltips
 * - Yearly breakdown accordion (Bootstrap 5 handles natively)
 */

const CropBook = (() => {
  "use strict";

  /* ------------------------------------------------------------------ */
  /* Helpers                                                              */
  /* ------------------------------------------------------------------ */

  function debounce(fn, ms = 250) {
    let timer;
    return (...args) => {
      clearTimeout(timer);
      timer = setTimeout(() => fn(...args), ms);
    };
  }

  function showTooltip(el, text) {
    let tip = document.querySelector(".cb-etag-tooltip");
    if (!tip) {
      tip = document.createElement("div");
      tip.className = "cb-etag-tooltip";
      document.body.appendChild(tip);
    }
    tip.textContent = text;
    tip.style.display = "block";
    const rect = el.getBoundingClientRect();
    tip.style.top = (rect.bottom + window.scrollY + 6) + "px";
    tip.style.right = (window.innerWidth - rect.right + window.scrollX) + "px";
    tip.style.left = "auto";
  }

  function hideTooltip() {
    const tip = document.querySelector(".cb-etag-tooltip");
    if (tip) tip.style.display = "none";
  }

  /* ------------------------------------------------------------------ */
  /* Entity tag tooltips                                                  */
  /* ------------------------------------------------------------------ */

  function initEntityTags() {
    document.querySelectorAll(".etag").forEach((el) => {
      el.addEventListener("mouseenter", () => {
        const etype = el.dataset.etype;
        const eid = el.dataset.eid;
        let text = el.textContent.trim();
        if (typeof ENTITY_REGISTRY !== "undefined") {
          const info = ENTITY_REGISTRY.lookup(etype, eid);
          if (info) {
            text = `${info.nameHe} (${info.typeLabel})`;
          }
        }
        showTooltip(el, text);
      });
      el.addEventListener("mouseleave", hideTooltip);
      // No click navigation — future_url not active yet
      el.addEventListener("click", (e) => e.preventDefault());
    });
  }

  /* ------------------------------------------------------------------ */
  /* Index page: category tabs + search + advanced filter                 */
  /* ------------------------------------------------------------------ */

  function initIndex({ apiUrl, initialCategory, initialQ }) {
    const grid = document.getElementById("cb-crop-grid");
    const countEl = document.getElementById("cb-visible-count");
    const searchInput = document.getElementById("cb-search-input");
    const dtmMaxInput = document.getElementById("cb-dtm-max");
    const adv_apply = document.getElementById("cb-adv-apply");
    const adv_reset = document.getElementById("cb-adv-reset");

    let currentCategory = initialCategory || "";
    let currentQ = initialQ || "";
    let currentDtmMax = null;
    let currentSeasons = [];

    // ── Category tab clicks ──────────────────────────────────────────
    document.querySelectorAll(".cb-cat-tab").forEach((btn) => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".cb-cat-tab").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        currentCategory = btn.dataset.category || "";
        fetchAndRender();
      });
    });

    // ── Free-text search ─────────────────────────────────────────────
    if (searchInput) {
      searchInput.addEventListener(
        "input",
        debounce(() => {
          currentQ = searchInput.value.trim();
          fetchAndRender();
        }, 300)
      );
    }

    // ── Advanced search ──────────────────────────────────────────────
    if (adv_apply) {
      adv_apply.addEventListener("click", () => {
        currentDtmMax = dtmMaxInput && dtmMaxInput.value ? parseInt(dtmMaxInput.value) : null;
        currentSeasons = Array.from(
          document.querySelectorAll(".cb-season-check:checked")
        ).map((cb) => cb.value);
        fetchAndRender();
      });
    }

    if (adv_reset) {
      adv_reset.addEventListener("click", () => {
        if (dtmMaxInput) dtmMaxInput.value = "";
        document.querySelectorAll(".cb-season-check").forEach((cb) => (cb.checked = false));
        currentDtmMax = null;
        currentSeasons = [];
        fetchAndRender();
      });
    }

    // ── Fetch from API and re-render grid ────────────────────────────
    async function fetchAndRender() {
      const params = new URLSearchParams();
      if (currentCategory) params.set("category", currentCategory);
      if (currentQ) params.set("q", currentQ);
      if (currentDtmMax) params.set("dtm_max", currentDtmMax);
      // For multiple seasons, send the first one (simplification — API handles one at a time)
      if (currentSeasons.length === 1) params.set("season", currentSeasons[0]);

      try {
        const resp = await fetch(apiUrl + "?" + params.toString());
        if (!resp.ok) throw new Error("API error " + resp.status);
        const crops = await resp.json();
        renderGrid(crops);
      } catch (err) {
        // On network error: fall back to client-side filtering of existing cards
        clientFilter();
      }
    }

    function renderGrid(crops) {
      if (!grid) return;

      // If API returns results, show/hide existing cards by id match
      const allCards = grid.querySelectorAll(".cb-crop-card-wrap");
      const cropIds = new Set(crops.map((c) => String(c.id)));

      if (crops.length === 0) {
        allCards.forEach((c) => (c.style.display = "none"));
        let emptyMsg = grid.querySelector(".cb-empty-msg");
        if (!emptyMsg) {
          emptyMsg = document.createElement("div");
          emptyMsg.className = "col-12 cb-empty-msg";
          emptyMsg.innerHTML = '<div class="alert alert-info text-center">לא נמצאו גידולים</div>';
          grid.appendChild(emptyMsg);
        }
        emptyMsg.style.display = "";
        if (countEl) countEl.textContent = "0";
      } else {
        let visible = 0;
        allCards.forEach((card) => {
          // Match by href crop id
          const link = card.querySelector("a");
          if (link) {
            const href = link.getAttribute("href") || "";
            const idMatch = href.match(/\/(\d+)\/$/);
            if (idMatch && cropIds.has(idMatch[1])) {
              card.style.display = "";
              visible++;
            } else {
              card.style.display = "none";
            }
          }
        });
        const emptyMsg = grid.querySelector(".cb-empty-msg");
        if (emptyMsg) emptyMsg.style.display = "none";
        if (countEl) countEl.textContent = String(visible);
      }
    }

    function clientFilter() {
      // Fallback: filter existing DOM cards
      const allCards = grid ? grid.querySelectorAll(".cb-crop-card-wrap") : [];
      let visible = 0;
      allCards.forEach((card) => {
        const nameHe = (card.dataset.nameHe || "").toLowerCase();
        const nameEn = (card.dataset.nameEn || "").toLowerCase();
        const scientific = (card.dataset.scientific || "").toLowerCase();
        const category = card.dataset.category || "";
        const dtm = card.dataset.dtm ? parseInt(card.dataset.dtm) : null;
        const seasons = (card.dataset.seasons || "").split(",").filter(Boolean);

        let show = true;
        const q = currentQ.toLowerCase();
        if (q && !nameHe.includes(q) && !nameEn.includes(q) && !scientific.includes(q)) {
          show = false;
        }
        if (currentCategory && category !== currentCategory) show = false;
        if (currentDtmMax && (dtm === null || dtm > currentDtmMax)) show = false;
        if (currentSeasons.length > 0) {
          const hasAny = currentSeasons.some((s) => seasons.includes(s));
          if (!hasAny) show = false;
        }

        card.style.display = show ? "" : "none";
        if (show) visible++;
      });
      if (countEl) countEl.textContent = String(visible);
    }

    // Init entity tags on index page too
    initEntityTags();
  }

  /* ------------------------------------------------------------------ */
  /* Detail page                                                          */
  /* ------------------------------------------------------------------ */

  function initDetail({ hasDescription }) {
    initEntityTags();

    // Sources toggle (unified / by-source)
    const btnUnified = document.getElementById("cb-src-unified");
    const btnBySource = document.getElementById("cb-src-by-source");
    const unifiedView = document.getElementById("cb-sources-unified-view");

    if (btnUnified && btnBySource) {
      btnUnified.addEventListener("click", () => {
        btnUnified.classList.add("active");
        btnBySource.classList.remove("active");
        if (unifiedView) unifiedView.style.display = "";
      });
      btnBySource.addEventListener("click", () => {
        btnBySource.classList.add("active");
        btnUnified.classList.remove("active");
        // By-source view: same table but could highlight per-source column
        // For now, same view — future enhancement
        if (unifiedView) unifiedView.style.display = "";
      });
    }

    // Build entity summary panel if description exists
    if (hasDescription) {
      buildEntitySummary();
    }
  }

  function buildEntitySummary() {
    const summaryEl = document.getElementById("cb-entity-summary");
    if (!summaryEl) return;

    const tags = document.querySelectorAll("#tab-description .etag");
    if (!tags.length) return;

    const byType = {};
    tags.forEach((tag) => {
      const etype = tag.dataset.etype;
      const eid = tag.dataset.eid;
      if (!byType[etype]) byType[etype] = [];
      if (!byType[etype].find((e) => e.eid === eid)) {
        byType[etype].push({ eid, label: tag.textContent.trim() });
      }
    });

    if (!Object.keys(byType).length) return;

    let html = '<div class="cb-entity-summary-panel border rounded p-3 bg-light">';
    html += '<h6 class="mb-2">ישויות מוזכרות</h6>';
    for (const [etype, entities] of Object.entries(byType)) {
      const typeLabel = (typeof ENTITY_REGISTRY !== "undefined")
        ? (ENTITY_REGISTRY.typeLabels[etype] || etype)
        : etype;
      html += `<div class="mb-1"><strong>${typeLabel}:</strong> `;
      html += entities.map((e) =>
        `<span class="etag et-${etype}" data-etype="${etype}" data-eid="${e.eid}">${e.label}</span>`
      ).join(" ");
      html += "</div>";
    }
    html += "</div>";
    summaryEl.innerHTML = html;

    // Re-init tooltips for the summary panel tags
    initEntityTags();
  }

  /* ------------------------------------------------------------------ */
  /* Public API                                                           */
  /* ------------------------------------------------------------------ */

  return { initIndex, initDetail };
})();
