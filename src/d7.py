"""Part VII diagrams: Verilog to hardware, chip design flow, yield, test, thermal."""
import math
import random
from dlib import Fig, diagram, fmt
from d3 import term
from d4 import clouds


@diagram("rtl_map")
def rtl_map():
    f = Fig(780, 250, "How a clocked always block maps onto hardware: the register, the incrementer and the enable multiplexer")
    f.rect(20, 40, 300, 120, "bg", 8)
    lines = ("always @(posedge clk)", "  if (rst)      count <= 0;", "  else if (en) count <= count + 1;")
    for i, ln in enumerate(lines):
        f.text(34, 76 + 26 * i, ln.replace(" ", " "), "tc")
    f.line([(330, 100), (370, 100)], "w", end="ah")
    f.block(400, 150, 60, 40, "+1", None, "bs")
    m1 = f.mux(500, 60, 2, 60)
    m2 = f.mux(580, 70, 2, 60, labels=("0", "1"))
    p = f.dff(660, 72, w=64, d="D", q="Q", qb=None)
    f.line([m1["out"], (560, m1["out"][1]), (560, m2["ins"][0][1]), m2["ins"][0]])
    f.line([(560, m2["ins"][1][1]), m2["ins"][1]])
    f.text(556, m2["ins"][1][1] + 4, "0", "tb", "end")
    f.line([m2["out"], (640, m2["out"][1]), (640, p["D"][1]), p["D"]])
    f.line([p["Q"], (760, p["Q"][1])])
    f.text(760, p["Q"][1] - 8, "count", "tcs", "end")
    f.dot(745, p["Q"][1])
    f.line([(745, p["Q"][1]), (745, 225), (380, 225), (380, 170), (400, 170)])
    f.dot(380, 205)
    f.line([(380, 205), (480, 205), (480, m1["ins"][0][1]), m1["ins"][0]])
    f.line([(460, 170), (470, 170), (470, m1["ins"][1][1]), m1["ins"][1]])
    f.line([m1["sel"], (m1["sel"][0], 140)])
    f.text(m1["sel"][0], 154, "en", "tcb", "middle")
    f.line([m2["sel"], (m2["sel"][0], 150)])
    f.text(m2["sel"][0], 164, "rst", "tcb", "middle")
    f.line([(648, 176), (648, p["CLK"][1]), p["CLK"]])
    f.text(648, 190, "clk", "tcb", "middle")
    return f.svg()


@diagram("blocking_nb")
def blocking_nb():
    f = Fig(780, 230, "Blocking and nonblocking assignments in a clocked block: nonblocking gives the intended two-stage shift register")
    f.text(30, 30, "nonblocking:  b <= a;  c <= b;".replace("  ", "  "), "tc")
    p1 = f.dff(110, 50, w=60, d="D", q="Q", qb=None)
    p2 = f.dff(250, 50, w=60, d="D", q="Q", qb=None)
    f.line([(60, p1["D"][1]), p1["D"]])
    f.text(56, p1["D"][1] + 4, "a", "tb", "end")
    f.line([p1["Q"], p2["D"]])
    f.text(210, p1["Q"][1] - 6, "b", "tb", "middle")
    f.line([p2["Q"], (350, p2["Q"][1])])
    f.text(356, p2["Q"][1] + 4, "c", "tb")
    f.text(210, 160, "c is a delayed by two cycles", "tm", "middle")
    f.text(430, 30, "blocking:  b = a;  c = b;".replace("  ", "  "), "tc")
    q1 = f.dff(530, 50, w=60, d="D", q="Q", qb=None)
    q2 = f.dff(530, 130, w=60, d="D", q="Q", qb=None)
    f.line([(470, q1["D"][1]), q1["D"]])
    f.text(466, q1["D"][1] + 4, "a", "tb", "end")
    f.dot(500, q1["D"][1])
    f.line([(500, q1["D"][1]), (500, q2["D"][1]), q2["D"]])
    f.line([q1["Q"], (640, q1["Q"][1])])
    f.text(646, q1["Q"][1] + 4, "b", "tb")
    f.line([q2["Q"], (640, q2["Q"][1])])
    f.text(646, q2["Q"][1] + 4, "c", "tb")
    f.text(610, 222, "b and c both capture a: the second stage is lost", "tm", "middle")
    return f.svg()


@diagram("design_flow")
def design_flow():
    f = Fig(800, 360, "The ASIC design flow from specification to packaged, tested chips")
    steps = (("specification", "PPA targets, cost, schedule"), ("architecture", "blocks, interfaces, budgets"),
             ("RTL design", "Verilog / SystemVerilog"), ("verification", "simulation, formal, coverage"),
             ("logic synthesis", "gates from a cell library"), ("DFT insertion", "scan chains, BIST"),
             ("physical design", "floorplan, place, clock tree, route"), ("signoff", "STA, power, DRC, LVS"),
             ("tapeout", "layout database to the fab"), ("fabrication", "~3 months, hundreds of steps"),
             ("wafer test, dicing,", "packaging, final test"))
    for i, (a, b) in enumerate(steps):
        col, row = divmod(i, 6)
        x, y = 40 + col * 380, 20 + row * 56
        cls = "ba" if i in (3, 7) else ("bs" if i < 8 else "bgr")
        f.rect(x, y, 300, 44, cls, 6)
        f.text(x + 14, y + 19, a, "tb")
        f.text(x + 14, y + 35, b, "tm")
        if i not in (5, 10):
            if row < 5:
                f.line([(x + 150, y + 44), (x + 150, y + 56)], "w", end="ah")
    f.line([(340, 312), (360, 312), (360, 34), (420, 34)], "w", end="ah")
    f.line([(40, 192), (24, 192), (24, 142), (40, 142)], "rw", end="ah")
    f.text(20, 170, "fix", "tcs tr", "end")
    f.line([(720, 118), (738, 118), (738, 46), (720, 46)], "rw", end="ah")
    f.text(744, 86, "iterate", "tcs tr")
    return f.svg()


def _wafer(f, cx, cy, R, die, defects):
    f.circle(cx, cy, R, "bg")
    good = bad = 0
    n = int(2 * R // die) + 2
    for i in range(-n, n):
        for j in range(-n, n):
            x0, y0 = cx + i * die, cy + j * die
            corners = [(x0, y0), (x0 + die, y0), (x0, y0 + die), (x0 + die, y0 + die)]
            if all(math.hypot(px - cx, py - cy) <= R - 3 for px, py in corners):
                hit = any(x0 <= dx < x0 + die and y0 <= dy < y0 + die for dx, dy in defects)
                f.rect(x0 + 1, y0 + 1, die - 2, die - 2, "br" if hit else "bs", 1)
                if hit:
                    bad += 1
                else:
                    good += 1
    for dx, dy in defects:
        f.dot(dx, dy, 2.6, "dot")
    return good, bad


@diagram("yield_wafer")
def yield_wafer():
    f = Fig(780, 330, "The same random defects on wafers with small and large dies: a larger die is more likely to contain a defect")
    rnd = random.Random(7)
    R = 130
    pts = []
    while len(pts) < 26:
        x, y = rnd.uniform(-R, R), rnd.uniform(-R, R)
        if math.hypot(x, y) < R - 10:
            pts.append((x, y))
    g1, b1 = _wafer(f, 190, 160, R, 26, [(190 + x, 160 + y) for x, y in pts])
    g2, b2 = _wafer(f, 560, 160, R, 52, [(560 + x, 160 + y) for x, y in pts])
    f.text(190, 312, f"small dies: {g1} good of {g1 + b1} ({round(100 * g1 / (g1 + b1))}%)", "tc", "middle")
    f.text(560, 312, f"large dies: {g2} good of {g2 + b2} ({round(100 * g2 / (g2 + b2))}%)", "tc", "middle")
    return f.svg()


@diagram("scan_chain")
def scan_chain():
    f = Fig(800, 250, "Scan design: in test mode each flip-flop's input multiplexer connects the flip-flops into one long shift register")
    xs = [100, 330, 560]
    prev = None
    for i, x in enumerate(xs):
        m = f.mux(x, 60, 2, 60, labels=("0", "1"))
        p = f.dff(x + 70, 60, w=60, d="D", q="Q", qb=None)
        f.line([m["out"], (x + 50, m["out"][1]), (x + 50, p["D"][1]), p["D"]])
        f.line([(x - 40, 40), (x - 40, m["ins"][0][1]), m["ins"][0]])
        f.text(x - 36, 34, "from logic", "tcs")
        if prev is None:
            f.line([(30, m["ins"][1][1]), m["ins"][1]], "hw")
            f.text(30, m["ins"][1][1] - 7, "scan\\_in", "tcs tcol")
        else:
            f.line([prev, (prev[0] + 30, prev[1]), (prev[0] + 30, 160), (x - 20, 160), (x - 20, m["ins"][1][1]), m["ins"][1]], "hw")
        f.line([m["sel"], (m["sel"][0], 200)])
        f.dot(m["sel"][0], 200)
        f.dot(x + 150, p["Q"][1])
        f.line([p["Q"], (x + 150, p["Q"][1]), (x + 150, 40)])
        f.text(x + 146, 34, "to logic", "tcs", "end")
        prev = (x + 150, p["Q"][1])
    f.line([prev, (prev[0] + 30, prev[1]), (prev[0] + 30, 160), (770, 160)], "hw")
    f.text(770, 152, "scan\\_out", "tcs tcol", "end")
    f.line([(40, 200), (xs[-1] + 17, 200)])
    f.text(36, 204, "scan\\_enable", "tcs", "end") if False else f.text(40, 194, "scan\\_enable", "tcs")
    f.text(400, 238, "test mode: shift a pattern in, pulse one functional clock, shift the captured results out", "tm", "middle")
    return f.svg()


@diagram("thermal_chain")
def thermal_chain():
    f = Fig(780, 230, "Heat flow from the silicon junction to the ambient air through a chain of thermal resistances")
    nodes = (("junction", 80), ("case", 280), ("heatsink", 480), ("ambient", 680))
    for name, x in nodes:
        f.dot(x, 110, 4)
        f.text(x, 92, name, "tb", "middle")
    temps = ("T_{J}", "T_{C}", "T_{S}", "T_{A}")
    for (name, x), t in zip(nodes, temps):
        f.text(x, 140, t, "tc", "middle")
    for (n1, x1), (n2, x2), lab in zip(nodes, nodes[1:], ("θ_{JC}", "θ_{CS} (thermal paste)", "θ_{SA} (heatsink, fan)")):
        f.resistor(x1, 110, x2, 110, None)
        f.text((x1 + x2) / 2, 80, lab, "tcs", "middle")
    f.line([(80, 60), (80, 104)], "aw", end="aha")
    f.text(86, 52, "P watts generated", "tcs ta")
    f.text(390, 190, "T_{J} = T_{A} + P × (θ_{JC} + θ_{CS} + θ_{SA})   — the thermal analog of Ohm's law: ΔT = P·θ", "tc", "middle")
    return f.svg()
