"""Discrete log profiler (prototype for cryspy.profiling.test_dlog).

    dlog(g, h, p) -> some x with pow(g, x, p) == h

Challenges run smallest p first. A function that runs out of time on
give_up challenges in a row is not tried on the rest (they show as
"skipped"). give_up=None runs every function on every challenge: a bigger p
is not always harder. Answers are checked with pow, so there is no answer key.

In Colab (after the usual cryspy setup cell):
    !pip install -q line_profiler
    sys.path.insert(0, "/content/cryspy/2.1.A")
    from dlog_profile import test_dlog, line_profile
    test_dlog(dlog_naive, dlog_bsgs)
    test_dlog(dlog_naive, give_up=None, time_limit=3)    # the full run
    line_profile(dlog_bsgs, challenge=12)

From the command line (this is what the GitHub Action runs):
    python 2.1.A/dlog_profile.py 2.1.A/group1.py --markdown >> $GITHUB_STEP_SUMMARY
which tests every function in that file whose name starts with "dlog".
Add --give-up 0 for the full run (Actions tab -> Discrete log profile ->
Run workflow -> tick "full").
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
    """Three significant figures: 420 ns, 3.17 µs, 41.2 ms, 1.22 s."""
    for scale, unit in ((1e-6, "ns"), (1e-3, "µs"), (1, "ms")):
        if s < scale:
            v = s / scale * 1000
            break
    else:
        v, unit = s, "s"
    d = 2 if v < 10 else 1 if v < 100 else 0
    return f"{v:.{d}f} {unit}"

with open(os.path.join(HERE, "dlog_challenges.json")) as f:
    CHALLENGES = [(c["p"], c["g"], c["h"]) for c in json.load(f)]


def check_cell(f, g, h, p, time_limit):
    status, x, seconds = run(f, (g, h, p), time_limit)
    if status == "slow":
        return "slow", f"over {time_limit:g} s", seconds
    if status == "error":
        return "error", x, seconds
    if isinstance(x, int) and pow(g, x, p) == h:
        return "ok", fmt_time(seconds), seconds
    return "wrong", f"gave {short(x)}", seconds


DESCRIBE_HEAD = ["bits", "p"]
SUMMARY_BIGGEST = "biggest p it solved"


def _describe(i):
    p, g, h = CHALLENGES[i - 1]
    return [str(p.bit_length()), short(p)]


def _biggest(res):
    bits = [b for _, b, s in res if s == "ok"]
    return f"{max(bits)} bits" if bits else "none"


_FS = []


def _column(j, which, time_limit, give_up=None):
    f = _FS[j]
    col = []
    streak = 0
    for i in which:
        p, g, h = CHALLENGES[i - 1]
        if give_up and streak >= give_up:
            col.append((i, p.bit_length(), "skip", "skipped", 0.0))
            continue
        status, text, sec = check_cell(f, g, h, p, time_limit)
        streak = streak + 1 if status == "slow" else 0
        col.append((i, p.bit_length(), status, text, sec))
    return col


def test_dlog(*fs, time_limit=1.0, challenges=None, markdown=False, out=None,
              parallel=False, give_up=3):
    """Run every function on the challenges, smallest p first, dropping a
    function after give_up time-outs in a row (give_up=None: never drop).
    Returns {name: [(i, bits, status), ...]}. parallel=True gives each
    function its own process."""
    out = out or sys.stdout
    fs = _named(fs)
    names = [f.__name__ for f in fs]
    which = sorted(challenges or range(1, len(CHALLENGES) + 1),
                   key=lambda i: (CHALLENGES[i - 1][0], i))
    _FS[:] = fs
    if parallel and len(fs) > 1:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(len(fs)) as pool:
            cols = pool.starmap(_column, [(j, which, time_limit, give_up)
                                          for j in range(len(fs))])
    else:
        cols = [_column(j, which, time_limit, give_up)
                for j in range(len(fs))]
    mark = {"ok": "✓", "slow": "·", "wrong": "✗", "error": "✗", "skip": "·"}
    results = {n: [(i, b, s) for i, b, s, *_ in c] for n, c in zip(names, cols)}

    def row(r):
        i = which[r]
        cells = [f"{mark[c[r][2]]} {c[r][3]}" for c in cols]
        return [str(i), *_describe(i)] + cells

    head = ["#", *DESCRIBE_HEAD] + [f"`{n}`" if markdown else n for n in names]
    rows = [row(r) for r in range(len(which))]
    trouble = [rw for r, rw in enumerate(rows)
               if any(c[r][2] not in ("ok", "skip") for c in cols)]

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
          "skipped", SUMMARY_BIGGEST]
    srows = []
    for n in names:
        st = [s for _, _, s in results[n]]
        srows.append([f"`{n}`" if markdown else n,
                      f"{st.count('ok')} of {len(st)}", str(st.count("wrong")),
                      str(st.count("error")), str(st.count("slow")),
                      str(st.count("skip")), _biggest(results[n])])
    if markdown:
        print("| " + " | ".join(sh) + " |\n|---|" + "---:|" * (len(sh) - 1),
              file=out)
        for rw in srows:
            print("| " + " | ".join(rw) + " |", file=out)
        print(f"\n### Where something went wrong ({len(trouble)} of "
              f"{len(rows)} cases)\n", file=out)
        print("✓ right, with its time · stopped at the time limit "
              "✗ wrong answer or error\n", file=out)
        if any(c[r][2] == "skip" for c in cols for r in range(len(rows))):
            print(f"A function that ran out of time on {give_up} challenges "
                  "in a row was not tried on the bigger ones (skipped). For "
                  "the full run: Actions tab, Discrete log profile, Run "
                  "workflow, tick full.\n", file=out)
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


def line_profile(f, challenge, extra=(), markdown=False, out=None,
                 time_limit=30.0):
    """Hit counts, line by line, for one call f(g, h, p) on one challenge.
    Also profiles every function defined next to f (helpers like bsgs, crt)
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
    p, g, h = CHALLENGES[challenge - 1]
    status, x, seconds = run(lp(f), (g, h, p), time_limit)
    title = (f"{f.__name__} on challenge #{challenge} ({p.bit_length()} bits): "
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
                 if n.startswith("dlog") and m.__module__ == mod.__name__]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("group_file")
    ap.add_argument("--time-limit", type=float, default=1.0)
    ap.add_argument("--markdown", action="store_true")
    ap.add_argument("--no-lines", action="store_true")
    ap.add_argument("--give-up", type=int, default=3,
                    help="drop a function after this many time-outs in a "
                         "row; 0 runs everything")
    a = ap.parse_args()
    mod, fs = load_group(a.group_file)
    fs.sort(key=lambda m: m.__code__.co_firstlineno)   # file order
    md = a.markdown
    if not fs:
        print(f"No functions yet: this tests every function in "
              f"`{a.group_file}` whose name starts with `dlog`.")
        sys.exit(0)
    if md:
        print(f"## Discrete log profile: `{os.path.basename(a.group_file)}`\n")
        print(f"Functions found: {', '.join(f'`{f.__name__}`' for f in fs)}. "
              f"Each call is stopped after {a.time_limit:g} s.\n")
        if not a.give_up:
            print("Full run: every function on every challenge.\n")
    t0 = time.time()
    res, cols = test_dlog(*fs, time_limit=a.time_limit, markdown=md,
                          parallel=True, give_up=a.give_up or None)
    if not a.no_lines:
        print("\n### Line by line (click to open)\n" if md else "\nLine by line")
        print("Each function once, on the biggest challenge it solved in under "
              f"{a.time_limit / 10:g} s. Hits are exact and the same on every "
              "computer; % is the share of that function's own time.\n"
              if md else "")
        for f, col in zip(fs, cols):
            quick = [(b, i) for i, b, s, t, sec in col
                     if s == "ok" and sec < a.time_limit / 10]
            if quick:
                line_profile(f, max(quick)[1], markdown=md)
    print(f"\n_Total {time.time() - t0:.0f} s._" if md
          else f"\nTotal {time.time() - t0:.0f} s")
