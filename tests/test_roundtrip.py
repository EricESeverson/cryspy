"""Round-trip tests: everything we send must come back unchanged.

Run from the repo folder with:  python3 tests/test_roundtrip.py
"""

import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cryspy import AdditionCipher, Blocker, CompressionEncoder, CryptoStack, TextEncoder, gcd, mult_inverse, vgcd
import math
from cryspy.compression import MinHeap

ALPHABET = "_ABCDEFGHIJKLMNOPQRSTUVWXYZ.-/"


def random_message(alphabet, rng, n):
    return "".join(rng.choice(alphabet) for _ in range(n))


def test_min_heap():
    heap = MinHeap()
    for x in [5, 3, 8, 1, 9, 2, 7]:
        heap.insert(x)
    assert [heap.pop() for _ in range(7)] == [1, 2, 3, 5, 7, 8, 9]


def test_blocker():
    rng = random.Random(0)
    for block_size in [1, 3, 5, 8, 13, 16, 64]:
        blocker = Blocker(block_size)
        for n in range(20):
            data = bytes(rng.randrange(256) for _ in range(n))
            assert blocker.deblock(blocker.block(data)) == data


def test_compression_encoder():
    rng = random.Random(1)
    enc = CompressionEncoder(ALPHABET)
    for message in ["", "A", "AB", "SIX_SEVENNNNNNNNN", "ABABAB", "ABCABCABC",
                    "BAD_BAD_BAD_CAB_BAD_DAB_BAD_CAB"]:
        assert enc.decode(enc.encode(message)) == message
    for _ in range(200):
        message = random_message("ABCD", rng, rng.randrange(1, 80))
        assert enc.decode(enc.encode(message)) == message

    weights = {"A": 4, "B": 2, "C": 1, "D": 1}
    enc = CompressionEncoder("ABCD", weights)
    for _ in range(200):
        message = "".join(rng.choices("ABCD", weights=[4, 2, 1, 1], k=rng.randrange(1, 80)))
        assert enc.decode(enc.encode(message)) == message


def test_stack():
    rng = random.Random(2)
    encoders = [TextEncoder(), CompressionEncoder(ALPHABET)]
    for encoder in encoders:
        for block_size, mod in [(8, 256), (8, 257), (5, 32), (16, 2**16), (12, 5000)]:
            for text_format in ["hex", "base64"]:
                stack = CryptoStack(encoder, block_size, AdditionCipher(mod), text_format)
                for _ in range(20):
                    message = random_message(ALPHABET, rng, rng.randrange(0, 40))
                    key = rng.randrange(mod)
                    assert stack.receive(stack.send(message, key), key) == message

    stack = CryptoStack(TextEncoder(), 8, AdditionCipher(256))
    message = "héllo, wörld 🔐"
    assert stack.receive(stack.send(message, 77), 77) == message


def test_mod_too_small():
    try:
        CryptoStack(TextEncoder(), 8, AdditionCipher(255))
    except ValueError:
        return
    raise AssertionError("expected a ValueError")


def test_number_theory():
    rng = random.Random(3)
    for bits in [4, 8, 64, 512]:
        for _ in range(200):
            n = rng.randrange(2, 2 ** bits)
            a = rng.randrange(0, n)
            assert gcd(n, a) == math.gcd(n, a)
            gx, gy = vgcd((0, n), (1, a))
            assert gy == math.gcd(n, a) and (gx * a - gy) % n == 0
            if gy == 1:
                assert mult_inverse(a, n) == pow(a, -1, n)
            else:
                try:
                    mult_inverse(a, n)
                except ValueError:
                    continue
                raise AssertionError("expected a ValueError")


def test_padding():
    # the padding count is sent in the clear; the padding bits are random
    stack = CryptoStack(TextEncoder(), 64, AdditionCipher(2 ** 64))
    message = "hi"  # 16 bits, so 48 padding bits
    first = stack.encrypt(message, 5)
    assert first[0] == 48
    assert any(stack.encrypt(message, 5)[-1] != first[-1] for _ in range(5))
    assert stack.decrypt(first, 5) == message


if __name__ == "__main__":
    for name, test in list(globals().items()):
        if name.startswith("test_"):
            test()
            print("passed", name)
