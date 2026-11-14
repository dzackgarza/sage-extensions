r"""Step 1 of the span batch: the index of the card's eleven, and membership (#387)

H. Sterk, Math. Z. 207 (1991), (4.3.10), p. 25: the roots of (4.3.8) span
`Z{e-f, e+f} + E8(-2)`, which he uses inside `H + E8(-2) = v^perp/Zv` (4.3.4,
p. 19).  This measures that span in the library's coordinates and asks, of each
wall the walk accepts, whether its class lies in it.

Everything runs in `Z^12`, the ambient coordinate lattice, where both the card's
walls and `class_lift`'s output live, with the Gram `G` built from the ambient
pairing.  A basis of `v^perp` is `{v}` together with the class lifts of the
reduction's module generators; `M + Zv` is the span of the card's eleven
together with `v`.  Then

    [v^perp : M + Zv]^2 = det Gram(M + Zv) / det Gram(v^perp),

and membership is decided by the Smith form of the generating matrix: with
`U A V = D` for the generators `A` as rows, `c A = w` has an integral solution
exactly when `w V` vanishes beyond the rank of `A` and its leading entries are
divisible by the corresponding `D[i,i]`.
"""

import time

from sage.matrix.constructor import matrix as sage_matrix
from sage.rings.integer_ring import ZZ as IntegerRing
from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.hyperbolic_lattices import HyperbolicLattices
from sage_extensions.sterk import Sterk

START = time.time()


def say(*parts):
    print(f"[{time.strftime('%H:%M:%S')} +{time.time() - START:7.1f}s] " + " ".join(str(p) for p in parts), flush=True)


def gamma_en_2():
    invariant = Involutions.I_En.invariant_lattice()
    labels = tuple(invariant.module_generating_set())
    for left in labels:
        for right in labels:
            if left < right and (
                invariant.q(invariant.module_generator(left)) == ZZ.zero()
                and invariant.q(invariant.module_generator(right)) == ZZ.zero()
                and invariant.b(invariant.module_generator(left), invariant.module_generator(right)) == ZZ(2)
            ):
                polarization = invariant.module_generator(left) + invariant.module_generator(right)
                return Involutions.I_En.polarized(invariant.inclusion()(polarization)).coinvariant_extension_subgroup()
    raise ArithmeticError("no degree-2 polarization found in the invariant lattice")


WALLS = [
    ((2, -5, -10, -15, -20, -25, -18, 6, 0, 2), -4, False),
    ((0, 1, 0, 0, 0, 0, 0, 0, 0, 0), -4, True),
    ((0, 0, 1, 0, 0, 0, 0, 0, 0, 0), -4, True),
    ((0, 0, 0, 1, 0, 0, 0, 0, 0, 0), -4, True),
    ((0, 0, 0, 0, 1, 0, 0, 0, 0, 0), -4, True),
    ((0, 0, 0, 0, 0, 1, 0, 0, 0, 0), -4, True),
    ((0, 0, 0, 0, 0, 0, 1, 0, 0, 0), -4, True),
    ((0, 0, 0, 0, 0, 0, 0, 0, 1, -1), -2, True),
    ((-5, 12, 25, 38, 51, 64, 45, -16, -3, -3), -2, False),
    ((-6, 13, 27, 41, 55, 69, 49, -17, -3, -3), -2, False),
    ((-13, 31, 62, 93, 125, 157, 111, -39, -7, -7), -2, False),
    ((-30, 72, 145, 218, 291, 364, 257, -90, -16, -16), -4, False),
    ((-20, 49, 98, 147, 196, 245, 173, -61, -11, -11), -2, False),
    ((-21, 50, 100, 150, 200, 250, 177, -62, -11, -11), -2, False),
    ((-27, 67, 134, 201, 268, 335, 236, -83, -15, -15), -2, False),
    ((-29, 69, 138, 207, 276, 345, 244, -85, -15, -15), -2, False),
]

say("building the subgroup and the reduction image")
subgroup = gamma_en_2()
image = subgroup.isotropic_vector_reduction_image(Sterk.sterk4_cusp_vector())
reduction = HyperbolicLattices(ZZ)(image.reduction())
ambient = NamedLattices.TEn
lattice = image.vector().parent()
rank = len(tuple(int(entry) for entry in image.vector().to_vector()))
unit = [tuple(1 if position == index else 0 for position in range(rank)) for index in range(rank)]
gram = [[int(ambient.b(ambient(left), ambient(right))) for right in unit] for left in unit]
G = sage_matrix(IntegerRing, gram)
v = tuple(int(entry) for entry in image.vector().to_vector())
say(f"rank {rank}, v = {v}")


def form(left, right):
    return sum(int(left[i]) * gram[i][j] * int(right[j]) for i in range(rank) for j in range(rank))


def gram_of(rows):
    size = len(rows)
    return sage_matrix(IntegerRing, [[int(form(rows[i], rows[j])) for j in range(size)] for i in range(size)])


generators = [
    tuple(int(entry) for entry in image.class_lift(reduction.module_generator(label)).to_vector())
    for label in reduction.module_generating_set()
]
perpendicular_basis = [v] + [row for row in generators if form(row, v) == 0]
say(f"basis of v^perp: {len(perpendicular_basis)} rows, all orthogonal to v: {all(form(row, v) == 0 for row in perpendicular_basis)}")
# A lattice index needs no quadratic form: the coordinate Gram of a rank-11
# basis determines the covolume in its own Q-span, and the form on v^perp is
# degenerate there because v itself is isotropic and lies in it.
def euclidean(rows):
    matrix = sage_matrix(IntegerRing, rows)
    return abs(int((matrix * matrix.transpose()).det()))


covolume_perpendicular = euclidean(perpendicular_basis)
say(f"coordinate covolume of v^perp: {covolume_perpendicular}")

card = [tuple(int(entry) for entry in wall.to_vector()) for wall in Sterk.cusp_roots_in_TEn("Sterk_4")]
say(f"the card's eleven: all orthogonal to v: {all(form(row, v) == 0 for row in card)}")
span_matrix = sage_matrix(IntegerRing, card)
say(f"the eleven have rank {span_matrix.rank()} in Z^{rank}")

walk = []
for coordinates, q, implied in WALLS:
    walk.append(tuple(int(entry) for entry in image.class_lift(reduction(coordinates)).to_vector()))

say("=== 1. the index of M in v^perp/Zv and the membership of the walk's walls ===")
independent = []
for row in card:
    trial = independent + [row]
    if sage_matrix(IntegerRing, trial).rank() == len(trial):
        independent.append(row)
say(f"a rank-{len(independent)} basis drawn from the eleven")
K = independent + [v]
say(f"M + Zv generated by {len(K)} vectors: the {len(independent)} independent walls and v")
if sage_matrix(IntegerRing, K).rank() != len(perpendicular_basis):
    say("the generators do not have full rank in v^perp: index not computed")
else:
    covolume_span = euclidean(K)
    say(f"coordinate covolume of M + Zv: {covolume_span}")
    from math import isqrt

    if covolume_span % covolume_perpendicular:
        say(f"index: {covolume_span}/{covolume_perpendicular} is not integral, so the two are not nested as computed")
    else:
        quotient = covolume_span // covolume_perpendicular
        root = isqrt(quotient)
        say(
            f"index [v^perp : M + Zv] = {root} (exact square: {root * root == quotient}), "
            f"ratio {quotient}"
        )

A = sage_matrix(IntegerRing, card + [v])
D, U, V = A.smith_form()
diagonal = [int(D[i][i]) for i in range(min(D.nrows(), D.ncols()))]
say(f"Smith diagonal of the eleven together with v: {diagonal}")


def in_span(vector):
    right = sage_matrix(IntegerRing, [[int(entry) for entry in vector]]) * V
    entries = [int(entry) for entry in right[0]]
    for position in range(len(entries)):
        if position < len(diagonal) and diagonal[position]:
            if entries[position] % diagonal[position]:
                return False
        elif entries[position]:
            return False
    return True


inside = {}
for position, vector in enumerate(walk):
    inside[position] = in_span(vector)
    say(f"walk wall {position} q={WALLS[position][1]} implied-by-card={WALLS[position][2]} in-M-plus-Zv={inside[position]}")
say(f"walk walls in M: {[p for p, value in inside.items() if value]}")
say(f"walk walls outside M: {[p for p, value in inside.items() if not value]}")
say("done")
