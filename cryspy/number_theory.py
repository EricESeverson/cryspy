"""Number theory primitives, as written with the class on Day 11 (Nov 3)."""


def gcd(a, b):
    """TODO"""
    if b == 0: return a
    return gcd(b, a % b)


def vgcd(u, v):
    """TODO"""
    if v[1] == 0: return u
    q, r = divmod(u[1], v[1])
    w = (u[0] - q*v[0], r)    # w = u - q v
    return vgcd(v, w)


def mult_inverse(a, n):
    """TODO"""
    gx, gy = vgcd((0, n), (1, a))
    if gy != 1: raise ValueError(f"gcd(n, a) = {gy} != 1")
    return gx % n

def exp(a: int, b: int, n: int) -> int:
    """Power function - TODO"""

    binary = bin(b)[3:][::-1]
    total = a

    for b in binary:
      if b == '0':
        total = (total * total) % n 
      elif b == '1': 
        total = (total * total * a) % n      

    return cur

def factor(n: int) -> dict[int, int]:
    """Factor function - TODO"""
    
    factors = {}
    def = 2

    while d ** 2 <= n:
        while n % d == 0:
            if d not in factors.keys():
                factors[d] = 0
            factors[d] += 1
            n = n // d
        d += 1
    
    if n > 1:
        factors[n] = 1

    return factors

def totient(n: int) -> int:
  """Euler's totient function

  Args:
    n (int): input integer
  
  Returns:
    Value of totient function on n

  """
  total = 1
  for n_fact, exp in factor(n).items():
    if exp == 1:
      total *= n_fact-1
    else:
      total *= n_fact**exp - n_fact**(exp-1)
  return total

def is_prime(n: int) -> bool:
    """Prime function - placeholder"""
    
    if n < 2:
        return False
    return len(factor(n)) == 1


