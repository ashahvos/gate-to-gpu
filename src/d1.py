"""Part I diagrams: digital abstraction, number representation."""
import math
from dlib import Fig, diagram, fmt


@diagram("logic_levels")
def logic_levels(vdd=5.0, voh=2.4, vih=2.0, vil=0.8, vol=0.4, left="Driver output", right="Receiver input",
                 note="TTL-compatible levels"):
    f = Fig(660, 330, f"Logic levels and noise margins: VOH {voh} V, VIH {vih} V, VIL {vil} V, VOL {vol} V")
    top, bot = 56, 306
    def Y(v):
        return bot - (v / vdd) * (bot - top)
    lx, rx, cw = 200, 450, 104
    f.text(lx + cw / 2, 26, left, "tb", "middle")
    f.text(lx + cw / 2, 42, "what it guarantees", "tm", "middle")
    f.text(rx + cw / 2, 26, right, "tb", "middle")
    f.text(rx + cw / 2, 42, "how it reads", "tm", "middle")
    # driver bands
    f.rect(lx, Y(vdd), cw, Y(voh) - Y(vdd), "ba", 0)
    f.text(lx + cw / 2, (Y(vdd) + Y(voh)) / 2 + 4, "valid 1", "tb", "middle")
    f.rect(lx, Y(voh), cw, Y(vol) - Y(voh), "b", 0, extra=' style="stroke-dasharray:4 3"')
    f.text(lx + cw / 2, (Y(voh) + Y(vol)) / 2 - 4, "not driven", "tm", "middle")
    f.text(lx + cw / 2, (Y(voh) + Y(vol)) / 2 + 11, "(switching only)", "tm", "middle")
    f.rect(lx, Y(vol), cw, Y(0) - Y(vol), "bg", 0)
    if Y(0) - Y(vol) > 16:
        f.text(lx + cw / 2, (Y(vol) + Y(0)) / 2 + 4, "valid 0", "tb", "middle")
    else:
        f.text(lx - 8, (Y(vol) + Y(0)) / 2 + 4, "valid 0", "tm", "end")
    # receiver bands
    f.rect(rx, Y(vdd), cw, Y(vih) - Y(vdd), "ba", 0)
    f.text(rx + cw / 2, (Y(vdd) + Y(vih)) / 2 + 4, "reads 1", "tb", "middle")
    f.rect(rx, Y(vih), cw, Y(vil) - Y(vih), "br", 0)
    f.text(rx + cw / 2, (Y(vih) + Y(vil)) / 2 + 4, "undefined", "tb", "middle")
    f.rect(rx, Y(vil), cw, Y(0) - Y(vil), "bg", 0)
    f.text(rx + cw / 2, (Y(vil) + Y(0)) / 2 + 4, "reads 0", "tb", "middle")
    # threshold lines
    v1 = lambda v: f"{v:.1f}" if abs(v * 10 - round(v * 10)) < 1e-9 else f"{v:.2f}"
    for v, lab, side in ((voh, "V_{OH} = " + v1(voh) + " V", "l"), (vol, "V_{OL} = " + v1(vol) + " V", "l"),
                         (vih, "V_{IH} = " + v1(vih) + " V", "r"), (vil, "V_{IL} = " + v1(vil) + " V", "r")):
        f.line([(lx + cw, Y(v)), (rx, Y(v))], "dash")
        if side == "l":
            f.text(lx - 8, Y(v) + 4, lab, "tc", "end")
        else:
            f.text(rx + cw + 8, Y(v) + 4, lab, "tc")
    # margins
    mx = lx + cw + 22
    if voh > vih:
        f.vdim(mx, Y(voh), Y(vih), "NM_{H} = " + v1(voh - vih) + " V")
    else:
        f.vdim(mx, Y(vih), Y(voh), "NM_{H} = " + v1(voh - vih) + " V", cls="rw", lcls="tr", kind="ah")
    if vil > vol:
        f.vdim(mx, Y(vil), Y(vol), "NM_{L} = " + v1(vil - vol) + " V")
    else:
        f.vdim(mx, Y(vol), Y(vil), "NM_{L} = " + v1(vil - vol) + " V", cls="rw", lcls="tr", kind="ah")
    # axis
    f.line([(44, Y(vdd)), (44, Y(0))], "wt")
    for v in (0, vdd):
        f.line([(39, Y(v)), (49, Y(v))], "wt")
        f.text(34, Y(v) + 4, v1(v) + " V", "tcs", "end")
    return f.svg()


@diagram("vtc")
def vtc(inverting=False, vdd=1.0, k=14.0, label=None):
    title = "Inverter" if inverting else "Buffer"
    f = Fig(560, 360, label or f"{title} voltage transfer characteristic with the unity-gain points that define VIL and VIH")
    X0, Y0, W, H = 96, 34, 300, 266
    fx, fy = f.axes(X0, Y0, W, H, (0, vdd), (0, vdd), xticks=[(0, "0"), (vdd, fmt(vdd) + " = V_{DD}")],
                    yticks=[(0, "0"), (vdd, fmt(vdd))], xlabel="input voltage V_{in}", ylabel="output voltage V_{out}", grid=False)
    def out(v):
        s = 1 / (1 + math.exp(-k * (v - vdd / 2) / vdd))
        lo, hi = 1 / (1 + math.exp(k / 2)), 1 / (1 + math.exp(-k / 2))
        s = (s - lo) / (hi - lo)
        return vdd * (1 - s if inverting else s)
    pts = [(i / 200 * vdd, out(i / 200 * vdd)) for i in range(201)]
    # unity-gain points
    def slope(v):
        h = 1e-4 * vdd
        return (out(v + h) - out(v - h)) / (2 * h)
    cands = []
    for i in range(1, 400):
        v = i / 400 * vdd
        if abs(abs(slope(v)) - 1) < 0.08:
            cands.append(v)
    vil = min(cands)
    vih = max(cands)
    # refine
    f.rect(fx(vil), fy(vdd), fx(vih) - fx(vil), fy(0) - fy(vdd), "br", 0, extra=' style="opacity:.55"')
    f.text((fx(vil) + fx(vih)) / 2, fy(vdd) - 6, "|gain| > 1 here", "tm", "middle")
    f.curve(fx, fy, pts, "hw")
    vol = out(vil) if not inverting else out(vih)
    voh = out(vih) if not inverting else out(vil)
    for v, lab in ((vil, "V_{IL}"), (vih, "V_{IH}")):
        f.line([(fx(v), fy(0)), (fx(v), fy(out(v)))], "dash")
        f.dot(fx(v), fy(out(v)), 3.6, "dotc")
        f.text(fx(v), fy(0) + 15, lab, "tcs", "middle")
    for v, lab in ((vol, "V_{OL}"), (voh, "V_{OH}")):
        f.line([(fx(0), fy(v)), (fx(vdd), fy(v))], "dash")
        f.text(fx(vdd) + 8, fy(v) + 4, lab + " ≈ " + fmt(round(v, 2)) + " V", "tc")
    f.text(fx(vdd) + 8, fy(vdd / 2) + 4, "slope −1 at V_{IL}, V_{IH}" if inverting else "slope +1 at V_{IL}, V_{IH}", "tm")
    f.text(fx(vdd) + 8, fy(vdd / 2) + 22, "NM_{L} = V_{IL} − V_{OL}", "tm")
    f.text(fx(vdd) + 8, fy(vdd / 2) + 40, "NM_{H} = V_{OH} − V_{IH}", "tm")
    return f.svg()


@diagram("restore")
def restore():
    f = Fig(680, 260, "A degraded, noisy input signal and the clean output a logic gate produces from it")
    x0, x1 = 110, 630
    # input trace area
    ytop, ybot = 30, 120
    vih_y = ytop + (ybot - ytop) * 0.32
    vil_y = ytop + (ybot - ytop) * 0.72
    f.text(10, (ytop + ybot) / 2 - 4, "gate input", "tb")
    f.text(10, (ytop + ybot) / 2 + 12, "(degraded)", "tm")
    pts = []
    level = [0, 1, 1, 0, 0, 1, 0, 1, 1, 0]
    seg = (x1 - x0) / len(level)
    for i in range(0, 600):
        x = x0 + i / 600 * (x1 - x0)
        k = min(int((x - x0) / seg), len(level) - 1)
        prev = level[k - 1] if k > 0 else level[0]
        t = (x - x0 - k * seg) / seg
        tgt = level[k]
        ramp = min(1, t / 0.35)
        v = prev + (tgt - prev) * ramp
        v = 0.12 + 0.76 * v
        v += 0.05 * math.sin(i * 0.9) + 0.035 * math.sin(i * 2.3 + 1) + 0.02 * math.sin(i * 5.1)
        y = ybot - v * (ybot - ytop)
        pts.append((x, y))
    f.line([(x0, vih_y), (x1, vih_y)], "dash")
    f.line([(x0, vil_y), (x1, vil_y)], "dash")
    f.text(x1 + 8, vih_y + 4, "V_{IH}", "tcs")
    f.text(x1 + 8, vil_y + 4, "V_{IL}", "tcs")
    f.line(pts, "aw", extra=' style="stroke-width:1.8"')
    # output
    yt2, yb2 = 170, 240
    f.text(10, (yt2 + yb2) / 2 - 4, "gate output", "tb")
    f.text(10, (yt2 + yb2) / 2 + 12, "(restored)", "tm")
    d = []
    delay = seg * 0.22
    cur = level[0]
    d.append((x0, yb2 if cur == 0 else yt2))
    for k in range(1, len(level)):
        if level[k] != level[k - 1]:
            x = x0 + k * seg + delay
            d.append((x, yb2 if level[k - 1] == 0 else yt2))
            d.append((x, yb2 if level[k] == 0 else yt2))
    d.append((x1, yb2 if level[-1] == 0 else yt2))
    f.line(d, "hw")
    f.text(x1 + 8, yt2 + 4, "V_{DD}", "tcs")
    f.text(x1 + 8, yb2 + 4, "0 V", "tcs")
    return f.svg()


@diagram("switch_logic")
def switch_logic():
    f = Fig(660, 250, "Two switches in series form AND; two switches in parallel form OR")
    def circuit(x0, parallel):
        top, botw = 58, 196
        b = f.battery(x0, 128)
        f.line([b["top"], (x0, top), (x0 + 60, top)])
        f.line([b["bot"], (x0, botw), (x0 + 240, botw), (x0 + 240, 139)])
        if not parallel:
            f.switch(x0 + 60, top, x0 + 100, closed=True, label="A = 1 (closed)")
            f.line([(x0 + 100, top), (x0 + 130, top)])
            f.switch(x0 + 130, top, x0 + 170, closed=False, label="B = 0 (open)")
            f.line([(x0 + 170, top), (x0 + 240, top), (x0 + 240, 117)])
            f.lamp(x0 + 240, 128, on=False)
            f.text(x0 + 120, 236, "Series: lamp = A·B (AND)", "tb", "middle")
            f.text(x0 + 262, 132, "off", "tm")
        else:
            f.line([(x0 + 60, top), (x0 + 60, top + 50)])
            f.dot(x0 + 60, top, 3.3)
            f.switch(x0 + 60, top, x0 + 140, closed=True, label="")
            f.text(x0 + 100, top - 10, "A = 1 (closed)", "tm", "middle")
            f.switch(x0 + 60, top + 50, x0 + 140, closed=False, label="B = 0 (open)")
            f.line([(x0 + 140, top), (x0 + 240, top), (x0 + 240, 117)])
            f.line([(x0 + 140, top + 50), (x0 + 160, top + 50), (x0 + 160, top)])
            f.dot(x0 + 160, top, 3.3)
            f.lamp(x0 + 240, 128, on=True)
            f.text(x0 + 120, 236, "Parallel: lamp = A + B (OR)", "tb", "middle")
            f.text(x0 + 262, 132, "on", "ta")
    circuit(40, False)
    circuit(360, True)
    return f.svg()


@diagram("bits_context")
def bits_context():
    f = Fig(680, 260, "The byte 01000001 read five different ways")
    bits = "01000001"
    x0, y0, cw = 28, 104, 34
    f.text(x0 + 4 * cw, y0 - 30, "one byte in memory", "tb", "middle")
    for i, b in enumerate(bits):
        f.rect(x0 + i * cw, y0, cw, 40, "ba" if b == "1" else "b", 0)
        f.text(x0 + i * cw + cw / 2, y0 + 26, b, "tc", "middle")
        f.text(x0 + i * cw + cw / 2, y0 - 8, str(7 - i), "tcs", "middle")
    f.text(x0 + 4 * cw, y0 + 62, "bit 7 (MSB) … bit 0 (LSB)", "tm", "middle")
    reads = [("unsigned integer", "65"), ("two's complement integer", "+65"), ("ASCII character", "'A'"),
             ("hexadecimal shorthand", "0x41"), ("BCD (two decimal digits)", "41")]
    bx, by, bw, bh, gap = 420, 18, 240, 38, 10
    sx, sy = x0 + 8 * cw + 6, y0 + 20
    for k, (name, val) in enumerate(reads):
        yy = by + k * (bh + gap)
        f.rect(bx, yy, bw, bh, "b", 5)
        f.text(bx + 12, yy + 24, name, "t")
        f.text(bx + bw - 12, yy + 25, val, "ta", "end")
        f.path(f"M{sx} {sy} C{sx + 60} {sy} {bx - 60} {yy + bh / 2} {bx - 2} {yy + bh / 2}", "wt", end="ah")
    return f.svg()


@diagram("twos_wheel")
def twos_wheel():
    f = Fig(680, 420, "Four-bit patterns arranged in a circle with their unsigned and two's complement values")
    cx, cy, R = 210, 210, 150
    f.circle(cx, cy, R, "bn")
    for i in range(16):
        a = math.radians(-90 + i * 22.5)
        px, py = cx + R * math.cos(a), cy + R * math.sin(a)
        f.dot(px, py, 3.2)
        bx, by = cx + (R + 26) * math.cos(a), cy + (R + 26) * math.sin(a)
        f.text(bx, by + 4, format(i, "04b"), "tc", "middle")
        ux, uy = cx + (R - 28) * math.cos(a), cy + (R - 28) * math.sin(a)
        f.text(ux, uy + 4, str(i), "tm", "middle")
        s = i - 16 if i >= 8 else i
        sx, sy = cx + (R - 56) * math.cos(a), cy + (R - 56) * math.sin(a)
        f.text(sx, sy + 4, ("−" + str(-s)) if s < 0 else ("+" + str(s) if s else "0"), "tb", "middle")
    # unsigned wrap between 15 and 0 (top), signed wrap between 7 and 8 (bottom)
    a = math.radians(-90 - 11.25)
    f.line([(cx + (R - 70) * math.cos(a), cy + (R - 70) * math.sin(a)), (cx + (R + 8) * math.cos(a), cy + (R + 8) * math.sin(a))], "hw")
    a2 = math.radians(-90 + 7.5 * 22.5)
    f.line([(cx + (R - 70) * math.cos(a2), cy + (R - 70) * math.sin(a2)), (cx + (R + 8) * math.cos(a2), cy + (R + 8) * math.sin(a2))], "aw")
    # clockwise arrow
    f.path(f"M{cx + 40} {cy - 34} A52 52 0 0 1 {cx + 48} {cy + 30}", "wt", end="ah")
    f.text(cx, cy + 4, "add 1 = one step", "tm", "middle")
    f.text(cx, cy + 20, "clockwise", "tm", "middle")
    lx = 430
    f.text(lx, 70, "Reading the rings", "tb")
    f.text(lx, 96, "outer: the 4-bit pattern", "tm")
    f.text(lx, 116, "middle: its unsigned value (0 to 15)", "tm")
    f.text(lx, 136, "inner: its two's complement value (−8 to +7)", "tm")
    f.line([(lx, 176), (lx + 26, 176)], "hw")
    f.text(lx + 34, 180, "unsigned overflow boundary", "t")
    f.text(lx + 34, 197, "15 + 1 wraps to 0 (carry out of bit 3)", "tm")
    f.line([(lx, 230), (lx + 26, 230)], "aw")
    f.text(lx + 34, 234, "signed overflow boundary", "t")
    f.text(lx + 34, 251, "+7 + 1 wraps to −8", "tm")
    f.text(lx, 300, "Subtracting k is the same as moving", "tm")
    f.text(lx, 318, "16 − k steps forward, which is why", "tm")
    f.text(lx, 336, "A − B can be computed as A + (−B).", "tm")
    return f.svg()


def _cells(f, x0, y0, bits, cw=28, h=30, hl=(), hlcls="ba", cls="b"):
    for i, b in enumerate(bits):
        f.rect(x0 + i * cw, y0, cw, h, hlcls if i in hl else cls, 0)
        f.text(x0 + i * cw + cw / 2, y0 + h / 2 + 5, b, "tc", "middle")


@diagram("sign_extend")
def sign_extend():
    f = Fig(640, 250, "Sign extension copies the sign bit into the new upper bits; zero extension fills them with zeros")
    cw = 30
    # signed example
    f.text(20, 30, "Sign extension (two's complement)", "tb")
    x4 = 40 + 4 * cw
    _cells(f, x4, 50, list("1011"))
    f.text(x4 + 4 * cw + 14, 70, "4 bits: −8 + 2 + 1 = −5", "tm")
    _cells(f, 40, 120, list("11111011"), hl=(0, 1, 2, 3))
    f.text(40 + 8 * cw + 14, 140, "8 bits: −128 + 64 + 32 + 16 + 8 + 2 + 1 = −5", "tm")
    for i in range(4):
        f.line([(x4 + cw / 2, 80), (40 + i * cw + cw / 2, 118)], "aw", end="aha", extra=' style="stroke-width:1.6"')
    for i in range(4):
        f.line([(x4 + i * cw + cw / 2, 80), (x4 + i * cw + cw / 2, 118)], "wt", end="ah")
    # zero extension
    f.text(20, 190, "Zero extension (unsigned): 1011 = 11 becomes", "tb")
    _cells(f, 40, 204, list("00001011"), hl=(0, 1, 2, 3), hlcls="bg")
    f.text(40 + 8 * cw + 14, 224, "0000 1011 = 11", "tm")
    return f.svg()


@diagram("shifts")
def shifts():
    f = Fig(760, 300, "Logical left shift, logical right shift and arithmetic right shift of 1011 0100 by one position")
    cw = 26
    rows = [("x << 1  (logical left)", "10110100", "01101000", 7, "0 enters on the right; the old bit 7 is lost", "×2, if the lost bit was 0"),
            ("x >> 1  (logical right)", "10110100", "01011010", 0, "0 enters on the left", "÷2 for unsigned values"),
            ("x >> 1  (arithmetic right)", "10110100", "11011010", 0, "the sign bit is copied in", "÷2 for signed values, rounding toward −∞")]
    y = 18
    for title, a, b, fill, n1, n2 in rows:
        f.text(20, y + 14, title, "tcb")
        _cells(f, 20, y + 24, list(a), cw)
        f.line([(20 + 8 * cw + 10, y + 39), (20 + 8 * cw + 46, y + 39)], "w", end="ah")
        x2 = 20 + 8 * cw + 56
        _cells(f, x2, y + 24, list(b), cw, hl=(fill,))
        f.text(x2 + 8 * cw + 14, y + 36, n1, "tm")
        f.text(x2 + 8 * cw + 14, y + 52, n2, "tm")
        y += 94
    return f.svg()


def _bitrow(f, x0, y0, bw, groups, label, example=None):
    """groups: list of (nbits, cls, name). example: string of bits."""
    f.text(x0 - 10, y0 + 21, label, "tb", "end")
    x = x0
    k = 0
    total = sum(g[0] for g in groups)
    for n, cls, name in groups:
        f.rect(x, y0, n * bw, 32, cls, 0)
        for j in range(1, n):
            f.line([(x + j * bw, y0 + 22), (x + j * bw, y0 + 32)], "wt", extra=' style="stroke-width:1"')
        if example:
            seg = example[k:k + n]
            if n * bw < 40:
                f.text(x + n * bw / 2, y0 + 20, seg, "tcs", "middle")
            else:
                for j, ch in enumerate(seg):
                    f.text(x + j * bw + bw / 2, y0 + 19, ch, "tcs", "middle")
        f.text(x + n * bw / 2, y0 + 48, name, "tm", "middle")
        hi = total - 1 - k
        lo = hi - n + 1
        f.text(x + 2, y0 - 5, str(hi), "tcs")
        if n > 1:
            f.text(x + n * bw - 2, y0 - 5, str(lo), "tcs", "end")
        x += n * bw
        k += n


@diagram("fp_layout")
def fp_layout():
    f = Fig(720, 290, "Bit fields of FP32, FP16 and BF16 with the value -6.75 encoded in each")
    bw = 19
    x0 = 70
    _bitrow(f, x0, 30, bw, [(1, "br", "sign"), (8, "bs", "exponent (bias 127)"), (23, "ba", "fraction: 23 bits after the hidden 1")], "FP32",
            "1" + "10000001" + "10110000000000000000000")
    _bitrow(f, x0, 120, bw, [(1, "br", "sign"), (5, "bs", "exp (bias 15)"), (10, "ba", "fraction (10 bits)")], "FP16", "1" + "10001" + "1011000000")
    _bitrow(f, x0, 210, bw, [(1, "br", "sign"), (8, "bs", "exponent (bias 127)"), (7, "ba", "fraction (7)")], "BF16", "1" + "10000001" + "1011000")
    f.text(x0 + 330, 160, "−6.75 = −1.1011₂ × 2²", "tb")
    f.text(x0 + 330, 180, "FP16 exponent field 2 + 15 = 17 = 10001", "tm")
    f.text(x0 + 330, 250, "BF16 is the top 16 bits of FP32:", "tm")
    f.text(x0 + 330, 268, "same range, fewer fraction bits", "tm")
    return f.svg()


@diagram("float_spacing")
def float_spacing():
    f = Fig(700, 236, "Representable values of a tiny 6-bit float format: spacing doubles in each binade")
    vals = []
    bias = 3
    for e in range(0, 7):
        for m in range(4):
            if e == 0:
                v = (m / 4) * 2 ** (1 - bias)
            else:
                v = (1 + m / 4) * 2 ** (e - bias)
            vals.append((v, e == 0))
    # full line 0..15
    x0, x1, y = 40, 670, 70
    def X(v):
        return x0 + v / 15 * (x1 - x0)
    f.line([(x0, y), (x1, y)], "wt")
    for v, sub in vals:
        f.line([(X(v), y - 9), (X(v), y + 9)], "aw" if not sub else "rw", extra=' style="stroke-width:1.6"')
    for v in (0, 1, 2, 4, 8, 14):
        f.text(X(v), y + 26, fmt(float(v)), "tcs", "middle")
    f.text(x0, y - 22, "All positive values, 0 to 14 (to scale)", "tb")
    f.text(X(10.9), y - 18, "spacing 2 between 8 and 14", "tm", "middle")
    f.text(X(5.5), y - 18, "spacing 1", "tm", "middle")
    # zoom 0..2
    y2 = 176
    def Z(v):
        return x0 + v / 2 * (x1 - x0)
    f.line([(x0, y2), (x1, y2)], "wt")
    for v, sub in vals:
        if v <= 2.0001:
            f.line([(Z(v), y2 - 9), (Z(v), y2 + 9)], "aw" if not sub else "rw", extra=' style="stroke-width:1.6"')
    for v in (0, 0.25, 0.5, 1, 1.5, 2):
        f.text(Z(v), y2 + 26, fmt(float(v)), "tcs", "middle")
    f.text(x0, y2 - 40, "Zoom: 0 to 2", "tb")
    f.text(Z(0.125), y2 - 14, "subnormals", "tr", "middle")
    f.text(Z(1.5), y2 - 14, "spacing 0.25 between 1 and 2", "tm", "middle")
    f.text(Z(0.75), y2 - 14, "spacing 0.125", "tm", "middle")
    return f.svg()
