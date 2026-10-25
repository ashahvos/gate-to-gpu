"""Part III diagrams: circuits, analog building blocks, transistors and CMOS, interfacing."""
import math
from dlib import Fig, diagram, fmt


# ---------- helpers ----------
def vsrc(f, x, y, r=15, kind="ac", label=None, lab_side="left"):
    """Voltage source centred at (x, y); terminals above and below."""
    f.circle(x, y, r, "b")
    if kind == "ac":
        pts = [(x - r * 0.6 + i * (1.2 * r) / 24, y - r * 0.32 * math.sin(i / 24 * 2 * math.pi)) for i in range(25)]
        f.line(pts, "wt")
    else:
        f.text(x, y - 2, "+", "tb", "middle")
        f.text(x, y + 11, "−", "tb", "middle")
    if label:
        if lab_side == "left":
            f.text(x - r - 6, y + 4, label, "tc", "end")
        else:
            f.text(x + r + 6, y + 4, label, "tc")
    return {"top": (x, y - r), "bot": (x, y + r)}


def inductor(f, x, y1, y2, label=None, cls="w", bumps=4):
    """Vertical inductor between (x, y1) and (x, y2)."""
    L = y2 - y1
    lead = (L - bumps * 12) / 2
    d = f"M{fmt(x)} {fmt(y1)} V{fmt(y1 + lead)}"
    for i in range(bumps):
        ya = y1 + lead + 12 * i
        d += f" A6 6 0 0 1 {fmt(x)} {fmt(ya + 12)}"
    d += f" V{fmt(y2)}"
    f.path(d, cls)
    if label:
        f.text(x + 14, (y1 + y2) / 2 + 4, label, "tc")


def term(f, x, y, label=None, side="right", cls="tc"):
    f.circle(x, y, 4, "b")
    if label:
        if side == "right":
            f.text(x + 9, y + 4, label, cls)
        elif side == "left":
            f.text(x - 9, y + 4, label, cls, "end")
        elif side == "above":
            f.text(x, y - 10, label, cls, "middle")
        else:
            f.text(x, y + 18, label, cls, "middle")


def chip(f, x, y, w, h, title, sub=None):
    f.rect(x, y, w, h, "bs", 6)
    f.text(x + w / 2, y + 20, title, "tb", "middle")
    if sub:
        f.text(x + w / 2, y + 36, sub, "tm", "middle")


# ======================================================================
# Module 10: circuit fundamentals
# ======================================================================
@diagram("divider")
def divider():
    f = Fig(720, 320, "A voltage divider unloaded and with a load resistor connected to its output")

    def panel(x0, loaded):
        b = f.battery(x0 + 20, 150, "V_{S}")
        f.line([b["top"], (x0 + 20, 50), (x0 + 140, 50)])
        f.resistor(x0 + 140, 50, x0 + 140, 140, "R_{1}", lab_dx=14)
        f.dot(x0 + 140, 140)
        f.resistor(x0 + 140, 140, x0 + 140, 230, "R_{2}", lab_dx=14)
        f.line([(x0 + 140, 230), (x0 + 140, 258), (x0 + 20, 258), b["bot"]])
        f.ground(x0 + 80, 258)
        f.arrow([(x0 + 112, 66), (x0 + 112, 106)], "hw", "ahc", "I", lx=-10, ly=4, lcls="tcb", anchor="end")
        if not loaded:
            f.line([(x0 + 140, 140), (x0 + 236, 140)])
            term(f, x0 + 240, 140, "V_{out}")
            f.text(x0 + 150, 296, "V_{out} = V_{S} · R_{2} / (R_{1} + R_{2})", "tc", "middle")
            f.text(x0 + 150, 22, "Unloaded", "tb", "middle")
        else:
            f.line([(x0 + 140, 140), (x0 + 236, 140)])
            f.dot(x0 + 236, 140)
            f.resistor(x0 + 236, 140, x0 + 236, 230, "R_{L}", lab_dx=14)
            f.line([(x0 + 236, 230), (x0 + 236, 258), (x0 + 140, 258)])
            f.dot(x0 + 140, 258)
            f.text(x0 + 244, 128, "V_{out}", "tc")
            f.text(x0 + 150, 296, "V_{out} = V_{S} · (R_{2} ∥ R_{L}) / (R_{1} + R_{2} ∥ R_{L})", "tc", "middle")
            f.text(x0 + 150, 22, "With a load R_{L}", "tb", "middle")
    panel(40, False)
    panel(400, True)
    return f.svg()


@diagram("series_parallel")
def series_parallel():
    f = Fig(780, 300, "Worked example: a 9 V source driving R1 in series with R2 in parallel with the series pair R3 and R4")
    b = f.battery(70, 150, "9 V")
    f.line([b["top"], (70, 60), (110, 60)])
    f.resistor(110, 60, 230, 60, None)
    f.text(170, 44, "R_{1} = 1 kΩ", "tc", "middle")
    f.line([(230, 60), (420, 60)])
    f.dot(300, 60)
    f.text(300, 48, "node X", "tm", "middle")
    f.resistor(300, 60, 300, 240, "R_{2} = 3 kΩ", lab_dx=14)
    f.resistor(420, 60, 420, 150, "R_{3} = 1 kΩ", lab_dx=14)
    f.resistor(420, 150, 420, 240, "R_{4} = 2 kΩ", lab_dx=14)
    f.line([(420, 240), (420, 262), (70, 262), b["bot"]])
    f.line([(300, 240), (300, 262)])
    f.dot(300, 262)
    f.ground(190, 262)
    f.arrow([(86, 120), (86, 90)], "hw", "ahc", "3.6 mA", lx=12, ly=4, lcls="tcb", anchor="start")
    f.arrow([(284, 120), (284, 160)], "hw", "ahc", "1.8 mA", lx=-12, ly=4, lcls="tcb", anchor="end")
    f.arrow([(404, 84), (404, 124)], "hw", "ahc", "1.8 mA", lx=-12, ly=4, lcls="tcb", anchor="end")
    f.text(570, 80, "R_{3} + R_{4} = 3 kΩ", "tc")
    f.text(570, 102, "3 kΩ ∥ 3 kΩ = 1.5 kΩ", "tc")
    f.text(570, 124, "R_{eq} = 1 + 1.5 = 2.5 kΩ", "tc")
    f.text(570, 150, "I = 9 V / 2.5 kΩ = 3.6 mA", "tc")
    f.text(570, 172, "V_{R1} = 3.6 V, V_{X} = 5.4 V", "tc")
    f.text(570, 194, "V_{R3} = 1.8 V, V_{R4} = 3.6 V", "tc")
    return f.svg()


@diagram("thevenin")
def thevenin():
    f = Fig(700, 240, "Any linear circuit seen from two terminals behaves like a voltage source in series with one resistor")
    f.rect(40, 50, 180, 140, "bg", 8)
    f.text(130, 108, "linear circuit:", "tb", "middle")
    f.text(130, 126, "sources and", "tm", "middle")
    f.text(130, 142, "resistors", "tm", "middle")
    f.line([(220, 80), (262, 80)])
    f.line([(220, 160), (262, 160)])
    term(f, 266, 80, "A")
    term(f, 266, 160, "B")
    f.text(330, 126, "≡", "tL", "middle")
    b = vsrc(f, 420, 120, 18, "dc", "V_{TH}")
    f.line([b["top"], (420, 70), (450, 70)])
    f.resistor(450, 70, 560, 70, None)
    f.text(505, 56, "R_{TH}", "tc", "middle")
    f.line([(560, 70), (596, 70)])
    term(f, 600, 70, "A")
    f.line([b["bot"], (420, 170), (596, 170)])
    term(f, 600, 170, "B")
    f.text(420, 214, "V_{TH} = open-circuit voltage between A and B", "tm", "middle")
    f.text(420, 230, "R_{TH} = V_{TH} / short-circuit current = resistance seen with sources zeroed", "tm", "middle")
    return f.svg()


@diagram("rc_step")
def rc_step():
    f = Fig(760, 310, "RC charging circuit and the exponential capacitor voltage with marks at one, two, three and five time constants")
    b = f.battery(50, 150, "V_{S}")
    f.line([b["top"], (50, 70), (80, 70)])
    f.switch(80, 70, 120, closed=False)
    f.text(100, 100, "closes at t = 0", "tm", "middle")
    f.line([(120, 70), (140, 70)])
    f.resistor(140, 70, 220, 70, None)
    f.text(180, 56, "R", "tc", "middle")
    f.line([(220, 70), (250, 70)])
    f.dot(250, 70)
    f.line([(250, 70), (250, 140)])
    c = f.capacitor(250, 150, "v", "C", lab_dx=20)
    f.line([c["b"], (250, 230), (50, 230), b["bot"]])
    f.ground(150, 230)
    f.line([(250, 70), (290, 70)])
    term(f, 294, 70, "v_{C}(t)")
    X0, Y0, W, H = 400, 30, 320, 220
    fx, fy = f.axes(X0, Y0, W, H, (0, 5), (0, 1.05), xticks=[(i, f"{i}τ" if i else "0") for i in range(6)],
                    yticks=[(0, "0"), (0.632, "0.63"), (0.865, "0.86"), (0.95, "0.95"), (1, "1")], xlabel="time (in time constants τ = RC)",
                    ylabel="v_{C} / V_{S}", grid=False)
    f.line([(fx(0), fy(1)), (fx(5), fy(1))], "dash")
    f.line([(fx(0), fy(0)), (fx(1), fy(1))], "dashc")
    f.text(fx(1) + 4, fy(1) - 6, "initial slope reaches V_{S} at t = τ", "tm")
    pts = [(t / 50, 1 - math.exp(-t / 50)) for t in range(0, 251)]
    f.curve(fx, fy, pts, "aw")
    for t in (1, 2, 3):
        v = 1 - math.exp(-t)
        f.line([(fx(t), fy(0)), (fx(t), fy(v))], "dash")
        f.dot(fx(t), fy(v), 3.6, "dotc")
    f.text(fx(2.2), fy(0.42), "v_{C}(t) = V_{S}(1 − e^{−t/RC})", "tc")
    return f.svg()


@diagram("rc_filters")
def rc_filters():
    f = Fig(760, 420, "RC low-pass and high-pass filters with their straight-line Bode magnitude approximations")

    def lp_panel(x0, high):
        s = vsrc(f, x0 + 30, 110, 15, "ac", "v_{in}")
        f.line([s["top"], (x0 + 30, 60), (x0 + 60, 60)])
        if not high:
            f.resistor(x0 + 60, 60, x0 + 150, 60, None)
            f.text(x0 + 105, 46, "R", "tc", "middle")
        else:
            f.line([(x0 + 60, 60), (x0 + 101, 60)])
            f.capacitor(x0 + 105, 60, "h", "C")
            f.line([(x0 + 109, 60), (x0 + 150, 60)])
        f.line([(x0 + 150, 60), (x0 + 196, 60)])
        f.dot(x0 + 170, 60)
        term(f, x0 + 200, 60, "v_{out}")
        if not high:
            f.line([(x0 + 170, 60), (x0 + 170, 102)])
            c = f.capacitor(x0 + 170, 106, "v", "C", lab_dx=18)
            f.line([c["b"], (x0 + 170, 160)])
        else:
            f.resistor(x0 + 170, 60, x0 + 170, 160, "R", lab_dx=14)
        f.line([s["bot"], (x0 + 30, 160), (x0 + 170, 160)])
        f.ground(x0 + 100, 160)
        f.text(x0 + 150, 22, "High-pass" if high else "Low-pass", "tb", "middle")
        # Bode sketch
        X0, Y0, W, H = x0 + 50, 220, 250, 140
        fx, fy = f.axes(X0, Y0, W, H, (0.01, 100), (-40, 6), logx=True,
                        xticks=[(0.01, "f_c/100"), (0.1, "f_c/10"), (1, "f_c"), (10, "10f_c"), (100, "100f_c")],
                        yticks=[(0, "0 dB"), (-20, "−20"), (-40, "−40")], grid=True)
        pts = []
        for i in range(0, 201):
            fr = 10 ** (-2 + 4 * i / 200)
            mag = 1 / math.sqrt(1 + fr * fr) if not high else fr / math.sqrt(1 + fr * fr)
            pts.append((fr, 20 * math.log10(mag)))
        if not high:
            f.line([(fx(0.01), fy(0)), (fx(1), fy(0)), (fx(100), fy(-40))], "dashc")
        else:
            f.line([(fx(0.01), fy(-40)), (fx(1), fy(0)), (fx(100), fy(0))], "dashc")
        f.curve(fx, fy, pts, "aw")
        f.dot(fx(1), fy(-3.01), 3.6, "dotc")
        f.text(fx(1) + (-8 if not high else 8), fy(-3.01) + 18, "−3 dB at f_c", "tcs halo", "end" if not high else "start")
        if not high:
            f.text(fx(0.012), fy(-27), "−20 dB/decade above f_c", "tcs halo")
        else:
            f.text(fx(85), fy(-27), "+20 dB/decade below f_c", "tcs halo", "end")
    lp_panel(20, False)
    lp_panel(400, True)
    f.text(380, 412, "f_c = 1 / (2πRC)", "tc", "middle")
    return f.svg()


# ======================================================================
# Module 11: analog building blocks
# ======================================================================
@diagram("diode_iv")
def diode_iv():
    f = Fig(680, 320, "Current versus voltage for a silicon diode and two LEDs: almost no current until the forward voltage, then a steep rise")
    X0, Y0, W, H = 90, 26, 470, 230
    fx, fy = f.axes(X0, Y0, W, H, (-1, 3.5), (-2, 20), xticks=[(-1, "−1"), (0, "0"), (0.7, "0.7"), (1, "1"), (2, "2"), (3, "3")],
                    yticks=[(0, "0"), (10, "10"), (20, "20 mA")], xlabel="voltage across the device (volts)", ylabel="current I", grid=True)
    f.line([(fx(0), fy(-2)), (fx(0), fy(20))], "dash")
    def iv(v, vf):
        n = 0.055
        return min(25, 0.02 * (math.exp((v - vf) / n) - math.exp(-vf / n)))
    for vf, lab, cls, lx in ((0.62, "Si diode ≈ 0.7 V", "w", 0.9), (1.85, "red LED ≈ 2 V", "hw", 2.12), (2.85, "blue LED ≈ 3 V", "mw", 3.27)):
        pts = []
        for i in range(0, 451):
            v = -1 + 4.5 * i / 450
            cur = iv(v, vf)
            if cur > 20.5:
                break
            pts.append((v, cur))
        f.curve(fx, fy, pts, cls)
        if vf < 2.5:
            f.text(fx(lx) - 4, fy(14), lab, "tcs halo", "end")
        else:
            f.text(fx(lx), fy(14), lab, "tcs halo")
    f.text(fx(-0.95), fy(1.4), "reverse: tiny leakage", "tcs")
    return f.svg()


def _opamp_panel(f, x0, y0, kind):
    if kind == "follower":
        o = f.opamp(x0 + 90, y0 + 40, flip=True)
        f.line([(x0 + 20, o["plus"][1]), o["plus"]])
        term(f, x0 + 16, o["plus"][1], "v_{in}", "left")
        f.line([o["out"], (x0 + 240, o["out"][1])])
        f.dot(x0 + 200, o["out"][1])
        f.line([(x0 + 200, o["out"][1]), (x0 + 200, y0 + 140), (x0 + 70, y0 + 140), (x0 + 70, o["minus"][1]), o["minus"]])
        term(f, x0 + 244, o["out"][1], "v_{out}")
        f.text(x0 + 150, y0 + 14, "Voltage follower (buffer)", "tb", "middle")
        f.text(x0 + 150, y0 + 172, "v_{out} = v_{in}", "tc", "middle")
    elif kind == "noninv":
        o = f.opamp(x0 + 90, y0 + 30, flip=True)
        f.line([(x0 + 20, o["plus"][1]), o["plus"]])
        term(f, x0 + 16, o["plus"][1], "v_{in}", "left")
        f.line([o["out"], (x0 + 240, o["out"][1])])
        term(f, x0 + 244, o["out"][1], "v_{out}")
        f.dot(x0 + 210, o["out"][1])
        f.line([(x0 + 210, o["out"][1]), (x0 + 210, y0 + 130)])
        f.resistor(x0 + 210, y0 + 130, x0 + 110, y0 + 130, None)
        f.text(x0 + 160, y0 + 120, "R_{f}", "tc", "middle")
        f.line([(x0 + 110, y0 + 130), (x0 + 70, y0 + 130)])
        f.dot(x0 + 70, y0 + 130)
        f.line([(x0 + 70, y0 + 130), (x0 + 70, o["minus"][1]), o["minus"]])
        f.resistor(x0 + 70, y0 + 130, x0 + 70, y0 + 190, "R_{g}", lab_dx=-30)
        f.ground(x0 + 70, y0 + 190)
        f.text(x0 + 150, y0 + 14, "Non-inverting amplifier", "tb", "middle")
        f.text(x0 + 200, y0 + 196, "v_{out} = v_{in} (1 + R_{f}/R_{g})", "tc", "middle")
    elif kind == "inv":
        o = f.opamp(x0 + 120, y0 + 64)
        f.resistor(x0 + 30, o["minus"][1], x0 + 96, o["minus"][1], None)
        f.text(x0 + 63, o["minus"][1] - 12, "R_{in}", "tc", "middle")
        term(f, x0 + 26, o["minus"][1], "v_{in}", "left")
        f.line([(x0 + 96, o["minus"][1]), o["minus"]])
        f.dot(x0 + 104, o["minus"][1])
        f.line([(x0 + 104, o["minus"][1]), (x0 + 104, y0 + 42), (x0 + 150, y0 + 42)])
        f.resistor(x0 + 150, y0 + 42, x0 + 220, y0 + 42, None)
        f.text(x0 + 185, y0 + 32, "R_{f}", "tc", "middle")
        f.line([(x0 + 220, y0 + 42), (x0 + 230, y0 + 42), (x0 + 230, o["out"][1])])
        f.line([o["out"], (x0 + 256, o["out"][1])])
        f.dot(x0 + 230, o["out"][1])
        term(f, x0 + 260, o["out"][1], "v_{out}")
        f.line([o["plus"], (x0 + 104, o["plus"][1]), (x0 + 104, y0 + 160)])
        f.ground(x0 + 104, y0 + 160)
        f.text(x0 + 150, y0 + 14, "Inverting amplifier", "tb", "middle")
        f.text(x0 + 200, y0 + 196, "v_{out} = −v_{in} · R_{f}/R_{in}", "tc", "middle")
    else:  # comparator
        o = f.opamp(x0 + 100, y0 + 40, flip=True)
        f.line([(x0 + 26, o["plus"][1]), o["plus"]])
        term(f, x0 + 22, o["plus"][1], "v_{in}", "left")
        f.line([(x0 + 26, o["minus"][1]), o["minus"]])
        term(f, x0 + 22, o["minus"][1], "V_{ref}", "left")
        f.line([o["out"], (x0 + 236, o["out"][1])])
        term(f, x0 + 240, o["out"][1], "v_{out}")
        f.text(x0 + 150, y0 + 14, "Comparator (no feedback)", "tb", "middle")
        f.text(x0 + 150, y0 + 152, "v_{out} = high if v_{in} > V_{ref}, else low", "tc", "middle")


@diagram("opamp_configs")
def opamp_configs():
    f = Fig(760, 470, "Four op-amp circuits: voltage follower, non-inverting amplifier, inverting amplifier and comparator")
    _opamp_panel(f, 50, 10, "follower")
    _opamp_panel(f, 430, 10, "comparator")
    _opamp_panel(f, 50, 230, "noninv")
    _opamp_panel(f, 430, 230, "inv")
    f.line([(380, 20), (380, 450)], "gridl")
    f.line([(20, 220), (740, 220)], "gridl")
    return f.svg()


@diagram("schmitt")
def schmitt():
    f = Fig(760, 350, "A noisy, slowly rising and falling input: a plain comparator output chatters, a Schmitt trigger switches once each way")
    x0, x1 = 120, 560
    yt, yb = 30, 150
    def V(t):
        base = 0.5 - 0.42 * math.cos(2 * math.pi * t)
        return base + 0.07 * math.sin(97 * t) + 0.05 * math.sin(211 * t + 1.3) + 0.03 * math.sin(431 * t)
    N = 2000
    ts = [i / N for i in range(N + 1)]
    vs = [V(t) for t in ts]
    X = lambda t: x0 + t * (x1 - x0)
    Yin = lambda v: yb - v * (yb - yt)
    f.text(14, 84, "input", "tb")
    f.text(14, 100, "(noisy)", "tm")
    th, tp, tn = 0.5, 0.68, 0.32
    f.line([(x0, Yin(th)), (x1, Yin(th))], "dash")
    f.text(x1 + 6, Yin(th) + 4, "comparator threshold", "tcs")
    f.line([(x0, Yin(tp)), (x1, Yin(tp))], "dashc")
    f.text(x1 + 6, Yin(tp) + 4, "V_{T+} (rising)", "tcs")
    f.line([(x0, Yin(tn)), (x1, Yin(tn))], "dashc")
    f.text(x1 + 6, Yin(tn) + 4, "V_{T−} (falling)", "tcs")
    f.line([(X(t), Yin(v)) for t, v in zip(ts, vs)], "aw", extra=' style="stroke-width:1.6"')
    # plain comparator output
    y1t, y1b = 188, 228
    f.text(14, 206, "comparator", "tb")
    f.text(14, 222, "output", "tm")
    pts = []
    prev = None
    for t, v in zip(ts, vs):
        o = 1 if v > th else 0
        y = y1t if o else y1b
        if prev is not None and o != prev:
            pts.append((X(t), y1t if prev else y1b))
        pts.append((X(t), y))
        prev = o
    f.line(pts, "rw", extra=' style="stroke-width:1.6"')
    # schmitt output
    y2t, y2b = 270, 310
    f.text(14, 288, "Schmitt", "tb")
    f.text(14, 304, "output", "tm")
    pts = []
    st = 0
    for t, v in zip(ts, vs):
        ns = st
        if st == 0 and v > tp:
            ns = 1
        elif st == 1 and v < tn:
            ns = 0
        if ns != st:
            pts.append((X(t), y2t if st else y2b))
        st = ns
        pts.append((X(t), y2t if st else y2b))
    f.line(pts, "hw")
    # hysteresis loop
    lx, ly, lw, lh = 620, 206, 110, 100
    f.text(lx + lw / 2, ly - 14, "transfer curve", "tm", "middle")
    f.path(f"M{lx} {ly} V{ly + lh} H{lx + lw}", "wt")
    a, b = lx + lw * 0.4, lx + lw * 0.6
    f.line([(lx + 4, ly + lh - 8), (b, ly + lh - 8), (b, ly + 8), (lx + lw - 4, ly + 8)], "hw", end="ahc")
    f.line([(lx + lw - 4, ly + 8), (a, ly + 8), (a, ly + lh - 8), (lx + 4, ly + lh - 8)], "dashc", end="ahc")
    f.text(a, ly + lh + 14, "V_{T−}", "tcs", "end")
    f.text(b, ly + lh + 14, "V_{T+}", "tcs", "start")
    f.text(lx + lw + 4, ly + lh + 4, "v_{in}", "tcs")
    f.text(lx - 4, ly + 4, "v_{out}", "tcs", "end")
    return f.svg()


@diagram("adc_quant")
def adc_quant():
    f = Fig(640, 340, "Transfer function of an ideal 3-bit ADC: a staircase of eight codes, each one LSB wide, with quantization error of at most half an LSB")
    X0, Y0, W, H = 90, 20, 400, 260
    fx, fy = f.axes(X0, Y0, W, H, (0, 8), (0, 8), xticks=[(i, f"{i}/8" if i not in (0, 8) else ("0" if i == 0 else "V_{ref}")) for i in range(9)],
                    yticks=[(i + 0.5, format(i, "03b")) for i in range(8)], xlabel="analog input (fraction of V_{ref})",
                    ylabel="output code", grid=False)
    f.line([(fx(0), fy(0)), (fx(8), fy(8))], "dash")
    pts = []
    for k in range(8):
        lo = 0 if k == 0 else k - 0.5
        hi = k + 0.5 if k < 7 else 8
        pts += [(fx(lo), fy(k + 0.5)), (fx(hi), fy(k + 0.5))]
    f.line(pts, "hw")
    f.text(fx(8) + 6, fy(7.6), "ideal line", "tm")
    f.dim(fx(3.5), fx(4.5), fy(4.5) - 22, "1 LSB", above=True)
    f.text(fx(5.2), fy(1.6), "1 LSB = V_{ref} / 2^{n}", "tc")
    f.text(fx(5.2), fy(0.9), "error ≤ ½ LSB (rounding)", "tc")
    return f.svg()


@diagram("r2r")
def r2r():
    f = Fig(760, 280, "A 4-bit R-2R ladder DAC driven by four logic outputs")
    y = 70
    xs = [150, 290, 430, 570]
    f.line([(60, y), (xs[0], y)])
    f.resistor(60, y, 60, 190, "2R", lab_dx=-30)
    f.line([(60, y), (90, y)])
    f.ground(60, 190)
    for i, x in enumerate(xs):
        f.dot(x, y)
        f.resistor(x, y, x, 190, "2R", lab_dx=14)
        f.line([(x, 190), (x, 214)])
        bit = i
        f.rect(x - 30, 214, 60, 30, "bs", 4)
        f.text(x, 234, f"b{bit}", "tcb", "middle")
        if i < 3:
            f.resistor(x, y, xs[i + 1], y, None)
            f.text((x + xs[i + 1]) / 2, y - 14, "R", "tc", "middle")
    f.dot(60, y)
    f.line([(xs[-1], y), (650, y)])
    term(f, 654, y, "V_{out}")
    f.text(380, 268, "each b_{i} pin drives 0 V or V_{ref}:   V_{out} = V_{ref} · (8b_{3} + 4b_{2} + 2b_{1} + b_{0}) / 16", "tc", "middle")
    f.text(60, 48, "LSB end", "tm", "middle")
    f.text(570, 48, "MSB end", "tm", "middle")
    return f.svg()


@diagram("aliasing")
def aliasing():
    f = Fig(720, 230, "A signal at 0.9 times the sampling rate produces the same samples as a signal at 0.1 times the sampling rate")
    x0, x1, yc, A = 40, 680, 105, 70
    T = 10.0
    X = lambda t: x0 + t / T * (x1 - x0)
    hi = [(X(i / 100), yc - A * math.sin(2 * math.pi * 0.9 * i / 100)) for i in range(0, 1001)]
    lo = [(X(i / 100), yc + A * math.sin(2 * math.pi * 0.1 * i / 100)) for i in range(0, 1001)]
    f.line([(x0, yc), (x1, yc)], "gridl")
    f.line(hi, "aw", extra=' style="stroke-width:1.4"')
    f.line(lo, "dashc")
    for n in range(0, 11):
        t = n
        f.line([(X(t), yc), (X(t), yc - A * math.sin(2 * math.pi * 0.9 * t))], "wt")
        f.dot(X(t), yc - A * math.sin(2 * math.pi * 0.9 * t), 4.2, "dotc")
    f.line([(x0, 210), (x0 + 30, 210)], "aw")
    f.text(x0 + 38, 214, "input at 0.9 f_{s}", "tm")
    f.line([(x0 + 170, 210), (x0 + 200, 210)], "dashc")
    f.text(x0 + 208, 214, "alias at 0.1 f_{s}", "tm")
    f.dot(x0 + 350, 210, 4.2, "dotc")
    f.text(x0 + 360, 214, "samples, one every 1/f_{s}: both sinusoids pass through every one", "tm")
    return f.svg()


@diagram("pwm_avg")
def pwm_avg():
    f = Fig(720, 236, "PWM waveforms with 25, 50 and 75 percent duty cycle and the average voltage a low-pass filter extracts")
    x0, yt, yb = 60, 40, 150
    per = 50
    duties = [0.25] * 4 + [0.5] * 4 + [0.75] * 4
    pts = [(x0, yb)]
    x = x0
    for d in duties:
        pts += [(x, yb), (x, yt), (x + per * d, yt), (x + per * d, yb), (x + per, yb)]
        x += per
    f.line(pts, "hw")
    avg = []
    for k, d in enumerate(duties):
        xa = x0 + k * per
        avg += [(xa, yb - d * (yb - yt)), (xa + per, yb - d * (yb - yt))]
    f.line(avg, "aw", extra=' style="stroke-dasharray:7 4"')
    f.text(x0 - 8, yt + 4, "V_{DD}", "tcs", "end")
    f.text(x0 - 8, yb + 4, "0", "tcs", "end")
    for k, d in enumerate((25, 50, 75)):
        f.text(x0 + 100 + k * 200, 176, f"duty {d}%", "tb", "middle")
        f.text(x0 + 100 + k * 200, 194, f"average {d / 100:g} V_{{DD}}", "tc", "middle")
    f.text(360, 220, "average = duty cycle × V_{DD}  (dashed: what an RC low-pass with f_c ≪ f_{PWM} outputs)", "tm", "middle")
    return f.svg()


# ======================================================================
# Module 12: transistors and CMOS
# ======================================================================
def vswitch(f, x, y1, y2, closed, cls="w"):
    """Vertical switch between (x, y1) and (x, y2)."""
    f.dot(x, y1, 3)
    f.dot(x, y2, 3)
    if closed:
        f.line([(x, y1), (x, y2)], cls)
    else:
        f.line([(x, y1), (x + 14, y2 - 4)], cls)


def mos_mirror(f, x, y, t="n", cls="w"):
    """MOSFET drawn with its gate on the right. Returns pins like Fig.mosfet but mirrored."""
    xc = x
    f.add(f'<g transform="translate({fmt(2 * xc)} 0) scale(-1 1)">')
    p = f.mosfet(x, y, t, cls=cls)
    f.add("</g>")
    mx = lambda pt: (2 * xc - pt[0], pt[1])
    return {"g": mx(p["g"]), "top": mx(p["top"]), "bot": mx(p["bot"])}


def mos_rot(f, cx, cy, t="n", cls="w"):
    """MOSFET rotated so the gate points up and the channel terminals point left (bot) and right (top)."""
    f.add(f'<g transform="rotate(90 {fmt(cx)} {fmt(cy)})">')
    f.mosfet(cx, cy, t, cls=cls)
    f.add("</g>")
    return {"g": (cx, cy - 30), "right": (cx + 26, cy + 16), "left": (cx - 26, cy + 16)}


@diagram("nmos_xsec")
def nmos_xsec():
    f = Fig(760, 330, "Cross-section of an NMOS transistor: n-type source and drain in a p-type substrate, with a gate above a thin oxide")
    f.rect(60, 150, 460, 140, "bg", 0)
    f.text(290, 280, "p-type substrate (body)", "tm", "middle")
    f.rect(100, 150, 110, 46, "bs", 10)
    f.text(155, 178, "n+ source", "tc", "middle")
    f.rect(370, 150, 110, 46, "bs", 10)
    f.text(425, 178, "n+ drain", "tc", "middle")
    f.rect(200, 100, 180, 38, "ba", 2)
    f.text(290, 124, "gate", "tb", "middle")
    f.rect(200, 138, 180, 12, "b", 0)
    f.rect(210, 151, 160, 8, "bgr", 0)
    f.dim(210, 370, 222, "L = channel length", above=False)
    for x, y, lab in ((122, 150, "S"), (290, 100, "G"), (464, 150, "D")):
        f.line([(x, y), (x, 62)])
        term(f, x, 58, lab, "above", "tb")
    f.line([(290, 290), (290, 306)])
    term(f, 290, 310, None)
    f.text(302, 314, "B", "tb")
    f.text(386, 147, "oxide", "tcs")
    f.text(290, 176, "channel forms", "tcs tg", "middle")
    f.text(290, 190, "when V_{GS} > V_{T}", "tcs tg", "middle")
    f.text(546, 120, "gate oxide: a few nm of SiO₂", "tm")
    f.text(546, 136, "or a high-κ dielectric", "tm")
    f.text(546, 168, "channel (green): a thin layer", "tm")
    f.text(546, 184, "of electrons under the oxide", "tm")
    f.text(546, 230, "W (width) runs into the page;", "tm")
    f.text(546, 246, "current ∝ W / L", "tm")
    return f.svg()


@diagram("mos_switches")
def mos_switches():
    f = Fig(760, 270, "NMOS and PMOS transistors as switches: an NMOS conducts when its gate is high, a PMOS when its gate is low")

    def panel(x0, t):
        p = f.mosfet(x0 + 90, 120, t)
        f.line([p["top"], (p["top"][0], 66)])
        f.line([p["bot"], (p["bot"][0], 174)])
        term(f, p["top"][0], 62, "D" if t == "n" else "S", "right", "tc")
        term(f, p["bot"][0], 178, "S" if t == "n" else "D", "right", "tc")
        term(f, p["g"][0] - 4, p["g"][1], "G", "left", "tc")
        name = "NMOS" if t == "n" else "PMOS"
        f.text(x0 + 100, 30, name, "tb", "middle")
        for i, (g, on) in enumerate(((1, t == "n"), (0, t != "n"))):
            sx = x0 + 200 + i * 80
            f.line([(sx, 66), (sx, 92)])
            vswitch(f, sx, 92, 148, on, "aw" if on else "w")
            f.line([(sx, 148), (sx, 174)])
            f.text(sx, 196, f"G = {g}", "tc", "middle")
            f.text(sx, 212, "on" if on else "off", "ta" if on else "tm", "middle")
        f.text(x0 + 180, 244, "passes a strong 0, a weak 1" if t == "n" else "passes a strong 1, a weak 0", "tm", "middle")
    panel(20, "n")
    panel(400, "p")
    f.line([(380, 20), (380, 250)], "gridl")
    return f.svg()


@diagram("nmos_rload")
def nmos_rload():
    f = Fig(780, 300, "Resistor-load NMOS logic: an inverter, a NAND with series transistors, and a NOR with parallel transistors")

    def top(x0, title, expr):
        f.supply(x0 + 120, 30)
        f.resistor(x0 + 120, 38, x0 + 120, 100, "R", lab_dx=14)
        f.line([(x0 + 120, 100), (x0 + 120, 110)])
        f.dot(x0 + 120, 110)
        f.line([(x0 + 120, 110), (x0 + 206, 110)])
        term(f, x0 + 210, 110, "F")
        f.text(x0 + 120, 272, title, "tb", "middle")
        f.text(x0 + 120, 290, expr, "tc", "middle")
    # inverter
    x0 = 10
    top(x0, "Inverter", "F = A′")
    p = f.mosfet(x0 + 104, 136, "n", glabel="A")
    f.line([p["bot"], (x0 + 120, 190)])
    f.ground(x0 + 120, 190)
    # NAND
    x0 = 270
    top(x0, "NAND (series)", "F = (A·B)′")
    p1 = f.mosfet(x0 + 104, 136, "n", glabel="A")
    p2 = f.mosfet(x0 + 104, 188, "n", glabel="B")
    f.line([p2["bot"], (x0 + 120, 226)])
    f.ground(x0 + 120, 226)
    # NOR
    x0 = 530
    top(x0, "NOR (parallel)", "F = (A + B)′")
    f.line([(x0 + 120, 110), (x0 + 120, 120)])
    f.line([(x0 + 80, 120), (x0 + 160, 120)])
    f.dot(x0 + 120, 120)
    q1 = f.mosfet(x0 + 64, 156, "n", glabel="A")
    q2 = f.mosfet(x0 + 144, 156, "n", glabel="B")
    f.line([(x0 + 80, 120), q1["top"]])
    f.line([(x0 + 160, 120), q2["top"]])
    f.line([q1["bot"], (x0 + 80, 194), (x0 + 160, 194), q2["bot"]])
    f.dot(x0 + 120, 194)
    f.line([(x0 + 120, 194), (x0 + 120, 204)])
    f.ground(x0 + 120, 204)
    return f.svg()


@diagram("cmos_gates")
def cmos_gates():
    f = Fig(800, 330, "CMOS inverter, NAND and NOR: a PMOS pull-up network above an NMOS pull-down network that is its dual")
    # inverter
    x0 = 20
    f.supply(x0 + 110, 40)
    pp = f.mosfet(x0 + 94, 80, "p")
    f.line([(x0 + 110, 48), pp["top"]])
    pn = f.mosfet(x0 + 94, 180, "n")
    f.line([pp["bot"], pn["top"]])
    f.dot(x0 + 110, 130)
    f.line([(x0 + 110, 130), (x0 + 166, 130)])
    term(f, x0 + 170, 130, "Y")
    f.line([pn["bot"], (x0 + 110, 214)])
    f.ground(x0 + 110, 214)
    f.line([pp["g"], (x0 + 50, 80), (x0 + 50, 180), pn["g"]])
    f.dot(x0 + 50, 130)
    f.line([(x0 + 24, 130), (x0 + 50, 130)])
    term(f, x0 + 20, 130, "A", "left")
    f.text(x0 + 100, 284, "Inverter: Y = A′", "tb", "middle")
    f.text(x0 + 100, 302, "2 transistors", "tm", "middle")
    # NAND
    x0 = 270
    a = f.mosfet(x0 + 64, 80, "p", glabel="A")
    b = f.mosfet(x0 + 144, 80, "p", glabel="B")
    f.line([(x0 + 80, 54), (x0 + 80, 48), (x0 + 160, 48), (x0 + 160, 54)])
    f.supply(x0 + 120, 40)
    f.line([a["bot"], (x0 + 80, 118), (x0 + 160, 118), b["bot"]])
    f.dot(x0 + 120, 118)
    f.line([(x0 + 120, 118), (x0 + 206, 118)])
    term(f, x0 + 210, 118, "Y")
    n1 = f.mosfet(x0 + 104, 160, "n", glabel="A")
    n2 = f.mosfet(x0 + 104, 212, "n", glabel="B")
    f.line([(x0 + 120, 118), n1["top"]])
    f.line([n2["bot"], (x0 + 120, 246)])
    f.ground(x0 + 120, 246)
    f.text(x0 + 120, 284, "NAND: Y = (A·B)′", "tb", "middle")
    f.text(x0 + 120, 302, "PMOS parallel, NMOS series", "tm", "middle")
    # NOR
    x0 = 540
    f.supply(x0 + 120, 22)
    p1 = f.mosfet(x0 + 104, 66, "p", glabel="A")
    p2 = f.mosfet(x0 + 104, 118, "p", glabel="B")
    f.line([(x0 + 120, 30), p1["top"]])
    f.line([p2["bot"], (x0 + 120, 156)])
    f.dot(x0 + 120, 156)
    f.line([(x0 + 120, 156), (x0 + 216, 156)])
    term(f, x0 + 220, 156, "Y")
    f.line([(x0 + 120, 156), (x0 + 120, 166)])
    f.line([(x0 + 80, 166), (x0 + 160, 166)])
    q1 = f.mosfet(x0 + 64, 202, "n", glabel="A")
    q2 = f.mosfet(x0 + 144, 202, "n", glabel="B")
    f.line([(x0 + 80, 166), q1["top"]])
    f.line([(x0 + 160, 166), q2["top"]])
    f.line([q1["bot"], (x0 + 80, 236), (x0 + 160, 236), q2["bot"]])
    f.dot(x0 + 120, 236)
    f.line([(x0 + 120, 236), (x0 + 120, 244)])
    f.ground(x0 + 120, 244)
    f.text(x0 + 120, 284, "NOR: Y = (A + B)′", "tb", "middle")
    f.text(x0 + 120, 302, "PMOS series, NMOS parallel", "tm", "middle")
    return f.svg()


def _tg_symbol(f, x, y, w=36):
    """Transmission-gate bow-tie symbol from (x, y) to (x + w, y). Control pins on top (EN) and bottom (EN′)."""
    h = 13
    f.path(f"M{fmt(x)} {fmt(y - h)} L{fmt(x + w)} {fmt(y)} L{fmt(x)} {fmt(y + h)} Z", "b")
    f.path(f"M{fmt(x + w)} {fmt(y - h)} L{fmt(x)} {fmt(y)} L{fmt(x + w)} {fmt(y + h)} Z", "b")
    f.line([(x + w / 2, y - h / 2 - 1), (x + w / 2, y - h - 12)])
    f.circle(x + w / 2, y + h / 2 + 5, 4.5, "b")
    f.line([(x + w / 2, y + h / 2 + 9.5), (x + w / 2, y + h + 14)])
    return {"in": (x, y), "out": (x + w, y), "en": (x + w / 2, y - h - 12), "enb": (x + w / 2, y + h + 14)}


@diagram("tgate")
def tgate():
    f = Fig(780, 270, "A transmission gate built from an NMOS and a PMOS in parallel, its symbol, and a 2-to-1 multiplexer made from two transmission gates")
    xc = 150
    f.line([(xc, 44), (xc, 70)])
    term(f, xc, 40, "A", "above")
    f.line([(xc - 24, 70), (xc + 24, 70)])
    f.dot(xc, 70)
    n = f.mosfet(xc - 40, 120, "n")
    p = mos_mirror(f, xc + 40, 120, "p")
    f.line([(xc - 24, 70), n["top"]])
    f.line([(xc + 24, 70), p["top"]])
    f.line([n["bot"], (xc - 24, 170), (xc + 24, 170), p["bot"]])
    f.dot(xc, 170)
    f.line([(xc, 170), (xc, 196)])
    term(f, xc, 200, "B", "below")
    f.text(n["g"][0] - 6, n["g"][1] + 4, "EN", "tc", "end")
    f.text(p["g"][0] + 6, p["g"][1] + 4, "EN′", "tc")
    f.text(xc, 250, "NMOS passes 0 well, PMOS passes 1 well:", "tm", "middle")
    f.text(xc, 266, "together they pass both", "tm", "middle")
    # symbol
    s = _tg_symbol(f, 330, 120)
    f.line([(300, 120), s["in"]])
    f.line([s["out"], (396, 120)])
    f.text(296, 124, "A", "tc", "end")
    f.text(400, 124, "B", "tc")
    f.text(s["en"][0], s["en"][1] - 6, "EN", "tc", "middle")
    f.text(s["enb"][0], s["enb"][1] + 14, "EN′", "tc", "middle")
    f.text(348, 40, "symbol", "tb", "middle")
    # mux
    t0 = _tg_symbol(f, 560, 90)
    t1 = _tg_symbol(f, 560, 180)
    f.line([(520, 90), t0["in"]])
    f.line([(520, 180), t1["in"]])
    f.text(514, 94, "D0", "tc", "end")
    f.text(514, 184, "D1", "tc", "end")
    f.line([t0["out"], (660, 90), (660, 180), t1["out"]])
    f.dot(660, 135)
    f.line([(660, 135), (700, 135)])
    term(f, 704, 135, "Y")
    f.text(t0["en"][0], t0["en"][1] - 6, "S′", "tc", "middle")
    f.text(t0["enb"][0] + 10, t0["enb"][1] + 4, "S", "tcs")
    f.text(t1["en"][0] + 10, t1["en"][1] + 6, "S", "tcs")
    f.text(t1["enb"][0], t1["enb"][1] + 14, "S′", "tc", "middle")
    f.text(620, 40, "2-to-1 mux", "tb", "middle")
    f.text(620, 262, "S = 0 passes D0, S = 1 passes D1", "tm", "middle")
    return f.svg()


@diagram("cmos_charge")
def cmos_charge():
    f = Fig(760, 316, "Where CMOS dynamic energy goes: charging the load through the PMOS, then discharging it through the NMOS")

    def panel(x0, rising):
        f.add('<g transform="translate(0 26)">')
        f.supply(x0 + 100, 30)
        f.line([(x0 + 100, 38), (x0 + 100, 52)])
        if rising:
            f.resistor(x0 + 100, 52, x0 + 100, 112, None)
            f.text(x0 + 86, 86, "PMOS on", "tm", "end")
        else:
            vswitch(f, x0 + 100, 60, 104, False)
            f.line([(x0 + 100, 52), (x0 + 100, 60)])
            f.line([(x0 + 100, 104), (x0 + 100, 112)])
            f.text(x0 + 84, 88, "PMOS off", "tm", "end")
        f.line([(x0 + 100, 112), (x0 + 100, 130)])
        f.dot(x0 + 100, 130)
        f.line([(x0 + 100, 130), (x0 + 200, 130), (x0 + 200, 164)])
        c = f.capacitor(x0 + 200, 168, "v", "C_{L}", lab_dx=20)
        f.line([c["b"], (x0 + 200, 214)])
        f.ground(x0 + 200, 214)
        f.text(x0 + 206, 124, "v_{out}", "tc")
        if not rising:
            f.resistor(x0 + 100, 130, x0 + 100, 196, None)
            f.text(x0 + 86, 166, "NMOS on", "tm", "end")
        else:
            f.line([(x0 + 100, 130), (x0 + 100, 144)])
            vswitch(f, x0 + 100, 144, 188, False)
            f.line([(x0 + 100, 188), (x0 + 100, 196)])
            f.text(x0 + 84, 172, "NMOS off", "tm", "end")
        f.line([(x0 + 100, 196), (x0 + 100, 214)])
        f.ground(x0 + 100, 214)
        if rising:
            f.line([(x0 + 118, 60), (x0 + 118, 116), (x0 + 184, 116), (x0 + 184, 150)], "aw", end="aha")
            f.add("</g>")
            f.text(x0 + 160, 22, "Output rises 0 → V_{DD}", "tb", "middle")
            f.text(x0 + 160, 282, "supply delivers C_{L}V_{DD}^{2}: half is stored", "tm", "middle")
            f.text(x0 + 160, 298, "on C_{L}, half is burned in the PMOS", "tm", "middle")
        else:
            f.line([(x0 + 184, 150), (x0 + 184, 142), (x0 + 118, 142), (x0 + 118, 200)], "aw", end="aha")
            f.add("</g>")
            f.text(x0 + 160, 22, "Output falls V_{DD} → 0", "tb", "middle")
            f.text(x0 + 160, 282, "the stored ½C_{L}V_{DD}^{2} is burned", "tm", "middle")
            f.text(x0 + 160, 298, "in the NMOS; nothing returns to the supply", "tm", "middle")
    panel(40, True)
    panel(420, False)
    f.line([(380, 20), (380, 300)], "gridl")
    return f.svg()


@diagram("mos_iv")
def mos_iv():
    f = Fig(660, 360, "NMOS drain current versus drain-source voltage for several gate voltages, showing the triode and saturation regions")
    X0, Y0, W, H = 80, 24, 420, 250
    fx, fy = f.axes(X0, Y0, W, H, (0, 2.0), (0, 0.42), xticks=[(0, "0"), (0.5, "0.5"), (1, "1.0"), (1.5, "1.5"), (2, "2.0")],
                    yticks=[], xlabel="drain-source voltage V_{DS} (V)", ylabel="drain current I_{D}", grid=False)
    k, lam = 1.0, 0.06
    for vov, lab in ((0.2, "V_{GS} − V_{T} = 0.2 V"), (0.4, "0.4 V"), (0.6, "0.6 V"), (0.8, "0.8 V")):
        pts = []
        for i in range(0, 201):
            v = 2.0 * i / 200
            if v < vov:
                cur = k * (vov * v - v * v / 2)
            else:
                cur = k * vov * vov / 2
            cur *= (1 + lam * v)
            pts.append((v, cur))
        f.curve(fx, fy, pts, "hw")
        f.text(fx(2.0) + 6, fy(pts[-1][1]) + 4, lab, "tcs")
    bpts = [(v / 100, k * (v / 100) ** 2 / 2 * (1 + lam * v / 100)) for v in range(0, 87)]
    f.curve(fx, fy, bpts, "dashc")
    f.text(fx(0.03), fy(0.39), "triode (linear):", "tm")
    f.text(fx(0.03), fy(0.39) + 15, "acts like a resistor", "tm")
    f.text(fx(1.35), fy(0.27), "saturation: nearly constant", "tm", "middle")
    f.text(fx(1.35), fy(0.27) + 15, "current set by V_{GS}", "tm", "middle")
    f.text(fx(0.9), fy(0.395), "boundary V_{DS} = V_{GS} − V_{T}", "tcs tcol")
    f.text(fx(1.0), fy(0) + 50, "below V_{GS} = V_{T}: cutoff, no channel, I_{D} ≈ 0", "tm", "middle")
    return f.svg()


# ======================================================================
# Module 13: interfacing
# ======================================================================
def pushbutton(f, x1, x2, y, pressed=False):
    f.dot(x1, y, 3)
    f.dot(x2, y, 3)
    yb = y - (4 if pressed else 12)
    f.line([(x1 - 3, yb), (x2 + 3, yb)])
    xm = (x1 + x2) / 2
    f.line([(xm, yb), (xm, yb - 12)])
    f.line([(xm - 7, yb - 12), (xm + 7, yb - 12)])


@diagram("led_drive")
def led_drive():
    f = Fig(780, 290, "Driving an LED from a microcontroller pin: active-high (the pin sources current) and active-low (the pin sinks current)")
    # active high
    x0 = 20
    chip(f, x0, 70, 110, 130, "MCU")
    f.text(x0 + 104, 124, "PB5 = 1", "tc", "end")
    f.line([(x0 + 110, 120), (x0 + 160, 120)])
    f.resistor(x0 + 160, 120, x0 + 250, 120, None)
    f.text(x0 + 205, 144, "R", "tc", "middle")
    f.line([(x0 + 250, 120), (x0 + 290, 120)])
    d = f.diode(x0 + 290, 170, "down", led=True)
    f.line([(x0 + 290, 120), d["a"]])
    f.line([d["k"], (x0 + 290, 226)])
    f.ground(x0 + 290, 226)
    f.arrow([(x0 + 172, 100), (x0 + 236, 100)], "aw", "aha", "I", ly=-6, lcls="ta")
    f.text(x0 + 180, 30, "Active-high: pin sources current", "tb", "middle")
    f.text(x0 + 180, 276, "lit when the pin outputs 1", "tm", "middle")
    # active low
    x0 = 410
    f.supply(x0 + 100, 70)
    f.resistor(x0 + 100, 78, x0 + 100, 134, "R", lab_dx=14)
    d = f.diode(x0 + 100, 162, "down", led=True)
    f.line([(x0 + 100, 134), d["a"]])
    f.line([d["k"], (x0 + 100, 206), (x0 + 230, 206)])
    chip(f, x0 + 230, 126, 110, 124, "MCU")
    f.text(x0 + 236, 210, "PB5 = 0", "tc")
    f.arrow([(x0 + 140, 192), (x0 + 210, 192)], "aw", "aha", "I", ly=-6, lcls="ta")
    f.text(x0 + 180, 30, "Active-low: pin sinks current", "tb", "middle")
    f.text(x0 + 180, 276, "lit when the pin outputs 0", "tm", "middle")
    f.line([(390, 20), (390, 280)], "gridl")
    return f.svg()


@diagram("pin_model")
def pin_model():
    f = Fig(760, 300, "An output pin modeled as two switched resistors: when it drives high, the load current flows through the PMOS on-resistance and the pin voltage drops")
    f.rect(40, 30, 250, 250, "bg", 8)
    f.text(60, 52, "inside the chip", "tm")
    f.supply(170, 70)
    f.resistor(170, 78, 170, 140, None)
    f.text(156, 106, "R_{P} ≈ 25 Ω", "tc", "end")
    f.text(156, 122, "(PMOS on)", "tm", "end")
    f.line([(170, 140), (170, 160)])
    f.dot(170, 160)
    f.line([(170, 160), (290, 160)])
    term(f, 290, 160, None)
    f.text(290, 182, "pin", "tm", "middle")
    f.line([(170, 160), (170, 180)])
    vswitch(f, 170, 180, 226, False)
    f.text(152, 208, "NMOS off", "tm", "end")
    f.line([(170, 226), (170, 240)])
    f.ground(170, 240)
    f.line([(294, 160), (380, 160)])
    f.resistor(380, 160, 380, 240, "R_{load}", lab_dx=14)
    f.ground(380, 240)
    f.arrow([(310, 146), (360, 146)], "aw", "aha", "I", ly=-6, lcls="ta")
    f.text(450, 90, "V_{pin} = V_{DD} · R_{load} / (R_{P} + R_{load})", "tc")
    f.text(450, 120, "R_{load} = 1 kΩ:   V_{pin} ≈ 4.88 V   (5 mA)", "tc")
    f.text(450, 142, "R_{load} = 100 Ω: V_{pin} = 4.0 V    (40 mA)", "tc")
    f.text(450, 164, "R_{load} = 10 Ω:  V_{pin} ≈ 1.43 V   (143 mA)", "tc")
    f.text(450, 196, "datasheets give this as V_{OH} versus I_{OH};", "tm")
    f.text(450, 212, "past the rated current the 1 is no longer a valid 1", "tm")
    f.text(450, 228, "and the pin can be damaged", "tm")
    return f.svg()


@diagram("button_pullup")
def button_pullup():
    f = Fig(760, 300, "A push button read with a pull-up resistor: the pin reads 1 when the button is released and 0 when it is pressed")
    f.supply(110, 40)
    f.resistor(110, 48, 110, 118, None)
    f.text(96, 80, "10 kΩ", "tc", "end")
    f.text(96, 96, "pull-up", "tm", "end")
    f.line([(110, 118), (110, 176)])
    f.dot(110, 160)
    f.line([(110, 160), (330, 160)])
    f.add('<g transform="rotate(90 110 196)">')
    pushbutton(f, 90, 130, 196)
    f.add("</g>")
    f.text(146, 200, "push button", "tm")
    f.line([(110, 216), (110, 236)])
    f.ground(110, 236)
    chip(f, 330, 50, 190, 210, "MCU", "PD2 configured as input")
    f.text(338, 152, "PD2", "tc")
    f.line([(330, 160), (450, 160)])
    f.dot(450, 160)
    f.supply(450, 104)
    f.resistor(450, 112, 450, 160, None)
    f.text(464, 132, "internal", "tcs")
    f.text(464, 145, "pull-up", "tcs")
    f.text(425, 196, "optional: enabled by", "tcs", "middle")
    f.text(425, 210, "DDRD bit 2 = 0 and", "tcs", "middle")
    f.text(425, 224, "PORTD bit 2 = 1", "tcs", "middle")
    f.text(546, 136, "released: pulled up, reads 1", "tb")
    f.text(546, 160, "pressed: grounded, reads 0", "tb")
    f.text(546, 192, "so the button is active-low:", "tm")
    f.text(546, 208, "pressed ⇔ (PIND & (1 << 2)) == 0", "tm")
    return f.svg()


@diagram("open_drain")
def open_drain():
    f = Fig(760, 290, "An open-drain shared line: each device can only pull the line low; a single pull-up resistor makes it high when everyone releases it")
    f.supply(90, 30)
    f.resistor(90, 38, 90, 90, "R_{pull-up}", lab_dx=-86)
    f.line([(90, 90), (700, 90)], "hw")
    f.dot(90, 90)
    f.text(130, 80, "shared line (for example I²C SDA)", "tcs")
    for i, (dx, on) in enumerate(((240, False), (420, True), (600, False))):
        f.rect(dx - 70, 130, 150, 130, "bs", 6)
        f.text(dx + 5, 250, f"device {i + 1}", "tb", "middle")
        p = f.mosfet(dx - 16, 190, "n", cls="aw" if on else "w")
        f.line([(dx, 90), p["top"]], "hw")
        f.dot(dx, 90)
        f.line([p["bot"], (dx, 220)])
        f.ground(dx, 220)
        f.text(p["g"][0] - 4, 194, "1" if on else "0", "ta" if on else "tc", "end")
        f.text(dx + 10, 152, "on" if on else "off", "ta" if on else "tcs")
        f.text(dx + 10, 166, "pulls low" if on else "released", "tcs")
    f.text(380, 286, "line = 0 if any device pulls it low (wired-AND); nobody ever drives it high, so there is no contention", "tm", "middle")
    return f.svg(min_width=560)


@diagram("lowside_switch")
def lowside_switch():
    f = Fig(720, 330, "A low-side MOSFET switch driving an inductive load from a microcontroller pin, with a gate resistor, a gate pull-down and a flyback diode")
    chip(f, 30, 150, 120, 110, "MCU")
    f.text(144, 204, "PB1", "tc", "end")
    f.line([(150, 200), (190, 200)])
    f.resistor(190, 200, 270, 200, None)
    f.text(230, 186, "R_{G} 100 Ω", "tcs", "middle")
    f.line([(270, 200), (314, 200)])
    f.dot(290, 200)
    f.resistor(290, 200, 290, 268, None)
    f.text(282, 240, "100 kΩ", "tcs", "end")
    f.ground(290, 268)
    p = f.mosfet(344, 200, "n")
    f.text(380, 204, "logic-level NMOS", "tm")
    f.line([p["bot"], (360, 244)])
    f.ground(360, 244)
    f.supply(360, 28, "+12 V")
    f.line([(360, 36), (360, 60)])
    f.dot(360, 60)
    f.line([(360, 60), (460, 60)])
    inductor(f, 360, 60, 150)
    f.text(318, 104, "motor or", "tm", "end")
    f.text(318, 120, "relay coil", "tm", "end")
    d = f.diode(460, 105, "up")
    f.line([(460, 60), d["k"]])
    f.line([d["a"], (460, 150), (360, 150)])
    f.dot(360, 150)
    f.line([(360, 150), p["top"]])
    f.text(476, 104, "flyback diode", "tm")
    f.text(476, 120, "(cathode to +12 V)", "tm")
    f.line([(380, 80), (380, 132), (440, 132), (440, 80), (392, 80)], "aw", end="aha", extra=' style="stroke-width:1.8"')
    f.text(520, 240, "when the MOSFET turns off, the coil", "tm")
    f.text(520, 256, "current circulates through the diode", "tm")
    f.text(520, 272, "instead of spiking the drain voltage", "tm")
    return f.svg()


@diagram("level_shift")
def level_shift():
    f = Fig(780, 300, "Two level shifters: a resistor divider for a one-way 5 V to 3.3 V signal, and a MOSFET shifter for a bidirectional open-drain line")
    # divider
    chip(f, 20, 80, 100, 110, "5 V chip", "output")
    f.line([(120, 120), (150, 120)])
    f.resistor(150, 120, 230, 120, None)
    f.text(190, 106, "1.8 kΩ", "tcs", "middle")
    f.line([(230, 120), (270, 120)])
    f.dot(250, 120)
    f.resistor(250, 120, 250, 200, None)
    f.text(238, 164, "3.3 kΩ", "tcs", "end")
    f.ground(250, 200)
    chip(f, 270, 80, 100, 110, "3.3 V chip", "input")
    f.text(196, 254, "5 V × 3.3 / (1.8 + 3.3) ≈ 3.24 V", "tc", "middle")
    f.text(196, 272, "one direction only, adds an RC delay", "tm", "middle")
    # MOSFET shifter
    m = mos_rot(f, 590, 140, "n")
    f.supply(470, 40, "3.3 V")
    f.resistor(470, 48, 470, 156, None)
    f.text(458, 104, "10 kΩ", "tcs", "end")
    f.supply(710, 40, "5 V")
    f.resistor(710, 48, 710, 156, None)
    f.text(722, 104, "10 kΩ", "tcs")
    f.line([(420, 156), m["left"]])
    f.dot(470, 156)
    f.line([m["right"], (760, 156)])
    f.dot(710, 156)
    f.supply(590, 70, "3.3 V")
    f.line([(590, 78), m["g"]])
    f.text(612, 128, "NMOS", "tm")
    f.text(420, 176, "3.3 V side", "tm")
    f.text(760, 176, "5 V side", "tm", "end")
    f.text(590, 254, "either side pulling low pulls the other low;", "tm", "middle")
    f.text(590, 270, "released, each side is pulled up to its own supply", "tm", "middle")
    f.line([(400, 20), (400, 280)], "gridl")
    return f.svg()
