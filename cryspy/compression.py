"""Huffman codes and LZ77, the pieces inside CompressionEncoder.

Notation from the Day 7 lecture: the message is read left to right, and i is
how many symbols have been written so far. A match token (d, m) means "go
back d symbols and copy m symbols". Since 1 <= d <= i, d - 1 fits in
ceil(log2 i) bits, and the decoder knows i too, so no width prefix is needed.
m is written with an Elias gamma code: (number of bits of m) - 1 zeros, then
m in binary.
"""

from __future__ import annotations

from collections.abc import Hashable, Sequence


class MinHeap:
    def __init__(self) -> None:
        self.lst = []
        self.size = 0

    def __len__(self) -> int:
        return self.size

    def _swap(self, a: int, b: int) -> None:
        temp = self.lst[a]
        self.lst[a] = self.lst[b]
        self.lst[b] = temp

    def insert(self, element) -> None:
        self.lst.append(element)
        cur = self.size
        self.size += 1

        while cur > 0:
            parent = (cur - 1) // 2
            if self.lst[parent] < self.lst[cur]:
                break
            self._swap(parent, cur)
            cur = parent

    def pop(self):
        if self.size == 0:
            raise IndexError("Cannot pop from an empty heap")

        top = self.lst[0]
        self.size -= 1

        if self.size == 0:
            self.lst = []
            return top

        self.lst[0] = self.lst.pop()

        cur = 0
        while cur < self.size:
            left = 2 * cur + 1
            right = 2 * cur + 2

            # swap with the smaller child, so the smallest of the three ends up on top
            smallest = cur
            if left < self.size and self.lst[left] < self.lst[smallest]:
                smallest = left
            if right < self.size and self.lst[right] < self.lst[smallest]:
                smallest = right
            if smallest == cur:
                break
            self._swap(cur, smallest)
            cur = smallest

        return top


def create_huffman_tree(letter_weights: dict[Hashable, float]) -> dict[Hashable, str]:
    """From the weight of each letter in an alphabet, creates a dict mapping
    each letter to its prefix-free bitstring. O(n log n) in the alphabet size."""

    if len(letter_weights) < 2:
        raise ValueError("A Huffman code needs at least two letters")

    class TreeNode:
        def __init__(self, letter, weight: float, left, right):
            self.letter = letter
            self.weight = weight
            self.left = left
            self.right = right

        def __lt__(self, other):
            return self.weight < other.weight

    nodes = MinHeap()

    for letter in letter_weights:
        nodes.insert(TreeNode(letter, letter_weights[letter], None, None))

    while len(nodes) > 1:
        a = nodes.pop()
        b = nodes.pop()
        nodes.insert(TreeNode(None, a.weight + b.weight, a, b))

    encodings = {}

    def dfs(node: TreeNode, prefix: str):
        if node.left is None:
            encodings[node.letter] = prefix
            return

        dfs(node.left, prefix + "0")
        dfs(node.right, prefix + "1")

    dfs(nodes.pop(), "")

    return encodings


class LZ77_Entry:
    def __init__(self, is_literal: bool, val):
        """A literal has val = the letter. A match has val = (d, m)."""
        self.is_literal = is_literal
        self.val = val


def _to_binary(n: int, width: int) -> str:
    n_bitstr = bin(n)[2:]
    return ("0" * (width - len(n_bitstr))) + n_bitstr


def match_bits(i: int, d: int, m: int) -> int:
    """Bits LZ77_to_bits spends on a match (d, m) at position i."""
    return 1 + (i - 1).bit_length() + (2 * m.bit_length() - 1)


def LZ77_encode(message: Sequence, code: dict[Hashable, str]) -> list[LZ77_Entry]:
    """Greedy LZ77 with no limit on history. O(len(message)^3).

    A match is used only when it costs fewer bits than writing its letters
    as literals with `code`.
    """

    out = []
    i = 0
    while i < len(message):
        longest_m = 0
        longest_start = 0
        for j in range(i - 1, -1, -1):
            # count how many symbols match starting at i and at j
            m = 0
            while i + m < len(message) and message[i + m] == message[j + m]:
                m += 1
            if longest_m < m:
                longest_start = j
                longest_m = m

        d = i - longest_start
        literal_bits = sum(1 + len(code[c]) for c in message[i:i + longest_m])
        if longest_m >= 2 and match_bits(i, d, longest_m) < literal_bits:
            out.append(LZ77_Entry(False, (d, longest_m)))
            i += longest_m
        else:
            out.append(LZ77_Entry(True, message[i]))
            i += 1
    return out


def LZ77_decode(lst: list[LZ77_Entry]) -> list:
    """LZ77_decode(LZ77_encode(message)) is the message, as a list. O(len(message))."""

    out = []
    for a in lst:
        if a.is_literal:
            out.append(a.val)
            continue

        d, m = a.val
        start = len(out) - d
        # copying one symbol at a time lets a match overlap itself (d < m)
        for k in range(m):
            out.append(out[start + k])

    return out


def LZ77_to_bits(LZ77_list: list[LZ77_Entry], code: dict[Hashable, str]) -> str:
    """Literal: 0, then the letter's Huffman code.
    Match (d, m): 1, then d - 1 in ceil(log2 i) bits, then m in Elias gamma."""
    bits = []
    i = 0  # how many symbols have been encoded so far

    for a in LZ77_list:
        if a.is_literal:
            bits.append("0")
            bits.append(code[a.val])
            i += 1
            continue

        bits.append("1")
        d, m = a.val

        width = (i - 1).bit_length()
        if width > 0:
            bits.append(_to_binary(d - 1, width))

        m_bitstr = bin(m)[2:]
        bits.append("0" * (len(m_bitstr) - 1))
        bits.append(m_bitstr)
        i += m

    return "".join(bits)


def bits_to_LZ77(bits: str, code: dict[Hashable, str]) -> list[LZ77_Entry]:
    """Inverse of LZ77_to_bits."""
    letter_of = {code[c]: c for c in code}
    k = 0  # position in bits
    i = 0  # how many symbols have been decoded so far
    out = []
    while k < len(bits):
        if bits[k] == "0":
            # literal: read bits until they spell a Huffman code
            k += 1
            word = bits[k]
            while word not in letter_of:
                k += 1
                word += bits[k]
            k += 1
            out.append(LZ77_Entry(True, letter_of[word]))
            i += 1
        else:
            k += 1
            # d - 1 in a fixed ceil(log2 i) bits
            width = (i - 1).bit_length()
            d = 0
            for _ in range(width):
                d <<= 1
                if bits[k] == "1":
                    d += 1
                k += 1
            d += 1
            # m: count zeros to get the width, then read that many bits
            width = 1
            while bits[k] == "0":
                k += 1
                width += 1
            m = 0
            for _ in range(width):
                m <<= 1
                if bits[k] == "1":
                    m += 1
                k += 1
            out.append(LZ77_Entry(False, (d, m)))
            i += m
    return out
