"""Number theory primitives."""


def gcd(a: int, b: int) -> int:
    """TODO"""
    if b == 0: return a
    return gcd(b, a % b)


def vgcd(u: tuple[int, int], v: tuple[int, int]) -> tuple[int, int]:
    """TODO"""
    if v[1] == 0: return u
    q, r = divmod(u[1], v[1])
    w = (u[0] - q*v[0], r)    # w = u - q v
    return vgcd(v, w)


def mult_inverse(a: int, n: int) -> int:
    """TODO"""
    gx, gy = vgcd((0, n), (1, a))
    if gy != 1: raise ValueError(f"gcd(n, a) = {gy} != 1")
    return gx % n


# Binary search. Seconds on a random n (laptop):
#     bits of n     seconds
#          1024      0.0001
#          4096      0.004
#         16384      0.15
#         65536      4.5
#        262144    157
# Each step of the loop halves the interval and squares a number half the
# size of n, so about (bits of n) / 2 squarings in all.
# OPEN: Newton's method takes far fewer steps (each one a big division),
# a possible improvement for huge n.
def isqrt(n: int) -> int:
    """
    returns floor(n ** 0.5), but without float artifacts
    """
    # rough approximation:
    # bitlength of sqrt(n) is (n+1) // 2 bits long I think????
    if n == 0:
        return 0
    new_len = (n.bit_length() + 1) // 2
    min = 1 << (new_len - 1)
    max = 1 << new_len
    while min < max - 1:
        mid = (min + max) // 2
        mid2 = mid ** 2
        if mid2 > n:
            max = mid
        elif mid2 < n:
            min = mid
        else:
            return mid
    return max - 1


# Trial division, stopping at isqrt(n) (computed once, not squaring d
# every step). When n is prime it returns n itself.
def factor(n: int) -> int:
    """TODO"""
    r = isqrt(n)
    d = 2
    while d <= r:
        if n % d == 0:
            return d
        d += 1
    return n


def factorize(n: int) -> dict[int, int]:
    """TODO"""
    factors = {}
    d = 2
    r = isqrt(n)

    while d <= r:
        while n % d == 0:
            if d not in factors.keys():
                factors[d] = 0
            factors[d] += 1
            n = n // d
            r = isqrt(n)    # n got smaller, so its bound does too
        d += 1

    if n > 1:
        factors[n] = 1

    return factors


def totient(n: int) -> int:
    """
    returns totient value of n
    """
    factorization = factorize(n)
    # n * (1 - 1/p_1) * ... * (1 - 1/p_k) proved in class
    # substitute n = p_1^(e_1) * ... * p_k^(e_k)
    # = p_1^(e_1 - 1)(p_1 - 1) * ... * p_k^(e_k - 1)(p_k - 1)
    product = 1
    for prime, exp in factorization.items():
        product *= (prime ** (exp-1)) * (prime-1)
    return product


# Pass factorize(p - 1) as factorization to avoid factoring it again.
def is_gen(g: int, p: int, factorization: dict[int, int] | None = None) -> bool:
    """
    returns true iff g is a generator mod p
    """
    if pow(g, p - 1, p) != 1:
        return False
    if factorization is None:
        factorization = factorize(p - 1)
    for q in factorization.keys():
        if pow(g, (p - 1) // q, p) == 1:
            return False
    return True


def find_gen(p: int) -> int | None:
    """TODO"""
    if p < 2:
        return None

    factorization = factorize(p - 1)
    for i in range(1, p):
        if is_gen(i, p, factorization):
            return i

    return None


# Building the whole list takes about p steps, too slow to ever run for a
# big p. OPEN: an iterator (yield) would let us loop through the primitive
# roots and stop at one we like.
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
        if gcd(i, p-1) == 1:
            coprimes.append(i)

    # this produces the rest of the primitive roots
    return [pow(gen, i, p) for i in coprimes]


# Sieve of Eratosthenes. Seconds (laptop): n = 10^4 0.0008, 10^5 0.007,
# 10^6 0.055.
def primes_under(n: int) -> list[int]:
    """
    returns all primes less than or equal to n
    """
    max = isqrt(n)
    primes = []
    sieve = [False] * 2 + [True] * (n - 1)
    for i in range(2, max + 1):
        if sieve[i]:
            for j in range(i, n // i + 1):
                sieve[j * i] = False
            primes.append(i)

    for i in range(max + 1, n + 1):
        if sieve[i]:
            primes.append(i)

    return primes


# Built every time cryspy is imported (under 0.001 s).
# OPEN: how many small primes to keep.
SMALL_PRIMES: list[int] = primes_under(10000)


# Small primes first, then prove n prime by finding a generator.
# If the Fermat test fails for any g, n is not prime.
# OPEN: factorize(n - 1) runs before the first Fermat test. For a composite
# n with no small factor, one Fermat test would say "not prime" at once,
# but we first spend as long as factoring n - 1 takes (an 83-bit example
# ran over 2 minutes). Testing first, then factoring, would fix this.
def is_prime(n: int) -> bool:
    """
    returns true iff n is prime
    """
    if n < 2:
        return False
    # check small prime factors
    if n in SMALL_PRIMES:
        return True
    for p in SMALL_PRIMES:
        if n % p == 0:
            return False

    # assume this is prime
    factorization = factorize(n - 1)
    for g in range(2, n):
        if pow(g, n - 1, n) != 1:
            return False
        if is_gen(g, n, factorization):
            return True
    return False


def next_prime(n: int) -> int:
    """
    Returns the next prime larger than n
    """
    i = n+1
    while not is_prime(i):
        i += 1
    return i
