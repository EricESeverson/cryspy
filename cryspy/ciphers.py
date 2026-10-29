from abc import ABC, abstractmethod


class Cipher(ABC):
    @abstractmethod
    def encrypt(self, num: int, key) -> int:
        """Encrypts a singular number"""

    @abstractmethod
    def decrypt(self, num: int, key) -> int:
        """Decrypts a singular number"""


class AdditionCipher(Cipher):
    def __init__(self, mod: int) -> None:
        self.mod = mod

    def encrypt(self, num: int, key: int) -> int:
        return (num + key) % self.mod

    def decrypt(self, num: int, key: int) -> int:
        return (num - key) % self.mod
