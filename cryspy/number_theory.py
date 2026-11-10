"""Number theory primitives, as written with the class on Day 11 (Nov 3)."""
from profiling import PRIMES_BELOW_200

def gcd(a, b):
    """GCD

    Args:
      a (int), b (int): input integers
  
    Returns:
      Value of gcd(a,b)

    """
    if b == 0: return a
    return gcd(b, a % b)


def vgcd(u, v):
    """Vector gcd

    Args: 
        u (tuple): first input vector
        v (tuple): second

    Returns:
        Vector gcd of u and v
    

    
    """
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

    binary = bin(b)[2:]
    cur = 1

    for char in binary:
        cur = (cur * cur)%n
        if char == '1':
            cur = (cur*a) % n

    return cur


def factor(n: int) -> dict[int, int]:
    """Factor function - TODO"""
    
    factors = {}
    d = 2

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


def is_gen(g: int, n: int, factorization: dict[int, int] | None = None) -> bool:
    """TODO"""
   
    if pow(g, n-1, n) != 1:
        return False
    
    if factorization == None:
      factorization = factor(m-1)

    for p in factorization.keys():
        if pow(g,(n-1)//p, n) == 1:
            return False
            
    return True


def find_gen(p: int) -> int | None:
    """TODO"""
    if p < 2:
        return None
        
    factorization = factor(p-1)
    for i in range(1, p):
        if is_gen(i, p, factorization):
            return i
            
    return None
    

def is_prime(n: int) -> bool:
    """TODO"""
    
    if n == 2 or n == 3:
        return True
    elif n < 2:
        return False
        
    for p in PRIMES_BELOW_200:
        if n % p == 0:
            return False

    g = find_gen(n)
    return g != None


def next_prime(n: int) -> int:
    """TODO"""
    
    while not is_prime(n):
        n += 1
    return n



