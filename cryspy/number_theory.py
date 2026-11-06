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
