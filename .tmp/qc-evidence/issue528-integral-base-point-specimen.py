r"""#528: the specimens of the search, sized before they are put in a test.

The search reports a lattice, a marked vector and a reduction isometry whose
lift's base point is not integral.  Such a specimen is only usable in the locus'
test file if the brute force over `P/mP` is affordable, so this probe prints, per
specimen, whether the lattice is even, the divisibility, the size of `P/mP` and
the size of the locus -- the number of lift tests the test's own comparison
makes.

    sage -python <this file>
"""

import time

from sage_extensions.all import *  # noqa: F401,F403

START = time.monotonic()


def say(*parts):
    print(f"[{time.monotonic() - START:7.1f}s]", *parts, flush=True)


def integer(value):
    try:
        return int(value)
    except Exception:
        from sage_extensions.categories.rings.ring_foundation import (
            _engine_element,
            _owned_integers,
        )

        return int(_engine_element(_owned_integers(), value))


def examine(name, lattice, coefficients):
    labels = tuple(lattice.module_generating_set())
    marked = lattice.linear_combination({
        label: ZZ(coefficient)
        for label, coefficient in zip(labels, coefficients, strict=True)
    })
    say(f"{name}: rank {lattice.module_rank()}, even {lattice.is_even()}, "
        f"divisibility {integer(lattice.div(marked))}")
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
    torsor = reduction.rational_lifts(reduction, isometry)
    base = torsor.base_point()
    say(f"    the base point is integral: {base.integral_restriction(lattice, lattice) is not None}")
    quotient = torsor.integral_parameter_quotient()
    classes = integer(quotient.codomain().cardinality())
    say(f"    P/mP has {classes} classes, period {integer(torsor.integral_parameter_period())}")
    begin = time.monotonic()
    locus = torsor.integral_parameter_classes()
    size = integer(locus.cardinality())
    say(f"    the locus has {size} classes, computed in {time.monotonic() - begin:.2f} s")



def hyper(d):
    return Lattices(ZZ)([[0, d], [d, 0]])


CASES = (
    ("U(5) + U(4) at -2e0 - e2", (hyper(5) + hyper(4)), (-2, 0, -1, 0)),
    ("U(5) + U(5) at -2e0 - e2", (hyper(5) + hyper(5)), (-2, 0, -1, 0)),
    ("U(4) + U(4) at -2e0 - e2", (hyper(4) + hyper(4)), (-2, 0, -1, 0)),
    ("U(4) + U(4) at -e0 - e2", (hyper(4) + hyper(4)), (-1, 0, -1, 0)),
    ("U(6) + U(4) at -2e0 - e2", (hyper(6) + hyper(4)), (-2, 0, -1, 0)),
    ("U(3) + U(4) at -2e0 - e2", (hyper(3) + hyper(4)), (-2, 0, -1, 0)),
    ("U(5) + U(4) + U(4) at -2e0 - e2", (hyper(5) + hyper(4) + hyper(4)), (-2, 0, -1, 0, 0, 0)),
    ("U(5) + U(5) + U(4) at -2e0 - e4", (hyper(5) + hyper(5) + hyper(4)), (-2, 0, 0, 0, -1, 0)),
    ("U(5) + U(4) + U(4) at -2e0 - e4", (hyper(5) + hyper(4) + hyper(4)), (-2, 0, 0, 0, -1, 0)),
)


def main():
    for name, lattice, coefficients in CASES:
        try:
            examine(name, lattice, coefficients)
        except Exception as error:
            say(f"{name}: raised {error!r}"[:200])
    say("PROBE DONE")


if __name__ == "__main__":
    raise SystemExit(main())
