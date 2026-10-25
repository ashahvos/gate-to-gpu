"""Part II diagrams: gates, Boolean algebra, two-level logic, K-maps, decoders/muxes, adders and ALUs."""
from dlib import Fig, diagram, fmt

LOOPC = ["hw", "gw", "mw", "rw"]


@diagram("gate_symbols")
def gate_symbols():
    f = Fig(720, 300, "Symbols, names and expressions of the eight basic logic gates")
    gates = [("BUF", "Y = A"), ("NOT", "Y = A′"), ("AND", "Y = A·B"), ("OR", "Y = A + B"),
             ("XOR", "Y = A ⊕ B"), ("NAND", "Y = (A·B)′"), ("NOR", "Y = (A + B)′"), ("XNOR", "Y = (A ⊕ B)′")]
    for k, (g, ex) in enumerate(gates):
        cx = 18 + (k % 4) * 176
        cy = 14 + (k // 4) * 140
        one = g in ("BUF", "NOT")
        gy = cy + 26 if not one else cy + 31
        p = f.gate(g, cx + 46, gy, 2 if not one else 1)
        for i, (px, py) in enumerate(p["ins"]):
            f.line([(cx + 16, py), (px, py)])
            f.text(cx + 8, py + 4, "AB"[i] if not one else "A", "tc", "middle")
        ox, oy = p["out"]
        f.line([(ox, oy), (cx + 150, oy)])
        f.text(cx + 158, oy + 4, "Y", "tc", "middle")
        f.text(cx + 82, cy + 98, g, "tb", "middle")
        f.text(cx + 82, cy + 116, ex, "tc", "middle")
    return f.svg()


@diagram("demorgan_gates")
def demorgan_gates():
    f = Fig(640, 230, "De Morgan equivalents: a NAND is an OR with inverted inputs, and a NOR is an AND with inverted inputs")
    rows = [("NAND", "OR", "(A·B)′  =  A′ + B′"), ("NOR", "AND", "(A + B)′  =  A′·B′")]
    for r, (g1, g2, eq) in enumerate(rows):
        y = 30 + r * 100
        p = f.gate(g1, 70, y, 2)
        for i, (px, py) in enumerate(p["ins"]):
            f.line([(30, py), (px, py)])
            f.text(22, py + 4, "AB"[i], "tc", "middle")
        f.line([p["out"], (180, p["out"][1])])
        f.text(222, y + 25, "≡", "tL", "middle")
        q = f.gate(g2, 300, y, 2, inv_in=(0, 1))
        for i, (px, py) in enumerate(q["ins"]):
            f.line([(260, py), (px, py)])
            f.text(252, py + 4, "AB"[i], "tc", "middle")
        f.line([q["out"], (400, q["out"][1])])
        f.text(430, y + 25, eq, "tcb")
    f.text(320, 222, "bubble = inversion; moving a bubble through a gate swaps AND and OR", "tm", "middle")
    return f.svg()


@diagram("nand_universal")
def nand_universal():
    f = Fig(800, 190, "NOT, AND and OR built from NAND gates only")
    # NOT
    p = f.gate("NAND", 60, 40, 2)
    f.line([(20, 70), (40, 70)])
    f.dot(40, 70)
    f.line([(40, 70), (40, p["ins"][0][1]), p["ins"][0]])
    f.line([(40, 70), (40, p["ins"][1][1]), p["ins"][1]])
    f.text(14, 74, "A", "tc", "middle")
    f.line([p["out"], (150, p["out"][1])])
    f.text(158, 64, "A′", "tc")
    f.text(85, 150, "NOT: A NAND A", "tb", "middle")
    # AND
    p1 = f.gate("NAND", 240, 40, 2)
    for i, (px, py) in enumerate(p1["ins"]):
        f.line([(210, py), (px, py)])
        f.text(202, py + 4, "AB"[i], "tc", "middle")
    p2 = f.gate("NAND", 340, 40, 2)
    ox, oy = p1["out"]
    f.line([(ox, oy), (322, oy)])
    f.dot(322, oy)
    f.line([(322, oy), (322, p2["ins"][0][1]), p2["ins"][0]])
    f.line([(322, oy), (322, p2["ins"][1][1]), p2["ins"][1]])
    f.line([p2["out"], (440, p2["out"][1])])
    f.text(446, 64, "AB", "tc")
    f.text(320, 150, "AND: NAND, then NAND as inverter", "tb", "middle")
    # OR
    a = f.gate("NAND", 540, 14, 2)
    b = f.gate("NAND", 540, 84, 2)
    for g, lab, yy in ((a, "A", 34), (b, "B", 104)):
        f.line([(510, yy), (520, yy)])
        f.dot(520, yy)
        f.line([(520, yy), (520, g["ins"][0][1]), g["ins"][0]])
        f.line([(520, yy), (520, g["ins"][1][1]), g["ins"][1]])
        f.text(502, yy + 4, lab, "tc", "middle")
    c = f.gate("NAND", 650, 50, 2)
    f.line([a["out"], (630, a["out"][1]), (630, c["ins"][0][1]), c["ins"][0]])
    f.line([b["out"], (630, b["out"][1]), (630, c["ins"][1][1]), c["ins"][1]])
    f.line([c["out"], (735, c["out"][1])])
    f.text(742, c["out"][1] + 4, "A + B", "tc")
    f.text(620, 172, "OR: (A′·B′)′ = A + B", "tb", "middle")
    return f.svg()


@diagram("xor_nand")
def xor_nand():
    f = Fig(600, 215, "A two-input XOR built from four NAND gates")
    n1 = f.gate("NAND", 160, 90)
    n2 = f.gate("NAND", 320, 40)
    n3 = f.gate("NAND", 320, 140)
    n4 = f.gate("NAND", 460, 90)
    f.text(40, 46, "A", "tb", "end")
    f.text(40, 186, "B", "tb", "end")
    f.line([(46, 50), n2["ins"][0]])
    f.dot(100, 50)
    f.line([(100, 50), (100, n1["ins"][0][1]), n1["ins"][0]])
    f.line([(46, 170), n3["ins"][1]])
    f.dot(120, 170)
    f.line([(120, 170), (120, n1["ins"][1][1]), n1["ins"][1]])
    ox, oy = n1["out"]
    f.line([(ox, oy), (260, oy)])
    f.dot(260, oy)
    f.line([(260, oy), (260, n2["ins"][1][1]), n2["ins"][1]])
    f.line([(260, oy), (260, n3["ins"][0][1]), n3["ins"][0]])
    f.line([n2["out"], (420, n2["out"][1]), (420, n4["ins"][0][1]), n4["ins"][0]])
    f.line([n3["out"], (420, n3["out"][1]), (420, n4["ins"][1][1]), n4["ins"][1]])
    f.line([n4["out"], (575, n4["out"][1])])
    f.text(582, 114, "Y", "tb")
    for g, lab in ((n1, "N1 = (AB)′"), (n2, "N2 = (A·N1)′"), (n3, "N3 = (B·N1)′"), (n4, "Y = (N2·N3)′")):
        x, y = g["ins"][0]
        f.text(x + 4, y - 16, lab, "tcs")
    return f.svg()


def _two_level(f, px, kind):
    """kind: 'andor', 'mid', 'nandnand'. Draws F = AB + CD in a 230-wide panel."""
    first = {"andor": "AND", "mid": "NAND", "nandnand": "NAND", "orand": "OR", "midpos": "NOR", "nornor": "NOR"}[kind]
    g1 = f.gate(first, px + 50, 30)
    g2 = f.gate(first, px + 50, 110)
    labs = "ABCD"
    for k, g in enumerate((g1, g2)):
        for i, (x, y) in enumerate(g["ins"]):
            f.line([(px + 24, y), (x, y)])
            f.text(px + 16, y + 4, labs[2 * k + i], "tc", "middle")
    if kind == "andor":
        o = f.gate("OR", px + 140, 70)
    elif kind == "mid":
        o = f.gate("OR", px + 140, 70, inv_in=(0, 1))
    elif kind == "nandnand":
        o = f.gate("NAND", px + 140, 70)
    elif kind == "orand":
        o = f.gate("AND", px + 140, 70)
    elif kind == "midpos":
        o = f.gate("AND", px + 140, 70, inv_in=(0, 1))
    else:
        o = f.gate("NOR", px + 140, 70)
    f.line([g1["out"], (px + 122, g1["out"][1]), (px + 122, o["ins"][0][1]), o["ins"][0]])
    f.line([g2["out"], (px + 122, g2["out"][1]), (px + 122, o["ins"][1][1]), o["ins"][1]])
    f.line([o["out"], (px + 218, o["out"][1])])
    f.text(px + 224, o["out"][1] + 4, "F", "tb")


@diagram("sop_nand")
def sop_nand():
    f = Fig(790, 225, "F = AB + CD as AND-OR logic, with a pair of bubbles added on each internal wire, and as NAND-NAND logic")
    for k, (kind, cap) in enumerate((("andor", "AND-OR"), ("mid", "add bubble pairs"), ("nandnand", "NAND-NAND"))):
        px = 4 + k * 266
        _two_level(f, px, kind)
        f.text(px + 120, 205, cap, "tb", "middle")
        if k < 2:
            f.text(px + 252, 96, "≡", "tL", "middle")
    return f.svg()


@diagram("pos_nor")
def pos_nor():
    f = Fig(790, 225, "F = (A + B)(C + D) as OR-AND logic, with bubble pairs added, and as NOR-NOR logic")
    for k, (kind, cap) in enumerate((("orand", "OR-AND"), ("midpos", "add bubble pairs"), ("nornor", "NOR-NOR"))):
        px = 4 + k * 266
        _two_level(f, px, kind)
        f.text(px + 120, 205, cap, "tb", "middle")
        if k < 2:
            f.text(px + 252, 96, "≡", "tL", "middle")
    return f.svg()


# ---------------- Karnaugh maps ----------------
GRAY = [0, 1, 3, 2]


def _kmap(f, x0, y0, n, ones=(), dcs=(), loops=(), names=None, cell=48, show_idx=True, values=None, idx_off=0):
    """Draw an n-variable K-map (2..4) at (x0, y0) = top-left of the cell grid.
    loops: list of dicts {m: [minterms], cls: 'hw', dash: bool}."""
    if n == 2:
        rows, cols = [0, 1], [0, 1]
        rl, cl = ["0", "1"], ["0", "1"]
        names = names or ("A", "B")
        corner = (names[0], names[1])
        idx = lambda r, c: r * 2 + c  # noqa: E731
    elif n == 3:
        rows, cols = [0, 1], GRAY
        rl, cl = ["0", "1"], ["00", "01", "11", "10"]
        names = names or ("A", "BC")
        corner = (names[0], names[1])
        idx = lambda r, c: r * 4 + c  # noqa: E731
    else:
        rows, cols = GRAY, GRAY
        rl, cl = ["00", "01", "11", "10"], ["00", "01", "11", "10"]
        names = names or ("AB", "CD")
        corner = (names[0], names[1])
        idx = lambda r, c: r * 4 + c  # noqa: E731
    nr, nc = len(rows), len(cols)
    W, H = nc * cell, nr * cell
    # corner label
    f.line([(x0 - 34, y0 - 30), (x0, y0)], "wt")
    f.text(x0 - 30, y0 - 4, corner[0], "tcb")
    f.text(x0 - 6, y0 - 22, corner[1], "tcb", "end")
    for j, lab in enumerate(cl):
        f.text(x0 + j * cell + cell / 2, y0 - 8, lab, "tc", "middle")
    for i, lab in enumerate(rl):
        f.text(x0 - 8, y0 + i * cell + cell / 2 + 4, lab, "tc", "end")
    for i, r in enumerate(rows):
        for j, c in enumerate(cols):
            m = idx(r, c)
            cx, cy = x0 + j * cell, y0 + i * cell
            v = "1" if m in ones else ("X" if m in dcs else "0")
            if values is not None:
                v = values.get(m, v)
            f.rect(cx, cy, cell, cell, "ba" if v == "1" else "b", 0)
            f.text(cx + cell / 2, cy + cell / 2 + 6, v, "tc" if v != "1" else "ta", "middle", extra=' style="font-size:15px"')
            if show_idx:
                f.text(cx + 4, cy + 12, str(m + idx_off), "tcs", extra=' style="font-size:9.5px;fill:var(--ink-2)"')
    # loops
    cid = f"{f.id}-km{int(x0)}"
    f.defs.append(f'<clipPath id="{cid}"><rect x="{x0 - 2}" y="{y0 - 2}" width="{W + 4}" height="{H + 4}"/></clipPath>')
    pos = {}
    for i, r in enumerate(rows):
        for j, c in enumerate(cols):
            pos[idx(r, c)] = (i, j)

    def intervals(vals, N):
        vals = sorted(set(vals))
        if len(vals) == N:
            return [(0, N - 1, False, False)]
        if vals[-1] - vals[0] + 1 == len(vals):
            return [(vals[0], vals[-1], False, False)]
        lo = [v for v in vals if v < N / 2]
        hi = [v for v in vals if v >= N / 2]
        return [(lo[0], lo[-1], True, False), (hi[0], hi[-1], False, True)]
    for k, lp in enumerate(loops):
        ms = lp["m"]
        rs = [pos[m][0] for m in ms]
        cs = [pos[m][1] for m in ms]
        inset = 4 + 4 * (k % 4)
        cls = lp.get("cls", LOOPC[k % 4])
        sty = "fill:none" + (";stroke-dasharray:6 4" if lp.get("dash") else "")
        for (r0, r1, rwl, rwh) in intervals(rs, nr):
            for (c0, c1, cwl, cwh) in intervals(cs, nc):
                x1 = x0 + c0 * cell + inset - (cell * 0.6 if cwl else 0)
                x2 = x0 + (c1 + 1) * cell - inset + (cell * 0.6 if cwh else 0)
                y1 = y0 + r0 * cell + inset - (cell * 0.6 if rwl else 0)
                y2 = y0 + (r1 + 1) * cell - inset + (cell * 0.6 if rwh else 0)
                f.add(f'<rect class="{cls}" x="{fmt(x1)}" y="{fmt(y1)}" width="{fmt(x2 - x1)}" height="{fmt(y2 - y1)}" rx="14" '
                      f'clip-path="url(#{cid})" style="{sty}"/>')
    return W, H


@diagram("kmap")
def kmap(n=4, ones=(), dcs=(), loops=(), terms=(), names=None, label="Karnaugh map", result=None, cell=48):
    nr = 2 if n <= 3 else 4
    nc = 2 if n == 2 else 4
    W = 60 + nc * cell + 260
    H = 50 + nr * cell + 30
    f = Fig(W, H, label)
    x0, y0 = 60, 46
    lps = [{"m": l["m"], "cls": l.get("cls", LOOPC[k % 4]), "dash": l.get("dash", False)} if isinstance(l, dict) else {"m": list(l), "cls": LOOPC[k % 4]}
           for k, l in enumerate(loops)]
    _kmap(f, x0, y0, n, ones, dcs, lps, names, cell)
    tx = x0 + nc * cell + 30
    ty = y0 + 10
    for k, t in enumerate(terms):
        cls = LOOPC[k % 4]
        f.line([(tx, ty + k * 26 - 4), (tx + 22, ty + k * 26 - 4)], cls)
        f.text(tx + 30, ty + k * 26, t, "tc")
    if result:
        f.text(tx, ty + len(terms) * 26 + 16, result, "tcb")
    return f.svg()


@diagram("kmap5")
def kmap5(ones=(), dcs=(), loops0=(), loops1=(), label="Five-variable K-map drawn as two four-variable maps"):
    f = Fig(700, 290, label)
    for k, (x0, aval, lps) in enumerate(((80, 0, loops0), (420, 1, loops1))):
        o = [m - 16 * aval for m in ones if (m >> 4) == aval]
        d = [m - 16 * aval for m in dcs if (m >> 4) == aval]
        _kmap(f, x0, 70, 4, o, d, [{"m": [m - 16 * aval for m in l], "cls": LOOPC[i % 4]} for i, l in enumerate(lps)], ("BC", "DE"), 46,
              idx_off=16 * aval)
        f.text(x0 + 92, 24, f"A = {aval}", "tb", "middle")
    return f.svg()


# ---------------- decoders, muxes, buses ----------------
@diagram("decoder24")
def decoder24():
    f = Fig(440, 420, "Gate-level 2-to-4 decoder: each AND gate recognizes one input combination")
    # inputs and rails
    f.text(14, 44, "A1", "tb")
    f.line([(36, 40), (90, 40), (90, 400)])
    f.dot(60, 40)
    f.line([(60, 40), (60, 70), (70, 70)])
    n1 = f.gate("NOT", 70, 55)
    f.line([n1["out"], (120, 70), (120, 400)])
    f.text(14, 124, "A0", "tb")
    f.line([(36, 120), (150, 120), (150, 400)])
    f.dot(60, 120)
    f.line([(60, 120), (60, 150), (70, 150)])
    n0 = f.gate("NOT", 70, 135)
    f.line([n0["out"], (180, 150), (180, 400)])
    for x, lab in ((90, "A1"), (120, "A1′"), (150, "A0"), (180, "A0′")):
        f.text(x, 410, lab, "tcs", "middle")
    combos = [((120, 180), "Y0 = A1′A0′"), ((120, 150), "Y1 = A1′A0"), ((90, 180), "Y2 = A1A0′"), ((90, 150), "Y3 = A1A0")]
    for k, ((ra, rb), lab) in enumerate(combos):
        y = 190 + 52 * k
        g = f.gate("AND", 240, y)
        for (rx, (px, py)) in zip((ra, rb), g["ins"]):
            f.dot(rx, py)
            f.line([(rx, py), (px, py)])
        f.line([g["out"], (330, g["out"][1])])
        f.text(336, g["out"][1] + 4, lab, "tc")
    return f.svg()


@diagram("mux4_tree")
def mux4_tree():
    f = Fig(460, 290, "A 4-to-1 multiplexer built from three 2-to-1 multiplexers")
    m0 = f.mux(140, 20, 2, 64)
    m1 = f.mux(140, 150, 2, 64)
    m2 = f.mux(300, 85, 2, 64)
    for k, (m, labs) in enumerate(((m0, ("I0", "I1")), (m1, ("I2", "I3")))):
        for (px, py), lab in zip(m["ins"], labs):
            f.line([(118, py), (px, py)])
            f.text(112, py + 4, lab, "tc", "end")
    f.line([m0["out"], (240, m0["out"][1]), (240, m2["ins"][0][1]), m2["ins"][0]])
    f.line([m1["out"], (240, m1["out"][1]), (240, m2["ins"][1][1]), m2["ins"][1]])
    sx = m0["sel"][0]
    f.line([(48, 250), (sx, 250), (sx, m1["sel"][1])])
    f.dot(86, 250)
    f.line([(86, 250), (86, 120), (sx, 120), (sx, m0["sel"][1])])
    f.text(42, 254, "S0", "tb", "end")
    f.line([m2["sel"], (m2["sel"][0], 270)])
    f.text(m2["sel"][0] + 8, 274, "S1", "tb")
    f.line([m2["out"], (410, m2["out"][1])])
    f.text(416, m2["out"][1] + 4, "Y", "tb")
    f.text(300, 40, "Y = I[S1 S0]", "tcb")
    return f.svg()


@diagram("decoder_tree")
def decoder_tree():
    f = Fig(600, 330, "A 3-to-8 decoder built from a 1-to-2 decoder that enables one of two 2-to-4 decoders")
    f.block(60, 130, 90, 70, "1:2 dec", None, "b")
    f.text(40, 160, "A2", "tb", "end")
    f.line([(44, 156), (60, 156)])
    f.text(70, 216, "EN", "tcs")
    f.line([(105, 200), (105, 240)])
    f.text(105, 256, "enable in", "tm", "middle")
    for k, y in enumerate((40, 200)):
        f.block(300, y, 110, 100, "2:4 dec", None, "b")
        f.line([(150, 150 + 30 * k), (230, 150 + 30 * k), (230, y + 85), (300, y + 85)])
        f.text(160, 145 + 30 * k, f"Q{k}", "tcs")
        f.text(306, y + 81, "EN", "tcs")
        f.line([(270, y + 25), (300, y + 25)])
        f.line([(270, y + 50), (300, y + 50)])
        f.text(264, y + 29, "A1", "tcs", "end")
        f.text(264, y + 54, "A0", "tcs", "end")
        for j in range(4):
            yy = y + 14 + 24 * j
            f.line([(410, yy), (450, yy)])
            f.text(456, yy + 4, f"Y{4 * k + j}", "tc")
    f.text(470, 26, "A2 = 0 → upper bank", "tm")
    f.text(470, 318, "A2 = 1 → lower bank", "tm")
    return f.svg()


@diagram("tristate_bus")
def tristate_bus():
    f = Fig(640, 230, "Three tri-state drivers share one bus wire; a decoder guarantees that at most one is enabled")
    f.line([(60, 150), (600, 150)], "hw")
    f.text(606, 154, "bus", "tb")
    for k in range(3):
        x = 110 + k * 160
        g = f.gate("TRI", x, 70)
        f.line([(x - 30, g["ins"][0][1]), g["ins"][0]])
        f.text(x - 36, g["ins"][0][1] + 4, f"D{k}", "tc", "end")
        f.line([g["out"], (g["out"][0] + 16, g["out"][1]), (g["out"][0] + 16, 150)])
        f.dot(g["out"][0] + 16, 150)
        ex, ey = g["en"]
        f.line([(ex, ey), (ex, 30)])
        f.text(ex, 24, f"EN{k}", "tcs", "middle")
    f.block(470, 175, 120, 40, "receiver", None, "bs")
    f.line([(530, 150), (530, 175)])
    f.dot(530, 150)
    f.text(60, 200, "EN = 1: output drives D", "tm")
    f.text(60, 218, "EN = 0: output is Z (disconnected)", "tm")
    return f.svg()


# ---------------- adders and ALUs ----------------
@diagram("full_adder")
def full_adder():
    f = Fig(580, 300, "Gate-level full adder: two XOR gates form the sum, two AND gates and an OR gate form the carry")
    x1 = f.gate("XOR", 140, 40)
    x2 = f.gate("XOR", 310, 100)
    a1 = f.gate("AND", 310, 180)
    a2 = f.gate("AND", 310, 240)
    o = f.gate("OR", 430, 210)
    f.text(20, 54, "A", "tb")
    f.text(20, 74, "B", "tb")
    f.text(14, 204, "Cin", "tb")
    f.line([(36, 50), x1["ins"][0]])
    f.line([(36, 70), x1["ins"][1]])
    f.dot(100, 50)
    f.line([(100, 50), (100, a1["ins"][0][1]), a1["ins"][0]])
    f.dot(120, 70)
    f.line([(120, 70), (120, a1["ins"][1][1]), a1["ins"][1]])
    xo = x1["out"]
    f.line([xo, (250, xo[1]), (250, x2["ins"][0][1]), x2["ins"][0]])
    f.dot(250, x2["ins"][0][1])
    f.line([(250, x2["ins"][0][1]), (250, a2["ins"][0][1]), a2["ins"][0]])
    f.line([(48, 200), (270, 200), (270, x2["ins"][1][1]), x2["ins"][1]])
    f.dot(270, 200)
    f.line([(270, 200), (270, a2["ins"][1][1]), a2["ins"][1]])
    f.text(256, 56, "A ⊕ B", "tcs")
    f.line([x2["out"], (540, x2["out"][1])])
    f.text(546, x2["out"][1] + 4, "S", "tb")
    f.line([a1["out"], (400, a1["out"][1]), (400, o["ins"][0][1]), o["ins"][0]])
    f.line([a2["out"], (400, a2["out"][1]), (400, o["ins"][1][1]), o["ins"][1]])
    f.line([o["out"], (540, o["out"][1])])
    f.text(546, o["out"][1] + 4, "Cout", "tb")
    f.text(368, 176, "AB", "tcs")
    f.text(368, 236, "(A⊕B)Cin", "tcs")
    return f.svg()


@diagram("ripple4")
def ripple4():
    f = Fig(720, 200, "A 4-bit ripple-carry adder: each full adder's carry out feeds the next column's carry in")
    for i in range(4):
        x = 520 - i * 150
        f.block(x, 60, 100, 70, f"FA {i}", None, "b")
        f.line([(x + 30, 22), (x + 30, 60)])
        f.line([(x + 70, 22), (x + 70, 60)])
        f.text(x + 30, 16, f"A{i}", "tc", "middle")
        f.text(x + 70, 16, f"B{i}", "tc", "middle")
        f.line([(x + 50, 130), (x + 50, 168)])
        f.text(x + 50, 184, f"S{i}", "tc", "middle")
        if i < 3:
            f.line([(x, 95), (x - 48, 95)], "hw", end="ahc")
            f.text(x - 25, 88, f"C{i + 1}", "tcb", "middle")
    f.line([(690, 95), (622, 95)], "hw", end="ahc")
    f.text(660, 88, "C0", "tcb", "middle")
    f.line([(70, 95), (24, 95)], "hw", end="ahc")
    f.text(46, 88, "C4", "tcb", "middle")
    return f.svg()


@diagram("addsub")
def addsub():
    f = Fig(780, 360, "A 4-bit adder/subtractor: XOR gates invert B when SUB = 1, and SUB also supplies the carry into bit 0")
    sub_y = 136
    for i in range(4):
        x = 560 - i * 150
        f.block(x, 180, 100, 70, f"FA {i}", None, "b")
        # A input
        f.line([(x + 22, 20), (x + 22, 180)])
        f.text(x + 22, 14, f"A{i}", "tc", "middle")
        # B through XOR
        g = f.gate("XOR", x + 44, 76)
        f.line([(x + 36, 20), (x + 36, g["ins"][0][1]), g["ins"][0]])
        f.text(x + 38, 14, f"B{i}", "tc", "start")
        f.dot(x + 40, sub_y)
        f.line([(x + 40, sub_y), (x + 40, g["ins"][1][1]), g["ins"][1]])
        ox, oy = g["out"]
        f.line([(ox, oy), (x + 112, oy), (x + 112, 166), (x + 78, 166), (x + 78, 180)])
        f.line([(x + 50, 250), (x + 50, 290)])
        f.text(x + 50, 306, f"S{i}", "tc", "middle")
        if i < 3:
            f.line([(x, 215), (x - 48, 215)], "hw", end="ahc")
            f.text(x - 26, 208, f"C{i + 1}", "tcb", "middle")
    f.line([(100, sub_y), (720, sub_y), (720, 215), (662, 215)], "w", end="ah")
    f.text(728, sub_y + 4, "SUB", "tb")
    f.text(692, 230, "C0", "tcb")
    # overflow
    f.line([(110, 215), (64, 215)], "hw", end="ahc")
    f.text(58, 220, "C4", "tcb", "end")
    f.text(110, 334, "V = C3 ⊕ C4 (signed overflow)", "tcb")
    f.text(110, 352, "C = C4; after a subtraction, C4 = 0 means a borrow (A < B unsigned)", "tm")
    return f.svg()


@diagram("cla_block")
def cla_block():
    f = Fig(720, 300, "A 4-bit carry-lookahead adder: every carry is computed directly from generate and propagate signals")
    for i in range(4):
        x = 500 - i * 150
        f.rect(x, 40, 120, 54, "b", 5)
        f.text(x + 60, 62, f"G{i} = A{i}·B{i}", "tcs", "middle")
        f.text(x + 60, 80, f"P{i} = A{i} ⊕ B{i}", "tcs", "middle")
        f.line([(x + 60, 94), (x + 60, 130)])
        f.rect(x, 210, 120, 44, "b", 5)
        f.text(x + 60, 236, f"S{i} = P{i} ⊕ C{i}", "tcs", "middle")
        f.line([(x + 60, 254), (x + 60, 284)])
        f.text(x + 60, 296, f"S{i}", "tcs", "middle")
        f.line([(x + 84, 170), (x + 84, 208)], "hw", end="ahc")
        f.text(x + 90, 196, f"C{i}", "tcb")
        f.line([(x + 30, 170), (x + 30, 210)], "wt")
        f.text(x + 24, 196, f"P{i}", "tcs", "end")
    f.rect(40, 130, 600, 40, "bs", 5)
    f.text(340, 155, "carry-lookahead logic: C1 … C4 from the G, P and C0 signals in two gate levels", "tc", "middle")
    f.line([(690, 150), (642, 150)], "w", end="ah")
    f.text(696, 154, "C0", "tcb")
    return f.svg()


@diagram("alu_block")
def alu_block():
    f = Fig(680, 360, "An ALU that shares one adder: input muxes steer X, X′, Y, Y′ or 0 into it, and an output mux picks the arithmetic or the logic result")
    mx = f.mux(60, 40, 2, 60)
    my = f.mux(240, 30, 3, 84)
    for (px, py), lab in zip(mx["ins"], ("X", "X′")):
        f.line([(30, py), (px, py)])
        f.text(24, py + 4, lab, "tc", "end")
    for (px, py), lab in zip(my["ins"], ("Y", "Y′", "0")):
        f.line([(210, py), (px, py)])
        f.text(204, py + 4, lab, "tc", "end")
    f.block(110, 150, 220, 60, "adder", "A + B + Cin", "b")
    f.line([mx["out"], (150, mx["out"][1]), (150, 150)])
    f.line([my["out"], (290, my["out"][1]), (290, 150)])
    f.text(156, 146, "A", "tcs")
    f.text(296, 146, "B", "tcs")
    f.line([(380, 180), (332, 180)], "w", end="ah")
    f.text(386, 184, "Cin", "tcs")
    f.line([mx["sel"], (mx["sel"][0], 124)])
    f.text(mx["sel"][0] - 6, 126, "S0", "tcs", "end")
    f.line([my["sel"], (my["sel"][0], 132)])
    f.text(my["sel"][0] - 6, 134, "S1 S2", "tcs", "end")
    f.block(420, 150, 170, 60, "logic unit", "AND, OR, XOR of X, Y", "b")
    om = f.mux(520, 256, 2, 64, labels=("1", "0"))
    f.line([(505, 210), (505, om["ins"][0][1]), om["ins"][0]])
    f.line([(220, 210), (220, om["ins"][1][1]), om["ins"][1]])
    f.line([om["out"], (620, om["out"][1])])
    f.text(626, om["out"][1] + 4, "result", "tb")
    f.line([om["sel"], (om["sel"][0], 340)])
    f.text(om["sel"][0] + 6, 344, "S3", "tcs")
    for i, t in enumerate(("S0 = 1: A gets X′", "S1 = 1: B gets 0", "S2 = 1: B gets Y′", "S3 = 1: logic result out")):
        f.text(30, 240 + 16 * i, t, "tm")
    for i, t in enumerate(("Flags: C, V from the adder,", "Z = NOR of the result bits,", "N = the result's MSB")):
        f.text(30, 312 + 16 * i, t, "tm")
    return f.svg()


@diagram("barrel4")
def barrel4():
    f = Fig(600, 330, "A 4-bit logical right shifter with two stages of 2-to-1 muxes: stage 1 shifts by 1 when s0 = 1, stage 2 shifts by 2 when s1 = 1")
    ys = [30, 100, 170, 240]
    x1, x2 = 140, 320
    m1 = [f.mux(x1, y, 2, 52) for y in ys]
    m2 = [f.mux(x2, y, 2, 52) for y in ys]
    for i in range(4):
        b = 3 - i
        yin = m1[i]["ins"][0][1]
        f.text(30, yin + 4, f"d{b}", "tc", "end")
        f.line([(38, yin), m1[i]["ins"][0]])
        if i > 0:
            ysrc = m1[i - 1]["ins"][0][1]
            f.dot(96, ysrc)
            f.line([(96, ysrc), (96, m1[i]["ins"][1][1]), m1[i]["ins"][1]], "wt")
        else:
            f.line([(112, m1[i]["ins"][1][1]), m1[i]["ins"][1]], "wt")
            f.text(108, m1[i]["ins"][1][1] + 4, "0", "tcs", "end")
        f.line([m1[i]["sel"], (m1[i]["sel"][0], m1[i]["sel"][1] + 12)], "wt")
        f.text(m1[i]["sel"][0] + 5, m1[i]["sel"][1] + 14, "s0", "tcs")
    for i in range(4):
        b = 3 - i
        o = m1[i]["out"]
        f.line([o, (230, o[1]), (230, m2[i]["ins"][0][1]), m2[i]["ins"][0]])
        if i >= 2:
            oj = m1[i - 2]["out"]
            f.dot(230, oj[1])
            f.line([(230, oj[1]), (270, oj[1]), (270, m2[i]["ins"][1][1]), m2[i]["ins"][1]], "wt")
        else:
            f.line([(292, m2[i]["ins"][1][1]), m2[i]["ins"][1]], "wt")
            f.text(288, m2[i]["ins"][1][1] + 4, "0", "tcs", "end")
        f.line([m2[i]["sel"], (m2[i]["sel"][0], m2[i]["sel"][1] + 12)], "wt")
        f.text(m2[i]["sel"][0] + 5, m2[i]["sel"][1] + 14, "s1", "tcs")
        f.line([m2[i]["out"], (420, m2[i]["out"][1])])
        f.text(426, m2[i]["out"][1] + 4, f"y{b}", "tc")
    f.text(456, 50, "y = d >> (2·s1 + s0)", "tcb")
    f.text(456, 72, "stage 1: mux input 1 takes", "tm")
    f.text(456, 88, "the bit one place above", "tm")
    f.text(456, 112, "stage 2: input 1 takes the", "tm")
    f.text(456, 128, "bit two places above", "tm")
    f.text(456, 152, "vacated bits are filled", "tm")
    f.text(456, 168, "with 0 (logical shift)", "tm")
    return f.svg()
