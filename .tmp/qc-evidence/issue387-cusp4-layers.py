r"""Record, layer by layer, the stage of the cusp-4 walk that holds its cost (#387).

Runs the public ``cusp_chamber`` call at Sterk's fourth cusp with the walk's own
layer enumeration instrumented: for every layer of Vinberg's sequence (38) it
prints the layer's distance, its time, the memory high-water mark, the number of
candidate vectors the enumeration writes down, every root the walk accepts (with
whether that root's half-space is one of the eleven walls of Sterk (4.3.8) as
printed in Fig. 10, p. 23) and, after each acceptance, the result of Vinberg's
finite-volume test on the accepted facets (Vinberg 1972, §3, Prop. 1, p. 22 --
the engine's ``is_FundPoly``, which is the test ``FindRoots`` stops on).

The instrumentation is a subclass of the library's own walk class, substituted
for it through the module attribute ``_filtered_vinal_class``, so the run is the
public ``cusp_chamber`` and not a re-implementation of it.

Bounded by the caller (SIGKILL at the outer timeout); every line is flushed, so
the table of a killed run is complete up to the layer it reached.
"""

import resource
import sys
import time

from sage_extensions.all import *  # noqa: F401,F403
import sage_extensions.categories.hyperbolic_lattices as hyperbolic_lattices
from sage_extensions.categories.hyperbolic_lattices import (
    HyperbolicLattices,
    _framing_coordinates,
    _filtered_vinal_class,
)
from sage_extensions.sterk import Sterk

START = time.time()


def say(*parts):
    stamp = time.strftime("%H:%M:%S", time.localtime())
    elapsed = time.time() - START
    print(f"[{stamp} +{elapsed:7.1f}s] " + " ".join(str(p) for p in parts), flush=True)


def peak_mib():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def element_rows(reduction, negated):
    def convert(row):
        converted = reduction(tuple(int(entry) for entry in row))
        return -converted if negated else converted

    return convert


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
began = time.time()
subgroup = gamma_en_2()
say(f"subgroup built in {time.time() - began:.1f} s")

name = "Sterk_4"
arguments = sys.argv[1:]
which = next((item for item in arguments if item in ("figure", "selected")), "selected")
cusp = (
    Sterk.sterk4_cusp_vector()
    if which == "figure"
    else Sterk.selected_isotropic_vectors()[name]
)
say(f"cusp representative: {which} {tuple(int(entry) for entry in cusp.to_vector())}")
image = subgroup.isotropic_vector_reduction_image(cusp)
reduction = HyperbolicLattices(ZZ)(image.reduction())
engine_gram, negated = reduction._engine_gram_of_signature_n_1()
to_element = element_rows(reduction, negated)

# Sterk's eleven printed walls of Fig. 10 (4.3.8, p. 23), in T_En.  They lie in
# eta^perp, so a half-space of the reduction is one of them exactly when the
# class_lift of the root differs from one of them by a multiple of eta.
cusp_vector = image.vector()
printed_all = tuple(Sterk.cusp_roots_in_TEn(name))


def coordinates_of(element):
    return tuple(int(entry) for entry in element.to_vector())


ambient = NamedLattices.TEn
ambient_labels = tuple(ambient.module_generating_set())
ambient_gram = [
    [
        int(ambient.b(ambient.module_generator(left), ambient.module_generator(right)))
        for right in ambient_labels
    ]
    for left in ambient_labels
]


def ambient_pairing(left, right):
    total = 0
    for position, entry in enumerate(left):
        if entry:
            row = ambient_gram[position]
            for other, coefficient in enumerate(right):
                if coefficient:
                    total += entry * row[other] * coefficient
    return total


printed_walls = tuple(
    wall
    for wall in printed_all
    if ambient_pairing(coordinates_of(wall), coordinates_of(cusp_vector)) == 0
)
say(f"printed walls through this cusp: {len(printed_walls)} of {len(printed_all)}")
say(f"printed walls of 4.3.8: {len(printed_walls)} vectors of {cusp_vector.parent()}")


def coordinates(element):
    return tuple(int(entry) for entry in element.to_vector())


printed_coordinates = tuple(coordinates(wall) for wall in printed_all)
cusp_coordinates = coordinates(cusp_vector)
covered = set()


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


def lift_in_ambient_coordinates(row):
    r"""Return the TEn coordinates of the class lift of a reduction root.

    ``class_lift`` returns an element of the perpendicular subobject, whose
    ``to_vector`` is in that subobject's frame and not in ``T_En``'s, so the
    lift is rebuilt here from the reduction's own coordinate frame -- the
    same section ``class_lift`` uses, summed in ``T_En`` coordinates.
    """
    total = [0] * len(ambient_labels)
    coefficients = [int(entry) for entry in row.to_vector()]
    for position, label in enumerate(frame_labels):
        coefficient = coefficients[position]
        if coefficient:
            piece = frame[label].to_vector()
            total = [entry + coefficient * int(other) for entry, other in zip(total, piece)]
    return tuple(total)


def printed_wall_index(row):
    lift = lift_in_ambient_coordinates(row)
    for index, wall in enumerate(printed_coordinates):
        for sign in (1, -1):
            difference = tuple(a - sign * b for a, b in zip(lift, wall))
            if all(entry == 0 for entry in difference) or multiple_of_cusp(difference):
                return index
    return None


class Recording(_filtered_vinal_class()):
    r"""The library's walk, with every stage of it written to the log."""

    layer_index = 0
    candidate_tests = 0
    accepted = 0

    def Roots_decomposed_into(self, a, k):
        Recording.layer_index += 1
        index = Recording.layer_index
        distance = float(-a.inner_product(self.v0) / k ** 0.5) if k > 0 else float("nan")
        began = time.time()
        found = super().Roots_decomposed_into(a, k)
        elapsed = time.time() - began
        before = Recording.candidate_tests
        Recording.current = (index, distance, k)
        say(
            f"layer {index}: distance={distance:.4f} k={k} candidates={len(found)} "
            f"time={elapsed:.1f} s peakrss={peak_mib():.0f} MiB"
        )
        Recording.layer_tests = before
        return found

    def IsNewRoot(self, vector):
        Recording.candidate_tests += 1
        return super().IsNewRoot(vector)

    def is_FundPoly(self):
        began = time.time()
        answer = super().is_FundPoly()
        elapsed = time.time() - began
        Recording.accepted += 1
        root = self.roots[-1]
        row = tuple(int(entry) for entry in root)
        index, distance, k = getattr(Recording, "current", (0, float("nan"), 0))
        printed = printed_wall_index(row)
        if printed is not None:
            covered.add(printed)
        say(
            f"  accept #{Recording.accepted} on layer {index} (distance={distance:.4f}, k={k}): "
            f"q={int(root.inner_product(root))} square={int(to_element(row).q())} "
            f"wall-of-4.3.8={printed if printed is not None else 'no'} "
            f"printed-covered={len(covered)}/{len(printed_coordinates)} fundpoly={answer} "
            f"fundpoly-time={elapsed:.1f} s roots={len(self.roots)}"
        )
        say(f"    root={row}")
        return answer


hyperbolic_lattices._filtered_vinal_class = lambda: Recording
say("walk instrumented; running the public cusp_chamber at Sterk_4")
began = time.time()
bound = next((int(item) for item in arguments if item.lstrip("-").isdigit()), None)
say(f"bound: max_decompositions={bound}")
chamber = image.cusp_chamber(max_decompositions=bound)
say(f"cusp_chamber returned in {time.time() - began:.1f} s")
walls = tuple(chamber.wall_roots())
say(f"walls={len(walls)} complete={chamber.is_complete_wall_set()}")
for wall in walls:
    say(f"    wall q={int(wall.q())} {tuple(int(entry) for entry in wall.to_vector())}")
say("done")
