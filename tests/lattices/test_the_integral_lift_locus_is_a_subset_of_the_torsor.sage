r"""The integral lift locus is the subset of the torsor its parameter's residue class cuts out.

The integral lifts of a marked-line reduction map are ``T_Z = phi(r^{-1}(C))``: ``r`` the
residue map of the parameter quotient, ``C`` the finite residue locus
(`isotropic_lifts.IsotropicReductionLiftTorsors.integral_parameter_classes`), and ``phi``
the parameterization of the rational lift torsor ``T``.  ``r`` is onto and ``phi`` is a
bijection onto ``T``, so ``T_Z`` is a *subset of the torsor*: the lifts whose parameter
class lies in ``C``.

That is the presentation, and it is what these tests pin.  The pair decomposition
``r^{-1}(C) = {s(c) + k}`` says the same thing, but presenting ``T_Z`` as the image of the
product ``C x ker r`` makes the construction of a subset a construction of a product: a
product of a finite index set is interned under its factors' hashes (``SET-05``), and the
hash of a finite set is the hash of its tuple of points, so the product's key enumerates
every class of ``C`` -- on ``T_Co`` its 131072 classes, once per candidate the plane row
tests.  A locus is a subset of the set it lies in, so it has that subset's inclusion, and
membership in it is the class test; these are the two facts a product presentation cannot
state.
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


def test_an_empty_residue_locus_gives_an_empty_subset() -> None:
    r"""``T_Z`` is empty exactly when ``C`` is, and the locus decides it.

    ``U``'s and ``U(2)``'s marked null lines both reduce to rank zero, but no integral
    isometry joins the ambient lattices, whose determinants differ, so the residue locus is
    empty and so is the integral locus -- a decision the locus has to make for itself,
    since a subset of an infinite torsor cannot be emptied by enumeration.
    """
    source = Lattices(ZZ)("U")
    target = Lattices(ZZ)([[0, 2], [2, 0]])
    first = source.basis_vector(0).isotropic_reduction()
    second = target.basis_vector(0).isotropic_reduction()
    torsor = first.rational_lifts(second, first.Isom(second)(()))

    assert source.determinant() != target.determinant()
    assert torsor.integral_parameter_classes().is_empty() is True
    assert torsor.integral_lift_locus().is_empty() is True
