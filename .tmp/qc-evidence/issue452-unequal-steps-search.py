"""Wide search for a marked line whose section's Smith invariants are not all one."""
import time
from itertools import product

from sage_extensions.all import *  # noqa: F401,F403
from sage.all import ZZ, gcd, lcm
from sage.matrix.constructor import matrix
from sage.rings.rational_field import QQ

T0 = time.time()


def say(*a):
    print(f"[{time.time()-T0:7.1f}s]", *a, flush=True)


def steps_of(t):
    quotient = t.integral_parameter_quotient()
    P = quotient.domain()
    m = int(t.integral_parameter_period())
    rank = int(P.module_rank())
    plabels = tuple(P.module_generating_set())
    target = t.target_reduction().isotropic_embedding().codomain()
    rational_target = t._target_witt.rational_lattice()
    section = t._target_section
    columns = [
        list(rational_target.rational_coordinates(
            section(P.inclusion()(P.module_generator(label)).underlying_element())
        ).list())
        for label in plabels
    ]
    rows = int(target.module_rank())
    coordinates = matrix(QQ, rows, rank, [
        columns[column][entry] for entry in range(rows) for column in range(rank)
    ])
    denominator = ZZ(1)
    for entry in coordinates.list():
        denominator = lcm(denominator, ZZ(entry.denominator()))
    integral = matrix(ZZ, rows, rank, [
        ZZ((entry * denominator).numerator()) for entry in coordinates.list()
    ])
    diagonal, _u, _v = integral.smith_form()
    inv = [int(diagonal[i, i]) for i in range(rank)]
    steps = tuple(int(denominator // gcd(abs(d), denominator)) for d in inv)
    return m, inv, steps, int(denominator)


U = [[0, 1], [1, 0]]
U2 = [[0, 2], [2, 0]]
U4 = [[0, 4], [4, 0]]
grams = {
    "U+<2>+<2>": (Lattices(ZZ)(U), Lattices(ZZ)([[2, 0], [0, 2]])),
    "U(2)+<2>+<2>": (Lattices(ZZ)(U2), Lattices(ZZ)([[2, 0], [0, 2]])),
    "U(2)+<2>+<4>": (Lattices(ZZ)(U2), Lattices(ZZ)([[2, 0], [0, 4]])),
    "U(2)+<4>+<4>": (Lattices(ZZ)(U2), Lattices(ZZ)([[4, 0], [0, 4]])),
    "U(4)+<2>+<2>": (Lattices(ZZ)(U4), Lattices(ZZ)([[2, 0], [0, 2]])),
    "U+U+<2>": (Lattices(ZZ)(U), Lattices(ZZ)(U) + Lattices(ZZ)([[2]])),
    "U+U+<4>": (Lattices(ZZ)(U), Lattices(ZZ)(U) + Lattices(ZZ)([[4]])),
    "U(2)+U(2)+<2>": (Lattices(ZZ)(U2), Lattices(ZZ)(U2) + Lattices(ZZ)([[2]])),
    "U(2)+U(2)+<4>": (Lattices(ZZ)(U2), Lattices(ZZ)(U2) + Lattices(ZZ)([[4]])),
    "U(2)+U(4)+<2>": (Lattices(ZZ)(U2), Lattices(ZZ)(U4) + Lattices(ZZ)([[2]])),
    "U+A2": (Lattices(ZZ)(U), Lattices(ZZ)([[2, 1], [1, 2]])),
    "U(2)+A2(2)": (Lattices(ZZ)(U2), Lattices(ZZ)([[4, 2], [2, 4]])),
    "U(2)+A3(2)": (Lattices(ZZ)(U2), Lattices(ZZ)([[4, 2, 0], [2, 4, 2], [0, 2, 4]])),
    "U(2)+D4(2)": (Lattices(ZZ)(U2), Lattices(ZZ)([[4, 2, 0, 0], [2, 4, 0, 0], [0, 0, 4, 2], [0, 0, 2, 4]])),
}

seen = {}
for name, (first, second) in grams.items():
    L = first + second
    labels = tuple(L.module_generating_set())
    basis = [L.module_generator(label) for label in labels]
    rank = len(basis)
    tried = 0
    for coefficients in product((-2, -1, 0, 1, 2), repeat=rank):
        if all(c == 0 for c in coefficients):
            continue
        vector = sum((c * b for c, b in zip(coefficients, basis)),
                     L.base_ring().zero() * basis[0])
        if L.q(vector) != 0 or not vector.is_primitive():
            continue
        tried += 1
        if tried > 10:
            break
        try:
            line = L.primitive_isotropic_subobject(vector)
            red = line.isotropic_reduction()
            t = red.rational_lifts(red, red.Aut().one())
            m, inv, steps, denominator = steps_of(t)
        except Exception as error:  # noqa: BLE001
            say(f"{name} {coefficients} failed: {type(error).__name__} {str(error)[:160]}")
            continue
        flag = "" if len(set(steps)) == 1 else "   <<< UNEQUAL"
        key = (name, tuple(coefficients))
        seen[key] = steps
        say(f"{name} v={coefficients} div={L.div(vector)} m={m} N={denominator} "
            f"D={inv} steps={steps}{flag}")
unequal = [key for key, steps in seen.items() if len(set(steps)) != 1]
say("candidates", len(seen), "unequal", unequal)
say("done")
