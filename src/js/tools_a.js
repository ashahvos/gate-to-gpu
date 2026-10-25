/* ================= gate symbols ================= */
function gateSVG(type) {
  var inv = /^(NAND|NOR|XNOR|NOT)$/.test(type);
  var one = (type === "NOT" || type === "BUF");
  var s = '<svg class="gsym" viewBox="0 0 92 60" aria-hidden="true">';
  if (one) s += '<path class="gl" d="M0 30 H24"/>';
  else s += '<path class="gl" d="M0 20 H30 M0 40 H30"/>';
  var outX;
  if (type === "AND" || type === "NAND") { s += '<path class="gb" d="M20 10 H44 A20 20 0 0 1 44 50 H20 Z"/>'; outX = 64; }
  else if (type === "OR" || type === "NOR") { s += '<path class="gb" d="M16 10 Q44 10 64 30 Q44 50 16 50 Q28 30 16 10 Z"/>'; outX = 64; }
  else if (type === "XOR" || type === "XNOR") { s += '<path class="gb" d="M22 10 Q50 10 70 30 Q50 50 22 50 Q34 30 22 10 Z"/><path class="gl" d="M14 10 Q26 30 14 50"/>'; outX = 70; }
  else { s += '<path class="gb" d="M24 12 L60 30 L24 48 Z"/>'; outX = 60; }
  if (inv) { s += '<circle class="gb" cx="' + (outX + 4.5) + '" cy="30" r="4.5"/>'; outX += 9; }
  s += '<path class="gl" d="M' + outX + ' 30 H92"/></svg>';
  return s;
}

/* ================= Boolean expression parser ================= */
function parseBool(src) {
  var s = src.replace(/\s+/g, "");
  if (!s) throw new Error("Type an expression first.");
  var i = 0, vars = {};
  function peek() { return s.charAt(i); }
  function isFactorStart(c) { return c !== "" && /[A-Za-z01(~!¬]/.test(c); }
  function parseOr() {
    var n = parseXor();
    while (peek() === "+" || peek() === "|") { i++; n = { t: "or", l: n, r: parseXor() }; }
    return n;
  }
  function parseXor() {
    var n = parseAnd();
    while (peek() === "^" || peek() === "⊕") { i++; n = { t: "xor", l: n, r: parseAnd() }; }
    return n;
  }
  function parseAnd() {
    var n = parseUnary();
    for (;;) {
      var c = peek();
      if (c === "·" || c === "*" || c === "&" || c === "." || c === "∙") { i++; n = { t: "and", l: n, r: parseUnary() }; }
      else if (isFactorStart(c)) { n = { t: "and", l: n, r: parseUnary() }; }
      else break;
    }
    return n;
  }
  function parseUnary() {
    var c = peek();
    if (c === "~" || c === "!" || c === "¬") { i++; return { t: "not", a: parseUnary() }; }
    var n = parsePrimary();
    while (peek() === "'" || peek() === "’" || peek() === "′") { i++; n = { t: "not", a: n }; }
    return n;
  }
  function parsePrimary() {
    var c = peek();
    if (c === "") throw new Error("The expression ends too early.");
    if (c === "(") {
      i++; var n = parseOr();
      if (peek() !== ")") throw new Error("A closing parenthesis is missing.");
      i++; return n;
    }
    if (c === "0" || c === "1") { i++; return { t: "c", v: +c }; }
    if (/[A-Za-z]/.test(c)) { i++; var v = c.toUpperCase(); vars[v] = 1; return { t: "v", v: v }; }
    throw new Error('Unexpected "' + c + '" at character ' + (i + 1) + ".");
  }
  var tree = parseOr();
  if (i < s.length) throw new Error('Unexpected "' + s.charAt(i) + '" at character ' + (i + 1) + ".");
  return { tree: tree, vars: Object.keys(vars).sort() };
}
function evalBool(n, env) {
  switch (n.t) {
    case "c": return n.v;
    case "v": return env[n.v];
    case "not": return 1 - evalBool(n.a, env);
    case "and": return evalBool(n.l, env) & evalBool(n.r, env);
    case "or": return evalBool(n.l, env) | evalBool(n.r, env);
    case "xor": return evalBool(n.l, env) ^ evalBool(n.r, env);
  }
  return 0;
}

/* ================= exact two-level minimizer (n <= 5) ================= */
function minimize(n, ones, dcs, names) {
  names = names || ["A", "B", "C", "D", "E"].slice(0, n);
  var N = 1 << n, isOne = {}, isDc = {};
  ones.forEach(function (m) { isOne[m] = 1; });
  dcs.forEach(function (m) { isDc[m] = 1; });
  if (!ones.length) return { terms: [], strs: [], expr: "0" };
  var terms = [], total = Math.pow(3, n);
  for (var code = 0; code < total; code++) {
    var pat = [], c = code;
    for (var k = 0; k < n; k++) { pat.push(c % 3); c = Math.floor(c / 3); }
    var cover = [], ok = true;
    for (var m = 0; m < N && ok; m++) {
      var match = true;
      for (var j = 0; j < n; j++) {
        var bit = (m >> (n - 1 - j)) & 1;
        if (pat[j] !== 2 && pat[j] !== bit) { match = false; break; }
      }
      if (match) { if (!isOne[m] && !isDc[m]) ok = false; else cover.push(m); }
    }
    if (ok) terms.push({ pat: pat, cover: cover, lits: pat.filter(function (x) { return x !== 2; }).length });
  }
  var primes = terms.filter(function (t) {
    return !terms.some(function (u) {
      return u !== t && u.cover.length > t.cover.length && t.cover.every(function (x) { return u.cover.indexOf(x) >= 0; });
    });
  }).filter(function (t) { return t.cover.some(function (x) { return isOne[x]; }); });
  var best = null;
  function lits(arr) { return arr.reduce(function (a, t) { return a + t.lits; }, 0); }
  function dfs(chosen, unc) {
    if (!unc.length) {
      if (!best || chosen.length < best.length || (chosen.length === best.length && lits(chosen) < lits(best))) best = chosen.slice();
      return;
    }
    if (best && chosen.length >= best.length) return;
    var m0 = unc[0];
    primes.forEach(function (t) {
      if (t.cover.indexOf(m0) >= 0 && chosen.indexOf(t) < 0) {
        chosen.push(t);
        dfs(chosen, unc.filter(function (x) { return t.cover.indexOf(x) < 0; }));
        chosen.pop();
      }
    });
  }
  dfs([], ones.slice().sort(function (a, b) { return a - b; }));
  best.sort(function (a, b) { return a.lits - b.lits || a.pat.join("").localeCompare(b.pat.join("")); });
  function termStr(t) {
    var s = "";
    t.pat.forEach(function (p, j) { if (p !== 2) s += names[j] + (p === 0 ? "′" : ""); });
    return s || "1";
  }
  var strs = best.map(termStr);
  return { terms: best, strs: strs, expr: strs.indexOf("1") >= 0 ? "1" : strs.join(" + "), primes: primes };
}
function minimizePOS(n, zeros, dcs, names) {
  // minimal POS of F = complement of the minimal SOP of F'
  names = names || ["A", "B", "C", "D", "E"].slice(0, n);
  if (!zeros.length) return { expr: "1", sums: [] };
  var r = minimize(n, zeros, dcs, names);
  if (r.expr === "1") return { expr: "0", sums: [] };
  var sums = r.terms.map(function (t) {
    var lits = [];
    t.pat.forEach(function (p, j) { if (p !== 2) lits.push(names[j] + (p === 1 ? "′" : "")); });
    return lits;
  });
  var expr = sums.map(function (l) { return l.length > 1 || sums.length > 1 ? "(" + l.join(" + ") + ")" : l.join(" + "); }).join("");
  return { expr: expr, sums: sums, terms: r.terms };
}
window.__g2gMinimize = minimize;

var TOOLS = {};

/* ================= number converter ================= */
TOOLS.numconv = function (el) {
  el.innerHTML = toolHead("Number converter", "one bit pattern, every common reading") + '<div class="wbody">' +
    '<div class="wrow"><label for="nc-in">Value</label><input type="text" id="nc-in" value="-19" size="14" spellcheck="false" autocomplete="off">' +
    '<label for="nc-base">written in</label><select id="nc-base"><option value="10">decimal</option><option value="16">hex</option><option value="2">binary</option><option value="8">octal</option></select>' +
    '<label for="nc-w">width</label><select id="nc-w"><option>4</option><option selected>8</option><option>12</option><option>16</option><option>32</option></select><span class="wlab">bits</span></div>' +
    '<div class="wout" id="nc-out" aria-live="polite"></div></div>';
  var inp = $("#nc-in", el), base = $("#nc-base", el), wsel = $("#nc-w", el), out = $("#nc-out", el);
  function group4(b) { return b.replace(/\B(?=(.{4})+(?!.))/g, " "); }
  function run() {
    var w = parseInt(wsel.value, 10), W = BigInt(w), MOD = 1n << W, HALF = 1n << (W - 1n);
    var raw = inp.value.replace(/[\s_]/g, "").toLowerCase();
    var b = base.value, pattern;
    try {
      if (!raw) throw new Error("Type a number.");
      if (b === "10") {
        if (!/^-?\d+$/.test(raw)) throw new Error("Use digits 0 to 9, with an optional minus sign.");
        var v = BigInt(raw);
        if (v < 0n) {
          if (v < -HALF) throw new Error(raw + " is below the " + w + "-bit two's complement minimum, −" + HALF + ". Pick a wider width.");
          pattern = MOD + v;
        } else {
          if (v >= MOD) throw new Error(raw + " needs more than " + w + " bits (the unsigned maximum is " + (MOD - 1n) + ").");
          pattern = v;
        }
      } else {
        var pre = { "16": /^0x/, "2": /^0b/, "8": /^0o/ }[b];
        var digits = raw.replace(pre, "");
        var re = { "16": /^[0-9a-f]+$/, "2": /^[01]+$/, "8": /^[0-7]+$/ }[b];
        if (!re.test(digits)) throw new Error({ "16": "Use hex digits 0–9 and A–F.", "2": "Use only 0 and 1.", "8": "Use octal digits 0–7." }[b]);
        pattern = 0n;
        for (var k = 0; k < digits.length; k++) pattern = pattern * BigInt(b) + BigInt(parseInt(digits[k], 16));
        if (pattern >= MOD) throw new Error("That pattern needs more than " + w + " bits.");
      }
    } catch (e) { out.innerHTML = '<p class="werr">' + esc(e.message) + "</p>"; return; }
    var bin = pattern.toString(2).padStart(w, "0");
    var hex = pattern.toString(16).toUpperCase().padStart(Math.ceil(w / 4), "0");
    var oct = pattern.toString(8);
    var msb = pattern >= HALF;
    var twos = msb ? pattern - MOD : pattern;
    var mag = pattern & (HALF - 1n);
    var signMag = msb ? (mag === 0n ? "−0" : "−" + mag) : String(mag);
    var ones = msb ? (((~pattern) & (MOD - 1n)) === 0n ? "−0" : "−" + ((~pattern) & (MOD - 1n))) : String(pattern);
    var excess = pattern - HALF;
    var html = '<dl class="kv"><dt>Binary</dt><dd>' + group4(bin) + "</dd><dt>Hex</dt><dd>0x" + hex + "</dd><dt>Octal</dt><dd>" + oct + "</dd>" +
      "<dt>Unsigned</dt><dd>" + pattern + "</dd><dt>Two's complement</dt><dd>" + twos + "</dd>" +
      "<dt>Sign-magnitude</dt><dd>" + signMag + "</dd><dt>One's complement</dt><dd>" + ones + "</dd>" +
      "<dt>Excess-" + HALF + " (bias)</dt><dd>" + excess + "</dd>";
    if (w % 4 === 0) {
      var bcdOk = /^[0-9]+$/.test(hex);
      html += "<dt>As BCD digits</dt><dd>" + (bcdOk ? hex.replace(/^0+(?=.)/, "") : "not valid BCD (a nibble is above 9)") + "</dd>";
    }
    if (pattern >= 32n && pattern <= 126n) html += "<dt>As an ASCII character</dt><dd>'" + esc(String.fromCharCode(Number(pattern))) + "'</dd>";
    html += "</dl>";
    if (twos < 0n) {
      var m2 = -twos;
      if (m2 < MOD) {
        var magBin = m2.toString(2).padStart(w, "0");
        var invBin = ((~m2) & (MOD - 1n)).toString(2).padStart(w, "0");
        html += '<p class="wnote">How ' + twos + " is formed: +" + m2 + " = <span class=\"m\">" + group4(magBin) + '</span>, invert every bit to get <span class="m">' + group4(invBin) + '</span>, then add 1 to get <span class="m">' + group4(bin) + "</span>.</p>";
      }
    }
    html += '<p class="wnote">' + w + "-bit ranges: unsigned 0 to " + (MOD - 1n) + "; two's complement −" + HALF + " to " + (HALF - 1n) + "; sign-magnitude and one's complement −" + (HALF - 1n) + " to " + (HALF - 1n) + ".</p>";
    out.innerHTML = html;
  }
  [inp, base, wsel].forEach(function (x) { x.addEventListener("input", run); x.addEventListener("change", run); });
  run();
};

/* ================= gate playground ================= */
TOOLS.gates = function (el) {
  var A = 1, B = 0;
  el.innerHTML = toolHead("Gate playground", "toggle the inputs") + '<div class="wbody"><div class="wrow"><span class="wlab">Inputs</span>' +
    '<button type="button" class="bit" id="g-a" aria-pressed="true">A = 1</button><button type="button" class="bit" id="g-b" aria-pressed="false">B = 0</button></div>' +
    '<div class="tbl" style="margin:0"><table><thead><tr><th>Gate</th><th>Symbol</th><th>Output</th><th>Expression</th></tr></thead><tbody id="g-body"></tbody></table></div></div>';
  var rows = [
    ["NOT", "A′ (uses A only)", function () { return 1 - A; }],
    ["BUF", "A (uses A only)", function () { return A; }],
    ["AND", "A · B", function () { return A & B; }],
    ["OR", "A + B", function () { return A | B; }],
    ["NAND", "(A · B)′", function () { return 1 - (A & B); }],
    ["NOR", "(A + B)′", function () { return 1 - (A | B); }],
    ["XOR", "A ⊕ B", function () { return A ^ B; }],
    ["XNOR", "(A ⊕ B)′", function () { return 1 - (A ^ B); }]
  ];
  var body = $("#g-body", el), ba = $("#g-a", el), bb = $("#g-b", el);
  function draw() {
    ba.textContent = "A = " + A; bb.textContent = "B = " + B;
    ba.setAttribute("aria-pressed", String(!!A)); bb.setAttribute("aria-pressed", String(!!B));
    body.innerHTML = rows.map(function (r) {
      var o = r[2]();
      return "<tr><td><b>" + r[0] + "</b></td><td>" + gateSVG(r[0]) + '</td><td style="white-space:nowrap"><span class="lamp' + (o ? " on" : "") +
        '"></span> <span class="m">' + o + '</span></td><td class="m">' + r[1] + "</td></tr>";
    }).join("");
  }
  ba.addEventListener("click", function () { A ^= 1; draw(); });
  bb.addEventListener("click", function () { B ^= 1; draw(); });
  draw();
};

/* ================= truth table and simplifier ================= */
TOOLS.truthtable = function (el) {
  el.innerHTML = toolHead("Truth table and simplifier", "type any expression") + '<div class="wbody">' +
    '<div class="wrow"><label for="tt-in">F =</label><input type="text" id="tt-in" value="A·B′ + A′·B + A·B" size="28" spellcheck="false" autocomplete="off"></div>' +
    '<p class="wnote">Variables are single letters. NOT: <code>A\'</code> or <code>~A</code>. AND: <code>AB</code>, <code>A·B</code>, <code>A*B</code> or <code>A&amp;B</code>. OR: <code>+</code> or <code>|</code>. XOR: <code>^</code>. Up to 5 variables.</p>' +
    '<div class="wout" id="tt-out" aria-live="polite"></div></div>';
  var inp = $("#tt-in", el), out = $("#tt-out", el);
  function run() {
    var r;
    try { r = parseBool(inp.value); } catch (e) { out.innerHTML = '<p class="werr">' + esc(e.message) + "</p>"; return; }
    var vars = r.vars, n = vars.length;
    if (n > 5) { out.innerHTML = '<p class="werr">Use at most 5 variables.</p>'; return; }
    var rows = [], ones = [], zeros = [];
    for (var m = 0; m < (1 << n); m++) {
      var env = {};
      vars.forEach(function (v, j) { env[v] = (m >> (n - 1 - j)) & 1; });
      var f = evalBool(r.tree, env);
      (f ? ones : zeros).push(m);
      rows.push("<tr><td>" + m + "</td>" + vars.map(function (v) { return "<td>" + env[v] + "</td>"; }).join("") + '<td class="o' + (f ? " v1" : "") + '">' + f + "</td></tr>");
    }
    var head = "<tr><th>row</th>" + vars.map(function (v) { return "<th>" + v + "</th>"; }).join("") + '<th class="o">F</th></tr>';
    var sop = n ? minimize(n, ones, [], vars) : { expr: String(evalBool(r.tree, {})) };
    var pos = n ? minimizePOS(n, zeros, [], vars) : { expr: String(evalBool(r.tree, {})) };
    out.innerHTML = '<div class="tbl tt" style="margin:0"><table><thead>' + head + "</thead><tbody>" + rows.join("") + "</tbody></table></div>" +
      '<dl class="kv"><dt>Sum of minterms</dt><dd>' + (n ? "F = Σm(" + ones.join(", ") + ")" : "—") +
      "</dd><dt>Product of maxterms</dt><dd>" + (n ? "F = ΠM(" + zeros.join(", ") + ")" : "—") +
      '</dd><dt>Minimal sum of products</dt><dd class="sop">F = ' + sop.expr + '</dd><dt>Minimal product of sums</dt><dd class="sop">F = ' + pos.expr + "</dd></dl>";
  }
  inp.addEventListener("input", run);
  run();
};

/* ================= K-map solver ================= */
TOOLS.kmap = function (el) {
  var COLORS = ["var(--cardinal)", "var(--green)", "var(--gold-deep)", "var(--plum)", "var(--orange)", "var(--ink-2)", "var(--brown)", "var(--olive)"];
  var n = 4, cells = new Array(16).fill(0);
  [0, 1, 2, 5, 8, 9, 10].forEach(function (m) { cells[m] = 1; });
  el.innerHTML = toolHead("K-map solver", "click cells: 0, then 1, then X") + '<div class="wbody">' +
    '<div class="wrow"><label for="km-n">Variables</label><select id="km-n"><option value="2">2 (A, B)</option><option value="3">3 (A, B, C)</option><option value="4" selected>4 (A, B, C, D)</option></select>' +
    '<label for="km-mode">Show</label><select id="km-mode"><option value="sop">sum of products (group the 1s)</option><option value="pos">product of sums (group the 0s)</option></select>' +
    '<button type="button" class="btn sm ghost" id="km-clear">Clear</button><button type="button" class="btn sm ghost" id="km-ex">Load example</button></div>' +
    '<p class="wnote">Each click cycles a cell through 0, 1 and X (don\'t care). Small numbers are minterm indices. Colored dots show which group covers each cell.</p>' +
    '<div class="tbl" id="km-grid" style="margin:0"></div><div class="wout" id="km-out" aria-live="polite"></div></div>';
  var grid = $("#km-grid", el), out = $("#km-out", el), nsel = $("#km-n", el), msel = $("#km-mode", el);
  var gray = [0, 1, 3, 2];
  function layout() {
    if (n === 2) return { rows: [0, 1], cols: [0, 1], rl: ["0", "1"], cl: ["0", "1"], corner: "A \\ B", idx: function (r, c) { return r * 2 + c; } };
    if (n === 3) return { rows: [0, 1], cols: gray, rl: ["0", "1"], cl: ["00", "01", "11", "10"], corner: "A \\ BC", idx: function (r, c) { return r * 4 + c; } };
    return { rows: gray, cols: gray, rl: ["00", "01", "11", "10"], cl: ["00", "01", "11", "10"], corner: "AB \\ CD", idx: function (r, c) { return r * 4 + c; } };
  }
  function draw() {
    var L = layout(), names = ["A", "B", "C", "D"].slice(0, n);
    var ones = [], dcs = [], zeros = [];
    for (var m = 0; m < (1 << n); m++) { if (cells[m] === 1) ones.push(m); else if (cells[m] === 2) dcs.push(m); else zeros.push(m); }
    var pos = msel.value === "pos";
    var res = pos ? minimizePOS(n, zeros, dcs, names) : minimize(n, ones, dcs, names);
    var labels = pos ? (res.sums || []).map(function (l) { return "(" + l.join(" + ") + ")"; }) : (res.strs || []);
    var dotMap = {};
    (res.terms || []).forEach(function (t, k) { t.cover.forEach(function (mm) { (dotMap[mm] = dotMap[mm] || []).push(COLORS[k % COLORS.length]); }); });
    var h = '<table class="kmap"><thead><tr><th>' + L.corner + "</th>" + L.cl.map(function (c) { return "<th>" + c + "</th>"; }).join("") + "</tr></thead><tbody>";
    L.rows.forEach(function (r, ri) {
      h += "<tr><th>" + L.rl[ri] + "</th>";
      L.cols.forEach(function (c) {
        var mm = L.idx(r, c), v = cells[mm];
        var dots = (dotMap[mm] || []).map(function (col) { return '<i style="background:' + col + '"></i>'; }).join("");
        h += '<td><button type="button" data-m="' + mm + '" class="' + (v === 1 ? "v1" : v === 2 ? "vx" : "") + '" aria-label="minterm ' + mm + ", value " + (v === 2 ? "don't care" : v) + '"><span class="mi">' + mm + "</span>" +
          (v === 2 ? "X" : v) + '<span class="dots">' + dots + "</span></button></td>";
      });
      h += "</tr>";
    });
    grid.innerHTML = h + "</tbody></table>";
    $$("button[data-m]", grid).forEach(function (b) {
      b.addEventListener("click", function () { var mm = +b.getAttribute("data-m"); cells[mm] = (cells[mm] + 1) % 3; draw(); });
    });
    var chips = labels.map(function (s, k) { return '<span style="border-color:' + COLORS[k % COLORS.length] + '">' + esc(s) + "</span>"; }).join("");
    out.innerHTML = '<dl class="kv"><dt>Function</dt><dd>F = Σm(' + ones.join(", ") + ")" + (dcs.length ? " + d(" + dcs.join(", ") + ")" : "") +
      '</dd><dt>' + (pos ? "Minimal product of sums" : "Minimal sum of products") + '</dt><dd class="sop">F = ' + res.expr + "</dd></dl>" + (chips ? '<div class="term-list">' + chips + "</div>" : "");
  }
  nsel.addEventListener("change", function () { n = +nsel.value; cells = new Array(1 << n).fill(0); draw(); });
  msel.addEventListener("change", draw);
  $("#km-clear", el).addEventListener("click", function () { cells = new Array(1 << n).fill(0); draw(); });
  $("#km-ex", el).addEventListener("click", function () {
    cells = new Array(1 << n).fill(0);
    var e = n === 4 ? [0, 1, 2, 5, 8, 9, 10] : n === 3 ? [3, 5, 6, 7] : [1, 3];
    e.forEach(function (mm) { cells[mm] = 1; });
    draw();
  });
  draw();
};

/* ================= 4-bit adder / subtractor ================= */
TOOLS.adder = function (el) {
  var a = [1, 0, 1, 1], b = [0, 1, 1, 0], sub = false; // index 0 = bit 3 (MSB)
  el.innerHTML = toolHead("4-bit adder and subtractor", "click bits to change A and B") + '<div class="wbody">' +
    '<div class="wrow"><span class="wlab">Operation</span><div class="seg" role="group" aria-label="Operation"><button type="button" id="ad-add" aria-pressed="true">A + B</button><button type="button" id="ad-sub" aria-pressed="false">A − B</button></div></div>' +
    '<div class="tbl" style="margin:0"><table id="ad-t"></table></div><div class="wout" id="ad-out" aria-live="polite"></div></div>';
  var t = $("#ad-t", el), out = $("#ad-out", el);
  function val(bits) { return bits[0] * 8 + bits[1] * 4 + bits[2] * 2 + bits[3]; }
  function sval(bits) { var u = val(bits); return u >= 8 ? u - 16 : u; }
  function draw() {
    var be = b.map(function (x) { return sub ? 1 - x : x; });
    var s = [0, 0, 0, 0], carryIn = [0, 0, 0, 0], cin = sub ? 1 : 0;
    for (var i = 3; i >= 0; i--) { carryIn[i] = cin; var sum = a[i] + be[i] + cin; s[i] = sum & 1; cin = sum >> 1; }
    var cout = cin, v = carryIn[0] ^ cout, Z = val(s) === 0, N = s[0] === 1;
    function bitBtns(arr, name) {
      return arr.map(function (x, i) { return '<td><button type="button" class="bit" data-r="' + name + '" data-i="' + i + '" aria-pressed="' + (x ? "true" : "false") + '" aria-label="' + name + " bit " + (3 - i) + '">' + x + "</button></td>"; }).join("");
    }
    t.innerHTML = '<thead><tr><th></th><th>bit 3</th><th>bit 2</th><th>bit 1</th><th>bit 0</th><th>unsigned</th><th>signed</th></tr></thead><tbody>' +
      '<tr><td class="m" style="color:var(--ink-2)">carry in</td>' + carryIn.map(function (x) { return '<td class="m" style="color:var(--gold-ink);text-align:center">' + x + "</td>"; }).join("") + "<td></td><td></td></tr>" +
      "<tr><td><b>A</b></td>" + bitBtns(a, "A") + '<td class="m">' + val(a) + '</td><td class="m">' + sval(a) + "</td></tr>" +
      "<tr><td><b>B</b></td>" + bitBtns(b, "B") + '<td class="m">' + val(b) + '</td><td class="m">' + sval(b) + "</td></tr>" +
      (sub ? '<tr><td class="m" style="color:var(--ink-2)">B inverted</td>' + be.map(function (x) { return '<td class="m" style="text-align:center">' + x + "</td>"; }).join("") + "<td></td><td></td></tr>" : "") +
      "<tr><td><b>" + (sub ? "A − B" : "A + B") + "</b></td>" + s.map(function (x) { return '<td class="m" style="text-align:center;font-weight:700;font-size:1.05rem">' + x + "</td>"; }).join("") +
      '<td class="m">' + val(s) + '</td><td class="m">' + sval(s) + "</td></tr></tbody>";
    $$("button[data-r]", t).forEach(function (btn) {
      btn.addEventListener("click", function () {
        var arr = btn.getAttribute("data-r") === "A" ? a : b, i = +btn.getAttribute("data-i");
        arr[i] ^= 1; draw();
      });
    });
    var trueU = sub ? val(a) - val(b) : val(a) + val(b), trueS = sub ? sval(a) - sval(b) : sval(a) + sval(b);
    function flag(name, on, why) { return '<span class="tag ' + (on ? "on" : "off") + '" title="' + why + '">' + name + " = " + (on ? 1 : 0) + "</span>"; }
    out.innerHTML = '<div class="wrow">' + flag("C", cout, "carry out of bit 3") + flag("V", v, "signed overflow") + flag("Z", Z, "result is zero") + flag("N", N, "bit 3 of the result") + "</div>" +
      "<p>Exact answer: unsigned " + trueU + ", signed " + trueS + ". " +
      (sub ? "Subtraction sends B through XOR gates (inverting it) and makes the first carry-in 1, so the circuit computes A + B′ + 1. " + (cout ? "C = 1 means no borrow: A ≥ B as unsigned numbers. " : "C = 0 means a borrow happened: A < B as unsigned numbers, so the unsigned result wrapped. ") :
        (cout ? "C = 1: the unsigned sum needed a fifth bit, so the 4-bit result is wrong as an unsigned number. " : "C = 0: the unsigned sum fits in 4 bits. ")) +
      (v ? "V = 1: carry into bit 3 differs from carry out of bit 3, so the signed result is outside −8 to 7 and is wrong." : "V = 0: the signed result is correct.") + "</p>";
  }
  var ba = $("#ad-add", el), bs = $("#ad-sub", el);
  ba.addEventListener("click", function () { sub = false; ba.setAttribute("aria-pressed", "true"); bs.setAttribute("aria-pressed", "false"); draw(); });
  bs.addEventListener("click", function () { sub = true; bs.setAttribute("aria-pressed", "true"); ba.setAttribute("aria-pressed", "false"); draw(); });
  draw();
};

/* ================= cache simulator ================= */
TOOLS.cache = function (el) {
  el.innerHTML = toolHead("Cache simulator", "LRU replacement, 32-bit addresses") + '<div class="wbody">' +
    '<div class="wrow"><label for="c-size">Cache size</label><select id="c-size"><option>32</option><option selected>64</option><option>128</option><option>256</option><option>1024</option><option>4096</option></select><span class="wlab">bytes</span>' +
    '<label for="c-block">Block</label><select id="c-block"><option>4</option><option>8</option><option selected>16</option><option>32</option><option>64</option></select><span class="wlab">bytes</span>' +
    '<label for="c-assoc">Ways</label><select id="c-assoc"><option value="1" selected>1 (direct-mapped)</option><option value="2">2-way</option><option value="4">4-way</option><option value="0">fully associative</option></select></div>' +
    '<div><label class="wlab" for="c-addr">Byte addresses in order (decimal, or hex with 0x)</label><textarea id="c-addr" spellcheck="false">0, 4, 16, 0, 64, 0, 128, 4</textarea></div>' +
    '<div class="wout" id="c-out" aria-live="polite"></div></div>';
  var sz = $("#c-size", el), bl = $("#c-block", el), as = $("#c-assoc", el), ad = $("#c-addr", el), out = $("#c-out", el);
  function lg(x) { return Math.round(Math.log2(x)); }
  function run() {
    var size = +sz.value, block = +bl.value, ways = +as.value;
    var lines = size / block;
    if (lines < 1) { out.innerHTML = '<p class="werr">The block is bigger than the whole cache. Pick a smaller block or a bigger cache.</p>'; return; }
    if (ways === 0) ways = lines;
    if (ways > lines) { out.innerHTML = '<p class="werr">This cache only has ' + lines + " line" + (lines > 1 ? "s" : "") + ", so it can't be " + ways + "-way. Pick fewer ways.</p>"; return; }
    var sets = lines / ways;
    var toks = ad.value.split(/[\s,;]+/).filter(Boolean);
    if (toks.length > 80) toks = toks.slice(0, 80);
    var addrs = [];
    for (var i = 0; i < toks.length; i++) {
      var tk = toks[i].toLowerCase(), v = /^0x[0-9a-f]+$/.test(tk) ? parseInt(tk, 16) : (/^\d+$/.test(tk) ? parseInt(tk, 10) : NaN);
      if (isNaN(v)) { out.innerHTML = '<p class="werr">"' + esc(toks[i]) + '" isn\'t an address. Use decimal like 64 or hex like 0x40.</p>'; return; }
      addrs.push(v);
    }
    var store = [], seen = {}, time = 0, hits = 0, rows = "";
    for (var s = 0; s < sets; s++) store.push([]);
    addrs.forEach(function (a) {
      time++;
      var blk = Math.floor(a / block), set = blk % sets, tag = Math.floor(blk / sets);
      var S = store[set], found = null;
      S.forEach(function (ln) { if (ln.tag === tag) found = ln; });
      var res, note = "";
      if (found) { res = '<span class="tag hit">hit</span>'; found.t = time; hits++; }
      else {
        res = '<span class="tag miss">miss</span>';
        if (!seen[blk]) note = "first use of this block (compulsory)";
        if (S.length < ways) { S.push({ tag: tag, t: time }); }
        else {
          var lru = S[0]; S.forEach(function (ln) { if (ln.t < lru.t) lru = ln; });
          note = (note ? note + "; " : "") + "evicts tag " + lru.tag;
          lru.tag = tag; lru.t = time;
        }
      }
      seen[blk] = 1;
      rows += "<tr><td>" + a + " (0x" + a.toString(16).toUpperCase() + ")</td><td>" + blk + "</td><td>" + set + "</td><td>" + tag + "</td><td>" + res + '</td><td style="text-align:left">' + note + "</td></tr>";
    });
    var off = lg(block), idx = lg(sets), tagb = 32 - off - idx;
    out.innerHTML = "<p>" + lines + " lines arranged as " + sets + " set" + (sets > 1 ? "s" : "") + " of " + ways + " way" + (ways > 1 ? "s" : "") + ".</p>" +
      '<div class="addr" aria-label="Address fields"><div class="a-tag" style="flex:' + Math.max(tagb, 4) + '">tag<small>' + tagb + " bits</small></div>" +
      (idx ? '<div class="a-idx" style="flex:' + Math.max(idx, 4) + '">index<small>' + idx + " bits</small></div>" : "") +
      '<div class="a-off" style="flex:' + Math.max(off, 4) + '">offset<small>' + off + " bits</small></div></div>" +
      '<div class="tbl tt" style="margin:0"><table><thead><tr><th>address</th><th>block</th><th>set</th><th>tag</th><th>result</th><th>note</th></tr></thead><tbody>' + rows +
      "</tbody></table></div><p><b>" + hits + " hit" + (hits === 1 ? "" : "s") + "</b> and " + (addrs.length - hits) + " miss" + (addrs.length - hits === 1 ? "" : "es") +
      (addrs.length ? " (hit rate " + Math.round(100 * hits / addrs.length) + "%)" : "") + ".</p>";
  }
  [sz, bl, as].forEach(function (x) { x.addEventListener("change", run); });
  ad.addEventListener("input", run);
  run();
};
