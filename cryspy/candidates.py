"""Every gcd, inverse and affine cipher written for 1.2.A, none chosen yet.

Copied from the two team.py files and from your own 1.2.A notebooks. Names
got a number so they don't clash; otherwise the code is as you wrote it,
including the bugs (marked BUG). The class decides what stays, under which
name and with which argument order. Until then, time them against each other.
"""

from .ciphers import Cipher


# ---------------------------------------------------------------- gcd

# Team Bob team.py
def gcd_1(a: int, b: int) -> int:
    """Simple Euclidean alg

    Args:
        a: first val
        b: second val

    Returns:
        The gcd of a, b.
    """

    if a < b:
        a, b = b, a

    if (a%b == 0):
        return b

    return gcd_1(b, a%b)


# Team Alice notebooks, and a Team Bob notebook
def gcd_2(a, b):
    if (b==0):
        return a
    return gcd_2(b, a%b)


# Team Alice notebooks
def gcd_3(A, B):
    a = max(A, B)
    b = min(A, B)
    if (a==0 or b==0):
        return max(a, b)
    r = a%b
    return gcd_3(b, r)


# ------------------------------------------- extended Euclid and inverses
# Watch the argument order: some take (n, mod), some take (mod, n).

# 1. Team Alice team.py: recursive, inverse of b mod a
def euclidean_recurse_1(a: int, b: int):
    # inverse of b mod a
    # returns values x, y such that ax + by = 1
    if (b == 1):
        return (0, 1)
    # a - qb = r
    q, r = divmod(a, b)

    qp, rp = euclidean_recurse_1(b, r)
    # gives qp * b + rp * r = 1

    # want qp * b + rp * (a - qb) = 1
    # rp * a + (qp - rp * q) * b = 1
    return rp, qp - rp * q


def euclidean_inverse_1(a: int, b: int):
    '''
    computes the inverse of b mod a
    '''
    return euclidean_recurse_1(a, b)[1] % a


# 2. Team Bob team.py: recursive
# BUG: the gcd it reports is wrong when r == 1 (egcd_2(30, 7) says 2).
def egcd_2(a: int, b: int) -> tuple[int]:
    """Extended Euclidean Algorithm

    Args:
        a, b: two ints

    Returns:
        a tuple (g, x, y) with
        g: gcd(a, b)
        x, y: where a*x + b*y = 1
    """
    if b == 1:
        return 1, 1, a
    q, r = divmod(a, b)
    if r == 1:
        return b, 1, -q
    g, x, y = egcd_2(b, r)
    return (g, y, x-y*q)


def multiplicative_inverse_2(n: int, mod: int) -> int:
    """Multiplicative inverse by extended Euclidean Algorithm

    Args:
        n: integer to get inverse of
        mod: modulo

    Returns:
        The multiplicative inverse of n modulo mod.
    """

    return egcd_2(mod, n)[2]


# 3. Team Bob notebooks: a loop instead of recursion
def egcd_3(a,b):
    x0, y0 = 1,0 #a = A*1 + B*0
    x1,y1 = 0,1 #sim

    while b != 0:
        q, r = divmod(a, b)

        a = b
        b = r


        x0,x1 = x1, x0-q*x1
        y0,y1 = y1, y0-q*y1

    return a, x0, y0


def inv_3(key , m):
    gcd,inv, _ = egcd_3(key,m)

    return inv%m


# 4. Team Bob notebooks: recursive, either argument may be bigger,
# checks the gcd first
def _ea_4(a, b):
    flipped = False
    if a < b:
        flipped = True
        a, b = b, a

    if (b == 1):
        return (1, 0) if flipped else (0, 1)

    if (b == 0):
        raise Exception("divide by zero sus")

    q, r = divmod(a, b)

    n, m = _ea_4(b, r)

    if flipped:
        return n - q * m, m
    return m, n - q * m


def multi_inverse_4(n, mod):
    if (gcd_1(n, mod)) != 1:
        raise Exception("divide by zero sus")
    return _ea_4(n, mod)[0]%mod


# 5. Team Bob notebook: a two-row table, everything reduced mod as it goes
def inverse_5(n, mod):
    dp = [
        [0, mod, 1, n],
        [0, 0, 0, 0],
    ]
    i = 0
    while True:
        q = dp[i][1] // dp[i][3]
        dp[1-i][0] = dp[i][2] % mod
        dp[1-i][1] = dp[i][3]

        dp[1-i][2] = (dp[i][0] - q * dp[i][2]) % mod
        dp[1-i][3] = (dp[i][1] - q * dp[i][3])

        if (dp[1-i][3] == 0):
            break

        i = 1-i

    return dp[1-i][0]


# 6. Team Alice notebook: a loop, clear error when there is no inverse
def better_inverse_6(n:int, m:int) -> int:
    '''
    computes the inverse of n mod m
    '''
    a = 0
    b = m
    c = 1
    d = n
    while d != 0:
        if d == 1:
            return c
        prev_a = a
        prev_b = b
        a = c
        b = d
        c, d = divmod(prev_b, b)
        c = prev_a - c * a
    raise ValueError("n does not have an inverse mod m")


# 7. Team Alice notebook: list the quotients, then fold them back up
# BUG: right only up to sign (5 mod 8 gives 3, and 5 * 3 = -1 mod 8).
def euclidean_algorithm_7(a, b):
  qs = []
  if b > a:
    t = a
    a = b
    b = t
  r = 1
  while r != 0:
    q, r = divmod(a, b)
    qs.append(q)
    a = b
    b = r
  return qs


def test_7(qs):
  a = 0
  b = 1
  while qs:
    t = b
    b = qs[-1] * b + a
    a = t
    qs = qs[:-1]
  return b


def find_inverse_7(a, b):
  qs = euclidean_algorithm_7(a, b)[:-1]
  return test_7(qs)


# 8. Team Bob notebook: try every number
def bash_multi_inverse_8(n, mod):
    for i in range(mod):
        if (n*i)%mod == 1:
            return i
    raise Exception("sus")


# ------------------------------------------------- multiplication ciphers

# Team Alice team.py: key given when the cipher is made
class MultiplicationCipher1(Cipher):
    def __init__(self, mod: int, key: int) -> None:
        self.mod = mod
        self.key = key
        self.inv = euclidean_inverse_1(self.mod, self.key)

    def encrypt(self, num: int, key: int) -> int:
        return (num*key) % self.mod

    def decrypt(self, num: int, key: int) -> int:
        if (key == 0):
            raise Exception("ur special key can't be 0")
        if (key != self.key):
            self.key = key
            self.inv = euclidean_inverse_1(self.mod, self.key)

        return (self.inv * num) % self.mod


# Team Bob notebook: remembers every inverse it has computed
class MultiplicationCipher2(Cipher):
    def __init__(self, mod: int) -> None:
        self.mod = mod
        self.inverses = {}


    def _inverse(self, key):
        if key not in self.inverses:
            self.inverses[key] = inv_3(key,self.mod)

        return self.inverses[key]

    def encrypt(self, num: int, key: int) -> int:
        return (num * key) % self.mod

    def decrypt(self, num: int, key: int) -> int:
        return (num*self._inverse(key)) % self.mod


# Team Alice notebook: tries every number on each decrypt
class MultiplicationCipher3(Cipher):
    def __init__(self, mod: int) -> None:
        self.mod = mod

    def encrypt(self, num: int, key: int) -> int:
        if(gcd_2(key, self.mod)!= 1):
            raise Exception("ur special key must be relatively prime")
        return (num*key) % self.mod

    def decrypt(self, num: int, key: int) -> int:
        #naive method
        #finding inverse of key
        if(gcd_2(key, self.mod)!= 1):
            raise Exception("ur special key must be relatively prime")
        for i in range(self.mod):
            if ((key*i)%self.mod == 1):
              return (i*num)% self.mod


# --------------------------------------------------------- affine ciphers

# Team Bob team.py: key is (a, b), remembers every inverse it has computed.
# BUG in team.py: _inverse passed 3 arguments to multiplicative_inverse.
# This is the fix from a Team Bob notebook. Another Team Bob notebook has the
# same class with inv_3 in place of egcd_2.
class AffineCipher1(Cipher):
    def __init__(self, mod: int) -> None:
        self.mod = mod
        self.inverses = {}

    def _inverse(self, key_a):
        """Returns inverse. If not already calculated, calculates it.

        Args:
            key_a: the multiplicative number in the key tuple

        Returns:
            The multiplicative inberse of `key_a` mod `self.mod`
        """
        if key_a not in self.inverses:
            self.inverses[key_a] = egcd_2(self.mod, key_a)[2]

        return self.inverses[key_a]

    def encrypt(self, num: int, key: tuple[int,int]) -> int:
        """Returns the num encrypted using the key

        Args:
            num: the integer to encrypt
            key: a tuple (a, b)

        Returns:
            encrypted num with affine cipher applied
        """
        a,b = key
        return (a * num + b) % self.mod

    def decrypt(self, num: int, key: tuple[int,int]) -> int:
        """Returns the decrypted num using the key

        Args:
            num: integer to decrypt
            key: a tuple (a, b)

        Returns:
            decrypted num using affine cipher
        """
        a,b = key
        return ((num-b)*self._inverse(a)) % self.mod


# Team Bob notebook: the key is loaded once; encrypt and decrypt ignore
# the key they are passed
class AffineCipher2(Cipher):
    def __init__(self, mod: int) -> None:
        self.mod = mod

    def load_key(self, key_a, key_b) -> None:
        self.key_a = key_a
        self.key_b = key_b
        self.inverse_key_a = multi_inverse_4(key_a, self.mod)

    def encrypt(self, num: int, fake_key) -> int:
        return (num * self.key_a + self.key_b) % self.mod

    def decrypt(self, num: int, fake_key) -> int:
        return ((num - self.key_b) * self.inverse_key_a) % self.mod


# Team Alice notebooks: key given when the cipher is made, updated when a
# different key is passed
class AffineCipher3(Cipher):
    def __init__(self, mod: int, key_m: int, key_a: int) -> None:
        self.mod = mod
        self.key_m = key_m
        self.inv = euclidean_inverse_1(self.mod, self.key_m)
        self.key_a = key_a

    def update_keys(self, key_m: int, key_a: int):
        if (key_m != self.key_m):
            self.key_m = key_m
            self.inv = euclidean_inverse_1(self.mod, self.key_m)
        if (key_a != self.key_a):
            self.key_a = key_a

    def encrypt(self, num: int, keys) -> int:
        if (keys[0] == 0):
            raise Exception("ur special multiplication key can't be 0")
        self.update_keys(keys[0], keys[1])

        return (num*keys[0] + keys[1]) % self.mod

    def decrypt(self, num: int, keys) -> int:
        if (keys[0] == 0):
            raise Exception("ur special multiplication key can't be 0")
        self.update_keys(keys[0], keys[1])

        return (self.inv * (num - keys[1])) % self.mod


# Team Alice notebook: computes the inverse again on every decrypt
class AffineCipher4(Cipher):
   def __init__(self, mod: int) -> None:
       self.mod = mod


   def encrypt(self, num: int, key: tuple[int, int]) -> int:
       return (num * key[0] + key[1]) % self.mod


   def decrypt(self, num: int, key: tuple[int, int]) -> int:
       if (gcd_2(self.mod, key[0]) != 1):
          raise Exception("not relatively prime")

       num -= key[1]
       i = euclidean_inverse_1(self.mod, key[0])
       return (num * i) % self.mod


# Team Alice notebook: the inverse is handed in when the cipher is made
class AffineCipher5(Cipher):
    def __init__(self, mod: int, inv: int) -> None:
        self.mod = mod
        self.inverse = inv

    def encrypt(self, num: int, key: tuple[int, int]) -> int:
        return (num * key[0] + key[1]) % self.mod

    def decrypt(self, num: int, key: tuple[int, int]) -> int:
        if key==0:
           raise Exception("Key can't be 0")
        num -= key[1]
        return (num * self.inverse) % self.mod
