"""The U + A3(2) control whose section has unequal Smith steps, read both ways (#452).

Prints the section's Smith data, the number of classes the locus reports, and the number
of classes of P/mP whose own parameter lift restricts to an isometry -- the direct
enumeration, with no coset decomposition used.
"""
import time

from sage_extensions.all import *  # noqa: F401,F403
from sage.all import ZZ, gcd, lcm
from sage.matrix.constructor import matrix
from sage.rings.rational_field import QQ

T0 = time.time()


def say(*a):
    print(f"[{time.time()-T0:7.1f}s]", *a, flush=True)


L = Lattices(ZZ)("U") + Lattices(ZZ)([[4, 2, 0], [2, 4, 2], [0, 2, 4]])
labels = tuple(L.module_generating_set())
basis = tuple(L.module_generator(label) for label in labels)
coefficients = (-2, 2, -1, 2, -1)
marked = sum((c * b for c, b in zip(coefficients, basis)), L.base_ring().zero() * basis[0])
say("lattice U + A3(2), marked", coefficients, "q", L.q(marked),
    "primitive", marked.is_primitive(), "div", L.div(marked))
reduction = L.primitive_isotropic_subobject(marked).isotropic_reduction()
torsor = reduction.rational_lifts(reduction, reduction.Isom(reduction).identity())
quotient = torsor.integral_parameter_quotient()
P = quotient.domain()
m = int(torsor.integral_parameter_period())
rank = int(P.module_rank())
plabels = tuple(P.module_generating_set())
target = torsor.target_reduction().isotropic_embedding().codomain()
rational_target = torsor._target_witt.rational_lattice()
section = torsor._target_section
columns = [
    list(rational_target.rational_coordinates(
        section(P.inclusion()(P.module_generator(label)).underlying_element())
    ).list())
    for label in plabels
]
rows = int(target.module_rank())
coordinate_matrix = matrix(QQ, rows, rank, [
    columns[column][entry] for entry in range(rows) for column in range(rank)
])
denominator = ZZ(1)
for entry in coordinate_matrix.list():
    denominator = lcm(denominator, ZZ(entry.denominator()))
integral_matrix = matrix(ZZ, rows, rank, [
    ZZ((entry * denominator).numerator()) for entry in coordinate_matrix.list()
])
diagonal, _left, right = integral_matrix.smith_form()
invariants = tuple(int(diagonal[i, i]) for i in range(rank))
steps = tuple(int(denominator // gcd(abs(d), denominator)) for d in invariants)
say("rank", rank, "period", m, "denominator", denominator,
    "smith invariants", invariants, "steps", steps)
say("V", tuple(tuple(int(entry) for entry in row) for row in right.rows()))
say("V permutes the cube", sorted(abs(int(entry)) for entry in right.list()) == [0, 0, 1, 1])

reported = set(torsor.integral_parameter_classes())
inclusion = P.inclusion()
start = time.time()
integral = set()
for residue in quotient.codomain():
    parameter = inclusion(quotient.preimage(residue)).underlying_element()
    if torsor.parameterization()(parameter).integral_restriction(L, L) is not None:
        integral.add(residue)
say("classes of P/mP", len(set(quotient.codomain())),
    "reported by the locus", len(reported),
    "integral by direct enumeration", len(integral),
    "in", time.time() - start, "s")
say("reported == integral", reported == integral,
    "reported inside integral", reported <= integral)
say("done")
