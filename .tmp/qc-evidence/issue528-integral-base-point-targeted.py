r"""#528: a reduction isometry whose lift has no integral base point, by construction.

At the identity of the reduction the lift's base point is the identity of the
lattice, so the question is only about isometries of the reduction that are not
the identity.  The isometries the control searches try are Eichler transvections
of the reduction and their products, and those lift integrally by construction
(`E_{e,x}` is integral whenever `q(x) div(e) / 2` is).  What is missing from that
search is a reduction whose isometries are *not* transvections: a definite
quotient, where the isometries are reflections, and a marked line whose section
carries denominators (`m = 2AB` with `B > 1`).

This probe builds such cases, enumerates the reduction's integral isometries --
reflections in its short vectors, its signed permutations of the Gram, its
transvections and pairwise products -- and asks each lift's base point for its
integral restriction.  A base point that is not an integral isometry is the
specimen the locus exists for.

    sage -python <this file> [budget=400]
"""

import itertools
import time

from sage_extensions.all import *  # noqa: F401,F403

START = time.monotonic()
BUDGET = 400.0


def now():
    return time.monotonic()


def say(*parts):
    print(f"[{now() - START:7.1f}s]", *parts, flush=True)


def integer(value):
    try:
        return int(value)
    except Exception:
        pass
    from sage_extensions.categories.rings.ring_foundation import _engine_element, _owned_integers

    return int(_engine_element(_owned_integers(), value))


def gram_of(lattice):
    return [[integer(lattice.b(left, right)) for right in lattice.module_generators()]
            for left in lattice.module_generators()]


def lattice_of(rows):
    rank = sum(len(row) for row in rows)
    gram = [[0] * rank for _ in range(rank)]
    offset = 0
    for row in rows:
        for i, line in enumerate(row):
            for j, entry in enumerate(line):
                gram[offset + i][offset + j] = entry
        offset += len(row)
    return Lattices(ZZ)(gram)


U1 = [[0, 1], [1, 0]]
U2 = [[0, 2], [2, 0]]
U3 = [[0, 3], [3, 0]]
A2 = [[2, -1], [-1, 2]]
A3 = [[2, -1, 0], [-1, 2, -1], [0, -1, 2]]
A32 = [[4, 2, 0], [2, 4, 2], [0, 2, 4]]
D4 = [[2, -1, 0, 0], [-1, 2, -1, 0], [0, -1, 2, -1], [0, 0, -1, 2]]


def cases():
    """(name, lattice, marked or None for the first basis line)."""
    yield "U + A3(2) at (-2,2,-1,2,-1)", lattice_of([U1, A32]), (-2, 2, -1, 2, -1)
    yield "U + A3(2) at the first basis line", lattice_of([U1, A32]), None
    yield "U(2) + A3(2) at the first basis line", lattice_of([U2, A32]), None
    yield "U + A3 at the first basis line", lattice_of([U1, A3]), None
    yield "U(2) + A3 at the first basis line", lattice_of([U2, A3]), None
    yield "U(3) + A2 at the first basis line", lattice_of([U3, A2]), None
    yield "U(3) + A3 at the first basis line", lattice_of([U3, A3]), None
    yield "U(2) + U(2) + A2 at the first basis line", lattice_of([U2, U2, A2]), None
    yield "U(2) + D4 at the first basis line", lattice_of([U2, D4]), None
    yield "U + D4 at the first basis line", lattice_of([U1, D4]), None
    yield "U(2) + U(2) + <2> at the first basis line", lattice_of([U2, U2, [[2]]]), None
    yield "U(3) + <1> + A2 at the first basis line", lattice_of([U3, [[1]], A2]), None


def marked_vector(lattice, coefficients):
    if coefficients is None:
        return lattice.module_generator(tuple(lattice.module_generating_set())[0])
    labels = tuple(lattice.module_generating_set())
    return lattice.linear_combination({
        label: ZZ(coefficient)
        for label, coefficient in zip(labels, coefficients, strict=True)
    })


def reduction_isometries(reduction, limit):
    """Integral isometries of the reduction: reflections, signed Gram symmetries, transvections."""
    labels = tuple(reduction.module_generating_set())
    basis = {label: reduction.module_generator(label) for label in labels}
    generators = tuple(basis[label] for label in labels)
    zero = reduction.base_ring().zero()
    identity = reduction.Isom(reduction).identity()
    seen = []
    count = 0

    def offer(name, isometry):
        nonlocal count
        if count >= limit:
            return False
        if isometry == identity:
            return True
        seen.append((name, isometry))
        count += 1
        return True

    # Reflections in the short vectors of the reduction, primitive or not.
    rank = len(labels)
    for coefficients in itertools.product(range(-2, 3), repeat=rank):
        if all(coefficient == 0 for coefficient in coefficients):
            continue
        vector = reduction.linear_combination({
            label: ZZ(coefficient)
            for label, coefficient in zip(labels, coefficients, strict=True)
            if coefficient
        })
        if vector.q() == zero:
            continue
        try:
            isometry = reduction.reflection(vector)
        except Exception:
            continue
        if not offer(f"reflection{coefficients}", isometry):
            return seen
    # Signed permutations that preserve the pairing.
    for permutation in itertools.permutations(range(rank)):
        for signs in itertools.product((1, -1), repeat=rank):
            images = {}
            for position, label in enumerate(labels):
                images[label] = reduction.scalar_multiple(
                    ZZ(signs[position]), generators[permutation[position]]
                )
            candidate = reduction.Isom(reduction)(images)
            if all(
                candidate(generators[i]).b(candidate(generators[j])) == generators[i].b(generators[j])
                for i in range(rank) for j in range(rank)
            ):
                if not offer(f"permuation{permutation}{signs}", candidate):
                    return seen
    # Eichler transvections of the reduction and pairwise products.
    transvections = []
    for direction in labels:
        for parameter in labels:
            vector, other = basis[direction], basis[parameter]
            if vector.q() != zero or vector.b(other) != zero:
                continue
            isometry = reduction.eichler_transvection(vector, other)
            if isometry != identity:
                transvections.append((f"transvection({direction},{parameter})", isometry))
    for name, isometry in transvections:
        if not offer(name, isometry):
            return seen
    for (left_name, left), (right_name, right) in itertools.combinations(transvections, 2):
        if not offer(f"{left_name}*{right_name}", left * right):
            return seen
    return seen


def main(argv):
    global BUDGET
    for argument in argv:
        if argument.startswith("budget="):
            BUDGET = float(argument.split("=", 1)[1])
    begin = now()
    total = 0
    hits = []
    for name, lattice, coefficients in cases():
        if now() - begin > BUDGET:
            say("budget spent")
            break
        marked = marked_vector(lattice, coefficients)
        if marked.q() != lattice.base_ring().zero():
            say(f"{name}: the marked vector is not isotropic")
            continue
        line = lattice.primitive_isotropic_subobject(marked)
        reduction = line.isotropic_reduction()
        identity_torsor = reduction.rational_lifts(
            reduction, reduction.Isom(reduction).identity()
        )
        quotient = identity_torsor.integral_parameter_quotient()
        period = integer(identity_torsor.integral_parameter_period())
        say(f"{name}: gram {gram_of(lattice)}, div {integer(lattice.div(marked))}, "
            f"reduction rank {reduction.module_rank()}, period {period}, "
            f"P/mP {integer(quotient.codomain().cardinality())} classes")
        isometries = reduction_isometries(reduction, limit=60)
        say(f"    {len(isometries)} integral isometries of the reduction to try")
        found = 0
        for isometry_name, isometry in isometries:
            if now() - begin > BUDGET:
                say("budget spent inside the isometries")
                break
            torsor = reduction.rational_lifts(reduction, isometry)
            total += 1
            if torsor.base_point().integral_restriction(lattice, lattice) is None:
                found += 1
                hits.append((name, isometry_name))
                say(f"    HIT {name}: {isometry_name}")
                say(f"        the base point is not integral; P/mP has "
                    f"{integer(torsor.integral_parameter_quotient().codomain().cardinality())} "
                    f"classes and the locus "
                    f"{integer(torsor.integral_parameter_classes().cardinality())}")
        if not found:
            say(f"    0 of {len(isometries)} have a base point that is not integral")
    say("")
    say(f"RESULT torsors={total} hits={len(hits)} seconds={now() - begin:.1f}")
    say("PROBE DONE")
    return 0 if hits else 1


if __name__ == "__main__":
    raise SystemExit(main(__import__("sys").argv[1:]))
