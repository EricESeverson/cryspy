"""gcd and lcm with any number of inputs: one row per call.

Run: python -m pytest tests/test_gcd_lcm.py
Right answers agree with Python's math.gcd / math.lcm.
"""
import math
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


def call(name, args):
    s = f"{name}({', '.join(short(a) for a in args)})"
    if len(s) > 60:
        digits = max(len(str(abs(a))) for a in args)
        s = f"{name}({len(args)} numbers, up to {digits} digits)"
    return s


@pytest.mark.parametrize("name, args, expected", CASES,
                         ids=[call(*c[:2]) for c in CASES])
def test_gcd_lcm(name, args, expected, record_property):
    record_property("call", call(name, args))
    record_property("expected", short(expected))
    f = getattr(nt, name, None)
    assert f is not None, f"cryspy has no {name} yet"
    start = time.perf_counter()
    got = f(*args)
    record_property("seconds", time.perf_counter() - start)
    record_property("got", short(got))
    assert got == expected, f"got {short(got)}"
