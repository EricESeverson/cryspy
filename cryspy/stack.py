"""CryptoStack: encode, block, encrypt, then write as text to paste into chat."""

from __future__ import annotations

import base64

from .blocker import Blocker
from .ciphers import Cipher
from .encoders import Encoder


def to_text(data: bytes, text_format: str) -> str:
    if text_format == "hex":
        return data.hex()
    if text_format == "base64":
        return base64.b64encode(data).decode("ascii")
    raise ValueError("text_format must be 'hex' or 'base64'")


def from_text(text: str, text_format: str) -> bytes:
    if text_format == "hex":
        return bytes.fromhex(text)
    if text_format == "base64":
        return base64.b64decode(text)
    raise ValueError("text_format must be 'hex' or 'base64'")


class CryptoStack:
    """send: encode, block, encrypt each block, write as text.
    receive: undo each step in reverse order."""

    def __init__(self, encoder: Encoder, block_size: int, cipher: Cipher,
                 text_format: str = "hex") -> None:
        self.encoder = encoder
        self.blocker = Blocker(block_size)
        if 2 ** block_size > cipher.mod:
            raise ValueError("Ur special! Cipher mod less than 2^block_size")
        self.cipher = cipher
        self.text_format = text_format
        # every ciphertext int is less than mod, so it fits in this many bytes
        self.bytes_per_block = ((cipher.mod - 1).bit_length() + 7) // 8

    def encrypt(self, message: str, key) -> list[int]:
        """message --> list of encrypted ints (the padding count is encrypted too)"""
        blocks = self.blocker.block(self.encoder.encode(message))
        return [self.cipher.encrypt(num, key) for num in blocks]

    def decrypt(self, ints: list[int], key) -> str:
        decrypted = [self.cipher.decrypt(num, key) for num in ints]
        return self.encoder.decode(self.blocker.deblock(decrypted))

    def send(self, message: str, key) -> str:
        ints = self.encrypt(message, key)
        data = b"".join(num.to_bytes(self.bytes_per_block, "big") for num in ints)
        return to_text(data, self.text_format)

    def receive(self, text: str, key) -> str:
        data = from_text(text, self.text_format)
        n = self.bytes_per_block
        ints = [int.from_bytes(data[k:k + n], "big") for k in range(0, len(data), n)]
        return self.decrypt(ints, key)
