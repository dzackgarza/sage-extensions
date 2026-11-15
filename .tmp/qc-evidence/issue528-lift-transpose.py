r"""#528: is the locus' matrix test the lift's matrix, or the transpose of the base point?

`_integral_parameter_cosets` (main `cff6a3a`) tests each class of the lift locus
by the matrix ``T * base_images``: ``T`` is the Eichler transvection's column
matrix at the class' section, and ``base_images`` is meant to carry the base
point's images of the source generators, one per **column**.  The images are
collected source-major and handed to ``matrix(QQ, n_target, n_source, entries)``,
which fills **by rows**, so the matrix holds one image per row: it is the
transpose of what the product needs, and ``T * base_images`` is ``T * B^t``
where the lift's matrix is ``T * B``.  On a square control the product is
dimensionally legal and the two agree only when ``B`` is symmetric.

The identity reduction isometry cannot see this, because its base point is
integral.  Every test of the locus and the previous round's equivalence probe
used the identity; this probe runs the control ``U(2) + U(2) + <2>`` at a
reduction isometry whose base point is **not** integral, found by a bounded
search over the reduction's own isometries, and compares three readings per
class of the parameter quotient:

* **the truth**: the lift ``parameterization()(a)`` asked for its own
  ``integral_restriction(L, L)``;
* **the reported locus**: the classes in ``integral_parameter_classes()``;
* **the matrix reading**, computed here twice by hand: ``T * B^t`` (what the
  source writes) and ``T * B`` (the same reading with the images in columns).

Nothing in the library changes, and no number is taken from a time: the probe
prints counts of agreement and disagreement.

    sage -python <this file>
"""

import time

from sage.rings.integer_ring import ZZ as SageZZ
from sage.matrix.constructor import matrix as sage_matrix
from sage.rings.rational_field import QQ as SageQQ

from sage_extensions.all import *  # noqa: F401,F403

START = time.monotonic()


def say(*parts):
    print(f"[{time.monotonic() - START:7.1f}s]", *parts, flush=True)


def _signed_permutations(lattice):
    r"""The non-identity signed permutations of the basis that preserve the form."""
    from itertools import permutations, product

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
                found.append((f"signed permutation {signs} over {permutation}", candidate))
    return found


def _transvections(lattice):
    r"""The non-identity Eichler transvections of the lattice at its isotropic basis vectors."""
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
                found.append((f"Eichler transvection t({direction_label}, {partner_label})", candidate))
    return found


def matrix_reading(torsor, parameter, transpose):
    r"""Whether the class' lift matrix is integral and unimodular, by one of the two readings."""
    base = torsor.base_point()
    rational_source = base.domain()
    rational_target = base.codomain()
    source_labels = tuple(torsor.source_reduction().isotropic_embedding().codomain().module_generating_set())
    target_labels = tuple(torsor.target_reduction().isotropic_embedding().codomain().module_generating_set())
    columns = [
        rational_target.rational_coordinates(base(rational_source.module_generator(label))).list()
        for label in source_labels
    ]
    if transpose:
        base_images = sage_matrix(SageQQ, len(target_labels), len(source_labels),
                                  [entry for column in columns for entry in column])
    else:
        base_images = sage_matrix(SageQQ, len(target_labels), len(source_labels), columns).transpose()
    transvection = rational_target._eichler_transvection_column_matrix(
        torsor._target_witt.isotropic_vector(),
        torsor._target_section(parameter),
    )
    images = transvection * base_images
    if any(entry.denominator() != 1 for entry in images.list()):
        return False
    return int(sage_matrix(SageZZ, [[int(entry) for entry in row] for row in images.rows()]).determinant()) in (1, -1)


def base_point_is_integral(torsor):
    r"""Whether the *base point* itself restricts integrally, not whether some lift does.

    ``integral_base_point_or_none`` answers the second question: it returns the base
    point when that is integral and otherwise searches the locus.  The matrix test's
    domain is the first question, so it is asked here directly.
    """
    lattice = torsor.source_reduction().isotropic_embedding().codomain()
    return torsor.base_point().integral_restriction(lattice, lattice) is not None


def base_matrix(torsor):
    r"""The base point's coordinate matrix, images in columns, as `_lift_at` composes them."""
    base = torsor.base_point()
    rational_source = base.domain()
    rational_target = base.codomain()
    source_labels = tuple(torsor.source_reduction().isotropic_embedding().codomain().module_generating_set())
    target_labels = tuple(torsor.target_reduction().isotropic_embedding().codomain().module_generating_set())
    columns = [
        rational_target.rational_coordinates(base(rational_source.module_generator(label))).list()
        for label in source_labels
    ]
    return sage_matrix(SageQQ, len(target_labels), len(source_labels), columns), source_labels, target_labels


def lift_matrix(torsor, parameter, source_labels, target_labels):
    r"""The lift's own matrix at this parameter: its images of the source generators, in columns."""
    lift = torsor.parameterization()(parameter)
    rational_source = lift.domain()
    rational_target = lift.codomain()
    columns = [
        rational_target.rational_coordinates(lift(rational_source.module_generator(label))).list()
        for label in source_labels
    ]
    return sage_matrix(SageQQ, len(target_labels), len(source_labels), columns)


def integral_and_unimodular(images):
    r"""Whether the matrix is integral with determinant ``+-1``."""
    if images is None:
        return False
    if any(entry.denominator() != 1 for entry in images.list()):
        return False
    return int(sage_matrix(SageZZ, [[int(entry) for entry in row] for row in images.rows()]).determinant()) in (1, -1)


def comparison(torsor):
    r"""Per class: the truth, the reported locus, and both matrix readings, with the matrices."""
    quotient = torsor.integral_parameter_quotient()
    inclusion = quotient.domain().inclusion()
    isometries = lattice_isometries(torsor)
    base, source_labels, target_labels = base_matrix(torsor)
    reported = set(torsor.integral_parameter_classes())
    truth, transposed_set, columns_set = set(), set(), set()
    matrix_disagreements = 0
    membership_disagreements = 0
    transposed_matrix_disagreements = 0
    columns_matrix_disagreements = 0
    first_matrix_difference = None
    for residue in quotient.codomain():
        parameter = inclusion(quotient.preimage(residue)).underlying_element()
        lift = lift_matrix(torsor, parameter, source_labels, target_labels)
        integral = torsor.parameterization()(parameter).integral_restriction(*lattice_pair(torsor)) in isometries
        transvection = torsor.base_point().codomain()._eichler_transvection_column_matrix(
            torsor._target_witt.isotropic_vector(), torsor._target_section(parameter)
        )
        transposed = integral_and_unimodular(transvection * base.transpose())
        columns = integral_and_unimodular(transvection * base)
        if integral:
            truth.add(residue)
        if transposed:
            transposed_set.add(residue)
        if columns:
            columns_set.add(residue)
        if not (transposed == columns == integral == (residue in reported)):
            membership_disagreements += 1
        if transposed != columns:
            matrix_disagreements += 1
        if transvection * base.transpose() != lift:
            transposed_matrix_disagreements += 1
            if first_matrix_difference is None:
                first_matrix_difference = (residue, transvection * base.transpose(), lift)
        if transvection * base != lift:
            columns_matrix_disagreements += 1
    return {
        "classes": int(quotient.codomain().cardinality()),
        "truth": len(truth),
        "reported": len(reported),
        "transposed": len(transposed_set),
        "columns": len(columns_set),
        "reported_equals_truth": reported == truth,
        "transposed_equals_truth": transposed_set == truth,
        "columns_equals_truth": columns_set == truth,
        "membership_disagreements": membership_disagreements,
        "matrix_disagreements": matrix_disagreements,
        "T_times_Bt_differs_from_the_lift_matrix": transposed_matrix_disagreements,
        "T_times_B_differs_from_the_lift_matrix": columns_matrix_disagreements,
        "base_symmetric": base == base.transpose(),
        "base_point_integral": base_point_is_integral(torsor),
    }


def lattice_isometries(torsor):
    lattice = torsor.source_reduction().isotropic_embedding().codomain()
    return lattice.Isom(lattice)


def lattice_pair(torsor):
    lattice = torsor.source_reduction().isotropic_embedding().codomain()
    return lattice, lattice


def search(description, lattice, marked, products=True):
    r"""Every reduction isometry of this control, and the ones whose base point is not symmetric."""
    reduction = lattice.primitive_isotropic_subobject(marked).isotropic_reduction()
    simple = _signed_permutations(reduction) + _transvections(reduction)
    candidates = [(name, candidate) for name, candidate in simple]
    if products:
        candidates += [(f"({left_name}) * ({right_name})", left * right)
                       for left_name, left in simple for right_name, right in simple]
    say("")
    say(f"### {description}")
    say(f"  lattice {lattice}, divisibility of the marked vector {lattice.div(marked)}")
    asymmetric = []
    for name, candidate in candidates:
        try:
            torsor = reduction.rational_lifts(reduction, candidate)
            base, _source_labels, _target_labels = base_matrix(torsor)
        except Exception as error:  # noqa: BLE001 - a candidate the library refuses is reported
            say(f"    {name}: refused, {type(error).__name__}")
            continue
        if base != base.transpose() or not base_point_is_integral(torsor):
            asymmetric.append((name, torsor))
    say(f"  {len(candidates)} reduction isometries tried; {len(asymmetric)} have a base point whose "
        f"matrix is not symmetric or whose base point does not restrict integrally")
    for name, torsor in asymmetric[:3]:
        say("")
        say(f"=== {description}, at {name}")
        outcome = comparison(torsor)
        for key in ("classes", "truth", "reported", "transposed", "columns", "base_symmetric",
                    "reported_equals_truth", "transposed_equals_truth", "columns_equals_truth",
                    "membership_disagreements", "matrix_disagreements",
                    "T_times_Bt_differs_from_the_lift_matrix",
                    "T_times_B_differs_from_the_lift_matrix", "base_point_integral"):
            say(f"  {key:<26}{outcome[key]}")
    return asymmetric


def main():
    hyperbolic = Lattices(ZZ)([[0, 2], [2, 0]])
    threelinear = Lattices(ZZ)([[2]])
    controls = (
        ("U(2) + U(2) + <2>, marked at the first basis vector",
         hyperbolic + hyperbolic + threelinear, None),
        ("U + A3(2), marked at -2e0 + 2e1 - e2 + 2e3 - e4",
         Lattices(ZZ)("U") + Lattices(ZZ)([[4, 2, 0], [2, 4, 2], [0, 2, 4]]), (-2, 2, -1, 2, -1)),
    )
    for description, lattice, coefficients in controls:
        labels = tuple(lattice.module_generating_set())
        if coefficients is None:
            marked = lattice.module_generator(labels[0])
        else:
            marked = lattice.linear_combination({
                label: ZZ(coefficient)
                for label, coefficient in zip(labels, coefficients, strict=True)
            })
        try:
            search(description, lattice, marked)
        except Exception as error:  # noqa: BLE001 - one control failing does not stop the other
            say(f"  {description}: the search raised {type(error).__name__}: {error}")
    say("")
    say("PROBE DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
