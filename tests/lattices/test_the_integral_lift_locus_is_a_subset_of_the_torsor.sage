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


def _reduction_reflection(reduction, root_index):
    r"""A non-identity isometry of ``reduction``: the reflection in a basis vector of square two."""
    roots = tuple(
        label
        for label in reduction.module_generating_set()
        if reduction.module_generator(label).q() == ZZ(2)
    )
    return reduction.reflection(reduction.module_generator(roots[root_index]))


class _BasePointIntegralRestrictions:
    r"""Count the integral restrictions the base point is asked for inside the block."""

    def __init__(self, point):
        self.point = point
        self.count = 0

    def __enter__(self):
        point, counted = self.point, self
        original = point.integral_restriction

        def integral_restriction(source, target):
            counted.count += 1
            return original(source, target)

        point.integral_restriction = integral_restriction
        return self

    def __exit__(self, *exception):
        del self.point.integral_restriction
        return False


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


class _InclusionQuestions:
    r"""Count the image questions the locus asks its parameter inclusion inside the block."""

    def __init__(self, inclusion):
        self.inclusion = inclusion
        self.membership = 0
        self.lifts = 0

    def __enter__(self):
        inclusion, counted = self.inclusion, self
        original_membership = inclusion.is_in_image
        original_lift = inclusion.lift

        def is_in_image(element):
            counted.membership += 1
            return original_membership(element)

        def lift(element):
            counted.lifts += 1
            return original_lift(element)

        inclusion.is_in_image = is_in_image
        inclusion.lift = lift
        return self

    def __exit__(self, *exception):
        del self.inclusion.is_in_image
        del self.inclusion.lift
        return False


def _non_integral_base_point_control(root_index):
    r"""``U(2) + A2`` at a marked line of divisibility two, lifting a reflection.

    ``root_index`` selects which square-two basis vector of the positive-definite
    rank-two reduction is reflected in: two isometries of one reduction, so two
    lift torsors with a locus each.

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
    isometry = _reduction_reflection(reduction, root_index)
    return lattice, marked, reduction, _marked_line_lift_torsor(reduction, isometry)


def test_the_integral_locus_is_a_subset_of_its_torsor() -> None:
    r"""``T_Z`` has the inclusion of a subset of ``T``, into the torsor itself."""
    lattice, marked, reduction, torsor = _non_integral_base_point_control(0)
    locus = torsor.integral_lift_locus()

    assert lattice.div(marked) == 2
    assert locus.inclusion().codomain() == torsor
    # A subset of a set is a set of that set's points, and the empty set is not the
    # answer here: this locus has a lift.
    assert locus.is_empty() is False


def test_the_nonempty_locus_is_a_point_of_the_torsors_power_set() -> None:
    r"""``T_Z`` is a subobject of ``T``: a point of ``P(T)``, as the empty locus is.

    The subsets of a set are the points of its power set, so a subset of ``T``
    lies in ``Sets().Subobjects(T)`` and is a member of ``T.power_set()``.  The
    empty locus is ``P(T)``'s bottom; this one is the same kind of object, cut
    out of ``T`` by the residue-class predicate, and the two cases owe the same.
    """
    lattice, marked, reduction, torsor = _non_integral_base_point_control(0)
    locus = torsor.integral_lift_locus()

    assert lattice.div(marked) == 2
    assert locus.is_empty() is False
    assert locus in Sets().Subobjects(torsor)
    assert locus in torsor.power_set()


def test_a_zero_dimensional_parameter_space_has_the_one_integral_lift() -> None:
    r"""``U``'s marked null line reduces to rank zero, so ``T_Z`` is one lift.

    The parameter lattice of a rank-zero reduction is zero, so ``P/mP`` is one
    class and the only lift a parameter names is ``phi(0)``: the torsor's base
    point.  The residue locus is either that class or empty, and here it is the
    class, so the integral locus is the one-point subset of ``T`` on the base
    point --- a finite set the set owner counts from its point.
    """
    U = Lattices(ZZ)("U")
    reduction = _reduction_at(U, U.basis_vector(0))
    torsor = _marked_line_lift_torsor(reduction, reduction.Isom(reduction).identity())
    locus = torsor.integral_lift_locus()

    assert torsor.parameter_space().module_rank() == 0
    assert torsor.integral_parameter_classes().is_empty() is False
    assert locus.is_parent_of(torsor.base_point()) is True
    assert locus.is_empty() is False
    assert locus.cardinality() == cardinal(1)


def test_the_point_the_locus_admits_is_an_integral_lift() -> None:
    r"""The locus' own point restricts to an isometry of the lattice.

    The nonempty locus admits the lift the residue locus built for its first
    passing representative, so the point it answers is a lift of the lattice's
    isometries and not merely a point of ``T``.  Asking it for its integral
    restriction is an independent check of the fact the construction read off
    the residue locus: the base point of this torsor has no integral
    restriction, and the admitted lift does.
    """
    lattice, marked, reduction, torsor = _non_integral_base_point_control(0)
    locus = torsor.integral_lift_locus()

    assert lattice.div(marked) == 2
    assert torsor.base_point().integral_restriction(lattice, lattice) is None
    assert locus.an_element().integral_restriction(lattice, lattice) in lattice.Isom(lattice)


def test_the_locus_is_membership_in_the_residue_class() -> None:
    r"""A lift is in ``T_Z`` exactly when its parameter's class lies in the residue locus.

    Both directions are decided on lifts the test builds: the classes of ``C`` itself give
    members, and the torsor's own base point -- whose parameter is the zero class, outside
    ``C`` at this specimen -- does not.
    """
    lattice, marked, reduction, torsor = _non_integral_base_point_control(0)
    locus = torsor.integral_lift_locus()
    classes = tuple(torsor.integral_parameter_classes())
    zero = torsor.integral_parameter_quotient().codomain().zero()

    assert zero not in classes
    assert locus.is_parent_of(torsor.base_point()) is False
    for residue in classes:
        assert locus.is_parent_of(_lift_at_class(torsor, residue)) is True
    # The lift the torsor answers with when asked for an integral point is the one the
    # locus admits, so membership answers without asking the predicate again.
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
    lattice, marked, reduction, torsor = _non_integral_base_point_control(0)
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


def test_building_the_locus_asks_the_base_point_for_no_integral_restriction() -> None:
    r"""``T_Z`` is built from the residue locus, not by testing the torsor's base point.

    The residue locus decides its classes by building a lift and asking it for its
    integral restriction, so the locus already holds an integral lift when it is cut
    out, and the base point's own integrality is a question its construction does
    not ask.  The specimen is the reflection in the reduction's second square-two
    basis vector: the first one's torsor is what the other tests read, and this one
    is asked for its locus here and nowhere else, so the construction measured is a
    cold one rather than a cached locus.
    """
    lattice, marked, reduction, torsor = _non_integral_base_point_control(1)
    base = torsor.base_point()

    assert lattice.div(marked) == 2
    assert base.integral_restriction(lattice, lattice) is None
    with _BasePointIntegralRestrictions(base) as asked:
        locus = torsor.integral_lift_locus()
        assert locus.is_empty() is False
    assert asked.count == 0


def test_a_membership_test_asks_the_parameter_inclusion_no_image_question() -> None:
    r"""Membership in ``T_Z`` solves the parameter's preimage once, not once per question.

    Whether a lift's parameter lies in ``P``, and which class of ``P/mP`` it has when
    it does, are one question: one preimage of the parameter, read for both facts.
    ``is_in_image`` and ``lift`` are two questions that each solve it, and the locus
    asks the inclusion neither.  What the locus answered while the count was taken
    is the two membership results below --- a lift whose class is in ``C``, and the
    base point, whose class is not.
    """
    lattice, marked, reduction, torsor = _non_integral_base_point_control(0)
    locus = torsor.integral_lift_locus()
    inclusion = torsor.integral_parameter_quotient().domain().inclusion()
    member = _lift_at_class(torsor, tuple(torsor.integral_parameter_classes())[0])

    assert lattice.div(marked) == 2
    assert locus.is_empty() is False
    with _InclusionQuestions(inclusion) as asked:
        assert locus.is_parent_of(member) is True
        assert locus.is_parent_of(torsor.base_point()) is False
    assert asked.membership == 0
    assert asked.lifts == 0
