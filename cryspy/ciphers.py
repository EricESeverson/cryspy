"""Ciphers act on one block at a time: an integer `num` and a key."""

from __future__ import annotations

from abc import ABC, abstractmethod


class Cipher(ABC):
    """Every cipher encrypts and decrypts a single integer `num` with a key.

    The key is given on every call and never stored ("the only secret is
    the key"). Ciphertext integers lie in range(mod).
    """

    mod: int

    @abstractmethod
    def encrypt(self, num: int, key) -> int:
        """Encrypts a single number."""

    @abstractmethod
    def decrypt(self, num: int, key) -> int:
        """Decrypts a single number."""


class AdditionCipher(Cipher):
    def __init__(self, mod: int) -> None:
        self.mod = mod

    def encrypt(self, num: int, key: int) -> int:
        return (num + key) % self.mod

    def decrypt(self, num: int, key: int) -> int:
        return (num - key) % self.mod
