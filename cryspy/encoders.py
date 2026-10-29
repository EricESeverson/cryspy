"""Encoders turn a message into bytes and back."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Hashable

from . import compression


class Encoder(ABC):
    @abstractmethod
    def encode(self, message: str) -> bytes:
        """message --> bytes"""

    @abstractmethod
    def decode(self, data: bytes) -> str:
        """bytes --> message. decode(encode(message)) is the message."""


class TextEncoder(Encoder):
    """Any text, using one of Python's encodings (UTF-8 by default)."""

    def __init__(self, encoding: str = "utf-8") -> None:
        self.encoding = encoding

    def encode(self, message: str) -> bytes:
        return message.encode(self.encoding)

    def decode(self, data: bytes) -> str:
        return data.decode(self.encoding)


class CompressionEncoder(Encoder):
    """Messages over a given alphabet, compressed with LZ77 and a Huffman code.

    `letter_weights` gives the Huffman code; by default every letter has
    weight 1. The receiver must use the same alphabet and weights.
    """

    def __init__(self, alphabet: str, letter_weights: dict[Hashable, float] | None = None) -> None:
        self.alphabet = alphabet
        if letter_weights is None:
            letter_weights = {c: 1 for c in alphabet}
        self.code = compression.create_huffman_tree(letter_weights)

    def compress(self, message: str) -> str:
        """message --> string of '0' and '1' characters"""
        for c in message:
            if c not in self.code:
                raise ValueError(f"{c!r} is not in the alphabet")
        LZ77_list = compression.LZ77_encode(message, self.code)
        return compression.LZ77_to_bits(LZ77_list, self.code)

    def decompress(self, bits: str) -> str:
        LZ77_list = compression.bits_to_LZ77(bits, self.code)
        return "".join(compression.LZ77_decode(LZ77_list))

    def encode(self, message: str) -> bytes:
        # same padding rule as Blocker: 0s at the back, and the first
        # byte says how many padding bits were added
        bits = self.compress(message)
        padding_len = (-len(bits)) % 8
        bits += "0" * padding_len
        return bytes([padding_len] + [int(bits[k:k + 8], 2) for k in range(0, len(bits), 8)])

    def decode(self, data: bytes) -> str:
        padding_len = data[0]
        bits = "".join(f"{byte:08b}" for byte in data[1:])
        if padding_len != 0:
            bits = bits[:-padding_len]
        return self.decompress(bits)
