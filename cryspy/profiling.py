"""Unit tests and timing for 1.3.A.

From the Nov 9 board, plus isqrt:

    is_prime(n: int) -> bool
    next_prime(n: int) -> int
    is_gen(g: int, p: int) -> bool      # g^1, ..., g^(p-1) = {1, ..., p-1}
    isqrt(n: int) -> int                # the largest r with r * r <= n

Each test takes your function, or several functions to compare:

    from cryspy.profiling import *    # test_is_prime, ..., compare_functions
    test_is_prime(is_prime)
    test_is_gen(slow_is_gen, is_gen)
    test_isqrt(isqrt)

and does three things:
  1. says what the examples are,
  2. runs each function on them and checks every answer,
  3. times the functions side by side on bigger and bigger inputs.

A call that takes longer than time_limit seconds (default 1) is stopped, and
that function skips the rest of that list, since the later inputs are bigger.

Head to head: put two (or more) functions in one call.

    test_is_prime(group1.is_prime, group2.is_prime)

The timing table then has one column per function. Functions with the same
name are labeled by module (group1.is_prime, group2.is_prime). To choose the
column names yourself, pass a dict:

    test_is_prime({"Group 1": group1.is_prime, "Group 2": group2.is_prime})

A list works too: test_is_prime([f, g, h]). Give a slow function more time
with time_limit=5.

compare_functions(fs, inputs) does step 3 for any functions you like:

    compare_functions([group1.totient, group2.totient], [10**k for k in range(2, 20)])
"""

import signal
import time

# ================================================================ test data
# Expected answers are typed in as plain numbers, not computed.

PRIMES_BELOW_200 = [
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67,
    71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149,
    151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199,
]

SMALL_COMPOSITES = [341, 561, 1105, 1729, 2047, 2465, 2821, 6601, 7921, 8911,
                    10403, 65535]

SMALL_PRIMES = [7919, 65537, 999983, 1000003]

# (n, is n prime?), smallest first
BIGGER_MIXED = [
    (168003672409, False),
    (16800367240931, True),
    (742403294138881, False),
    (15021804274836409, False),
    (11459588966629853689, False),
    (15241578790931261393, False),
    (141776957697278073396409, False),
    (92657661366880910921629609, False),
    (271017128857254504705902822401, False),
    (27101712885725450470590282240137, True),
    (93779122071803839968096384251761, False),
    (496757958275272577729908884399939997312496935424849671193310676199353,
     True),
    (49675795827527257772990888439993999731249693542484967119331067619934769,
     False),
]

# not prime, smallest first
BIGGER_COMPOSITES = [
    10097063, 1000730021, 100003300009, 10000049000057, 1000001970000133,
    100000007700000049, 10000000089000000133, 1000000001930000000057,
    100000000006900000000117, 10000000000427000000001443,
    1000000000004010000000001147,
]

BIGGER_PRIMES = [
    1000000007, 8211739271, 3506498416453947794933,
    49182124578376174015858333011122132081897957,
    10**99 + 289,
]

# (n, label), all not prime
VERY_BIG_COMPOSITES = [(2**1100, "2^1100"), (3**700, "3^700"), (10**400, "10^400")]

# (n, next_prime(n)) where n is not prime, so "> n" and ">= n" agree
SMALL_NEXT_PRIME = [
    (0, 2), (1, 2), (8, 11), (14, 17), (24, 29), (90, 97), (114, 127),
    (200, 211), (1000, 1009), (7920, 7927), (32768, 32771), (65536, 65537),
]

# next_prime(10^d) = 10^d + k, as (d, k)
POWERS_OF_TEN_NEXT_PRIME = [
    (4, 7), (5, 3), (6, 3), (7, 19), (8, 7), (9, 7), (10, 19), (11, 3),
    (12, 39), (13, 37), (99, 289),
]

# every generator g in 1..p-1, for each prime p < 32
GENERATORS = {
    2: [1], 3: [2], 5: [2, 3], 7: [3, 5], 11: [2, 6, 7, 8], 13: [2, 6, 7, 11],
    17: [3, 5, 6, 7, 10, 11, 12, 14], 19: [2, 3, 10, 13, 14, 15],
    23: [5, 7, 10, 11, 14, 15, 17, 19, 20, 21],
    29: [2, 3, 8, 10, 11, 14, 15, 18, 19, 21, 26, 27],
    31: [3, 11, 12, 13, 17, 21, 22, 24],
}

# (g, p, answer) with p not prime
IS_GEN_NOT_PRIME = [(2, 4, False), (3, 4, False), (2, 9, False),
                    (5, 6, False), (3, 10, False), (7, 15, False)]

# (g, p, answer) with bigger primes p, smallest first
IS_GEN_BIGGER = (
    [(2, 19, True), (7, 10831, True)]
    + [(g, 10831, False) for g in range(2, 7)]
    + [(7, 8211739271, True)]
    + [(g, 8211739271, False) for g in range(2, 7)]
    + [(3, 3506498416453947794933, True), (2, 3506498416453947794933, False),
       (2, 49182124578376174015858333011122132081897957, True)]
)

# (n, isqrt(n))
ISQRT_NEAR_SQUARES = [
    (99, 9), (100, 10), (9999, 99), (10000, 100),
    (4503599761588224, 67108864), (4503599761588225, 67108865),
    (10**16 - 1, 99999999), (10**16, 100000000),
    (10**18 - 1, 999999999), (2**64 - 1, 4294967295),
]
# n = p * p for big primes p, so isqrt(n) = p
ISQRT_PRIME_SQUARES = [9007199254740997, 18446744073709551629]

ISQRT_HUGE = [
    (4**1100 - 1, 2**1100 - 1), (4**1100, 2**1100),
    (10**400 - 1, 10**200 - 1), (10**400, 10**200),
]

# isqrt(4^k - 1) = 2^k - 1, timed for k = 16, 32, ..., 65536
ISQRT_TIMING_BITS = [2**j for j in range(4, 17)]

# (bits k, smallest prime p >= 2^k, smallest generator g mod p)
TIMING_PRIMES = [
    (10, 1031, 14), (12, 4099, 2), (14, 16411, 3), (16, 65537, 3),
    (18, 262147, 2), (20, 1048583, 5), (22, 4194319, 3), (24, 16777259, 2),
    (26, 67108879, 3), (28, 268435459, 2), (30, 1073741827, 2),
    (32, 4294967311, 3), (34, 17179869209, 3), (36, 68719476767, 5),
    (38, 274877906951, 7), (40, 1099511627791, 3), (42, 4398046511119, 7),
    (44, 17592186044423, 5), (46, 70368744177679, 3),
    (48, 281474976710677, 6), (50, 1125899906842679, 11),
    (52, 4503599627370517, 2), (54, 18014398509482143, 3),
    (56, 72057594037928017, 10), (58, 288230376151711813, 5),
    (60, 1152921504606847009, 13), (62, 4611686018427388039, 3),
    (64, 18446744073709551629, 2),
]

# ================================================================ naming


class _Named:
    """A function with a display name, so group1.is_prime and group2.is_prime
    get different columns."""

    def __init__(self, f, name):
        self.f, self.__name__ = f, name

    def __call__(self, *args):
        return self.f(*args)


def _named(fs):
    """Accept f, g, ... or a list [f, g] or a dict {"label": f}. Repeated
    names get their module in front: group1.is_prime, group2.is_prime."""
    flat = []
    for f in fs:
        if isinstance(f, dict):
            flat += list(f.items())
        elif isinstance(f, (list, tuple)):
            flat += [(None, g) for g in f]
        else:
            flat.append((None, f))
    names = [k or getattr(g, "__name__", repr(g)) for k, g in flat]
    out = []
    for i, ((k, g), n) in enumerate(zip(flat, names)):
        if k is None and names.count(n) > 1:
            n = f"{getattr(g, '__module__', None) or '?'}.{n}"
        if [m for m in out if m.__name__ == n]:
            n = f"{n} #{i + 1}"
        out.append(_Named(g, n))
    return out


# ================================================================ timing


class TooSlow(Exception):
    pass


def _alarm(signum, frame):
    raise TooSlow


def run(f, args, time_limit=1.0):
    """Call f(*args), stopping it after time_limit seconds.

    Returns (status, answer, seconds), where status is "ok", "slow" or "error".
    (Stopping works on Mac, Linux and Colab. On Windows a slow call runs to
    the end and is then marked "slow".)
    """
    try:
        old = signal.signal(signal.SIGALRM, _alarm)
        signal.setitimer(signal.ITIMER_REAL, time_limit)
        alarm = True
    except (AttributeError, ValueError):
        alarm = False
    start = time.perf_counter()
    try:
        answer, status = f(*args), "ok"
    except TooSlow:
        answer, status = None, "slow"
    except Exception as e:
        answer, status = f"raised {type(e).__name__}", "error"
    finally:
        if alarm:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, old)
    seconds = time.perf_counter() - start
    if status == "ok" and seconds > time_limit:
        status = "slow"
    return status, answer, seconds


def short(x):
    """Long numbers print as 49675795...19934769 (71 digits)."""
    if isinstance(x, int) and x.bit_length() > 10000:
        return f"(a {x.bit_length()}-bit number)"
    s = str(x)
    return s if len(s) <= 26 else f"{s[:8]}...{s[-8:]} ({len(s)} digits)"


def compare_functions(fs, inputs, time_limit=1.0, labels=None, expected=None):
    """Time several functions side by side, one row per input.

    Args:
        fs: a function, or a list of functions
        inputs: a list of arguments, getting harder. Use tuples for functions
            of several arguments: [(2, 5), (3, 7), ...]
        time_limit: a function that takes longer than this many seconds on
            one input is stopped and skips the rest of the inputs
        labels: optional names for the inputs, printed instead of the inputs
        expected: optional list of correct answers. A wrong answer also
            stops that function.

    Returns:
        for each function, how many inputs it finished
    """
    fs = _named(fs if isinstance(fs, (list, tuple)) else [fs])
    inputs = [x if isinstance(x, tuple) else (x,) for x in inputs]
    labels = labels or [", ".join(short(a) for a in args) for args in inputs]
    names = [f.__name__ for f in fs]
    w = max(10, *map(len, names))
    lw = max(5, *map(len, labels))
    print(f"  {'input':<{lw}}" + "".join(f"  {n:>{w}}" for n in names)
          + "  answer")

    running = set(range(len(fs)))
    finished = [0] * len(fs)
    for row, (args, label) in enumerate(zip(inputs, labels)):
        if not running:
            break
        cells, answers, notes = [], [], []
        for j, f in enumerate(fs):
            if j not in running:
                cells.append("")
                continue
            status, got, seconds = run(f, args, time_limit)
            if status == "ok" and (expected is None or got == expected[row]):
                cells.append(f"{seconds:.6f}")
                answers.append(got)
                finished[j] += 1
                continue
            running.discard(j)
            if status == "slow":
                cells.append(f"over {time_limit:g} s")
            elif status == "error":
                cells.append("error")
                notes.append(f"{names[j]} {got}")
            else:
                cells.append("wrong")
                notes.append(f"{names[j]} returned {short(got)}")
        if expected is not None:
            answer = short(expected[row])
        elif len({repr(a) for a in answers}) > 1:
            answer = "disagree: " + " / ".join(short(a) for a in answers)
        else:
            answer = short(answers[0]) if answers else ""
        print(f"  {label:<{lw}}" + "".join(f"  {c:>{w}}" for c in cells)
              + f"  {answer}")
        for note in notes:
            print(f"      ({note})")
    if running:
        print("  (finished every input)")
    return finished


# ================================================================ checking


class Score:
    def __init__(self):
        self.right = self.wrong = self.skipped = 0

    def __str__(self):
        s = f"{self.right} right, {self.wrong} wrong"
        return s + (f", {self.skipped} skipped as too slow" if self.skipped
                    else "")


def check(f, cases, score, time_limit=1.0, only_mistakes=False):
    """cases: list of (args, expected) or (args, expected, label), smallest
    first. Prints one line per case. After a call slower than time_limit,
    skips the rest of the list."""
    for i, (args, expected, *label) in enumerate(cases):
        status, got, seconds = run(f, args, time_limit)
        shown_args = label[0] if label else ", ".join(short(a) for a in args)
        call = f"{f.__name__}({shown_args})"
        if status == "slow":
            rest = len(cases) - i - 1
            print(f"  {call}: over {time_limit:g} s, so skipping this"
                  + (f" and the {rest} bigger ones" if rest else ""))
            score.skipped += rest + 1
            return
        if status == "ok" and got == expected:
            score.right += 1
            if not only_mistakes:
                print(f"  {call} = {short(got)}  ✓   {seconds:.6f} s")
        else:
            score.wrong += 1
            shown = short(got) if status == "ok" else got
            print(f"  {call} = {shown}  ✗ expected {short(expected)}")


def _header(test, f):
    print(f"\n======== {test}: {f.__name__} ========")


def _summary(test, fs, scores, finished, bits):
    print(f"\n{test} summary (largest timing input finished, in bits):")
    for f, score, k in zip(fs, scores, finished):
        top = bits[k - 1] if k else 0
        print(f"  {f.__name__}: {score}; timing reached {top} bits")
    return {f.__name__: dict(right=s.right, wrong=s.wrong, skipped=s.skipped,
                             bits=bits[k - 1] if k else 0)
            for f, s, k in zip(fs, scores, finished)}


# ================================================================ the tests


def test_is_prime(*fs, time_limit=1.0):
    """Examples, checks and timing for is_prime(n) -> bool."""
    fs = _named(fs)
    scores = []
    for f in fs:
        _header("test_is_prime", f)
        s = Score()
        print("\nExamples 1: every n from 0 to 199 (only mistakes are shown)")
        check(f, [((n,), n in PRIMES_BELOW_200) for n in range(200)], s,
              time_limit, only_mistakes=True)
        print(f"  {s.right}/200 right")
        print("\nExamples 2: small numbers that are not prime")
        check(f, [((n,), False) for n in SMALL_COMPOSITES], s, time_limit)
        print("\nExamples 3: small primes")
        check(f, [((n,), True) for n in SMALL_PRIMES], s, time_limit)
        print("\nExamples 4: bigger numbers, some prime and some not")
        check(f, [((n,), a) for n, a in BIGGER_MIXED], s, time_limit)
        print("\nExamples 5: bigger numbers that are not prime")
        check(f, [((n,), False) for n in BIGGER_COMPOSITES], s, time_limit)
        print("\nExamples 6: bigger primes")
        check(f, [((n,), True) for n in BIGGER_PRIMES], s, time_limit)
        print("\nExamples 7: very big numbers that are not prime")
        check(f, [((n,), False, lab) for n, lab in VERY_BIG_COMPOSITES], s,
              time_limit)
        scores.append(s)

    print("\n======== Timing: n is the smallest prime with k bits ========")
    finished = compare_functions(
        list(fs), [p for k, p, g in TIMING_PRIMES], time_limit,
        labels=[f"{k} bits: {p}" for k, p, g in TIMING_PRIMES],
        expected=[True] * len(TIMING_PRIMES))
    return _summary("test_is_prime", fs, scores, finished,
                    [k for k, p, g in TIMING_PRIMES])


def test_next_prime(*fs, time_limit=1.0):
    """Examples, checks and timing for next_prime(n) -> int."""
    fs = _named(fs)
    scores = []
    for f in fs:
        _header("test_next_prime", f)
        s = Score()
        print("\nExamples 1: small n that are not prime")
        check(f, [((n,), p) for n, p in SMALL_NEXT_PRIME], s, time_limit)
        print("\nExamples 2: n = 10^d")
        check(f, [((10**d,), 10**d + k, f"10^{d}")
                  for d, k in POWERS_OF_TEN_NEXT_PRIME], s, time_limit)
        print("\nNot checked, since the class hasn't decided: n already prime")
        for n in (7, 13):
            status, got, seconds = run(f, (n,), time_limit)
            print(f"  {f.__name__}({n}) = {got if status == 'ok' else status}")
        scores.append(s)

    print("\n======== Timing: n = 2^k ========")
    finished = compare_functions(
        list(fs), [2**k for k, p, g in TIMING_PRIMES], time_limit,
        labels=[f"2^{k}" for k, p, g in TIMING_PRIMES],
        expected=[p for k, p, g in TIMING_PRIMES])
    return _summary("test_next_prime", fs, scores, finished,
                    [k for k, p, g in TIMING_PRIMES])


def test_is_gen(*fs, time_limit=1.0):
    """Examples, checks and timing for is_gen(g, p) -> bool."""
    fs = _named(fs)
    scores = []
    for f in fs:
        _header("test_is_gen", f)
        s = Score()
        print("\nExamples 1: every g from 1 to p-1, for each prime p < 32.")
        print("Each line lists the g where your function returns True.")
        for p, gens in GENERATORS.items():
            results = {g: run(f, (g, p), time_limit) for g in range(1, p)}
            says_true = [g for g, r in results.items() if r[:2] == ("ok", True)]
            for g, (status, got, _) in results.items():
                if status == "ok" and got == (g in gens):
                    s.right += 1
                else:
                    s.wrong += 1
            line = f"  p = {p:2}:  {says_true}"
            print(line + ("  ✓" if says_true == gens else f"  ✗ expected {gens}"))
            for g, (status, got, _) in results.items():
                if status != "ok":
                    print(f"      {f.__name__}({g}, {p}): {status} {got or ''}")
                elif got not in (True, False):
                    print(f"      {f.__name__}({g}, {p}) = {got!r}, not True or False")
        print("\nExamples 2: p is not prime")
        check(f, [((g, p), a) for g, p, a in IS_GEN_NOT_PRIME], s, time_limit)
        print("\nExamples 3: bigger primes p")
        check(f, [((g, p), a) for g, p, a in IS_GEN_BIGGER], s, time_limit)
        scores.append(s)

    print("\n======== Timing: p is the smallest prime with k bits, "
          "g a generator ========")
    finished = compare_functions(
        list(fs), [(g, p) for k, p, g in TIMING_PRIMES], time_limit,
        labels=[f"{k} bits: g={g}, p={p}" for k, p, g in TIMING_PRIMES],
        expected=[True] * len(TIMING_PRIMES))
    return _summary("test_is_gen", fs, scores, finished,
                    [k for k, p, g in TIMING_PRIMES])


def test_isqrt(*fs, time_limit=1.0):
    """Examples, checks and timing for isqrt(n) -> int, the largest r with
    r * r <= n."""
    fs = _named(fs)
    scores = []
    for f in fs:
        _header("test_isqrt", f)
        s = Score()
        print("\nExamples 1: every n from 0 to 199, checking r * r <= n < (r+1) * (r+1)"
              " (only mistakes are shown)")
        for n in range(200):
            status, r, seconds = run(f, (n,), time_limit)
            if status == "ok" and isinstance(r, int) and r * r <= n < (r + 1) * (r + 1):
                s.right += 1
            else:
                s.wrong += 1
                print(f"  {f.__name__}({n}) = {r if status == 'ok' else status}  ✗")
        print(f"  {s.right}/200 right")
        print("\nExamples 2: n near a perfect square")
        check(f, [((n,), r) for n, r in ISQRT_NEAR_SQUARES], s, time_limit)
        print("\nExamples 3: n = p * p for a big prime p")
        check(f, [((p * p,), p, f"{p} * {p}") for p in ISQRT_PRIME_SQUARES],
              s, time_limit)
        print("\nExamples 4: very big n")
        labels = ["4^1100 - 1", "4^1100", "10^400 - 1", "10^400"]
        check(f, [((n,), r, lab) for (n, r), lab in zip(ISQRT_HUGE, labels)],
              s, time_limit)
        scores.append(s)

    print("\n======== Timing: n = 4^k - 1, so the answer is 2^k - 1 ========")
    finished = compare_functions(
        list(fs), [4**k - 1 for k in ISQRT_TIMING_BITS], time_limit,
        labels=[f"{2 * k} bits: 4^{k} - 1" for k in ISQRT_TIMING_BITS],
        expected=[2**k - 1 for k in ISQRT_TIMING_BITS])
    return _summary("test_isqrt", fs, scores, finished,
                    [2 * k for k in ISQRT_TIMING_BITS])
