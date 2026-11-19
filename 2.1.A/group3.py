# 2.1.A Group 3
import cryspy as cp
import math

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
    """returns log_g(h) mod p"""
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
