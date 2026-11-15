r"""#528: the data the smaller locus test names, printed from one process.

The search (`issue528-locus-specimen.py`) returned one lattice whose non-identity reduction
isometries leave a base point that is not integral with a parameter quotient small enough to
enumerate: `U(2) + A2(2)`, 256 classes.  This probe prints, for the specimen the test will use,
the reduction's own basis and squares, the reflection it lifts, and the facts the test asserts --
so the test states measured data rather than a guess.
"""

import time
import traceback

from sage_extensions.all import *  # noqa: F401,F403

START = time.monotonic()


def now():
    return time.monotonic()


def say(*parts):
    print(f"[{now() - START:6.2f}s]", *parts, flush=True)


def main():
    lattice = Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)([[2, -1], [-1, 2]])
    labels = tuple(lattice.module_generating_set())
    say(f"lattice {lattice}, rank {lattice.module_rank()}, even {lattice.is_even()}")
    say(f"gram {lattice.gram_matrix()}")
    for coefficients in ((-2, 1, -2, -2), (-2, 1, -2, 0), (-2, 1, 0, -2)):
        marked = lattice.linear_combination({
            label: ZZ(coefficient)
            for label, coefficient in zip(labels, coefficients, strict=True)
            if coefficient
        })
        say(f"marked {marked}: q = {marked.q()}, divisibility {lattice.div(marked)}")
        try:
            subobject = lattice.primitive_isotropic_subobject(marked)
            reduction = subobject.isotropic_reduction()
        except Exception as error:  # noqa: BLE001
            say(f"  no reduction: {type(error).__name__}: {error}"[:160])
            continue
        reduction_labels = tuple(reduction.module_generating_set())
        say(f"  reduction rank {reduction.module_rank()}; basis {reduction_labels}")
        for label in reduction_labels:
            vector = reduction.module_generator(label)
            say(f"    basis vector {label}: q = {vector.q()}")
        square_two = [
            label for label in reduction_labels
            if reduction.module_generator(label).q() == ZZ(2)
        ]
        say(f"  basis vectors of square two: {square_two}")
        if not square_two:
            continue
        reflection = reduction.reflection(reduction.module_generator(square_two[0]))
        identity = reduction.Isom(reduction).identity()
        say(f"  reflection is not the identity: {reflection != identity}")
        torsor = reduction.rational_lifts(reduction, reflection)
        quotient = torsor.integral_parameter_quotient()
        say(
            f"  |P/mP| = {quotient.codomain().cardinality()}; "
            f"period m = {torsor.integral_parameter_period()}"
        )
        begin = now()
        base = torsor.base_point()
        say(f"  base point built in {now() - begin:.2f} s")
        begin = now()
        restricted = base.integral_restriction(lattice, lattice)
        say(f"  base point integral restriction: {restricted} ({now() - begin:.2f} s)")
        begin = now()
        answered = torsor.integral_base_point_or_none()
        say(f"  integral_base_point_or_none in {now() - begin:.2f} s")
        begin = now()
        answer = answered.integral_restriction(lattice, lattice)
        say(f"  the answered lift restricts in {now() - begin:.2f} s, isometry {answer in lattice.Isom(lattice)}")
        begin = now()
        reported = set(torsor.integral_parameter_classes())
        say(f"  integral_parameter_classes: {now() - begin:.2f} s")
        begin = now()
        inclusion = quotient.domain().inclusion()
        isometries = lattice.Isom(lattice)

        def lifts_integrally(residue) -> bool:
            parameter = inclusion(quotient.preimage(residue)).underlying_element()
            return torsor.parameterization()(parameter).integral_restriction(
                lattice, lattice
            ) in isometries

        enumerated = set(residue for residue in quotient.codomain() if lifts_integrally(residue))
        say(f"  every class enumerated in {now() - begin:.2f} s")
        zero = quotient.codomain().zero()
        say(
            f"  agree {reported == enumerated}; nonempty {bool(reported)}; "
            f"zero in reported {zero in reported}; zero in enumerated {zero in enumerated}; "
            f"whole {reported == set(quotient.codomain())}"
        )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException:  # noqa: BLE001
        traceback.print_exc()
        raise
