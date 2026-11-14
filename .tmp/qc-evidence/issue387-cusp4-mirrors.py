r"""Does a mirror of W_v meet the card's eleven-wall polyhedron's interior? (#387)

Two questions, both decided exactly.

1. For each of the sixteen walls the walk accepts at Sterk's 4.3.8 cusp, decide
   whether its mirror meets the interior of the polyhedron `P` that card `029J`'s
   eleven printed walls cut out.  A half-space `b(r,x) >= 0` is implied by the
   eleven exactly when the covector of `r` lies in the cone they generate (the
   correlation is injective, `issue387-cusp4-redundancy.py`), so the mirror
   `b(r,x) = 0` meets the *interior* of `P` exactly when neither `r` nor `-r` lies
   in that cone: `r` absent says the oracle does not force `b(r,x) >= 0`, `-r`
   absent says it does not force `b(r,x) <= 0` either, and a supporting hyperplane
   is the only remaining way for the intersection to hold.  Where both are
   absent, a point of the interior on the mirror is produced by linear
   programming over `QQ`: the system `u_j . x >= 1` (the eleven) with
   `u_r . x = 0` is feasible exactly then, since the region is a cone and a
   strictly positive point can be rescaled into it.

2. The card's row against the figure: the cusp vector, the eleven wall vectors
   and the Gram matrix of the eleven, against Sterk's printed data
   (`.tmp/sources/sterk-1991-...-i.md`, 4.3.8 with Fig. 10, p. 23) as this
   library transcribes it (`Sterk.sterk4_cusp_vector`,
   `Sterk.cusp_roots_in_TEn("Sterk_4")`), and against the edge orders the card's
   own row records.
"""

import json
import sys
import time
from pathlib import Path

from sage.geometry.polyhedron.constructor import Polyhedron
from sage.rings.rational_field import QQ as RationalField
from sage.geometry.cone import Cone
from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.hyperbolic_lattices import HyperbolicLattices
from sage_extensions.sterk import Sterk

START = time.time()


def say(*parts):
    print(f"[{time.strftime('%H:%M:%S')} +{time.time() - START:7.1f}s] " + " ".join(str(p) for p in parts), flush=True)


def gamma_en_2():
    invariant = Involutions.I_En.invariant_lattice()
    labels = tuple(invariant.module_generating_set())
    marks = [
        (left, right)
        for left in labels
        for right in labels
        if left <= right
        and invariant.q(invariant.module_generator(left)) == ZZ.zero()
        and invariant.q(invariant.module_generator(right)) == ZZ.zero()
        and invariant.b(invariant.module_generator(left), invariant.module_generator(right)) == ZZ(2)
    ]
    left, right = marks[0]
    polarization = invariant.module_generator(left) + invariant.module_generator(right)
    return Involutions.I_En.polarized(invariant.inclusion()(polarization)).coinvariant_extension_subgroup()


def interior_point_on_mirror(eleven, mirror):
    r"""A point of `P`'s interior on the mirror `b(r, x) = 0`, certified exactly.

    The region is the cone `{x : u_j . x > 0 for the eleven, u_r . x = 0}`.  A
    float linear program locates a candidate, and the candidate is then checked
    over `QQ`: every one of the eleven pairings strictly positive and the
    mirror's pairing exactly zero.  A rounded float is a witness only because
    the exact check passes afterwards; the check is what the log reports.
    """
    import numpy

    try:
        from scipy.optimize import linprog
    except Exception as error:  # noqa: BLE001
        return f"no-LP-route:{type(error).__name__}"
    matrix = numpy.array([[float(entry) for entry in covector] for covector in eleven])
    objective = numpy.zeros(matrix.shape[1])
    inequalities = -matrix, -numpy.ones(len(eleven))
    equality = numpy.array([[float(entry) for entry in mirror]])
    solution = linprog(
        objective,
        A_ub=inequalities[0],
        b_ub=inequalities[1],
        A_eq=equality,
        b_eq=numpy.zeros(1),
        bounds=[(None, None)] * matrix.shape[1],
        method="highs",
    )
    if not solution.success:
        return f"LP-infeasible:{solution.message}"
    from fractions import Fraction

    candidate = [Fraction(float(entry)).limit_denominator(10**6) for entry in solution.x]
    slack = [sum(Fraction(int(c)) * y for c, y in zip(covector, candidate)) for covector in eleven]
    mirror_value = sum(Fraction(int(c)) * y for c, y in zip(mirror, candidate))
    if min(slack) <= 0 or mirror_value != 0:
        return f"LP-candidate-not-certified:min-slack={min(slack)},mirror={mirror_value}"
    return f"{tuple(candidate)} certified: min pairing with the eleven = {min(slack)}, mirror pairing = {mirror_value}"


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
lattice = image.vector().parent()
ambient = NamedLattices.TEn
correlation = ambient.algebraic_correlation_morphism()


def covector_of_ambient_coordinates(element):
    return tuple(int(entry) for entry in correlation(element).to_vector())


printed = tuple(Sterk.cusp_roots_in_TEn("Sterk_4"))
printed_covectors = [covector_of_ambient_coordinates(ambient(tuple(int(e) for e in wall.to_vector()))) for wall in printed]
say(f"printed walls={len(printed)}")
carrier = Cone(printed_covectors)
say(f"cone of the eleven: dimension {carrier.dim()}, rays {len(carrier.rays())}")

say("=== 1. does each mirror meet the interior of the card's polyhedron? ===")
verdicts = {}
for position, (coordinates, q, implied) in enumerate(WALLS):
    root = reduction(coordinates)
    lift = ambient(tuple(int(entry) for entry in image.class_lift(root).to_vector()))
    u = covector_of_ambient_coordinates(lift)
    forward = carrier.contains(u)
    backward = carrier.contains(tuple(-entry for entry in u))
    meets = (not forward) and (not backward)
    point = None
    if meets:
        point = interior_point_on_mirror(printed_covectors, u)
    verdicts[position] = meets
    say(
        f"wall {position} q={q} implied-card={implied} r-in-cone={forward} minus-r-in-cone={backward} "
        f"mirror-meets-interior={meets} interior-point-on-mirror={point}"
    )
say(f"walls whose mirror meets the interior: {[p for p, m in verdicts.items() if m]}")

say("=== 2. card 029J row 4.3.8 against the figure ===")
digest = Path("/repos/sage-extensions/tests/cards/lattice-database-enriques.json")
rows = json.loads(digest.read_text(encoding="utf-8"))["cusp_diagrams"]["029J"]["rows"]["gamma-en-2"]
row = next(item for item in rows if item.get("statement") == "4.3.8")
say(f"card row: figure={row['figure']} printed_page={row['printed_page']} wall_count={row['wall_count']} vertices={row['vertices']}")
card_cusp = tuple(row["cusp"])
library_cusp = tuple(int(entry) for entry in Sterk.sterk4_cusp_vector().to_vector())
say(f"card cusp vector    {card_cusp}")
say(f"library cusp vector {library_cusp}")
say(f"they agree: {card_cusp == library_cusp}")
say(
    "their pairing: "
    f"{ambient.b(ambient(card_cusp), ambient(library_cusp))}"
)
card_walls = [tuple(vector) for vector in row["wall_vectors"]]
library_walls = [tuple(int(entry) for entry in wall.to_vector()) for wall in printed]
say(f"card walls={len(card_walls)} library walls={len(library_walls)}")
for index, (from_card, from_library) in enumerate(zip(card_walls, library_walls)):
    say(f"  vertex {row['vertices'][index]}: card={from_card} library={from_library} agree={from_card == from_library}")
say(f"as sets they agree: {sorted(card_walls) == sorted(library_walls)}")

say("card edge orders against the computed Gram matrix of the eleven")
gram = [[int(ambient.b(printed[i], printed[j])) for j in range(len(printed))] for i in range(len(printed))]
say(f"computed Gram: {gram}")
name_to_index = {name: index for index, name in enumerate(row["vertices"])}
mismatches = 0
for edge in row["edges"]:
    left = name_to_index.get(edge["left"])
    right = name_to_index.get(edge["right"])
    if left is None or right is None:
        say(f"  edge {edge['left']}--{edge['right']}: names not both in the card's vertices")
        mismatches += 1
        continue
    value = gram[left][right]
    order = edge["order"]
    # cos(pi/k) = b_ij / sqrt(q_i q_j) is the diagram relation for vectors of
    # arbitrary square; compare the squares exactly.
    numerator, denominator = {3: (1, 4), 4: (1, 2), 6: (3, 4)}.get(order, (None, None))
    if numerator is None:
        agrees = None
    else:
        left_square = gram[left][left]
        right_square = gram[right][right]
        agrees = value**2 * denominator == left_square * right_square * numerator
    mismatches += 0 if agrees else 1
    say(
        f"  edge {edge['left']}--{edge['right']} order {order}: gram={value} "
        f"squares=({gram[left][left]},{gram[right][right]}) agrees={agrees}"
    )
negatives = sum(1 for i in range(len(gram)) for j in range(i + 1, len(gram)) if gram[i][j] < 0)
say(f"edge entries in the card's row: {len(row['edges'])}; negative Gram entries away from the diagonal: {negatives}; mismatches: {mismatches}")
say("done")
