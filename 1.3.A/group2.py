# 1.3.A Group 2
import cryspy as cp

def exp(a, b, m):
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

def is_prime(n: int) -> bool:
    """
    Returns true if n is prime and false otherwise
    """
    return len(factors(n)) == 1

def factors(n: int) -> list[int]:
    """
    Returns a list of the factors of n
    """
    divisors = []
    for i in range(1, n):
        if n%i == 0:
            divisors.append(i)
    return divisors

def prime_factor(n):
    """
    returns a list of tuples of (prime, prime-adic valuation of n)
    """
    if (n == 1):
        return []
    for test_div in range(2, n + 1):
        if n % test_div == 0:
            i = 1

def totient(n):
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
    if not is_prime(p):
        return False
    # check g to the power of all divisors of the totient (which will be p-1)
    factors = prime_factor(p-1)
    for factor in factors:
        # we check g ** ((p-1) / each prime function)
        if pow(g, (p - 1) // factor[0], p) == 1:
            return False
    return True
