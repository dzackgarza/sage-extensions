r"""A subgroup acts through its inclusion, and the form layer keeps the action.

A group is not a set with an action: the action is a datum of the G-*set*, and a
subgroup's action is the ambient one read through the retained inclusion
``H -> G``.  ``GObjects.restrict_action`` is that construction, and the form
layer's own presentation (``_torsion_form_element_action``) is the second route
to the same points.

The consumer that motivated these tests asked ``H.orbits()`` of a subgroup of
2047 generators acting on a 2048-element discriminant form and was refused: a
subgroup has no canonical action to take orbits of.  What it needed is the
three lines below, and they are stated here on a small form so that the shape is
read off a specimen rather than discovered from a forty-minute run.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _orthogonal_group_of_the_d4_discriminant_form():
    r"""``G = O(D)`` for the discriminant form of ``D_4``: six automorphisms."""
    form = Lattices(ZZ)("D4").discriminant_quadratic_form()
    return form, form.automorphism_group()


def _orthogonal_group_of_the_hyperbolic_discriminant_form():
    r"""``G = O(D)`` for ``U(2)``'s discriminant form: three isotropic points."""
    form = Lattices(ZZ)("U").twist(2).discriminant_quadratic_form()
    return form, form.automorphism_group()


def test_a_group_has_no_action_but_its_g_set_does() -> None:
    r"""``G.element_action()`` is the action; ``G`` itself has none to take orbits of.

    ``element_action`` is the represented ``G``-set on the form's elements, and
    the action is a left action through the group's own law: the identity fixes
    every point and a product acts as the composite.
    """
    form, group = _orthogonal_group_of_the_d4_discriminant_form()
    action = group.element_action()

    assert action.acting_group() is group
    assert tuple(action) == tuple(form.elements())
    one = group.one()
    for point in form.elements():
        assert action.act(one, point) == point
    elements = tuple(group)
    for left in elements:
        for right in elements:
            point = form.elements().an_element()
            assert action.act(left * right, point) == action.act(
                left, action.act(right, point)
            )


def test_a_subgroup_acts_through_its_retained_inclusion() -> None:
    r"""``action.restrict_action(H.inclusion())`` is the ``H``-set on the same points.

    Every element of the restricted set's action is the ambient action of the
    inclusion's image, and the restricted set's acting group is ``H`` itself,
    the same subgroup object the inclusion starts at.
    """
    form, group = _orthogonal_group_of_the_d4_discriminant_form()
    action = group.element_action()
    subgroup = group.subgroup_on(tuple(group.group_generators()))
    inclusion = subgroup.inclusion()

    restricted = action.restrict_action(inclusion)

    assert restricted.acting_group() is subgroup
    assert inclusion.domain() is subgroup and inclusion.codomain() is group
    for element in subgroup:
        for point in form.elements():
            assert restricted.act(element, point) == action.act(inclusion(element), point)


def test_the_isotropic_points_carry_the_restricted_action() -> None:
    r"""The isotropic set is an invariant point set, and its action is the restriction.

    ``D.isotropic_elements()`` is the set the consumer wants orbits on.  It is
    invariant under the form's automorphisms, so the same action presents it, and
    ``FiniteGSets`` -- the construction the form layer itself uses -- states it
    on those points.  Both routes agree with the ambient action through the
    inclusion.
    """
    form, group = _orthogonal_group_of_the_d4_discriminant_form()
    action = group.element_action()
    subgroup = group.subgroup_on(tuple(group.group_generators()))
    inclusion = subgroup.inclusion()
    restricted = action.restrict_action(inclusion)
    isotropic = form.isotropic_elements()

    on_isotropic = FiniteGSets(subgroup)(isotropic, lambda element, point: element(point))
    presented = GObjects(subgroup, Sets()).on_set(isotropic, restricted.act)

    assert set(tuple(on_isotropic)) == set(tuple(isotropic))
    for element in subgroup:
        for point in isotropic:
            assert on_isotropic.act(element, point) == restricted.act(element, point)
            assert presented.act(element, point) == action.act(inclusion(element), point)


def test_the_restricted_action_carries_the_orbit_and_stabilizer_constructions() -> None:
    r"""Orbits are taken of the ``H``-set, and a covering presents them when it is large.

    ``orbits()`` is the coequalizer of the action and the projection, so it needs
    the orbit relation decided; ``orbits_presented_by(covering)`` presents the
    same orbit set from a stated finite covering meeting every orbit -- the route
    a group too large to enumerate needs.  On a group small enough to enumerate,
    both constructions see the same partition of the points, and the stabilizer
    of a point is the subgroup the action names, inside ``H``.
    """
    form, group = _orthogonal_group_of_the_hyperbolic_discriminant_form()
    subgroup = group.subgroup_on(tuple(group.group_generators()))
    isotropic = form.isotropic_elements()
    on_isotropic = FiniteGSets(subgroup)(isotropic, lambda element, point: element(point))

    enumerated = on_isotropic.orbits()
    presented = on_isotropic.orbits_presented_by(isotropic)

    # An orbit names its own parent, so the two orbit sets are compared by the
    # partition of the points they induce rather than by orbit equality.
    enumerated_partition = {frozenset(orbit.points()) for orbit in enumerated}
    presented_partition = {frozenset(orbit.points()) for orbit in presented}
    assert enumerated_partition == presented_partition
    assert set().union(*enumerated_partition) == set(tuple(isotropic))

    for point in isotropic:
        stabilizer = on_isotropic.stabilizer(point)
        assert stabilizer.supergroup() is subgroup
        for element in subgroup:
            assert (element in stabilizer) == (element(point) == point)
