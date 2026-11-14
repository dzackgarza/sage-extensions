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


def _marked_line_lift_torsor(lattice):
    r"""The first basis line of ``lattice`` and the lift torsor of its identity reduction.

    The first basis vector of each control below is a primitive isotropic vector, so its line
    is a rank-one primitive totally isotropic subobject and the reduction is defined.
    """
    labels = tuple(lattice.module_generating_set())
    marked = lattice.module_generator(labels[0])
    reduction = lattice.primitive_isotropic_subobject(marked).isotropic_reduction()
    return marked, reduction.rational_lifts(reduction, reduction.Isom(reduction).identity())


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


def _assert_locus_is_the_integral_classes(lattice, divisibility) -> None:
    r"""The reported locus is exactly the classes of ``P/mP`` that lift integrally."""
    marked, torsor = _marked_line_lift_torsor(lattice)
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


def test_the_locus_of_a_divisibility_four_control_is_every_class_that_lifts() -> None:
    r"""On `U(4) + <2>` the marked line has divisibility four.

    Nothing in the criterion is special to `d = 2`: the locus is a union of cosets for every
    divisibility, so a lattice whose marked line is even less self-dual must agree as well.
    """
    lattice = Lattices(ZZ)([[0, 4], [4, 0]]) + Lattices(ZZ)([[2]])

    _assert_locus_is_the_integral_classes(lattice, 4)
