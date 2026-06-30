/* =============================================================
   AI Development Patterns - catalog app
   Renders the pattern grid, search/filters, and the detail modal
   from window.PATTERNS_DATA (generated from README.md).
   ============================================================= */
(function () {
  "use strict";

  var DATA = window.PATTERNS_DATA;
  if (!DATA || !Array.isArray(DATA.patterns)) {
    console.error("PATTERNS_DATA missing - run scripts/generate-patterns-data.py");
    return;
  }

  var patternsById = {};
  DATA.patterns.forEach(function (p) { patternsById[p.id] = p; });

  var state = { query: "", category: "all", maturity: "all" };
  var cardEls = [];
  var lastFocused = null;
  var pushedModalState = false;

  /* ---------- helpers ---------- */
  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach(function (k) {
        if (k === "class") node.className = attrs[k];
        else if (k === "text") node.textContent = attrs[k];
        else if (k.indexOf("data-") === 0) node.setAttribute(k, attrs[k]);
        else if (k in node) node[k] = attrs[k];
        else node.setAttribute(k, attrs[k]);
      });
    }
    (children || []).forEach(function (c) {
      if (c == null) return;
      node.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
    });
    return node;
  }

  function categoryName(id) {
    var c = (DATA.categories || []).find(function (x) { return x.id === id; });
    return c ? c.name : id;
  }

  /* ---------- markdown rendering (mermaid-aware) ---------- */
  function renderMarkdown(md) {
    var blocks = [];
    var staged = md.replace(/```mermaid\n([\s\S]*?)```/g, function (_m, body) {
      var i = blocks.push(body.replace(/\n+$/, "")) - 1;
      return "\n\nMERMAIDPLACEHOLDER" + i + "\n\n";
    });
    var html = window.marked ? window.marked.parse(staged) : staged;
    html = html.replace(/<p>\s*MERMAIDPLACEHOLDER(\d+)\s*<\/p>/g, function (_m, i) {
      return '<div class="mermaid">' + blocks[Number(i)] + "</div>";
    });
    html = html.replace(/MERMAIDPLACEHOLDER(\d+)/g, function (_m, i) {
      return '<div class="mermaid">' + blocks[Number(i)] + "</div>";
    });
    return html;
  }

  function runMermaid(scope) {
    if (!window.mermaid) return;
    var nodes = scope.querySelectorAll(".mermaid:not([data-processed])");
    if (!nodes.length) return;
    try {
      window.mermaid.run({ nodes: nodes });
    } catch (e) {
      /* leave raw diagram source visible if rendering fails */
    }
  }

  /* ---------- card construction ---------- */
  function buildCard(p) {
    var card = el("button", {
      class: "pattern-card",
      type: "button",
      "data-id": p.id,
      "data-cat": p.category,
      "data-maturity": p.maturity,
      "aria-label": "View pattern: " + p.name
    });
    card._search = (
      p.name + " " + p.shortDescription + " " + p.type + " " +
      p.maturity + " " + p.category + " " + p.bodyMarkdown
    ).toLowerCase();

    var top = el("div", { class: "card-top" }, [
      el("span", { class: "card-eyebrow", text: categoryName(p.category) + " / " + p.type }),
      el("span", { class: "maturity-tag", "data-maturity": p.maturity, text: p.maturity })
    ]);

    var depCount = (p.dependencies || []).length;
    var depText = depCount === 0
      ? "No prerequisites"
      : depCount + " prerequisite" + (depCount > 1 ? "s" : "");

    var foot = el("div", { class: "card-foot" }, [
      el("span", { text: depText }),
      el("span", { class: "go" }, ["View pattern ", el("span", { class: "arrow", text: "→" })])
    ]);

    card.appendChild(top);
    card.appendChild(el("h3", { text: p.name }));
    card.appendChild(el("p", { class: "card-desc", text: p.shortDescription }));
    card.appendChild(foot);

    card.addEventListener("click", function () { openPattern(p.id); });
    return card;
  }

  function renderCatalog() {
    var root = document.getElementById("catalog");
    root.innerHTML = "";
    cardEls = [];

    (DATA.categories || []).forEach(function (cat) {
      var inCat = DATA.patterns.filter(function (p) { return p.category === cat.id; });
      if (!inCat.length) return;

      var section = el("section", { class: "cat-section", "data-cat": cat.id, id: "cat-" + cat.id });
      var head = el("div", { class: "cat-head" }, [
        el("span", { class: "cat-dot", "aria-hidden": "true" }),
        el("h2", { text: cat.name }),
        el("span", { class: "cat-count", text: inCat.length + " patterns" }),
        el("p", { class: "cat-blurb", text: cat.blurb })
      ]);
      var grid = el("div", { class: "pattern-grid" });
      inCat.forEach(function (p) {
        var card = buildCard(p);
        cardEls.push(card);
        grid.appendChild(card);
      });
      section.appendChild(head);
      section.appendChild(grid);
      root.appendChild(section);
    });
  }

  /* ---------- filtering ---------- */
  function applyFilters() {
    var q = state.query.trim().toLowerCase();
    var visible = 0;
    cardEls.forEach(function (card) {
      var p = patternsById[card.getAttribute("data-id")];
      var ok =
        (state.category === "all" || p.category === state.category) &&
        (state.maturity === "all" || p.maturity === state.maturity) &&
        (q === "" || card._search.indexOf(q) !== -1);
      card.style.display = ok ? "" : "none";
      if (ok) visible++;
    });
    document.querySelectorAll(".cat-section").forEach(function (sec) {
      var anyVisible = sec.querySelectorAll('.pattern-card:not([style*="display: none"])').length > 0;
      sec.style.display = anyVisible ? "" : "none";
    });
    document.getElementById("noResults").classList.toggle("show", visible === 0);
  }

  function setupFilters() {
    var search = document.getElementById("search");
    var wrap = document.getElementById("searchWrap");
    search.addEventListener("input", function () {
      state.query = search.value;
      wrap.classList.toggle("has-text", search.value.length > 0);
      applyFilters();
    });
    document.getElementById("searchClear").addEventListener("click", function () {
      search.value = ""; state.query = ""; wrap.classList.remove("has-text");
      applyFilters(); search.focus();
    });

    document.querySelectorAll("[data-filter]").forEach(function (chip) {
      chip.addEventListener("click", function () {
        var group = chip.getAttribute("data-filter");
        var value = chip.getAttribute("data-value");
        state[group] = value;
        document.querySelectorAll('[data-filter="' + group + '"]').forEach(function (c) {
          c.setAttribute("aria-pressed", c === chip ? "true" : "false");
        });
        applyFilters();
      });
    });

    document.getElementById("resetFilters").addEventListener("click", resetFilters);
  }

  function resetFilters() {
    state = { query: "", category: "all", maturity: "all" };
    var search = document.getElementById("search");
    search.value = "";
    document.getElementById("searchWrap").classList.remove("has-text");
    document.querySelectorAll("[data-filter]").forEach(function (c) {
      c.setAttribute("aria-pressed", c.getAttribute("data-value") === "all" ? "true" : "false");
    });
    applyFilters();
  }

  /* ---------- modal ---------- */
  function relBlock(label, items) {
    if (!items || !items.length) return null;
    var chips = el("div", { class: "rel-chips" });
    items.forEach(function (item) {
      var known = item.id && patternsById[item.id];
      var chip = el("button", {
        class: "rel-chip", type: "button", text: item.name,
        "aria-label": item.name
      });
      if (known) {
        chip.addEventListener("click", function () { openPattern(item.id); });
      } else {
        chip.setAttribute("disabled", "disabled");
      }
      chips.appendChild(chip);
    });
    return el("div", { class: "rel-block" }, [
      el("div", { class: "rel-label", text: label }), chips
    ]);
  }

  function renderModal(id) {
    var p = patternsById[id];
    if (!p) return;
    var card = document.getElementById("modalCard");
    card.setAttribute("data-cat", p.category);

    var eyebrow = document.getElementById("modalEyebrow");
    eyebrow.innerHTML = "";
    eyebrow.appendChild(el("span", { class: "eyebrow", text: categoryName(p.category) }));
    eyebrow.appendChild(el("span", { class: "maturity-tag", "data-maturity": p.maturity, text: p.maturity }));
    eyebrow.appendChild(el("span", { class: "maturity-tag", text: p.type }));

    document.getElementById("modalTitle").textContent = p.name;

    var relations = document.getElementById("modalRelations");
    relations.innerHTML = "";
    var depBlock = relBlock("Builds on", p.dependencies);
    var relatedBlock = relBlock("Related patterns", p.related);
    if (depBlock) relations.appendChild(depBlock);
    if (relatedBlock) relations.appendChild(relatedBlock);

    var bodyEl = document.getElementById("modalMarkdown");
    bodyEl.innerHTML = renderMarkdown(p.bodyMarkdown);

    var actions = document.getElementById("modalActions");
    actions.innerHTML = "";
    actions.appendChild(el("a", {
      class: "primary", href: p.githubUrl, target: "_blank", rel: "noopener"
    }, ["Read on GitHub ", el("span", { text: "↗" })]));
    actions.appendChild(el("a", {
      class: "ghost", href: "#", id: "modalCloseLink"
    }, ["Back to catalog"]));
    actions.querySelector("#modalCloseLink").addEventListener("click", function (ev) {
      ev.preventDefault(); closeModal();
    });

    document.getElementById("modalBody").scrollTop = 0;
    runMermaid(bodyEl);

    // Re-anchor focus inside the dialog. Related-chip and popstate navigation
    // re-render while the modal is already open and would otherwise drop focus
    // to <body> when the focused chip is replaced.
    if (document.getElementById("modal").classList.contains("open")) {
      document.getElementById("modalTitle").focus();
    }
  }

  function setBackgroundInert(on) {
    document.querySelectorAll(".status-bar, .topbar-editorial, main, .site-foot").forEach(function (elm) {
      if (on) elm.setAttribute("inert", "");
      else elm.removeAttribute("inert");
    });
  }

  function openModalUI() {
    var backdrop = document.getElementById("modalBackdrop");
    var modal = document.getElementById("modal");
    if (modal.classList.contains("open")) return;
    lastFocused = document.activeElement;
    backdrop.classList.add("open");
    modal.classList.add("open");
    document.body.classList.add("modal-open");
    setBackgroundInert(true);
    document.getElementById("modalCloseBtn").focus();
  }

  function closeModalUI() {
    setBackgroundInert(false);
    document.getElementById("modalBackdrop").classList.remove("open");
    document.getElementById("modal").classList.remove("open");
    document.body.classList.remove("modal-open");
    if (lastFocused && lastFocused.focus) lastFocused.focus();
  }

  function openPattern(id) {
    if (!patternsById[id]) return;
    renderModal(id);
    openModalUI();
    history.pushState({ patternId: id }, "", "#" + id);
    pushedModalState = true;
  }

  function closeModal() {
    if (pushedModalState) {
      history.back(); // triggers popstate -> closeModalUI
    } else {
      closeModalUI();
      if (location.hash) history.replaceState(null, "", location.pathname + location.search);
    }
  }

  function setupModal() {
    document.getElementById("modalCloseBtn").addEventListener("click", closeModal);
    document.getElementById("modalBackdrop").addEventListener("click", closeModal);

    document.addEventListener("keydown", function (e) {
      if (!document.getElementById("modal").classList.contains("open")) return;
      if (e.key === "Escape") { e.preventDefault(); closeModal(); }
      else if (e.key === "Tab") { trapFocus(e); }
    });

    window.addEventListener("popstate", function (e) {
      var id = (e.state && e.state.patternId) || hashId();
      if (id && patternsById[id]) {
        renderModal(id);
        openModalUI();
        pushedModalState = true;
      } else {
        closeModalUI();
        pushedModalState = false;
      }
    });
  }

  function trapFocus(e) {
    var modal = document.getElementById("modalCard");
    var f = modal.querySelectorAll(
      'a[href], button:not([disabled]), input, [tabindex]:not([tabindex="-1"])'
    );
    if (!f.length) return;
    var first = f[0], last = f[f.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    else if (!modal.contains(document.activeElement)) { e.preventDefault(); first.focus(); }
  }

  function hashId() {
    return location.hash ? decodeURIComponent(location.hash.slice(1)) : "";
  }

  /* ---------- stats ---------- */
  function renderStats() {
    var counts = { foundation: 0, development: 0, operations: 0 };
    DATA.patterns.forEach(function (p) { counts[p.category] = (counts[p.category] || 0) + 1; });
    var setText = function (id, v) { var n = document.getElementById(id); if (n) n.textContent = v; };
    setText("statTotal", DATA.patternCount);
    setText("statFoundation", counts.foundation);
    setText("statDevelopment", counts.development);
    setText("statOperations", counts.operations);
  }

  // Called by the dependency diagram's mermaid `click` directives. Mermaid
  // passes the node id (underscored); map it back to the pattern id.
  window.openPatternFromDiagram = function (nodeId) {
    openPattern(String(nodeId).replace(/_/g, "-"));
  };

  /* ---------- init ---------- */
  function init() {
    renderStats();
    renderCatalog();
    setupFilters();
    setupModal();
    applyFilters();

    var id = hashId();
    if (id && patternsById[id]) {
      renderModal(id);
      openModalUI();
      history.replaceState({ patternId: id }, "", "#" + id);
      pushedModalState = false;
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
