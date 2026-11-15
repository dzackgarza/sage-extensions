r"""The integral parameters of a marked-line lift are a union of transvection cosets.

A marked-line reduction lift is evaluated at additive coordinates by Eichler transvections
(Gritsenko--Hulek--Sankaran, arXiv:0810.1614, section 3.1, (4)--(5)), and its integral points
are the coordinates whose lift restricts to an isometry of the lattice.
`isotropic_lifts.IsotropicReductionLiftTorsors.integral_parameter_classes` answers with the
classes of that locus in `P/mP`.

Its first cheap form reported the kernel of `a + mP |-> s(a) + L'` and justified it by
"`E_{f,x}` is integral exactly when `x` lies in `L'`".  That converse needs a `y` with
`b(y,f) = 1`, and a primitive isotropic vector only supplies `b(f, L') = d Z` for the
divisibility `d = div(f)`.  When `d > 1` there are integral transvections whose parameter is
not a lattice vector -- at `d = 2` the parameter `f/2` gives the identity -- so the kernel is a
proper subset of the locus and the call loses integral lifts.

What holds for every base point and every divisibility is that the locus is a union of cosets
of that kernel `K`: the sections land in the perpendicular of the marked isotropic vector, so
`phi(a + k) = E_{f,s(k)} phi(a)` with `E_{f,s(k)}` integral and integrally invertible.  Each
test below therefore compares the returned locus with the classes that lift integrally,
decided by the lift itself over *every* class of `P/mP`.  The controls are small enough for
that enumeration; the `T_Co` row that needs the cheap form is
`test_the_coble_lattice_line_orbit_call_returns.sage`.

The two sides are compared as Python sets of the module's own classes, because a set literal
in this session is an owned set and an owned set is not equal to a Python one.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _marked_line_lift_torsor(lattice, marked, reduction_isometry=None):
    r"""The lift torsor of a reduction of ``lattice`` at the line spanned by ``marked``.

    ``marked`` must be a primitive isotropic vector of ``lattice``, so that its line is a
    rank-one primitive totally isotropic subobject and the reduction along it is defined.
    ``reduction_isometry`` is an isometry of that reduction, by default its identity; a
    nontrivial one lifts to a base point that is not the identity of the lattice, which is
    the case the locus' per-class test has to answer for.
    """
    reduction = lattice.primitive_isotropic_subobject(marked).isotropic_reduction()
    isometry = reduction.Isom(reduction).identity() if reduction_isometry is None else reduction_isometry
    return reduction.rational_lifts(reduction, isometry)


def _reduction_transvection(lattice, marked):
    r"""A non-identity isometry of the reduction at ``marked``: an Eichler transvection.

    The reduction's basis carries an isotropic vector and a vector perpendicular to it, so the
    transvection ``t(e, a)`` of that pair is an isometry of the reduction that is not the
    identity.  Its lift's base point is not the identity either: it moves the marked line's
    complement, so the locus' per-class test is asked about parameters that do not fix the
    base point's images.
    """
    reduction = lattice.primitive_isotropic_subobject(marked).isotropic_reduction()
    labels = tuple(reduction.module_generating_set())
    basis_vector = {label: reduction.module_generator(label) for label in labels}
    zero = reduction.base_ring().zero()
    direction_label = next(
        label for label in labels
        if basis_vector[label].q() == zero and basis_vector[label] != reduction.zero()
    )
    partner_label = next(
        label for label in labels
        if label != direction_label and basis_vector[direction_label].b(basis_vector[label]) == zero
    )
    return reduction.eichler_transvection(basis_vector[direction_label], basis_vector[partner_label])


def _first_basis_line(lattice):
    r"""The first basis vector of ``lattice``, which is the marked line of the small controls.

    The first basis vector of each control whose marked vector is not given below is a
    primitive isotropic vector.
    """
    labels = tuple(lattice.module_generating_set())
    return lattice.module_generator(labels[0])


def _classes_that_lift_integrally(lattice, torsor):
    r"""The classes of ``P/mP`` whose own parameter lift restricts to an isometry of ``lattice``.

    This is the expensive per-class test: build the lift at that parameter and ask for its
    integral restriction.  Every class of the finite parameter quotient is tested, which is
    affordable exactly on the controls: the ``T_Co`` module has 262144 of them.
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


def _assert_locus_is_the_integral_classes(lattice, divisibility, marked=None) -> None:
    r"""The reported locus is exactly the classes of ``P/mP`` that lift integrally.

    ``marked`` is the primitive isotropic vector whose line is reduced at; without it the
    first basis line is taken, which is what the small controls mark.
    """
    if marked is None:
        marked = _first_basis_line(lattice)
    torsor = _marked_line_lift_torsor(lattice, marked)
    integral_classes = _classes_that_lift_integrally(lattice, torsor)
    zero = torsor.integral_parameter_quotient().codomain().zero()

    reported = set(torsor.integral_parameter_classes())

    assert lattice.div(marked) == divisibility
    assert reported == integral_classes
    # The identity lift is integral and its parameter is the zero class, so neither side is
    # empty: the comparison above is not the comparison of two empty sets.
    assert zero in integral_classes
    assert zero in reported


def test_the_locus_of_divisibility_one_controls_is_every_class_that_lifts() -> None:
    r"""On `U + <2>` and `U + U + <2>` the marked line has divisibility one."""
    controls = (
        Lattices(ZZ)("U") + Lattices(ZZ)([[2]]),
        Lattices(ZZ)("U") + Lattices(ZZ)("U") + Lattices(ZZ)([[2]]),
    )
    for lattice in controls:
        _assert_locus_is_the_integral_classes(lattice, 1)


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
        _assert_locus_is_the_integral_classes(lattice, 2)


def test_the_locus_of_a_divisibility_two_control_with_a_nontrivial_kernel_is_every_class() -> None:
    r"""On `U(2) + U(2) + <2>` the reported locus is the integral classes, not more.

    This is the smallest control where the class coordinates of the locus decide the
    answer: the section's coordinate matrix has Smith invariants one, its saturation
    differs from the parameter lattice in every coordinate, and the transvection kernel
    `K = {a : s(a) in L'}` has a proper complement inside the locus.  Read with the
    coordinate change inverted -- `a = V^-1 u` instead of `a = V u` for the Smith
    decomposition `U (N A) V = D` -- the same code reported all 64 classes of `P/mP`
    while only 32 of them lift integrally (#405), so the comparison below is what pins
    the coset reading and not only the divisibility of the marked vector.
    """
    lattice = (
        Lattices(ZZ)([[0, 2], [2, 0]])
        + Lattices(ZZ)([[0, 2], [2, 0]])
        + Lattices(ZZ)([[2]])
    )

    _assert_locus_is_the_integral_classes(lattice, 2)


def test_the_locus_at_a_non_identity_reduction_is_every_class_that_lifts() -> None:
    r"""On `U(2) + U(2) + <2>` at a reduction isometry that is not the identity.

    The other tests reduce at the identity isometry of the reduction, where the base point of
    the lift is the identity of the lattice and its coordinate matrix is the identity.  That
    makes every reading of the lift's integrality agree, so it cannot separate the lift's own
    matrix from a transposed reading of it -- the failure the review of `0a55452cfa` reported,
    where `base_images` was filled by rows and the product `T * base_images` was read as the
    lift's matrix.

    This test answers the same question at an Eichler transvection of the reduction, whose
    lift's base point is not the identity and whose coordinate matrix is not symmetric: the
    locus' classes are exactly the classes of `P/mP` whose lift restricts to an isometry of the
    lattice, against the lift's own `integral_restriction`.
    """
    lattice = (
        Lattices(ZZ)([[0, 2], [2, 0]])
        + Lattices(ZZ)([[0, 2], [2, 0]])
        + Lattices(ZZ)([[2]])
    )
    marked = _first_basis_line(lattice)
    isometry = _reduction_transvection(lattice, marked)
    reduction = lattice.primitive_isotropic_subobject(marked).isotropic_reduction()
    # The isometry is not the identity: the test is not the identity case again.
    assert isometry != reduction.Isom(reduction).identity()
    torsor = _marked_line_lift_torsor(lattice, marked, reduction_isometry=isometry)
    integral_classes = _classes_that_lift_integrally(lattice, torsor)
    reported = set(torsor.integral_parameter_classes())
    quotient = torsor.integral_parameter_quotient()

    assert reported == integral_classes
    # The comparison is neither of two empty sets nor of the whole parameter quotient.
    zero = quotient.codomain().zero()
    assert zero in integral_classes
    assert zero in reported
    assert reported != set(quotient.codomain())


def test_the_locus_of_a_divisibility_four_control_is_every_class_that_lifts() -> None:
    r"""On `U(4) + <2>` the marked line has divisibility four.

    Nothing in the criterion is special to `d = 2`: the locus is a union of cosets for every
    divisibility, so a lattice whose marked line is even less self-dual must agree as well.
    """
    lattice = Lattices(ZZ)([[0, 4], [4, 0]]) + Lattices(ZZ)([[2]])

    _assert_locus_is_the_integral_classes(lattice, 4)


def test_the_locus_of_a_section_with_unequal_smith_steps_is_every_class_that_lifts() -> None:
    r"""On `U + A3(2)` at a marked line of divisibility two the section's steps are `(4, 2, 2)`.

    The marked vector `-2e0 + 2e1 - e2 + 2e3 - e4` of `U + A3(2)` is primitive isotropic of
    divisibility two.  Its period is eight, and the section's coordinate matrix has Smith
    invariants `(1, 2, 2)` over the denominator four, so the saturation
    `S = {a : s(a) in L'}` is `V(4Z x 2Z x 2Z)` for a `V` that is not the identity.

    Reading the saturation as the cube `4Z x 2Z x 2Z` itself -- which is `S` only when the
    steps are all equal, as they are in every other control here -- reported 256 of the 512
    classes of `P/mP`, while every class of this control lifts integrally.  The comparison
    below is therefore what pins the kernel's reading through `V`, and not only the
    divisibility of the marked vector.
    """
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)([[4, 2, 0], [2, 4, 2], [0, 2, 4]])
    labels = tuple(lattice.module_generating_set())
    marked = lattice.linear_combination({
        label: ZZ(coefficient)
        for label, coefficient in zip(labels, (-2, 2, -1, 2, -1), strict=True)
    })

    _assert_locus_is_the_integral_classes(lattice, 2, marked=marked)


