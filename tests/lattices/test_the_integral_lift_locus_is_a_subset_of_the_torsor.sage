r"""The integral lift locus is the subset of the torsor its parameter's residue class cuts out.

The integral lifts of a marked-line reduction map are ``T_Z = phi(r^{-1}(C))``: ``r`` the
residue map of the parameter quotient, ``C`` the finite residue locus
(`isotropic_lifts.IsotropicReductionLiftTorsors.integral_parameter_classes`), and ``phi``
the parameterization of the rational lift torsor ``T``.  ``r`` is onto and ``phi`` is a
bijection onto ``T``, so ``T_Z`` is a *subset of the torsor*: the lifts whose parameter
class lies in ``C``.

That is the presentation, and it is what these tests pin: the two facts a subset of ``T``
owes.  A locus is a subset of the set it lies in, so ``T_Z`` carries ``T``'s inclusion.  And
membership is the class test, asked of every point of ``T``: ``phi`` is a bijection onto
``T``, so a lift whose parameter is not in ``P`` is a point of ``T`` all the same, and it is
not a member.  An empty residue locus gives the empty subset of ``T``, which is the least
point of ``T``'s power set, decided empty by its construction and not by a search of ``T``.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _reduction_at(lattice, marked):
    r"""The reduction of ``lattice`` along the line spanned by the primitive isotropic ``marked``."""
    return lattice.primitive_isotropic_subobject(marked).isotropic_reduction()


def _marked_line_lift_torsor(reduction, reduction_isometry):
    r"""The lift torsor of ``reduction`` at its marked line, at ``reduction_isometry``."""
    return reduction.rational_lifts(reduction, reduction_isometry)


def _reduction_reflection(reduction):
    r"""A non-identity isometry of ``reduction``: the reflection in a basis vector of square two."""
    labels = tuple(reduction.module_generating_set())
    root = next(
        label for label in labels if reduction.module_generator(label).q() == ZZ(2)
    )
    return reduction.reflection(reduction.module_generator(root))


def _lift_at_class(torsor, residue):
    r"""The lift ``phi(a)`` of the parameter ``a`` whose class in ``P/mP`` is ``residue``.

    The class is read back to a parameter by the quotient's own section and evaluated by
    the torsor's parameterization, so the lift is the one the locus discusses and not a
    second construction of it.
    """
    quotient = torsor.integral_parameter_quotient()
    parameter = quotient.domain().inclusion()(
        quotient.preimage(residue)
    ).underlying_element()
    return torsor.parameterization()(parameter)


def _non_integral_base_point_control():
    r"""``U(2) + A2`` at a marked line of divisibility two, lifting a reflection.

    The marked vector ``-2e_0 + e_1 - 2e_3`` is primitive isotropic of divisibility two,
    its reduction is the rank-two lattice with basis of squares two and two, and the lift
    of that reduction's reflection is not an isometry of the lattice: the torsor's base
    point lies outside the integral locus, so the locus is a proper subset of the torsor
    and has points besides the one the base point would supply.
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
    return lattice, marked, reduction, _marked_line_lift_torsor(reduction, isometry)


def test_the_integral_locus_is_a_subset_of_its_torsor() -> None:
    r"""``T_Z`` has the inclusion of a subset of ``T``, into the torsor itself."""
    lattice, marked, reduction, torsor = _non_integral_base_point_control()
    locus = torsor.integral_lift_locus()

    assert lattice.div(marked) == 2
    assert locus.inclusion().codomain() == torsor
    # A subset of a set is a set of that set's points, and the empty set is not the
    # answer here: this locus has a lift.
    assert locus.is_empty() is False


def test_the_locus_is_membership_in_the_residue_class() -> None:
    r"""A lift is in ``T_Z`` exactly when its parameter's class lies in the residue locus.

    Both directions are decided on lifts the test builds: the classes of ``C`` itself give
    members, and the torsor's own base point -- whose parameter is the zero class, outside
    ``C`` at this specimen -- does not.
    """
    lattice, marked, reduction, torsor = _non_integral_base_point_control()
    locus = torsor.integral_lift_locus()
    classes = tuple(torsor.integral_parameter_classes())
    zero = torsor.integral_parameter_quotient().codomain().zero()

    assert zero not in classes
    assert locus.is_parent_of(torsor.base_point()) is False
    for residue in classes:
        assert locus.is_parent_of(_lift_at_class(torsor, residue)) is True
    # The lift the torsor answers with when asked for an integral point is a member, and
    # admitting it into the locus is asking the same question once more.
    answered = torsor.integral_base_point()
    assert locus.is_parent_of(answered) is True
    assert locus(answered) == answered


def test_a_parameter_outside_the_integral_lattice_is_not_a_member() -> None:
    r"""Membership answers for a lift of ``T`` whose parameter is not in ``P``.

    ``phi`` is a bijection onto ``T``, so a parameter outside the integral
    parameter lattice still names a lift of the torsor.  That lift is not an
    integral isometry of the lattice, and membership in ``T_Z`` is the question
    that says so -- the locus is a subset of ``T``, not a set that refuses the
    points of ``T`` outside it.
    """
    lattice, marked, reduction, torsor = _non_integral_base_point_control()
    locus = torsor.integral_lift_locus()
    parameters = torsor.parameter_space()
    labels = tuple(parameters.module_generating_set())
    parameter = parameters.linear_combination({labels[0]: QQ(1) / QQ(7)})
    outside = torsor.parameterization()(parameter)

    assert outside.integral_restriction(lattice, lattice) is None
    assert locus.is_parent_of(outside) is False
    assert locus.is_parent_of(torsor.integral_base_point()) is True


def test_an_empty_residue_locus_gives_the_empty_subset_of_the_torsor() -> None:
    r"""``T_Z`` is empty exactly when ``C`` is, and it is then the empty subset of ``T``.

    ``U``'s and ``U(2)``'s marked null lines both reduce to rank zero, but no integral
    isometry joins the ambient lattices, whose determinants differ, so the residue locus is
    empty and so is the integral locus -- a decision the locus has to make for itself,
    since a subset of an infinite torsor cannot be emptied by enumeration.  The empty
    subset of a set is the least point of its power set, and that is the object the empty
    locus is: a point of ``P(T)``, carrying ``T``'s inclusion, admitting no point of ``T``.
    """
    source = Lattices(ZZ)("U")
    target = Lattices(ZZ)([[0, 2], [2, 0]])
    first = source.basis_vector(0).isotropic_reduction()
    second = target.basis_vector(0).isotropic_reduction()
    torsor = first.rational_lifts(second, first.Isom(second)(()))
    power = torsor.power_set()
    locus = torsor.integral_lift_locus()

    assert source.determinant() != target.determinant()
    assert torsor.integral_parameter_classes().is_empty() is True
    assert locus is power.bottom()
    assert locus in power
    assert locus in Sets().Subobjects(torsor)
    assert locus.inclusion().codomain() == torsor
    assert locus.is_empty() is True
    assert locus.cardinality() == cardinal(0)
    assert locus.is_parent_of(torsor.base_point()) is False
