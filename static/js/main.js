/* Apex Solutions: progressive enhancement only. The site works without JavaScript. */
(function () {
  var root = document.documentElement;
  root.classList.remove("no-js");

  document.addEventListener("DOMContentLoaded", function () {
    var toggle = document.querySelector(".nav-toggle");
    var nav = toggle ? document.getElementById(toggle.getAttribute("aria-controls")) : null;
    if (toggle && nav) {
      toggle.addEventListener("click", function () {
        var open = nav.classList.toggle("is-open");
        toggle.setAttribute("aria-expanded", open ? "true" : "false");
      });
    }

    var drops = Array.prototype.slice.call(document.querySelectorAll(".dd"));
    drops.forEach(function (d) {
      d.addEventListener("toggle", function () {
        if (d.open) drops.forEach(function (o) { if (o !== d) o.open = false; });
      });
    });
    document.addEventListener("click", function (e) {
      drops.forEach(function (d) { if (d.open && !d.contains(e.target)) d.open = false; });
    });
    document.addEventListener("keydown", function (e) {
      if (e.key !== "Escape") return;
      drops.forEach(function (d) {
        if (d.open) { d.open = false; d.querySelector("summary").focus(); }
      });
      if (nav && nav.classList.contains("is-open")) {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.focus();
      }
    });

    /* Our Work: filter project cards by category. Without JavaScript all cards show. */
    var filters = Array.prototype.slice.call(document.querySelectorAll(".filter"));
    var cards = Array.prototype.slice.call(document.querySelectorAll("#work-grid .wcard"));
    var empty = document.getElementById("work-empty");
    filters.forEach(function (btn) {
      btn.addEventListener("click", function () {
        var key = btn.getAttribute("data-filter");
        var shown = 0;
        filters.forEach(function (b) {
          var on = b === btn;
          b.classList.toggle("is-on", on);
          b.setAttribute("aria-pressed", on ? "true" : "false");
        });
        cards.forEach(function (card) {
          var match = key === "all" || card.getAttribute("data-cat") === key;
          card.hidden = !match;
          if (match) shown++;
        });
        if (empty) empty.hidden = shown !== 0;
      });
    });

    /* Solution pages: service explorer. Without JavaScript every service shows in full, one after another.
       With it, the list becomes tabs and one service shows at a time. Links like #retail-pos open that service. */
    Array.prototype.slice.call(document.querySelectorAll("[data-svx]")).forEach(function (box) {
      var tabs = Array.prototype.slice.call(box.querySelectorAll("[data-svx-tab]"));
      var panels = Array.prototype.slice.call(box.querySelectorAll("[data-svx-panel]"));
      if (!tabs.length) return;
      var list = box.querySelector(".svx__list");
      var narrow = window.matchMedia("(max-width: 899px)");
      box.classList.add("is-tabs");
      list.setAttribute("role", "tablist");
      list.setAttribute("aria-orientation", "vertical");
      tabs.forEach(function (t) {
        var id = t.getAttribute("data-svx-tab");
        t.parentNode.setAttribute("role", "presentation");
        t.setAttribute("role", "tab");
        t.setAttribute("aria-controls", id);
      });
      panels.forEach(function (p) {
        p.setAttribute("role", "tabpanel");
        p.setAttribute("tabindex", "0");
        p.setAttribute("aria-labelledby", "tab-" + p.id);
      });

      function select(id, opts) {
        opts = opts || {};
        var found = false;
        tabs.forEach(function (t) {
          var on = t.getAttribute("data-svx-tab") === id;
          if (on) found = true;
          t.setAttribute("aria-selected", on ? "true" : "false");
          t.setAttribute("tabindex", on ? "0" : "-1");
          t.classList.toggle("is-on", on);
        });
        if (!found) return false;
        panels.forEach(function (p) { p.hidden = p.id !== id; });
        if (opts.focus) box.querySelector('[data-svx-tab="' + id + '"]').focus();
        if (opts.push && window.history && history.replaceState) history.replaceState(null, "", "#" + id);
        if (opts.reveal) {
          var target = narrow.matches ? document.getElementById(id) : box;
          target.scrollIntoView({ block: "start" });
        }
        return true;
      }

      tabs.forEach(function (t, i) {
        t.addEventListener("click", function (e) {
          e.preventDefault();
          select(t.getAttribute("data-svx-tab"), { push: true, reveal: narrow.matches });
        });
        t.addEventListener("keydown", function (e) {
          var next = null;
          if (e.key === "ArrowDown" || e.key === "ArrowRight") next = tabs[(i + 1) % tabs.length];
          else if (e.key === "ArrowUp" || e.key === "ArrowLeft") next = tabs[(i - 1 + tabs.length) % tabs.length];
          else if (e.key === "Home") next = tabs[0];
          else if (e.key === "End") next = tabs[tabs.length - 1];
          if (!next) return;
          e.preventDefault();
          select(next.getAttribute("data-svx-tab"), { focus: true, push: true });
        });
      });

      function fromHash(reveal) {
        var id = decodeURIComponent((location.hash || "").slice(1));
        return id && select(id, { reveal: reveal });
      }
      if (!fromHash(true)) select(tabs[0].getAttribute("data-svx-tab"));
      window.addEventListener("hashchange", function () { fromHash(true); });
    });

    /* Dashboard: confirm before deleting. */
    Array.prototype.slice.call(document.querySelectorAll("form.js-confirm")).forEach(function (f) {
      f.addEventListener("submit", function (e) {
        if (!window.confirm(f.getAttribute("data-confirm") || "Are you sure?")) e.preventDefault();
      });
    });

    /* Document form: only show the client picker when sharing with one client. */
    var vis = document.getElementById("visibility");
    var pick = document.querySelector(".js-client-pick");
    if (vis && pick) {
      var sync = function () { pick.hidden = vis.value !== "client"; };
      vis.addEventListener("change", sync);
      sync();
    }

    /* Prevent double submission of the enquiry form. */
    var form = document.querySelector("form.form[action$=\"/contact\"]");
    if (form) {
      form.addEventListener("submit", function () {
        var btn = form.querySelector("button[type=submit]");
        if (btn) { btn.disabled = true; btn.textContent = "Sending message"; }
      });
    }
  });
})();
