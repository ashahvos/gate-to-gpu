"""Part V diagrams: processor organization, performance, caches, memories, FPGAs, parallelism and GPUs."""
import math
from dlib import Fig, diagram, fmt
from d3 import term
from d4 import clouds, slash


def arrow_lbl(f, pts, label, cls="w", kind="ah", lx=0, ly=-6, lcls="tcs", anchor="middle"):
    f.line(pts, cls, end=kind)
    if label:
        (x1, y1), (x2, y2) = pts[0], pts[-1]
        f.text((x1 + x2) / 2 + lx, (y1 + y2) / 2 + ly, label, lcls, anchor)


# ======================================================================
# Module 18: datapath
# ======================================================================
@diagram("computer_bus")
def computer_bus():
    f = Fig(780, 300, "A computer: processor, memory and I/O devices connected by address, data and control buses")
    f.rect(30, 30, 230, 150, "bs", 8)
    f.text(145, 52, "processor (CPU)", "tb", "middle")
    for lab, x, y, w in (("registers R0–R15", 46, 66, 200), ("ALU", 46, 104, 90), ("control", 146, 104, 100), ("PC", 46, 142, 90), ("IR", 146, 142, 100)):
        f.rect(x, y, w, 28, "b", 4)
        f.text(x + w / 2, y + 19, lab, "tc", "middle")
    f.rect(310, 50, 170, 110, "b", 8)
    f.text(395, 82, "memory", "tb", "middle")
    f.text(395, 102, "program and data", "tm", "middle")
    f.text(395, 120, "one word per address", "tm", "middle")
    f.rect(530, 22, 230, 176, "bg", 8)
    f.text(645, 190, "I/O devices (memory-mapped)", "tm", "middle")
    for i, lab in enumerate(("GPIO ports", "LCD controller", "timer / ADC")):
        y = 32 + 48 * i
        f.rect(545, y, 200, 38, "ba", 6)
        f.text(645, y + 24, lab, "tb", "middle")
    for lab, y, cls in (("address bus", 222, "hw"), ("data bus", 246, "aw"), ("control bus (read, write)", 270, "w")):
        f.line([(20, y), (760, y)], cls, extra=' style="stroke-width:4"')
        f.text(24, y - 6, lab, "tcs")
    for x0, top in ((90, 180), (340, 160), (590, 198)):
        f.line([(x0, top), (x0, 222)], "hw")
        f.dot(x0, 222, 4, "dotc")
        f.line([(x0 + 40, top), (x0 + 40, 246)], "aw")
        f.dot(x0 + 40, 246, 4)
        f.line([(x0 + 80, top), (x0 + 80, 270)])
        f.dot(x0 + 80, 270, 4)
    return f.svg()


@diagram("instr_format")
def instr_format():
    f = Fig(780, 230, "Instruction encodings: a 16-bit teaching format and the 32-bit RISC-V R-type format")
    f.text(20, 30, "16-bit format: 0x0201", "tb")
    fields = (("opcode", "0000", "ADD"), ("dst", "0010", "R2"), ("src1", "0000", "R0"), ("src2", "0001", "R1"))
    x = 20
    for name, bits, meaning in fields:
        f.rect(x, 44, 120, 34, "bs", 0)
        f.text(x + 60, 66, bits, "tc", "middle")
        f.text(x + 60, 94, name, "tcs", "middle")
        f.text(x + 60, 110, meaning, "tcb", "middle")
        x += 120
    f.text(520, 66, "R2 ← R0 + R1", "tc")
    f.text(20, 148, "RISC-V R-type (32 bits): add x5, x6, x7", "tb")
    fields = (("funct7", 7, "0000000"), ("rs2", 5, "00111"), ("rs1", 5, "00110"), ("funct3", 3, "000"), ("rd", 5, "00101"), ("opcode", 7, "0110011"))
    x = 20
    for name, w, bits in fields:
        wpx = w * 22
        f.rect(x, 160, wpx, 34, "ba", 0)
        f.text(x + wpx / 2, 182, bits, "tcs", "middle")
        f.text(x + wpx / 2, 212, name, "tcs", "middle")
        x += wpx
    return f.svg()


@diagram("regfile")
def regfile():
    f = Fig(780, 340, "A register file with four registers, one write port and two read ports")
    f.rect(90, 66, 70, 180, "b", 4)
    f.text(125, 150, "2:4", "tb", "middle")
    f.text(125, 166, "decoder", "tcs", "middle")
    f.line([(30, 156), (90, 156)])
    f.text(30, 174, "write addr", "tcs")
    slash(f, 64, 156, 2)
    f.line([(125, 246), (125, 272)])
    f.text(125, 288, "RegWrite", "tcb", "middle")
    f.line([(30, 40), (240, 40), (240, 222)], "aw")
    f.text(30, 32, "write data", "tcs")
    outs = []
    for i in range(4):
        y = 62 + 45 * i
        f.rect(260, y, 110, 38, "bs", 4)
        f.text(330, y + 24, f"R{i}", "tb", "middle")
        f.text(266, y + 15, "D", "tcs")
        f.text(266, y + 31, "en", "tcs")
        f.line([(240, y + 11), (260, y + 11)], "aw")
        f.dot(240, y + 11, 3)
        f.line([(160, y + 26.5), (260, y + 26.5)])
        outs.append((370, y + 19))
    m1 = f.mux(560, 40, 4, 120)
    m2 = f.mux(560, 190, 4, 120)
    for i, (ox, oy) in enumerate(outs):
        xb = 420 + 22 * i
        f.line([(ox, oy), (xb, oy)])
        f.dot(xb, oy)
        top, bot = min(oy, m1["ins"][i][1]), m2["ins"][i][1]
        f.line([(xb, top), (xb, bot)])
        f.line([(xb, m1["ins"][i][1]), m1["ins"][i]])
        f.line([(xb, m2["ins"][i][1]), m2["ins"][i]])
    f.line([m1["out"], (660, m1["out"][1])])
    term(f, 664, m1["out"][1], "read data A", "right", "tc")
    f.line([m2["out"], (660, m2["out"][1])])
    term(f, 664, m2["out"][1], "read data B", "right", "tc")
    f.line([m1["sel"], (m1["sel"][0], 178)])
    f.text(m1["sel"][0] + 8, 182, "read addr A", "tcs")
    f.line([m2["sel"], (m2["sel"][0], 326)])
    f.text(m2["sel"][0] + 8, 330, "read addr B", "tcs")
    return f.svg()


@diagram("cpu_datapath")
def cpu_datapath():
    f = Fig(800, 390, "A simplified single-cycle processor datapath with its control unit")
    f.block(20, 30, 160, 44, "next-PC logic", "PC + 4 or branch target", "bg")
    f.block(40, 160, 60, 50, "PC", None, "bs")
    f.line([(60, 74), (60, 160)], "w", end="ah")
    f.line([(85, 160), (85, 110), (150, 110), (150, 74)], "w", end="ah")
    f.block(120, 120, 100, 130, "instruction", "memory", "b")
    f.line([(100, 185), (120, 185)], "w", end="ah")
    f.block(290, 140, 110, 110, "register", "file", "b")
    for lab, y in (("rs1", 160), ("rs2", 185), ("rd", 210)):
        f.line([(220, y), (290, y)], "w", end="ah")
        f.text(255, y - 4, lab, "tcs", "middle")
    f.block(300, 285, 100, 34, "imm gen", None, "bg")
    f.line([(220, 235), (240, 235), (240, 302), (300, 302)], "w", end="ah")
    f.block(300, 30, 130, 50, "control unit", None, "ba")
    f.line([(220, 135), (260, 135), (260, 55), (300, 55)], "w", end="ah")
    f.text(266, 98, "opcode", "tcs")
    f.text(440, 46, "RegWrite, ALUSrc, ALUOp,", "tcs tcol")
    f.text(440, 62, "MemRead, MemWrite, MemtoReg, Branch", "tcs tcol")
    f.line([(180, 52), (300, 52)], "dashc", start="ahc")
    m = f.mux(440, 170, 2, 60)
    f.line([(400, 160), (490, 160), (490, 165), (510, 165)], "w", end="ah")
    f.line([(400, 185), (440, 185)], "w", end="ah")
    f.dot(415, 185)
    f.line([(400, 302), (425, 302), (425, 215), (440, 215)], "w", end="ah")
    f.text(457, 246, "ALUSrc", "tcs tcol", "middle")
    f.path("M510 135 L570 160 V230 L510 255 V210 L522 195 L510 180 Z", "bs")
    f.text(548, 199, "ALU", "tb", "middle")
    f.line([m["out"], (510, 200)], "w", end="ah")
    f.block(610, 160, 90, 90, "data", "memory", "b")
    f.line([(570, 195), (610, 195)], "w", end="ah")
    f.text(590, 189, "addr", "tcs", "middle")
    f.line([(415, 185), (415, 340), (595, 340), (595, 230), (610, 230)], "w", end="ah")
    f.text(505, 354, "write data (rs2)", "tcs", "middle")
    m2 = f.mux(730, 165, 2, 60)
    f.dot(585, 195)
    f.line([(585, 195), (585, 130), (715, 130), (715, m2["ins"][0][1]), m2["ins"][0]], "w", end="ah")
    f.line([(700, m2["ins"][1][1]), m2["ins"][1]], "w", end="ah")
    f.text(747, 241, "MemtoReg", "tcs tcol", "middle")
    f.line([m2["out"], (786, m2["out"][1]), (786, 374), (270, 374), (270, 235), (290, 235)], "w", end="ah")
    f.text(528, 368, "write-back to rd", "tcs", "middle")
    return f.svg()


# ======================================================================
# Module 19: performance and pipelining
# ======================================================================
@diagram("pipeline_stages")
def pipeline_stages():
    f = Fig(780, 270, "Pipelining a 10 ns block: one stage needs a 10 ns clock; two balanced 5 ns stages separated by a register allow a 5 ns clock")

    def reg(x, y):
        f.rect(x, y, 16, 54, "bs", 2)
    reg(40, 40)
    clouds(f, 90, 34, 520, 66, "combinational logic", "10 ns")
    reg(660, 40)
    f.line([(56, 67), (90, 67)], "w", end="ah")
    f.line([(610, 67), (660, 67)], "w", end="ah")
    f.text(360, 124, "unpipelined: T = 10 ns, one result every 10 ns, latency 10 ns", "tm", "middle")
    reg(40, 160)
    clouds(f, 90, 154, 240, 66, "stage 1", "5 ns")
    reg(352, 160)
    clouds(f, 400, 154, 240, 66, "stage 2", "5 ns")
    reg(660, 160)
    f.line([(56, 187), (90, 187)], "w", end="ah")
    f.line([(330, 187), (352, 187)], "w", end="ah")
    f.line([(368, 187), (400, 187)], "w", end="ah")
    f.line([(640, 187), (660, 187)], "w", end="ah")
    f.text(360, 246, "2 stages: T = 5 ns (plus register overhead), one result every 5 ns, latency 10 ns", "tm", "middle")
    return f.svg()


@diagram("pipe5")
def pipe5():
    f = Fig(800, 250, "The classic five-stage pipeline with pipeline registers and forwarding paths into the ALU")
    stages = (("IF", "fetch"), ("ID", "decode,", "read regs"), ("EX", "ALU"), ("MEM", "data", "memory"), ("WB", "write", "back"))
    xs = [30, 190, 350, 510, 670]
    for i, (x, st) in enumerate(zip(xs, stages)):
        f.rect(x, 80, 100, 80, "b", 6)
        f.text(x + 50, 112, st[0], "tb", "middle")
        for k, line in enumerate(st[1:]):
            f.text(x + 50, 130 + 14 * k, line, "tm", "middle")
        if i < 4:
            f.rect(x + 118, 70, 22, 100, "bs", 2)
            f.text(x + 129, 190, ["IF/ID", "ID/EX", "EX/MEM", "MEM/WB"][i], "tcs", "middle")
            f.line([(x + 100, 120), (x + 118, 120)], "w", end="ah")
            f.line([(x + 140, 120), (xs[i + 1], 120)], "w", end="ah")
    f.line([(479, 70), (479, 46), (412, 46), (412, 80)], "aw", end="aha")
    f.text(486, 50, "forward from EX/MEM", "tcs")
    f.line([(639, 70), (639, 24), (388, 24), (388, 80)], "mw", end="ah")
    f.text(646, 28, "forward from MEM/WB", "tcs")
    f.text(400, 232, "one instruction enters per cycle; up to five are in flight at once", "tm", "middle")
    return f.svg()


@diagram("bp2bit")
def bp2bit():
    f = Fig(780, 230, "A 2-bit saturating counter branch predictor: two wrong guesses in a row are needed to change the prediction")
    st = {"ST": dict(x=110, y=120, lines=["11", "taken"], cls="ba"), "WT": dict(x=300, y=120, lines=["10", "taken"], cls="ba"),
          "WN": dict(x=490, y=120, lines=["01", "not taken"]), "SN": dict(x=680, y=120, lines=["00", "not taken"])}
    ed = [dict(a="ST", b="ST", label="T", ang=-90), dict(a="ST", b="WT", label="N", bend=-22),
          dict(a="WT", b="ST", label="T", bend=-22), dict(a="WT", b="WN", label="N", bend=-22),
          dict(a="WN", b="WT", label="T", bend=-22), dict(a="WN", b="SN", label="N", bend=-22),
          dict(a="SN", b="WN", label="T", bend=-22), dict(a="SN", b="SN", label="N", ang=-90)]
    f.fsm(st, ed, r=40)
    f.text(390, 214, "predict taken in 11 and 10; T = branch was taken, N = not taken", "tm", "middle")
    return f.svg(min_width=560)


# ======================================================================
# Module 20: caches and virtual memory
# ======================================================================
@diagram("memhier")
def memhier():
    f = Fig(780, 330, "The memory hierarchy: each level is larger, slower and cheaper per byte than the one above it")
    levels = (("registers", "~1 KB", "< 0.3 ns", "ba"), ("L1 cache", "32–64 KB per core", "~1 ns (4 cycles)", "ba"),
              ("L2 cache", "0.25–2 MB per core", "~3–5 ns", "bs"), ("L3 cache", "8–64 MB shared", "~10–20 ns", "bs"),
              ("main memory (DRAM)", "8–512 GB", "~60–100 ns", "b"), ("SSD", "0.5–8 TB", "~50–100 μs", "bg"))
    cx, top, h = 300, 20, 46
    for i, (name, size, lat, cls) in enumerate(levels):
        w0 = 70 + 70 * i
        w1 = 70 + 70 * (i + 1)
        y = top + i * h
        f.path(f"M{cx - w0 / 2} {y} H{cx + w0 / 2} L{cx + w1 / 2} {y + h - 4} H{cx - w1 / 2} Z", cls)
        f.text(cx, y + 27, name, "tb" if i < 5 else "tm", "middle")
        f.text(560, y + 20, size, "tc")
        f.text(560, y + 36, lat, "tcs")
    f.text(560, 12, "capacity / latency", "tm")
    f.line([(30, 30), (30, 290)], "dashc", start="ahc", end="ahc")
    f.text(40, 40, "faster,", "tcs tcol")
    f.text(40, 54, "smaller", "tcs tcol")
    f.text(40, 270, "larger,", "tcs tcol")
    f.text(40, 284, "cheaper", "tcs tcol")
    return f.svg()


@diagram("cache_lookup")
def cache_lookup():
    f = Fig(800, 330, "Looking up a direct-mapped cache: the index selects one line, the stored tag is compared with the address tag, and the offset selects bytes within the block")
    f.text(40, 24, "32-bit address", "tb")
    for x, w, lab, bits, cls in ((40, 300, "tag", "bits 31–14 (18 bits)", "bs"), (340, 160, "index", "bits 13–6 (8)", "ba"), (500, 120, "offset", "bits 5–0 (6)", "bg")):
        f.rect(x, 34, w, 32, cls, 0)
        f.text(x + w / 2, 55, lab, "tb", "middle")
        f.text(x + w / 2, 82, bits, "tcs", "middle")
    cols = ((290, 140, "tag"), (430, 30, "V"), (470, 230, "data block (64 bytes)"))
    for x, w, lab in cols:
        f.text(x + w / 2, 112, lab, "tcs", "middle")
    for r in range(4):
        y = 118 + r * 20
        sel = (r == 3)
        for x, w, _ in cols:
            f.rect(x, y, w, 20, "ba" if sel else "b", 0)
        if r == 2:
            f.text(360, y + 15, "⋮", "tcs", "middle")
            f.text(585, y + 15, "⋮", "tcs", "middle")
    f.text(706, 193, "selected line", "tcs")
    f.line([(486, 66), (486, 96), (250, 96), (250, 188), (290, 188)], "aw", end="aha")
    f.text(244, 140, "index", "tcs", "end")
    f.text(244, 154, "selects", "tcs", "end")
    f.text(244, 168, "one line", "tcs", "end")
    f.circle(360, 250, 16, "b")
    f.text(360, 255, "=", "tb", "middle")
    f.line([(360, 198), (360, 234)], "w", end="ah")
    f.line([(60, 66), (60, 250), (344, 250)], "hw", end="ahc")
    f.text(66, 242, "address tag", "tcs tcol")
    g = f.gate("AND", 440, 240)
    f.line([(445, 198), (445, 222), (424, 222), (424, 250), g["ins"][0]])
    f.text(452, 220, "valid", "tcs")
    f.line([(376, 250), (400, 250), (400, 270), g["ins"][1]])
    f.line([g["out"], (530, g["out"][1])])
    term(f, 534, g["out"][1], "hit", "right", "tb")
    f.block(560, 228, 130, 40, "select bytes", None, "bg")
    f.line([(625, 198), (625, 228)], "w", end="ah")
    f.line([(560, 66), (560, 96), (740, 96), (740, 248), (690, 248)], "wt", end="ah")
    f.text(748, 150, "offset", "tcs")
    f.line([(625, 268), (625, 296)])
    term(f, 625, 300, "data", "below", "tb")
    return f.svg()


@diagram("vm_translate")
def vm_translate():
    f = Fig(780, 250, "Virtual-to-physical address translation: the page number is translated through the TLB or the page table; the offset passes through unchanged")
    f.text(30, 30, "virtual address (48 bits)", "tb")
    f.rect(30, 40, 300, 32, "bs", 0)
    f.text(180, 61, "virtual page number (36 bits)", "tc", "middle")
    f.rect(330, 40, 140, 32, "bg", 0)
    f.text(400, 61, "offset (12)", "tc", "middle")
    f.block(120, 110, 140, 50, "TLB", "recent translations", "ba")
    f.block(330, 110, 170, 50, "page table walk", "in memory, on TLB miss", "b")
    f.line([(180, 72), (180, 110)], "w", end="ah")
    f.line([(260, 135), (330, 135)], "dash", end="ah")
    f.text(295, 128, "miss", "tcs", "middle")
    f.text(30, 200, "physical address", "tb")
    f.rect(30, 210, 300, 32, "bs", 0)
    f.text(180, 231, "physical page number", "tc", "middle")
    f.rect(330, 210, 140, 32, "bg", 0)
    f.text(400, 231, "offset (12)", "tc", "middle")
    f.line([(180, 160), (180, 210)], "w", end="ah")
    f.text(186, 190, "hit", "tcs")
    f.line([(415, 160), (415, 180), (230, 180), (230, 210)], "dash", end="ah")
    f.line([(450, 72), (450, 96), (520, 96), (520, 226), (470, 226)], "w", end="ah")
    f.text(526, 150, "offset copied", "tcs")
    f.text(526, 164, "unchanged", "tcs")
    f.text(600, 60, "4 KB pages:", "tm")
    f.text(600, 76, "offset = low 12 bits", "tm")
    f.text(600, 108, "each entry also holds", "tm")
    f.text(600, 124, "permissions (read, write,", "tm")
    f.text(600, 140, "execute, user) and a", "tm")
    f.text(600, 156, "valid (present) bit", "tm")
    return f.svg()


@diagram("row_major")
def row_major():
    f = Fig(780, 230, "A 4-by-4 C array is stored row after row; walking along a row touches consecutive addresses, walking down a column jumps a whole row each step")
    x0, y0, c = 40, 50, 36
    for r in range(4):
        for k in range(4):
            cls = "ba" if r == 1 else ("bs" if k == 2 else "b")
            f.rect(x0 + k * c, y0 + r * c, c, c, cls, 0)
            f.text(x0 + k * c + c / 2, y0 + r * c + 23, f"{r}{k}", "tcs", "middle")
    f.text(x0 + 2 * c, 36, "a[r][c]", "tc", "middle")
    f.text(x0 + 4 * c + 10, y0 + 1.5 * c + 5, "row 1", "tcs ta")
    f.text(x0 + 2.5 * c, y0 + 4 * c + 16, "column 2", "tcs tcol", "middle")
    mx, my, w = 260, 110, 30
    f.text(mx + 16 * w, 96, "memory, increasing addresses →", "tm", "end")
    for i in range(16):
        r, k = divmod(i, 4)
        cls = "ba" if r == 1 else ("bs" if k == 2 else "b")
        f.rect(mx + i * w, my, w, 30, cls, 0)
        f.text(mx + i * w + w / 2, my + 20, f"{r}{k}", "tcs", "middle")
    for i in range(4, 7):
        f.path(f"M{mx + i * w + w / 2} {my - 4} Q{mx + i * w + w} {my - 18} {mx + (i + 1) * w + w / 2 - 2} {my - 4}", "aw", end="aha")
    for i in (2, 6, 10):
        f.path(f"M{mx + i * w + w / 2} {my + 34} Q{mx + (i + 2) * w + w / 2} {my + 70} {mx + (i + 4) * w + w / 2 - 2} {my + 36}", "hw", end="ahc")
    f.text(mx + 5 * w, 74, "stride 1 element: same cache line", "tcs ta", "middle")
    f.text(mx + 8 * w, 206, "stride 4 elements: a new line each step for wide rows", "tcs tcol", "middle")
    return f.svg()


# ======================================================================
# Module 21: memories and FPGAs
# ======================================================================
from d3 import mos_rot  # noqa: E402
from d4 import not_left  # noqa: E402


@diagram("sram6t")
def sram6t():
    f = Fig(780, 270, "A six-transistor SRAM cell: two cross-coupled inverters store the bit, and two access transistors connect it to the bit lines when the word line is high")
    f.line([(100, 36), (100, 236)], "hw")
    f.line([(460, 36), (460, 236)], "hw")
    f.text(100, 254, "BL", "tcb", "middle")
    f.text(460, 254, "BL′", "tcb", "middle")
    f.line([(70, 60), (490, 60)], "aw")
    f.text(66, 64, "WL", "ta", "end")
    a = f.gate("NOT", 250, 115)
    b = not_left(f, 250, 175)
    f.line([(200, 130), a["ins"][0]])
    f.line([a["out"], (360, 130)])
    f.line([(360, 130), (360, 190), b["in"]])
    f.line([b["out"], (200, 190), (200, 130)])
    f.dot(200, 130)
    f.dot(360, 130)
    f.text(206, 152, "Q", "tb")
    f.text(354, 152, "Q′", "tb", "end")
    l = mos_rot(f, 150, 114, "n")
    r = mos_rot(f, 410, 114, "n")
    f.line([(100, 130), l["left"]])
    f.line([l["right"], (200, 130)])
    f.line([(360, 130), r["left"]])
    f.line([r["right"], (460, 130)])
    f.line([l["g"], (150, 60)])
    f.line([r["g"], (410, 60)])
    f.dot(150, 60, 3, "dot")
    f.dot(410, 60, 3, "dot")
    f.dot(100, 130)
    f.dot(460, 130)
    f.text(520, 80, "Read: precharge BL and BL′ high,", "tm")
    f.text(520, 96, "raise WL; the side holding 0 pulls", "tm")
    f.text(520, 112, "its bit line down slightly, and a", "tm")
    f.text(520, 128, "sense amplifier detects the difference.", "tm")
    f.text(520, 160, "Write: drive BL and BL′ to the new", "tm")
    f.text(520, 176, "value and its complement, raise WL;", "tm")
    f.text(520, 192, "the access transistors overpower", "tm")
    f.text(520, 208, "the inverters.", "tm")
    return f.svg()


@diagram("dram1t")
def dram1t():
    f = Fig(640, 250, "A one-transistor DRAM cell: the bit is charge on a capacitor, connected to the bit line by an access transistor")
    f.line([(216, 30), (216, 104)], "hw")
    f.text(222, 44, "BL", "tcb")
    p = f.mosfet(200, 130, "n")
    f.line([(80, 60), (300, 60)], "aw")
    f.text(76, 64, "WL", "ta", "end")
    f.line([p["g"], (150, 130), (150, 60)])
    f.dot(150, 60, 3)
    f.line([p["bot"], (216, 176)])
    c = f.capacitor(216, 180, "v", "C_{S} (a few fF)", lab_dx=20)
    f.line([c["b"], (216, 204)])
    f.ground(216, 204)
    f.text(340, 80, "Write: raise WL and drive BL;", "tm")
    f.text(340, 96, "the capacitor charges or discharges.", "tm")
    f.text(340, 128, "Read: precharge BL to V_{DD}/2, raise WL;", "tm")
    f.text(340, 144, "charge sharing moves BL by tens of mV,", "tm")
    f.text(340, 160, "which a sense amplifier detects. The read", "tm")
    f.text(340, 176, "destroys the value, so it is written back.", "tm")
    f.text(340, 208, "Leakage drains C_{S}: every row must be", "tm")
    f.text(340, 224, "refreshed periodically (about every 64 ms).", "tm")
    return f.svg()


@diagram("memarray")
def memarray():
    f = Fig(780, 380, "Organization of a memory array: a row decoder drives one word line, every cell in that row drives its bit line, and a column multiplexer picks the requested bits")
    f.block(70, 70, 110, 190, "row", "decoder", "b")
    f.line([(10, 165), (70, 165)], "w", end="ah")
    f.text(10, 156, "row addr", "tcs")
    x0, y0, cw, ch, nr, nc = 200, 70, 44, 22, 8, 10
    for r in range(nr):
        y = y0 + r * ch + ch / 2 + 1
        sel = (r == 3)
        f.line([(180, y), (x0 + nc * cw, y)], "aw" if sel else "wt")
        for k in range(nc):
            f.rect(x0 + k * cw + 10, y0 + r * ch + 4, cw - 20, ch - 8, "ba" if sel else "b", 2)
    for k in range(nc):
        x = x0 + k * cw + cw / 2
        f.line([(x, y0 - 6), (x, y0 + nr * ch + 10)], "hw" if k == 6 else "gridl")
    f.text(x0 + nc * cw + 8, y0 + 3 * ch + 16, "word line", "tcs ta")
    f.text(x0 + 6 * cw + cw / 2, y0 - 12, "bit lines", "tcs tcol", "middle")
    f.block(x0, y0 + nr * ch + 18, nc * cw, 30, "sense amplifiers", None, "bs", tcls="tcs")
    f.block(x0, y0 + nr * ch + 56, nc * cw, 30, "column multiplexer", None, "bg", tcls="tcs")
    f.line([(x0 + nc * cw + 50, y0 + nr * ch + 71), (x0 + nc * cw, y0 + nr * ch + 71)], "w", end="ah")
    f.text(x0 + nc * cw + 54, y0 + nr * ch + 75, "column addr", "tcs")
    f.line([(x0 + nc * cw / 2, y0 + nr * ch + 86), (x0 + nc * cw / 2, y0 + nr * ch + 106)], "w", end="ah")
    f.text(x0 + nc * cw / 2 + 8, y0 + nr * ch + 104, "data", "tcs")
    f.text(20, 300, "2^{r} rows × 2^{c} columns", "tm")
    f.text(20, 316, "address = row bits | column bits", "tm")
    return f.svg()


@diagram("mem_expand")
def mem_expand():
    f = Fig(780, 300, "Depth expansion: four 1K by 8 memory chips form a 4K by 8 memory; the two upper address bits select one chip through a decoder")
    xs = [230, 360, 490, 620]
    for i, x in enumerate(xs):
        f.rect(x, 80, 100, 110, "bs", 6)
        f.text(x + 50, 118, "1K × 8", "tb", "middle")
        f.text(x + 50, 136, f"chip {i}", "tm", "middle")
        f.line([(x + 30, 80), (x + 30, 50)])
        f.dot(x + 30, 50)
        f.line([(x + 22, 190), (x + 22, 204)])
        f.text(x + 22, 218, f"CS{i}′", "tcs tcol", "middle")
        f.line([(x + 70, 190), (x + 70, 240)], "aw")
        f.dot(x + 70, 240, 3.5)
    f.line([(160, 50), (680, 50)])
    f.text(160, 42, "A9–A0 (to every chip)", "tcs")
    f.line([(280, 240), (760, 240)], "aw")
    f.text(760, 258, "D7–D0 (shared, tristate)", "tcs", "end")
    f.block(40, 100, 100, 110, "2:4", "decoder", "b")
    f.line([(10, 155), (40, 155)], "w", end="ah")
    f.text(10, 140, "A11–A10", "tcs")
    for i in range(4):
        y = 114 + 26 * i
        f.line([(140, y), (162, y)])
        f.text(166, y + 4, f"CS{i}′", "tcs tcol")
    f.text(40, 284, "matching labels are connected; an active-low chip select from the decoder enables exactly one chip", "tm")
    return f.svg()


@diagram("lut_mem")
def lut_mem():
    f = Fig(760, 270, "A memory used as a truth table: the inputs form the address, and the stored words are the outputs; this 8 by 2 memory is a full adder")
    for i, lab in enumerate(("A", "B", "Cin")):
        f.line([(40, 70 + 30 * i), (150, 70 + 30 * i)], "w", end="ah")
        f.text(36, 74 + 30 * i, lab, "tb", "end")
        f.text(100, 64 + 30 * i, f"A{2 - i}", "tcs", "middle")
    f.rect(150, 40, 220, 200, "bs", 6)
    f.text(260, 60, "8 × 2 memory", "tb", "middle")
    rows = ["00", "01", "01", "10", "01", "10", "10", "11"]
    for i, r in enumerate(rows):
        y = 74 + 20 * i
        f.text(200, y + 14, format(i, "03b"), "tcs", "middle")
        f.rect(240, y, 80, 18, "b", 2)
        f.text(280, y + 14, r, "tc", "middle")
    f.text(200, 250, "address", "tcs", "middle")
    f.text(280, 250, "data (Cout S)", "tcs", "middle")
    f.line([(370, 110), (440, 110)], "w", end="ah")
    f.text(446, 114, "Cout", "tb")
    f.line([(370, 150), (440, 150)], "w", end="ah")
    f.text(446, 154, "S", "tb")
    f.text(500, 90, "any n-input, m-output function", "tm")
    f.text(500, 106, "fits in a 2^{n} × m memory:", "tm")
    f.text(500, 122, "store the truth table's outputs", "tm")
    f.text(500, 154, "cost doubles with every input,", "tm")
    f.text(500, 170, "so FPGAs use many small LUTs", "tm")
    f.text(500, 186, "(4 to 6 inputs) plus routing", "tm")
    return f.svg()


@diagram("clb")
def clb():
    f = Fig(760, 266, "A simplified FPGA logic cell: a lookup table, a flip-flop, and a configuration-controlled multiplexer that selects a combinational or registered output")
    f.rect(30, 30, 560, 200, "bg", 10)
    f.text(46, 52, "logic cell", "tb")
    f.block(120, 70, 120, 100, "4-input", "LUT (16 bits)", "bs")
    for i in range(4):
        f.line([(10, 85 + 22 * i), (120, 85 + 22 * i)], "w", end="ah")
    f.text(8, 76, "inputs", "tcs")
    p = f.dff(320, 100, w=64, d="D", q="Q", qb=None)
    f.line([(240, 120), (280, 120)])
    f.dot(280, 120)
    f.line([(280, 120), (280, p["D"][1]), p["D"]])
    m = f.mux(450, 90, 2, 70)
    f.line([(280, 120), (280, 76), (430, 76), (430, m["ins"][0][1]), m["ins"][0]])
    f.line([p["Q"], (420, p["Q"][1]), (420, m["ins"][1][1]), m["ins"][1]])
    f.line([(300, 210), (300, p["CLK"][1]), p["CLK"]])
    f.text(300, 224, "CLK", "tcs", "middle")
    f.line([m["out"], (620, m["out"][1])], "w", end="ah")
    f.text(626, m["out"][1] + 4, "to routing", "tcs")
    f.rect(452, 178, 30, 22, "ba", 2)
    f.line([(467, 178), m["sel"]])
    f.rect(165, 178, 30, 22, "ba", 2)
    f.line([(180, 178), (180, 170)])
    f.text(30, 252, "gold boxes are configuration bits, loaded when the FPGA powers up: they hold the LUT's truth table and choose the output", "tm")
    return f.svg()


@diagram("fpga_fabric")
def fpga_fabric():
    f = Fig(760, 330, "FPGA fabric: an array of logic blocks surrounded by routing channels; programmable switch boxes connect the wires")
    n = 3
    x0, y0, s, b = 120, 40, 90, 50
    for r in range(n + 1):
        y = y0 + r * s - 20
        f.line([(x0 - 40, y), (x0 + n * s, y)], "gridl", extra=' style="stroke-width:3"')
    for k in range(n + 1):
        x = x0 + k * s - 20
        f.line([(x, y0 - 40), (x, y0 + n * s)], "gridl", extra=' style="stroke-width:3"')
    for r in range(n):
        for k in range(n):
            f.rect(x0 + k * s, y0 + r * s, b, b, "bs", 4)
            f.text(x0 + k * s + b / 2, y0 + r * s + 30, "CLB", "tcs", "middle")
    for r in range(n + 1):
        for k in range(n + 1):
            f.rect(x0 + k * s - 28, y0 + r * s - 28, 16, 16, "b", 2)
    path = [(x0 + b, y0 + 25), (x0 + s - 20, y0 + 25), (x0 + s - 20, y0 + s - 20), (x0 + 2 * s - 20, y0 + s - 20),
            (x0 + 2 * s - 20, y0 + 2 * s + 25), (x0 + 2 * s, y0 + 2 * s + 25)]
    f.line(path, "aw", end="aha")
    f.text(x0 + n * s + 30, 60, "blue: logic blocks (LUTs + flip-flops)", "tm")
    f.text(x0 + n * s + 30, 80, "white: switch boxes (muxes set by", "tm")
    f.text(x0 + n * s + 30, 96, "configuration bits)", "tm")
    f.text(x0 + n * s + 30, 116, "gray: routing channels", "tm")
    f.text(x0 + n * s + 30, 146, "gold: one routed connection,", "tm")
    f.text(x0 + n * s + 30, 162, "chosen by place-and-route", "tm")
    f.text(x0 + n * s + 30, 200, "real devices add block RAM,", "tm")
    f.text(x0 + n * s + 30, 216, "DSP (multiply-add) blocks,", "tm")
    f.text(x0 + n * s + 30, 232, "clock managers, high-speed", "tm")
    f.text(x0 + n * s + 30, 248, "transceivers, even CPU cores", "tm")
    return f.svg()


# ======================================================================
# Module 22: parallelism and GPUs
# ======================================================================
@diagram("roofline")
def roofline():
    f = Fig(760, 340, "Roofline model: attainable performance is the lower of the compute peak and memory bandwidth times arithmetic intensity")
    X0, Y0, W, H = 90, 24, 460, 250
    lx = lambda v: math.log2(v)
    xr = (lx(1 / 16), lx(256))
    yr = (math.log10(0.05), math.log10(100))
    def fx(v):
        return X0 + (lx(v) - xr[0]) / (xr[1] - xr[0]) * W
    def fy(v):
        return Y0 + H - (math.log10(v) - yr[0]) / (yr[1] - yr[0]) * H
    for v, lab in ((1 / 16, "1/16"), (1 / 4, "1/4"), (1, "1"), (4, "4"), (16, "16"), (64, "64"), (256, "256")):
        f.line([(fx(v), Y0), (fx(v), Y0 + H)], "gridl")
        f.text(fx(v), Y0 + H + 16, lab, "tcs", "middle")
    for v, lab in ((0.1, "0.1"), (1, "1"), (10, "10"), (100, "100")):
        f.line([(X0, fy(v)), (X0 + W, fy(v))], "gridl")
        f.text(X0 - 6, fy(v) + 4, lab, "tcs", "end")
    f.path(f"M{X0} {Y0} V{Y0 + H} H{X0 + W}", "wt")
    f.text(X0 + W / 2, Y0 + H + 36, "arithmetic intensity (FLOP per byte of DRAM traffic)", "tm", "middle")
    f.add(f'<text class="tm" text-anchor="middle" transform="translate({X0 - 44} {Y0 + H / 2}) rotate(-90)">attainable TFLOP/s</text>')
    peak, bw = 60.0, 2.0
    ridge = peak / bw
    pts = []
    for i in range(0, 201):
        ai = 2 ** (xr[0] + (xr[1] - xr[0]) * i / 200)
        pts.append((fx(ai), fy(min(peak, bw * ai))))
    f.line(pts, "hw", extra=' style="stroke-width:3"')
    f.line([(fx(ridge), fy(peak)), (fx(ridge), Y0 + H)], "dash")
    f.text(fx(ridge) + 6, Y0 + H - 8, "ridge: 30 FLOP/B", "tcs")
    f.text(fx(1.3), fy(bw * 1.3) - 12, "memory bound: 2 TB/s × intensity", "tcs tcol halo", "middle")
    f.text(fx(110), fy(peak) - 8, "compute bound: 60 TFLOP/s", "tcs tcol", "middle")
    f.dot(fx(1 / 12), fy(bw / 12), 5, "dot")
    f.text(fx(1 / 12) + 10, fy(bw / 12) + 16, "vector add (1/12 FLOP/B)", "tcs ta halo")
    f.dot(fx(100), fy(peak), 5, "dot")
    f.text(fx(100) - 40, fy(peak) + 30, "large matrix multiply", "tcs ta halo")
    f.text(570, 150, "example GPU:", "tm")
    f.text(570, 166, "peak 60 TFLOP/s,", "tm")
    f.text(570, 182, "DRAM 2 TB/s", "tm")
    return f.svg()


@diagram("cuda_hier")
def cuda_hier():
    f = Fig(780, 330, "The CUDA execution hierarchy and memory spaces: a grid of thread blocks, each block a group of threads executed in warps of 32")
    f.rect(20, 30, 300, 200, "bg", 8)
    f.text(36, 52, "grid (one kernel launch)", "tb")
    for r in range(2):
        for c in range(3):
            x, y = 40 + c * 92, 70 + r * 76
            cls = "ba" if (r, c) == (1, 2) else "bs"
            f.rect(x, y, 80, 60, cls, 6)
            f.text(x + 40, y + 28, f"block ({c},{r})", "tcs", "middle")
            f.text(x + 40, y + 44, "blockIdx", "tcs", "middle")
    f.line([(304, 146), (380, 70)], "dash")
    f.line([(304, 206), (380, 240)], "dash")
    f.rect(380, 70, 230, 170, "ba", 8)
    f.text(396, 92, "block (2,1): 128 threads", "tb")
    for w in range(4):
        y = 104 + 30 * w
        f.text(396, y + 18, f"warp {w}", "tcs")
        for t in range(8):
            f.rect(456 + t * 17, y + 6, 13, 16, "b", 2)
        f.text(598, y + 18, "…", "tcs", "end")
    f.text(396, 232, "threads 0–31 form warp 0, and so on", "tcs")
    f.rect(630, 70, 130, 170, "b", 8)
    f.text(695, 92, "memory spaces", "tb", "middle")
    for i, (lab, sub) in enumerate((("registers", "per thread"), ("shared memory", "per block, on-chip"), ("L1 / L2 cache", "on-chip"), ("global memory", "all threads, DRAM"))):
        y = 102 + 34 * i
        f.text(695, y + 12, lab, "tcs", "middle")
        f.text(695, y + 26, sub, "tcs tcol", "middle")
    f.text(20, 262, "threadIdx locates a thread within its block; blockIdx locates the block within the grid.", "tm")
    f.text(20, 280, "Global index of a thread in a 1-D launch: i = blockIdx.x * blockDim.x + threadIdx.x", "tc")
    f.text(20, 304, "Blocks run independently, in any order, on whichever multiprocessor has room; threads in a block can share memory and synchronize.", "tm")
    return f.svg()


@diagram("gpu_sm")
def gpu_sm():
    f = Fig(780, 320, "A simplified GPU streaming multiprocessor: four partitions, each with a warp scheduler, a register file and execution units, sharing an L1 cache and shared memory")
    f.rect(20, 20, 740, 280, "bg", 10)
    f.text(36, 42, "streaming multiprocessor (SM)", "tb")
    for p in range(4):
        x = 36 + p * 182
        f.rect(x, 56, 170, 170, "b", 6)
        f.rect(x + 8, 64, 154, 26, "ba", 4)
        f.text(x + 85, 82, "warp scheduler", "tcs", "middle")
        f.rect(x + 8, 96, 154, 26, "bs", 4)
        f.text(x + 85, 114, "register file (64 KB)", "tcs", "middle")
        for k in range(8):
            f.rect(x + 8 + (k % 4) * 39, 128 + (k // 4) * 24, 35, 20, "b", 3)
        f.text(x + 85, 182, "FP32 and INT32 lanes", "tcs", "middle")
        f.rect(x + 8, 190, 74, 28, "bgr", 4)
        f.text(x + 45, 208, "tensor", "tcs", "middle")
        f.rect(x + 88, 190, 74, 28, "b", 4)
        f.text(x + 125, 208, "load/store", "tcs", "middle")
    f.rect(36, 236, 716, 50, "bs", 6)
    f.text(394, 258, "L1 data cache / shared memory (configurable, about 128–256 KB)", "tc", "middle")
    f.text(394, 276, "plus texture units; all SMs share an L2 cache in front of the GPU's DRAM", "tcs", "middle")
    return f.svg()


@diagram("warp_divergence")
def warp_divergence():
    f = Fig(780, 240, "Branch divergence in a warp: the two paths of an if statement execute one after the other with part of the warp masked off")
    lanes = 8
    steps = (("common", list(range(8))), ("if: A", [0, 1, 2]), ("if: A", [0, 1, 2]), ("else: B", [3, 4, 5, 6, 7]),
             ("else: B", [3, 4, 5, 6, 7]), ("reconverge", list(range(8))))
    x0, y0, cw, ch = 120, 50, 100, 20
    for i, (lab, act) in enumerate(steps):
        f.text(x0 + i * cw + cw / 2, y0 - 12, lab, "tcs", "middle")
        for l in range(lanes):
            on = l in act
            f.rect(x0 + i * cw + 4, y0 + l * ch + 2, cw - 8, ch - 4, "ba" if on else "bg", 2)
    for l in range(lanes):
        f.text(x0 - 8, y0 + l * ch + 15, f"lane {l}", "tcs", "end")
    f.line([(x0, y0 + lanes * ch + 14), (x0 + 6 * cw, y0 + lanes * ch + 14)], "wt", end="ah")
    f.text(x0 + 3 * cw, y0 + lanes * ch + 30, "time (instructions issued)", "tm", "middle")
    f.text(x0 + 6 * cw + 10, 80, "gold: active", "tcs ta")
    f.text(x0 + 6 * cw + 10, 96, "gray: masked off", "tcs")
    return f.svg()


@diagram("coalescing")
def coalescing():
    f = Fig(720, 280, "Memory coalescing: consecutive threads reading consecutive addresses need one transaction; strided addresses need more")
    def row(y, stride, title):
        f.text(20, y - 30, title, "tb")
        for t in range(8):
            f.rect(42 + t * 40, y - 20, 36, 20, "ba", 3)
            f.text(60 + t * 40, y - 5, f"t{t}", "tcs", "middle")
        for k in range(16):
            used = (k % stride == 0) and (k // stride < 8)
            f.rect(40 + k * 40, y + 50, 40, 24, "bs" if used else "b", 0)
            f.text(60 + k * 40, y + 67, f"{k}", "tcs", "middle")
        f.line([(360, y + 44), (360, y + 80)], "rw")
        for t in range(8):
            f.line([(60 + t * 40, y), (60 + t * stride * 40, y + 48)], "wt", end="ah")
    row(60, 1, "a[i]: eight consecutive floats, one 32-byte segment")
    row(185, 2, "a[2*i]: the same eight threads now touch two segments")
    f.text(700, 274, "element index in memory; red line = 32-byte segment boundary", "tm", "end")
    return f.svg()


@diagram("false_sharing")
def false_sharing():
    f = Fig(760, 230, "False sharing: two cores update different variables that happen to share one cache line, so the line moves back and forth between their caches")
    for i, (x, var) in enumerate(((60, "a"), (440, "b"))):
        f.rect(x, 30, 260, 70, "bs", 6)
        f.text(x + 130, 52, f"core {i}: repeatedly writes {var}", "tb", "middle")
        f.rect(x + 20, 64, 220, 24, "b", 3)
        f.rect(x + 20, 64, 30, 24, "ba" if var == "a" else "b", 0)
        f.rect(x + 50, 64, 30, 24, "ba" if var == "b" else "b", 0)
        f.text(x + 35, 81, "a", "tcs", "middle")
        f.text(x + 65, 81, "b", "tcs", "middle")
        f.text(x + 165, 81, "rest of the 64-byte line", "tcs", "middle")
    f.path("M320 70 C370 40 390 40 440 70", "aw", end="aha")
    f.path("M440 90 C390 120 370 120 320 90", "mw", end="ah")
    f.text(380, 30, "invalidate", "tcs", "middle")
    f.text(380, 130, "invalidate", "tcs", "middle")
    f.text(380, 170, "each write invalidates the other core's copy; the line ping-pongs across the chip", "tm", "middle")
    f.text(380, 190, "fix: pad or align so that a and b live in different cache lines", "tm", "middle")
    return f.svg()
