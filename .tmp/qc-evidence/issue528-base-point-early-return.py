r"""#528: the locus' test file reduces at isometries whose base point answers first.

`IsotropicReductionLiftTorsors.integral_base_point_or_none`
(`isotropic_lifts.py:768`) returns `self.base_point()` as soon as that base
point restricts integrally, and only otherwise walks
`integral_parameter_classes()`.  This probe builds the file's own non-identity
specimen -- `U(2) + U(2) + <2>` at its first basis line and at the Eichler
transvection of the reduction that the file uses -- and asks the two questions
the early return asks, plus the one that decides whether the locus was
consulted.

    sage -python <this file>
"""

import time

from sage_extensions.all import *  # noqa: F401,F403

START = time.monotonic()


def say(*parts):
    print(f"[{time.monotonic() - START:7.1f}s]", *parts, flush=True)


def main():
    lattice = (
        Lattices(ZZ)([[0, 2], [2, 0]])
        + Lattices(ZZ)([[0, 2], [2, 0]])
        + Lattices(ZZ)([[2]])
    )
    labels = tuple(lattice.module_generating_set())
    marked = lattice.module_generator(labels[0])
    line = lattice.primitive_isotropic_subobject(marked)
    reduction = line.isotropic_reduction()
    reduction_labels = tuple(reduction.module_generating_set())
    vectors = {label: reduction.module_generator(label) for label in reduction_labels}
    zero = reduction.base_ring().zero()
    direction = next(
        label for label in reduction_labels
        if vectors[label].q() == zero and vectors[label] != reduction.zero()
    )
    partner = next(
        label for label in reduction_labels
        if label != direction and vectors[direction].b(vectors[label]) == zero
    )
    isometry = reduction.eichler_transvection(vectors[direction], vectors[partner])
    identity = reduction.Isom(reduction).identity()
    say(f"the specimen: {lattice}")
    say(f"    the reduction isometry is not the identity: {isometry != identity}")

    for name, point in (("identity", identity), ("transvection", isometry)):
        torsor = reduction.rational_lifts(reduction, point)
        base = torsor.base_point()
        integral = base.integral_restriction(lattice, lattice)
        answer = torsor.integral_base_point_or_none()
        say(f"at the {name} of the reduction:")
        say(f"    the base point restricts integrally: {integral is not None}")
        say(f"    integral_base_point_or_none() returns the base point: {answer == base}")
        say(f"    the locus was consulted: {answer != base}")
    say("PROBE DONE")


if __name__ == "__main__":
    raise SystemExit(main())
