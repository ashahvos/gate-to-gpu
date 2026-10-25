"""Part IV diagrams and generated timing diagrams: latches, flip-flops, registers, counters, FSMs, timing."""
import math
from dlib import Fig, diagram, fmt, wave
from d3 import _tg_symbol, term


# ======================================================================
# helpers
# ======================================================================
def not_left(f, x, y, h=30, cls="b"):
    """Inverter pointing left, body spanning x..x+39 (bubble on the left). Returns pins in (right) and out (left)."""
    xc = x + 19.5
    f.add(f'<g transform="translate({fmt(2 * xc)} 0) scale(-1 1)">')
    f.gate("NOT", x, y, h=h, cls=cls)
    f.add("</g>")
    return {"in": (x + 39, y + h / 2), "out": (x, y + h / 2)}


def latch_box(f, x, y, w=70, h=76, d="D", c="C", q="Q", title=None, cls="b"):
    f.rect(x, y, w, h, cls, 3)
    f.text(x + 7, y + 22.5, d, "tc")
    f.text(x + 7, y + h - 13.5, c, "tc")
    f.text(x + w - 7, y + 22.5, q, "tc", "end")
    if title:
        f.text(x + w / 2, y - 7, title, "tm", "middle")
    return {"D": (x, y + 18), "C": (x, y + h - 18), "Q": (x + w, y + 18)}


def clouds(f, x, y, w, h, label, sub=None):
    """Combinational-logic cloud drawn as a rounded blob."""
    f.path(f"M{fmt(x + 20)} {fmt(y)} H{fmt(x + w - 20)} Q{fmt(x + w)} {fmt(y)} {fmt(x + w)} {fmt(y + 20)} V{fmt(y + h - 20)} "
           f"Q{fmt(x + w)} {fmt(y + h)} {fmt(x + w - 20)} {fmt(y + h)} H{fmt(x + 20)} Q{fmt(x)} {fmt(y + h)} {fmt(x)} {fmt(y + h - 20)} "
           f"V{fmt(y + 20)} Q{fmt(x)} {fmt(y)} {fmt(x + 20)} {fmt(y)} Z", "bg")
    f.text(x + w / 2, y + h / 2 + (0 if sub else 5), label, "tb", "middle")
    if sub:
        f.text(x + w / 2, y + h / 2 + 16, sub, "tm", "middle")


def slash(f, x, y, n):
    f.line([(x - 5, y + 6), (x + 5, y - 6)], "wt")
    f.text(x + 2, y - 9, str(n), "tcs", "middle")


# ======================================================================
# Module 14: latches and flip-flops
# ======================================================================
@diagram("bistable")
def bistable():
    f = Fig(760, 300, "Two cross-coupled inverters form a bistable element; their overlaid transfer curves cross at two stable points and one metastable point")
    a = f.gate("NOT", 120, 70)
    b = not_left(f, 120, 170)
    f.line([a["out"], (230, a["out"][1]), (230, b["in"][1]), b["in"]])
    f.line([b["out"], (60, b["out"][1]), (60, a["ins"][0][1]), a["ins"][0]])
    f.dot(230, a["out"][1])
    f.dot(60, b["out"][1])
    f.text(238, a["out"][1] + 4, "Q", "tb")
    f.text(52, b["out"][1] + 4, "Q′", "tb", "end")
    f.text(145, 40, "each inverter drives", "tm", "middle")
    f.text(145, 56, "the other's input", "tm", "middle")
    f.text(145, 250, "no input: it can only hold", "tm", "middle")
    f.text(145, 266, "the value it powered up with", "tm", "middle")
    X0, Y0, W, H = 400, 24, 230, 230
    fx, fy = f.axes(X0, Y0, W, H, (0, 1), (0, 1), xticks=[(0, "0"), (1, "V_{DD}")], yticks=[(0, "0"), (1, "V_{DD}")],
                    xlabel="V(Q′)", ylabel="V(Q)", grid=False)

    def inv(v):
        k = 14.0
        s = 1 / (1 + math.exp(-k * (v - 0.5)))
        lo, hi = 1 / (1 + math.exp(k / 2)), 1 / (1 + math.exp(-k / 2))
        return 1 - (s - lo) / (hi - lo)
    pts1 = [(i / 200, inv(i / 200)) for i in range(201)]
    pts2 = [(inv(i / 200), i / 200) for i in range(201)]
    f.curve(fx, fy, pts1, "hw")
    f.curve(fx, fy, pts2, "aw")
    f.dot(fx(0), fy(1), 5, "dotc")
    f.text(fx(0) + 10, fy(1) + 20, "stable", "tcs halo")
    f.text(fx(0) + 10, fy(1) + 34, "Q = 1", "tcs halo")
    f.dot(fx(1), fy(0), 5, "dotc")
    f.text(fx(1) - 10, fy(0) - 26, "stable", "tcs halo", "end")
    f.text(fx(1) - 10, fy(0) - 12, "Q = 0", "tcs halo", "end")
    f.dot(fx(0.5), fy(0.5), 5, "dot")
    f.text(fx(0.5) + 12, fy(0.5) - 6, "metastable", "tcs halo")
    f.text(X0 + W + 14, Y0 + 40, "blue: top inverter", "tm")
    f.text(X0 + W + 14, Y0 + 56, "Q = f(Q′)", "tm")
    f.text(X0 + W + 14, Y0 + 84, "gold: bottom inverter", "tm")
    f.text(X0 + W + 14, Y0 + 100, "Q′ = f(Q)", "tm")
    return f.svg()


@diagram("sr_latch")
def sr_latch():
    f = Fig(560, 250, "An SR latch made from two cross-coupled NOR gates")
    t = f.gate("NOR", 180, 50)
    b = f.gate("NOR", 180, 150)
    f.line([(80, t["ins"][0][1]), t["ins"][0]])
    term(f, 76, t["ins"][0][1], "R", "left", "tb")
    f.line([(80, b["ins"][1][1]), b["ins"][1]])
    term(f, 76, b["ins"][1][1], "S", "left", "tb")
    f.line([t["out"], (356, t["out"][1])])
    term(f, 360, t["out"][1], "Q", "right", "tb")
    f.line([b["out"], (356, b["out"][1])])
    term(f, 360, b["out"][1], "Q′", "right", "tb")
    f.dot(280, t["out"][1])
    f.line([(280, t["out"][1]), (280, 120), (150, 120), (150, b["ins"][0][1]), b["ins"][0]])
    f.dot(300, b["out"][1])
    f.line([(300, b["out"][1]), (300, 132), (130, 132), (130, t["ins"][1][1]), t["ins"][1]])
    f.text(410, 70, "S = 1 sets Q = 1", "tm")
    f.text(410, 86, "R = 1 resets Q = 0", "tm")
    f.text(410, 102, "S = R = 0 holds", "tm")
    f.text(410, 118, "S = R = 1 is", "tm")
    f.text(410, 134, "not allowed", "tm")
    return f.svg()


@diagram("d_latch_mux")
def d_latch_mux():
    f = Fig(700, 230, "A D latch as a 2-to-1 multiplexer whose output feeds back to its own input")
    m = f.mux(260, 50, 2, 90, labels=("0", "1"))
    f.line([(150, m["ins"][1][1]), m["ins"][1]])
    term(f, 146, m["ins"][1][1], "D", "left", "tb")
    f.line([m["out"], (450, m["out"][1])])
    term(f, 454, m["out"][1], "Q", "right", "tb")
    f.dot(400, m["out"][1])
    f.line([(400, m["out"][1]), (400, 30), (220, 30), (220, m["ins"][0][1]), m["ins"][0]])
    f.line([m["sel"], (m["sel"][0], 180)])
    term(f, m["sel"][0], 184, "C (enable)", "below", "tb")
    f.text(520, 80, "C = 1: Q follows D", "tm")
    f.text(520, 96, "(transparent)", "tm")
    f.text(520, 128, "C = 0: Q holds its", "tm")
    f.text(520, 144, "last value (opaque)", "tm")
    return f.svg(min_width=520)


@diagram("dff_ms")
def dff_ms():
    f = Fig(760, 250, "A positive-edge-triggered D flip-flop built from two D latches enabled on opposite clock phases")
    a = latch_box(f, 200, 60, title="leader latch")
    b = latch_box(f, 420, 60, title="follower latch")
    f.line([(120, a["D"][1]), a["D"]])
    term(f, 116, a["D"][1], "D", "left", "tb")
    f.line([a["Q"], (345, a["Q"][1])])
    f.dot(345, a["Q"][1])
    f.line([(345, a["Q"][1]), b["D"]])
    f.text(345, a["Q"][1] - 10, "X", "tc", "middle")
    f.line([b["Q"], (580, b["Q"][1])])
    term(f, 584, b["Q"][1], "Q", "right", "tb")
    inv = f.gate("NOT", 140, a["C"][1] - 15)
    f.line([inv["out"], a["C"]])
    f.line([(100, 200), (100, a["C"][1]), inv["ins"][0]])
    f.dot(100, 200)
    f.line([(80, 200), (380, 200), (380, b["C"][1]), b["C"]])
    term(f, 76, 200, "CLK", "left", "tb")
    f.text(235, 166, "transparent while CLK = 0", "tcs", "middle")
    f.text(392, 166, "transparent while CLK = 1", "tcs")
    f.text(620, 70, "On the rising edge the", "tm")
    f.text(620, 86, "leader closes, holding", "tm")
    f.text(620, 102, "D as it was just before", "tm")
    f.text(620, 118, "the edge, and the", "tm")
    f.text(620, 134, "follower opens to pass", "tm")
    f.text(620, 150, "that value to Q.", "tm")
    return f.svg()


@diagram("ff_symbols")
def ff_symbols():
    f = Fig(780, 200, "Schematic symbols: a D latch, a rising-edge D flip-flop, a falling-edge D flip-flop, and a flip-flop with enable and asynchronous reset")

    def stubs(pins, keys_left, keys_right):
        for k in keys_left:
            x, y = pins[k]
            f.line([(x - 16, y), (x, y)])
        for k in keys_right:
            x, y = pins[k]
            f.line([(x, y), (x + 16, y)])
    p = latch_box(f, 40, 50, w=64)
    stubs(p, ("D", "C"), ("Q",))
    f.text(72, 160, "D latch", "tb", "middle")
    p = f.dff(220, 50, d="D", q="Q", qb=None)
    stubs(p, ("D", "CLK"), ("Q",))
    f.text(252, 160, "rising-edge", "tb", "middle")
    f.text(252, 176, "flip-flop", "tm", "middle")
    p = f.dff(410, 50, d="D", q="Q", qb=None, neg=True)
    stubs(p, ("D", "CLK"), ("Q",))
    f.text(442, 160, "falling-edge", "tb", "middle")
    f.text(442, 176, "flip-flop (bubble)", "tm", "middle")
    p = f.dff(600, 50, w=74, d="D", q="Q", qb=None, extra=(("left", 0.5, "EN"), ("bottom", 0.5, "RST")))
    stubs(p, ("D", "CLK", "EN"), ("Q",))
    f.line([p["RST"], (p["RST"][0], 142)])
    f.text(637, 160, "with enable and", "tb", "middle")
    f.text(637, 176, "asynchronous reset", "tm", "middle")
    return f.svg()


# ======================================================================
# Module 15: registers, counters, shift registers
# ======================================================================
@diagram("reg_enable")
def reg_enable():
    f = Fig(720, 230, "A register with a load enable: a 2-to-1 multiplexer recirculates the current value when EN = 0")
    m = f.mux(230, 50, 2, 80)
    p = f.dff(340, 52, w=70, d="D", q="Q", qb=None)
    f.line([m["out"], (300, m["out"][1]), (300, p["D"][1]), p["D"]])
    f.line([(130, m["ins"][1][1]), m["ins"][1]])
    term(f, 126, m["ins"][1][1], "D_{in}", "left", "tb")
    slash(f, 180, m["ins"][1][1], "n")
    f.line([p["Q"], (520, p["Q"][1])])
    term(f, 524, p["Q"][1], "Q", "right", "tb")
    slash(f, 480, p["Q"][1], "n")
    f.dot(450, p["Q"][1])
    f.line([(450, p["Q"][1]), (450, 26), (200, 26), (200, m["ins"][0][1]), m["ins"][0]])
    f.line([m["sel"], (m["sel"][0], 170)])
    term(f, m["sel"][0], 174, "EN", "below", "tb")
    f.line([(310, 190), (310, p["CLK"][1]), p["CLK"]])
    term(f, 310, 194, "CLK", "below", "tb")
    f.text(560, 80, "EN = 1: load D_{in}", "tm")
    f.text(560, 96, "EN = 0: Q* = Q (hold)", "tm")
    f.text(560, 128, "n flip-flops and n muxes", "tm")
    f.text(560, 144, "share CLK and EN", "tm")
    return f.svg()


@diagram("clock_gate")
def clock_gate():
    f = Fig(780, 230, "Gating a clock: an AND gate alone can produce glitches; an integrated clock-gating cell latches the enable while the clock is low")
    g = f.gate("AND", 150, 70)
    f.line([(70, g["ins"][0][1]), g["ins"][0]])
    term(f, 66, g["ins"][0][1], "CLK", "left", "tb")
    f.line([(70, g["ins"][1][1]), g["ins"][1]])
    term(f, 66, g["ins"][1][1], "EN", "left", "tb")
    f.line([g["out"], (260, g["out"][1])])
    term(f, 264, g["out"][1], "GCLK", "right", "tb")
    f.text(160, 30, "Unsafe: AND only", "tb", "middle")
    f.text(160, 170, "EN changing while CLK = 1", "tm", "middle")
    f.text(160, 186, "chops or adds clock pulses", "tm", "middle")
    l = latch_box(f, 470, 52, w=64, d="D", c="C", q="Q", title="latch, open while CLK = 0")
    f.circle(470 - 4.5, l["C"][1], 4.5, "b")
    g2 = f.gate("AND", 600, 60)
    f.line([(410, l["D"][1]), l["D"]])
    term(f, 406, l["D"][1], "EN", "left", "tb")
    f.line([l["Q"], (570, l["Q"][1]), (570, g2["ins"][0][1]), g2["ins"][0]])
    f.line([(410, 160), (580, 160), (580, g2["ins"][1][1]), g2["ins"][1]])
    f.dot(440, 160)
    f.line([(440, 160), (440, l["C"][1]), (461, l["C"][1])])
    term(f, 406, 160, "CLK", "left", "tb")
    f.line([g2["out"], (700, g2["out"][1])])
    term(f, 704, g2["out"][1], "GCLK", "right", "tb")
    f.text(590, 30, "Safe: integrated clock gate", "tb", "middle")
    f.text(590, 196, "the AND's enable input can only", "tm", "middle")
    f.text(590, 212, "change while CLK is low", "tm", "middle")
    f.line([(370, 20), (370, 220)], "gridl")
    return f.svg()


@diagram("shift_reg")
def shift_reg():
    f = Fig(780, 230, "A 4-bit serial-in, parallel-out shift register: on each clock edge every bit moves one flip-flop to the right")
    xs = [120, 270, 420, 570]
    ps = [f.dff(x, 60, w=64, d="D", q="Q", qb=None) for x in xs]
    f.line([(60, ps[0]["D"][1]), ps[0]["D"]])
    term(f, 56, ps[0]["D"][1], "SIN", "left", "tb")
    for i in range(3):
        f.line([ps[i]["Q"], ps[i + 1]["D"]])
        f.dot(ps[i]["Q"][0] + 30, ps[i]["Q"][1])
        f.line([(ps[i]["Q"][0] + 30, ps[i]["Q"][1]), (ps[i]["Q"][0] + 30, 34)])
        f.text(ps[i]["Q"][0] + 30, 26, f"Q{i}", "tc", "middle")
    f.line([ps[3]["Q"], (720, ps[3]["Q"][1])])
    term(f, 724, ps[3]["Q"][1], "Q3 = SOUT", "below", "tb")
    f.line([(80, 190), (640, 190)])
    term(f, 76, 190, "CLK", "left", "tb")
    for p in ps:
        f.dot(p["CLK"][0] - 20, 190)
        f.line([(p["CLK"][0] - 20, 190), (p["CLK"][0] - 20, p["CLK"][1]), p["CLK"]])
    return f.svg()


@diagram("lfsr")
def lfsr():
    f = Fig(780, 250, "A 4-bit linear-feedback shift register: the XOR of two taps is shifted in, cycling through all 15 nonzero states")
    xs = [150, 290, 430, 570]
    ps = [f.dff(x, 90, w=64, d="D", q="Q", qb=None) for x in xs]
    for i in range(3):
        f.line([ps[i]["Q"], ps[i + 1]["D"]])
    for i, p in enumerate(ps):
        f.text(p["Q"][0] - 32, 82, f"s{i}", "tcb", "middle")
    xc = 400 + 29
    f.add(f'<g transform="translate({fmt(2 * xc)} 0) scale(-1 1)">')
    f.gate("XOR", 400, 14)
    f.add("</g>")
    ins = [(458, 24), (458, 44)]
    out = (400, 34)
    f.dot(690, ps[3]["Q"][1])
    f.line([ps[3]["Q"], (690, ps[3]["Q"][1]), (690, ins[0][1]), ins[0]])
    f.dot(530, ps[2]["Q"][1])
    f.line([(530, ps[2]["Q"][1]), (530, ins[1][1]), ins[1]])
    f.line([out, (100, out[1]), (100, ps[0]["D"][1]), ps[0]["D"]])
    f.line([(690, ps[3]["Q"][1]), (720, ps[3]["Q"][1])])
    term(f, 724, ps[3]["Q"][1], "out", "below", "tb")
    f.line([(110, 214), (660, 214)])
    term(f, 106, 214, "CLK", "left", "tb")
    for p in ps:
        f.dot(p["CLK"][0] - 20, 214)
        f.line([(p["CLK"][0] - 20, 214), (p["CLK"][0] - 20, p["CLK"][1]), p["CLK"]])
    f.text(450, 246, "new s0 = s3 ⊕ s2   (taps for the polynomial x^{4} + x^{3} + 1)", "tm", "middle")
    return f.svg()


@diagram("sync_counter")
def sync_counter():
    f = Fig(780, 300, "A synchronous counter with reset, load and count enable: a register, an incrementer and three levels of selection")
    m1 = f.mux(250, 100, 2, 60)
    m2 = f.mux(370, 110, 2, 60, labels=("1", "0"))
    m3 = f.mux(490, 120, 2, 60, labels=("1", "0"))
    f.block(590, 100, 90, 100, "register", "4 flip-flops", "b")
    f.block(150, 200, 70, 40, "+1", None, "bs")
    f.line([m1["out"], (320, m1["out"][1]), (320, m2["ins"][1][1]), m2["ins"][1]])
    f.line([m2["out"], (440, m2["out"][1]), (440, m3["ins"][1][1]), m3["ins"][1]])
    f.line([m3["out"], (590, m3["out"][1])])
    f.line([(340, 76), (340, m2["ins"][0][1]), m2["ins"][0]])
    f.text(340, 68, "D", "tb", "middle")
    f.line([(460, 86), (460, m3["ins"][0][1]), m3["ins"][0]])
    f.text(460, 78, "0", "tb", "middle")
    f.line([(680, 150), (740, 150)])
    term(f, 744, 150, "Q", "below", "tb")
    f.dot(710, 150)
    f.line([(710, 150), (710, 274), (110, 274), (110, m1["ins"][0][1]), m1["ins"][0]])
    f.dot(110, 220)
    f.line([(110, 220), (150, 220)])
    f.line([(220, 220), (230, 220), (230, m1["ins"][1][1]), m1["ins"][1]])
    for m, lab in ((m1, "CE"), (m2, "LD"), (m3, "RST")):
        f.line([m["sel"], (m["sel"][0], m["sel"][1] + 22)])
        f.text(m["sel"][0], m["sel"][1] + 36, lab, "tcb", "middle")
    f.line([(635, 200), (635, 226)])
    f.text(635, 240, "CLK", "tcb", "middle")
    f.text(400, 24, "priority: RST > LD > CE", "tb", "middle")
    f.text(400, 40, "Q* = 0 if RST, else D if LD, else Q + 1 if CE, else Q", "tm", "middle")
    return f.svg()


@diagram("ripple_counter")
def ripple_counter():
    f = Fig(780, 210, "A 3-bit ripple counter built from toggle flip-flops: each stage is clocked by the previous stage's complemented output")
    xs = [160, 350, 540]
    for i, x in enumerate(xs):
        p = f.dff(x, 50, w=64, d="T", q="Q", qb="Q′")
        f.line([(x - 22, p["D"][1]), p["D"]])
        f.text(x - 26, p["D"][1] + 4, "1", "tb", "end")
        f.line([p["Q"], (x + 96, p["Q"][1])])
        term(f, x + 100, p["Q"][1], f"Q{i}", "right", "tb")
        if i == 0:
            f.line([(80, p["CLK"][1]), p["CLK"]])
            term(f, 76, p["CLK"][1], "CLK", "left", "tb")
        if i < 2:
            f.line([p["QB"], (xs[i + 1], p["QB"][1])])
    f.text(390, 170, "T = 1: every flip-flop toggles on its own clock edge", "tm", "middle")
    f.text(390, 188, "stage i + 1 toggles when Q_{i} falls (Q′_{i} rises), so the delays add up along the chain", "tm", "middle")
    return f.svg()


# ======================================================================
# Module 16: state machines
# ======================================================================
@diagram("fsm_block")
def fsm_block():
    f = Fig(780, 270, "Structure of a synchronous state machine: next-state logic, a state register, and output logic")
    clouds(f, 170, 70, 150, 100, "next-state", "logic (combinational)")
    f.block(380, 80, 110, 80, "state", "register", "bs")
    clouds(f, 560, 70, 130, 100, "output", "logic")
    f.line([(60, 100), (170, 100)], "w", end="ah")
    f.text(56, 104, "inputs", "tb", "end")
    f.line([(320, 120), (380, 120)], "w", end="ah")
    f.text(350, 112, "D", "tcs", "middle")
    f.line([(490, 120), (560, 120)], "w", end="ah")
    f.text(524, 112, "Q", "tcs", "middle")
    f.dot(525, 120)
    f.line([(525, 120), (525, 220), (140, 220), (140, 140), (170, 140)], "w", end="ah")
    f.text(330, 238, "current state", "tm", "middle")
    f.line([(690, 120), (750, 120)], "w", end="ah")
    f.text(722, 108, "outputs", "tb", "middle")
    f.line([(100, 100), (100, 30), (625, 30), (625, 70)], "dashc", end="ahc")
    f.dot(100, 100)
    f.text(360, 22, "Mealy only: outputs also depend directly on the inputs", "tcs tcol", "middle")
    f.line([(435, 52), (435, 80)], "w", end="ah")
    f.text(443, 50, "CLK, reset", "tcb")
    return f.svg()


@diagram("consec1s")
def consec1s():
    f = Fig(700, 270, "State diagram of a detector whose output F is 1 after two or more consecutive 1s")
    st = {"S0": dict(x=110, y=130, lines=["S0", "F = 0"]), "S1": dict(x=330, y=130, lines=["S1", "F = 0"]),
          "S2": dict(x=550, y=130, lines=["S2", "F = 1"], cls="ba")}
    ed = [dict(a="S0", b="S0", label="X = 0", ang=-90), dict(a="S0", b="S1", label="X = 1", bend=-30),
          dict(a="S1", b="S0", label="X = 0", bend=-26), dict(a="S1", b="S2", label="X = 1", bend=-30),
          dict(a="S2", b="S2", label="X = 1", ang=-90), dict(a="S2", b="S0", label="X = 0", bend=-130, off=12)]
    f.fsm(st, ed, r=34, reset=("S0", 180))
    return f.svg(min_width=520)


@diagram("seq101")
def seq101(kind="moore"):
    if kind == "moore":
        f = Fig(780, 260, "Moore state diagram for an overlapping 101 sequence detector; the output is 1 in state S3")
        st = {"S0": dict(x=100, y=140, lines=["S0", "out 0"]), "S1": dict(x=290, y=140, lines=["S1", "out 0"]),
              "S2": dict(x=480, y=140, lines=["S2", "out 0"]), "S3": dict(x=670, y=140, lines=["S3", "out 1"], cls="ba")}
        ed = [dict(a="S0", b="S0", label="0", ang=-90), dict(a="S0", b="S1", label="1", bend=-24),
              dict(a="S1", b="S1", label="1", ang=-90), dict(a="S1", b="S2", label="0", bend=-24),
              dict(a="S2", b="S0", label="0", bend=-70, off=10), dict(a="S2", b="S3", label="1", bend=-24),
              dict(a="S3", b="S1", label="1", bend=100, off=10), dict(a="S3", b="S2", label="0", bend=-24)]
        f.fsm(st, ed, r=34, reset=("S0", 180))
        f.text(390, 250, "S1: seen 1;  S2: seen 10;  S3: seen 101 (output 1)".replace("  ", "\u00a0\u00a0"), "tm", "middle")
    else:
        f = Fig(700, 290, "Mealy state diagram for an overlapping 101 sequence detector; the output is on the transition into a 1 after 10")
        st = {"S0": dict(x=120, y=140, lines=["S0"]), "S1": dict(x=350, y=140, lines=["S1"]), "S2": dict(x=580, y=140, lines=["S2"])}
        ed = [dict(a="S0", b="S0", label="0/0", ang=-90), dict(a="S0", b="S1", label="1/0", bend=-24),
              dict(a="S1", b="S1", label="1/0", ang=-90), dict(a="S1", b="S2", label="0/0", bend=-24),
              dict(a="S2", b="S0", label="0/0", bend=-140, off=10), dict(a="S2", b="S1", label="1/1", bend=-24, lcls="ta")]
        f.fsm(st, ed, r=32, reset=("S0", 180))
        f.text(350, 280, "labels are input/output; S1: seen 1, S2: seen 10", "tm", "middle")
    return f.svg(min_width=520)


@diagram("pump_fsm")
def pump_fsm():
    f = Fig(700, 230, "A two-state pump controller with hysteresis: it starts when the water drops below the low sensor and stops when it reaches the high sensor")
    st = {"OFF": dict(x=200, y=120, lines=["OFF", "pump 0"]), "ON": dict(x=500, y=120, lines=["ON", "pump 1"], cls="ba")}
    ed = [dict(a="OFF", b="OFF", label="L = 1", ang=-90), dict(a="OFF", b="ON", label="L = 0 (below low)", bend=-34),
          dict(a="ON", b="ON", label="H = 0", ang=-90), dict(a="ON", b="OFF", label="H = 1 (reached high)", bend=-34)]
    f.fsm(st, ed, r=36, reset=("OFF", 180))
    return f.svg(min_width=520)


@diagram("divider_dp")
def divider_dp():
    f = Fig(790, 330, "Datapath and controller for division by repeated subtraction")
    f.rect(20, 30, 530, 270, "bg", 10)
    f.text(36, 52, "datapath", "tb")
    m = f.mux(110, 80, 2, 70)
    f.line([(30, m["ins"][0][1]), m["ins"][0]])
    f.text(28, m["ins"][0][1] - 7, "dividend", "tcs")
    f.block(180, 90, 100, 50, "REM", "enable REM\\_LD", "b")
    f.line([m["out"], (180, m["out"][1])])
    f.line([m["sel"], (m["sel"][0], 172)])
    f.text(m["sel"][0], 186, "LOAD", "tcb", "middle")
    f.block(180, 200, 100, 50, "DIVISOR", None, "b")
    f.block(320, 130, 120, 60, "subtract", "REM − DIVISOR", "bs")
    f.line([(280, 115), (300, 115), (300, 145), (320, 145)])
    f.line([(280, 225), (300, 225), (300, 175), (320, 175)])
    f.line([(440, 160), (470, 160), (470, 64), (90, 64), (90, m["ins"][1][1]), m["ins"][1]])
    f.text(476, 112, "difference", "tcs")
    f.block(320, 236, 120, 50, "QUO", "clear, QUO\\_INC", "b")
    f.line([(380, 190), (380, 214), (600, 214)], "dashc", end="ahc")
    f.text(490, 208, "borrow", "tcs tcol", "middle")
    f.block(600, 80, 182, 170, None, None, "ba")
    f.text(691, 102, "controller (FSM)", "tb", "middle")
    for i, t in enumerate(("INIT: load, clear QUO", "TEST: borrow → DONE", "      else → SUB", "SUB:  REM ← diff,", "      QUO++ → TEST", "DONE: result ready")):
        f.text(610, 126 + 18 * i, t.replace(" ", "\u00a0"), "tcs")
    f.line([(600, 112), (550, 112)], "dashc", end="ahc")
    f.text(575, 104, "control", "tcs tcol", "middle")
    f.text(395, 322, "solid lines carry data; dashed lines carry control signals (LOAD, REM\\_LD, QUO\\_INC) and status (borrow)", "tm", "middle")
    return f.svg()


# ======================================================================
# Module 17: timing
# ======================================================================
@diagram("reg2reg")
def reg2reg():
    f = Fig(780, 250, "A register-to-register path: launch flip-flop, combinational logic, capture flip-flop, with the clock arriving at each")
    p1 = f.dff(110, 60, w=70, d="D", q="Q", qb=None, title="launch FF1")
    clouds(f, 260, 50, 200, 90, "combinational logic", "t_{pd} (max), t_{cd} (min)")
    p2 = f.dff(540, 60, w=70, d="D", q="Q", qb=None, title="capture FF2")
    f.line([(60, p1["D"][1]), p1["D"]])
    f.line([p1["Q"], (260, p1["Q"][1])])
    f.line([(460, p1["Q"][1]), p2["D"]])
    f.line([p2["Q"], (680, p2["Q"][1])])
    f.text(220, 70, "t_{clk→Q}", "tcs", "middle")
    f.text(500, 70, "t_{setup}, t_{hold}", "tcs", "middle")
    f.line([(40, 200), (500, 200)])
    term(f, 36, 200, "CLK", "left", "tb")
    f.line([(90, 200), (90, p1["CLK"][1]), p1["CLK"]])
    f.dot(90, 200)
    f.line([(500, 200), (500, p2["CLK"][1]), p2["CLK"]])
    f.rect(330, 190, 60, 20, "b", 3)
    f.text(360, 204, "wire", "tcs", "middle")
    f.text(300, 232, "clock arrives t_{skew} later at FF2", "tcs tcol", "middle")
    f.text(655, 176, "T ≥ t_{clk→Q} + t_{pd} + t_{setup} − t_{skew}", "tc", "middle")
    f.text(655, 198, "t_{clk→Q} + t_{cd} ≥ t_{hold} + t_{skew}", "tc", "middle")
    return f.svg()


@diagram("sync2ff")
def sync2ff():
    f = Fig(780, 220, "A two-flip-flop synchronizer: the first flip-flop may go metastable, and the second gives it a full clock period to resolve")
    p1 = f.dff(230, 50, w=70, d="D", q="Q", qb=None, title="FF1")
    p2 = f.dff(400, 50, w=70, d="D", q="Q", qb=None, title="FF2")
    f.line([(110, p1["D"][1]), p1["D"]])
    term(f, 106, p1["D"][1], "async\\_in", "left", "tb")
    f.line([p1["Q"], p2["D"]])
    f.text(335, p1["Q"][1] - 8, "may be metastable", "tcs tr", "middle")
    f.line([p2["Q"], (560, p2["Q"][1])])
    term(f, 564, p2["Q"][1], "sync\\_out", "right", "tb")
    f.line([(160, 170), (380, 170)])
    term(f, 156, 170, "dst\\_clk", "left", "tb")
    f.line([(210, 170), (210, p1["CLK"][1]), p1["CLK"]])
    f.dot(210, 170)
    f.line([(380, 170), (380, p2["CLK"][1]), p2["CLK"]])
    f.text(390, 206, "no logic between FF1 and FF2: the whole period is resolution time", "tm", "middle")
    return f.svg()


@diagram("async_fifo")
def async_fifo():
    f = Fig(780, 340, "An asynchronous FIFO: a dual-port memory written in one clock domain and read in another, with Gray-coded pointers synchronized across")
    f.rect(300, 60, 180, 110, "bs", 6)
    f.text(390, 112, "dual-port RAM", "tb", "middle")
    f.text(390, 130, "2^{n} entries", "tm", "middle")
    f.line([(340, 22), (340, 60)], "w", end="ah")
    f.text(340, 16, "wdata", "tcs", "middle")
    f.line([(440, 60), (440, 22)], "w", end="ah")
    f.text(440, 16, "rdata", "tcs", "middle")
    f.block(40, 60, 160, 50, "write pointer", "binary and Gray", "b")
    f.block(580, 60, 160, 50, "read pointer", "binary and Gray", "b")
    f.line([(200, 85), (300, 85)], "w", end="ah")
    f.text(250, 78, "waddr", "tcs", "middle")
    f.line([(580, 85), (480, 85)], "w", end="ah")
    f.text(530, 78, "raddr", "tcs", "middle")
    f.block(40, 220, 160, 44, "full flag logic", None, "b")
    f.block(580, 220, 160, 44, "empty flag logic", None, "b")
    f.line([(120, 110), (120, 220)], "w", end="ah")
    f.line([(660, 110), (660, 220)], "w", end="ah")
    f.block(300, 200, 180, 36, "2-FF sync into rclk", None, "ba", tcls="tcs")
    f.block(300, 262, 180, 36, "2-FF sync into wclk", None, "ba", tcls="tcs")
    f.line([(200, 100), (250, 100), (250, 218), (300, 218)], "w", end="ah")
    f.text(256, 160, "wptr", "tcs")
    f.text(256, 174, "(Gray)", "tcs")
    f.line([(480, 218), (560, 218), (560, 236), (580, 236)], "w", end="ah")
    f.line([(580, 100), (530, 100), (530, 280), (480, 280)], "w", end="ah")
    f.text(524, 160, "rptr", "tcs", "end")
    f.text(524, 174, "(Gray)", "tcs", "end")
    f.line([(300, 280), (230, 280), (230, 248), (200, 248)], "w", end="ah")
    f.text(120, 40, "write clock domain", "tcb", "middle")
    f.text(660, 40, "read clock domain", "tcb", "middle")
    f.text(390, 326, "only Gray-coded pointers cross between domains: one bit changes per increment", "tm", "middle")
    return f.svg()


@diagram("reset_sync")
def reset_sync():
    f = Fig(760, 220, "A reset synchronizer: reset asserts asynchronously and deasserts synchronously to the clock")
    p1 = f.dff(230, 50, w=70, d="D", q="Q", qb=None, extra=(("bottom", 0.5, "CLR"),), title="FF1")
    p2 = f.dff(400, 50, w=70, d="D", q="Q", qb=None, extra=(("bottom", 0.5, "CLR"),), title="FF2")
    f.line([(180, p1["D"][1]), p1["D"]])
    f.text(176, p1["D"][1] + 4, "1", "tb", "end")
    f.line([p1["Q"], p2["D"]])
    f.line([p2["Q"], (560, p2["Q"][1])])
    term(f, 564, p2["Q"][1], "rst\\_n\\_sync", "right", "tb")
    f.line([(120, 160), (450, 160)])
    term(f, 116, 160, "CLK", "left", "tb")
    f.line([(210, 160), (210, p1["CLK"][1]), p1["CLK"]])
    f.dot(210, 160)
    f.line([(380, 160), (380, p2["CLK"][1]), p2["CLK"]])
    f.dot(380, 160)
    f.line([(120, 196), (435, 196)], "rw")
    term(f, 116, 196, "rst\\_n (async)", "left", "tb")
    f.line([(265, 196), (265, p1["CLR"][1])], "rw")
    f.dot(265, 196)
    f.line([(435, 196), (435, p2["CLR"][1])], "rw")
    f.text(600, 120, "rst\\_n low: both FFs clear at once", "tm")
    f.text(600, 136, "rst\\_n high: a 1 shifts in, so", "tm")
    f.text(600, 152, "rst\\_n\\_sync rises on a clock edge", "tm")
    return f.svg()


# ======================================================================
# generated timing diagrams
# ======================================================================
def _compress(samples):
    """samples: list of (t, v); return change points."""
    out = []
    for t, v in samples:
        if not out or out[-1][1] != v:
            out.append([t, v])
    return out


def _clk_val(t, P, first, hi=None):
    hi = P / 2 if hi is None else hi
    if t < first:
        ph = (t - first) % P
    else:
        ph = (t - first) % P
    return 1 if ph < hi else 0


@wave("latch_ff")
def w_latch_ff():
    P, first, end, d = 20, 10, 170, 1.5
    dchg = [[0, 0], [14, 1], [23, 0], [27, 1], [44, 0], [57, 1], [76, 0], [93, 1], [104, 0], [116, 1], [134, 0], [155, 1]]

    def D(t):
        v = 0
        for tt, vv in dchg:
            if tt <= t:
                v = vv
        return v
    step = 0.25
    ts = [i * step for i in range(int(end / step) + 1)]
    ql, qf = [], []
    cur_l, cur_f = 0, 0
    prev_c = _clk_val(0, P, first)
    hist = {}
    for t in ts:
        c = _clk_val(t, P, first)
        if c == 1:
            cur_l = D(t)
        if c == 1 and prev_c == 0:
            cur_f = D(t - 0.01)
        prev_c = c
        hist[t] = (cur_l, cur_f)
    for t in ts:
        src = t - d
        if src < 0:
            ql.append((t, 0))
            qf.append((t, 0))
        else:
            k = round(src / step) * step
            l, ff = hist[k]
            ql.append((t, l))
            qf.append((t, ff))
    return {"end": end, "grid": [first + P * i for i in range(8) if first + P * i < end], "noTicks": True,
            "signals": [{"n": "CLK", "clk": [P, first]}, {"n": "D", "v": dchg, "c": 1},
                        {"n": "Q (latch)", "v": _compress(ql), "c": 2}, {"n": "Q (flip-flop)", "v": _compress(qf), "c": 3}],
            "alt": "Latch output follows D while the clock is high; flip-flop output changes only at rising edges"}


@wave("ff_timing")
def w_ff_timing():
    return {"end": 100, "grid": [50], "noTicks": True,
            "shade": [[38, 50, "setup", 1], [50, 57, "hold", 2]], "marks": [[63, "Q valid"]],
            "signals": [{"n": "CLK", "clk": [60, 50, 30]},
                        {"n": "D", "bus": [[0, "x"], [30, "new value"], [66, "x"]], "c": 1},
                        {"n": "Q", "bus": [[0, "old value"], [54, "x"], [63, "new value"]], "c": 2}],
            "alt": "D must be stable during the setup and hold window around the clock edge; Q changes after the clock-to-Q delay"}


@wave("resets")
def w_resets():
    P, first, end, d = 20, 10, 110, 1.5
    return {"end": end, "grid": [10, 30, 50, 70, 90], "noTicks": True,
            "shade": [[24, 34, "RST = 1"]],
            "signals": [{"n": "CLK", "clk": [P, first]}, {"n": "RST", "v": [[0, 0], [24, 1], [34, 0]], "c": 3},
                        {"n": "D", "v": [[0, 1]], "c": 1},
                        {"n": "Q (sync reset)", "v": [[0, 1], [30 + d, 0], [50 + d, 1]], "c": 2},
                        {"n": "Q (async reset)", "v": [[0, 1], [24 + d, 0], [50 + d, 1]], "c": 4}],
            "alt": "Synchronous reset takes effect at the next clock edge; asynchronous reset takes effect immediately"}


@wave("shift4")
def w_shift4():
    P, first, d = 20, 10, 1.5
    bits = [1, 0, 1, 1, 0, 0, 1, 0]
    end = first + P * len(bits) + 4
    sin = []
    for i, b in enumerate(bits):
        sin.append([max(0, first - 5 + P * i), b])
    q = [[0] for _ in range(4)]
    regs = [0, 0, 0, 0]
    chg = [[[0, 0]] for _ in range(4)]
    for i, b in enumerate(bits):
        t = first + P * i
        regs = [b] + regs[:3]
        for k in range(4):
            if chg[k][-1][1] != regs[k]:
                chg[k].append([t + d, regs[k]])
    sigs = [{"n": "CLK", "clk": [P, first]}, {"n": "SIN", "v": _compress([(a, b) for a, b in sin]), "c": 1}]
    for k in range(4):
        sigs.append({"n": f"Q{k}", "v": chg[k], "c": 2 if k < 3 else 3})
    return {"end": end, "grid": [first + P * i for i in range(len(bits))], "noTicks": True, "signals": sigs,
            "alt": "Shift register: each bit appears at Q0 and moves one stage per clock"}


@wave("counter_wave")
def w_counter():
    P, first, d = 20, 10, 1.5
    n = 11
    end = first + P * n + 2
    ce_off = (first + P * 5 + 5, first + P * 7 + 5)
    ld_on = (first + P * 8 + 5, first + P * 9 + 5)
    ce = [[0, 1], [ce_off[0], 0], [ce_off[1], 1]]
    ld = [[0, 0], [ld_on[0], 1], [ld_on[1], 0]]
    q, bus = 13, [[0, "13"]]
    for i in range(n):
        t = first + P * i
        ce_v = 0 if ce_off[0] <= t < ce_off[1] else 1
        ld_v = 1 if ld_on[0] <= t < ld_on[1] else 0
        if ld_v:
            q = 9
        elif ce_v:
            q = (q + 1) % 16
        if bus[-1][1] != str(q):
            bus.append([t + d, str(q)])
    return {"end": end, "grid": [first + P * i for i in range(n)], "noTicks": True,
            "signals": [{"n": "CLK", "clk": [P, first]}, {"n": "CE", "v": ce, "c": 1}, {"n": "LD (D = 9)", "v": ld, "c": 3},
                        {"n": "Q", "bus": bus, "c": 2}],
            "alt": "Counter counts when CE is 1, wraps from 15 to 0, holds when CE is 0, and loads 9 when LD is 1"}


@wave("ripple_wave")
def w_ripple():
    d = 3
    end = 60
    # counter goes from 3 to 4 at the clock edge at t = 10; then 4 -> 5 at t = 40
    return {"end": end, "grid": [10, 40], "noTicks": True, "shade": [[10, 10 + 3 * d, "wrong values", 3]],
            "signals": [{"n": "CLK", "clk": [30, 10]},
                        {"n": "Q0", "v": [[0, 1], [10 + d, 0], [40 + d, 1]], "c": 1},
                        {"n": "Q1", "v": [[0, 1], [10 + 2 * d, 0]], "c": 2},
                        {"n": "Q2", "v": [[0, 0], [10 + 3 * d, 1]], "c": 3},
                        {"n": "Q2 Q1 Q0", "bus": [[0, "011"], [10 + d, "010"], [10 + 2 * d, "000"], [10 + 3 * d, "100"], [40 + d, "101"]], "c": 4}],
            "alt": "A ripple counter passes through intermediate wrong values as each stage toggles the next"}


@wave("moore_mealy")
def w_moore_mealy():
    P, first, d = 20, 10, 1.5
    xs = [1, 0, 1, 0, 1, 1, 0, 1, 0, 0]
    end = first + P * len(xs) + 2
    def tchg(i):
        return max(0, first + P * (i - 1) + 3)
    xv = []
    for i, b in enumerate(xs):
        xv.append([tchg(i), b])
    xv = _compress([(a, b) for a, b in xv])
    # Moore 101 overlapping: states 0..3
    s = 0
    moore = [[0, 0]]
    mealy = [[0, 0]]
    sbus = [[0, "S0"]]

    def nxt(s, x):
        return {0: (1 if x else 0), 1: (1 if x else 2), 2: (3 if x else 0), 3: (1 if x else 2)}[s]
    ms = 0  # mealy state 0..2

    def mnxt(s, x):
        return {0: (1 if x else 0), 1: (1 if x else 2), 2: (1 if x else 0)}[s]
    for i, b in enumerate(xs):
        t_change = tchg(i)
        mo = 1 if (ms == 2 and b == 1) else 0
        if mealy[-1][1] != mo:
            mealy.append([t_change + 1, mo])
        te = first + P * i
        s = nxt(s, b)
        ms = mnxt(ms, b)
        out = 1 if s == 3 else 0
        if moore[-1][1] != out:
            moore.append([te + d, out])
        if sbus[-1][1] != f"S{s}":
            sbus.append([te + d, f"S{s}"])
        mo2 = 1 if (ms == 2 and b == 1) else 0
        if mealy[-1][1] != mo2:
            mealy.append([te + d, mo2])
    return {"end": end, "grid": [first + P * i for i in range(len(xs))], "noTicks": True,
            "signals": [{"n": "CLK", "clk": [P, first]}, {"n": "X", "v": xv, "c": 1},
                        {"n": "Moore state", "bus": sbus, "c": 4},
                        {"n": "Moore out", "v": moore, "c": 2}, {"n": "Mealy out", "v": mealy, "c": 3}],
            "alt": "The Mealy output rises as soon as the final 1 arrives; the Moore output rises after the next clock edge and lasts a full cycle"}


@wave("metastable")
def w_metastable():
    return {"end": 120, "grid": [30, 60, 90], "noTicks": True, "shade": [[58, 61, "", 3], [62, 78, "resolving", 3]],
            "signals": [{"n": "dst_clk", "clk": [30, 30]},
                        {"n": "async_in", "v": [[0, 0], [59, 1]], "c": 1},
                        {"n": "FF1 Q", "v": [[0, 0], [62, "x"], [78, 1]], "c": 3},
                        {"n": "FF2 Q", "v": [[0, 0], [92, 1]], "c": 2}],
            "alt": "The input changes inside the setup window; FF1 hangs between levels before resolving; FF2 samples a clean value one cycle later"}


@wave("icg_wave")
def w_icg():
    return {"end": 120, "grid": [10, 30, 50, 70, 90, 110], "noTicks": True, "shade": [[33, 40, "glitch", 3], [70, 76, "short", 3]],
            "signals": [{"n": "CLK", "clk": [20, 10]},
                        {"n": "EN", "v": [[0, 0], [33, 1], [76, 0]], "c": 1},
                        {"n": "CLK·EN (unsafe)", "v": [[0, 0], [33, 1], [40, 0], [50, 1], [60, 0], [70, 1], [76, 0]], "c": 3},
                        {"n": "latched EN", "v": [[0, 0], [40, 1], [80, 0]], "c": 4},
                        {"n": "GCLK (ICG)", "v": [[0, 0], [50, 1], [60, 0], [70, 1], [80, 0]], "c": 2}],
            "alt": "With a plain AND gate an enable change while the clock is high creates a short pulse; the latch-based gate passes only whole pulses"}
