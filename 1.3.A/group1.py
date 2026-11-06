# 1.3.A Group 1
import cryspy as cp

def is_prime(n: int) -> bool:
    """checks if number is prime"""
    return None

def prime_factorize(n ) --> dict: # key = prime, value = exp
    """returns prime factorization as dict"""
	pass


def find_primative_root(n: int) --> int:
    """returns a primative root of n"""
    pass

def find_all_primative_roots(n: int, p: int) --> int:
    """returns list of primitives roots of n"""
    pass

def slow_exp(a: int, p: int, n: int) -> int:
    """Returns a ** p mod n"""
    return a ** p mod n


def fast_exp(a: int, p: int, n: int) -> int:
    """Returns a ** p mod n faster"""
    return a ** p mod n

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

