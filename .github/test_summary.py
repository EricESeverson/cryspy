"""Turns pytest's report.xml into the table on the Actions run page.

Used by .github/workflows/tests.yml:
    python .github/test_summary.py report.xml >> $GITHUB_STEP_SUMMARY
A test that records a "call" property (one row per call, see
tests/test_gcd_lcm.py) gets a row: call, right answer, result.
"""
import sys
import xml.etree.ElementTree as ET


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


def cell(x):
    return str(x).replace("|", "\\|")


calls, others = [], []
for case in ET.parse(sys.argv[1]).iter("testcase"):
    props = {p.get("name"): p.get("value") for p in case.iter("property")}
    bad = case.find("failure")
    if bad is None:
        bad = case.find("error")
    msg = "" if bad is None else (bad.get("message") or "").splitlines()[0]
    for prefix in ("AssertionError: ", "assert "):
        msg = msg[len(prefix):] if msg.startswith(prefix) else msg
    msg = msg.split("\nassert")[0].split(" assert ")[0][:120]
    if "call" in props:
        if bad is None:
            result = f"✓ {fmt_time(float(props.get('seconds', 0)))}"
        else:
            result = f"✗ {msg}"
        calls.append((bad is None, props["call"], props["expected"], result))
    else:
        others.append((bad is None, case.get("classname", "").split(".")[-1],
                       case.get("name"), msg))

ok = sum(c[0] for c in calls) + sum(o[0] for o in others)
total = len(calls) + len(others)
print(f"## Unit tests: {ok} of {total} right\n")
if calls:
    print("✓ right, with its time ✗ wrong answer or error\n")
    print("| call | right answer | result |\n|---|---:|---|")
    for _, c, e, r in calls:
        print(f"| `{cell(c)}` | {cell(e)} | {cell(r)} |")
bad_others = [o for o in others if not o[0]]
if bad_others:
    print("\n**Other tests that failed**\n")
    for _, mod, name, msg in bad_others:
        print(f"- ✗ `{mod}` `{name}`: {cell(msg)}")
good = [o for o in others if o[0]]
if good:
    print(f"\n<details><summary>{len(good)} other tests passed</summary>\n")
    for _, mod, name, _ in good:
        print(f"- ✓ `{mod}` `{name}`")
    print("\n</details>")
