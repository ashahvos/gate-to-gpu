/* ================= shared helpers ================= */
var KEY_DONE = "g2g.v2.done", KEY_FILTER = "g2g.v2.filter";
function load(k, d) { try { var v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch (e) { return d; } }
function save(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { } }
var reduced = false;
try { reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches; } catch (e) { }
function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
function $(sel, root) { return (root || document).querySelector(sel); }
function $$(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }
function hashStr(s) { var h = 2166136261; for (var i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return (h >>> 0).toString(36); }
var WAVE_ICON = '<svg viewBox="0 0 24 14" aria-hidden="true"><path d="M1 12 H6 V2 H12 V12 H18 V2 H23" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>';
function toolHead(title, sub) { return '<p class="wt">' + WAVE_ICON + "<span>" + esc(title) + "</span>" + (sub ? "<small>" + esc(sub) + "</small>" : "") + "</p>"; }
function clamp(x, a, b) { return Math.max(a, Math.min(b, x)); }
var SUP = { "-": "⁻", "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹" };
function supNum(n) { return String(n).replace(/[-0-9]/g, function (c) { return SUP[c]; }); }
function fmtNum(x, digits) {
  if (!isFinite(x)) return String(x);
  var a = Math.abs(x);
  if (a !== 0 && (a < 1e-3 || a >= 1e7)) {
    var parts = x.toExponential(digits == null ? 3 : digits).split("e");
    return parseFloat(parts[0]) + " × 10" + supNum(parseInt(parts[1], 10));
  }
  var d = digits == null ? 4 : digits;
  return String(parseFloat(x.toPrecision(d)));
}
function siFmt(x, unit, digits) {
  if (!isFinite(x)) return String(x) + " " + unit;
  var pre = [[1e9, "G"], [1e6, "M"], [1e3, "k"], [1, ""], [1e-3, "m"], [1e-6, "µ"], [1e-9, "n"], [1e-12, "p"], [1e-15, "f"]];
  var a = Math.abs(x);
  if (a === 0) return "0 " + unit;
  for (var i = 0; i < pre.length; i++) {
    if (a >= pre[i][0] * 0.9995) return parseFloat((x / pre[i][0]).toPrecision(digits || 4)) + " " + pre[i][1] + unit;
  }
  return x.toExponential(2) + " " + unit;
}

/* ================= problems, filters and progress ================= */
var done = new Set(load(KEY_DONE, []));
var filter = load(KEY_FILTER, { level: "all", hideDone: false });
if (!filter || typeof filter !== "object") filter = { level: "all", hideDone: false };
var modules = $$("section.module");
var probs = [];
var LV = { intro: ["Intro", 1], easy: ["Easy", 2], medium: ["Medium", 3], hard: ["Hard", 4] };

modules.forEach(function (sec) {
  var num = sec.getAttribute("data-num"), pfx = sec.getAttribute("data-pfx");
  $$("article.prob", sec).forEach(function (p, i) {
    var q = $(".q", p);
    var key = sec.id + ":" + hashStr(((q && q.textContent) || "").replace(/\s+/g, " ").trim().slice(0, 200));
    p.id = "p-" + sec.id + "-" + (i + 1);
    var lvl = p.getAttribute("data-level") || "easy";
    var info = LV[lvl] || [lvl, 0];
    var meter = "";
    for (var k = 1; k <= 4; k++) meter += "<i" + (k <= info[1] ? ' class="on"' : "") + "></i>";
    var tags = p.getAttribute("data-tags");
    var head = document.createElement("div");
    head.className = "ph";
    head.innerHTML = '<span class="pid">' + esc(pfx ? pfx + (i + 1) : num + "." + (i + 1)) + '</span><span class="lvl lvl-' + lvl + '"><span class="meter" aria-hidden="true">' + meter + "</span>" + info[0] + "</span>" +
      (tags ? '<span class="ptags">' + esc(tags) + "</span>" : "") +
      '<label class="got"><input type="checkbox" id="got-' + p.id + '"> Got it</label>';
    p.insertBefore(head, p.firstChild);
    var cb = head.querySelector("input");
    cb.checked = done.has(key);
    p.classList.toggle("is-done", cb.checked);
    cb.addEventListener("change", function () {
      if (cb.checked) done.add(key); else done.delete(key);
      save(KEY_DONE, Array.from(done));
      p.classList.toggle("is-done", cb.checked);
      refresh();
    });
    probs.push({ el: p, key: key, sec: sec, lvl: lvl, box: p.closest(".practice") });
  });
  $$(".showall", sec).forEach(function (btn) {
    btn.addEventListener("click", function () {
      var box = btn.closest(".practice") || sec;
      var sols = $$("details.sol", box);
      var anyClosed = sols.some(function (d) { return !d.open; });
      sols.forEach(function (d) { d.open = anyClosed; });
      btn.textContent = anyClosed ? "Hide all solutions" : "Show all solutions";
    });
  });
});

var levelBtns = $$(".toolbar [data-level]");
levelBtns.forEach(function (b) {
  b.addEventListener("click", function () { filter.level = b.getAttribute("data-level"); save(KEY_FILTER, filter); refresh(); });
});
var hideDone = $("#hideDone");
hideDone.addEventListener("change", function () { filter.hideDone = hideDone.checked; save(KEY_FILTER, filter); refresh(); });
function visible(p) {
  if (filter.level !== "all" && p.lvl !== filter.level) return false;
  if (filter.hideDone && done.has(p.key)) return false;
  return true;
}
var navItems = {};
function refresh() {
  levelBtns.forEach(function (b) { b.setAttribute("aria-pressed", String(b.getAttribute("data-level") === filter.level)); });
  hideDone.checked = !!filter.hideDone;
  var total = probs.length, nd = 0, per = {}, boxes = new Map();
  probs.forEach(function (p) {
    var v = visible(p), d = done.has(p.key);
    p.el.hidden = !v;
    var s = per[p.sec.id] || (per[p.sec.id] = { t: 0, d: 0, v: 0 });
    s.t++; if (d) { s.d++; nd++; } if (v) s.v++;
    if (p.box) {
      var b = boxes.get(p.box) || { t: 0, d: 0, v: 0 };
      b.t++; if (d) b.d++; if (v) b.v++;
      boxes.set(p.box, b);
    }
  });
  modules.forEach(function (sec) {
    var s = per[sec.id], a = navItems[sec.id];
    var np = a ? a.querySelector(".nprog") : null;
    if (s) {
      if (np) { np.textContent = s.d + "/" + s.t; np.classList.toggle("full", s.d === s.t); }
    } else if (np) np.textContent = "";
  });
  // each practice block reports its own count (the interview set has several blocks)
  boxes.forEach(function (b, box) {
    var pc = $(".pcount", box), em = $(".empty-msg", box);
    if (pc) pc.textContent = b.d + " of " + b.t + " marked done";
    if (em) em.hidden = b.v > 0;
  });
  $("#progTxt").textContent = nd + " of " + total + " done";
  $("#progBar").style.width = (total ? (100 * nd / total) : 0) + "%";
}

$("#randBtn").addEventListener("click", function () {
  var c = probs.filter(function (p) { return visible(p) && !done.has(p.key); });
  var msg = $("#tbMsg");
  if (!c.length) { msg.textContent = "Every problem that matches this filter is marked done."; return; }
  msg.textContent = "";
  var p = c[Math.floor(Math.random() * c.length)];
  p.el.scrollIntoView({ behavior: reduced ? "auto" : "smooth", block: "center" });
  p.el.classList.remove("flash"); void p.el.offsetWidth; p.el.classList.add("flash");
});

/* ================= contents, find, scroll spy ================= */
var navlist = $("#navlist");
var side = $("#side"), menuBtn = $("#menuBtn");
function closeSide() { side.classList.remove("open"); menuBtn.setAttribute("aria-expanded", "false"); }
function openSide() { side.classList.add("open"); menuBtn.setAttribute("aria-expanded", "true"); var f = $("#find"); if (f && window.innerWidth > 960) f.focus(); }
menuBtn.addEventListener("click", function () { if (side.classList.contains("open")) closeSide(); else openSide(); });
$("#sideClose").addEventListener("click", closeSide);
$("#fabBtn").addEventListener("click", openSide);
document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeSide(); });

var subLinks = {};
$$("main > section").forEach(function (sec) {
  if (sec.classList.contains("part")) {
    var li = document.createElement("li");
    li.className = "npart";
    li.innerHTML = '<span class="rn">' + esc(sec.getAttribute("data-roman")) + '</span><a href="#' + sec.id + '">' + esc(sec.getAttribute("data-name")) + "</a>";
    navlist.appendChild(li);
    return;
  }
  if (!sec.classList.contains("module")) return;
  var li2 = document.createElement("li");
  var a = document.createElement("a");
  a.className = "nav"; a.href = "#" + sec.id;
  var n = sec.getAttribute("data-num");
  var label = sec.getAttribute("data-nav") || (n === "0" ? "··" : (sec.getAttribute("data-badge") || (n.length < 2 ? "0" + n : n)));
  a.innerHTML = '<span class="nnum">' + esc(label) + '</span><span class="ntitle">' + esc(sec.getAttribute("data-short") || sec.getAttribute("data-title")) + '</span><span class="nprog"></span>';
  li2.appendChild(a);
  var hs = $$("h3[id]", sec);
  if (hs.length) {
    var ol = document.createElement("ol");
    ol.className = "subnav";
    hs.forEach(function (h) {
      var sl = document.createElement("li");
      var sa = document.createElement("a");
      sa.href = "#" + h.id; sa.textContent = h.textContent;
      sl.appendChild(sa); ol.appendChild(sl);
      subLinks[h.id] = sa;
      sa.addEventListener("click", closeSide);
    });
    li2.appendChild(ol);
  }
  navlist.appendChild(li2);
  navItems[sec.id] = a;
  a.addEventListener("click", closeSide);
});

var activeMod = null;
function setActiveModule(id) {
  if (activeMod === id) return;
  activeMod = id;
  Object.keys(navItems).forEach(function (k) {
    var on = k === id;
    navItems[k].classList.toggle("active", on);
    navItems[k].parentNode.classList.toggle("open", on);
  });
}
if ("IntersectionObserver" in window) {
  var ioM = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) { if (en.isIntersecting) setActiveModule(en.target.id); });
  }, { rootMargin: "-30% 0px -65% 0px" });
  modules.forEach(function (m) { ioM.observe(m); });
  var ioH = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (en.isIntersecting) {
        Object.keys(subLinks).forEach(function (k) { subLinks[k].classList.toggle("active", k === en.target.id); });
      }
    });
  }, { rootMargin: "-12% 0px -80% 0px" });
  Object.keys(subLinks).forEach(function (k) { var h = document.getElementById(k); if (h) ioH.observe(h); });
}

// find a topic: headings, glossary terms, tools
var findIndex = [];
modules.forEach(function (sec) {
  var mt = sec.getAttribute("data-title");
  var n = sec.getAttribute("data-num");
  var where = n === "0" ? mt : (sec.getAttribute("data-badge") ? mt : "Module " + n + ", " + mt);
  findIndex.push({ t: mt, w: n === "0" ? "Start here" : (sec.getAttribute("data-badge") ? "Section" : "Module " + n), href: "#" + sec.id, k: 3 });
  $$("h3[id], h4[id]", sec).forEach(function (h) { findIndex.push({ t: h.textContent, w: where, href: "#" + h.id, k: h.tagName === "H3" ? 2 : 1 }); });
  $$(".note.def[id]", sec).forEach(function (d) { findIndex.push({ t: d.getAttribute("data-term"), w: "Definition in " + where, href: "#" + d.id, k: 2 }); });
  $$(".widget[data-tool][id]", sec).forEach(function (w) { findIndex.push({ t: w.getAttribute("data-title") || "Tool", w: "Tool in " + where, href: "#" + w.id, k: 1 }); });
});
// glossary-only terms join the topic finder; the glossary gets its own filter box
$$(".gl-item[data-g]").forEach(function (it) { var dt = $("dt", it); if (dt) findIndex.push({ t: dt.textContent, w: "Glossary", href: "#" + it.id, k: 2 }); });
$$(".gl-wrap").forEach(function (wrap) {
  var inp = $("input", wrap), items = $$(".gl-item", wrap), none = $(".gl-none", wrap), cnt = $(".gl-count", wrap);
  if (!inp) return;
  var texts = items.map(function (it) { return it.textContent.toLowerCase(); });
  function apply() {
    var words = inp.value.trim().toLowerCase().split(/\s+/).filter(Boolean), shown = 0;
    items.forEach(function (it, i) {
      var ok = words.every(function (w) { return texts[i].indexOf(w) >= 0; });
      it.hidden = !ok;
      if (ok) shown++;
    });
    if (none) none.hidden = shown > 0;
    if (cnt) cnt.textContent = words.length ? shown + " of " + items.length + " terms" : items.length + " terms";
  }
  inp.addEventListener("input", apply);
  inp.addEventListener("keydown", function (e) { if (e.key === "Escape") { inp.value = ""; apply(); } });
});
var findIn = $("#find"), findRes = $("#findres");
function runFind() {
  var q = findIn.value.trim().toLowerCase();
  if (!q) { findRes.hidden = true; findRes.innerHTML = ""; navlist.hidden = false; return; }
  var words = q.split(/\s+/);
  var hits = findIndex.filter(function (it) {
    var t = (it.t || "").toLowerCase();
    return words.every(function (w) { return t.indexOf(w) >= 0; });
  });
  hits.sort(function (a, b) {
    var at = a.t.toLowerCase().indexOf(q) === 0 ? 1 : 0, bt = b.t.toLowerCase().indexOf(q) === 0 ? 1 : 0;
    return (bt - at) || (b.k - a.k);
  });
  hits = hits.slice(0, 14);
  navlist.hidden = true;
  findRes.hidden = false;
  findRes.innerHTML = hits.length ? hits.map(function (h) { return '<li><a href="' + h.href + '">' + esc(h.t) + "<small>" + esc(h.w) + "</small></a></li>"; }).join("")
    : '<li class="none">Nothing matches "' + esc(findIn.value.trim()) + '". Try a shorter word, such as "latch" or "cache".</li>';
  $$("a", findRes).forEach(function (a) { a.addEventListener("click", function () { closeSide(); }); });
}
findIn.addEventListener("input", runFind);
findIn.addEventListener("keydown", function (e) {
  if (e.key === "Enter") { var a = $("a", findRes); if (a) { a.click(); location.hash = a.getAttribute("href"); } }
  if (e.key === "Escape") { findIn.value = ""; runFind(); }
});

/* ================= timing diagrams ================= */
function renderWave(el) {
  var spec;
  try { spec = JSON.parse(el.getAttribute("data-wave")); } catch (e) { el.textContent = "This timing diagram could not be read."; return; }
  var sigs = spec.signals || [];
  var topText = (spec.shade || []).some(function (x) { return !!x[2]; }) || (spec.marks || []).length || ((sigs[0] || {}).lab || []).length;
  var end = spec.end, LW = spec.lw || 112, W = spec.w || 760, RH = spec.rh || 40, top = topText ? 30 : 14;
  var rows = sigs.length, H = top + rows * RH + (spec.noTicks ? 8 : 22);
  function X(t) { return LW + (t / end) * (W - LW - 12); }
  var s = '<svg viewBox="0 0 ' + W + " " + H + '" role="img" aria-label="' + esc(spec.alt || "Timing diagram") + '">';
  (spec.shade || []).forEach(function (sh) {
    var cls = sh[3] === 2 ? "wshade2" : sh[3] === 3 ? "wshade3" : "wshade";
    s += '<rect class="' + cls + '" x="' + X(sh[0]) + '" y="' + (top - 6) + '" width="' + Math.max(0, X(sh[1]) - X(sh[0])) + '" height="' + (rows * RH + 6) + '"/>';
    if (sh[2]) s += '<text x="' + ((X(sh[0]) + X(sh[1])) / 2) + '" y="' + (top - 11) + '" text-anchor="middle">' + esc(sh[2]) + "</text>";
  });
  (spec.grid || []).forEach(function (g) {
    s += '<line class="wg" x1="' + X(g) + '" y1="' + (top - 4) + '" x2="' + X(g) + '" y2="' + (top + rows * RH) + '"/>';
    if (!spec.noTicks) s += '<text x="' + X(g) + '" y="' + (top + rows * RH + 15) + '" text-anchor="middle">' + g + "</text>";
  });
  (spec.marks || []).forEach(function (m) {
    s += '<line class="wmk" x1="' + X(m[0]) + '" y1="' + (top - 6) + '" x2="' + X(m[0]) + '" y2="' + (top + rows * RH) + '"/>';
    if (m[1]) s += '<text class="wmkt" x="' + X(m[0]) + '" y="' + (top - 11) + '" text-anchor="middle">' + esc(m[1]) + "</text>";
  });
  var auto = 0;
  sigs.forEach(function (sig, r) {
    var y0 = top + r * RH, hi = y0 + 7, lo = y0 + 29, mid = (hi + lo) / 2;
    var ch = sig.c != null ? sig.c : (sig.clk ? 0 : (auto++ % 4) + 1);
    s += '<rect class="chip f' + ch + '" x="2" y="' + (y0 + 10) + '" width="4" height="16" rx="1"/>';
    s += '<text class="wn" x="12" y="' + (y0 + 22) + '">' + esc(sig.n) + "</text>";
    if (sig.clk) {
      var P = sig.clk[0], first = sig.clk[1], hiT = sig.clk[2] != null ? sig.clk[2] : P / 2;
      var d = "M" + X(0) + " " + lo;
      var t0 = first;
      while (t0 - P >= 0) t0 -= P;
      if (t0 - P + hiT > 0) { d = "M" + X(0) + " " + hi + " H" + X(t0 - P + hiT) + " V" + lo; }
      for (var t = t0; t < end; t += P) {
        d += " H" + X(t) + " V" + hi;
        var f = Math.min(t + hiT, end);
        d += " H" + X(f);
        if (t + hiT < end) d += " V" + lo;
      }
      d += " H" + X(end);
      s += '<path class="wl c' + ch + '" d="' + d + '"/>';
    } else if (sig.v) {
      var pts = sig.v, segs = [];
      pts.forEach(function (p, k) { segs.push({ t: p[0], v: p[1], t2: k + 1 < pts.length ? pts[k + 1][0] : end }); });
      var d2 = "", prevY = null;
      segs.forEach(function (sg) {
        if (sg.v === "x") {
          if (d2) { s += '<path class="wl c' + ch + '" d="' + d2 + '"/>'; d2 = ""; }
          s += '<path class="wx" d="M' + X(sg.t) + " " + hi + " H" + X(sg.t2) + " V" + lo + " H" + X(sg.t) + ' Z"/>';
          prevY = null;
          return;
        }
        var y = sg.v === 1 ? hi : sg.v === 0 ? lo : mid;
        if (sg.v === "z") {
          if (d2) { s += '<path class="wl c' + ch + '" d="' + d2 + '"/>'; d2 = ""; }
          s += '<path class="wl wz c' + ch + '" d="M' + X(sg.t) + " " + mid + " H" + X(sg.t2) + '"/>';
          prevY = null;
          return;
        }
        if (!d2) d2 = "M" + X(sg.t) + " " + y;
        else d2 += " V" + y;
        d2 += " H" + X(sg.t2);
        prevY = y;
      });
      if (d2) s += '<path class="wl c' + ch + '" d="' + d2 + '"/>';
    } else if (sig.bus) {
      var bs = sig.bus;
      bs.forEach(function (sg, k) {
        var x1 = X(sg[0]), x2 = X(k + 1 < bs.length ? bs[k + 1][0] : end), e = Math.min(4, (x2 - x1) / 3);
        var first2 = k === 0, last = k + 1 >= bs.length;
        if (sg[1] === "x" || sg[1] === "X") {
          s += '<path class="wx" d="M' + (x1 + (first2 ? 0 : e)) + " " + hi + " H" + (x2 - (last ? 0 : e)) + " L" + x2 + " " + mid + " L" + (x2 - (last ? 0 : e)) + " " + lo + " H" + (x1 + (first2 ? 0 : e)) + " L" + x1 + " " + mid + ' Z"/>';
          return;
        }
        s += '<path class="wbus c' + ch + '" d="M' + (x1 + (first2 ? 0 : e)) + " " + hi + " H" + (x2 - (last ? 0 : e)) + " L" + x2 + " " + mid + " L" + (x2 - (last ? 0 : e)) + " " + lo + " H" + (x1 + (first2 ? 0 : e)) + " L" + x1 + " " + mid + ' Z"/>';
        if (sg[1] !== "") s += '<text class="wb" x="' + ((x1 + x2) / 2) + '" y="' + (mid + 4) + '" text-anchor="middle">' + esc(sg[1]) + "</text>";
      });
    }
    (sig.lab || []).forEach(function (lb) {
      s += '<text x="' + X(lb[0]) + '" y="' + (y0 + 3) + '" text-anchor="middle">' + esc(lb[1]) + "</text>";
    });
  });
  s += "</svg>";
  el.innerHTML = '<div class="ws">' + s + "</div>" + (spec.cap ? '<p class="wcap">' + spec.cap + "</p>" : "");
}
$$(".wave[data-wave]").forEach(renderWave);
