from collections.abc import Hashable, Sequence

from .encoders import Encoder
from .stack import bits_to_blocks, blocks_to_bits


class CompressionEncoder(Encoder):
    """TODO"""
    def __init__(self, alphabet: str, letter_weights: dict[Hashable, float] | None = None) -> None:
        self.alphabet = alphabet
        if letter_weights is None:
            letter_weights = {c: 1 for c in alphabet}
        self.code = create_huffman_tree(letter_weights)

    def compress(self, message: str) -> str:
        """TODO"""
        for c in message:
            if c not in self.code:
                raise ValueError(f"{c!r} is not in the alphabet")
        LZ77_list = LZ77_encode(message, self.code)
        return LZ77_to_bits(LZ77_list, self.code)

    def decompress(self, bits: str) -> str:
        """TODO"""
        LZ77_list = bits_to_LZ77(bits, self.code)
        return "".join(LZ77_decode(LZ77_list))

    def encode(self, message: str) -> bytes:
        # same padding rule as Blocker, with 8-bit blocks
        """TODO"""
        return bytes(bits_to_blocks(self.compress(message), 8))

    def decode(self, data: bytes) -> str:
        """TODO"""
        return self.decompress(blocks_to_bits(list(data), 8))


class LZ77_Entry:
    """TODO"""
    def __init__(self, is_literal: bool, val):
        self.is_literal = is_literal
        self.val = val


def LZ77_encode(message: Sequence, code: dict[Hashable, str]) -> list[LZ77_Entry]:
    """Compress message using LZ77. O(len(message)^3).

    Args:
        message: the symbols to compress.
        code: the Huffman code, used to tell whether a match costs fewer
            bits than its literals.

    Returns:
        A list of literals and (distance, length) matches.
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


def match_bits(i: int, d: int, m: int) -> int:
    """TODO"""
    return 1 + (i - 1).bit_length() + (2 * m.bit_length() - 1)


def LZ77_decode(lst: list[LZ77_Entry]) -> list:
    """Decompress lst using LZ77. O(len(message)).

    LZ77_decode(LZ77_encode(message, code)) is list(message).

    Args:
        lst: the entries from LZ77_encode.

    Returns:
        The decompressed symbols, as a list.
    """

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
    """TODO"""
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


def _to_binary(n: int, width: int) -> str:
    """TODO"""
    n_bitstr = bin(n)[2:]
    return ("0" * (width - len(n_bitstr))) + n_bitstr


def bits_to_LZ77(bits: str, code: dict[Hashable, str]) -> list[LZ77_Entry]:
    """TODO"""
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


def create_huffman_tree(letter_weights: dict[Hashable, float]) -> dict[Hashable, str]:
    """Build a Huffman code. O(n log n) in the alphabet size.

    Args:
        letter_weights: the frequency of each character in an alphabet.

    Returns:
        A dict mapping each character to its prefix free string of 0s and 1s.

    Raises:
        ValueError: if there are fewer than two letters.
    """

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


class MinHeap:
    """TODO"""
    def __init__(self) -> None:
        self.lst = []
        self.size = 0

    def __len__(self) -> int:
        return self.size

    def _swap(self, a: int, b: int) -> None:
        """TODO"""
        temp = self.lst[a]
        self.lst[a] = self.lst[b]
        self.lst[b] = temp

    def insert(self, element) -> None:
        """TODO"""
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
        """TODO"""
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
