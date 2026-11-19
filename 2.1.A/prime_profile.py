"""Primality profiler (prototype, same shape as dlog_profile.py).

    is_prime(n) -> True or False

Every function runs on every case (no early stop). Row 0 is every n from
0 to 199 at once.

In Colab (after the usual cryspy setup cell):
    !pip install -q line_profiler
    sys.path.insert(0, "/content/cryspy/2.1.A")
    from prime_profile import test_primes, line_profile
    test_primes(is_prime, cp.is_prime)
    line_profile(is_prime, case=40)

From the command line (this is what the GitHub Action runs):
    python 2.1.A/prime_profile.py 2.1.A/group1.py --markdown >> $GITHUB_STEP_SUMMARY
which tests every function in that file whose name starts with "is_prime".
"""

import argparse
import importlib.util
import inspect
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from cryspy.profiling import run, short, _named


def fmt_time(s):
    """12 µs, 3.4 ms, 1.20 s."""
    if s < 1e-6:
        return "< 1 µs"
    if s < 1e-3:
        return f"{s * 1e6:.0f} µs"
    if s < 1:
        return f"{s * 1e3:.1f} ms"
    return f"{s:.2f} s"

with open(os.path.join(HERE, "prime_cases.json")) as f:
    CASES = [(int(c["n"]), c["prime"]) for c in json.load(f)]
PRIMES_BELOW_200 = {n for n in range(2, 200)
                    if all(n % d for d in range(2, n))}


def _small(f, time_limit):
    """Row 0: every n from 0 to 199, one time limit for the whole row."""
    def all_small():
        return [n for n in range(200) if f(n) != (n in PRIMES_BELOW_200)]
    status, bad, seconds = run(all_small, (), time_limit)
    if status != "ok":
        return status, (bad if status == "error" else f"over {time_limit:g} s")
    if bad:
        return "wrong", f"wrong at n = {', '.join(map(str, bad[:4]))}" + (
            "..." if len(bad) > 4 else "")
    return "ok", fmt_time(seconds)


def check_cell(f, n, answer, time_limit):
    status, x, seconds = run(f, (n,), time_limit)
    if status == "slow":
        return "slow", f"over {time_limit:g} s", seconds
    if status == "error":
        return "error", x, seconds
    if x is answer or (type(x) is bool and x == answer):
        return "ok", fmt_time(seconds), seconds
    return "wrong", f"said {short(x)}", seconds


DESCRIBE_HEAD = ["bits", "n", "prime?"]
SUMMARY_BIGGEST = "biggest prime it got right"


def _describe(i):
    if i == 0:
        return ["", "every n from 0 to 199", ""]
    n, answer = CASES[i - 1]
    return [str(n.bit_length()), short(n), "yes" if answer else "no"]


def _biggest(res):
    bits = [CASES[i - 1][0].bit_length() for i, _, s in res
            if s == "ok" and i and CASES[i - 1][1]]
    return f"{max(bits)} bits" if bits else "none"


_FS = []


def _column(j, which, time_limit):
    f = _FS[j]
    col = []
    for i in which:
        if i == 0:
            col.append((0, 8, *_small(f, time_limit), 0.0))
            continue
        n, answer = CASES[i - 1]
        status, text, sec = check_cell(f, n, answer, time_limit)
        col.append((i, n.bit_length(), status, text, sec))
    return col


def test_primes(*fs, time_limit=1.0, cases=None, markdown=False, out=None,
              parallel=False):
    """Run every function on every case. Returns {name: [(i, bits,
    status), ...]}. parallel=True gives each function its own process."""
    out = out or sys.stdout
    fs = _named(fs)
    names = [f.__name__ for f in fs]
    which = list(cases or range(0, len(CASES) + 1))
    _FS[:] = fs
    if parallel and len(fs) > 1:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(len(fs)) as pool:
            cols = pool.starmap(_column, [(j, which, time_limit)
                                          for j in range(len(fs))])
    else:
        cols = [_column(j, which, time_limit) for j in range(len(fs))]
    mark = {"ok": "✓", "slow": "·", "wrong": "✗", "error": "✗"}
    results = {n: [(i, b, s) for i, b, s, *_ in c] for n, c in zip(names, cols)}

    def row(r):
        i = which[r]
        cells = [f"{mark[c[r][2]]} {c[r][3]}" for c in cols]
        return [str(i), *_describe(i)] + cells

    head = ["#", *DESCRIBE_HEAD] + [f"`{n}`" if markdown else n for n in names]
    rows = [row(r) for r in range(len(which))]
    trouble = [rw for r, rw in enumerate(rows)
               if any(c[r][2] != "ok" for c in cols)]

    def table(rs):
        if markdown:
            print("| " + " | ".join(head) + " |", file=out)
            print("|" + "---:|" * len(DESCRIBE_HEAD) + "---:|"
                  + "---|" * len(names), file=out)
            for rw in rs:
                print("| " + " | ".join(rw) + " |", file=out)
        else:
            w = [max(len(x[k]) for x in [head] + rs) for k in range(len(head))]
            for rw in [head] + rs:
                print("  " + "  ".join(x.rjust(wk) for x, wk in zip(rw, w)),
                      file=out)

    # summary first
    sh = ["function", "right", "wrong", "errors", f"over {time_limit:g} s",
          SUMMARY_BIGGEST]
    srows = []
    for n in names:
        st = [s for _, _, s in results[n]]
        srows.append([f"`{n}`" if markdown else n,
                      f"{st.count('ok')} of {len(st)}", str(st.count("wrong")),
                      str(st.count("error")), str(st.count("slow")),
                      _biggest(results[n])])
    if markdown:
        print("| " + " | ".join(sh) + " |\n|---|" + "---:|" * (len(sh) - 1),
              file=out)
        for rw in srows:
            print("| " + " | ".join(rw) + " |", file=out)
        print(f"\n### Where something went wrong ({len(trouble)} of "
              f"{len(rows)} cases)\n", file=out)
        print("✓ right, with its time · stopped at the time limit "
              "✗ wrong answer or error\n", file=out)
        table(trouble) if trouble else print("Nothing: every function "
                                             "was right every time.", file=out)
        print(f"\n<details><summary><b>All {len(rows)} cases</b></summary>\n",
              file=out)
        table(rows)
        print("\n</details>", file=out)
    else:
        for rw in srows:
            print("  " + "  ".join(rw), file=out)
        print(f"\nWhere something went wrong ({len(trouble)} of {len(rows)}):",
              file=out)
        table(trouble)
    return results, cols


def line_profile(f, case, extra=(), markdown=False, out=None,
                 time_limit=30.0):
    """Hit counts, line by line, for one call f(n) on one case.
    Also profiles every function defined next to f (helpers like modexp)
    and the cryspy number theory functions; shows only lines that ran."""
    from line_profiler import LineProfiler
    import cryspy.number_theory as nt
    out = out or sys.stdout
    mod = sys.modules.get(f.__module__)
    funcs = [f] + [m for _, m in inspect.getmembers(mod, inspect.isfunction)
                   if m.__module__ == f.__module__ and m is not f]
    funcs += [m for _, m in inspect.getmembers(nt, inspect.isfunction)
              if m.__module__ == nt.__name__] + list(extra)
    lp = LineProfiler()
    for m in funcs:
        lp.add_function(m)
    n, _ = CASES[case - 1]
    status, x, seconds = run(lp(f), (n,), time_limit)
    title = (f"{f.__name__} on case #{case} ({n.bit_length()} bits): "
             f"{status}, {fmt_time(seconds)} with the profiler on")
    print(f"\n<details><summary><b>{title}</b></summary>\n" if markdown
          else f"\n{title}", file=out)
    stats = lp.get_stats()
    blocks = []
    for m in funcs:
        code = m.__code__
        key = next((k for k in stats.timings
                    if k[1] == code.co_firstlineno and k[2] == code.co_name), None)
        lines = {ln: (hits, t) for ln, hits, t in stats.timings.get(key, [])}
        if not lines:
            continue
        ftime = sum(t for _, t in lines.values()) or 1
        blocks.append((m, lines, ftime))
    top = max((ft for m, _, ft in blocks if m is f), default=1)
    if markdown:
        print("```", file=out)
    for m, lines, ftime in blocks:
        if m.__module__ != f.__module__ and ftime < 0.05 * top:
            continue          # a cryspy helper that cost next to nothing
        src, start = inspect.getsourcelines(m)
        print(f"{'hits':>12} {'%':>4}  {m.__module__}.{m.__name__}", file=out)
        for k, s in enumerate(src):
            ln = start + k
            if ln in lines:
                hits, t = lines[ln]
                print(f"{hits:>12,} {100 * t / ftime:>4.0f}  {s.rstrip()}",
                      file=out)
            elif s.strip().startswith(("def ", "else")):
                print(f"{'':>12} {'':>4}  {s.rstrip()}", file=out)
        print(file=out)
    if markdown:
        print("```\n</details>", file=out)


def load_group(path):
    spec = importlib.util.spec_from_file_location(
        os.path.splitext(os.path.basename(path))[0], path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    import contextlib
    with contextlib.redirect_stdout(sys.stderr):   # prints in the group file
        spec.loader.exec_module(mod)               # stay out of the report
    return mod, [m for n, m in inspect.getmembers(mod, inspect.isfunction)
                 if n.startswith("is_prime") and m.__module__ == mod.__name__]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("group_file")
    ap.add_argument("--time-limit", type=float, default=1.0)
    ap.add_argument("--markdown", action="store_true")
    ap.add_argument("--no-lines", action="store_true")
    a = ap.parse_args()
    mod, fs = load_group(a.group_file)
    fs.sort(key=lambda m: m.__code__.co_firstlineno)   # file order
    md = a.markdown
    if not fs:
        print(f"No functions yet: this tests every function in "
              f"`{a.group_file}` whose name starts with `is_prime`.")
        sys.exit(0)
    if md:
        print(f"## Primality profile: `{os.path.basename(a.group_file)}`\n")
        print(f"Functions found: {', '.join(f'`{f.__name__}`' for f in fs)}. "
              f"Each call is stopped after {a.time_limit:g} s.\n")
    t0 = time.time()
    res, cols = test_primes(*fs, time_limit=a.time_limit, markdown=md,
                          parallel=True)
    if not a.no_lines:
        print("\n### Line by line (click to open)\n" if md else "\nLine by line")
        print("Each function once, on the biggest prime it got right in under "
              f"{a.time_limit / 10:g} s. Hits are exact and the same on every "
              "computer; % is the share of that function's own time.\n"
              if md else "")
        for f, col in zip(fs, cols):
            quick = [(b, i) for i, b, s, t, sec in col
                     if i and CASES[i - 1][1] and s == "ok"
                     and sec < a.time_limit / 10]
            if quick:
                line_profile(f, max(quick)[1], markdown=md)
    print(f"\n_Total {time.time() - t0:.0f} s._" if md
          else f"\nTotal {time.time() - t0:.0f} s")
