# 1.3.A Group 2
import cryspy as cp
import math

def exp(a: int, b: int, m: int) -> int:
    '''
    returns a ** b mod m
    '''
    a_raised_to_power_of_two = a % m
    res = 1
    for i in range(0, b.bit_length()):
        if (b >> i & 1 == 1):
            res = res * a_raised_to_power_of_two % m
        # calculate a ** (2 ** i)
        a_raised_to_power_of_two = a_raised_to_power_of_two ** 2 % m
    return res

def is_prime(n):
    """
    returns true iff n is prime
    """
    # trial division up to sqrt(n), only by 1 or -1 mod 6
    if n == 2 or n == 3:
        return True
    
    if n % 2 == 0 or n % 3 == 0:
        return False
    
    for i in range(math.floor(n ** 0.5) // 6):
        if n % (6 * i - 1) == 0 or n % (6 * i + 1) == 0:
            return False
    return True

def factors(n: int) -> list[int]:
    """
    Returns a list of the factors of n
    """
    divisors = []
    for i in range(1, n):
        if n%i == 0:
            divisors.append(i)
    return divisors

def prime_factor(n: int) -> list[list[int, int]]:
    """
    returns a list of tuples of (prime, prime-adic valuation of n)
    """
    if (n == 1):
        return []
    for test_div in range(2, n + 1):
        if n % test_div == 0:
            i = 1
            while n % (test_div ** (i + 1)) == 0:
                i += 1
            return [(test_div, i)] + prime_factor(n // (test_div ** i))

def next_prime(n: int) -> int:
    """
    Returns the next prime larger than n
    """
    i = n+1
    while not is_prime(i):
        i += 1
    return i

def totient(n: int) -> int:
    """
    returns euler's totient of n
    """
    prime_factors = prime_factor(n)
    res = 1
    for factor in prime_factors:
        res *= factor[0] ** (factor[1] - 1) * (factor[0] - 1)
    return res

def is_gen(g: int, p: int) -> bool:
    """
    returns true iff g is a generator mod p
    """
    if pow(g, p-1, p) != 1:
        return False
    # check g to the power of all divisors of the totient (which will be p-1)
    factors = prime_factor(p-1)
    for factor in factors:
        # we check g ** ((p-1) / each prime function)
        if pow(g, (p - 1) // factor[0], p) == 1:
            return False
    return True

def find_gens(p: int) -> list[int]:
    """
    Returns a list of multiplicative generators 
    (primitive roots) within Z mod p
    """
    # finding first generator
    gen = 0
    for i in range(1, p):
        if is_gen(i, p):
            gen = i
            break

    # finding all of p's coprimes
    coprimes = [1]
    for i in range(2, p-1):
        if cp.gcd(i, p-1) == 1:
            coprimes.append(i)

    # this produces the rest of the primitive roots
    return [gen ** i % p for i in coprimes]
