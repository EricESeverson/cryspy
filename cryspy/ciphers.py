from abc import ABC, abstractmethod

from .number_theory import mult_inverse


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


# Team Bob's AffineCipher from 1.2.A, with Bob's docstrings, using
# mult_inverse from Day 11. Encrypt checks the inverse exists too, so
# nothing gets encrypted that can't be decrypted.
class AffineCipher(Cipher):
    """TODO"""

    def __init__(self, mod: int) -> None:
        self.mod = mod
        self.inverses = {}

    def _inverse(self, key_a):
        """Returns inverse. If not already calculated, calculates it.

        Args:
            key_a: the multiplicative number in the key tuple

        Returns:
            The multiplicative inverse of `key_a` mod `self.mod`
        """
        if key_a not in self.inverses:
            self.inverses[key_a] = mult_inverse(key_a, self.mod)

        return self.inverses[key_a]

    def encrypt(self, num: int, key: tuple[int, int]) -> int:
        """Returns the num encrypted using the key

        Args:
            num: the integer to encrypt
            key: a tuple (a, b)

        Returns:
            encrypted num with affine cipher applied
        """
        a, b = key
        self._inverse(a)
        return (a * num + b) % self.mod

    def decrypt(self, num: int, key: tuple[int, int]) -> int:
        """Returns the decrypted num using the key

        Args:
            num: integer to decrypt
            key: a tuple (a, b)

        Returns:
            decrypted num using affine cipher
        """
        a, b = key
        return ((num - b) * self._inverse(a)) % self.mod
