"""Part VI diagrams and timing diagrams: microcontrollers, GPIO, software FSMs, interrupts, timers, serial interfaces."""
import math
from dlib import Fig, diagram, fmt, wave
from d3 import term, chip
from d4 import latch_box


# ======================================================================
# Module 23: microcontrollers and GPIO
# ======================================================================
@diagram("mcu_block")
def mcu_block():
    f = Fig(780, 300, "Inside a microcontroller: a CPU core, flash and SRAM, and peripherals, all connected by an internal bus")
    f.rect(20, 20, 740, 260, "bg", 10)
    f.text(36, 42, "ATmega328P-class microcontroller", "tb")
    f.block(40, 60, 130, 70, "AVR CPU", "8-bit, 16 MHz", "bs")
    f.block(190, 60, 120, 32, "flash 32 KB", None, "b", tcls="tcs")
    f.block(190, 98, 120, 32, "SRAM 2 KB", None, "b", tcls="tcs")
    f.block(330, 60, 120, 32, "EEPROM 1 KB", None, "b", tcls="tcs")
    f.block(330, 98, 120, 32, "clock, reset", None, "b", tcls="tcs")
    f.line([(40, 152), (740, 152)], "hw", extra=' style="stroke-width:5"')
    f.text(470, 146, "internal bus: registers are memory-mapped", "tcs tcol")
    for x in (105, 250, 390):
        f.line([(x, 130), (x, 152)], "hw")
    per = (("GPIO ports", "B, C, D"), ("timers", "0, 1, 2"), ("ADC", "10-bit, 8 ch"), ("USART", "serial"), ("SPI", ""), ("TWI (I²C)", ""), ("interrupt", "controller"))
    for i, (a, b) in enumerate(per):
        x = 40 + i * 100
        f.block(x, 176, 90, 50, a, b or None, "ba", tcls="tcs")
        f.line([(x + 45, 152), (x + 45, 176)], "hw")
    f.text(400, 258, "pins are shared: each physical pin is a GPIO bit or a peripheral function (TX, SCK, ADC input…)", "tm", "middle")
    return f.svg()


@diagram("gpio_pin")
def gpio_pin():
    f = Fig(780, 350, "Inside one AVR GPIO pin: the DDR bit enables the output driver, the PORT bit sets the output value or the pull-up, and PIN reads the synchronized pin voltage")
    f.block(40, 40, 110, 40, "DDRx bit", "1 = output", "bs")
    f.block(40, 120, 110, 40, "PORTx bit", "value / pull-up", "bs")
    f.block(40, 230, 110, 40, "PINx bit", "read only", "bs")
    tri_x, tri_y = 420, 125
    f.path(f"M{tri_x} {tri_y} L{tri_x + 40} {tri_y + 15} L{tri_x} {tri_y + 30} Z", "b")
    f.line([(150, 140), (tri_x, 140)])
    f.line([(150, 60), (440, 60), (440, tri_y + 8)])
    f.text(446, 100, "enable", "tcs")
    f.line([(tri_x + 40, 140), (620, 140)])
    f.rect(620, 122, 36, 36, "ba", 4)
    f.text(638, 145, "pin", "tcs", "middle")
    f.text(638, 176, "physical pin", "tcs", "middle")
    f.supply(560, 40)
    f.add('<g>')
    f.resistor(560, 48, 560, 100, None)
    f.add('</g>')
    f.text(574, 76, "pull-up", "tcs")
    f.text(574, 90, "20–50 kΩ", "tcs")
    f.line([(560, 100), (560, 108)])
    f.dot(560, 108, 3)
    f.line([(560, 108), (574, 120)], "w")
    f.dot(560, 140)
    f.line([(560, 124), (560, 140)])
    f.text(590, 112, "on if DDR = 0 and PORT = 1", "tcs tcol")
    f.dot(600, 140)
    f.line([(600, 140), (600, 250), (470, 250)])
    f.path("M470 238 L430 250 L470 262 Z", "b")
    f.text(474, 284, "Schmitt input", "tcs")
    f.rect(270, 232, 120, 36, "b", 4)
    f.text(330, 254, "2-FF synchronizer", "tcs", "middle")
    f.line([(430, 250), (390, 250)])
    f.line([(270, 250), (150, 250)], "w", end="ah")
    f.text(210, 244, "PINx", "tcs", "middle")
    f.text(24, 304, "DDR = 0, PORT = 0: input, floating (high impedance)", "tcs")
    f.text(24, 320, "DDR = 0, PORT = 1: input with pull-up", "tcs")
    f.text(24, 336, "DDR = 1: output, driving the PORT value", "tcs")
    return f.svg()


@diagram("bitmask_ops")
def bitmask_ops():
    f = Fig(780, 300, "The four basic bit operations on an 8-bit register with the mask for bit 4")
    rows = (("register", "10100110", None), ("mask = 1 << 4", "00010000", None),
            ("set:    x | mask", "10110110", "bit 4 forced to 1"), ("clear:  x & ~mask", "10100110", "bit 4 forced to 0 (already 0)"),
            ("toggle: x ^ mask", "10110110", "bit 4 inverted"), ("test:   x & mask", "00000000", "zero, so bit 4 was 0"))
    for i, (lab, bits, note) in enumerate(rows):
        y = 26 + i * 44
        f.text(20, y + 22, lab, "tc")
        for k, b in enumerate(bits):
            hl = (k == 3)
            cls = "ba" if hl else ("bs" if i == 1 and b == "1" else "b")
            f.rect(250 + k * 34, y, 34, 30, cls, 0)
            f.text(267 + k * 34, y + 20, b, "tc", "middle")
        if note:
            f.text(540, y + 20, note, "tm")
        if i == 1:
            f.line([(20, y + 38), (760, y + 38)], "gridl")
    for k in range(8):
        f.text(267 + k * 34, 20, str(7 - k), "tcs", "middle")
    return f.svg()


@diagram("copy_bits")
def copy_bits():
    f = Fig(780, 260, "Copying bits 7 to 5 of one register into bits 5 to 3 of another without disturbing the other bits")
    def bits_row(y, label, cells, hl=(), cls_hl="ba"):
        f.text(20, y + 20, label, "tc")
        for k, b in enumerate(cells):
            cls = cls_hl if k in hl else "b"
            f.rect(300 + k * 34, y, 34, 30, cls, 0)
            f.text(317 + k * 34, y + 20, b, "tc", "middle")
    bits_row(20, "PORTC", ["c7", "c6", "c5", "c4", "c3", "c2", "c1", "c0"], hl=(0, 1, 2))
    bits_row(70, "PORTC >> 2", ["0", "0", "c7", "c6", "c5", "c4", "c3", "c2"], hl=(2, 3, 4))
    bits_row(120, "(PORTC >> 2) & 0x38", ["0", "0", "c7", "c6", "c5", "0", "0", "0"], hl=(2, 3, 4))
    bits_row(170, "PORTB & ~0x38", ["b7", "b6", "0", "0", "0", "b2", "b1", "b0"], hl=(2, 3, 4), cls_hl="bs")
    bits_row(220, "OR of the two", ["b7", "b6", "c7", "c6", "c5", "b2", "b1", "b0"], hl=(2, 3, 4))
    f.text(590, 40, "1. shift the source", "tm")
    f.text(590, 56, "into position", "tm")
    f.text(590, 140, "2. mask the source", "tm")
    f.text(590, 190, "3. clear the destination", "tm")
    f.text(590, 240, "4. OR them together", "tm")
    return f.svg()


@diagram("uno_map")
def uno_map():
    f = Fig(780, 230, "How the Arduino Uno's labeled pins map onto ATmega328P port bits")
    groups = (("PORTD", [f"PD{i}" for i in range(7, -1, -1)], [f"D{i}" for i in range(7, -1, -1)]),
              ("PORTB", ["PB7", "PB6"] + [f"PB{i}" for i in range(5, -1, -1)], ["XTAL", "XTAL", "D13", "D12", "D11", "D10", "D9", "D8"]),
              ("PORTC", ["PC7", "PC6"] + [f"PC{i}" for i in range(5, -1, -1)], ["—", "RESET", "A5", "A4", "A3", "A2", "A1", "A0"]))
    for g, (name, bits, labels) in enumerate(groups):
        y = 30 + g * 66
        f.text(20, y + 22, name, "tb")
        for k, (b, l) in enumerate(zip(bits, labels)):
            special = l in ("XTAL", "RESET", "—")
            f.rect(110 + k * 80, y, 80, 30, "bg" if special else "bs", 0)
            f.text(150 + k * 80, y + 20, b, "tcs", "middle")
            f.text(150 + k * 80, y + 46, l, "tcs tcol" if not special else "tcs", "middle")
    return f.svg()


# ---------------- waves ----------------
@wave("bounce")
def w_bounce():
    v = [[0, 1], [20, 0], [21.5, 1], [23, 0], [25.5, 1], [26.5, 0], [70, 1], [71, 0], [72.5, 1], [74, 0], [75, 1]]
    return {"end": 110, "grid": [], "noTicks": True, "shade": [[20, 27, "bounce", 3], [70, 75.5, "bounce", 3]],
            "signals": [{"n": "contact", "v": v, "c": 1},
                        {"n": "debounced", "v": [[0, 1], [32, 0], [81, 1]], "c": 2}],
            "marks": [[32, "after 5 ms stable"], [81, ""]],
            "alt": "A mechanical button bounces for a few milliseconds on press and release; the debounced signal changes once each"}


# ======================================================================
# Module 24: software state machines
# ======================================================================
@diagram("washer_fsm")
def washer_fsm():
    f = Fig(780, 340, "A washing machine controller as a state machine with a rinse counter")
    st = {"IDLE": dict(x=110, y=150, lines=["IDLE"]), "FILL": dict(x=300, y=150, lines=["FILL", "valve on"], cls="ba"),
          "AGITATE": dict(x=500, y=150, lines=["AGITATE", "motor on"], cls="ba"), "DRAIN": dict(x=690, y=150, lines=["DRAIN", "pump on"], cls="ba")}
    ed = [dict(a="IDLE", b="IDLE", label="else", ang=-90), dict(a="IDLE", b="FILL", label="PAID·LID", bend=-24),
          dict(a="FILL", b="FILL", label="FULL′", ang=-90), dict(a="FILL", b="AGITATE", label="FULL / start T", bend=-24),
          dict(a="AGITATE", b="AGITATE", label="T′", ang=-90), dict(a="AGITATE", b="DRAIN", label="T", bend=-24),
          dict(a="DRAIN", b="DRAIN", label="EMPTY′", ang=-90),
          dict(a="DRAIN", b="FILL", label="EMPTY·(N > 0) / N ← N − 1", bend=-70, off=12),
          dict(a="DRAIN", b="IDLE", label="EMPTY·(N = 0)", bend=-170, off=14)]
    f.fsm(st, ed, r=40, reset=("IDLE", 180))
    f.text(390, 330, "T: the 5-minute timer has expired; N: rinse cycles remaining", "tm", "middle")
    return f.svg(min_width=600)


@diagram("superloop")
def superloop():
    f = Fig(780, 200, "The structure of a software state machine: one loop iteration per time step, with exactly one delay")
    steps = ("read inputs", "next state and outputs", "write outputs", "delay one tick")
    for i, s in enumerate(steps):
        x = 40 + i * 180
        f.block(x, 60, 150, 50, s, None, "bs" if i != 3 else "ba", tcls="tcs")
        if i < 3:
            f.line([(x + 150, 85), (x + 180, 85)], "w", end="ah")
    f.line([(670, 110), (670, 150), (115, 150), (115, 110)], "w", end="ah")
    f.text(392, 170, "while (1) { … } — every task gets a short turn on every tick; nothing waits in a long blocking loop", "tm", "middle")
    return f.svg()


# ======================================================================
# Module 25: interrupts and timers
# ======================================================================
@diagram("isr_timeline")
def isr_timeline():
    f = Fig(780, 230, "Handling an interrupt: the current instruction finishes, the processor saves its place and runs the ISR, then resumes")
    y = 90
    f.rect(40, y, 260, 34, "bs", 4)
    f.text(170, y + 22, "main program", "tcs", "middle")
    f.rect(300, y, 50, 34, "bg", 4)
    f.text(325, y + 22, "save", "tcs", "middle")
    f.rect(350, y, 200, 34, "ba", 4)
    f.text(450, y + 22, "ISR (interrupts disabled)", "tcs", "middle")
    f.rect(550, y, 50, 34, "bg", 4)
    f.text(575, y + 22, "reti", "tcs", "middle")
    f.rect(600, y, 140, 34, "bs", 4)
    f.text(670, y + 22, "main resumes", "tcs", "middle")
    f.line([(270, 40), (270, y)], "rw", end="ah")
    f.text(270, 32, "event: flag set", "tcs tr", "middle")
    f.text(300, y + 56, "finish current instruction,", "tcs", "middle")
    f.text(300, y + 70, "push PC, clear I bit,", "tcs", "middle")
    f.text(300, y + 84, "jump via vector table", "tcs", "middle")
    f.text(575, y + 56, "pop PC,", "tcs", "middle")
    f.text(575, y + 70, "set I bit", "tcs", "middle")
    f.line([(40, 200), (740, 200)], "wt", end="ah")
    f.text(740, 218, "time", "tcs", "end")
    return f.svg()


@diagram("timer_ctc")
def timer_ctc():
    f = Fig(780, 270, "A timer in CTC mode: the counter climbs to the compare value, matches, sets the flag and restarts from zero")
    X0, Y0, W, H = 80, 30, 600, 170
    f.path(f"M{X0} {Y0} V{Y0 + H} H{X0 + W}", "wt")
    top = 0.8
    f.line([(X0, Y0 + H - top * H), (X0 + W, Y0 + H - top * H)], "dashc")
    f.text(X0 - 6, Y0 + H - top * H + 4, "OCR1A", "tcs tcol", "end")
    f.text(X0 - 6, Y0 + H + 4, "0", "tcs", "end")
    per = 150
    pts = []
    for k in range(4):
        x = X0 + k * per
        pts += [(x, Y0 + H), (x + per - 1, Y0 + H - top * H)]
    f.line(pts, "hw")
    for k in range(1, 5):
        x = X0 + k * per
        if x <= X0 + W:
            f.line([(x, Y0 + H), (x, Y0 + H + 14)], "aw")
            f.text(x, Y0 + H + 28, "match: OCF1A set", "tcs ta", "middle")
    f.text(X0 + 8, Y0 + 14, "TCNT1", "tcs")
    f.dim(X0, X0 + per, Y0 + H + 44, "period = (OCR1A + 1) × N / f_{clk}", above=False)
    return f.svg()


@diagram("pwm_fast")
def pwm_fast():
    f = Fig(780, 280, "Fast PWM: the counter ramps from 0 to TOP; the output is high from the start of each period until the counter passes the compare value")
    X0, Y0, W, H = 80, 20, 600, 130
    f.path(f"M{X0} {Y0} V{Y0 + H} H{X0 + W}", "wt")
    per = 150
    pts = []
    for k in range(4):
        x = X0 + k * per
        pts += [(x, Y0 + H), (x + per - 1, Y0)]
    f.line(pts, "hw")
    ocr = [0.3, 0.3, 0.7, 0.7]
    for k, o in enumerate(ocr):
        y = Y0 + H - o * H
        f.line([(X0 + k * per, y), (X0 + (k + 1) * per, y)], "dashc")
    f.text(X0 - 6, Y0 + 4, "TOP", "tcs", "end")
    f.text(X0 - 6, Y0 + H + 4, "0", "tcs", "end")
    f.text(X0 + 2 * per + 8, Y0 + H - 0.7 * H - 6, "OCR0A raised", "tcs tcol")
    yo, yl = 200, 240
    out = []
    for k, o in enumerate(ocr):
        x = X0 + k * per
        xm = x + o * per
        out += [(x, yl), (x, yo), (xm, yo), (xm, yl)]
    out.append((X0 + 4 * per, yl))
    f.line(out, "aw")
    f.text(X0 - 6, yo + 4, "OC0A", "tcs", "end")
    f.text(X0 + per, 270, "duty = (OCR0A + 1)/(TOP + 1): 30% then 70%", "tm", "middle")
    return f.svg()


# ======================================================================
# Module 26: devices and serial interfaces
# ======================================================================
@diagram("lcd_wiring")
def lcd_wiring():
    f = Fig(780, 240, "A character LCD on a 4-bit parallel interface: four data lines plus register-select and enable")
    chip(f, 40, 40, 150, 170, "ATmega328P")
    chip(f, 520, 40, 200, 170, "LCD controller", "16 × 2 characters")
    pins = (("PD7–PD4", "D7–D4", 80, "aw"), ("PB0", "RS", 140, "w"), ("PB1", "E", 180, "w"))
    for a, b, y, cls in pins:
        f.text(184, y + 4, a, "tcs", "end")
        f.text(526, y + 4, b, "tcs")
        f.line([(190, y), (520, y)], cls, extra=' style="stroke-width:3"' if cls == "aw" else "")
    f.text(355, 72, "4-bit data bus (one nibble at a time)", "tcs ta", "middle")
    f.text(355, 132, "RS = 0: command register, RS = 1: character data", "tcs", "middle")
    f.text(355, 172, "E pulse 0 → 1 → 0 latches each nibble", "tcs", "middle")
    return f.svg()


@wave("lcd_nibbles")
def w_lcd_nibbles():
    return {"end": 100, "grid": [], "noTicks": True,
            "signals": [{"n": "RS", "v": [[0, 1]], "c": 3},
                        {"n": "D7–D4", "bus": [[0, "x"], [8, "0100 (upper)"], [46, "x"], [52, "1000 (lower)"], [92, "x"]], "c": 2},
                        {"n": "E", "v": [[0, 0], [16, 1], [28, 0], [62, 1], [74, 0]], "c": 1}],
            "marks": [[28, "latched"], [74, "latched"]],
            "alt": "Writing the character H (0x48) as two nibbles, each latched by a pulse on E"}


@wave("uart_frame")
def w_uart():
    bits = [1, 0, 0, 0, 0, 0, 1, 0]  # 0x41 LSB first
    v = [[0, 1], [10, 0]]
    t = 20
    for b in bits:
        v.append([t, b])
        t += 10
    v.append([t, 1])
    v2 = []
    for a, b in v:
        if not v2 or v2[-1][1] != b:
            v2.append([a, b])
    bus = [[0, "idle"], [10, "start"]] + [[20 + 10 * i, f"d{i}={b}"] for i, b in enumerate(bits)] + [[100, "stop"], [110, "idle"]]
    return {"end": 120, "grid": list(range(10, 111, 10)), "noTicks": True,
            "signals": [{"n": "TX line", "v": v2, "c": 2}, {"n": "bit", "bus": bus, "c": 4}],
            "alt": "UART frame for the character A (0x41): start bit, eight data bits least significant first, stop bit"}


@wave("spi_mode0")
def w_spi():
    P = 10
    sck = []
    mosi_bits = [1, 0, 1, 1, 0, 0, 1, 0]
    miso_bits = [0, 1, 1, 0, 1, 0, 0, 1]
    return {"end": 100, "grid": [15 + P * i for i in range(8)], "noTicks": True,
            "signals": [{"n": "SS′", "v": [[0, 1], [5, 0], [93, 1]], "c": 3},
                        {"n": "SCK", "v": [[0, 0]] + sum([[[10 + P * i + 5, 1], [10 + P * i + 10, 0]] for i in range(8)], []), "c": 0},
                        {"n": "MOSI", "bus": [[0, "x"], [5, ""]] + [[10 + P * i, str(b)] for i, b in enumerate(mosi_bits)] + [[90, "x"]], "c": 1},
                        {"n": "MISO", "bus": [[0, "x"], [5, ""]] + [[10 + P * i, str(b)] for i, b in enumerate(miso_bits)] + [[90, "x"]], "c": 2}],
            "alt": "SPI mode 0: data changes on falling edges of SCK and is sampled on rising edges; both directions shift at once"}


@wave("i2c_start")
def w_i2c():
    return {"end": 120, "grid": [], "noTicks": True,
            "shade": [[4, 10, "START", 1], [104, 110, "STOP", 1]],
            "signals": [{"n": "SCL", "v": [[0, 1], [10, 0], [16, 1], [22, 0], [28, 1], [34, 0], [40, 1], [46, 0], [88, 1], [94, 0], [100, 1]], "c": 0},
                        {"n": "SDA", "v": [[0, 1], [6, 0], [13, 1], [25, 0], [37, 1], [43, 0], [91, 0], [97, 0], [106, 1]], "c": 2},
                        {"n": "meaning", "bus": [[0, ""], [10, "A6=1"], [22, "A5=0"], [34, "A4=1"], [46, "…"], [85, "ACK (0)"], [97, ""]], "c": 4}],
            "alt": "I2C: a START condition (SDA falls while SCL is high), address bits sampled while SCL is high, an acknowledge, and a STOP condition"}


@diagram("spi_bus")
def spi_bus():
    f = Fig(780, 270, "SPI: a controller and peripherals share SCK, MOSI and MISO; each peripheral has its own select line")
    chip(f, 30, 30, 170, 210, "controller", "(MCU)")
    f.rect(50, 90, 130, 30, "ba", 3)
    f.text(115, 110, "8-bit shift register", "tcs", "middle")
    for i, y in enumerate((30, 150)):
        chip(f, 580, y, 170, 90, f"peripheral {i}", "shift register")
    sig = (("SCK", 470, "w", 0), ("MOSI", 495, "aw", 20), ("MISO", 520, "hw", 40))
    for name, xv, cls, off in sig:
        y0 = 54 + off
        f.line([(200, y0), (xv, y0)], cls)
        f.text(206, y0 - 4, name, "tcs")
        f.line([(xv, y0), (xv, 174 + off)], cls)
        f.line([(xv, y0), (580, y0)], cls)
        f.line([(xv, 174 + off), (580, 174 + off)], cls)
        f.dot(xv, y0, 3)
        f.dot(xv, 174 + off, 3)
    f.line([(200, 200), (240, 200)], "rw")
    f.text(244, 204, "SS0′", "tcs tr")
    f.line([(200, 224), (240, 224)], "rw")
    f.text(244, 228, "SS1′", "tcs tr")
    for i, y in enumerate((106, 226)):
        f.line([(560, y), (580, y)], "rw")
        f.text(556, y + 4, f"SS{i}′", "tcs tr", "end")
    f.text(390, 262, "labels with the same name are connected; only the selected peripheral drives MISO", "tm", "middle")
    return f.svg()

@diagram("debounce_fsm")
def debounce_fsm():
    f = Fig(780, 270, "A non-blocking debouncer as a four-state machine stepped every millisecond; counter c counts stable samples")
    st = {"UP": dict(x=110, y=130, lines=["RELEASED"]), "MD": dict(x=310, y=130, lines=["MAYBE", "DOWN"], cls="bs"),
          "DN": dict(x=510, y=130, lines=["PRESSED"], cls="ba"), "MU": dict(x=700, y=130, lines=["MAYBE", "UP"], cls="bs")}
    ed = [dict(a="UP", b="UP", label="up", ang=-90), dict(a="UP", b="MD", label="down / c ← 0", bend=-24),
          dict(a="MD", b="UP", label="up", bend=-24), dict(a="MD", b="MD", label="down / c++", ang=-90),
          dict(a="MD", b="DN", label="c = 5", bend=-24), dict(a="DN", b="DN", label="down", ang=-90),
          dict(a="DN", b="MU", label="up / c ← 0", bend=-24), dict(a="MU", b="DN", label="down", bend=-24),
          dict(a="MU", b="MU", label="up / c++", ang=-90), dict(a="MU", b="UP", label="c = 5", bend=-120, off=14)]
    f.fsm(st, ed, r=40, reset=("UP", 180))
    return f.svg(min_width=600)


@wave("multirate")
def w_multirate():
    ticks = list(range(0, 550, 50))
    a = [[0, 0]]
    st = 0
    for t in range(250, 551, 250):
        st ^= 1
        a.append([t + 3, st])
    b = []
    for t in range(0, 551, 100):
        b += [[t, 1], [t + 12, 0]]
    tick_sig = []
    for t in ticks:
        tick_sig += [[t, 1], [t + 4, 0]]
    return {"end": 560, "grid": ticks, "noTicks": False,
            "signals": [{"n": "50 ms tick", "v": tick_sig, "c": 0},
                        {"n": "LED (250 ms)", "v": a, "c": 1},
                        {"n": "sample button (100 ms)", "v": b, "c": 2}],
            "alt": "A 50 ms base tick drives one task every 5 ticks and another every 2 ticks"}
