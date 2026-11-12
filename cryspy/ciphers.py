from abc import ABC, abstractmethod

from .number_theory import mult_inverse


class Cipher(ABC):
    """TODO"""
    messages: range    # M, the set of messages; each cipher sets it in __init__

    @abstractmethod
    def encrypt(self, num: int, key) -> int:
        """Encrypts a singular number.

        Args:
            num: the number to encrypt.
            key: the key.

        Returns:
            The encrypted number.
        """

    # A cipher that writes no decrypt gets this brute force one.
    def decrypt(self, num: int, key) -> int:
        """Decrypts a singular number.

        Args:
            num: the number to decrypt.
            key: the key.

        Returns:
            The decrypted number.
        """
        return self.brute_force_decrypt(num, key)

    # Tries every message, about len(messages) encryptions.
    def brute_force_decrypt(self, num: int, key) -> int:
        """TODO"""
        for m in self.messages:
            if self.encrypt(m, key) == num:
                return m
        raise ValueError(f"no message encrypts to {num}")

    # decrypt undoes encrypt on every message, so encrypt is one-to-one.
    # With the brute force decrypt this takes about len(messages)^2 steps.
    def is_valid(self, key) -> bool:
        """
        Tests to see if a cipher is a bijection

        Args:
            key: the key

        Returns:
            True if cipher is valid, False otherwise
        """
        for m in self.messages:
            if self.decrypt(self.encrypt(m, key), key) != m:
                return False
        return True


class AdditionCipher(Cipher):
    """TODO"""
    def __init__(self, mod: int) -> None:
        self.mod = mod
        self.messages = range(mod)

    def encrypt(self, num: int, key: int) -> int:
        """TODO"""
        return (num + key) % self.mod

    def decrypt(self, num: int, key: int) -> int:
        """TODO"""
        return (num - key) % self.mod


# Encrypt checks the inverse exists too, so nothing gets encrypted that
# can't be decrypted.
class AffineCipher(Cipher):
    """TODO"""

    def __init__(self, mod: int) -> None:
        self.mod = mod
        self.messages = range(mod)
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


# The key g is the base; messages are exponents 0, ..., mod - 2.
# When mod is a prime p, is_valid(g) exactly when g is a primitive root
# mod p.
class ExponentiationCipher(Cipher):
    """Exponentiation Cipher"""
    def __init__(self, mod: int) -> None:
        self.mod = mod
        self.messages = range(mod - 1)

    def encrypt(self, num: int, key: int) -> int:
        "returns key ^ num"
        return pow(key, num, self.mod)


# The key k is the exponent; messages are bases 0, ..., mod - 1.
class PowerCipher(Cipher):
    """TODO"""
    def __init__(self, mod: int) -> None:
        self.mod = mod
        self.messages = range(mod)

    def encrypt(self, num: int, key: int) -> int:
        """TODO"""
        return pow(num, key, self.mod)
