"""Correctness tests for gcd and lcm with any number of inputs.

Run: python -m pytest tests/test_gcd_lcm.py
Each expected value agrees with Python's math.gcd / math.lcm.
"""
import math
import random

import cryspy.number_theory as nt

gcd = nt.gcd
lcm = getattr(nt, "lcm", None)


def need_lcm():
    assert lcm is not None, "cryspy has no lcm yet"


def test_gcd_two():
    assert gcd(12, 18) == 6
    assert gcd(17, 5) == 1


def test_gcd_several():
    assert gcd(12, 18, 8) == 2
    assert gcd(30, 42, 70, 105) == 1


def test_gcd_list():
    assert gcd(*[30, 42, 70]) == 2


def test_gcd_negatives():
    assert gcd(4, -6) == 2
    assert gcd(-4, -6) == 2
    assert gcd(-5, 0) == 5


def test_gcd_zeros():
    assert gcd(0, 7) == 7
    assert gcd(0, 0) == 0


def test_gcd_one():
    assert gcd(-5) == 5


def test_gcd_empty():
    assert gcd() == 0


def test_lcm_two():
    need_lcm()
    assert lcm(4, 6) == 12


def test_lcm_several():
    need_lcm()
    assert lcm(4, 6, 10) == 60
    assert lcm(*[2, 3, 4, 5, 6]) == 60


def test_lcm_negatives_and_zeros():
    need_lcm()
    assert lcm(-4, 6) == 12
    assert lcm(0, 5) == 0
    assert lcm(-5) == 5


def test_lcm_empty():
    need_lcm()
    assert lcm() == 1


def test_against_math():
    rng = random.Random(2026)
    for _ in range(300):
        ns = [rng.randint(-10**6, 10**6) for _ in range(rng.randrange(1, 6))]
        assert gcd(*ns) == math.gcd(*ns), ns
        if lcm is not None:
            assert lcm(*ns) == math.lcm(*ns), ns


def test_big():
    rng = random.Random(1410)
    for _ in range(20):
        a, b, c = (rng.getrandbits(1000) for _ in range(3))
        assert gcd(a * c, b * c) == math.gcd(a * c, b * c)
