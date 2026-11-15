r"""#528: rank-five even specimens, sized, so the test's brute force stays cheap.

The search's first even specimen is `U(5) + U(5) + U(4)` at `-2 e_1 - e_5`, with
`4096` classes in `P/mP`: the test's brute force over every class of the quotient
then costs far more than a test may.  A rank-five lattice has three parameter
coordinates, so `P/mP` has `m^3` classes -- `512` at period eight, `64` at period
four -- which is the size the file's own `U + A3(2)` test already carries.

This probe scans rank-five even lattices of the same shape for a marked line
whose lift's base point is not integral, and prints the period and the size of
the quotient for every hit, so the cheapest one can be put in the test.

    sage -python <this file> [budget=420]
"""

import itertools
import math
import time

from sage_extensions.all import *  # noqa: F401,F403

START = time.monotonic()
BUDGET = 420.0


def now():
    return time.monotonic()


def say(*parts):
    print(f"[{now() - START:7.1f}s]", *parts, flush=True)


def integer(value):
    try:
        return int(value)
    except Exception:
        from sage_extensions.categories.rings.ring_foundation import (
            _engine_element,
            _owned_integers,
        )

        return int(_engine_element(_owned_integers(), value))


def hyper(d):
    return Lattices(ZZ)([[0, d], [d, 0]])


def one(m):
    return Lattices(ZZ)([[m]])


LATTICES = {
    "U(5)+U(4)+<2>": hyper(5) + hyper(4) + one(2),
    "U(5)+U(3)+<2>": hyper(5) + hyper(3) + one(2),
    "U(5)+U(2)+<2>": hyper(5) + hyper(2) + one(2),
    "U(4)+U(4)+<2>": hyper(4) + hyper(4) + one(2),
    "U(6)+U(4)+<2>": hyper(6) + hyper(4) + one(2),
    "U(5)+U(4)+<-2>": hyper(5) + hyper(4) + one(-2),
    "U(3)+U(4)+<2>": hyper(3) + hyper(4) + one(2),
    "U(5)+U(4)+A2": hyper(5) + hyper(4) + Lattices(ZZ)("A2"),
    "U(5)+U(4)+<4>": hyper(5) + hyper(4) + one(4),
}


def patterns(rank):
    for position in range(rank):
        for value in (-2, -1, 1, 2):
            pattern = [0] * rank
            pattern[position] = value
            yield tuple(pattern)
    for first, second in itertools.combinations(range(rank), 2):
        for left in (-2, -1, 1, 2):
            for right in (-2, -1, 1, 2):
                pattern = [0] * rank
                pattern[first] = left
                pattern[second] = right
                yield tuple(pattern)


def main(argv):
    global BUDGET
    for argument in argv:
        if argument.startswith("budget="):
            BUDGET = float(argument.split("=", 1)[1])
    begin = now()
    tried = 0
    hits = []
    for name, lattice in LATTICES.items():
        labels = tuple(lattice.module_generating_set())
        say(f"{name}: rank {lattice.module_rank()}, even {lattice.is_even()}")
        for pattern in patterns(len(labels)):
            if now() - begin > BUDGET:
                say("budget spent")
                break
            if math.gcd(*[abs(coefficient) for coefficient in pattern]) != 1:
                continue
            marked = lattice.linear_combination({
                label: ZZ(coefficient)
                for label, coefficient in zip(labels, pattern, strict=True)
                if coefficient
            })
            if marked.q() != lattice.base_ring().zero():
                continue
            if integer(lattice.div(marked)) < 2:
                continue
            line = lattice.primitive_isotropic_subobject(marked)
            reduction = line.isotropic_reduction()
            reduction_labels = tuple(reduction.module_generating_set())
            vectors = {label: reduction.module_generator(label) for label in reduction_labels}
            zero = reduction.base_ring().zero()
            directions = [label for label in reduction_labels if vectors[label].q() == zero]
            isometry = None
            for direction in directions:
                for partner in reduction_labels:
                    if partner == direction or vectors[direction].b(vectors[partner]) != zero:
                        continue
                    candidate = reduction.eichler_transvection(
                        vectors[direction], vectors[partner]
                    )
                    if candidate != reduction.Isom(reduction).identity():
                        isometry = candidate
                        break
                if isometry is not None:
                    break
            if isometry is None:
                continue
            torsor = reduction.rational_lifts(reduction, isometry)
            tried += 1
            if torsor.base_point().integral_restriction(lattice, lattice) is None:
                classes = integer(torsor.integral_parameter_quotient().codomain().cardinality())
                hits.append((name, pattern, integer(lattice.div(marked)),
                             integer(torsor.integral_parameter_period()), classes))
                say(f"    HIT {name} at {pattern}: div {integer(lattice.div(marked))}, "
                    f"period {integer(torsor.integral_parameter_period())}, "
                    f"P/mP {classes}")
    say("")
    say(f"RESULT torsors={tried} hits={len(hits)} seconds={now() - begin:.1f}")
    for hit in sorted(hits, key=lambda item: item[4]):
        say(f"  {hit[0]} {hit[1]} div={hit[2]} period={hit[3]} classes={hit[4]}")
    say("PROBE DONE")


if __name__ == "__main__":
    raise SystemExit(main(__import__("sys").argv[1:]))
