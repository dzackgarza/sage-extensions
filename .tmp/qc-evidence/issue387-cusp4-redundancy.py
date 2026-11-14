r"""Are the walk's extra facets implied by the card's eleven walls? (#387)

At Sterk's fourth cusp the walk accepts sixteen normals before it is stopped by
a bound: seven are printed walls of (4.3.8), Fig. 10, p. 23, and nine are not.
Vinberg's sequence (38) legitimately carries roots whose half-space the others
imply (Vinberg 1972, Proposition 4, p. 28; the pruning of #401), so the question
that decides whether the walk can close on the card's eleven is not how many
roots it accepted but whether each extra half-space is implied by the eleven.

A half-space \(b(r,x)\ge 0\) is implied by the half-spaces of \(w_1,\dots,w_{11}\)
exactly when the covector of \(r\) lies in the cone they generate, and the
correlation is injective, so this is a cone-membership question in the
coordinates the library's own `rational_polyhedral_cone` reads.  All of it is
done in `T_En` coordinates: the printed walls and the lifts of the facets both
lie in the cusp's perpendicular, and modding by the cusp vector does not change
which half-spaces imply which.
"""

import sys
import time

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

ambient = NamedLattices.TEn
labels = tuple(ambient.module_generating_set())
correlation = ambient.algebraic_correlation_morphism()


def covector(element):
    return tuple(int(entry) for entry in correlation(element).to_vector())


printed = tuple(Sterk.cusp_roots_in_TEn("Sterk_4"))
printed_covectors = [covector(wall) for wall in printed]
say(f"printed walls={len(printed)}")

frame = image.reduction().coordinate_frame()
frame_labels = tuple(image.reduction().module_generating_set())


def lift_of(reduction_element):
    total = [0] * len(labels)
    coefficients = [int(entry) for entry in reduction_element.to_vector()]
    for position, label in enumerate(frame_labels):
        coefficient = coefficients[position]
        if not coefficient:
            continue
        piece = frame[label]
        piece = piece.to_vector() if hasattr(piece, "to_vector") else piece
        piece = [int(entry) for entry in piece]
        total = [entry + coefficient * other for entry, other in zip(total, piece)]
    return tuple(total)


carrier = Cone(printed_covectors)
say(f"cone of the eleven printed walls: dimension {carrier.dim()}, rays {len(carrier.rays())}")
implied = 0
for wall in walls:
    lift = lift_of(wall)
    inside = carrier.contains(covector(ambient(lift)))
    implied += 1 if inside else 0
    say(f"  accepted q={int(wall.q())} implied-by-the-eleven={inside} {tuple(int(entry) for entry in wall.to_vector())}")
say(f"accepted walls whose half-space the eleven imply: {implied} of {len(walls)}")
say("done")
