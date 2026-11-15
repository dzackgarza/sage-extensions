r"""#528: the smallest specimen of a lift whose base point is not integral.

`11806f8edf`'s new test decides, class by class over the whole parameter
quotient, that the reported integral lift locus is the set of classes whose own
parameter lift restricts to an isometry, at a reduction isometry that is not the
identity -- and it does so on `U(5) + U(5) + U(4)`, where a call takes 181--201 s
against the repository's 20 s test-call ceiling and its 60 s hang bound
(`pyproject.toml`, `suite_budget.TEST_CALL_CEILING`).  The test needs a
*smaller* specimen of the same situation, not a shorter test: a base point that
is not integral, a locus that is neither empty nor the whole quotient, and a
parameter quotient of a few hundred classes.

This probe searches for one and prints what each candidate costs, so the test
cites a measurement and not a guess.  For every (lattice, marked primitive
isotropic vector, reduction isometry) it reports:

  * the lattice's rank, the marked vector, its divisibility, and the rank of the
    reduction;
  * ``|P/mP|``, the number of classes of the integral parameter quotient;
  * whether the lift's base point restricts integrally (the property the test is
    about: at ``None`` the tortor's own cheap route cannot answer from it);
  * the time of the torsor's own ``integral_parameter_classes()`` and of the
    full class-by-class enumeration, and whether the two agree, whether the
    locus is nonempty, whether the zero class is in it, and whether it is the
    whole quotient.

The reduction isometries are the ones an integral reduction actually has: the
identity, negation, an Eichler transvection at a pair (isotropic, perpendicular)
of the reduction's basis, the reflection in a vector of square two when the
reduction has one, and the products of those with negation.  A candidate whose
class count is over ``BIG`` is not enumerated -- the point of the search is the
small ones -- and the whole probe stops listing new candidates at ``DEADLINE``
seconds.
"""

import sys
import time
import traceback
from itertools import product

from sage_extensions.all import *  # noqa: F401,F403

START = time.monotonic()
BIG = 2000
DEADLINE = 480.0


def now():
    return time.monotonic()


def say(*parts):
    print(f"[{now() - START:7.1f}s]", *parts, flush=True)


def lattices():
    """The small even lattices the search runs over, by their names."""
    return [
        ("U(2)+<2>", Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)([[2]])),
        ("U(2)+U(2)", Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)([[0, 2], [2, 0]])),
        (
            "U(2)+U(2)+<2>",
            Lattices(ZZ)([[0, 2], [2, 0]])
            + Lattices(ZZ)([[0, 2], [2, 0]])
            + Lattices(ZZ)([[2]]),
        ),
        ("U(4)+<2>", Lattices(ZZ)([[0, 4], [4, 0]]) + Lattices(ZZ)([[2]])),
        ("U(5)+U(4)", Lattices(ZZ)([[0, 5], [5, 0]]) + Lattices(ZZ)([[0, 4], [4, 0]])),
        (
            "U(5)+U(5)+U(4)",
            Lattices(ZZ)([[0, 5], [5, 0]])
            + Lattices(ZZ)([[0, 5], [5, 0]])
            + Lattices(ZZ)([[0, 4], [4, 0]]),
        ),
        ("U+U(2)", Lattices(ZZ)("U") + Lattices(ZZ)([[0, 2], [2, 0]])),
        ("U+<2>", Lattices(ZZ)("U") + Lattices(ZZ)([[2]])),
        ("U(2)+A2(2)", Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)([[2, -1], [-1, 2]])),
    ]


def marked_vectors(lattice, limit=4):
    """Small primitive isotropic vectors of ``lattice``, by increasing weight.

    The marked vector is what the lift reduces at, and the test needs one whose
    line is not divisibility one (a base point that is an isometry of the
    lattice has nothing to decide).  The scan is over coordinates of absolute
    value at most two, which is where the small controls live.
    """
    labels = tuple(lattice.module_generating_set())
    rank = len(labels)
    found = []
    for coefficients in product((-2, -1, 0, 1, 2), repeat=rank):
        if now() - START > DEADLINE - 150.0:
            return found
        if not any(coefficients):
            continue
        if rank > 1 and coefficients[0] == 0:
            # Same vector up to a smaller lattice: the scan reaches it there.
            continue
        vector = lattice.linear_combination({
            label: ZZ(coefficient)
            for label, coefficient in zip(labels, coefficients, strict=True)
            if coefficient
        })
        if vector.q() != ZZ(0):
            continue
        try:
            lattice.primitive_isotropic_subobject(vector)
        except Exception:  # noqa: BLE001 - a refused marking is a row of the table
            continue
        if any(vector == seen for seen in found):
            continue
        found.append(vector)
        if len(found) >= limit:
            break
    return found


def echo(owner, name, *arguments):
    """Call ``owner.name(*arguments)`` and return it with its wall time."""
    begin = now()
    value = getattr(owner, name)(*arguments)
    return value, now() - begin


def transvection_of(reduction):
    """An Eichler transvection of ``reduction``, or ``None`` where it has none."""
    labels = tuple(reduction.module_generating_set())
    basis = {label: reduction.module_generator(label) for label in labels}
    zero = reduction.base_ring().zero()
    direction = next(
        (label for label in labels
         if basis[label].q() == zero and basis[label] != reduction.zero()),
        None,
    )
    if direction is None:
        return None
    partner = next(
        (label for label in labels
         if label != direction and basis[direction].b(basis[label]) == zero),
        None,
    )
    if partner is None:
        return None
    return reduction.eichler_transvection(basis[direction], basis[partner])


def reflection_of(reduction):
    """The reflection in a vector of square two of ``reduction``, or ``None``."""
    labels = tuple(reduction.module_generating_set())
    for label in labels:
        vector = reduction.module_generator(label)
        if vector.q() == ZZ(2):
            return reduction.reflection(vector)
    return None


def isometries_of(reduction):
    """The reduction isometries the search tries, by name."""
    identity = reduction.Isom(reduction).identity()
    negation = reduction.Isom(reduction)({
        label: -reduction.module_generator(label)
        for label in reduction.module_generating_set()
    })
    candidates = [("identity", identity), ("negation", negation)]
    transvection = transvection_of(reduction)
    if transvection is not None:
        candidates.append(("transvection", transvection))
        candidates.append(("negation*transvection", negation * transvection))
    reflection = reflection_of(reduction)
    if reflection is not None:
        candidates.append(("reflection", reflection))
        candidates.append(("negation*reflection", negation * reflection))
    return candidates


def class_count(torsor):
    """``|P/mP|``, the number of classes of the integral parameter quotient."""
    codomain = torsor.integral_parameter_quotient().codomain()
    for name in ("cardinality",):
        method = getattr(codomain, name, None)
        if method is not None:
            try:
                return int(method())
            except (ValueError, TypeError):
                pass
    return len(tuple(codomain))


def all_classes_that_lift(lattice, torsor):
    """The classes whose own parameter lift restricts to an isometry of ``lattice``."""
    quotient = torsor.integral_parameter_quotient()
    inclusion = quotient.domain().inclusion()
    isometries = lattice.Isom(lattice)

    def lifts_integrally(residue) -> bool:
        parameter = inclusion(quotient.preimage(residue)).underlying_element()
        return torsor.parameterization()(parameter).integral_restriction(
            lattice, lattice
        ) in isometries

    return set(residue for residue in quotient.codomain() if lifts_integrally(residue))


def main():
    offenders = []
    for name, lattice in lattices():
        say(f"=== {name}: rank {lattice.module_rank()}, even {lattice.is_even()}")
        for marked in marked_vectors(lattice):
            try:
                reduction = lattice.primitive_isotropic_subobject(marked).isotropic_reduction()
            except Exception as error:  # noqa: BLE001 - a refusal is a row of the table
                say(f"  marked {marked}: no reduction ({type(error).__name__})")
                continue
            divisibility = int(lattice.div(marked))
            say(
                f"  marked {marked}: divisibility {divisibility}, "
                f"reduction rank {reduction.module_rank()}"
            )
            for kind, isometry in isometries_of(reduction):
                if now() - START > DEADLINE:
                    say("DEADLINE reached; the table below is what was measured")
                    return report(offenders)
                label = f"{name} | div {divisibility} | {kind}"
                try:
                    torsor, build = echo(
                        reduction, "rational_lifts", reduction, isometry
                    )
                    count = class_count(torsor)
                    base, base_time = echo(
                        torsor.base_point(), "integral_restriction", lattice, lattice
                    )
                except Exception as error:  # noqa: BLE001
                    say(f"    {kind:<22} refused: {type(error).__name__}: {error}"[:200])
                    continue
                note = (
                    f"    {kind:<22} |P/mP|={count:>7} build={build:6.2f}s "
                    f"base_point={base_time:6.2f}s integral={base is not None}"
                )
                if count > BIG or base is not None:
                    say(note)
                    continue
                try:
                    reported, reported_time = echo(torsor, "integral_parameter_classes")
                    reported = set(reported)
                    begin = now()
                    enumerated = all_classes_that_lift(lattice, torsor)
                    enumerated_time = now() - begin
                except Exception as error:  # noqa: BLE001
                    say(f"{note} -> enumeration refused {type(error).__name__}: {error}"[:220])
                    continue
                zero = torsor.integral_parameter_quotient().codomain().zero()
                agree = reported == enumerated
                say(
                    f"{note} locus={reported_time:6.2f}s "
                    f"enumerated={enumerated_time:6.2f}s agree={agree} "
                    f"nonempty={bool(reported)} zero_in={zero in reported} "
                    f"whole={reported == set(torsor.integral_parameter_quotient().codomain())}"
                )
                if agree and reported and zero not in reported:
                    offenders.append(
                        (
                            label,
                            count,
                            reported_time + enumerated_time,
                            marked,
                            kind,
                        )
                    )
                    say(f"      CANDIDATE {label} at {reported_time + enumerated_time:.2f} s")
    return report(offenders)


def report(offenders):
    say("")
    say("=== candidates: non-integral base point, nonempty locus, zero class absent ===")
    for label, count, spent, marked, kind in sorted(offenders, key=lambda row: row[2]):
        say(f"  {spent:7.2f}s |P/mP|={count:>6}  {label}  marked {marked}")
    if not offenders:
        say("  none")
    say(f"RESULT candidates={len(offenders)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException:  # noqa: BLE001
        traceback.print_exc()
        raise
