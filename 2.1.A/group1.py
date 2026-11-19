# 2.1.A Group 1
import cryspy as cp


def dlog_slowest(g, h, p):
    for i in range(p):
        if pow(g, i, p) == h:
            return i

# solves x_i ** a = y_i
def dlog(xs, ys, p):
    x = xs[0]
    y = ys[0]

    d = nt.isqrt(p)
    x_hat = pow(x, d, p)
    # x^e1 * x_hat ^ e2 \equiv y mod p
    # x^(e1 + d * e2) \equiv y mod p

    seen = {}
    for e2 in range(d+1):
        seen[(y * nt.mult_inverse(pow(x_hat, e2, p), p))%p] = e2

    for e1 in range(d+1):
        j = pow(x, e1, p)
        if j in seen:
            k = e1 + seen[j] * d
            if (_check_dlog(xs, ys, k, p)):
                return k
