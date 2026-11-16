r"""The integral parameters of a marked-line lift are a union of transvection cosets.

A marked-line reduction lift is evaluated at additive coordinates by Eichler transvections
(Gritsenko--Hulek--Sankaran, arXiv:0810.1614, section 3.1, (4)--(5)), and its integral points are
the coordinates whose lift restricts to an isometry of the lattice.
`isotropic_lifts.IsotropicReductionLiftTorsors.integral_parameter_classes` answers with the classes
of that locus in `P/mP`.

The sections land in the perpendicular of the marked isotropic vector, so `phi(a + k) =
E_{f,s(k)} phi(a)` with `E_{f,s(k)}` integral and integrally invertible for every `k` in
`K = {a : s(a) in L'}`: the locus is a union of cosets of `K`. Each test below therefore compares
the returned locus with the classes that lift integrally, decided by the lift itself over *every*
class of `P/mP`. The controls are small enough for that enumeration; the `T_Co` row that needs the
cheap form is `test_the_coble_lattice_line_orbit_call_returns.sage`.

The two sides are compared as Python sets of the module's own classes, because a set literal in
this session is an owned set and an owned set is not equal to a Python one.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _reduction_at(lattice, marked):
    r"""The reduction of ``lattice`` along the line spanned by the primitive isotropic ``marked``."""
    return lattice.primitive_isotropic_subobject(marked).isotropic_reduction()


def _marked_line_lift_torsor(reduction, reduction_isometry):
    r"""The lift torsor of ``reduction`` at its marked line, at ``reduction_isometry``.

    ``reduction`` is the reduction the caller built: it is a datum of the question, and the
    isometry being lifted and the torsor that lifts it are both objects over it.
    """
    return reduction.rational_lifts(reduction, reduction_isometry)


def _reduction_reflection(reduction):
    r"""A non-identity isometry of ``reduction``: the reflection in a basis vector of square two.

    The lift of a reduction isometry has a base point that is not an isometry of the lattice
    exactly when that isometry does not lift integrally.  On the control below the reduction is
    positive definite of rank two, with a basis vector of square two, so its reflection is the
    non-identity isometry at hand -- there is no isotropic vector of the reduction to transvect
    along.
    """
    labels = tuple(reduction.module_generating_set())
    root = next(
        label for label in labels if reduction.module_generator(label).q() == ZZ(2)
    )
    return reduction.reflection(reduction.module_generator(root))


def _classes_that_lift_integrally(lattice, torsor):
    r"""The classes of ``P/mP`` whose own parameter lift restricts to an isometry of ``lattice``.

    This is the per-class test the reported locus has to agree with: build the lift at that
    parameter and ask for its integral restriction.  Every class of the finite parameter quotient
    is tested, which is affordable exactly on the controls.
    """
    quotient = torsor.integral_parameter_quotient()
    inclusion = quotient.domain().inclusion()
    isometries = lattice.Isom(lattice)

    def lifts_integrally(residue) -> bool:
        parameter = inclusion(quotient.preimage(residue)).underlying_element()
        lift = torsor.parameterization()(parameter)
        return lift.integral_restriction(lattice, lattice) in isometries

    return set(
        residue for residue in quotient.codomain() if lifts_integrally(residue)
    )


def _assert_locus_is_the_integral_classes(lattice, marked, divisibility) -> None:
    r"""The reported locus is exactly the classes of ``P/mP`` that lift integrally.

    ``marked`` is the primitive isotropic vector whose line is reduced at, and ``divisibility``
    is its divisibility, asserted so that a test cannot silently run on a different line than the
    one it names.
    """
    reduction = _reduction_at(lattice, marked)
    torsor = _marked_line_lift_torsor(
        reduction, reduction.Isom(reduction).identity()
    )
    integral_classes = _classes_that_lift_integrally(lattice, torsor)
    zero = torsor.integral_parameter_quotient().codomain().zero()

    reported = set(torsor.integral_parameter_classes())

    assert lattice.div(marked) == divisibility
    assert reported == integral_classes
    # The identity lift is integral and its parameter is the zero class, so neither side is
    # empty: the comparison above is not the comparison of two empty sets.
    assert zero in integral_classes
    assert zero in reported


def _first_basis_vector(lattice):
    r"""The first basis vector of ``lattice``, which is the marked vector of each control.

    The first basis vector of every control that goes through
    :func:`_assert_locus_is_the_integral_classes` is a primitive isotropic vector, and each of
    those tests marks the line it spans.
    """
    labels = tuple(lattice.module_generating_set())
    return lattice.module_generator(labels[0])


def test_the_locus_of_divisibility_one_controls_is_every_class_that_lifts() -> None:
    r"""On `U + <2>` and `U + U + <2>` the marked line has divisibility one."""
    controls = (
        Lattices(ZZ)("U") + Lattices(ZZ)([[2]]),
        Lattices(ZZ)("U") + Lattices(ZZ)("U") + Lattices(ZZ)([[2]]),
    )
    for lattice in controls:
        _assert_locus_is_the_integral_classes(lattice, _first_basis_vector(lattice), 1)


def test_the_locus_of_the_divisibility_two_controls_is_every_class_that_lifts() -> None:
    r"""On `U(2) + <2>` and `U(2) + U(2)` the marked line has divisibility two.

    These are the specimens where the kernel of `a + mP |-> s(a) + L'` is not the locus: `f/2`
    gives an integral transvection, so classes outside the kernel lift integrally as well.
    """
    controls = (
        Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)([[2]]),
        Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)([[0, 2], [2, 0]]),
    )
    for lattice in controls:
        _assert_locus_is_the_integral_classes(lattice, _first_basis_vector(lattice), 2)


def test_the_locus_of_a_divisibility_two_control_with_a_nontrivial_kernel_is_every_class() -> None:
    r"""On `U(2) + U(2) + <2>` the reported locus is the integral classes, not more.

    This is the smallest control where the class coordinates of the locus decide the answer: the
    section's coordinate matrix has Smith invariants one, its saturation differs from the
    parameter lattice in every coordinate, and the transvection kernel `K = {a : s(a) in L'}` has
    a proper complement inside the locus, so a reading of the locus that loses the coset structure
    reports classes that do not lift.
    """
    lattice = (
        Lattices(ZZ)([[0, 2], [2, 0]])
        + Lattices(ZZ)([[0, 2], [2, 0]])
        + Lattices(ZZ)([[2]])
    )

    _assert_locus_is_the_integral_classes(lattice, _first_basis_vector(lattice), 2)


def test_the_locus_at_a_non_integral_base_point_is_every_class_that_lifts() -> None:
    r"""On `U(2) + A2` at the reflection in a square-two vector of the reduction at `-2e_0 + e_1 - 2e_3`.

    The marked vector `-2e_0 + e_1 - 2e_3` of `U(2) + A2` is primitive isotropic of divisibility
    two, its reduction is the rank-two lattice with basis of squares two and two, and the lift of
    that reduction's reflection is not an isometry of the lattice.  What this test decides: the
    base point does not restrict integrally, so `integral_base_point_or_none` cannot answer from it
    and has to walk the locus; the lift it answers with restricts integrally; the reported locus is
    exactly the classes of `P/mP` whose own parameter lift restricts to an isometry of the lattice,
    decided class by class over the whole parameter quotient against the lift's own
    `integral_restriction`; and the locus is neither empty nor the whole quotient, with the zero
    class -- the base point's own parameter -- on neither side.
    """
    lattice = Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)([[2, -1], [-1, 2]])
    labels = tuple(lattice.module_generating_set())
    marked = lattice.linear_combination({
        label: ZZ(coefficient)
        for label, coefficient in zip(labels, (-2, 1, 0, -2), strict=True)
        if coefficient
    })
    reduction = _reduction_at(lattice, marked)
    isometry = _reduction_reflection(reduction)
    torsor = _marked_line_lift_torsor(reduction, isometry)
    quotient = torsor.integral_parameter_quotient()

    # The isometry is not the identity, so this is not the identity case again, and the base point
    # it lifts to is not integral, so the locus is consulted rather than bypassed.
    assert isometry != reduction.Isom(reduction).identity()
    assert lattice.div(marked) == 2
    assert torsor.base_point().integral_restriction(lattice, lattice) is None
    answered = torsor.integral_base_point_or_none()
    assert answered.integral_restriction(lattice, lattice) in lattice.Isom(lattice)

    integral_classes = _classes_that_lift_integrally(lattice, torsor)
    reported = set(torsor.integral_parameter_classes())
    zero = quotient.codomain().zero()

    assert reported == integral_classes
    # Neither side is empty, neither is the whole quotient, and at a base point that is not
    # integral the zero parameter is on neither side.
    assert integral_classes
    assert zero not in integral_classes
    assert zero not in reported
    assert reported != set(quotient.codomain())


def test_the_locus_of_a_divisibility_four_control_is_every_class_that_lifts() -> None:
    r"""On `U(4) + <2>` the marked line has divisibility four.

    Nothing in the criterion is special to `d = 2`: the locus is a union of cosets for every
    divisibility, so a lattice whose marked line is even less self-dual must agree as well.
    """
    lattice = Lattices(ZZ)([[0, 4], [4, 0]]) + Lattices(ZZ)([[2]])

    _assert_locus_is_the_integral_classes(lattice, _first_basis_vector(lattice), 4)


def test_the_locus_of_a_section_with_unequal_smith_steps_is_a_proper_subset() -> None:
    r"""On `U(2) + A2` at the marked line `e_0 - 2e_1 - 2e_2 - 2e_3` the steps are `(8, 4)`.

    The section's coordinate matrix has steps `(8, 4)` over the period sixteen, so its
    saturation is read through a `V` that is not the identity, and the kernel is a proper
    subgroup of `P/mP`.  Sixteen of the 256 classes of `P/mP` lift, so this is the control
    that states both directions of the comparison: a reading that loses a class of the
    locus and a reading that admits a class whose own lift is not integral are both wrong
    here.  The base point is integral, so the zero class is in the locus.
    """
    lattice = Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)([[2, -1], [-1, 2]])
    labels = tuple(lattice.module_generating_set())
    marked = lattice.linear_combination({
        label: ZZ(coefficient)
        for label, coefficient in zip(labels, (1, -2, -2, -2), strict=True)
    })
    reduction = _reduction_at(lattice, marked)
    torsor = _marked_line_lift_torsor(
        reduction, reduction.Isom(reduction).identity()
    )
    quotient = torsor.integral_parameter_quotient()

    assert lattice.div(marked) == 2
    integral_classes = _classes_that_lift_integrally(lattice, torsor)
    reported = set(torsor.integral_parameter_classes())

    assert reported == integral_classes
    # Neither side is empty and neither is the whole parameter quotient: the locus is a
    # proper subset of `P/mP` here, so the comparison above decides both directions.
    assert integral_classes
    assert reported != set(quotient.codomain())
    # The base point is integral, so the zero parameter -- its own parameter -- lifts.
    zero = quotient.codomain().zero()
    assert zero in integral_classes
    assert zero in reported


def test_the_locus_of_a_section_with_unequal_smith_steps_is_every_class_that_lifts() -> None:
    r"""On `U + A3(2)` at a marked line of divisibility two the section's steps are `(4, 2, 2)`.

    The marked vector `-2e0 + 2e1 - e2 + 2e3 - e4` of `U + A3(2)` is primitive isotropic of
    divisibility two.  Its period is eight, and the section's coordinate matrix has Smith
    invariants `(1, 2, 2)` over the denominator four, so the saturation `S = {a : s(a) in L'}` is
    `V(4Z x 2Z x 2Z)` for a `V` that is not the identity: the kernel is read through `V`, which is
    what the comparison below pins, and not only the divisibility of the marked vector.
    """
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)([[4, 2, 0], [2, 4, 2], [0, 2, 4]])
    labels = tuple(lattice.module_generating_set())
    marked = lattice.linear_combination({
        label: ZZ(coefficient)
        for label, coefficient in zip(labels, (-2, 2, -1, 2, -1), strict=True)
    })

    _assert_locus_is_the_integral_classes(lattice, marked, 2)
