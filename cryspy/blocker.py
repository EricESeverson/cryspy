"""Cutting bytes into blocks of `block_size` bits, and gluing them back."""

from __future__ import annotations


class Blocker:
    def __init__(self, block_size: int) -> None:
        self.block_size = block_size

    def block(self, data: bytes) -> list[int]:
        """bytes --> list of ints, each less than 2**block_size.

        The bits are padded with 0s at the back to fill the last block, and
        the FIRST int in the list is how many padding bits were added.
        """
        bits = "".join(f"{byte:08b}" for byte in data)
        padding_len = (-len(bits)) % self.block_size
        bits += "0" * padding_len
        # the int(..., 2) means reading off in base 2
        blocks = [int(bits[k:k + self.block_size], 2)
                  for k in range(0, len(bits), self.block_size)]
        return [padding_len] + blocks

    def deblock(self, ints: list[int]) -> bytes:
        """list of ints --> bytes. Reads the first int as the amount of padding."""
        padding_len = ints[0]
        bits = "".join(f"{num:0{self.block_size}b}" for num in ints[1:])
        if padding_len != 0:
            bits = bits[:-padding_len]
        # the 8s here are for grouping 8 bits into a byte
        return bytes(int(bits[k:k + 8], 2) for k in range(0, len(bits), 8))
