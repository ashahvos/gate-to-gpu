"""Exact two-level minimizer and expression evaluator used to check answers in the modules."""
import itertools
import re


def minimize(n, ones, dcs=(), names="ABCDE"):
    names = names[:n]
    N = 1 << n
    ones, dcs = set(ones), set(dcs)
    terms = []
    for pat in itertools.product((0, 1, 2), repeat=n):
        cover = []
        ok = True
        for m in range(N):
            bits = [(m >> (n - 1 - j)) & 1 for j in range(n)]
            if all(p == 2 or p == b for p, b in zip(pat, bits)):
                if m not in ones and m not in dcs:
                    ok = False
                    break
                cover.append(m)
        if ok and cover:
            terms.append((pat, frozenset(cover)))
    primes = [t for t in terms if not any(u[1] > t[1] for u in terms) and t[1] & ones]
    best = None
    for k in range(1, len(primes) + 1):
        for combo in itertools.combinations(primes, k):
            if ones <= set().union(*[c[1] for c in combo]):
                lits = sum(sum(1 for p in c[0] if p != 2) for c in combo)
                if best is None or lits < best[0]:
                    best = (lits, combo)
        if best:
            break
    if not ones:
        return "0", []
    def ts(p):
        s = "".join(names[j] + ("'" if v == 0 else "") for j, v in enumerate(p) if v != 2)
        return s or "1"
    strs = sorted(ts(c[0]) for c in best[1])
    return " + ".join(strs), [sorted(c[1]) for c in best[1]]


def all_minimal(n, ones, dcs=(), names="ABCDE"):
    """Return every minimal SOP (same term count and literal count)."""
    names = names[:n]
    N = 1 << n
    ones, dcs = set(ones), set(dcs)
    terms = []
    for pat in itertools.product((0, 1, 2), repeat=n):
        cover = []
        ok = True
        for m in range(N):
            bits = [(m >> (n - 1 - j)) & 1 for j in range(n)]
            if all(p == 2 or p == b for p, b in zip(pat, bits)):
                if m not in ones and m not in dcs:
                    ok = False
                    break
                cover.append(m)
        if ok and cover:
            terms.append((pat, frozenset(cover)))
    primes = [t for t in terms if not any(u[1] > t[1] for u in terms) and t[1] & ones]
    sols = []
    for k in range(1, len(primes) + 1):
        for combo in itertools.combinations(primes, k):
            if ones <= set().union(*[c[1] for c in combo]):
                lits = sum(sum(1 for p in c[0] if p != 2) for c in combo)
                sols.append((k, lits, combo))
        if sols:
            break
    m = min(s[1] for s in sols)
    def ts(p):
        return "".join(names[j] + ("'" if v == 0 else "") for j, v in enumerate(p) if v != 2) or "1"
    return [" + ".join(sorted(ts(c[0]) for c in s[2])) for s in sols if s[1] == m], [ts(p[0]) for p in primes]


def evaluate(expr, n, names="ABCDE"):
    """Truth table (list of minterms where expr = 1) of an expression using ' for NOT, juxtaposition/· for AND, + for OR, ^ for XOR."""
    names = names[:n]
    e = expr.replace("·", "*").replace("′", "'").replace("⊕", "^")
    # convert to python: insert * between adjacent factors
    toks = re.findall(r"[A-Z]|'|\(|\)|\+|\*|\^|0|1", e)
    out = []
    prev = None
    for t in toks:
        if prev is not None and (prev in names or prev in ")'01") and (t in names or t == "(" or t in "01"):
            out.append("&")
        if t == "'":
            out.append("^1")
            prev = t
            continue
        out.append({"+": "|", "*": "&"}.get(t, t))
        prev = t
    py = "".join(out)
    # NOT binds tighter: wrap var^1 properly by converting X^1 groups
    py = re.sub(r"([A-Z]|\))\^1", lambda m: m.group(0), py)
    res = []
    for m in range(1 << n):
        env = {names[j]: (m >> (n - 1 - j)) & 1 for j in range(n)}
        # build with explicit parentheses for postfix NOT
        val = eval(_postfix_not(e, names), {}, env)
        if val & 1:
            res.append(m)
    return res


def _postfix_not(e, names):
    # tokenize and convert to python with proper precedence: ' -> (1-x), juxtaposition AND, + OR, ^ XOR
    toks = re.findall(r"[A-Z]|'|\(|\)|\+|\*|\^|0|1", e)
    pos = 0

    def peek():
        return toks[pos] if pos < len(toks) else None

    def parse_or():
        nonlocal pos
        l = parse_xor()
        while peek() == "+":
            pos += 1
            l = f"({l}|{parse_xor()})"
        return l

    def parse_xor():
        nonlocal pos
        l = parse_and()
        while peek() == "^":
            pos += 1
            l = f"({l}^{parse_and()})"
        return l

    def parse_and():
        nonlocal pos
        l = parse_un()
        while True:
            t = peek()
            if t == "*":
                pos += 1
                l = f"({l}&{parse_un()})"
            elif t is not None and (t in names or t == "(" or t in ("0", "1")):
                l = f"({l}&{parse_un()})"
            else:
                break
        return l

    def parse_un():
        nonlocal pos
        t = peek()
        pos += 1
        if t == "(":
            v = parse_or()
            pos += 1
        else:
            v = t
        while peek() == "'":
            pos += 1
            v = f"(1-{v})"
        return v
    return parse_or()


if __name__ == "__main__":
    print(minimize(4, [0, 1, 2, 5, 8, 9, 10]))
