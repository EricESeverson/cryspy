# 2.1.A Group 2
import cryspy as cp
import cryspy.number_theory as nt

def dlog_slow(g,h,p):
    x = 0
    for i in range(p):
        if pow(g,i,p)==h:
            return i

def dlog(g, x, n):
    '''
    finds a such that g^a = x mod n
    '''
    sqrt = nt.isqrt(n) + 1
    # we can write a as sqrt * i + j where i and j are both <= than sqrt
    # then compare g^(sqrt * i) to x * g^(-j)

    # generate dict of x * g^(-j)
    ginv = nt.mult_inverse(g, n)
    xginv = {x * pow(ginv, j, n) % n:j for j in range(sqrt+1)}

    cur_x = 1
    step = pow(g, sqrt, n)
    for i in range(sqrt + 1):
        if cur_x in xginv:
            return i * sqrt + xginv[cur_x]
        cur_x = (cur_x * step) % n
