"""Unit 1 test data: the same files the figures were made from.

    from cryspy import unit1_test as u1
    text = u1.toy_source()           # 100000 symbols of toy English (Figures 1, 2)
    ct = u1.ciphertext()             # Figure 5, as symbols
    affine_ct = u1.affine_ciphertext()   # Figure 9, bytes
    power_ct = u1.power_ciphertext()     # Figure 14, 16-bit blocks
    u1.generate(1000, seed=7)        # fresh toy English from the model behind toy_source()

toy_source() is exactly generate(100000, seed=4242).
"""
import json
import random
import re
from pathlib import Path

_HERE = Path(__file__).parent


def _read(name):
    return (_HERE / name).read_text()


def toy_source():
    return _read("toy_source.txt")


def ciphertext():
    return _read("ciphertext.txt")


def affine_ciphertext():
    return [int(x) for x in _read("affine_ciphertext.txt").split()]


def power_ciphertext():
    return [int(x) for x in _read("power_ciphertext.txt").split()]


MODEL = json.loads(_read("toy_model.json"))  # sentence templates; each {SLOT} is a weighted word choice


def generate(n, seed=None):
    """n symbols of toy English: repeat the templates in order, filling each slot by weighted choice."""
    rng = random.Random(seed)
    out = []
    while len("".join(out)) < n:
        k = 0
        for t in MODEL["templates"]:
            def fill(_):
                nonlocal k
                w = MODEL["W"][k]
                k += 1
                return rng.choices(list(w), list(w.values()))[0]
            out.append(re.sub(r"\{\w+\}", fill, t) + " ")
    return "".join(out)[:n]
