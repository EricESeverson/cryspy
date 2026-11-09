# 1.3.A Group 1
import cryspy as cp

def is_prime(n) -> bool:
    for i in range(2, int(n**0.5+1)):
        if (n%i == 0):
            return False
    return True

def factorize(n) -> dict[int, int]: # key = prime, value = exp
    out = {}
    div = 2
    while (div <= int(n**0.5+1)):
        while (n%div == 0):
            if(out.get(div) == None):
                out[div] = 0
            out[div]+=1
            n /= div
        div +=1
    if (n > 1):
        out[int(n)] = 1
    return out

def fast_totient(factorization: dict[int, int]) -> int:
    """
    takes in dictionary of prime factors and powers
    returns totient value of n
    """
    
    product = 1
    for prime, exp in factorization.items():
        product *= (prime ** (exp-1)) * (prime-1)
    return product

def slow_is_gen(g: int, p: int) -> bool:
    """Sees if the set r^k| 0<k<n is the same as {1, …, n-1}"""
    reached = [False]*p
    for i in range(0, p-1):
        val = fast_exp(g, i, p)
        if reached[val]:
            return False
        reached[val] = True
    return True


def find_all_primative_roots(n: int, p: int) -> int:
    """returns list of primitives roots of n"""
    pass

def fast_exp(a: int, p: int, n: int) -> int:
    """Find a ** p mod n.

    Args:
        a: base of exponentiation
        p: power
        n: modulo

    Returns:
        (a ** p) mod n.

    """
    out = 1
    for d in bin(p)[2:]:
        out *= out
        if (d == "1"):
            out *= a
        out %= n
    return out

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

