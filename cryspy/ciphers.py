from abc import ABC, abstractmethod


class Cipher(ABC):
    """TODO"""
    @abstractmethod
    def encrypt(self, num: int, key) -> int:
        """Encrypts a singular number.

        Args:
            num: the number to encrypt.
            key: the key.

        Returns:
            The encrypted number.
        """

    @abstractmethod
    def decrypt(self, num: int, key) -> int:
        """Decrypts a singular number.

        Args:
            num: the number to decrypt.
            key: the key.

        Returns:
            The decrypted number.
        """


class AdditionCipher(Cipher):
    """TODO"""
    def __init__(self, mod: int) -> None:
        self.mod = mod

    def encrypt(self, num: int, key: int) -> int:
        """TODO"""
        return (num + key) % self.mod

    def decrypt(self, num: int, key: int) -> int:
        """TODO"""
        return (num - key) % self.mod
