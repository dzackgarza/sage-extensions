r"""#528: does any lift torsor of `T_Co` have a base point that is not integral?

The small-lattice search reports where a non-integral base point is *not* found.
This probe reports the nearest case that is found: the issue's own lattice,
`T_Co`, at its primitive isotropic basis line `ep`, over the identity of the
reduction and over an Eichler transvection of it -- the two isometries the
locus' test file uses.  For each, the base point is asked for its integral
restriction, which is what `integral_base_point_or_none` asks first.

    sage -python <this file>
"""

import time

from sage_extensions.all import *  # noqa: F401,F403

START = time.monotonic()


def say(*parts):
    print(f"[{time.monotonic() - START:7.1f}s]", *parts, flush=True)


def main():
    lattice = NamedLattices.Tco
    labels = tuple(lattice.module_generating_set())
    vectors = {label: lattice.module_generator(label) for label in labels}
    isotropic = [label for label in labels if vectors[label].q() == lattice.base_ring().zero()]
    say(f"T_Co of rank {lattice.module_rank()}, isotropic basis vectors {isotropic}")
    for label in isotropic:
        marked = vectors[label]
        line = lattice.primitive_isotropic_subobject(marked)
        reduction = line.isotropic_reduction()
        identity = reduction.Isom(reduction).identity()
        say(f"line {label}: divisibility {lattice.div(marked)}, reduction rank "
            f"{reduction.module_rank()}")
        reduction_labels = tuple(reduction.module_generating_set())
        reduction_vectors = {key: reduction.module_generator(key) for key in reduction_labels}
        zero = reduction.base_ring().zero()
        # Short vectors of the reduction, one and two nonzero coordinates: the
        # reduction's isotropic directions are not among its basis vectors.
        short = []
        for position, key in enumerate(reduction_labels):
            for sign in (1, -1):
                pattern = {label: ZZ(0) for label in reduction_labels}
                pattern[key] = ZZ(sign)
                short.append((f"{sign}*{key}", reduction.linear_combination(pattern)))
        for first in range(len(reduction_labels)):
            for second in range(first + 1, len(reduction_labels)):
                left, right = reduction_labels[first], reduction_labels[second]
                for left_sign in (1, -1):
                    for right_sign in (1, -1):
                        pattern = {label: ZZ(0) for label in reduction_labels}
                        pattern[left] = ZZ(left_sign)
                        pattern[right] = ZZ(right_sign)
                        short.append(
                            (f"{left_sign}*{left}+{right_sign}*{right}",
                             reduction.linear_combination(pattern))
                        )
        say(f"    {len(short)} short vectors of the reduction")
        directions = [(name, vector) for name, vector in short if vector.q() == zero]
        say(f"    isotropic ones: {[name for name, _ in directions]}")
        transvection = None
        for direction_name, direction in directions:
            for partner_name, partner in short:
                if direction.b(partner) != zero:
                    continue
                candidate = reduction.eichler_transvection(direction, partner)
                if candidate != identity:
                    transvection = (f"transvection({direction_name},{partner_name})", candidate)
                    break
            if transvection is not None:
                break
        isometries = [("identity", identity)]
        if transvection is not None:
            isometries.append(transvection)
        else:
            say("    the reduction has no non-identity Eichler transvection here")
        for name, isometry in isometries:
            torsor = reduction.rational_lifts(reduction, isometry)
            base = torsor.base_point()
            integral = base.integral_restriction(lattice, lattice)
            say(f"    at the {name}: the base point is integral: {integral is not None}; "
                f"P/mP has {torsor.integral_parameter_quotient().codomain().cardinality()} classes")
    say("PROBE DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
