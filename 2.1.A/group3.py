# 2.1.A Group 3
import cryspy as cp
import math


def gcd(*nums):
    if len(nums) == 0:
        return 0
    elif len(nums) == 1:
        return abs(nums[0])
    elif len(nums) == 2:
        a,b = nums
        if b == 0: 
            return a

        return abs(gcd(b, a % b))

    else:
        return abs(gcd(gcd(nums[0], nums[1]), *nums[2:]))


def lcm(*ints):
    if len(ints) == 0:
        return 1
    if len(ints) == 1:
        return abs(ints[0])
    if len(ints) == 2:
        return abs(int(ints[0]*ints[1]/cp.gcd(ints[0], ints[1])))

    else:
        return abs(lcm(lcm(ints[0],ints[1]), *ints[2:]))


def crt(*kwargs) -> tuple[int, int]:
    """Does crt on input
    
    Args:
        *kwargs: a bunch of tuples (x_i, m_i)
    
    Returns:
        a tuple (x, m) that satisfies given conditions
    """
    if len(kwargs) >= 2:
        x1 = kwargs[0][0]
        m1 = kwargs[0][1]
        x2 = kwargs[1][0]
        m2 = kwargs[1][1]

        inv = cp.mult_inverse(m1, m2)
        j = ((x2-x1) * inv) % m2
        x = (m1 * j + x1) % (m1*m2)

        k = ((x, m1*m2), *kwargs[2:])
        if len(k) == 1:
            return k[0]
        return crt(*k)


def dlog_slow(g: int, h: int, p: int) -> int:
    """returns log_g(h) mod p"""
    product = 1
    for i in range(p):
        product *= g
        product %= p
        if product == h:
            return i


def dlog_slowest(g: int, h: int, p: int) -> int:
    """returns log_g(h) mod p"""
    for i in range(p):
        if pow(g, i, p) == h:
            return i


def dlog_think(g: int,h: int,p: int) -> int:
    """returns log_g(h) mod p
    uses window alg (Babystep-Giantstep)"""
    window_size = math.floor(math.sqrt(p))
    window = {}
    prod = 1
    for i in range(window_size):
        window[prod] = i
        prod = (prod*g)%p

    cur = h
    step = pow(g,window_size,p)
    for j in range(math.ceil(p/window_size)):
        if cur in window:
            index = window[cur]
            return (index - window_size * j )%(p-1)
        cur = (cur*step)%p
