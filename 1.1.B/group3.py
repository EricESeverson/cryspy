from collections.abc import Callable, Sequence, Iterable


class MinHeap[T]:
    def __init__(self) -> None:
        self.lst = []
        self.size = 0

    def __len__(self) -> int:
        return self.size

    def _swap(self, a: int, b: int) -> None:
        temp = self.lst[a]
        self.lst[a] = self.lst[b]
        self.lst[b] = temp

    def insert(self, element: T) -> None:
        self.lst.append(element)
        cur = self.size
        self.size += 1

        while (cur > 0):
            parent = (cur-1)//2
            if (self.lst[parent] < self.lst[cur]):
                break
            self._swap(parent, cur)
            cur = parent

    def pop(self) -> T:
        if (self.size == 0):
            raise Exception("Cannot pop from an empty heap")

        top = self.lst[0]
        self.size -= 1

        if self.size == 0:
            self.lst = []
            return top

        self.lst[0] = self.lst.pop()

        cur = 0
        while (cur < self.size):
            left = 2 * cur + 1
            right = 2 * cur + 2

            # swap with the smaller child, so the smallest of the three ends up on top
            smallest = cur
            if (left < self.size) and (self.lst[left] < self.lst[smallest]):
                smallest = left
            if (right < self.size) and (self.lst[right] < self.lst[smallest]):
                smallest = right
            if smallest == cur:
                break
            self._swap(cur, smallest)
            cur = smallest

        return top
    

from typing_extensions import Hashable

def create_huffman_tree(frequencies: dict[Hashable, float]) -> dict[Hashable, str]:
    """From frequencies of each character in an alphabet,
    creates a dict mapping byte to its prefix free string.
    O(n log n) in the alphabet size"""

    class TreeNode:
        def __init__(self, b: bytes, val: int, left, right):
            self.b = b
            self.val = val
            self.left = left
            self.right = right

        def __lt__(self, other):
            return self.val < other.val

    nodes = MinHeap()

    for b in frequencies:
        nodes.insert(TreeNode(b, frequencies[b], None, None))

    while len(nodes) > 1:
        a = nodes.pop()
        b = nodes.pop()

        new = TreeNode(None, a.val + b.val, a, b)
        nodes.insert(new)


    encodings = {}
    def dfs(node: TreeNode, prefix: str):
        if not node.b is None:
            encodings[node.b] = prefix
            return

        dfs(node.left, prefix + "0")
        dfs(node.right, prefix + "1")

    dfs(nodes.pop(), "")

    return encodings

class LZ77_Entry:
    def __init__(self, is_literal, val):
        self.is_literal = is_literal
        self.val = val

def LZ77_encode(b: Iterable) -> list[LZ77_Entry]:
    """O(len(b)^3)"""

    out = []
    i = 0
    while i < len(b):
        longest_match_len = 0
        longest_match = 0
        for i2 in range(i-1, -1, -1):
            cur_match_len = 0
            # search d characters match, no limit to history
            d = 0
            while (i + d < len(b)):
                if b[i + d] == b[i2 + d]:
                    cur_match_len += 1
                else:
                    break
                d += 1
            if longest_match_len < cur_match_len:
                longest_match = i2
                longest_match_len = cur_match_len
        # assume that match length must be greater than 2
        if longest_match_len >= 2:
            entry = LZ77_Entry(False, (i-longest_match, longest_match_len))
            out.append(entry)
            i += longest_match_len
        else:
            entry = LZ77_Entry(True, b[i])
            out.append(entry)
            i += 1
    return out

def LZ77_decode(lst):
    """Decompressed lst using LZ77. LZ77_decode(LZ77_encode(b)) is b.
    O(len(b))"""

    out = []
    for a in lst:
        if a.is_literal:
            out.append(a.val)
            continue


        index = len(out) - a.val[0]

        for i in range(a.val[1]):
            out.append(out[index])
            index += 1

    return out

from math import log2, ceil

def _to_binary(n, l):
    n_bistr = bin(n)[2:]
    return ("0" * (l - len(n_bistr))) + n_bistr


# s to i is literal -> prefix free bitstring
def encode_compress(LZ77_list, stoi):
    bits = []

    for a in LZ77_list:
        if a.is_literal:
            bits.append("0")
            for b in stoi[a.val]:
                bits.append(b)

            continue

        bits.append("1")

        n, m = a.val

        l = ceil(log2(max(n, m) + 1))

        for _ in range(l-1):
            bits.append("0")
        bits.append("1")


        n_bitstr = _to_binary(n, l)
        m_bitstr = _to_binary(m, l)

        for b in (n_bitstr):
            bits.append(b)
        for b in (m_bitstr):
            bits.append(b)

    return "".join(bits)

# b is bitstring, itos is from bitstring to character
def decode_compressed(b, itos):
    keys = itos.keys()
    i = 0
    s = []
    while i < len(b):
        if b[i] == "0":
            i += 1
            # literal
            # then following was encoded by dictionary
            n = b[i]
            while n not in keys:
                i += 1
                n += b[i]
            entry = LZ77_Entry(True, itos[n])
            s.append(entry)
            i += 1
        else:
            i += 1
            # then this is LZ77 thing
            
            # figure out byte length of integers
            l = 1 # l is subtracted one from encode
            while b[i] == "0":
                i += 1
                l += 1
            # skip the one bit
            i += 1
            m = 0
            for _ in range(l):
                m <<= 1
                if b[i] == "1":
                    m += 1
                i += 1
            # read n same way
            n = 0
            for _ in range(l):
                n <<= 1
                if b[i] == "1":
                    n += 1
                i += 1
            entry = LZ77_Entry(False, (m, n))
            s.append(entry)
    return s


class Encoder:
    def __init__(self, alphabet, frequencies: dict) -> None:
        self.alphabet = alphabet
        self.compressor = Compressor(alphabet, frequencies)

    def encode(self, message: Sequence) -> bytes:
        return None

    def decode(self, data: bytes) -> Sequence:
        return None

class Compressor:
    def _invert_dict(self, d: dict) -> dict:
        return {d[k] : k for k in d}

    def _create_huffman_tree(self, frequencies: dict[Hashable, float]) -> dict[Hashable, str]:
        """From frequencies of each character in an alphabet,
        creates a dict mapping byte to its prefix free string.
        O(n log n) in the alphabet size"""

        class TreeNode:
            def __init__(self, b: bytes, val: int, left, right):
                self.b = b
                self.val = val
                self.left = left
                self.right = right

            def __lt__(self, other):
                return self.val < other.val

        nodes = MinHeap()

        for b in frequencies:
            nodes.insert(TreeNode(b, frequencies[b], None, None))

        while len(nodes) > 1:
            a = nodes.pop()
            b = nodes.pop()

            new = TreeNode(None, a.val + b.val, a, b)
            nodes.insert(new)


        encodings = {}
        def dfs(node: TreeNode, prefix: str):
            if not node.b is None:
                encodings[node.b] = prefix
                return

            dfs(node.left, prefix + "0")
            dfs(node.right, prefix + "1")

        dfs(nodes.pop(), "")

        return encodings

    def LZ77_encode(self, b: Sequence) -> list[LZ77_Entry]:
        """O(len(b)^3)"""

        out = []
        i = 0
        while i < len(b):
            longest_match_len = 0
            longest_match = 0
            for i2 in range(i-1, -1, -1):
                cur_match_len = 0
                # search d characters match, no limit to history
                d = 0
                while (i + d < len(b)):
                    if b[i + d] == b[i2 + d]:
                        cur_match_len += 1
                    else:
                        break
                    d += 1
                if longest_match_len < cur_match_len:
                    longest_match = i2
                    longest_match_len = cur_match_len
            # assume that match length must be greater than 2
            if longest_match_len >= 2:
                entry = LZ77_Entry(False, (i-longest_match, longest_match_len))
                out.append(entry)
                i += longest_match_len
            else:
                entry = LZ77_Entry(True, b[i])
                out.append(entry)
                i += 1
        return out

    def LZ77_decode(self, lst: list[LZ77_Entry]) -> Sequence:
        """Decompressed lst using LZ77. LZ77_decode(LZ77_encode(b)) is b.
        O(len(b))"""

        out = []
        for a in lst:
            if a.is_literal:
                out.append(a.val)
                continue


            index = len(out) - a.val[0]

            for i in range(a.val[1]):
                out.append(out[index])
                index += 1

        return out

    def LZ77_to_bits(self, LZ77_list: list[LZ77_Entry], stoi: dict[Hashable, str]) -> str:
        bits = []

        for a in LZ77_list:
            if a.is_literal:
                bits.append("0")
                for b in stoi[a.val]:
                    bits.append(b)

                continue

            bits.append("1")

            n, m = a.val

            # each number gets its own width: (width - 1) zeros, then the
            # number in binary, whose leading 1 marks where the zeros end
            for x in (n, m):
                x_bitstr = bin(x)[2:]
                for _ in range(len(x_bitstr) - 1):
                    bits.append("0")
                for b in x_bitstr:
                    bits.append(b)

        return "".join(bits)

    def bits_to_LZ77(self, b: str, itos: dict[Hashable, str]) -> list[LZ77_Entry]:
        keys = itos.keys()
        i = 0
        s = []
        while i < len(b):
            if b[i] == "0":
                i += 1
                # literal
                # then following was encoded by dictionary
                n = b[i]
                while n not in keys:
                    i += 1
                    n += b[i]
                entry = LZ77_Entry(True, itos[n])
                s.append(entry)
                i += 1
            else:
                i += 1
                # then this is LZ77 thing
                
                vals = []
                for _ in range(2):
                    # count zeros to get the width, then read that many bits
                    l = 1
                    while b[i] == "0":
                        i += 1
                        l += 1
                    x = 0
                    for _ in range(l):
                        x <<= 1
                        if b[i] == "1":
                            x += 1
                        i += 1
                    vals.append(x)
                entry = LZ77_Entry(False, (vals[0], vals[1]))
                s.append(entry)
        return s

    def __init__(self, alphabet, letter_weights: dict) -> None:
        self.alphabet = alphabet
        self.encoding_tree = self._create_huffman_tree(letter_weights)
        self.decoding_tree = self._invert_dict(self.encoding_tree)

    def compress(self, message: Sequence) -> bytes:
        LZ77_list = self.LZ77_encode(message)
        return self.LZ77_to_bits(LZ77_list, self.encoding_tree)

    def decompress(self, data: bytes) -> Sequence:
        LZ77_list = self.bits_to_LZ77(data, self.decoding_tree)
        print([l.val for l in LZ77_list])
        return self.LZ77_decode(LZ77_list)



class CompressTest:
    def __init__(self, 
                compress: Callable[[bytes], bytes], 
                decompress: Callable[[bytes], bytes]):
                
        self.compress = compress
        self.decompress = decompress

    def _test_compression_corpus(self, corpus: bytes) -> tuple[bool, float]:
        """
        
        """
        compressed = self.compress(corpus)
        return (self.decompress(compressed) == corpus, len(compressed)/len(bytes))

    def _get_test_corpora(self) -> list[bytes]:
        pass

    def _test_compress_decompress(self) -> bool:
        corpora = _get_test_corpora()
        pass_all_cases = True

        for i, corpus in enumerate(corpora):
            does_pass, score = _test_self.compression_corpus(corpus)
            pass_all_cases = pass_all_cases and does_pass
            pass_status = '✅' if does_pass else '❌'
            print(f"Test case #{i}: {pass_status} {score=}")



