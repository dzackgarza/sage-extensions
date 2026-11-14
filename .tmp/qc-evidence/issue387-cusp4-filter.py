r"""Decide, for every wall the cusp-4 walk accepts, whether its reflection is in G_v (#387).

The walk accepts roots whose reflection the root filter admits.  This probe asks
the same question of each accepted root by both public doors the library has --
``admits_root`` (the filter the walk uses) and ``contains_root_reflection``
(which goes through the Levi image ``reduction_image``) -- and marks the roots
that are one of the eleven printed walls of Sterk (4.3.8), Fig. 10, p. 23.
A disagreement between the two doors is the defect; agreement with "not a
printed wall" means the accepted set is the honest chamber of the group the
filter defines.
"""

import sys
import time

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.hyperbolic_lattices import (
    HyperbolicLattices,
    _framing_coordinates,
)
from sage_extensions.sterk import Sterk

START = time.time()


def say(*parts):
    stamp = time.strftime("%H:%M:%S", time.localtime())
    print(f"[{stamp} +{time.time() - START:7.1f}s] " + " ".join(str(p) for p in parts), flush=True)


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


say("building the subgroup")
subgroup = gamma_en_2()
say("subgroup built")

which = sys.argv[1] if len(sys.argv) > 1 else "figure"
cusp = Sterk.sterk4_cusp_vector() if which == "figure" else Sterk.selected_isotropic_vectors()["Sterk_4"]
image = subgroup.isotropic_vector_reduction_image(cusp)
reduction = HyperbolicLattices(ZZ)(image.reduction())
chamber = image.cusp_chamber(max_decompositions=int(sys.argv[2]) if len(sys.argv) > 2 else 40)
walls = tuple(chamber.wall_roots())
say(f"cusp={which} walls={len(walls)} complete={chamber.is_complete_wall_set()}")

printed = tuple(Sterk.cusp_roots_in_TEn("Sterk_4"))
say(f"printed walls of 4.3.8: {len(printed)}")

agree = 0
disagree = 0
for wall in walls:
    by_the_filter = bool(image.admits_root(wall))
    by_the_levi_map = bool(image.contains_root_reflection(image.class_lift(wall)))
    if by_the_filter == by_the_levi_map:
        agree += 1
    else:
        disagree += 1
    say(
        f"  wall q={int(wall.q())} filter={by_the_filter} levi={by_the_levi_map} "
        f"{tuple(int(entry) for entry in wall.to_vector())}"
    )
say(f"agreements={agree} disagreements={disagree}")

say("the printed walls through the filter and the Levi map")
for position, root in enumerate(printed):
    say(
        f"  printed {position}: q={int(root.q())} "
        f"admits={bool(image.admits_root(image.reduction()(tuple(int(entry) for entry in root.to_vector()))))} "
        f"{tuple(int(entry) for entry in root.to_vector())}"
    )
say("done")
