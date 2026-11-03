"""Round-trip tests: everything we send must come back unchanged.

Run from the repo folder with:  python3 tests/test_roundtrip.py
"""

import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cryspy import candidates
from cryspy import AdditionCipher, Blocker, CompressionEncoder, CryptoStack, TextEncoder
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


def test_padding_count_not_encrypted():
    stack = CryptoStack(TextEncoder(), 8, AdditionCipher(257))
    ints = stack.encrypt("hello", 5)
    assert ints[0] == stack.blocker.block(TextEncoder().encode("hello"))[0]


def test_candidate_inverses():
    rng = random.Random(3)
    cases = [(7, 30), (3, 8), (5, 8), (11, 26), (17, 256), (65535, 2**16)]
    cases += [(rng.getrandbits(512) | 1, 2**512) for _ in range(5)]
    for n, mod in cases:
        assert n * candidates.euclidean_inverse_1(mod, n) % mod == 1
        assert n * candidates.multiplicative_inverse_2(n, mod) % mod == 1
        assert n * candidates.inv_3(n, mod) % mod == 1
        assert n * candidates.multi_inverse_4(n, mod) % mod == 1
        assert n * candidates.inverse_5(n, mod) % mod == 1
        assert n * candidates.better_inverse_6(n, mod) % mod == 1
        assert n * candidates.find_inverse_7(n, mod) % mod in (1, mod - 1)
    for n, mod in cases[:6]:
        assert n * candidates.bash_multi_inverse_8(n, mod) % mod == 1


def test_candidate_ciphers():
    rng = random.Random(4)
    for block_size in [8, 16, 64]:
        mod = 2 ** block_size
        a, b = rng.randrange(mod) | 1, rng.randrange(mod)
        ciphers = [
            (candidates.MultiplicationCipher1(mod, a), a),
            (candidates.MultiplicationCipher2(mod), a),
            (candidates.AffineCipher1(mod), (a, b)),
            (candidates.AffineCipher3(mod, a, b), (a, b)),
            (candidates.AffineCipher4(mod), (a, b)),
            (candidates.AffineCipher5(mod, candidates.inv_3(a, mod)), (a, b)),
        ]
        if block_size <= 16:
            ciphers.append((candidates.MultiplicationCipher3(mod), a))
        loaded = candidates.AffineCipher2(mod)
        loaded.load_key(a, b)
        ciphers.append((loaded, None))
        for cipher, key in ciphers:
            stack = CryptoStack(TextEncoder(), block_size, cipher)
            message = random_message(ALPHABET, rng, 30)
            assert stack.receive(stack.send(message, key), key) == message


if __name__ == "__main__":
    for name, test in list(globals().items()):
        if name.startswith("test_"):
            test()
            print("passed", name)
