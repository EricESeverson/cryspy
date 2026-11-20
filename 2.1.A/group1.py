# 2.1.A Group 1
import cryspy as cp
import cryspy.number_theory as nt


def _check_dlog(xs, ys, k, p):
    for (x, y) in zip(xs, ys):
        if pow(x, k, p) != y:
            return False
    return True


def dlog_slowest(g, h, p):
    for i in range(p):
        if pow(g, i, p) == h:
            return i

def dlog(x, y, p):
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


def _gcd(a, b):
    if b == 0: return a
    return gcd(b, a % b)

def _lcm(a, b):
    return (a * b) // _gcd(a, b)

def gcd(*args):
    """Returns the gcd of all arguments.

    Args:
        *args: integers to take gcd of

    Returns:
        An integer which is the gcd of all args.
    """

    if len(args) == 0:
        return 0

    g = args[0]

    for a in args[1:]:
        g = _gcd(g, a)
    
    return g


def lcm(*args):
    """Returns the lcm of all arguments.

    Args:
        *args: integers to take lcm of

    Returns:
        An integer which is the lcm of all args.
    """

    if len(args) == 0:
        return 1

    l = args[0]

    for a in args[1:]:
        l = _lcm(l, a)
    
    return l


def crt(*args):
    """TODO"""
    
    if len(args) == 0:
        raise

    a, n = args[0][0], args[0][1]

    for (a0, n0) in args[1:]:
        g = gcd(n, n0)
        if (a0%g) != 1:
            return None
            
        a0 //= g
        n0 //= g

        j = ((a0 - a) * nt.mult_inverse(n, n0))%(n0)

        a = (a + n * j)
        n = n * n0

    return a, n

def poh_hell_dlog(g: int, h: int, p: int) -> int: # returning x where g ^ x =h mod p
   """Discrete log mod p, using the Pohlig-Hellman algorithm
  
   Args:
       g: log base
       h: log value
       p: prime modulus
  
   Returns:
       int x where g ^ x = h mod p, or log_g(h) mod p
   """
  
   factorization = nt.factorize(p-1)
   cris = []


   for prime, exp in factorization.items():
       order = pow(prime, exp, p) # prime ^ exp
       new_mod = (p-1) // order # p-1 / order
  
       a = pow(h, new_mod, p) # h ^ (p-1 / order)
       b = pow(g, new_mod, p) # q ^ (p-1 / order)


       # manual dlog in Z_order subgroup
       # finding b ^ x = a
       for i in range(1, order):
           if pow(b, i, p) == a:
               cris.append((i, order))
  
   return crt(*cris)



