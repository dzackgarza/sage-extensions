r"""What a class lift's coordinates are, in this library's own terms (#387)."""

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


subgroup = gamma_en_2()
cusp = Sterk.sterk4_cusp_vector()
image = subgroup.isotropic_vector_reduction_image(cusp)
reduction = HyperbolicLattices(ZZ)(image.reduction())
say(f"cusp vector: {len(tuple(int(e) for e in image.vector().to_vector()))} coordinates in {image.vector().parent()}")
frame = image.reduction().coordinate_frame()
say(f"coordinate_frame: {type(frame)} with {len(frame)} entries")
position = 0
for label in image.reduction().module_generating_set():
    lift = frame[label]
    coordinates = lift.to_vector() if hasattr(lift, "to_vector") else lift
    say(f"  frame[{label}]: type={type(lift).__name__} coordinates={len(list(coordinates))} first={list(coordinates)[:4]}")
    position += 1
    if position >= 2:
        break
perpendicular = image.reduction().orthogonal_complement()
say(f"orthogonal_complement: {perpendicular}")
label = tuple(image.reduction().module_generating_set())[0]
included = perpendicular.inclusion()(frame[label])
coordinates = included.to_vector() if hasattr(included, "to_vector") else included
say(f"  inclusion of the first frame lift: type={type(included).__name__} coordinates={len(list(coordinates))} first={list(coordinates)[:4]}")
root = reduction(tuple([1] + [0] * 9))
lifted = image.class_lift(root) if root.q() else None
if lifted is not None:
    coordinates = lifted.to_vector()
    say(f"  class_lift of a reduction vector: type={type(lifted).__name__} coordinates={len(list(coordinates))} first={list(coordinates)[:4]}")
say("done")
