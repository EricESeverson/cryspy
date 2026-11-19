# 2.1.A Group 2
import cryspy as cp


def dlog_slow(g,h,p):
    x = 0
    for i in range(p):
        if pow(g,i,p)==h:
            return i
