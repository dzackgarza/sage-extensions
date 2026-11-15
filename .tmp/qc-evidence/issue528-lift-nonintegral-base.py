r"""#528: which small control has a reduction isometry whose base point is not integral?

The review of `0a55452cfa` says its matrix test `T * base_images` computes `T * B^t`
where the lift's matrix is `T * B`, and that "the answer changes exactly when the
base point is not integral".  A test of that change therefore needs a control whose
reduction isometry has a **non-integral base point** -- a lift of the reduction's
isometry that is not itself an isometry of the lattice.

This probe looks for one: over the small lattices the locus' own tests use, at the
marked line each test marks, over the reduction's signed permutations, its Eichler
transvections, and their pairwise products, it asks each lift torsor's own base point
for its integral restriction, and for every isometry whose base point fails it prints
the three readings per class of the parameter quotient: the lift's own
`integral_restriction`, the locus' reported classes, and both matrix readings.

    sage -python <this file>
"""

import time

from itertools import permutations, product

from sage.rings.integer_ring import ZZ as SageZZ
from sage.matrix.constructor import matrix as sage_matrix
from sage.rings.rational_field import QQ as SageQQ

from sage_extensions.all import *  # noqa: F401,F403

START = time.monotonic()


def say(*parts):
    print(f"[{time.monotonic() - START:7.1f}s]", *parts, flush=True)


def signed_permutations(lattice):
    labels = tuple(lattice.module_generating_set())
    generators = {label: lattice.module_generator(label) for label in labels}
    found = []
    for permutation in permutations(range(len(labels))):
        for signs in product((1, -1), repeat=len(labels)):
            if all(sign == 1 for sign in signs):
                continue
            images = {
                label: lattice.scalar_multiple(ZZ(signs[position]), generators[labels[permutation[position]]])
                for position, label in enumerate(labels)
            }
            candidate = lattice.Isom(lattice)(images)
            if all(
                candidate(generators[left]).b(candidate(generators[right])) == generators[left].b(generators[right])
                for left in labels
                for right in labels
            ):
                found.append((f"signs {signs} over {permutation}", candidate))
    return found


def transvections(lattice):
    labels = tuple(lattice.module_generating_set())
    zero = lattice.base_ring().zero()
    generators = {label: lattice.module_generator(label) for label in labels}
    found = []
    for direction_label in labels:
        direction = generators[direction_label]
        if direction.q() != zero or direction == lattice.zero():
            continue
        for partner_label in labels:
            partner = generators[partner_label]
            if direction.b(partner) != zero:
                continue
            candidate = lattice.eichler_transvection(direction, partner)
            if all(
                candidate(generators[left]).b(candidate(generators[right])) == generators[left].b(generators[right])
                for left in labels
                for right in labels
            ):
                found.append((f"t({direction_label}, {partner_label})", candidate))
    return found


def images_of(torsor, element, source_labels, target_labels, rational_source, rational_target):
    columns = [
        rational_target.rational_coordinates(element(rational_source.module_generator(label))).list()
        for label in source_labels
    ]
    return sage_matrix(SageQQ, len(target_labels), len(source_labels), columns)


def integral_and_unimodular(images):
    if any(entry.denominator() != 1 for entry in images.list()):
        return False
    return int(sage_matrix(SageZZ, [[int(entry) for entry in row] for row in images.rows()]).determinant()) in (1, -1)


def comparison(torsor, lattice, description):
    quotient = torsor.integral_parameter_quotient()
    inclusion = quotient.domain().inclusion()
    isometries = lattice.Isom(lattice)
    base = torsor.base_point()
    rational_source, rational_target = base.domain(), base.codomain()
    source_labels = tuple(lattice.module_generating_set())
    target_labels = tuple(lattice.module_generating_set())
    base_matrix = images_of(torsor, base, source_labels, target_labels, rational_source, rational_target)
    reported = set(torsor.integral_parameter_classes())
    truth, transposed_set, columns_set = set(), set(), set()
    matrix_differences = 0
    membership_differences = 0
    for residue in quotient.codomain():
        parameter = inclusion(quotient.preimage(residue)).underlying_element()
        lift = torsor.parameterization()(parameter)
        integral = lift.integral_restriction(lattice, lattice) in isometries
        transvection = rational_target._eichler_transvection_column_matrix(
            torsor._target_witt.isotropic_vector(), torsor._target_section(parameter)
        )
        transposed = integral_and_unimodular(transvection * base_matrix.transpose())
        columns = integral_and_unimodular(transvection * base_matrix)
        if integral:
            truth.add(residue)
        if transposed:
            transposed_set.add(residue)
        if columns:
            columns_set.add(residue)
        if not (transposed == columns == integral == (residue in reported)):
            membership_differences += 1
        lift_matrix = images_of(torsor, lift, source_labels, target_labels, lift.domain(), lift.codomain())
        if transvection * base_matrix != lift_matrix:
            matrix_differences += 1
    say(f"  === {description}")
    say(f"    classes {quotient.codomain().cardinality()}, truth {len(truth)}, "
        f"reported {len(reported)}, T*B^t {len(transposed_set)}, T*B {len(columns_set)}")
    say(f"    reported == truth {reported == truth}, T*B^t == truth {transposed_set == truth}, "
        f"T*B == truth {columns_set == truth}")
    say(f"    classes where the readings disagree {membership_differences}; "
        f"classes where T*B is not the lift's matrix {matrix_differences}")
    return membership_differences


def main():
    hyperbolic = Lattices(ZZ)([[0, 2], [2, 0]])
    controls = (
        ("U + <2>", Lattices(ZZ)("U") + Lattices(ZZ)([[2]]), None),
        ("U + U + <2>", Lattices(ZZ)("U") + Lattices(ZZ)("U") + Lattices(ZZ)([[2]]), None),
        ("U(2) + <2>", hyperbolic + Lattices(ZZ)([[2]]), None),
        ("U(2) + U(2)", hyperbolic + hyperbolic, None),
        ("U(4) + <2>", Lattices(ZZ)([[0, 4], [4, 0]]) + Lattices(ZZ)([[2]]), None),
        ("U(2) + U(2) + <2>", hyperbolic + hyperbolic + Lattices(ZZ)([[2]]), None),
        ("U + A3(2) at -2e0 + 2e1 - e2 + 2e3 - e4",
         Lattices(ZZ)("U") + Lattices(ZZ)([[4, 2, 0], [2, 4, 2], [0, 2, 4]]), (-2, 2, -1, 2, -1)),
    )
    total_hits = 0
    for description, lattice, coefficients in controls:
        labels = tuple(lattice.module_generating_set())
        if coefficients is None:
            marked = lattice.module_generator(labels[0])
        else:
            marked = lattice.linear_combination({
                label: ZZ(coefficient)
                for label, coefficient in zip(labels, coefficients, strict=True)
            })
        reduction = lattice.primitive_isotropic_subobject(marked).isotropic_reduction()
        simple = signed_permutations(reduction) + transvections(reduction)
        candidates = list(simple) + [(f"({left_name}) * ({right_name})", left * right)
                                     for left_name, left in simple for right_name, right in simple]
        hits = []
        for name, candidate in candidates:
            try:
                torsor = reduction.rational_lifts(reduction, candidate)
                base = torsor.base_point()
                if base.integral_restriction(lattice, lattice) is None:
                    hits.append((name, torsor))
            except Exception as error:  # noqa: BLE001 - a refused candidate is reported
                del error
        say("")
        say(f"### {description}: rank {lattice.module_rank()}, divisibility {lattice.div(marked)}, "
            f"reduction rank {reduction.module_rank()}, {len(candidates)} isometries tried, "
            f"{len(hits)} with a base point that does not restrict integrally")
        total_hits += len(hits)
        for name, torsor in hits[:2]:
            comparison(torsor, lattice, f"{description} at {name}")
    say("")
    say(f"controls with a non-integral base point: {total_hits}")
    say("PROBE DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
