# 2.1.A Group 3
import cryspy as cp


def dlog_slow(g: int, h: int, p: int) -> int:
    """calculating log_g (h) mod p"""
    product = 1
    for i in range(p):
        product *= g
        product %= p
        if product == h:
            return i

def dlog_slowest(g: int, h: int, p: int) -> int:
    """calculating log_g (h) mod p"""
    for i in range(p):
        if pow(g, i, p) == h:
            return i