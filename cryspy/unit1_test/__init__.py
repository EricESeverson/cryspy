"""Unit 1 test data: the same files the figures were made from.

    from cryspy import unit1_test as u1
    text = u1.toy_source()           # 100000 symbols of toy English (Figures 1, 2)
    ct = u1.ciphertext()             # Figure 5, as symbols
    affine_ct = u1.affine_ciphertext()   # Figure 9, bytes
    power_ct = u1.power_ciphertext()     # Figure 14, 16-bit blocks
"""
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
