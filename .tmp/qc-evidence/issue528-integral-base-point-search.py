r"""#528: is there a small marked line whose reduction's lift has no integral base point?

The locus `integral_parameter_classes` exists for the case
`IsotropicReductionLiftTorsors.integral_base_point_or_none`
(`isotropic_lifts.py:768`) falls through: its rational base point is not an
integral isometry, so the integral lift has to be found among the parameter
classes.  The test file's seven controls all have an integral base point -- the
early return fires -- so none of them reaches the locus on that path.

This probe searches small lattices for the opposite specimen.  For each lattice
(orthogonal sums of the small blocks below, rank at most `max_rank`) it takes
the primitive isotropic vectors of a bounded coefficient pattern, builds the
marked-line reduction and the lift torsor at the identity of the reduction and
at an Eichler transvection of it (the file's own two isometries), and asks the
base point for its integral restriction.  A base point that is not integral is
the specimen wanted; the search stops at the first one and prints it with the
data needed to write it into a test.

    sage -python <this file> [max_rank=7] [box=2] [budget=600]
"""

import itertools
import math
import time

from sage_extensions.all import *  # noqa: F401,F403

START = time.monotonic()
MAX_RANK = 7
MIN_RANK = 1
BOX = 2
BUDGET = 600


def now():
    return time.monotonic()


def say(*parts):
    print(f"[{now() - START:7.1f}s]", *parts, flush=True)


def integer(value):
    """The Python integer behind a coefficient of this session's integer ring."""
    try:
        return int(value)
    except Exception:
        pass
    try:
        return int(ZZ(value))
    except Exception:
        pass
    from sage_extensions.categories.rings.ring_foundation import _engine_element, _owned_integers

    return int(_engine_element(_owned_integers(), value))


def gram_of(lattice):
    return [[integer(lattice.b(left, right))
             for right in lattice.module_generators()]
            for left in lattice.module_generators()]


BLOCKS = {
    "<1>": [[1]],
    "<-1>": [[-1]],
    "<3>": [[3]],
    "<-3>": [[-3]],
    "U(5)": [[0, 5], [5, 0]],
    "U(1)": [[0, 1], [1, 0]],
    "U(2)": [[0, 2], [2, 0]],
    "U(3)": [[0, 3], [3, 0]],
    "U(4)": [[0, 4], [4, 0]],
    "<2>": [[2]],
    "<-2>": [[-2]],
    "<4>": [[4]],
    "<-4>": [[-4]],
    "<6>": [[6]],
    "<-6>": [[-6]],
    "A2": [[2, -1], [-1, 2]],
    "A3": [[2, -1, 0], [-1, 2, -1], [0, -1, 2]],
    "D4": [[2, -1, 0, 0], [-1, 2, -1, 0], [0, -1, 2, -1], [0, 0, -1, 2]],
}


def lattice_from(rows):
    rank = sum(len(row) for row in rows)
    gram = [[0] * rank for _ in range(rank)]
    offset = 0
    for row in rows:
        size = len(row)
        for i in range(size):
            for j in range(size):
                gram[offset + i][offset + j] = row[i][j]
        offset += size
    return Lattices(ZZ)(gram)


def block_sums(min_rank, max_rank):
    """Every multiset of at most four blocks whose total rank lies in the slice."""
    names = tuple(BLOCKS)
    sums = []
    for size in (1, 2, 3, 4):
        for chosen in itertools.combinations_with_replacement(names, size):
            rank = sum(len(BLOCKS[name]) for name in chosen)
            if min_rank <= rank <= max_rank and any(name.startswith("U(") for name in chosen):
                sums.append(chosen)
    return tuple(sums)


def primitive(pattern):
    """Whether the coefficients have gcd one, i.e. the vector is primitive in a basis."""
    return math.gcd(*[abs(coefficient) for coefficient in pattern]) == 1


def patterns(rank, box):
    """Coefficient patterns: one or two nonzero entries, in ``-box..box``."""
    yield tuple([1] + [0] * (rank - 1))
    for position in range(rank):
        for value in range(-box, box + 1):
            if value == 0:
                continue
            pattern = [0] * rank
            pattern[position] = value
            yield tuple(pattern)
    for first, second in itertools.combinations(range(rank), 2):
        for left in range(-box, box + 1):
            if left == 0:
                continue
            for right in range(-box, box + 1):
                if right == 0:
                    continue
                pattern = [0] * rank
                pattern[first] = left
                pattern[second] = right
                yield tuple(pattern)


def candidate_vectors(lattice):
    labels = tuple(lattice.module_generating_set())
    rank = len(labels)
    seen = set()
    for pattern in patterns(rank, BOX):
        if pattern in seen:
            continue
        seen.add(pattern)
        if all(coefficient == 0 for coefficient in pattern) or not primitive(pattern):
            continue
        vector = lattice.linear_combination({
            label: ZZ(coefficient)
            for label, coefficient in zip(labels, pattern, strict=True)
            if coefficient
        })
        if vector.q() != lattice.base_ring().zero():
            continue
        yield pattern, vector


def reduction_isometries(lattice, marked):
    """The identity of the reduction and an Eichler transvection of it."""
    reduction = lattice.primitive_isotropic_subobject(marked).isotropic_reduction()
    yield "identity", reduction, reduction.Isom(reduction).identity()
    labels = tuple(reduction.module_generating_set())
    vectors = {label: reduction.module_generator(label) for label in labels}
    zero = reduction.base_ring().zero()
    directions = [label for label in labels if vectors[label].q() == zero]
    for direction in directions:
        for partner in labels:
            if partner == direction:
                continue
            if vectors[direction].b(vectors[partner]) != zero:
                continue
            isometry = reduction.eichler_transvection(vectors[direction], vectors[partner])
            if isometry == reduction.Isom(reduction).identity():
                continue
            yield "transvection", reduction, isometry
            return


def main(argv):
    global MAX_RANK, BOX, BUDGET, MIN_RANK
    for argument in argv:
        if argument.startswith("max_rank="):
            MAX_RANK = int(argument.split("=", 1)[1])
        elif argument.startswith("min_rank="):
            MIN_RANK = int(argument.split("=", 1)[1])
        elif argument.startswith("box="):
            BOX = int(argument.split("=", 1)[1])
        elif argument.startswith("budget="):
            BUDGET = int(argument.split("=", 1)[1])

    say(f"min_rank={MIN_RANK} max_rank={MAX_RANK} box={BOX} budget={BUDGET} s, "
        f"one search over every block sum")
    sums = block_sums(MIN_RANK, MAX_RANK)
    say(f"{len(sums)} lattices in the search space")
    tried = 0
    candidates = 0
    odd_lattices = 0
    lattices_done = 0
    completed = True
    hits = []
    begin = now()
    for chosen in sums:
        if now() - begin > BUDGET:
            say(f"budget spent after {tried} torsors, {lattices_done} of {len(sums)} lattices")
            completed = False
            break
        lattices_done += 1
        lattice = lattice_from([BLOCKS[name] for name in chosen])
        if not lattice.is_isotropic():
            continue
        # The locus is a union of transvection cosets only on an even lattice:
        # `_integral_parameter_cosets` asserts it (isotropic_lifts.py:473), so a
        # lattice whose transvections are not all integral is not a specimen here.
        if lattice.is_even() is not True:
            odd_lattices += 1
            continue
        for pattern, vector in candidate_vectors(lattice):
            if vector.q() != lattice.base_ring().zero():
                continue
            if lattice.div(vector) < 2:
                continue
            candidates += 1
            try:
                line = lattice.primitive_isotropic_subobject(vector)
                for kind, reduction, isometry in reduction_isometries(lattice, vector):
                    torsor = reduction.rational_lifts(reduction, isometry)
                    base = torsor.base_point()
                    integral = base.integral_restriction(lattice, lattice)
                    tried += 1
                    if integral is None:
                        hits.append((chosen, pattern, kind, integer(lattice.div(vector))))
                        say(f"HIT lattice {chosen} gram {gram_of(lattice)}")
                        say(f"    marked pattern {pattern} of divisibility {lattice.div(vector)}, "
                            f"reduction isometry {kind}")
                        say(f"    the base point is not integral: "
                            f"{base.integral_restriction(lattice, lattice) is None}")
                        say(f"    residue classes of P/mP: "
                            f"{torsor.integral_parameter_quotient().codomain().cardinality()}")
                        say(f"    the locus: {torsor.integral_parameter_classes().cardinality()}")
                        say(f"    {tried} torsors tried so far")
                        if len(hits) >= 3:
                            break
                    elif tried % 50 == 0:
                        say(f"  {tried} torsors tried, {len(hits)} hits")
            except Exception as error:
                failures = globals().setdefault("FAILURES", [])
                failures.append((chosen, pattern, repr(error)[:120]))
                if len(failures) <= 3:
                    say(f"  lattice {chosen} pattern {pattern}: raised {error!r}"[:200])
                continue
            if len(hits) >= 3:
                break
        if len(hits) >= 3:
            break
    say("")
    say(f"RESULT lattices={len(sums)} lattices_searched={lattices_done} "
        f"odd_lattices_skipped={odd_lattices} "
        f"marked_lines={candidates} torsors={tried} hits={len(hits)} completed={completed} "
        f"failures={len(globals().get('FAILURES', []))} seconds={now() - begin:.1f}")
    for chosen, pattern, kind, divisibility in hits:
        say(f"  {chosen} {pattern} {kind} div={divisibility}")
    say("PROBE DONE")
    return 0 if hits else 1


if __name__ == "__main__":
    raise SystemExit(main(__import__("sys").argv[1:]))
