# 1.3.A Group 1
import cryspy as cp

from collections.abc import Iterator
from itertools import product

def is_prime(n: int) -> bool:
    if (n <= 1):
        return False

    i = 2
    while (i * i) <= n:
        if (n%i) == 0:
            return False
        i += 1

    return True


def next_prime(n: int) -> bool:
    while True:
        if is_prime(n):
            return n

        n += 1


def totient(factorization: dict[int, int]) -> int:
    """
    takes in dictionary of prime factors and powers
    returns totient value of n
    """
    
    product = 1
    for prime, exp in factorization.items():
        product *= (prime ** (exp-1)) * (prime-1)
    return product


def factorize(n: int) -> dict[int, int]:
    factors = {}

    i = 2
    while n > 1:
        if (n%i) == 0:
            factors[i] = 0
            while (n%i) == 0:
                factors[i] += 1
                n //= i

        i += 1

    return factors
            

def factors(n: int) -> Iterator[int]:
    factors = list(factorize(n).items())
    iterators = [range(e+1) for p, e in factors]

    for exponents in product(*iterators):
        out = 1
        for i in range(len(factors)):
            out *= factors[i][0] ** exponents[i]
        
        yield out


def is_gen(g: int, p: int) -> bool:
    for f in factors(p-1):
        if f == (p-1):
            continue

        if pow(g, f, p) == 1:
            return False
    
    return pow(g, p-1, p) == 1


class ExponentiationCipher:
   def __init__(self, mod: int) -> None:
       self.mod = mod


   def encrypt(self, num: int, key: int) -> int:
       return fast_exp(key, num, self.mod)


   def decrypt(self, num: int, key: int) -> int:
       for i in range(self.mod):
           if fast_exp(key, i, self.mod) == num:
               return i


class PowerCipher:
   def __init__(self, mod: int) -> None:
       self.mod = mod


   def encrypt(self, num: int, key: int) -> int:
       return fast_exp(num, key, self.mod)


   def decrypt(self, num: int, key: int) -> int:
       for i in range(self.mod):
           if fast_exp(i, key, self.mod) == num:
               return i

