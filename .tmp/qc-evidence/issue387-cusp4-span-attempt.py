r"""What the card's eleven walls span in `v^perp/Zv` (#387)

H. Sterk, Math. Z. 207 (1991), (4.3.8) with Fig. 10, p. 23, and card `029J`'s
row for it list eleven walls, and (4.3.10), p. 25 prints that their span is
`Z{e-f, e+f} + E8(-2)` -- an index-two sublattice of `H + E8(-2)`, which is
`v^perp/Zv` by (4.3.4), p. 19.  This probe measures that index in the library's
own coordinates, and asks of each of the sixteen walls the walk accepts whether
its class lies in the span.

Everything is computed in one space: the coefficient vectors of the linear
functionals `b(w, .)` on `v^perp/Zv`, which is where the implication questions
of the earlier probes already lived.  The correlation of the ambient lattice is
injective, so `r` lies in the `Z`-span of the eleven exactly when its covector
does, and the index of a span is the same in either lattice because the
correlation is a `QQ`-linear isomorphism carrying one integral structure to the
other.

The span is computed by the Hermite normal form of the eleven covectors, which
for a rank-ten lattice gives a triangular basis of the span; membership is
back-substitution in that basis, and the index is the determinant of the basis.
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
correlation = ambient.algebraic_correlation_morphism()


lattice = image.vector().parent()
card = []
for wall in Sterk.cusp_roots_in_TEn("Sterk_4"):
    element = lattice(tuple(int(entry) for entry in wall.to_vector()))
    card.append(tuple(int(entry) for entry in reduction.projection()(element).to_vector()))
walk = [tuple(int(entry) for entry in coordinates) for coordinates, q, implied in WALLS]
say(f"card walls {len(card)}, walk walls {len(walk)}, coordinates each {len(card[0])} in v^perp/Zv")
say(f"the card's eleven in v^perp/Zv: {card}")

span = sage_matrix(IntegerRing, card)
say(f"the eleven's matrix is {span.nrows()}x{span.ncols()}, rank {span.rank()}")
normal = span.hermite_form()
say(f"its Hermite normal form has {sum(1 for row in normal.rows() if any(row))} nonzero rows")
basis = sage_matrix(IntegerRing, [list(row) for row in normal.rows() if any(row)])
det = abs(int(basis.det()))
say(f"determinant of the span's basis = {det}, so the index of M in the full lattice is {det}")
say(f"index given as a factorization: {det.factor() if det > 1 else 1}")

say("=== 1. does each walk wall lie in M? ===")
solutions = {}
for position, vector in enumerate(walk):
    coefficients = basis.transpose().solve_right(vector)
    integral = all(entry.denominator() == 1 for entry in coefficients)
    solutions[position] = bool(integral)
    say(
        f"walk wall {position} q={WALLS[position][1]} implied-by-card={WALLS[position][2]} "
        f"in-M={integral} coefficients={tuple(int(entry) if entry.denominator() == 1 else entry for entry in coefficients)}"
    )
say(f"walk walls inside M: {[p for p, inside in solutions.items() if inside]}")
say(f"walk walls outside M: {[p for p, inside in solutions.items() if not inside]}")
say("done")
