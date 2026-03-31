/**
 * Client-side sort for admin tables. Add class `table-sortable` on <table>.
 * Optional per header: data-sort-type="text" | "number" | "date"
 * Optional: data-sort-none on <th> to skip sorting (e.g. actions column).
 * Optional on <td>: data-sort-value for stable sort key (ISO dates, raw numbers).
 */
(function () {
  "use strict";

  /** Inline SVG only (no CSS mask) — avoids broken rendering where mask URL shows as text/digits. */
  var SVG_NS = "http://www.w3.org/2000/svg";
  var GLYPH_BOTH =
    "<path fill=\"currentColor\" d=\"M6 5.5L8 3.5 10 5.5z\"/><path fill=\"currentColor\" d=\"M6 10.5L8 12.5 10 10.5z\"/>";
  var GLYPH_ASC = "<path fill=\"currentColor\" d=\"M4 10L8 5l4 5H4z\"/>";
  var GLYPH_DESC = "<path fill=\"currentColor\" d=\"M4 6l4 5 4-5H4z\"/>";

  function setSortGlyph(th, mode) {
    var wrap = th.querySelector(".sort-th-glyph");
    if (!wrap) return;
    wrap.textContent = "";
    var svg = document.createElementNS(SVG_NS, "svg");
    svg.setAttribute("viewBox", "0 0 16 16");
    svg.setAttribute("width", "14");
    svg.setAttribute("height", "14");
    svg.setAttribute("class", "sort-th-svg");
    svg.setAttribute("aria-hidden", "true");
    svg.setAttribute("focusable", "false");
    if (mode === "asc") {
      svg.innerHTML = GLYPH_ASC;
    } else if (mode === "desc") {
      svg.innerHTML = GLYPH_DESC;
    } else {
      svg.innerHTML = GLYPH_BOTH;
    }
    wrap.appendChild(svg);
  }

  function cellSortValue(td, type) {
    if (!td) return "";
    const explicit = td.getAttribute("data-sort-value");
    if (explicit !== null && explicit !== "") return explicit;
    const t = (type || "text").toLowerCase();
    const raw = (td.textContent || "").trim();
    if (t === "number") {
      const n = parseFloat(raw.replace(/[₪,\s]/g, "").replace(/,/g, ""));
      return Number.isFinite(n) ? n : NaN;
    }
    if (t === "date") {
      return raw;
    }
    return raw.toLocaleLowerCase("he");
  }

  function cmpValues(va, vb, type) {
    const t = (type || "text").toLowerCase();
    if (t === "number") {
      const na = typeof va === "number" && !Number.isNaN(va) ? va : parseFloat(va) || 0;
      const nb = typeof vb === "number" && !Number.isNaN(vb) ? vb : parseFloat(vb) || 0;
      return na - nb;
    }
    return String(va).localeCompare(String(vb), "he", { numeric: true, sensitivity: "base" });
  }

  function sortTable(table, colIndex, thClicked) {
    const tbody = table.querySelector("tbody");
    if (!tbody) return;
    const type = (thClicked.getAttribute("data-sort-type") || "text").toLowerCase();
    const rows = Array.from(tbody.querySelectorAll("tr"));
    const key = "sortDir_" + colIndex;
    const prev = table.dataset[key];
    const asc = prev !== "asc";
    table.dataset[key] = asc ? "asc" : "desc";

    table.querySelectorAll("thead th").forEach((th) => {
      th.classList.remove("sort-asc", "sort-desc");
      if (th.classList.contains("sortable-th")) {
        th.setAttribute("aria-sort", "none");
        setSortGlyph(th, "both");
      }
    });
    thClicked.classList.add(asc ? "sort-asc" : "sort-desc");
    thClicked.setAttribute("aria-sort", asc ? "ascending" : "descending");
    setSortGlyph(thClicked, asc ? "asc" : "desc");

    rows.sort((a, b) => {
      const tda = a.children[colIndex];
      const tdb = b.children[colIndex];
      const va = cellSortValue(tda, type);
      const vb = cellSortValue(tdb, type);
      const cmp = cmpValues(va, vb, type);
      return asc ? cmp : -cmp;
    });
    rows.forEach((r) => tbody.appendChild(r));
  }

  function initTable(table) {
    if (table.dataset.sortableBound === "1") return;
    table.dataset.sortableBound = "1";
    const headerRow = table.querySelector("thead tr");
    if (!headerRow) return;
    const ths = headerRow.querySelectorAll("th");
    ths.forEach((th, idx) => {
      if (th.hasAttribute("data-sort-none")) return;
      th.classList.add("sortable-th");
      th.setAttribute("role", "button");
      th.setAttribute("tabindex", "0");
      th.setAttribute("aria-sort", "none");
      if (!th.querySelector(".sort-th-glyph")) {
        const g = document.createElement("span");
        g.className = "sort-th-glyph";
        g.setAttribute("aria-hidden", "true");
        th.appendChild(g);
        setSortGlyph(th, "both");
      }
      th.addEventListener("click", (ev) => {
        ev.preventDefault();
        sortTable(table, idx, th);
      });
      th.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          sortTable(table, idx, th);
        }
      });
    });
  }

  function init() {
    try {
      document.querySelectorAll("table.table-sortable").forEach(initTable);
    } catch (err) {
      console.error("[sortable_tables] init failed:", err);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
