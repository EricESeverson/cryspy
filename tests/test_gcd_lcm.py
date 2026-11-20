"""gcd and lcm with any number of inputs: one row per call.

Run: python -m pytest tests/test_gcd_lcm.py
Right answers agree with Python's math.gcd / math.lcm.
On a group branch, the group's own gcd / lcm in 2.1.A/groupN.py are tested
if it defines them; otherwise cryspy's. Each row names which one.
"""
import glob
import importlib.util
import math
import os
import random
import time

import pytest

import cryspy.number_theory as nt
from cryspy.profiling import short

rng = random.Random(2026)
big = [rng.getrandbits(200) * 6 for _ in range(3)]
small = [rng.randrange(1, 10**6) for _ in range(8)]

CASES = [
    ("gcd", (12, 18), 6),
    ("gcd", (17, 5), 1),
    ("gcd", (12, 18, 8), 2),
    ("gcd", (30, 42, 70, 105), 1),
    ("gcd", (4, -6), 2),
    ("gcd", (-4, -6), 2),
    ("gcd", (0, 7), 7),
    ("gcd", (0, 0), 0),
    ("gcd", (-5,), 5),
    ("gcd", (), 0),
    ("gcd", tuple(big), math.gcd(*big)),
    ("lcm", (4, 6), 12),
    ("lcm", (4, 6, 10), 60),
    ("lcm", (2, 3, 4, 5, 6), 60),
    ("lcm", (-4, 6), 12),
    ("lcm", (0, 5), 0),
    ("lcm", (-5,), 5),
    ("lcm", (), 1),
    ("lcm", tuple(small), math.lcm(*small)),
]


def _group_module():
    """The branch's 2.1.A/groupN.py, or None (on main, or if it won't load)."""
    here = os.path.dirname(os.path.abspath(__file__))
    paths = sorted(glob.glob(os.path.join(here, "..", "2.1.A", "group*.py")))
    if not paths:
        return None, None
    name = os.path.splitext(os.path.basename(paths[0]))[0]
    try:
        spec = importlib.util.spec_from_file_location(name, paths[0])
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod, None
    except Exception as e:  # report it on every row rather than crash
        return None, f"{name}.py failed to load: {type(e).__name__}: {e}"


GROUP, LOAD_ERROR = _group_module()


def find(name):
    """(label, function): the group's own if defined, else cryspy's."""
    if GROUP is not None and callable(getattr(GROUP, name, None)):
        return GROUP.__name__, getattr(GROUP, name)
    return "cryspy", getattr(nt, name, None)


def call(name, args):
    who = find(name)[0]
    s = f"{who}.{name}({', '.join(short(a) for a in args)})"
    if len(s) > 70:
        digits = max(len(str(abs(a))) for a in args)
        s = f"{who}.{name}({len(args)} numbers, up to {digits} digits)"
    return s


@pytest.mark.parametrize("name, args, expected", CASES,
                         ids=[call(*c[:2]) for c in CASES])
def test_gcd_lcm(name, args, expected, record_property):
    record_property("call", call(name, args))
    record_property("expected", short(expected))
    assert LOAD_ERROR is None, LOAD_ERROR
    who, f = find(name)
    assert f is not None, f"no {name} yet (not in your group file or cryspy)"
    start = time.perf_counter()
    got = f(*args)
    record_property("seconds", time.perf_counter() - start)
    record_property("got", short(got))
    assert got == expected, f"got {short(got)}"
