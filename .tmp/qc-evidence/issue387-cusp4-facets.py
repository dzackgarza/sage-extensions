r"""Are the sixteen accepted walls the facets of the card's chamber? (#387)

Vinberg's algorithm stops on the finite-volume test of the polyhedron the
accepted normals cut out (Vinberg 1972, Proposition 5, p. 29).  At Sterk's
fourth cusp the walk accepts sixteen normals and the test never fires.  Two
readings are possible and this probe separates them: either the sixteen
half-spaces cut a strictly smaller polyhedron than card 029J's eleven-wall
chamber (the accepted set is wrong), or they cut that chamber and the test is
wrong.

The facets of the intersection are decided exactly by the library's own
``_facet_roots`` (the cone's ``facet_covectors``), and each facet is compared
with Sterk's eleven printed walls of (4.3.8), Fig. 10, p. 23, as a class of the
reduction: the printed wall minus the facet's class lift is a multiple of the
cusp vector.
"""

import sys
import time

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


arguments = sys.argv[1:]
which = next((item for item in arguments if item in ("figure", "selected")), "figure")
bound = next((int(item) for item in arguments if item.isdigit()), 12)

say("building the subgroup")
subgroup = gamma_en_2()
cusp = Sterk.sterk4_cusp_vector() if which == "figure" else Sterk.selected_isotropic_vectors()["Sterk_4"]
image = subgroup.isotropic_vector_reduction_image(cusp)
reduction = HyperbolicLattices(ZZ)(image.reduction())
say(f"cusp={which} bound={bound}")
chamber = image.cusp_chamber(max_decompositions=bound)
walls = tuple(chamber.wall_roots())
say(f"accepted walls={len(walls)} complete={chamber.is_complete_wall_set()}")

elements = tuple(reduction(tuple(int(entry) for entry in wall.to_vector())) for wall in walls)
facets = reduction._facet_roots(elements)
say(f"facets of the intersection={len(facets)}")
for facet in facets:
    say(f"  facet q={int(facet.q())} {tuple(int(entry) for entry in facet.to_vector())}")

printed = tuple(
    tuple(int(entry) for entry in wall.to_vector()) for wall in Sterk.cusp_roots_in_TEn("Sterk_4")
)
cusp_coordinates = tuple(int(entry) for entry in image.vector().to_vector())


def multiple_of_cusp(difference):
    ratio = None
    for entry, base in zip(difference, cusp_coordinates):
        if base == 0:
            if entry != 0:
                return False
            continue
        if entry % base != 0:
            return False
        quotient = entry // base
        if ratio is None:
            ratio = quotient
        elif ratio != quotient:
            return False
    return ratio is not None


frame = image.reduction().coordinate_frame()
frame_labels = tuple(image.reduction().module_generating_set())


def lift_of(element):
    total = [0] * len(cusp_coordinates)
    coefficients = [int(entry) for entry in element.to_vector()]
    for position, label in enumerate(frame_labels):
        coefficient = coefficients[position]
        if not coefficient:
            continue
        piece = frame[label]
        piece = piece.to_vector() if hasattr(piece, "to_vector") else piece
        piece = [int(entry) for entry in piece]
        total = [entry + coefficient * other for entry, other in zip(total, piece)]
    return tuple(total)


matched = 0
for facet in facets:
    lift = lift_of(facet)
    hits = []
    for index, wall in enumerate(printed):
        for sign in (1, -1):
            difference = tuple(a - sign * b for a, b in zip(lift, wall))
            if all(entry == 0 for entry in difference) or multiple_of_cusp(difference):
                hits.append(index)
    if hits:
        matched += 1
    say(f"  facet {tuple(int(entry) for entry in facet.to_vector())} printed={hits}")
say(f"facets that are printed walls of 4.3.8: {matched} of {len(facets)}; printed total {len(printed)}")
say("done")
