"""Small schematic/diagram library that emits inline SVG.

All colors come from CSS classes defined in style.css (.dg .w, .b, .bs, ...), so the drawings follow
the page theme. Coordinates are in SVG user units; each Fig sets viewBox="0 0 w h".
Text supports a tiny markup: _{sub}, _x (one char), ^{sup}. Use \\_ for a literal underscore.
"""
import html
import math
import re

REGISTRY = {}
WAVES = {}


def wave(name):
    """Register a function that returns a timing-diagram spec (dict) for <wavegen name=...>."""
    def deco(fn):
        WAVES[name] = fn
        return fn
    return deco


def diagram(name):
    def deco(fn):
        REGISTRY[name] = fn
        return fn
    return deco


def esc(s):
    return html.escape(str(s), quote=True)


def fmt(v):
    if isinstance(v, float):
        s = f"{v:.2f}".rstrip("0").rstrip(".")
        return s if s not in ("-0", "") else "0"
    return str(v)


_tok = re.compile(r"\\_|_\{([^}]*)\}|_(\S)|\^\{([^}]*)\}")


def markup(s):
    """Convert _{..} / _x / ^{..} to tspans; escape everything else."""
    out, pos = [], 0
    for m in _tok.finditer(s):
        out.append(esc(s[pos:m.start()]))
        if m.group(0) == "\\_":
            out.append("_")
        elif m.group(1) is not None or m.group(2) is not None:
            sub = m.group(1) if m.group(1) is not None else m.group(2)
            out.append(f'<tspan baseline-shift="sub" font-size="72%">{esc(sub)}</tspan>')
        else:
            out.append(f'<tspan baseline-shift="super" font-size="72%">{esc(m.group(3))}</tspan>')
        pos = m.end()
    out.append(esc(s[pos:]))
    return "".join(out)


class Fig:
    _n = 0

    def __init__(self, w, h, label):
        Fig._n += 1
        self.id = f"g{Fig._n}"
        self.w, self.h, self.label = w, h, label
        self.el = []
        self.defs = []
        self._markers = set()

    # ---------- basics ----------
    def add(self, s):
        self.el.append(s)

    def marker(self, kind="ah"):
        mid = f"{self.id}-{kind}"
        if kind not in self._markers:
            self._markers.add(kind)
            self.defs.append(
                f'<marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
                f'orient="auto-start-reverse"><path class="{kind}" d="M0 0 L10 5 L0 10 z"/></marker>')
        return f"url(#{mid})"

    def path(self, d, cls="w", end=None, start=None, extra=""):
        m = ""
        if end:
            m += f' marker-end="{self.marker(end)}"'
        if start:
            m += f' marker-start="{self.marker(start)}"'
        self.add(f'<path class="{cls}" d="{d}"{m}{extra}/>')

    def line(self, pts, cls="w", end=None, start=None, extra=""):
        d = "M" + " L".join(f"{fmt(x)} {fmt(y)}" for x, y in pts)
        self.path(d, cls, end, start, extra)

    def hv(self, x1, y1, x2, y2, cls="w", first="h", end=None):
        """Orthogonal two-segment wire."""
        if first == "h":
            pts = [(x1, y1), (x2, y1), (x2, y2)]
        else:
            pts = [(x1, y1), (x1, y2), (x2, y2)]
        self.line(pts, cls, end)

    def text(self, x, y, s, cls="", anchor="start", extra=""):
        c = f' class="{cls}"' if cls else ""
        a = f' text-anchor="{anchor}"' if anchor != "start" else ""
        self.add(f'<text x="{fmt(x)}" y="{fmt(y)}"{c}{a}{extra}>{markup(s)}</text>')

    def rect(self, x, y, w, h, cls="b", rx=4, extra=""):
        self.add(f'<rect class="{cls}" x="{fmt(x)}" y="{fmt(y)}" width="{fmt(w)}" height="{fmt(h)}" rx="{fmt(rx)}"{extra}/>')

    def circle(self, x, y, r, cls="b", extra=""):
        self.add(f'<circle class="{cls}" cx="{fmt(x)}" cy="{fmt(y)}" r="{fmt(r)}"{extra}/>')

    def dot(self, x, y, r=3.3, cls="dot"):
        self.circle(x, y, r, cls)

    def svg(self, min_width=None):
        mw = ""
        if min_width is None:
            min_width = min(self.w, 520)
        if min_width:
            mw = f' style="min-width:{int(min_width)}px"'
        defs = f"<defs>{''.join(self.defs)}</defs>" if self.defs else ""
        return (f'<svg viewBox="0 0 {fmt(self.w)} {fmt(self.h)}" width="{fmt(self.w)}"{mw} role="img" '
                f'aria-label="{esc(self.label)}">{defs}{"".join(self.el)}</svg>')

    # ---------- logic gates ----------
    def gate(self, kind, x, y, n=2, h=None, inv_in=(), label=None, cls="b"):
        """Body top-left at (x, y). Returns {'ins': [(x, y)...], 'out': (x, y)}."""
        kind = kind.upper()
        if kind in ("NOT", "BUF", "TRI"):
            h = h or 30
            w = 30
            yc = y + h / 2
            self.path(f"M{fmt(x)} {fmt(y)} L{fmt(x + w)} {fmt(yc)} L{fmt(x)} {fmt(y + h)} Z", cls)
            ox = x + w
            pins = {"ins": [(x, yc)]}
            if kind == "NOT":
                self.circle(ox + 4.5, yc, 4.5, cls)
                ox += 9
            if kind == "TRI":
                ex = x + w * 0.45
                ey = y + (h / 2) * 0.45
                pins["en"] = (ex, ey)
            pins["out"] = (ox, yc)
            return pins
        h = h or 20 * n
        r = h / 2
        ins_y = [y + 10 + 20 * i for i in range(n)] if h == 20 * n else [y + h * (i + 0.5) / n for i in range(n)]
        pins = {"ins": [], "out": None}
        base = kind.replace("N", "", 1) if kind in ("NAND", "NOR") else kind
        if kind in ("XOR", "XNOR"):
            base = "XOR"
        if base == "AND":
            w = 30 + r
            self.path(f"M{fmt(x)} {fmt(y)} H{fmt(x + 30)} A{fmt(r)} {fmt(r)} 0 0 1 {fmt(x + 30)} {fmt(y + h)} H{fmt(x)} Z", cls)
            ox = x + w
            for yi in ins_y:
                pins["ins"].append((x, yi))
        else:
            off = 8 if base == "XOR" else 0
            bx = x + off
            w = 30 + r
            c = 0.25 * h
            self.path(f"M{fmt(bx)} {fmt(y)} Q{fmt(bx + 0.62 * w)} {fmt(y)} {fmt(bx + w)} {fmt(y + h / 2)} "
                      f"Q{fmt(bx + 0.62 * w)} {fmt(y + h)} {fmt(bx)} {fmt(y + h)} Q{fmt(bx + c)} {fmt(y + h / 2)} {fmt(bx)} {fmt(y)} Z", cls)
            if base == "XOR":
                self.path(f"M{fmt(x)} {fmt(y)} Q{fmt(x + c)} {fmt(y + h / 2)} {fmt(x)} {fmt(y + h)}", "w")
            ox = bx + w
            for yi in ins_y:
                t = (yi - y) / h
                cx = x + 2 * t * (1 - t) * c
                if cx - x > 0.5:
                    self.line([(x, yi), (cx, yi)])
                pins["ins"].append((x, yi))
        if kind in ("NAND", "NOR", "XNOR"):
            self.circle(ox + 4.5, y + h / 2, 4.5, cls)
            ox += 9
        pins["out"] = (ox, y + h / 2)
        for i in inv_in:
            px, py = pins["ins"][i]
            self.circle(px - 4.5, py, 4.5, cls)
            pins["ins"][i] = (px - 9, py)
        if label:
            self.text(x + 14, y + h / 2 + 4, label, "tm")
        return pins

    # ---------- blocks ----------
    def block(self, x, y, w, h, title=None, sub=None, cls="b", rx=5, tcls="tb"):
        self.rect(x, y, w, h, cls, rx)
        if title:
            ty = y + h / 2 + (5 if not sub else -2)
            self.text(x + w / 2, ty, title, tcls, "middle")
        if sub:
            self.text(x + w / 2, y + h / 2 + 15, sub, "tm", "middle")

    def mux(self, x, y, n=2, h=None, w=34, labels=True, cls="b", sel="bottom"):
        h = h or (28 * n + 8)
        inset = min(12, h * 0.18)
        self.path(f"M{fmt(x)} {fmt(y)} L{fmt(x + w)} {fmt(y + inset)} V{fmt(y + h - inset)} L{fmt(x)} {fmt(y + h)} Z", cls)
        ins = []
        for i in range(n):
            yi = y + h * (i + 0.5) / n
            ins.append((x, yi))
            if labels:
                self.text(x + 6, yi + 4, str(labels[i]) if isinstance(labels, (list, tuple)) else str(i), "tcs")
        out = (x + w, y + h / 2)
        if sel == "bottom":
            s = (x + w / 2, y + h - inset / 2)
        else:
            s = (x + w / 2, y + inset / 2)
        return {"ins": ins, "out": out, "sel": s}

    def dff(self, x, y, w=64, h=76, d="D", q="Q", qb="Q′", neg=False, cls="b", extra=(), title=None):
        """Edge-triggered flip-flop box. extra: list of (side, frac, label) pins to add ('top'/'bottom'/'left')."""
        self.rect(x, y, w, h, cls, 3)
        pins = {}
        yd = y + 18
        yc = y + h - 18
        self.text(x + 7, yd + 4.5, d, "tc")
        pins["D"] = (x, yd)
        self.text(x + w - 7, yd + 4.5, q, "tc", "end")
        pins["Q"] = (x + w, yd)
        self.path(f"M{fmt(x)} {fmt(yc - 7)} L{fmt(x + 10)} {fmt(yc)} L{fmt(x)} {fmt(yc + 7)}", "w")
        if neg:
            self.circle(x - 4.5, yc, 4.5, cls)
            pins["CLK"] = (x - 9, yc)
        else:
            pins["CLK"] = (x, yc)
        if qb:
            self.text(x + w - 7, yc + 4.5, qb, "tc", "end")
            pins["QB"] = (x + w, yc)
        for side, frac, lab in extra:
            if side == "top":
                px, py = x + w * frac, y
                self.text(px, py + 14, lab, "tcs", "middle")
            elif side == "bottom":
                px, py = x + w * frac, y + h
                self.text(px, py - 6, lab, "tcs", "middle")
            else:
                px, py = x, y + h * frac
                self.text(px + 7, py + 4, lab, "tcs")
            pins[lab] = (px, py)
        if title:
            self.text(x + w / 2, y - 6, title, "tm", "middle")
        return pins

    # ---------- circuit symbols ----------
    def mosfet(self, x, y, t="n", label=None, cls="w", glabel=None, lab_side="right"):
        """Channel at x; gate lead from x-30. Returns pins g, top, bot."""
        self.path(f"M{fmt(x - 6)} {fmt(y - 13)} V{fmt(y + 13)} M{fmt(x)} {fmt(y - 16)} V{fmt(y + 16)} "
                  f"M{fmt(x)} {fmt(y - 11)} H{fmt(x + 16)} V{fmt(y - 26)} M{fmt(x)} {fmt(y + 11)} H{fmt(x + 16)} V{fmt(y + 26)}", cls)
        if t == "p":
            self.line([(x - 30, y), (x - 15, y)], cls)
            self.circle(x - 10.5, y, 4.5, "b")
        else:
            self.line([(x - 30, y), (x - 6, y)], cls)
        if glabel:
            self.text(x - 35, y + 4.5, glabel, "tb", "end")
        if label:
            if lab_side == "right":
                self.text(x + 24, y + 4, label, "tm")
            else:
                self.text(x - 36, y + 18, label, "tm", "end")
        return {"g": (x - 30, y), "top": (x + 16, y - 26), "bot": (x + 16, y + 26)}

    def ground(self, x, y, cls="w"):
        self.path(f"M{fmt(x)} {fmt(y)} V{fmt(y + 9)} M{fmt(x - 13)} {fmt(y + 9)} H{fmt(x + 13)} M{fmt(x - 8.5)} {fmt(y + 15)} H{fmt(x + 8.5)} M{fmt(x - 4)} {fmt(y + 21)} H{fmt(x + 4)}", cls)

    def supply(self, x, y, label="V_{DD}", cls="w"):
        """Small T-bar supply symbol whose stem goes down from (x, y)."""
        self.path(f"M{fmt(x - 12)} {fmt(y)} H{fmt(x + 12)} M{fmt(x)} {fmt(y)} V{fmt(y + 8)}", cls)
        self.text(x, y - 6, label, "tm", "middle")

    def resistor(self, x1, y1, x2, y2, label=None, cls="w", lab_dx=12, lab_dy=4, zig=6, amp=6):
        L = math.hypot(x2 - x1, y2 - y1)
        ux, uy = (x2 - x1) / L, (y2 - y1) / L
        px, py = -uy, ux
        lead = max(0, (L - 6 * zig * 2) / 2)
        pts = [(x1, y1), (x1 + ux * lead, y1 + uy * lead)]
        seg = (L - 2 * lead) / 12
        for i in range(1, 12):
            s = lead + seg * i
            a = amp if i % 2 else -amp
            if i == 11:
                a = 0
            pts.append((x1 + ux * s + px * a, y1 + uy * s + py * a))
        pts.append((x1 + ux * (L - lead), y1 + uy * (L - lead)))
        pts.append((x2, y2))
        self.line(pts, cls)
        if label:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            self.text(mx + lab_dx, my + lab_dy, label, "tc")

    def capacitor(self, x, y, orient="v", label=None, gap=7, plate=24, cls="w", lab_dx=18):
        """orient 'v': terminals above and below (plates horizontal), centered at (x, y)."""
        g = gap / 2
        if orient == "v":
            self.path(f"M{fmt(x - plate / 2)} {fmt(y - g)} H{fmt(x + plate / 2)} M{fmt(x - plate / 2)} {fmt(y + g)} H{fmt(x + plate / 2)}", cls, extra=' style="stroke-width:2.4"')
            if label:
                self.text(x + lab_dx, y + 4, label, "tc")
            return {"a": (x, y - g), "b": (x, y + g)}
        self.path(f"M{fmt(x - g)} {fmt(y - plate / 2)} V{fmt(y + plate / 2)} M{fmt(x + g)} {fmt(y - plate / 2)} V{fmt(y + plate / 2)}", cls, extra=' style="stroke-width:2.4"')
        if label:
            self.text(x, y - plate / 2 - 6, label, "tc", "middle")
        return {"a": (x - g, y), "b": (x + g, y)}

    def diode(self, x, y, direction="down", led=False, label=None, cls="b", size=16):
        s = size
        if direction == "down":
            self.path(f"M{fmt(x - s / 2)} {fmt(y - s / 2)} H{fmt(x + s / 2)} L{fmt(x)} {fmt(y + s / 2)} Z", cls)
            self.line([(x - s / 2, y + s / 2), (x + s / 2, y + s / 2)], "w")
            a, k = (x, y - s / 2), (x, y + s / 2)
            if led:
                for dy in (-4, 4):
                    self.line([(x + s / 2 + 2, y + dy - 2), (x + s / 2 + 12, y + dy - 10)], "wt", end="ah")
        elif direction == "right":
            self.path(f"M{fmt(x - s / 2)} {fmt(y - s / 2)} V{fmt(y + s / 2)} L{fmt(x + s / 2)} {fmt(y)} Z", cls)
            self.line([(x + s / 2, y - s / 2), (x + s / 2, y + s / 2)], "w")
            a, k = (x - s / 2, y), (x + s / 2, y)
            if led:
                for dx in (-4, 4):
                    self.line([(x + dx - 2, y - s / 2 - 2), (x + dx + 6, y - s / 2 - 12)], "wt", end="ah")
        else:  # up
            self.path(f"M{fmt(x - s / 2)} {fmt(y + s / 2)} H{fmt(x + s / 2)} L{fmt(x)} {fmt(y - s / 2)} Z", cls)
            self.line([(x - s / 2, y - s / 2), (x + s / 2, y - s / 2)], "w")
            a, k = (x, y + s / 2), (x, y - s / 2)
        if label:
            self.text(x + s / 2 + 8, y + 4, label, "tm")
        return {"a": a, "k": k}

    def opamp(self, x, y, w=72, h=76, flip=False, cls="b"):
        """Triangle with inputs on the left. flip=True puts + on top."""
        self.path(f"M{fmt(x)} {fmt(y)} L{fmt(x + w)} {fmt(y + h / 2)} L{fmt(x)} {fmt(y + h)} Z", cls)
        y1, y2 = y + h * 0.3, y + h * 0.7
        top, bot = ("+", "−") if flip else ("−", "+")
        self.text(x + 9, y1 + 5, top, "tb")
        self.text(x + 9, y2 + 5, bot, "tb")
        pins = {"out": (x + w, y + h / 2)}
        if flip:
            pins["plus"], pins["minus"] = (x, y1), (x, y2)
        else:
            pins["minus"], pins["plus"] = (x, y1), (x, y2)
        return pins

    def switch(self, x1, y, x2, closed=False, label=None, cls="w"):
        """Horizontal single-pole switch between (x1, y) and (x2, y)."""
        self.dot(x1, y, 3)
        self.dot(x2, y, 3)
        if closed:
            self.line([(x1, y), (x2, y)], cls)
        else:
            self.line([(x1, y), (x2 - 4, y - 14)], cls)
        if label:
            self.text((x1 + x2) / 2, y + 18, label, "tm", "middle")

    def lamp(self, x, y, r=11, on=False):
        self.circle(x, y, r, "ba" if on else "b")
        d = r * 0.7
        self.path(f"M{fmt(x - d)} {fmt(y - d)} L{fmt(x + d)} {fmt(y + d)} M{fmt(x + d)} {fmt(y - d)} L{fmt(x - d)} {fmt(y + d)}", "wt")

    def battery(self, x, y, label=None):
        """Vertical cell centered at (x, y); + on top."""
        self.path(f"M{fmt(x - 14)} {fmt(y - 4)} H{fmt(x + 14)}", "w", extra=' style="stroke-width:2.2"')
        self.path(f"M{fmt(x - 8)} {fmt(y + 4)} H{fmt(x + 8)}", "w", extra=' style="stroke-width:3.4"')
        self.text(x + 18, y - 2, "+", "tm")
        if label:
            self.text(x + 18, y + 12, label, "tm")
        return {"top": (x, y - 4), "bot": (x, y + 4)}

    # ---------- arrows and labels ----------
    def arrow(self, pts, cls="w", kind="ah", label=None, lx=0, ly=-6, lcls="tm", anchor="middle"):
        self.line(pts, cls, end=kind)
        if label:
            (x1, y1), (x2, y2) = pts[0], pts[-1]
            self.text((x1 + x2) / 2 + lx, (y1 + y2) / 2 + ly, label, lcls, anchor)

    def dim(self, x1, x2, y, label, cls="hw", lcls="tcb", above=True, kind="ahc"):
        """Horizontal dimension line with arrowheads on both ends."""
        self.line([(x1, y), (x2, y)], cls, end=kind, start=kind, extra=' style="stroke-width:1.5"')
        self.text((x1 + x2) / 2, y + (-6 if above else 15), label, lcls + " halo", "middle")

    def vdim(self, x, y1, y2, label, cls="hw", lcls="tcb", side="right", kind="ahc"):
        self.line([(x, y1), (x, y2)], cls, end=kind, start=kind, extra=' style="stroke-width:1.5"')
        self.text(x + (8 if side == "right" else -8), (y1 + y2) / 2 + 4, label, lcls + " halo", "start" if side == "right" else "end")

    # ---------- state machines ----------
    def fsm(self, states, edges, r=30, reset=None):
        """states: {name: dict(x, y, lines=[...], cls='b')}; edges: list of dict(a, b, label, bend, lx, ly, ang (self-loop deg))."""
        ah = "ah"
        for e in edges:
            a, b = states[e["a"]], states[e["b"]]
            lab = e.get("label", "")
            if e["a"] == e["b"]:
                ang = math.radians(e.get("ang", -90))
                spread = math.radians(28)
                p1 = (a["x"] + r * math.cos(ang - spread), a["y"] + r * math.sin(ang - spread))
                p2 = (a["x"] + (r + 2) * math.cos(ang + spread), a["y"] + (r + 2) * math.sin(ang + spread))
                k = r * 2.3
                c1 = (a["x"] + k * math.cos(ang - spread * 1.25), a["y"] + k * math.sin(ang - spread * 1.25))
                c2 = (a["x"] + k * math.cos(ang + spread * 1.25), a["y"] + k * math.sin(ang + spread * 1.25))
                self.path(f"M{fmt(p1[0])} {fmt(p1[1])} C{fmt(c1[0])} {fmt(c1[1])} {fmt(c2[0])} {fmt(c2[1])} {fmt(p2[0])} {fmt(p2[1])}",
                          e.get("cls", "w"), end=ah, extra=' style="stroke-width:1.7"')
                lr = r * 2.05 + e.get("lr", 8)
                tx = a["x"] + lr * math.cos(ang) + e.get("lx", 0)
                ty = a["y"] + lr * math.sin(ang) + 4 + e.get("ly", 0)
                self.text(tx, ty, lab, e.get("lcls", "tcb"), "middle")
                continue
            x1, y1, x2, y2 = a["x"], a["y"], b["x"], b["y"]
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            dx, dy = x2 - x1, y2 - y1
            L = math.hypot(dx, dy)
            px, py = -dy / L, dx / L
            bend = e.get("bend", 0)
            cx, cy = mx + px * bend, my + py * bend
            def toward(sx, sy, tx, ty, rr):
                ddx, ddy = tx - sx, ty - sy
                ll = math.hypot(ddx, ddy)
                return sx + ddx / ll * rr, sy + ddy / ll * rr
            s = toward(x1, y1, cx, cy, r)
            t = toward(x2, y2, cx, cy, r + 2)
            self.path(f"M{fmt(s[0])} {fmt(s[1])} Q{fmt(cx)} {fmt(cy)} {fmt(t[0])} {fmt(t[1])}", e.get("cls", "w"), end=ah,
                      extra=' style="stroke-width:1.7"')
            qx = 0.25 * s[0] + 0.5 * cx + 0.25 * t[0]
            qy = 0.25 * s[1] + 0.5 * cy + 0.25 * t[1]
            sgn = 1 if bend >= 0 else -1
            off = e.get("off", 13)
            tx = qx + px * off * sgn + e.get("lx", 0)
            ty = qy + py * off * sgn + 4 + e.get("ly", 0)
            self.text(tx, ty, lab, e.get("lcls", "tcb"), "middle")
        for name, st in states.items():
            self.circle(st["x"], st["y"], r, st.get("cls", "b"))
            lines = st.get("lines", [name])
            if len(lines) == 1:
                self.text(st["x"], st["y"] + 5, lines[0], "tb", "middle")
            else:
                self.text(st["x"], st["y"] - 2, lines[0], "tb", "middle")
                self.text(st["x"], st["y"] + 14, lines[1], "tcs", "middle")
        if reset:
            name, ang = reset
            st = states[name]
            a = math.radians(ang)
            p_end = (st["x"] + (r + 2) * math.cos(a), st["y"] + (r + 2) * math.sin(a))
            p_start = (st["x"] + (r + 30) * math.cos(a), st["y"] + (r + 30) * math.sin(a))
            self.line([p_start, p_end], "w", end=ah)
            self.text(p_start[0] + 10 * math.cos(a), p_start[1] + 10 * math.sin(a) + 4, "reset", "tm",
                      "middle" if abs(math.cos(a)) < 0.5 else ("start" if math.cos(a) > 0 else "end"))

    # ---------- plots ----------
    def axes(self, x, y, w, h, xr, yr, xticks=(), yticks=(), xlabel=None, ylabel=None, grid=True, logx=False):
        """Returns mapping functions (fx, fy). x, y = top-left of the plot area."""
        def fx(v):
            if logx:
                return x + (math.log10(v) - math.log10(xr[0])) / (math.log10(xr[1]) - math.log10(xr[0])) * w
            return x + (v - xr[0]) / (xr[1] - xr[0]) * w

        def fy(v):
            return y + h - (v - yr[0]) / (yr[1] - yr[0]) * h
        for v, lab in xticks:
            if grid:
                self.line([(fx(v), y), (fx(v), y + h)], "gridl")
            self.text(fx(v), y + h + 15, lab, "tcs", "middle")
        for v, lab in yticks:
            if grid:
                self.line([(x, fy(v)), (x + w, fy(v))], "gridl")
            self.text(x - 6, fy(v) + 4, lab, "tcs", "end")
        self.path(f"M{fmt(x)} {fmt(y)} V{fmt(y + h)} H{fmt(x + w)}", "wt")
        if xlabel:
            self.text(x + w / 2, y + h + 32, xlabel, "tm", "middle")
        if ylabel:
            self.add(f'<text class="tm" text-anchor="middle" transform="translate({fmt(x - 38)} {fmt(y + h / 2)}) rotate(-90)">{markup(ylabel)}</text>')
        return fx, fy

    def curve(self, fx, fy, pts, cls="hw"):
        self.line([(fx(a), fy(b)) for a, b in pts], cls)


def figure(fig_html, cap):
    return f'<figure class="dg"><div class="scroll">{fig_html}</div><figcaption>{cap}</figcaption></figure>'
