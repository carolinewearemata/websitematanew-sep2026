(function () {
  "use strict";
  var doc = document;
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var PREF_KEY = "mata-assinatura";

  function store(get, value) {
    try {
      if (get) return JSON.parse(localStorage.getItem(PREF_KEY) || "null");
      if (value === null) localStorage.removeItem(PREF_KEY);
      else localStorage.setItem(PREF_KEY, JSON.stringify(value));
    } catch (e) { return null; }
    return null;
  }

  /* Menu */
  function setupMenus() {
    var menuBtn = doc.getElementById("menu-btn");
    var mobile = doc.getElementById("mobile-nav");
    if (menuBtn && mobile) {
      menuBtn.addEventListener("click", function () {
        var open = menuBtn.getAttribute("aria-expanded") === "true";
        menuBtn.setAttribute("aria-expanded", String(!open));
        mobile.hidden = open;
      });
    }
    var subBtn = doc.getElementById("sub-btn");
    var subPanel = doc.getElementById("sub-panel");
    if (subBtn && subPanel) {
      var close = function () { subBtn.setAttribute("aria-expanded", "false"); subPanel.hidden = true; };
      subBtn.addEventListener("click", function (e) {
        e.stopPropagation();
        var open = subBtn.getAttribute("aria-expanded") === "true";
        subBtn.setAttribute("aria-expanded", String(!open));
        subPanel.hidden = open;
      });
      doc.addEventListener("click", function (e) { if (!subPanel.contains(e.target)) close(); });
      doc.addEventListener("keydown", function (e) { if (e.key === "Escape") { close(); } });
      subPanel.addEventListener("click", function (e) { if (e.target.closest("a")) close(); });
    }
    var skip = doc.querySelector(".skip");
    if (skip) {
      skip.addEventListener("click", function (e) {
        var main = doc.querySelector("main:not([hidden])");
        if (!main) return;
        e.preventDefault();
        var h1 = main.querySelector("h1");
        (h1 || main).setAttribute("tabindex", "-1");
        (h1 || main).focus();
      });
    }
  }

  /* Prévia em página única: cada página do site vira uma vista com o próprio H1 */
  function setupRouter() {
    var views = doc.querySelectorAll("main[data-route]");
    if (views.length < 2) return;
    var mobile = doc.getElementById("mobile-nav");
    var menuBtn = doc.getElementById("menu-btn");
    function show(hash, first) {
      var key = (hash || "").replace(/^#/, "");
      var target = null, anchor = null;
      if (!key) key = "inicio";
      target = doc.querySelector('main[data-route="' + key + '"]');
      if (!target) {
        anchor = doc.getElementById(key);
        if (anchor) target = anchor.closest("main[data-route]");
      }
      if (!target) target = doc.querySelector('main[data-route="404"]');
      views.forEach(function (v) { v.hidden = v !== target; });
      var route = target.getAttribute("data-route");
      doc.title = target.getAttribute("data-title");
      var desc = doc.querySelector('meta[name="description"]');
      if (desc) desc.setAttribute("content", target.getAttribute("data-description"));
      doc.querySelectorAll("[data-nav]").forEach(function (a) {
        var keys = a.getAttribute("data-nav").split(" ");
        if (keys.indexOf(route) > -1 || keys.indexOf(target.getAttribute("data-section")) > -1) a.setAttribute("aria-current", "page");
        else a.removeAttribute("aria-current");
      });
      var subBtn = doc.getElementById("sub-btn");
      if (subBtn) subBtn.classList.toggle("is-current", target.getAttribute("data-section") === "como-funciona");
      if (mobile && menuBtn) { mobile.hidden = true; menuBtn.setAttribute("aria-expanded", "false"); }
      if (anchor) {
        anchor.scrollIntoView();
      } else if (!first) {
        window.scrollTo(0, 0);
        var h1 = target.querySelector("h1");
        if (h1) { h1.setAttribute("tabindex", "-1"); h1.focus({ preventScroll: true }); }
      }
      doc.dispatchEvent(new CustomEvent("mata:view", { detail: route }));
    }
    window.addEventListener("hashchange", function () { show(location.hash, false); });
    show(location.hash, true);
  }

  /* Cena: a pergunta percorre a semana */
  function setupScene() {
    var board = doc.querySelector(".board");
    if (!board) return;
    var moments = board.querySelectorAll(".moment");
    function update() {
      if (!board.offsetParent) return;
      var r = board.getBoundingClientRect();
      var line = window.innerHeight * 0.62;
      var p = reduce ? 1 : Math.max(0, Math.min(1, (line - r.top) / r.height));
      board.style.setProperty("--p", p.toFixed(3));
      moments.forEach(function (m) {
        var lab = m.querySelector(".m-label");
        if (lab) m.classList.toggle("lit", reduce || lab.getBoundingClientRect().top < line);
      });
    }
    var ticking = false;
    window.addEventListener("scroll", function () {
      if (!ticking) { ticking = true; requestAnimationFrame(function () { ticking = false; update(); }); }
    }, { passive: true });
    window.addEventListener("resize", update);
    doc.addEventListener("mata:view", function () { setTimeout(update, 30); });
    update();

    var card = board.querySelector(".rpm-card");
    if (!card) return;
    var list = card.querySelector(".rpm-list");
    var state = card.querySelector("output");
    var replay = card.querySelector(".replay");
    var items = Array.prototype.slice.call(list.children);
    function order(attr) {
      return items.slice().sort(function (a, b) { return a.getAttribute(attr) - b.getAttribute(attr); });
    }
    function place(seq) {
      seq.forEach(function (li, i) { list.appendChild(li); li.querySelector(".pos").textContent = i + 1; });
    }
    function planned() {
      place(order("data-planned"));
      card.classList.add("planned");
      state.textContent = state.getAttribute("data-planned");
    }
    function toFinal() {
      var first = new Map();
      items.forEach(function (li) { first.set(li, li.getBoundingClientRect().top); });
      place(order("data-final"));
      card.classList.remove("planned");
      state.textContent = state.getAttribute("data-final");
      if (reduce) return;
      items.forEach(function (li) {
        var dy = first.get(li) - li.getBoundingClientRect().top;
        if (!dy) return;
        li.style.transition = "none";
        li.style.transform = "translateY(" + dy + "px)";
        requestAnimationFrame(function () {
          requestAnimationFrame(function () {
            li.style.transition = "transform .7s cubic-bezier(.2,.7,.2,1)";
            li.style.transform = "";
          });
        });
      });
    }
    if (reduce || !("IntersectionObserver" in window)) return;
    planned();
    var played = false;
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting && !played) { played = true; setTimeout(toFinal, 650); }
      });
    }, { threshold: 0.6 });
    io.observe(card);
    if (replay) {
      replay.hidden = false;
      replay.addEventListener("click", function () { planned(); setTimeout(toFinal, 500); });
    }
  }

  /* Assinatura: preferência que acompanha o contato */
  function setupSubscription() {
    var form = doc.getElementById("assinatura-pref");
    if (!form) return;
    var saved = store(true) || {};
    Object.keys(saved).forEach(function (k) {
      var v = saved[k];
      form.querySelectorAll('[name="' + k + '"]').forEach(function (el) {
        if (el.type === "checkbox") el.checked = !!v;
        else if (el.value === v) el.checked = true;
      });
    });
    function read() {
      var data = {};
      ["modalidade", "ponto", "lab"].forEach(function (k) {
        var el = form.querySelector('[name="' + k + '"]:checked');
        if (el) data[k] = el.value;
      });
      var esp = form.querySelector('[name="especialistas"]');
      if (esp && esp.checked) data.especialistas = esp.value;
      return data;
    }
    function render() {
      var data = read();
      doc.querySelectorAll("[data-sum]").forEach(function (dd) {
        var k = dd.getAttribute("data-sum");
        dd.textContent = data[k] || dd.getAttribute("data-empty");
      });
      store(false, Object.keys(data).length ? data : null);
    }
    form.addEventListener("change", render);
    render();
  }

  /* Contato */
  function setupContact() {
    var form = doc.getElementById("contato-form");
    if (!form) return;
    var status = doc.getElementById("form-status");
    var prefBox = doc.getElementById("pref-box");
    var prefText = doc.getElementById("pref-text");
    var prefInput = doc.getElementById("pref-input");
    function showPref() {
      var p = store(true);
      if (!p || !prefBox) { if (prefBox) prefBox.hidden = true; if (prefInput) prefInput.value = ""; return; }
      var parts = [p.modalidade, p.ponto, p.lab ? "AI Lab: " + p.lab.toLowerCase() : "", p.especialistas].filter(Boolean);
      prefText.textContent = parts.join(" · ");
      prefInput.value = parts.join(" · ");
      prefBox.hidden = false;
    }
    showPref();
    doc.addEventListener("mata:view", function (e) { if (e.detail === "contato") showPref(); });
    var clear = doc.getElementById("pref-clear");
    if (clear) clear.addEventListener("click", function () { store(false, null); showPref(); });

    var msgs = form.dataset;
    function check(field) {
      var err = doc.getElementById(field.id + "-err");
      var v = field.value.trim();
      var text = "";
      if (!v) text = msgs.required;
      else if (field.type === "email" && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v)) text = msgs.email;
      field.setAttribute("aria-invalid", text ? "true" : "false");
      err.textContent = text;
      err.hidden = !text;
      return !text;
    }
    var fields = form.querySelectorAll("input[required], textarea[required]");
    fields.forEach(function (f) {
      f.addEventListener("blur", function () { if (f.value.trim() || f.getAttribute("aria-invalid")) check(f); });
    });
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var firstBad = null;
      fields.forEach(function (f) { if (!check(f) && !firstBad) firstBad = f; });
      if (firstBad) { firstBad.focus(); return; }
      var btn = form.querySelector("button[type=submit]");
      btn.disabled = true;
      status.hidden = false;
      status.className = "status wait";
      status.textContent = msgs.sending;
      var endpoint = window.MATA_FORM_ENDPOINT;
      var payload = {};
      new FormData(form).forEach(function (v, k) { payload[k] = v; });
      var done = function (ok) {
        btn.disabled = false;
        status.className = "status " + (ok ? "ok" : "fail");
        status.textContent = ok ? msgs.ok : msgs.fail;
        status.focus();
        if (ok) form.reset();
      };
      if (!endpoint) { setTimeout(function () { done(false); }, 700); return; }
      fetch(endpoint, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) })
        .then(function (r) { done(r.ok); })
        .catch(function () { done(false); });
    });
  }

  setupMenus();
  setupRouter();
  setupScene();
  setupSubscription();
  setupContact();
})();
