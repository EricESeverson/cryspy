# 2.1.A Group 1
import cryspy as cp


def dlog_slowest(g, h, p):
    for i in range(p):
        if pow(g, i, p) == h:
            return i
