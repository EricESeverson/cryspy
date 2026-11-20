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


def crt(*args) -> tuple[int, int]:
    """Does crt on input. Works with non-coprime mods
    
    Args:
        *args: a bunch of tuples (x_i, m_i)
    
    Returns:
        a tuple (x, m) that satisfies given conditions
        None if no solution
    """
    for i, (x, m) in enumerate(args):
        for j in range(i+1, len(args)):
            g = cp.gcd(m, args[j][1])
            if g != 1:
                args = (*args[:i], (x, m/g), *args[i+1:])

    return crt_relatively_prime(*args)


def crt_relatively_prime(*args) -> tuple[int, int]:
    """Does crt on input. Only works if mods are relatively prime
    
    Args:
        *args: a bunch of tuples (x_i, m_i)
    
    Returns:
        a tuple (x, m) that satisfies given conditions
        None if no solution
    """
    if len(args) >= 2:
        x1 = args[0][0]
        m1 = args[0][1]
        x2 = args[1][0]
        m2 = args[1][1]

        inv = cp.mult_inverse(m1, m2)
        j = ((x2-x1) * inv) % m2
        x = (m1 * j + x1) % (m1*m2)

        k = ((x, m1*m2), *args[2:])
        if len(k) == 1:
            return k[0]
        return crt_relatively_prime(*k)
    if len(args) == 1:
        return args[0]
    return None


def dlog_slow(g: int, h: int, p: int) -> int:
    """returns log_g(h) mod p"""
    product = 1
    for i in range(p):
        if product == h:
            return i
        product *= g
        product %= p


def dlog_slowest(g: int, h: int, p: int) -> int:
    """returns log_g(h) mod p"""
    for i in range(p):
        if pow(g, i, p) == h:
            return i


def dlog_window(g: int,h: int,p: int) -> int:
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
