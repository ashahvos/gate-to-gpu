/* ================= shared: SI parsing and small plots ================= */
function parseSI(str) {
  var m = String(str).trim().match(/^([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)\s*([pnuµmkKMG]?)\s*(?:ohms?|Ω|F|Hz|s|V|A)?$/);
  if (!m) return NaN;
  var mult = { "": 1, p: 1e-12, n: 1e-9, u: 1e-6, "µ": 1e-6, m: 1e-3, k: 1e3, K: 1e3, M: 1e6, G: 1e9 }[m[2]];
  return parseFloat(m[1]) * mult;
}
function plotSVG(o) {
  // o: {w,h,x0,x1,y0,y1,logx,xt:[[v,label]],yt:[[v,label]],series:[{pts:[[x,y]],cls}],marks:[{x,y,label}],xl,yl,vlines:[[x,cls]],hlines:[[y,cls]]}
  var W = o.w || 360, H = o.h || 220, L = 46, R = 12, T = 12, B = 34;
  function fx(x) { var a = o.logx ? Math.log10(x) : x, a0 = o.logx ? Math.log10(o.x0) : o.x0, a1 = o.logx ? Math.log10(o.x1) : o.x1; return L + (a - a0) / (a1 - a0) * (W - L - R); }
  function fy(y) { return T + (o.y1 - y) / (o.y1 - o.y0) * (H - T - B); }
  var s = '<svg class="plot" viewBox="0 0 ' + W + " " + H + '" role="img" aria-label="' + esc(o.alt || "plot") + '">';
  (o.xt || []).forEach(function (t) { var X = fx(t[0]); s += '<line class="gr" x1="' + X + '" y1="' + T + '" x2="' + X + '" y2="' + (H - B) + '"/><text x="' + X + '" y="' + (H - B + 14) + '" text-anchor="middle">' + esc(t[1]) + "</text>"; });
  (o.yt || []).forEach(function (t) { var Y = fy(t[0]); s += '<line class="gr" x1="' + L + '" y1="' + Y + '" x2="' + (W - R) + '" y2="' + Y + '"/><text x="' + (L - 6) + '" y="' + (Y + 4) + '" text-anchor="end">' + esc(t[1]) + "</text>"; });
  s += '<path class="ax" d="M' + L + " " + T + " V" + (H - B) + " H" + (W - R) + '"/>';
  (o.hlines || []).forEach(function (h) { var Y = fy(h[0]); s += '<line class="' + (h[1] || "l3") + '" x1="' + L + '" y1="' + Y + '" x2="' + (W - R) + '" y2="' + Y + '"/>'; });
  (o.vlines || []).forEach(function (v) { var X = fx(v[0]); s += '<line class="' + (v[1] || "l3") + '" x1="' + X + '" y1="' + T + '" x2="' + X + '" y2="' + (H - B) + '"/>'; });
  (o.series || []).forEach(function (se) {
    var d = se.pts.map(function (p, k) { return (k ? "L" : "M") + fx(p[0]).toFixed(1) + " " + fy(clamp(p[1], o.y0, o.y1)).toFixed(1); }).join(" ");
    s += '<path class="' + se.cls + '" d="' + d + '"/>';
  });
  (o.marks || []).forEach(function (m) {
    var X = fx(m.x), Y = fy(clamp(m.y, o.y0, o.y1));
    s += '<circle class="pt" cx="' + X + '" cy="' + Y + '" r="4.5"/>';
    if (m.label) s += '<text class="lb" x="' + (X + (m.dx || 8)) + '" y="' + (Y + (m.dy || -8)) + '"' + (m.anchor ? ' text-anchor="' + m.anchor + '"' : "") + ">" + esc(m.label) + "</text>";
  });
  if (o.xl) s += '<text class="lb" x="' + ((L + W - R) / 2) + '" y="' + (H - 4) + '" text-anchor="middle">' + esc(o.xl) + "</text>";
  if (o.yl) s += '<text class="lb" x="' + 4 + '" y="' + (T + 2) + '" text-anchor="start" dominant-baseline="hanging" transform="rotate(0)">' + "" + "</text>";
  s += "</svg>";
  return s;
}

/* ================= floating-point explorer ================= */
TOOLS.float = function (el) {
  var FMT = { fp32: { e: 8, f: 23, name: "FP32" }, fp16: { e: 5, f: 10, name: "FP16" }, bf16: { e: 8, f: 7, name: "BF16" } };
  var fmt = "fp32", bits = [];
  el.innerHTML = toolHead("Floating-point explorer", "IEEE 754 encoding, bit by bit") + '<div class="wbody">' +
    '<div class="wrow"><label for="fp-fmt">Format</label><select id="fp-fmt"><option value="fp32">FP32 single (1 + 8 + 23)</option><option value="fp16">FP16 half (1 + 5 + 10)</option><option value="bf16">BF16 bfloat16 (1 + 8 + 7)</option></select>' +
    '<label for="fp-in">Decimal value</label><input type="text" id="fp-in" value="-6.75" size="16" spellcheck="false" autocomplete="off"></div>' +
    '<p class="wnote">Type a number (or inf, -inf, nan), or click the bits. Orange border: sign. Cardinal: exponent. Gold: fraction.</p>' +
    '<div class="bits" id="fp-bits"></div><div class="wout" id="fp-out" aria-live="polite"></div></div>';
  var sel = $("#fp-fmt", el), inp = $("#fp-in", el), bitBox = $("#fp-bits", el), out = $("#fp-out", el);
  function roundEven(v) { var r = Math.floor(v), d = v - r; if (d > 0.5 || (d === 0.5 && r % 2 === 1)) r += 1; return r; }
  function encode(x, E, F) {
    var bias = Math.pow(2, E - 1) - 1, emax = Math.pow(2, E) - 1;
    var s = (x < 0 || (x === 0 && 1 / x < 0)) ? 1 : 0, a = Math.abs(x), e = 0, f = 0;
    if (isNaN(x)) return { s: 0, e: emax, f: Math.pow(2, F - 1) };
    if (a === Infinity) return { s: s, e: emax, f: 0 };
    if (a === 0) return { s: s, e: 0, f: 0 };
    var ex = Math.floor(Math.log2(a));
    while (Math.pow(2, ex) > a) ex--;
    while (Math.pow(2, ex + 1) <= a) ex++;
    if (ex < 1 - bias) {
      f = roundEven(a / Math.pow(2, 1 - bias - F));
      if (f >= Math.pow(2, F)) return { s: s, e: 1, f: 0 };
      return { s: s, e: 0, f: f };
    }
    f = roundEven((a / Math.pow(2, ex) - 1) * Math.pow(2, F));
    if (f >= Math.pow(2, F)) { f = 0; ex++; }
    e = ex + bias;
    if (e >= emax) return { s: s, e: emax, f: 0 };
    return { s: s, e: e, f: f };
  }
  function fieldsFromBits() {
    var o = FMT[fmt], s = bits[0], e = 0, f = 0;
    for (var i = 1; i <= o.e; i++) e = e * 2 + bits[i];
    for (var j = o.e + 1; j <= o.e + o.f; j++) f = f * 2 + bits[j];
    return { s: s, e: e, f: f };
  }
  function setBits(fl) {
    var o = FMT[fmt]; bits = [fl.s];
    for (var i = o.e - 1; i >= 0; i--) bits.push(Math.floor(fl.e / Math.pow(2, i)) % 2);
    for (var j = o.f - 1; j >= 0; j--) bits.push(Math.floor(fl.f / Math.pow(2, j)) % 2);
  }
  function exactDec(s, M, k) {
    // value = M * 2^k, M a non-negative BigInt
    var str;
    if (M === 0n) str = "0";
    else if (k >= 0) str = (M << BigInt(k)).toString();
    else {
      var digs = (M * (5n ** BigInt(-k))).toString();
      var p = -k;
      if (digs.length <= p) digs = "0".repeat(p - digs.length + 1) + digs;
      str = digs.slice(0, digs.length - p) + "." + digs.slice(digs.length - p);
      str = str.replace(/0+$/, "").replace(/\.$/, "");
    }
    return (s ? "−" : "") + str;
  }
  function draw() {
    var o = FMT[fmt], bias = Math.pow(2, o.e - 1) - 1, emax = Math.pow(2, o.e) - 1;
    var h = "";
    bits.forEach(function (b, i) {
      var grp = i === 0 ? "orange" : i <= o.e ? "cardinal" : "gold-deep";
      if (i === 1 || i === o.e + 1) h += '<span class="gap"></span>';
      h += '<button type="button" class="bit" data-i="' + i + '" aria-pressed="' + (b ? "true" : "false") + '" style="min-width:1.75em;height:2.1em;font-size:.82rem;border-color:var(--' + grp + ')" aria-label="bit ' + (bits.length - 1 - i) + '">' + b + "</button>";
    });
    bitBox.innerHTML = h;
    $$("button", bitBox).forEach(function (btn) { btn.addEventListener("click", function () { var i = +btn.getAttribute("data-i"); bits[i] ^= 1; inp.value = ""; draw(); }); });
    var fl = fieldsFromBits(), val, cls, formula, M, k;
    if (fl.e === emax) { val = fl.f ? NaN : (fl.s ? -Infinity : Infinity); cls = fl.f ? "NaN (not a number)" : "infinity"; formula = fl.f ? "exponent all ones, fraction ≠ 0" : "exponent all ones, fraction = 0"; }
    else if (fl.e === 0) {
      M = BigInt(fl.f); k = 1 - bias - o.f;
      val = (fl.s ? -1 : 1) * fl.f * Math.pow(2, k);
      cls = fl.f ? "subnormal (no hidden 1)" : "zero";
      formula = fl.f ? "(−1)" + supNum(fl.s) + " × 0." + bits.slice(o.e + 1).join("").replace(/0+$/, "") + "₂ × 2" + supNum(1 - bias) : (fl.s ? "−0" : "+0");
    } else {
      M = BigInt(fl.f) + (1n << BigInt(o.f)); k = fl.e - bias - o.f;
      val = (fl.s ? -1 : 1) * Number(M) * Math.pow(2, k);
      cls = "normal";
      var fr = bits.slice(o.e + 1).join("").replace(/0+$/, "");
      formula = "(−1)" + supNum(fl.s) + " × 1." + (fr || "0") + "₂ × 2" + supNum(fl.e) + "⁻" + supNum(bias) + " = " + (fl.s ? "−" : "") + "1." + (fr || "0") + "₂ × 2" + supNum(fl.e - bias);
    }
    var hex = 0n; bits.forEach(function (b) { hex = hex * 2n + BigInt(b); });
    var hexStr = "0x" + hex.toString(16).toUpperCase().padStart(bits.length / 4, "0");
    var exact = (M !== undefined) ? exactDec(fl.s, M, k) : String(val);
    var ulp = "";
    if (fl.e !== emax) {
      var ue = (fl.e === 0 ? 1 - bias : fl.e - bias) - o.f;
      ulp = "2" + supNum(ue) + " ≈ " + fmtNum(Math.pow(2, ue), 4);
    }
    var typed = parseFloat(inp.value);
    var errLine = "";
    if (inp.value && isFinite(typed) && isFinite(val) && typed !== val) errLine = "<dt>Rounding error</dt><dd>stored − typed = " + fmtNum(val - typed, 4) + " (relative " + fmtNum(Math.abs((val - typed) / typed), 3) + ")</dd>";
    out.innerHTML = '<dl class="kv"><dt>Bit pattern</dt><dd>' + hexStr + "</dd><dt>Fields</dt><dd>sign " + fl.s + ", exponent " + bits.slice(1, o.e + 1).join("") + " = " + fl.e + ", fraction " + bits.slice(o.e + 1).join("") + "</dd>" +
      "<dt>Class</dt><dd>" + cls + "</dd><dt>Formula</dt><dd>" + esc(formula) + "</dd><dt>Value stored</dt><dd>" + esc(exact) + "</dd>" + errLine +
      (ulp ? "<dt>Gap to the next value (1 ulp)</dt><dd>" + ulp + "</dd>" : "") + "</dl>" +
      '<p class="wnote">' + o.name + ": bias " + bias + ", " + o.f + " stored fraction bits plus the hidden 1, so about " + (Math.log10(Math.pow(2, o.f + 1))).toFixed(1) + " significant decimal digits; largest finite value ≈ " + fmtNum((2 - Math.pow(2, -o.f)) * Math.pow(2, emax - 1 - bias), 4) + ".</p>";
  }
  function fromInput() {
    var t = inp.value.trim().toLowerCase(), x;
    if (t === "") return;
    if (t === "inf" || t === "+inf" || t === "infinity") x = Infinity;
    else if (t === "-inf" || t === "−inf") x = -Infinity;
    else if (t === "nan") x = NaN;
    else { x = Number(t.replace("−", "-")); if (isNaN(x)) { out.innerHTML = '<p class="werr">Type a decimal number such as 0.1, -6.75 or 1e-8.</p>'; return; } }
    var o = FMT[fmt]; setBits(encode(x, o.e, o.f)); draw();
  }
  sel.addEventListener("change", function () { fmt = sel.value; if (inp.value.trim() === "") inp.value = "0.1"; fromInput(); });
  inp.addEventListener("input", fromInput);
  fromInput();
};

/* ================= RC filter explorer ================= */
TOOLS.rcfilter = function (el) {
  el.innerHTML = toolHead("RC filter explorer", "first-order low-pass and high-pass") + '<div class="wbody">' +
    '<div class="wrow"><label for="rc-t">Filter</label><select id="rc-t"><option value="lp">low-pass (output across C)</option><option value="hp">high-pass (output across R)</option></select>' +
    '<label for="rc-r">R</label><input type="text" id="rc-r" value="10k" size="7" spellcheck="false"><span class="wlab">Ω</span>' +
    '<label for="rc-c">C</label><input type="text" id="rc-c" value="100n" size="7" spellcheck="false"><span class="wlab">F</span></div>' +
    '<div class="wrow"><label for="rc-f">Input frequency</label><input type="range" id="rc-f" min="-200" max="200" value="0" step="1"><span class="m" id="rc-fv"></span></div>' +
    '<div class="wout" id="rc-out" aria-live="polite"></div></div>';
  var tsel = $("#rc-t", el), rin = $("#rc-r", el), cin = $("#rc-c", el), fr = $("#rc-f", el), fv = $("#rc-fv", el), out = $("#rc-out", el);
  function run() {
    var R = parseSI(rin.value), C = parseSI(cin.value), lp = tsel.value === "lp";
    if (!(R > 0) || !(C > 0)) { out.innerHTML = '<p class="werr">Give R and C as positive values, for example 4.7k and 22n.</p>'; fv.textContent = ""; return; }
    var tau = R * C, fc = 1 / (2 * Math.PI * tau), ratio = Math.pow(10, +fr.value / 100), f = fc * ratio;
    fv.textContent = siFmt(f, "Hz", 3) + " (" + fmtNum(ratio, 3) + " × fc)";
    function mag(x) { return lp ? 1 / Math.sqrt(1 + x * x) : x / Math.sqrt(1 + x * x); }
    var g = mag(ratio), db = 20 * Math.log10(g), ph = lp ? -Math.atan(ratio) * 180 / Math.PI : 90 - Math.atan(ratio) * 180 / Math.PI;
    var pts = [];
    for (var i = -300; i <= 300; i += 4) { var x = Math.pow(10, i / 100); pts.push([fc * x, 20 * Math.log10(mag(x))]); }
    var xt = [];
    for (var d = -3; d <= 3; d++) xt.push([fc * Math.pow(10, d), d === 0 ? "fc" : (d > 0 ? "10^" + d : "10^" + d) + "·fc"]);
    var bode = plotSVG({ w: 380, h: 230, x0: fc / 1000, x1: fc * 1000, y0: -60, y1: 5, logx: true, xt: xt, yt: [[0, "0 dB"], [-20, "−20"], [-40, "−40"], [-60, "−60"]],
      series: [{ pts: pts, cls: "l1" }], hlines: [[-3.01, "l3"]], vlines: [[fc, "l3"]], marks: [{ x: f, y: db, label: fmtNum(db, 3) + " dB", dx: lp ? 8 : -8, anchor: lp ? "start" : "end" }],
      xl: "frequency (log scale)", alt: "Magnitude response in decibels" });
    var sp = [];
    for (var t = 0; t <= 5.0001; t += 0.05) sp.push([t, lp ? 1 - Math.exp(-t) : Math.exp(-t)]);
    var step = plotSVG({ w: 380, h: 230, x0: 0, x1: 5, y0: 0, y1: 1.05, xt: [[0, "0"], [1, "τ"], [2, "2τ"], [3, "3τ"], [4, "4τ"], [5, "5τ"]], yt: [[0, "0"], [0.5, "0.5"], [1, "1"]],
      series: [{ pts: sp, cls: "l2" }], marks: [{ x: 1, y: lp ? 1 - Math.exp(-1) : Math.exp(-1), label: lp ? "63.2% at t = τ" : "36.8% at t = τ" }], xl: "time after a 0 → 1 input step", alt: "Step response" });
    out.innerHTML = '<dl class="kv"><dt>Time constant τ = RC</dt><dd>' + siFmt(tau, "s") + '</dd><dt>Cutoff fc = 1/(2πRC)</dt><dd>' + siFmt(fc, "Hz") +
      "</dd><dt>Gain at the input frequency</dt><dd>|H| = " + fmtNum(g, 4) + " = " + fmtNum(db, 3) + " dB, phase " + fmtNum(ph, 3) + "°</dd></dl>" +
      '<div class="cards" style="margin:4px 0 0"><div>' + bode + '</div><div>' + step + "</div></div>" +
      '<p class="wnote">' + (lp ? "Well above fc the low-pass output falls 20 dB per decade (a factor of 10 in amplitude for each factor of 10 in frequency)." : "Well below fc the high-pass output falls 20 dB per decade; above fc the signal passes almost unchanged.") + " At fc the gain is 1/√2 (−3 dB) and the phase is " + (lp ? "−45°" : "+45°") + ".</p>";
  }
  [tsel, rin, cin, fr].forEach(function (x) { x.addEventListener("input", run); x.addEventListener("change", run); });
  run();
};

/* ================= CMOS switch-level explorer ================= */
TOOLS.cmos = function (el) {
  var inputs = { A: 1, B: 0, C: 0 };
  var GATES = {
    inv: { name: "Inverter", expr: "Y = A′", ins: ["A"], w: 300, h: 290, count: 2,
      tr: [{ t: "p", x: 150, y: 86, in: "A" }, { t: "n", x: 150, y: 214, in: "A" }],
      pun: function (p) { return p[0]; }, pdn: function (p) { return p[1]; },
      rails: { vdd: [110, 226, 24], gnd: [166, 262] },
      wires: [[[166, 24], [166, 60]], [[166, 112], [166, 188]], [[166, 240], [166, 262]]], out: [166, 150, 240] },
    nand: { name: "NAND2", expr: "Y = (A·B)′", ins: ["A", "B"], w: 384, h: 344, count: 4,
      tr: [{ t: "p", x: 100, y: 84, in: "A" }, { t: "p", x: 250, y: 84, in: "B" }, { t: "n", x: 175, y: 194, in: "A" }, { t: "n", x: 175, y: 272, in: "B" }],
      pun: function (p) { return p[0] || p[1]; }, pdn: function (p) { return p[2] && p[3]; },
      rails: { vdd: [70, 296, 24], gnd: [191, 318] },
      wires: [[[116, 24], [116, 58]], [[266, 24], [266, 58]], [[116, 110], [116, 140], [266, 140], [266, 110]], [[191, 140], [191, 168]], [[191, 220], [191, 246]], [[191, 298], [191, 318]]], out: [266, 140, 330] },
    nor: { name: "NOR2", expr: "Y = (A + B)′", ins: ["A", "B"], w: 384, h: 346, count: 4,
      tr: [{ t: "p", x: 175, y: 80, in: "A" }, { t: "p", x: 175, y: 158, in: "B" }, { t: "n", x: 100, y: 262, in: "A" }, { t: "n", x: 250, y: 262, in: "B" }],
      pun: function (p) { return p[0] && p[1]; }, pdn: function (p) { return p[2] || p[3]; },
      rails: { vdd: [130, 256, 24], gnd: [191, 316], gndbar: [116, 266] },
      wires: [[[191, 24], [191, 54]], [[191, 106], [191, 132]], [[191, 184], [191, 210]], [[116, 236], [116, 210], [266, 210], [266, 236]], [[116, 288], [116, 316], [266, 316], [266, 288]]], out: [266, 210, 330] },
    aoi: { name: "AOI21", expr: "Y = (A·B + C)′", ins: ["A", "B", "C"], w: 400, h: 414, count: 6,
      tr: [{ t: "p", x: 100, y: 80, in: "A" }, { t: "p", x: 250, y: 80, in: "B" }, { t: "p", x: 175, y: 176, in: "C" }, { t: "n", x: 100, y: 270, in: "A" }, { t: "n", x: 100, y: 340, in: "B" }, { t: "n", x: 250, y: 305, in: "C" }],
      pun: function (p) { return (p[0] || p[1]) && p[2]; }, pdn: function (p) { return (p[3] && p[4]) || p[5]; },
      rails: { vdd: [70, 296, 24], gnd: [191, 386], gndbar: [116, 266] },
      wires: [[[116, 24], [116, 54]], [[266, 24], [266, 54]], [[116, 106], [116, 130], [266, 130], [266, 106]], [[191, 130], [191, 150]], [[191, 202], [191, 226]], [[116, 244], [116, 226], [266, 226], [266, 279]], [[116, 296], [116, 314]], [[116, 366], [116, 386], [266, 386], [266, 331]]], out: [191, 226, 340] }
  };
  var g = "nand";
  el.innerHTML = toolHead("CMOS switch-level explorer", "which transistors conduct") + '<div class="wbody">' +
    '<div class="wrow"><label for="cm-g">Gate</label><select id="cm-g"><option value="inv">Inverter</option><option value="nand" selected>NAND2</option><option value="nor">NOR2</option><option value="aoi">AOI21: (A·B + C)′</option></select><span class="wlab">Inputs</span><span id="cm-ins" class="bits"></span></div>' +
    '<div id="cm-svg" class="ws" style="overflow-x:auto"></div><div class="wout" id="cm-out" aria-live="polite"></div></div>';
  var gsel = $("#cm-g", el), insBox = $("#cm-ins", el), svgBox = $("#cm-svg", el), out = $("#cm-out", el);
  function trSVG(T, on) {
    var x = T.x, y = T.y, s = '<g class="' + (on ? "on" : "") + '">';
    s += '<path class="w" d="M' + (x - 6) + " " + (y - 13) + " V" + (y + 13) + " M" + x + " " + (y - 16) + " V" + (y + 16) + " M" + x + " " + (y - 11) + " H" + (x + 16) + " V" + (y - 26) + " M" + x + " " + (y + 11) + " H" + (x + 16) + " V" + (y + 26) + '"/>';
    if (T.t === "p") s += '<path class="w" d="M' + (x - 34) + " " + y + " H" + (x - 15) + '"/><circle class="b" cx="' + (x - 10.5) + '" cy="' + y + '" r="4.5"/>';
    else s += '<path class="w" d="M' + (x - 34) + " " + y + " H" + (x - 6) + '"/>';
    s += '<text x="' + (x - 40) + '" y="' + (y + 5) + '" text-anchor="end" style="font-weight:600">' + T.in + "</text>";
    s += '<text class="' + (on ? "tx-on" : "tx-off") + '" x="' + (x + 24) + '" y="' + (y + 4) + '">' + (T.t === "p" ? "PMOS" : "NMOS") + (on ? " on" : " off") + "</text>";
    return s + "</g>";
  }
  function draw() {
    var G = GATES[g];
    insBox.innerHTML = G.ins.map(function (k) { return '<button type="button" class="bit" data-k="' + k + '" aria-pressed="' + (inputs[k] ? "true" : "false") + '">' + k + " = " + inputs[k] + "</button>"; }).join("");
    $$("button", insBox).forEach(function (b) { b.addEventListener("click", function () { var k = b.getAttribute("data-k"); inputs[k] ^= 1; draw(); }); });
    var on = G.tr.map(function (T) { return T.t === "n" ? inputs[T.in] === 1 : inputs[T.in] === 0; });
    var up = !!G.pun(on), dn = !!G.pdn(on);
    var s = '<svg class="cmos-svg" viewBox="0 0 ' + G.w + " " + G.h + '" width="' + G.w + '" role="img" aria-label="' + G.name + ' transistor schematic">';
    var v = G.rails.vdd;
    s += '<path class="w' + (up ? " on" : "") + '" d="M' + v[0] + " " + v[2] + " H" + v[1] + '"/><text x="' + (v[1] + 6) + '" y="' + (v[2] + 4) + '">V<tspan baseline-shift="sub" font-size="10">DD</tspan> = 1</text>';
    var gd = G.rails.gnd;
    if (G.rails.gndbar) s += '<path class="w' + (dn ? " on" : "") + '" d="M' + G.rails.gndbar[0] + " " + gd[1] + " H" + G.rails.gndbar[1] + '"/>';
    s += '<path class="w' + (dn ? " on" : "") + '" d="M' + gd[0] + " " + gd[1] + " V" + (gd[1] + 10) + " M" + (gd[0] - 14) + " " + (gd[1] + 10) + " H" + (gd[0] + 14) + " M" + (gd[0] - 9) + " " + (gd[1] + 16) + " H" + (gd[0] + 9) + " M" + (gd[0] - 4) + " " + (gd[1] + 22) + " H" + (gd[0] + 4) + '"/>' +
      '<text x="' + (gd[0] + 22) + '" y="' + (gd[1] + 20) + '">GND = 0</text>';
    G.wires.forEach(function (wl) { s += '<path class="w" d="' + wl.map(function (p, k) { return (k ? "L" : "M") + p[0] + " " + p[1]; }).join(" ") + '"/>'; });
    G.tr.forEach(function (T, k) { s += trSVG(T, on[k]); });
    var o = G.out, yv = up && !dn ? 1 : dn && !up ? 0 : null;
    s += '<circle class="dot" cx="' + o[0] + '" cy="' + o[1] + '" r="3.5"/><path class="w' + (yv === 1 ? " on" : "") + '" d="M' + o[0] + " " + o[1] + " H" + o[2] + '"/><text x="' + (o[2] + 6) + '" y="' + (o[1] + 5) + '" style="font-weight:600">Y = ' + (yv == null ? "?" : yv) + "</text>";
    s += "</svg>";
    svgBox.innerHTML = s;
    var msg;
    if (up && !dn) msg = "The pull-up network (PMOS) conducts and the pull-down network (NMOS) is open, so the output is connected to V<sub>DD</sub>: <b>Y = 1</b>.";
    else if (dn && !up) msg = "The pull-down network (NMOS) conducts and the pull-up network (PMOS) is open, so the output is connected to ground: <b>Y = 0</b>.";
    else msg = "Both or neither network conducts. A correct static CMOS gate never does this; check the networks are duals.";
    out.innerHTML = "<p>" + G.name + ", " + G.expr + ", " + G.count + " transistors. " + msg + " Exactly one network conducts for every input combination, so no steady current flows from V<sub>DD</sub> to ground.</p>";
  }
  gsel.addEventListener("change", function () { g = gsel.value; draw(); });
  draw();
};

/* ================= latch vs flip-flop lab ================= */
TOOLS.latchlab = function (el) {
  var N = 24, D = "001101100011100110011100".split("").map(Number);
  el.innerHTML = toolHead("Latch vs flip-flop lab", "edit D and compare the two outputs") + '<div class="wbody">' +
    '<div class="wrow"><label for="ll-l">Latch is transparent while</label><select id="ll-l"><option value="1">CLK = 1</option><option value="0">CLK = 0</option></select>' +
    '<label for="ll-f">Flip-flop samples on the</label><select id="ll-f"><option value="r">rising edge</option><option value="f">falling edge</option></select></div>' +
    '<div class="wrow"><label for="ll-d">D in each of the ' + N + ' time slots</label><input type="text" id="ll-d" size="30" spellcheck="false" autocomplete="off"></div>' +
    '<p class="wnote">Click a slot in the D row, or edit the string. Shaded columns are where the latch is transparent; dashed lines are the flip-flop\'s sampling edges.</p>' +
    '<div id="ll-w" class="ws" style="overflow-x:auto"></div><div class="wout" id="ll-out" aria-live="polite"></div></div>';
  var lsel = $("#ll-l", el), fsel = $("#ll-f", el), din = $("#ll-d", el), wbox = $("#ll-w", el), out = $("#ll-out", el);
  function clk(i) { return Math.floor(i / 3) % 2; }
  function draw() {
    din.value = D.join("");
    var lat = [], ff = [], ql = 0, qf = 0, en = +lsel.value, rising = fsel.value === "r", edges = [];
    for (var i = 0; i < N; i++) {
      if (i > 0 && ((rising && clk(i) === 1 && clk(i - 1) === 0) || (!rising && clk(i) === 0 && clk(i - 1) === 1))) { qf = D[i - 1]; edges.push(i); }
      ff.push(qf);
      if (clk(i) === en) ql = D[i];
      lat.push(ql);
    }
    var W = 760, LW = 120, sw = (W - LW - 12) / N, RH = 42, top = 14, H = top + 4 * RH + 10;
    function X(i) { return LW + i * sw; }
    var s = '<svg viewBox="0 0 ' + W + " " + H + '" width="' + W + '" style="min-width:560px;width:100%;height:auto;display:block" role="img" aria-label="Clock, D, latch output and flip-flop output">';
    for (var k = 0; k < N; k++) if (clk(k) === en) s += '<rect x="' + X(k) + '" y="' + (top - 4) + '" width="' + sw + '" height="' + (4 * RH) + '" style="fill:var(--gold-soft)"/>';
    edges.forEach(function (e) { s += '<line x1="' + X(e) + '" y1="' + (top - 4) + '" x2="' + X(e) + '" y2="' + (top + 4 * RH) + '" style="stroke:var(--cardinal);stroke-width:1.4;stroke-dasharray:5 3"/>'; });
    function row(r, name, arr, color) {
      var y0 = top + r * RH, hi = y0 + 8, lo = y0 + 30, d = "";
      arr.forEach(function (v, i) { var y = v ? hi : lo; d += (i ? " V" + y : "M" + X(0) + " " + y) + " H" + X(i + 1); });
      return '<text x="10" y="' + (y0 + 23) + '" style="font:500 12.5px var(--font-mono);fill:var(--ink)">' + name + '</text><path d="' + d + '" style="fill:none;stroke:' + color + ';stroke-width:2.2;stroke-linejoin:round"/>';
    }
    var C = []; for (var j = 0; j < N; j++) C.push(clk(j));
    s += row(0, "CLK", C, "var(--ink)") + row(1, "D (click)", D, "var(--ch2)") + row(2, "Q latch", lat, "var(--ch1)") + row(3, "Q flip-flop", ff, "var(--ch3)");
    for (var m = 0; m < N; m++) s += '<rect class="ll-hit" data-i="' + m + '" x="' + X(m) + '" y="' + (top + RH) + '" width="' + sw + '" height="' + RH + '" style="fill:transparent;cursor:pointer"><title>slot ' + m + "</title></rect>";
    s += "</svg>";
    wbox.innerHTML = s;
    $$(".ll-hit", wbox).forEach(function (r) { r.addEventListener("click", function () { var i = +r.getAttribute("data-i"); D[i] ^= 1; draw(); }); });
    var latCh = 0, ffCh = 0;
    for (var t = 1; t < N; t++) { if (lat[t] !== lat[t - 1]) latCh++; if (ff[t] !== ff[t - 1]) ffCh++; }
    out.innerHTML = "<p>The latch output changed " + latCh + " times and the flip-flop output " + ffCh + " times. The latch copies every change of D while it is transparent, including short pulses. The flip-flop only looks at D at " + edges.length + " sampling edges, so its output can change at most once per clock period.</p>";
  }
  din.addEventListener("input", function () {
    var v = din.value.replace(/[^01]/g, "");
    if (v.length) { for (var i = 0; i < N; i++) D[i] = i < v.length ? +v[i] : D[i]; }
    var pos = din.selectionStart; draw(); try { din.setSelectionRange(pos, pos); } catch (e) { }
  });
  lsel.addEventListener("change", draw); fsel.addEventListener("change", draw);
  draw();
};

/* ================= sequence detector generator ================= */
TOOLS.fsmgen = function (el) {
  el.innerHTML = toolHead("Sequence detector generator", "builds the state table for any bit pattern") + '<div class="wbody">' +
    '<div class="wrow"><label for="sd-p">Pattern</label><input type="text" id="sd-p" value="1011" size="8" spellcheck="false" autocomplete="off">' +
    '<label for="sd-t">Machine</label><select id="sd-t"><option value="moore">Moore (output in the state)</option><option value="mealy">Mealy (output on the arc)</option></select>' +
    '<label class="chk"><input type="checkbox" id="sd-o" checked> Overlapping matches count</label></div>' +
    '<div class="wrow"><label for="sd-in">Input stream</label><input type="text" id="sd-in" value="1101101110110" size="26" spellcheck="false" autocomplete="off"></div>' +
    '<div class="wout" id="sd-out" aria-live="polite"></div></div>';
  var pin = $("#sd-p", el), tsel = $("#sd-t", el), ov = $("#sd-o", el), sin = $("#sd-in", el), out = $("#sd-out", el);
  function longest(str, P) { for (var j = Math.min(P.length, str.length); j >= 0; j--) if (str.slice(str.length - j) === P.slice(0, j)) return j; return 0; }
  function run() {
    var P = pin.value.replace(/\s/g, ""), stream = sin.value.replace(/\s/g, ""), moore = tsel.value === "moore", overlap = ov.checked;
    if (!/^[01]{1,8}$/.test(P)) { out.innerHTML = '<p class="werr">The pattern must be 1 to 8 bits of 0 and 1.</p>'; return; }
    if (!/^[01]{0,48}$/.test(stream)) { out.innerHTML = '<p class="werr">The input stream must be up to 48 bits of 0 and 1.</p>'; return; }
    var k = P.length, nS = moore ? k + 1 : k, delta = [], outp = [];
    for (var i = 0; i < nS; i++) {
      delta.push([]); outp.push([]);
      for (var b = 0; b < 2; b++) {
        var bit = String(b), j;
        if (moore) {
          if (i < k) j = longest(P.slice(0, i) + bit, P);
          else j = overlap ? longest(P + bit, P) : longest(bit, P);
          delta[i][b] = j; outp[i][b] = 0;
        } else {
          j = longest(P.slice(0, i) + bit, P);
          if (j === k) { outp[i][b] = 1; delta[i][b] = overlap ? longest(P.slice(1), P) : 0; }
          else { outp[i][b] = 0; delta[i][b] = j; }
        }
      }
    }
    function nm(i) { return "S" + i; }
    function meaning(i) { return i === 0 ? "no useful prefix yet" : (moore && i === k ? "just saw " + P + " (match)" : "last bits were " + P.slice(0, i)); }
    var t = '<div class="tbl tt" style="margin:0"><table><thead><tr><th>state</th><th style="text-align:left">remembers</th><th>next if x = 0</th><th>next if x = 1</th>' + (moore ? '<th class="o">z</th>' : '<th class="o">z if x = 0</th><th class="o">z if x = 1</th>') + "</tr></thead><tbody>";
    for (var s2 = 0; s2 < nS; s2++) {
      t += "<tr><td>" + nm(s2) + '</td><td style="text-align:left;font-family:var(--font-display)">' + esc(meaning(s2)) + "</td><td>" + nm(delta[s2][0]) + "</td><td>" + nm(delta[s2][1]) + "</td>" +
        (moore ? '<td class="o' + (s2 === k ? " v1" : "") + '">' + (s2 === k ? 1 : 0) + "</td>" : '<td class="o' + (outp[s2][0] ? " v1" : "") + '">' + outp[s2][0] + '</td><td class="o' + (outp[s2][1] ? " v1" : "") + '">' + outp[s2][1] + "</td>") + "</tr>";
    }
    t += "</tbody></table></div>";
    var st = 0, rows = "", hits = 0;
    for (var c = 0; c < stream.length; c++) {
      var x = +stream[c], ns = delta[st][x], z = moore ? (ns === k ? 1 : 0) : outp[st][x];
      hits += z;
      rows += "<tr><td>" + (c + 1) + "</td><td>" + nm(st) + "</td><td>" + x + "</td><td>" + nm(ns) + '</td><td class="o' + (z ? " v1" : "") + '">' + z + "</td></tr>";
      st = ns;
    }
    var bin = Math.max(1, Math.ceil(Math.log2(nS)));
    out.innerHTML = "<p>" + nS + " states: " + bin + " flip-flop" + (bin > 1 ? "s" : "") + " with binary encoding, or " + nS + " with one-hot encoding.</p>" + t +
      (stream.length ? '<p>Trace (the machine starts in S0; ' + (moore ? "z is the Moore output after each clock edge" : "z is the Mealy output while each bit is on the input") + "):</p>" +
        '<div class="tbl tt" style="margin:0"><table><thead><tr><th>clock</th><th>state</th><th>x</th><th>next</th><th class="o">z</th></tr></thead><tbody>' + rows + "</tbody></table></div><p><b>" + hits + " match" + (hits === 1 ? "" : "es") + "</b> found.</p>" : "");
  }
  [pin, tsel, ov, sin].forEach(function (x) { x.addEventListener("input", run); x.addEventListener("change", run); });
  run();
};

/* ================= setup / hold slack calculator ================= */
TOOLS.timing = function (el) {
  var F = [["tcq", "clock-to-Q, max", 60], ["tcqmin", "clock-to-Q, min", 40], ["tpd", "logic delay, max (critical path)", 700], ["tcd", "logic delay, min (shortest path)", 30],
    ["tsu", "setup time", 50], ["th", "hold time", 45], ["T", "clock period", 850], ["sk", "clock skew (capture clock minus launch clock)", 0]];
  el.innerHTML = toolHead("Setup and hold slack calculator", "all times in picoseconds") + '<div class="wbody">' +
    '<div class="cards" style="margin:0">' + F.map(function (f) { return '<div style="padding:8px 10px"><label class="wlab" for="tm-' + f[0] + '" style="display:block">' + f[1] + '</label><input type="number" id="tm-' + f[0] + '" value="' + f[2] + '" step="5"></div>'; }).join("") + "</div>" +
    '<div class="wout" id="tm-out" aria-live="polite"></div></div>';
  var out = $("#tm-out", el), v = {};
  function bar(parts, total) {
    var h = '<div style="display:flex;height:26px;border:1px solid var(--rule-2);border-radius:5px;overflow:hidden;max-width:620px">';
    parts.forEach(function (p) { if (p[1] > 0) h += '<div title="' + esc(p[0]) + '" style="flex:' + p[1] + ";background:" + p[2] + ';display:grid;place-items:center;font:600 .72rem var(--font-mono);color:var(--ink);min-width:0;overflow:hidden;white-space:nowrap">' + esc(p[0]) + "</div>"; });
    return h + "</div>";
  }
  function run() {
    F.forEach(function (f) { v[f[0]] = parseFloat($("#tm-" + f[0], el).value); });
    if (F.some(function (f) { return !isFinite(v[f[0]]); })) { out.innerHTML = '<p class="werr">Every field needs a number.</p>'; return; }
    var need = v.tcq + v.tpd + v.tsu, avail = v.T + v.sk;
    var setup = avail - need, hold = v.tcqmin + v.tcd - v.th - v.sk;
    var tmin = need - v.sk, fmax = tmin > 0 ? 1e12 / tmin : Infinity;
    var parts = [["clk→Q " + v.tcq, v.tcq, "var(--cardinal-soft)"], ["logic " + v.tpd, v.tpd, "var(--gold-soft)"], ["setup " + v.tsu, v.tsu, "var(--orange-soft)"]];
    if (setup >= 0) parts.push(["slack " + Math.round(setup), setup, "var(--green-soft)"]);
    out.innerHTML = '<dl class="kv"><dt>Setup slack</dt><dd>(T + skew) − (t<sub>cq</sub> + t<sub>pd</sub> + t<sub>su</sub>) = ' + avail + " − " + need + " = <b>" + fmtNum(setup, 6) + " ps</b> " +
      '<span class="tag ' + (setup >= 0 ? "hit" : "miss") + '">' + (setup >= 0 ? "met" : "violated") + "</span></dd>" +
      "<dt>Hold slack</dt><dd>(t<sub>cq,min</sub> + t<sub>cd</sub>) − (t<sub>h</sub> + skew) = " + (v.tcqmin + v.tcd) + " − " + (v.th + v.sk) + " = <b>" + fmtNum(hold, 6) + " ps</b> " +
      '<span class="tag ' + (hold >= 0 ? "hit" : "miss") + '">' + (hold >= 0 ? "met" : "violated") + "</span></dd>" +
      "<dt>Fastest clock that meets setup</dt><dd>T<sub>min</sub> = " + fmtNum(tmin, 6) + " ps, f<sub>max</sub> = " + (isFinite(fmax) ? siFmt(fmax, "Hz", 4) : "unbounded") + "</dd></dl>" +
      "<p class=\"wnote\">One clock period (plus skew) has to hold the launch flip-flop's delay, the slowest logic and the capture flip-flop's setup time:</p>" + bar(parts, avail) +
      '<p class="wnote">' + (setup < 0 ? "Setup fails: lengthen the period, shorten the critical path (fewer logic levels, faster cells, retiming or pipelining) or add useful skew. " : "") +
      (hold < 0 ? "Hold fails: the clock period does not appear in the hold check, so slowing the clock cannot fix it. Add delay (buffers) on the short path or reduce skew. " : "") +
      "Positive skew (capture clock later) helps setup by the same amount it hurts hold.</p>";
  }
  F.forEach(function (f) { $("#tm-" + f[0], el).addEventListener("input", run); });
  run();
};

/* ================= pipeline hazard visualizer ================= */
TOOLS.pipeline = function (el) {
  el.innerHTML = toolHead("Pipeline hazard visualizer", "classic 5-stage in-order pipeline") + '<div class="wbody">' +
    '<div class="wrow" style="align-items:flex-start"><div style="flex:1 1 260px;min-width:0"><label class="wlab" for="pl-code">Program (one instruction per line)</label><textarea id="pl-code" spellcheck="false" style="min-height:130px">lw   r1, 0(r2)\nadd  r3, r1, r4\nsub  r5, r3, r6\nsw   r5, 8(r2)\nand  r7, r8, r9</textarea></div>' +
    '<div style="flex:1 1 200px;min-width:0;display:grid;gap:6px"><label class="chk"><input type="checkbox" id="pl-fw" checked> Forwarding (bypassing)</label>' +
    '<p class="wnote">Supported: add, sub, and, or, xor, slt, addi, lw, sw, beq. Append "taken" to a beq to model a taken branch (resolved in EX, wrong-path fetches are flushed). The register file writes in the first half of a cycle and reads in the second.</p></div></div>' +
    '<div class="wout" id="pl-out" aria-live="polite"></div></div>';
  var code = $("#pl-code", el), fw = $("#pl-fw", el), out = $("#pl-out", el);
  function parse(line) {
    var L = line.replace(/[#;].*$/, "").trim();
    if (!L) return null;
    var m = L.toLowerCase().match(/^([a-z]+)\s+(.*)$/);
    if (!m) throw new Error('Can\'t read "' + line.trim() + '".');
    var op = m[1], a = m[2].split(",").map(function (x) { return x.trim(); });
    var reg = /^\$?[a-z]+\d*$/;
    function R(x) { if (!reg.test(x)) throw new Error('"' + x + '" in "' + line.trim() + '" is not a register.'); return x.replace("$", ""); }
    if (/^(add|sub|and|or|xor|slt|nor|mul)$/.test(op)) { if (a.length !== 3) throw new Error(op + " needs three registers."); return { op: op, d: R(a[0]), s: [R(a[1]), R(a[2])], k: "alu", txt: L }; }
    if (/^(addi|andi|ori|slti)$/.test(op)) { if (a.length !== 3) throw new Error(op + " needs two registers and a constant."); return { op: op, d: R(a[0]), s: [R(a[1])], k: "alu", txt: L }; }
    if (op === "lw" || op === "sw") {
      var mm = (a[1] || "").match(/^(-?\w*)\((\$?[a-z]+\d*)\)$/);
      if (a.length !== 2 || !mm) throw new Error(op + ' uses the form "' + op + ' r1, 8(r2)".');
      return op === "lw" ? { op: op, d: R(a[0]), s: [R(mm[2])], k: "load", txt: L } : { op: op, d: null, s: [R(mm[2]), R(a[0])], k: "store", txt: L };
    }
    if (op === "beq" || op === "bne") { if (a.length < 3) throw new Error(op + " needs two registers and a label."); return { op: op, d: null, s: [R(a[0]), R(a[1])], k: "branch", taken: /taken/.test(a[2]), txt: L }; }
    if (op === "nop") return { op: op, d: null, s: [], k: "alu", txt: L };
    throw new Error('Unknown instruction "' + op + '".');
  }
  function run() {
    var ins = [];
    try { code.value.split("\n").forEach(function (l) { var p = parse(l); if (p) ins.push(p); }); }
    catch (e) { out.innerHTML = '<p class="werr">' + esc(e.message) + "</p>"; return; }
    if (!ins.length) { out.innerHTML = '<p class="werr">Type at least one instruction.</p>'; return; }
    if (ins.length > 12) { out.innerHTML = '<p class="werr">Keep it to 12 instructions or fewer.</p>'; return; }
    var useFw = fw.checked, rec = [], notes = [], stalls = 0, flushes = 0, redirect = 0;
    ins.forEach(function (I, i) {
      var P0 = rec[i - 1];
      var IF = Math.max(P0 ? P0.IF + 1 : 1, redirect);          // fetch one per cycle unless a taken branch redirects
      var ID = Math.max(IF + 1, P0 ? P0.EX : 0);                 // enter ID once the previous instruction has left it
      var EX = Math.max(ID + 1, P0 ? P0.EX + 1 : 0), why = [], fwd = false;
      I.s.forEach(function (r) {
        if (r === "r0" || r === "x0" || r === "zero") return;
        for (var j = i - 1; j >= 0; j--) {
          var P = rec[j];
          if (P.I.d !== r) continue;
          var need = useFw ? (P.I.k === "load" ? P.MEM + 1 : P.EX + 1) : P.WB + 1;
          if (need > EX) { why.push(r + " from instruction " + (j + 1)); EX = need; }
          break;
        }
      });
      I.s.forEach(function (r) {
        for (var j = i - 1; j >= 0; j--) { var P = rec[j]; if (P.I.d !== r) continue; if (useFw && EX - 1 < P.WB) fwd = true; break; }
      });
      var st = EX - ID - 1;
      if (st > 0) { stalls += st; notes.push("Instruction " + (i + 1) + " waits " + st + " cycle" + (st > 1 ? "s" : "") + " in ID for " + why.join(" and ") + (useFw ? " (a load's data is only ready after MEM)." : " (without forwarding, a value can be read only in the cycle it is written back or later).")); }
      rec.push({ I: I, IF: IF, ID: ID, EX: EX, MEM: EX + 1, WB: EX + 2, fw: fwd });
      if (I.k === "branch" && I.taken) { redirect = EX + 1; flushes += 2; notes.push("Instruction " + (i + 1) + " is a taken branch resolved in EX. The two instructions fetched behind it are flushed (2 bubbles) and the next line is treated as the branch target."); }
    });
    var last = rec[rec.length - 1].WB;
    var head = "<tr><th>instruction</th>";
    for (var c = 1; c <= last; c++) head += "<th>" + c + "</th>";
    head += "</tr>";
    var body = rec.map(function (R, i) {
      var row = '<tr><td class="lbl">' + (i + 1) + ". " + esc(R.I.txt) + "</td>";
      for (var c2 = 1; c2 <= last; c2++) {
        var cell = "", cls = "";
        if (c2 >= R.IF && c2 < R.ID) { cell = "IF"; cls = c2 === R.IF ? "st" : "bub"; }
        else if (c2 >= R.ID && c2 < R.EX) { cell = "ID"; cls = c2 === R.ID ? "st" : "bub"; }
        else if (c2 === R.EX) { cell = "EX"; cls = R.fw ? "fw" : "st"; }
        else if (c2 === R.MEM) { cell = "MEM"; cls = "st"; }
        else if (c2 === R.WB) { cell = "WB"; cls = "st"; }
        row += '<td class="' + cls + '">' + cell + "</td>";
      }
      return row + "</tr>";
    }).join("");
    var n = rec.length, ideal = n + 4;
    out.innerHTML = '<div class="tbl" style="margin:0"><table class="pipe"><thead>' + head + "</thead><tbody>" + body + "</tbody></table></div>" +
      "<p><b>" + n + " instructions in " + last + " cycles</b> (ideal " + ideal + "). Stall cycles: " + stalls + (flushes ? ", flushed slots: " + flushes : "") + ". Gold EX cells receive at least one forwarded operand. Red cells repeat a stage because the instruction is held there by a stall.</p>" +
      (notes.length ? "<ul style=\"margin:0\">" + notes.map(function (t) { return "<li>" + esc(t) + "</li>"; }).join("") + "</ul>" : "<p>No hazards cause stalls in this program" + (useFw ? " with forwarding." : ".") + "</p>");
  }
  code.addEventListener("input", run); fw.addEventListener("change", run);
  run();
};

/* ================= Amdahl's law ================= */
TOOLS.amdahl = function (el) {
  el.innerHTML = toolHead("Amdahl's law", "speedup when only part of the work gets faster") + '<div class="wbody">' +
    '<div class="wrow"><label for="am-p">Parallel (or improved) fraction p</label><input type="range" id="am-p" min="0" max="100" value="90"><span class="m" id="am-pv"></span></div>' +
    '<div class="wrow"><label for="am-n">Processors (or speedup of that part) N</label><input type="range" id="am-n" min="0" max="12" value="4"><span class="m" id="am-nv"></span></div>' +
    '<div class="wout" id="am-out" aria-live="polite"></div></div>';
  var ps = $("#am-p", el), ns = $("#am-n", el), pv = $("#am-pv", el), nv = $("#am-nv", el), out = $("#am-out", el);
  function run() {
    var p = +ps.value / 100, N = Math.pow(2, +ns.value);
    pv.textContent = (+ps.value) + "%"; nv.textContent = String(N);
    var S = 1 / ((1 - p) + p / N), Smax = p < 1 ? 1 / (1 - p) : Infinity, G = (1 - p) + p * N;
    var pts = [];
    for (var k = 0; k <= 12; k += 0.25) { var n = Math.pow(2, k); pts.push([n, 1 / ((1 - p) + p / n)]); }
    var ymax = Math.min(64, Math.max(4, Math.ceil(Math.min(Smax, 4096) * 1.1)));
    var yt = []; var step = ymax <= 8 ? 1 : ymax <= 20 ? 2 : ymax <= 40 ? 5 : 10;
    for (var y = 0; y <= ymax; y += step) yt.push([y, String(y)]);
    var plot = plotSVG({ w: 520, h: 240, x0: 1, x1: 4096, y0: 0, y1: ymax, logx: true, xt: [[1, "1"], [4, "4"], [16, "16"], [64, "64"], [256, "256"], [1024, "1024"], [4096, "4096"]], yt: yt,
      series: [{ pts: pts, cls: "l1" }], hlines: isFinite(Smax) && Smax <= ymax ? [[Smax, "l3"]] : [], marks: [{ x: N, y: S, label: fmtNum(S, 3) + "×" }], xl: "N (log scale)", alt: "Speedup versus N" });
    out.innerHTML = '<dl class="kv"><dt>Speedup S = 1 / ((1 − p) + p/N)</dt><dd>' + fmtNum(S, 4) + "×</dd><dt>Limit as N → ∞</dt><dd>" + (isFinite(Smax) ? fmtNum(Smax, 4) + "×" : "unbounded") +
      "</dd><dt>Efficiency S / N</dt><dd>" + fmtNum(100 * S / N, 3) + "%</dd><dt>Gustafson scaled speedup</dt><dd>(1 − p) + p·N = " + fmtNum(G, 4) + "×</dd></dl>" + plot +
      '<p class="wnote">The dashed line is the ceiling 1/(1 − p): the serial part runs at the same speed no matter how large N gets. Gustafson\'s figure assumes the problem grows with N so the parallel part keeps every processor busy.</p>';
  }
  ps.addEventListener("input", run); ns.addEventListener("input", run);
  run();
};

/* ================= register bit-fiddling playground ================= */
TOOLS.bitfiddle = function (el) {
  var REGN = ["DDRB", "PORTB", "PINB", "DDRC", "PORTC", "PINC", "DDRD", "PORTD", "PIND"];
  var init = { DDRB: 0x00, PORTB: 0x00, PINB: 0x00, DDRC: 0x00, PORTC: 0x00, PINC: 0x34, DDRD: 0x00, PORTD: 0x00, PIND: 0xF7 };
  var regs = {}, vars = {}, intBits = 16;
  var PRESETS = [
    ["Set bit 3 of PORTB", "PORTB |= (1 << 3);"],
    ["Clear bit 3 of PORTB", "PORTB = 0xFF;\nPORTB &= ~(1 << 3);"],
    ["Toggle bits 0 and 1", "PORTB = 0x05;\nPORTB ^= (1 << 0) | (1 << 1);"],
    ["Make PB5 an output and turn it on", "DDRB |= (1 << 5);\nPORTB |= (1 << 5);"],
    ["Enable the pull-up on PC2 (input)", "DDRC &= ~(1 << 2);\nPORTC |= (1 << 2);"],
    ["Check bit 4 of PINC", "(PINC & (1 << 4)) != 0"],
    ["Bug: comparing a masked bit to 1", "(PINC & (1 << 4)) == 1"],
    ["Bug: precedence of == over &", "PIND & (1 << 3) == 0"],
    ["Bug: clearing with &= (1 << 3)", "PORTB = 0xFF;\nPORTB &= (1 << 3);"],
    ["Copy PORTC[7:5] into PORTB[5:3]", "PORTC = 0xA0;\nPORTB = 0xFF;\nPORTB &= ~0x38;\nPORTB |= (PORTC >> 2) & 0x38;"],
    ["Writing a 1 to PINB toggles PORTB", "PORTB = 0x01;\nPINB = (1 << 0);"]
  ];
  el.innerHTML = toolHead("Register bit-fiddling playground", "C statements on 8-bit AVR registers") + '<div class="wbody">' +
    '<div class="wrow"><label for="bf-pre">Example</label><select id="bf-pre">' + PRESETS.map(function (p, i) { return '<option value="' + i + '">' + esc(p[0]) + "</option>"; }).join("") + "</select>" +
    '<label for="bf-int">int is</label><select id="bf-int"><option value="16">16 bits (AVR)</option><option value="32">32 bits (PC)</option></select></div>' +
    '<textarea id="bf-code" spellcheck="false" style="min-height:84px"></textarea>' +
    '<div class="wrow"><button type="button" class="btn sm" id="bf-run">Run from reset</button><button type="button" class="btn sm ghost" id="bf-reset">Reset registers</button></div>' +
    '<div class="wout" id="bf-out" aria-live="polite"></div>' +
    '<p class="wnote">Registers start from the values shown after a reset of this simulator (PINC and PIND hold sample input levels; click their bits to change them). Statements use C syntax, including |=, &amp;=, ^=, ~, &lt;&lt;, &gt;&gt;, &amp;&amp;, ||, == and !=. Lowercase names become int variables.</p></div>';
  var pre = $("#bf-pre", el), codeEl = $("#bf-code", el), out = $("#bf-out", el), isel = $("#bf-int", el);
  function reset() { REGN.forEach(function (r) { regs[r] = init[r]; }); vars = {}; }
  function wrapInt(v) { var M = Math.pow(2, intBits); v = ((v % M) + M) % M; return v >= M / 2 ? v - M : v; }
  function tokenize(s) {
    var toks = [], re = /\s*(0[xX][0-9a-fA-F]+|0[bB][01]+|\d+)[uUlL]*|\s*([A-Za-z_]\w*)|\s*(<<=|>>=|\|=|&=|\^=|\+=|-=|==|!=|<=|>=|<<|>>|&&|\|\||[!~&|^+\-*\/%<>=()])|\s*(\S)/g, m;
    while ((m = re.exec(s))) {
      if (m[1] !== undefined) { var t = m[1]; toks.push({ t: "n", v: /^0[bB]/.test(t) ? parseInt(t.slice(2), 2) : Number(t) }); }
      else if (m[2] !== undefined) toks.push({ t: "id", v: m[2] });
      else if (m[3] !== undefined) toks.push({ t: "op", v: m[3] });
      else if (m[4] !== undefined) throw new Error('Unexpected character "' + m[4] + '".');
    }
    return toks;
  }
  var PREC = { "||": 1, "&&": 2, "|": 3, "^": 4, "&": 5, "==": 6, "!=": 6, "<": 7, ">": 7, "<=": 7, ">=": 7, "<<": 8, ">>": 8, "+": 9, "-": 9, "*": 10, "/": 10, "%": 10 };
  function evalStmt(src) {
    var toks = tokenize(src), i = 0;
    function peek() { return toks[i]; }
    function readVar(name) {
      if (REGN.indexOf(name) >= 0) return regs[name];
      if (/^[a-z_]\w*$/.test(name)) { if (!(name in vars)) throw new Error('"' + name + '" is used before it has a value.'); return vars[name]; }
      throw new Error('Unknown name "' + name + '". The registers here are ' + REGN.join(", ") + ".");
    }
    function primary() {
      var t = toks[i++];
      if (!t) throw new Error("The statement ends too early.");
      if (t.t === "n") return wrapInt(t.v);
      if (t.t === "id") return readVar(t.v);
      if (t.v === "(") { var v = expr(0); var c = toks[i++]; if (!c || c.v !== ")") throw new Error("A closing parenthesis is missing."); return v; }
      if (t.v === "~") return wrapInt(~primary());
      if (t.v === "!") return primary() ? 0 : 1;
      if (t.v === "-") return wrapInt(-primary());
      if (t.v === "+") return primary();
      throw new Error('Unexpected "' + t.v + '".');
    }
    function expr(minP) {
      var lhs = primary();
      for (;;) {
        var t = peek();
        if (!t || t.t !== "op" || !(t.v in PREC) || PREC[t.v] <= minP) break;
        i++;
        var rhs = expr(PREC[t.v]);
        lhs = apply(t.v, lhs, rhs);
      }
      return lhs;
    }
    function apply(op, a, b) {
      switch (op) {
        case "||": return (a || b) ? 1 : 0; case "&&": return (a && b) ? 1 : 0;
        case "|": return wrapInt(a | b); case "^": return wrapInt(a ^ b); case "&": return wrapInt(a & b);
        case "==": return a === b ? 1 : 0; case "!=": return a !== b ? 1 : 0;
        case "<": return a < b ? 1 : 0; case ">": return a > b ? 1 : 0; case "<=": return a <= b ? 1 : 0; case ">=": return a >= b ? 1 : 0;
        case "<<": return wrapInt(a * Math.pow(2, b)); case ">>": return wrapInt(Math.floor(a / Math.pow(2, b)));
        case "+": return wrapInt(a + b); case "-": return wrapInt(a - b); case "*": return wrapInt(a * b);
        case "/": if (b === 0) throw new Error("Division by zero."); return wrapInt(Math.trunc(a / b));
        case "%": if (b === 0) throw new Error("Division by zero."); return wrapInt(a % b);
      }
      throw new Error("Unsupported operator " + op);
    }
    var res = { kind: "expr" };
    if (toks.length >= 2 && toks[0].t === "id" && toks[1].t === "op" && /^(=|\|=|&=|\^=|<<=|>>=|\+=|-=)$/.test(toks[1].v)) {
      var name = toks[0].v, op = toks[1].v; i = 2;
      var rhs = expr(0);
      if (i < toks.length) throw new Error('Unexpected "' + toks[i].v + '" after the expression.');
      var old = REGN.indexOf(name) >= 0 ? regs[name] : (name in vars ? vars[name] : null);
      if (old === null && op !== "=") throw new Error('"' + name + '" is used before it has a value.');
      var nv = op === "=" ? rhs : apply(op.slice(0, -1), old, rhs);
      if (REGN.indexOf(name) >= 0) {
        if (/^PIN/.test(name)) { var port = "PORT" + name.slice(3); regs[port] = (regs[port] ^ (nv & 0xFF)) & 0xFF; res = { kind: "pin", name: name, port: port, rhs: nv }; }
        else { regs[name] = nv & 0xFF; res = { kind: "assign", name: name, full: nv, stored: nv & 0xFF }; }
      } else if (/^[a-z_]\w*$/.test(name)) { vars[name] = wrapInt(nv); res = { kind: "var", name: name, full: nv }; }
      else throw new Error('Unknown name "' + name + '".');
      return res;
    }
    var v = expr(0);
    if (i < toks.length) throw new Error('Unexpected "' + toks[i].v + '" after the expression.');
    res.value = v;
    return res;
  }
  function hx(v, bits) { var M = Math.pow(2, bits); var u = ((v % M) + M) % M; return "0x" + u.toString(16).toUpperCase().padStart(bits / 4, "0"); }
  function regRow(name, before) {
    var v = regs[name], h = '<div class="regline"><span class="rn">' + name + '</span><span class="bits">', input = /^PIN/.test(name);
    for (var b = 7; b >= 0; b--) {
      var bit = (v >> b) & 1, chg = before != null && (((before >> b) & 1) !== bit);
      if (input) h += '<button type="button" class="bit' + (chg ? " cell-chg" : "") + '" data-r="' + name + '" data-b="' + b + '" aria-pressed="' + (bit ? "true" : "false") + '" title="Click to change the level on ' + name.replace("PIN", "P") + b + '" aria-label="' + name + " bit " + b + '">' + bit + "</button>";
      else h += '<span class="bit' + (chg ? " cell-chg" : "") + '" aria-pressed="' + (bit ? "true" : "false") + '" style="display:inline-grid;place-items:center" title="' + name + " bit " + b + '">' + bit + "</span>";
    }
    return h + '</span><span class="rv">' + hx(v, 8) + " = " + v + (input ? " (input pins: click to change)" : "") + "</span></div>";
  }
  var lastShown = ["DDRB", "PORTB", "PINC"];
  function run(fromReset) {
    if (fromReset) reset();
    var before = {}; REGN.forEach(function (r) { before[r] = regs[r]; });
    var lines = codeEl.value.split(/;|\n/).map(function (s) { return s.trim(); }).filter(Boolean);
    var log = [], shown = [], err = null;
    lines.forEach(function (ln) {
      if (err) return;
      try {
        var r = evalStmt(ln);
        REGN.forEach(function (n) { if (new RegExp("\\b" + n + "\\b").test(ln) && shown.indexOf(n) < 0) shown.push(n); });
        if (r.kind === "expr") log.push("<code>" + esc(ln) + "</code> evaluates to " + hx(r.value, intBits) + " = " + r.value + (r.value ? " (true)" : " (false)"));
        else if (r.kind === "assign") log.push("<code>" + esc(ln) + "</code>: right side is " + hx(r.full, intBits) + " as an int; " + r.name + " keeps the low 8 bits, " + hx(r.stored, 8));
        else if (r.kind === "pin") log.push("<code>" + esc(ln) + "</code>: on an ATmega328P, writing 1s to " + r.name + " toggles those bits of " + r.port);
        else log.push("<code>" + esc(ln) + "</code>: " + r.name + " = " + hx(r.full, intBits) + " = " + wrapInt(r.full));
      } catch (e) { err = "In “" + ln + "”: " + e.message; }
    });
    if (!shown.length) shown = lastShown; else lastShown = shown;
    var vlist = Object.keys(vars).map(function (k) { return k + " = " + vars[k]; }).join(", ");
    out.innerHTML = (err ? '<p class="werr">' + esc(err) + "</p>" : "") + '<div class="regview">' + shown.map(function (n) { return regRow(n, before[n]); }).join("") + "</div>" +
      (log.length ? '<ul style="margin:0;padding-left:1.2em">' + log.map(function (l) { return "<li>" + l + "</li>"; }).join("") + "</ul>" : "") + (vlist ? '<p class="wnote">Variables: ' + esc(vlist) + "</p>" : "") +
      '<p class="wnote">Bits with a blue outline changed. Bit 7 is on the left.</p>';
    $$(".regview button.bit", out).forEach(function (b) {
      b.addEventListener("click", function () { var n = b.getAttribute("data-r"), k = +b.getAttribute("data-b"); init[n] ^= (1 << k); run(true); });
    });
  }
  pre.addEventListener("change", function () { codeEl.value = PRESETS[+pre.value][1]; run(true); });
  isel.addEventListener("change", function () { intBits = +isel.value; run(true); });
  $("#bf-run", el).addEventListener("click", function () { run(true); });
  $("#bf-reset", el).addEventListener("click", function () { reset(); codeEl.value = ""; run(false); });
  codeEl.value = PRESETS[0][1];
  run(true);
};

/* ================= AVR timer calculator ================= */
TOOLS.avrtimer = function (el) {
  el.innerHTML = toolHead("AVR timer calculator", "CTC mode compare values and PWM frequencies") + '<div class="wbody">' +
    '<div class="wrow"><label for="at-f">CPU clock</label><input type="text" id="at-f" value="16M" size="7"><span class="wlab">Hz</span>' +
    '<label for="at-t">Interrupt every</label><input type="text" id="at-t" value="250m" size="7"><span class="wlab">s</span>' +
    '<label for="at-w">Timer</label><select id="at-w"><option value="16">Timer1 (16-bit)</option><option value="8">Timer0 (8-bit)</option></select></div>' +
    '<div class="wout" id="at-out" aria-live="polite"></div></div>';
  var fin = $("#at-f", el), tin = $("#at-t", el), wsel = $("#at-w", el), out = $("#at-out", el);
  var PS = [[1, "001"], [8, "010"], [64, "011"], [256, "100"], [1024, "101"]];
  function run() {
    var f = parseSI(fin.value), t = parseSI(tin.value), bits = +wsel.value, max = Math.pow(2, bits) - 1;
    if (!(f > 0) || !(t > 0)) { out.innerHTML = '<p class="werr">Give the clock and the interval as positive values, for example 16M and 250m (or 0.25).</p>'; return; }
    var best = null, rows = PS.map(function (p) {
      var ticks = f * t / p[0], ocr = Math.round(ticks) - 1, fits = ocr >= 0 && ocr <= max, act = (ocr + 1) * p[0] / f, err = (act - t) / t * 100;
      if (fits && !best) best = { p: p, ocr: ocr, act: act, err: err };
      return "<tr" + (best && best.p === p ? ' style="background:var(--green-soft)"' : "") + "><td>" + p[0] + "</td><td>" + siFmt(p[0] / f, "s", 4) + "</td><td>" + fmtNum(ticks, 7) + "</td><td>" + (fits ? ocr : (ocr < 0 ? "too short" : "> " + max)) + "</td><td>" + (fits ? siFmt(act, "s", 6) : "—") + "</td><td>" + (fits ? fmtNum(err, 3) + "%" : "—") + "</td></tr>";
    }).join("");
    var codeTxt = "";
    if (best) {
      var cs = best.p[1], csBits = [];
      for (var k = 0; k < 3; k++) if (cs[k] === "1") csBits.push("(1 << CS" + (bits === 16 ? "1" : "0") + (2 - k) + ")");
      if (bits === 16) codeTxt = "TCCR1B |= (1 << WGM12);          // CTC mode: count 0..OCR1A, then restart\nOCR1A = " + best.ocr + ";                    // (" + best.ocr + " + 1) × " + best.p[0] + " / " + siFmt(f, "Hz") + " = " + siFmt(best.act, "s", 6) + "\nTIMSK1 |= (1 << OCIE1A);         // enable the compare-match A interrupt\nTCCR1B |= " + csBits.join(" | ") + ";   // prescaler " + best.p[0] + " (starts the timer)\nsei();                           // global interrupt enable\n\nISR(TIMER1_COMPA_vect) { /* runs every " + siFmt(best.act, "s", 6) + " */ }";
      else codeTxt = "TCCR0A |= (1 << WGM01);          // CTC mode: count 0..OCR0A, then restart\nOCR0A = " + best.ocr + ";\nTIMSK0 |= (1 << OCIE0A);\nTCCR0B |= " + csBits.join(" | ") + ";   // prescaler " + best.p[0] + "\nsei();\n\nISR(TIMER0_COMPA_vect) { /* runs every " + siFmt(best.act, "s", 6) + " */ }";
    }
    var pwm = PS.map(function (p) { return "<tr><td>" + p[0] + "</td><td>" + siFmt(f / (p[0] * 256), "Hz", 4) + "</td><td>" + siFmt(f / (p[0] * 510), "Hz", 4) + "</td></tr>"; }).join("");
    out.innerHTML = '<div class="tbl tt" style="margin:0"><table><thead><tr><th>prescaler N</th><th>tick</th><th>ticks needed</th><th>compare value</th><th>actual interval</th><th>error</th></tr></thead><tbody>' + rows + "</tbody></table></div>" +
      (best ? "<p>The smallest prescaler that fits gives the finest resolution (highlighted). In CTC mode the counter runs from 0 up to the compare value, so one period is <b>(compare + 1) × N / f<sub>clk</sub></b>.</p><pre data-lang=\"C\"><code>" + esc(codeTxt) + "</code></pre>" :
        '<p class="werr">No prescaler fits in a ' + bits + "-bit counter. Use the 16-bit timer, count several interrupts in software, or shorten the interval.</p>") +
      "<p>8-bit PWM frequencies at this clock:</p><div class=\"tbl tt\" style=\"margin:0\"><table><thead><tr><th>prescaler N</th><th>fast PWM f<sub>clk</sub>/(256N)</th><th>phase-correct f<sub>clk</sub>/(510N)</th></tr></thead><tbody>" + pwm + "</tbody></table></div>";
  }
  [fin, tin, wsel].forEach(function (x) { x.addEventListener("input", run); x.addEventListener("change", run); });
  run();
};
