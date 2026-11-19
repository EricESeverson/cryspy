"""Discrete log profiler (prototype for cryspy.profiling.test_dlog).

    dlog(g, h, p) -> some x with pow(g, x, p) == h

Every function runs on every challenge (no early stop: a bigger p is not
always harder). Answers are checked with pow, so there is no answer key.

In Colab (after the usual cryspy setup cell):
    !pip install -q line_profiler
    sys.path.insert(0, "/content/cryspy/2.1.A")
    from dlog_profile import test_dlog, line_profile
    test_dlog(dlog_naive, dlog_bsgs)
    line_profile(dlog_bsgs, challenge=12)

From the command line (this is what the GitHub Action runs):
    python 2.1.A/dlog_profile.py 2.1.A/group1.py --markdown >> $GITHUB_STEP_SUMMARY
which tests every function in that file whose name starts with "dlog".
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

with open(os.path.join(HERE, "dlog_challenges.json")) as f:
    CHALLENGES = [(c["p"], c["g"], c["h"]) for c in json.load(f)]


def check_cell(f, g, h, p, time_limit):
    status, x, seconds = run(f, (g, h, p), time_limit)
    if status == "slow":
        return "slow", f"over {time_limit:g} s", seconds
    if status == "error":
        return "error", x, seconds
    if isinstance(x, int) and pow(g, x, p) == h:
        return "ok", f"{seconds:.4f}", seconds
    return "wrong", f"wrong: {short(x)}", seconds


_FS = []


def _column(j, which, time_limit):
    f = _FS[j]
    col = []
    for i in which:
        p, g, h = CHALLENGES[i - 1]
        status, text, _ = check_cell(f, g, h, p, time_limit)
        col.append((i, p.bit_length(), status, text))
    return col


def test_dlog(*fs, time_limit=1.0, challenges=None, markdown=False, out=None,
              parallel=False):
    """Run every function on every challenge. Returns {name: [(i, bits,
    status), ...]}. parallel=True gives each function its own process."""
    out = out or sys.stdout
    fs = _named(fs)
    names = [f.__name__ for f in fs]
    which = list(challenges or range(1, len(CHALLENGES) + 1))
    _FS[:] = fs
    if parallel and len(fs) > 1:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(len(fs)) as pool:
            cols = pool.starmap(_column, [(j, which, time_limit)
                                          for j in range(len(fs))])
    else:
        cols = [_column(j, which, time_limit) for j in range(len(fs))]
    mark = {"ok": "✓", "slow": "·", "wrong": "✗", "error": "✗"}
    if markdown:
        print("| # | bits | " + " | ".join(f"`{n}`" for n in names) + " |",
              file=out)
        print("|---:|---:|" + "---|" * len(names), file=out)
    for r, i in enumerate(which):
        bits = CHALLENGES[i - 1][0].bit_length()
        cells = [f"{mark[c[r][2]]} {c[r][3]}" for c in cols]
        if markdown:
            print(f"| {i} | {bits} | " + " | ".join(cells) + " |", file=out)
        else:
            print(f"  #{i:<3} {bits:>5} bits  "
                  + "  ".join(f"{c:>18}" for c in cells), file=out)
    results = {n: [(i, b, s) for i, b, s, _ in c] for n, c in zip(names, cols)}

    print("\n**Summary**\n" if markdown else "\nSummary", file=out)
    for n in names:
        ok = [b for _, b, s in results[n] if s == "ok"]
        bad = sum(s in ("wrong", "error") for _, _, s in results[n])
        slow = sum(s == "slow" for _, _, s in results[n])
        line = (f"{n}: solved {len(ok)} of {len(results[n])}, "
                f"{slow} over {time_limit:g} s, {bad} wrong or errors; "
                f"biggest p solved: {max(ok, default=0)} bits")
        print(f"- {line}" if markdown else f"  {line}", file=out)
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
             f"{status}, {seconds:.3f} s with the profiler on")
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
    a = ap.parse_args()
    mod, fs = load_group(a.group_file)
    fs.sort(key=lambda m: m.__code__.co_firstlineno)   # file order
    md = a.markdown
    if not fs:
        print(f"No functions yet: this tests every function in "
              f"`{a.group_file}` whose name starts with `dlog`.")
        sys.exit(0)
    if md:
        print(f"## Discrete log profile: `{a.group_file}`\n")
        print(f"Functions found: {', '.join(f'`{f.__name__}`' for f in fs)}. "
              f"Each call is stopped after {a.time_limit:g} s. "
              "✓ seconds · too slow ✗ wrong\n")
    t0 = time.time()
    res, cols = test_dlog(*fs, time_limit=a.time_limit, markdown=md,
                          parallel=True)
    if not a.no_lines:
        print("\n### Line by line\n" if md else "\nLine by line")
        print("Each function once, on the biggest challenge it solved in under "
              f"{a.time_limit / 10:g} s. Hits are exact and the same on every "
              "computer; % is the share of that function's own time.\n"
              if md else "")
        for f, col in zip(fs, cols):
            quick = [(b, i) for i, b, s, t in col
                     if s == "ok" and float(t) < a.time_limit / 10]
            if quick:
                line_profile(f, max(quick)[1], markdown=md)
    print(f"\n_Total {time.time() - t0:.0f} s._" if md
          else f"\nTotal {time.time() - t0:.0f} s")
