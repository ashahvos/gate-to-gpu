#!/usr/bin/env python3
"""Build Gate to GPU: authored modules (custom tags) -> one self-contained HTML page."""
import glob
import html
import json
import os
import re
import sys
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
sys.path.insert(0, SRC)

import dlib  # noqa: E402
import importlib  # noqa: E402

for modname in sorted(os.path.basename(p)[:-3] for p in glob.glob(os.path.join(SRC, "d[0-9]*.py"))):
    importlib.import_module(modname)

PARTS = {
    "1": ("I", "Foundations: information as bits", "How a voltage becomes a bit, how bits represent numbers and text, and how signed and real numbers are encoded and computed with."),
    "2": ("II", "Combinational logic", "Circuits whose outputs depend only on their present inputs: Boolean algebra, canonical forms, minimization, and the standard building blocks (decoders, multiplexers, adders, ALUs)."),
    "3": ("III", "Circuits and the physical layer", "The electrical reality under the logic: circuit laws, RC behavior and filters, analog building blocks, transistors and CMOS gates, and what it takes for two chips to talk."),
    "4": ("IV", "Sequential logic", "Circuits with memory: latches and flip-flops, registers and counters, state machines in hardware, and the timing rules every clocked design must meet."),
    "5": ("V", "Computer organization and architecture", "How datapaths and control become a processor, how performance is measured and improved with pipelining and caches, how memories and FPGAs are built, and how GPUs run thousands of threads."),
    "6": ("VI", "Embedded systems", "Programming a microcontroller at the register level: GPIO and bit manipulation in C, software state machines, interrupts and timers, and talking to devices over parallel and serial interfaces."),
    "7": ("VII", "Implementation", "Describing hardware in Verilog, and the power, thermal and manufacturing realities of turning a design into a chip."),
    "8": ("VIII", "Reference and practice", "A formula and fact sheet with a searchable glossary, then a large set of interview-style problems that draw on every part of the guide."),
}

TOOL_TITLES = {
    "numconv": "Number converter", "float": "Floating-point explorer", "gates": "Gate playground", "truthtable": "Truth table and simplifier",
    "kmap": "K-map solver", "adder": "4-bit adder and subtractor", "rcfilter": "RC filter explorer", "cmos": "CMOS switch-level explorer",
    "latchlab": "Latch vs flip-flop lab", "fsmgen": "Sequence detector generator", "timing": "Setup and hold slack calculator",
    "pipeline": "Pipeline hazard visualizer", "amdahl": "Amdahl's law", "cache": "Cache simulator", "bitfiddle": "Register bit-fiddling playground",
    "avrtimer": "AVR timer calculator",
}

DARK = """
    --paper: #1B1714; --sheet: #241F1B; --wash: #2D2722; --ink: #F2E9DC; --ink-2: #B8AB9B; --rule: #3A322B; --rule-2: #54493F;
    --dot: rgba(255, 228, 196, 0.11);
    --cardinal: #F0726A; --cardinal-ink: #1B1714; --cardinal-soft: #43201E; --cardinal-wash: #2E1D1B; --margin: rgba(240, 114, 106, 0.42);
    --btn: #B33A36; --btn-ink: #FFF3E6; --tab: #5E1A1D; --tab-ink: #F6E8D3;
    --cover: #3F0E10; --cover-ink: #F6E8D3; --cover-ink-2: #CFB19C; --cover-rule: rgba(255, 214, 170, 0.16);
    --cover-hover: rgba(255, 236, 214, 0.07); --cover-active: rgba(0, 0, 0, 0.3); --label: #2A241F;
    --gold: #FFCC00; --gold-deep: #FFCC00; --gold-ink: #FFD75A; --gold-soft: #3A3012; --hl: rgba(255, 204, 0, 0.3);
    --green: #8BCB96; --green-soft: #1E3326; --orange: #F49B5E; --orange-ink: #F7A872; --orange-soft: #3E2618;
    --plum: #D1A5E8; --plum-soft: #33243C; --brown: #D9A57E; --olive: #BFCB6E;
    --lv-intro: #C3B5A3; --lv-intro-soft: #2F2924; --lv-easy: #8BCB96; --lv-easy-soft: #1E3326;
    --lv-medium: #FFD75A; --lv-medium-soft: #3A3012; --lv-hard: #F0726A; --lv-hard-soft: #43201E;
    --ch1: #FF8F86; --ch2: #FFCC00; --ch3: #8BCB96; --ch4: #D1A5E8;
    --shadow: 0 10px 30px rgba(0, 0, 0, 0.6); --lift: 0 1px 1px rgba(0, 0, 0, 0.3), 0 12px 20px -12px rgba(0, 0, 0, 0.85);
    color-scheme: dark;"""

ESC = lambda s: html.escape(s, quote=True)  # noqa: E731
WARN = []


def warn(msg):
    WARN.append(msg)


def slug(s):
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:48] or "s"


def attrs(s):
    return {m.group(1): (m.group(2) if m.group(2) is not None else m.group(3) if m.group(3) is not None else "")
            for m in re.finditer(r'([\w-]+)(?:="([^"]*)"|=\'([^\']*)\')?', s)}


# ---------------- syntax highlighting ----------------
C_KW = set("""if else for while do switch case default break continue return goto sizeof typedef struct union enum static const volatile
extern inline register auto true false nullptr new delete class public private protected template typename namespace using this
operator virtual override constexpr noexcept static_cast reinterpret_cast const_cast dynamic_cast
__global__ __device__ __host__ __shared__ __syncthreads alignas""".split())
C_TY = set("""void char short int long float double signed unsigned bool size_t uint8_t uint16_t uint32_t uint64_t int8_t int16_t int32_t
int64_t uintptr_t intptr_t ptrdiff_t std string vector atomic mutex threadIdx blockIdx blockDim gridDim""".split())
V_KW = set("""module endmodule input output inout wire reg logic integer real always always_ff always_comb always_latch assign begin end if else
case casez casex endcase default posedge negedge or and not parameter localparam genvar generate endgenerate for initial function
endfunction task endtask signed unsigned typedef enum struct packed unique priority forever repeat while wait""".split())


def highlight(code, lang):
    code = textwrap.dedent(code).strip("\n")
    lines = code.split("\n")
    hl = set()
    for i, ln in enumerate(lines):
        if ln.rstrip().endswith("//!"):
            hl.add(i)
            lines[i] = ln.rstrip()[:-3].rstrip()
    code = "\n".join(lines)
    lang = (lang or "").lower()
    if lang in ("c", "cpp", "c++", "cuda"):
        pat = re.compile(r'(?P<c>//[^\n]*|/\*.*?\*/)|(?P<s>"(?:\\.|[^"\\\n])*"|\'(?:\\.|[^\'\\\n])+\')|(?P<pp>^[ \t]*#\w+[^\n]*)|'
                         r'(?P<n>\b(?:0[xX][0-9a-fA-F]+|0[bB][01]+|\d+\.?\d*(?:[eE][+-]?\d+)?)[uUlLfF]*\b)|(?P<id>[A-Za-z_]\w*)', re.S | re.M)
        kw, ty = C_KW, C_TY
    elif lang in ("v", "verilog", "sv", "systemverilog"):
        pat = re.compile(r'(?P<c>//[^\n]*|/\*.*?\*/)|(?P<s>"(?:\\.|[^"\\\n])*")|(?P<pp>`\w+|\$\w+)|'
                         r"(?P<n>\b\d*'[sS]?[bBoOdDhH][0-9a-fA-FxXzZ_?]+|\b\d+\b)|(?P<id>[A-Za-z_]\w*)", re.S)
        kw, ty = V_KW, set()
    elif lang in ("asm",):
        pat = re.compile(r"(?P<c>;[^\n]*)|(?P<n>\b(?:0x[0-9a-fA-F]+|\d+)\b)|(?P<id>[A-Za-z_]\w*)", re.S)
        kw, ty = set("ldi ld st sts lds sbi cbi sbis sbic in out rjmp jmp call rcall ret reti nop add adc sub and or eor inc dec push pop mov cli sei brne breq".split()), set()
    elif lang in ("riscv",):
        pat = re.compile(r"(?P<c>#[^\n]*)|(?P<n>-?\b(?:0x[0-9a-fA-F]+|\d+)\b)|(?P<id>[A-Za-z_][\w.]*)", re.S)
        kw, ty = set("add addi sub and andi or ori xor xori sll slli srl srli sra srai lw sw lb sb lh sh lbu lhu lui auipc beq bne blt bge bltu bgeu jal jalr mul div rem li mv ret call j nop".split()), set()
    else:
        pat, kw, ty = None, set(), set()
    out = []
    if pat is None:
        out = [ESC(code)]
    else:
        pos = 0
        for m in pat.finditer(code):
            out.append(ESC(code[pos:m.start()]))
            g = m.lastgroup
            t = m.group(0)
            if g == "id":
                if t in kw:
                    out.append(f'<span class="k">{ESC(t)}</span>')
                elif t in ty:
                    out.append(f'<span class="ty">{ESC(t)}</span>')
                else:
                    out.append(ESC(t))
            else:
                cls = {"c": "c", "s": "s", "pp": "pp", "n": "n"}[g]
                parts = t.split("\n")
                out.append("\n".join(f'<span class="{cls}">{ESC(p)}</span>' if p else "" for p in parts))
            pos = m.end()
        out.append(ESC(code[pos:]))
    res = "".join(out)
    if hl:
        rl = res.split("\n")
        for i in hl:
            if i < len(rl):
                rl[i] = f'<span class="hl">{rl[i]}</span>'
        res = "\n".join(rl)
    label = {"c": "C", "cpp": "C++", "c++": "C++", "cuda": "CUDA C++", "v": "Verilog", "verilog": "Verilog", "sv": "SystemVerilog",
             "systemverilog": "SystemVerilog", "asm": "AVR assembly", "riscv": "RISC-V assembly"}.get(lang, "")
    la = f' data-lang="{label}"' if label else ""
    return f"<pre{la}><code>{res}</code></pre>"


# ---------------- tables ----------------
def truth_table(head, body):
    h = head.split("|")
    ins = h[0].split()
    outs = h[1].split() if len(h) > 1 else []
    th = "".join(f"<th>{ESC(x)}</th>" for x in ins)
    th += "".join(f'<th class="o{" sep" if i == 0 else ""}">{ESC(x)}</th>' for i, x in enumerate(outs))
    rows = [r.strip() for r in re.split(r"[;\n]", body) if r.strip()]
    trs = []
    for r in rows:
        parts = r.split("|")
        a = parts[0].split()
        b = parts[1].split() if len(parts) > 1 else []
        if len(a) != len(ins) or len(b) != len(outs):
            warn(f"truth row mismatch: {r!r} for header {head!r}")
        td = "".join(f"<td>{x}</td>" for x in a)
        td += "".join(f'<td class="o{" v1" if x == "1" else ""}{" sep" if i == 0 else ""}">{x}</td>' for i, x in enumerate(b))
        trs.append(f"<tr>{td}</tr>")
    return f'<div class="tbl tt"><table><thead><tr>{th}</tr></thead><tbody>{"".join(trs)}</tbody></table></div>'


def grid_table(cls, body):
    rows = [r for r in body.strip("\n").split("\n") if r.strip()]
    def cells(r):
        return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", r)]
    head = cells(rows[0])
    th = "".join(f"<th>{c}</th>" for c in head)
    trs = []
    for r in rows[1:]:
        cs = cells(r)
        if len(cs) != len(head):
            warn(f"grid row has {len(cs)} cells, header has {len(head)}: {r[:60]!r}")
        trs.append("<tr>" + "".join(f"<td>{c}</td>" for c in cs) + "</tr>")
    c = ("tbl " + cls).strip()
    return f'<div class="{c}"><table><thead><tr>{th}</tr></thead><tbody>{"".join(trs)}</tbody></table></div>'


# ---------------- module conversion ----------------
NOTE_LABEL = {"key": "Key idea", "warn": "Common mistake", "ex": "Worked example", "prac": "In practice", "analogy": "Analogy"}


def convert(src, mid, modmeta, stash):
    def keep(htmltext):
        stash.append(htmltext)
        return f"@@K{len(stash) - 1}@@"

    # glossary-only terms: <gterm t="Term" to="module-id">definition</gterm>
    def gterm(m):
        a = attrs(m.group(1))
        gterms.append((a.get("t", "?"), a.get("to", ""), convert_inline(m.group(2).strip()), mid))
        return ""
    src = re.sub(r"<gterm\s+([^>]*)>(.*?)</gterm>", gterm, src, flags=re.S)
    # code blocks
    src = re.sub(r'<pre(?:\s+lang="([^"]*)")?>(.*?)</pre>', lambda m: keep(highlight(m.group(2), m.group(1))), src, flags=re.S)
    # waves
    def wave(m):
        raw = m.group(1).strip()
        try:
            json.loads(raw)
        except Exception as e:  # noqa: BLE001
            warn(f"[{mid}] bad wave JSON: {e}: {raw[:80]}")
        return keep(f'<div class="wave" data-wave="{ESC(raw)}"></div>')
    src = re.sub(r"<wave>(.*?)</wave>", wave, src, flags=re.S)
    # generated waves: <wavegen name="..." args='{...}'>caption</wavegen>
    def wavegen(m):
        a = attrs(m.group(1))
        name = a.get("name")
        fn = dlib.WAVES.get(name)
        if not fn:
            warn(f"[{mid}] unknown wavegen {name}")
            return keep(f'<p class="werr">Missing timing diagram {ESC(name or "")}</p>')
        kw = json.loads(a["args"]) if a.get("args") else {}
        spec = fn(**kw)
        cap = m.group(2).strip()
        if cap:
            spec["cap"] = convert_inline(cap)
        return keep(f'<div class="wave" data-wave="{ESC(json.dumps(spec, ensure_ascii=False))}"></div>')
    src = re.sub(r"<wavegen\s+([^>]*?)>(.*?)</wavegen>", wavegen, src, flags=re.S)
    # diagrams
    def diag(m):
        a = attrs(m.group(1))
        cap = m.group(2).strip()
        name = a.get("name")
        fn = dlib.REGISTRY.get(name)
        if not fn:
            warn(f"[{mid}] unknown diagram {name}")
            return keep(f'<p class="werr">Missing diagram {ESC(name or "")}</p>')
        kw = json.loads(a["args"]) if a.get("args") else {}
        svg = fn(**kw)
        stats["diagrams"] += 1
        return keep(dlib.figure(svg, convert_inline(cap)))
    src = re.sub(r"<diagram\s+([^>]*?)>(.*?)</diagram>", diag, src, flags=re.S)
    # tables
    src = re.sub(r'<truth\s+h="([^"]*)">(.*?)</truth>', lambda m: keep(convert_inline(truth_table(m.group(1), m.group(2)))), src, flags=re.S)
    src = re.sub(r'<grid(?:\s+cls="([^"]*)")?>(.*?)</grid>', lambda m: keep(convert_inline(grid_table(m.group(1) or "", m.group(2)))), src, flags=re.S)
    src = convert_inline(src)
    # practice blocks
    pids = set()
    def practice(m):
        title = m.group(1) or "Practice problems"
        pid = f"{mid}-practice" if not m.group(1) else f"{mid}-{slug(title)}"
        while pid in pids:
            pid += "-2"
        pids.add(pid)
        return (f'<div class="practice"><div class="practice-head"><h3 id="{pid}">{title}</h3>'
                f'<span class="pcount"></span><button class="btn sm ghost showall" type="button">Show all solutions</button></div><div class="probs">')
    src = re.sub(r"<practice(?:\s+title=\"([^\"]*)\")?>", practice, src)
    src = src.replace("</practice>", '<p class="empty-msg" hidden>No problems here match the current filter.</p></div></div>')
    def prob(m):
        a = attrs(m.group(1) or "")
        lvl = a.get("level", "easy")
        if lvl not in ("intro", "easy", "medium", "hard"):
            warn(f"[{mid}] bad level {lvl}")
        stats["levels"][lvl] = stats["levels"].get(lvl, 0) + 1
        modmeta["probs"] += 1
        t = f' data-tags="{ESC(a["tags"])}"' if a.get("tags") else ""
        return f'<article class="prob" data-level="{lvl}"{t}>'
    src = re.sub(r"<prob(\s[^>]*)?>", prob, src)
    src = src.replace("</prob>", "</article>")
    src = src.replace("<ask>", '<div class="q">').replace("</ask>", "</div>")
    src = re.sub(r"<hint(?:\s+label=\"([^\"]*)\")?>", lambda m: f'<details class="hint"><summary>{m.group(1) or "Hint"}</summary><div class="dbody">', src)
    src = src.replace("</hint>", "</div></details>")
    src = re.sub(r"<sol(?:\s+label=\"([^\"]*)\")?>", lambda m: f'<details class="sol"><summary>{m.group(1) or "Solution"}</summary><div class="dbody">', src)
    src = src.replace("</sol>", "</div></details>")
    # notes
    def note(m):
        kind = m.group(1)
        a = attrs(m.group(2) or "")
        if kind == "def":
            term = a.get("term", "Definition")
            did = "def-" + slug(term)
            if did in defs_seen:
                did += "-" + mid
            defs_seen.add(did)
            glossary.append((term, did, mid))
            return f'<aside class="note def" id="{did}" data-term="{ESC(term)}"><p class="note-t">{ESC(term)}</p>'
        label = a.get("title") if kind != "ex" else NOTE_LABEL[kind]
        label = label or NOTE_LABEL[kind]
        extra = ""
        if kind == "ex" and a.get("title"):
            extra = f'<p class="ex-title"><b>{a["title"]}</b></p>'
        return f'<aside class="note {kind}"><p class="note-t">{label}</p>{extra}'
    src = re.sub(r"<(key|warn|ex|prac|analogy|def)(\s[^>]*)?>", note, src)
    src = re.sub(r"</(key|warn|ex|prac|analogy|def)>", "</aside>", src)
    src = re.sub(r'<deeper\s+title="([^"]*)">', lambda m: f'<details class="deeper"><summary>{m.group(1)} <small>going deeper</small></summary><div class="dd">', src)
    src = src.replace("</deeper>", "</div></details>")
    # tools
    def tool(m):
        name = m.group(1)
        if name not in TOOL_TITLES:
            warn(f"[{mid}] unknown tool {name}")
        modmeta["tools"].append(name)
        stats["tools"] += 1
        return f'<div class="widget" data-tool="{name}" id="tool-{name}" data-title="{ESC(TOOL_TITLES.get(name, name))}"></div>'
    src = re.sub(r'<tool\s+name="(\w+)"\s*/>', tool, src)
    # misc inline
    src = re.sub(r"<eq(\s+c)?>", lambda m: '<div class="eq c">' if m.group(1) else '<div class="eq">', src)
    src = src.replace("</eq>", "</div>")
    # h3 ids
    used = set()
    def h3(m):
        a = m.group(1) or ""
        if "id=" in a:
            return m.group(0)
        sid = f"{mid}-{slug(m.group(2))}"
        while sid in used:
            sid += "-2"
        used.add(sid)
        return f'<h3 id="{sid}"{a}>{m.group(2)}</h3>'
    src = re.sub(r"<h3(\s[^>]*)?>(.*?)</h3>", h3, src)
    return src


def convert_inline(s):
    s = re.sub(r"`([^`\n]+)`", lambda m: f"<code>{ESC(html.unescape(m.group(1)))}</code>", s)
    s = re.sub(r"<m>(.*?)</m>", r'<span class="m">\1</span>', s, flags=re.S)
    s = re.sub(r"<ov>(.*?)</ov>", r'<span class="ov">\1</span>', s)
    s = re.sub(r"<frac>(.*?)\|\|(.*?)</frac>", r'<span class="frac"><span>\1</span><span>\2</span></span>', s)
    return s


SUP_MAP = dict(zip("⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿⁱ", "0123456789+−=()ni"))
SUB_MAP = dict(zip("₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑₒₓₙ", "0123456789+−=()aeoxn"))


def unicode_scripts_to_tags(body):
    """Web-font subsets cover only ¹ ² ³ among the Unicode superscripts and none of the subscripts, so the rest
    would fall back to another font. Rewrite every run in running text as <sup>/<sub> so all exponents and
    indices look alike (SVG, code blocks and attributes are left alone)."""
    sup_re = re.compile("[" + "".join(SUP_MAP) + "]+")
    sub_re = re.compile("[" + "".join(SUB_MAP) + "]+")

    def fix_text(t):
        t = sup_re.sub(lambda m: "<sup>" + "".join(SUP_MAP[c] for c in m.group(0)) + "</sup>", t)
        return sub_re.sub(lambda m: "<sub>" + "".join(SUB_MAP[c] for c in m.group(0)) + "</sub>", t)

    out = []
    for seg in re.split(r"(<(?:svg|pre|script|style|textarea)\b.*?</(?:svg|pre|script|style|textarea)>)", body, flags=re.S):
        if re.match(r"<(?:svg|pre|script|style|textarea)\b", seg):
            out.append(seg)
            continue
        parts = re.split(r"(<[^>]+>)", seg)
        out.append("".join(p if p.startswith("<") else fix_text(p) for p in parts))
    return "".join(out)


def restore(s, stash):
    for _ in range(3):
        s2 = re.sub(r"@@K(\d+)@@", lambda m: stash[int(m.group(1))], s)
        if s2 == s:
            break
        s = s2
    return s


stats = {"diagrams": 0, "tools": 0, "levels": {}}
glossary = []
gterms = []
defs_seen = set()


def main():
    files = sorted(glob.glob(os.path.join(SRC, "modules", "*.html")))
    mods = []
    for fp in files:
        raw = open(fp, encoding="utf-8").read()
        m = re.search(r"<module\s+([^>]*)>(.*)</module>", raw, flags=re.S)
        if not m:
            warn(f"no module tag in {fp}")
            continue
        a = attrs(m.group(1))
        mods.append({"a": a, "body": m.group(2), "file": os.path.basename(fp), "probs": 0, "tools": []})
    ids = {md["a"]["id"]: md for md in mods}
    numbered = [md for md in mods if md["a"].get("num", "0").isdigit() and md["a"].get("num") != "0"]
    total_num = max([int(md["a"]["num"]) for md in numbered] or [0])
    out_sections = []
    seen_parts = set()
    stash = []
    converted = []
    for md in mods:
        md["html"] = convert(md["body"], md["a"]["id"], md, stash)
        converted.append(md)
    # refs need module numbers, so resolve after conversion
    all_ids = set(ids) | set(re.findall(r'id="([^"]+)"', "".join(md["html"] for md in converted) + "".join(stash)))
    all_ids |= {f"part-{p}" for p in PARTS} | {"top"} | {f"tool-{t}" for t in TOOL_TITLES}

    def ref(m):
        a = attrs(m.group(1))
        to = a.get("to", "")
        tgt = ids.get(to)
        if tgt:
            n = tgt["a"].get("num")
            txt = a.get("t") or (f"Module {n}" if n and n != "0" else tgt["a"]["title"])
            if "full" in a:
                txt = f"Module {n}, {tgt['a']['title']}"
            return f'<a href="#{to}">{txt}</a>'
        txt = a.get("t") or to
        if to not in all_ids:
            warn(f"ref to unknown id {to}")
        return f'<a href="#{to}">{txt}</a>'
    for md in converted:
        a = md["a"]
        mid = a["id"]
        part = a.get("part")
        if part and part not in seen_parts:
            seen_parts.add(part)
            roman, pname, pintro = PARTS[part]
            plist = "".join(
                f'<li><a href="#{x["a"]["id"]}"><span class="nnum">{x["a"]["num"].zfill(2) if x["a"].get("num", "").isdigit() else ESC(x["a"].get("nav") or x["a"].get("badge", ""))}</span><span>{ESC(x["a"]["title"])}</span></a></li>'
                for x in mods if x["a"].get("part") == part)
            out_sections.append(f'<section class="part" id="part-{part}" data-roman="{roman}" data-name="{ESC(pname)}"><p class="rn">Part {roman}</p>'
                                f'<h2>{ESC(pname)}</h2><p>{pintro}</p><ol class="part-mods">{plist}</ol></section>')
        body = re.sub(r"<ref\s+([^>]*?)/>", ref, md["html"])
        body = restore(body, stash)
        body = re.sub(r"<ref\s+([^>]*?)/>", ref, body)
        num = a.get("num", "0")
        badge = a.get("badge")
        title = a["title"]
        short = a.get("short", "")
        blurb = a.get("blurb", "")
        pre = [p.strip() for p in a.get("pre", "").split(",") if p.strip()]
        pre_links = ", ".join(f'<a href="#{p}">{ESC(ids[p]["a"].get("short") or ids[p]["a"]["title"])}</a>' for p in pre if p in ids)
        for p in pre:
            if p not in ids:
                warn(f"[{mid}] unknown prerequisite {p}")
        tools = ", ".join(f'<a href="#tool-{t}">{ESC(TOOL_TITLES.get(t, t))}</a>' for t in dict.fromkeys(md["tools"]))
        metas = []
        if pre_links:
            metas.append(f"<span><b>Builds on</b>{pre_links}</span>")
        if tools:
            metas.append(f"<span><b>Tools</b>{tools}</span>")
        if md["probs"]:
            metas.append(f"<span><b>Practice</b>{md['probs']} problems</span>")
        meta_html = f'<div class="tb-meta">{"".join(metas)}</div>' if metas else ""
        if badge and a.get("nav"):
            sub = a.get("numsub") or (f"{md['probs']} problems" if md["probs"] else "")
            numcell = f'<div class="tb-num"><span>{ESC(badge)}</span><b>{ESC(a["nav"])}</b><small>{ESC(sub)}</small></div>'
        elif badge:
            numcell = f'<div class="tb-num tb-badge"><b>{ESC(badge)}</b></div>'
        else:
            numcell = f'<div class="tb-num"><span>Module</span><b>{num.zfill(2)}</b><small>of {total_num}</small></div>'
        partline = ""
        if part:
            roman, pname, _ = PARTS[part]
            partline = f'<p class="tb-part"><a href="#part-{part}">Part {roman}: {ESC(pname)}</a></p>'
        extra_attr = f' data-badge="{ESC(badge)}"' if badge else ""
        if a.get("nav"):
            extra_attr += f' data-nav="{ESC(a["nav"])}"'
        if a.get("pfx"):
            extra_attr += f' data-pfx="{ESC(a["pfx"])}"'
        head = (f'<section class="module" id="{mid}" data-num="{ESC(num)}" data-title="{ESC(title)}" data-short="{ESC(short)}"{extra_attr}>'
                f'<header class="mhead"><div class="tblock">{numcell}<div class="tb-main">{partline}<h2>{ESC(title)}</h2>'
                f'<p class="tb-blurb">{blurb}</p></div>{meta_html}</div></header>')
        out_sections.append(head + body + "</section>")
    page_body = "\n".join(out_sections)
    # glossary
    if "<glossary/>" in page_body:
        entries = []
        for term, did, mid in glossary:
            if mid == "start":          # the sample callout on the start page
                continue
            mm = re.search(r'<aside class="note def" id="' + re.escape(did) + r'"[^>]*><p class="note-t">.*?</p>(.*?)</aside>', page_body, flags=re.S)
            raw = mm.group(1) if mm else ""
            keep_html = re.sub(r"<(?!/?(?:sub|sup|code|i|b)\b)[^>]+>", "", raw).strip()
            keep_html = re.sub(r"\s+", " ", keep_html)
            plain = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", raw))).strip()
            if len(plain) > 300:
                plain = plain[:297].rsplit(" ", 1)[0] + "…"
                entries.append((term, f"#{did}", ESC(plain), mid, False))
            else:
                entries.append((term, f"#{did}", keep_html, mid, False))
        for term, to, htmltxt, _mid in gterms:
            if to not in ids:
                warn(f"glossary term {term!r} links to unknown module {to}")
            entries.append((term, f"#{to}", htmltxt, to, True))
        seen_terms = {}
        for e in entries:
            k = e[0].lower()
            if k in seen_terms:
                warn(f"glossary term defined twice: {e[0]!r}")
            seen_terms[k] = 1
        entries.sort(key=lambda e: re.sub(r"^[^a-z0-9]+", "", e[0].lower()))
        items, gl_ids = [], set()
        for term, href, txt, where, isg in entries:
            gid = "gl-" + slug(term)
            while gid in gl_ids:
                gid += "-2"
            gl_ids.add(gid)
            tgt = ids.get(where)
            label = ""
            if tgt:
                n = tgt["a"].get("num", "")
                label = f"Module {n}" if n.isdigit() and n != "0" else tgt["a"].get("short") or tgt["a"]["title"]
            where_html = f' <a class="gl-where" href="{href}">{ESC(label)}</a>' if label else ""
            gattr = ' data-g="1"' if isg else ""
            items.append(f'<div class="gl-item" id="{gid}"{gattr}><dt><a href="{href}">{ESC(term)}</a></dt><dd>{txt}{where_html}</dd></div>')
        gl_html = ('<div class="gl-wrap"><label class="gl-find"><span>Filter</span>'
                   '<input type="search" placeholder="Part of a term or its definition, such as hold or cache" aria-label="Filter the glossary"></label>'
                   f'<p class="gl-count">{len(items)} terms</p><dl class="glossary">{"".join(items)}</dl>'
                   '<p class="gl-none" hidden>No glossary entries match. Try a shorter word.</p></div>')
        page_body = page_body.replace("<glossary/>", gl_html)
        print(f"glossary: {len(items)} terms ({sum(1 for e in entries if e[4])} glossary-only)")
    page_body = unicode_scripts_to_tags(page_body)
    # tag balance checks
    for tag in ("aside", "details", "div", "article", "section", "table", "ul", "ol", "p", "figure", "pre", "code", "span", "b", "i", "a", "li"):
        o = len(re.findall(rf"<{tag}[\s>]", page_body))
        c = len(re.findall(rf"</{tag}>", page_body))
        if o != c:
            warn(f"tag imbalance <{tag}>: {o} open vs {c} close")
    for leftover in ("<wavegen", "<prob", "<ask>", "<sol>", "<hint", "<key>", "<warn>", "<tool ", "<wave>", "<diagram", "<truth", "<grid", "<m>", "<ref ", "<def ", "<ex ", "<prac>", "@@K"):
        if leftover in page_body:
            warn(f"unconverted markup: {leftover}")
    style = open(os.path.join(SRC, "style.css"), encoding="utf-8").read()
    dark = ("@media (prefers-color-scheme: dark) {\n  :root:not([data-theme=\"light\"]) {" + DARK + "\n  }\n}\n:root[data-theme=\"dark\"] {" + DARK + "\n}")
    style = style.replace("/*DARK*/", dark)
    nprob = sum(md["probs"] for md in mods)
    nint = sum(md["probs"] for md in mods if md["a"]["id"] == "interview")
    nmods = len(numbered)
    hero = (f"<b>{nmods} modules</b>, <b>{nprob - nint} practice problems</b>, <b>{nint} interview problems</b>, "
            f"<b>{stats['tools']} interactive tools</b> and <b>{stats['diagrams']} diagrams</b>. Progress you mark is saved in this browser.")
    top = open(os.path.join(SRC, "shell_top.html"), encoding="utf-8").read()
    top = top.replace("{{STYLE}}", style).replace("{{NPROB}}", str(nprob)).replace("{{HEROMETA}}", hero)
    js = "".join(open(os.path.join(SRC, "js", f), encoding="utf-8").read() + "\n" for f in ("core.js", "tools_a.js", "tools_b.js", "init.js"))
    page = top + page_body + "\n  </main>\n</div>\n<script>\n(function () {\n\"use strict\";\n" + js + "})();\n</script>\n"
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    outp = os.path.join(HERE, "out", "gate-to-gpu.html")
    open(outp, "w", encoding="utf-8").write(page)
    # A complete, standalone page for any static host such as GitHub Pages: add the document skeleton
    # (charset, viewport, a small reset) that the artifact viewer otherwise supplies.
    cut = page.index("</style>") + len("</style>")
    head = page[:cut].replace('<meta name="claude:viewport-fit-sides" content="cover">\n', "")
    reset = ('<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}'
             'body{margin:0}img{max-width:100%}[hidden]:not([hidden=until-found i]){display:none!important}</style>\n')
    standalone = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
                  '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                  + reset + head + "\n</head>\n<body>" + page[cut:] + "</body>\n</html>\n")
    os.makedirs(os.path.join(HERE, "docs"), exist_ok=True)
    open(os.path.join(HERE, "docs", "index.html"), "w", encoding="utf-8").write(standalone)
    open(os.path.join(HERE, "docs", ".nojekyll"), "w").close()
    print(f"wrote {outp} and docs/index.html: {len(page) / 1024:.0f} KB, {len(mods)} sections, {nprob} problems {stats['levels']}, {stats['tools']} tools, {stats['diagrams']} diagrams")
    for md in mods:
        print(f"  {md['a']['id']:<12} {md['probs']:>3} problems  tools={','.join(md['tools'])}")
    if WARN:
        print("WARNINGS:")
        for w in WARN:
            print("  -", w)


if __name__ == "__main__":
    main()
