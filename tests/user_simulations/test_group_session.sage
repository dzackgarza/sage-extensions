r"""A group theorist's session: subgroups, quotients, actions, representations.

One long session per finite group, typed as into a notebook.
"""

import pytest
from sage.misc.latex import latex

from sage_extensions.all import *  # noqa: F401,F403


def rendered(obj) -> str:
    text = repr(obj)
    assert "object at 0x" not in text
    assert "object at 0x" not in latex(obj)
    return text


SESSIONS = {
    # name: (constructor, order, number of conjugacy classes, abelianization order, |Aut|, degree of a permutation action)
    "S3": (lambda: Groups.S(3), 6, 3, 2, 6, 3),
    "S4": (lambda: Groups.S(4), 24, 5, 2, 24, 4),
    "A4": (lambda: Groups.A(4), 12, 4, 3, 24, 4),
    "D4": (lambda: Groups.D(4), 8, 5, 4, 8, 4),
    "Q8": (lambda: Groups.Q(), 8, 5, 4, 24, 8),
    "C6": (lambda: Groups.C(6), 6, 6, 6, 2, 6),
}


@pytest.mark.parametrize("name", sorted(SESSIONS))
def test_a_finite_group_session(name) -> None:
    build, order, classes, abelianization_order, automorphism_order, degree = SESSIONS[name]

    group = build()
    rendered(group)
    assert group in Groups()
    assert group in FiniteGroups()
    assert group.order() == order
    assert group.cardinality() == cardinal(order)
    assert group in FinitelyPresentedGroups()
    assert group not in GroupsWithChosenFinitePresentation()
    assert group.presentation() in GroupsWithChosenFinitePresentation()
    assert group.group_generators().cardinality() >= cardinal(1)
    assert group.conjugacy_classes_representatives().cardinality() == cardinal(classes)
    assert (group in AbelianGroups()) == (classes == order)

    # Elements, orders, cyclic subgroups.
    g = group.group_generators()[0]
    rendered(g)
    assert g * g.inverse() == group.one()
    cyclic = group.subgroup([g])
    rendered(cyclic)
    assert cyclic in Subgroups(group)
    assert cyclic.order() == g.order()
    assert order % cyclic.order() == 0
    assert cyclic.inclusion()(cyclic.one()) == group.one()

    # A subgroup, its cosets, its centralizer, its normality.
    subgroup = group.subgroup([g])
    rendered(subgroup)
    assert subgroup in Groups()
    assert subgroup.order() == cyclic.order()
    cosets = group.left_cosets(subgroup)
    rendered(cosets)
    assert cosets.cardinality() * subgroup.order() == order
    assert group.right_cosets(subgroup).cardinality() == cosets.cardinality()
    center_of_g = group.centralizer(g)
    rendered(center_of_g)
    assert g in center_of_g
    assert center_of_g.order() % cyclic.order() == 0
    assert order % center_of_g.order() == 0
    whole = group.centralizer(group.one())
    assert whole.order() == order
    assert whole == group

    # Abelianization, automorphisms, homomorphisms.
    abelianization = Groups().abelianization()(group)
    rendered(abelianization)
    assert abelianization in AbelianGroups()
    assert abelianization in Modules(ZZ)
    assert abelianization.order() == abelianization_order
    automorphisms = group.Aut()
    rendered(automorphisms)
    assert automorphisms.order() == automorphism_order
    inner = automorphisms.an_element()
    assert inner(group.one()) == group.one()
    assert inner(g) in group
    signs = group.Mor(Groups.C(2))
    rendered(signs)
    assert signs.cardinality() >= cardinal(1)
    assert group.Mor(group).identity()(g) == g
    assert group.End().cardinality() >= cardinal(automorphisms.order())
    assert group.is_isomorphic_to(group)
    assert not group.is_isomorphic_to(Groups.C(order + 1))

    # A permutation action and its orbits and fixed points.
    points = tuple(ZZ(k) for k in range(1, degree + 1))
    if name in ("S3", "S4", "A4", "D4"):
        action = lambda h, point: h(point)  # noqa: E731
    else:
        action = lambda h, point: point  # noqa: E731
    g_set = FiniteGSets(group)(points, action)
    rendered(g_set)
    assert g_set in FiniteGSets(group)
    assert g_set.point_set().cardinality() == cardinal(degree)
    fixed = g_set.fixed_points()
    rendered(fixed)
    if name in ("S3", "S4", "A4", "D4"):
        assert fixed.cardinality() == cardinal(0)
    else:
        assert fixed.cardinality() == cardinal(degree)
    assert g_set.act(group.one(), points[0]) == points[0]

    # The permutation representation over ZZ, QQ and GF(2), with invariants.
    for ring in (ZZ, QQ, GF(2)):
        module = ring.free_module(degree)

        def permutation(h, module=module, action=action):
            return module.Mor(module)(
                {label: module.module_generator(int(action(h, points[label])) - 1) for label in range(degree)}
            )

        def act(h, vector, permutation=permutation):
            return permutation(h)(vector)

        representation = Modules(ring[group])(module, act)
        rendered(representation)
        assert representation.group() is group
        assert representation.action_of(group.one())(module.module_generator(0)) == module.module_generator(0)
        invariants = representation.module_invariants()
        rendered(invariants)
        assert invariants in Modules(ring)
        if name in ("S3", "S4", "A4", "D4"):
            assert invariants.module_rank() == cardinal(1)
        else:
            assert invariants.module_rank() == cardinal(degree)
        coinvariants = representation.module_coinvariants()
        rendered(coinvariants)
        assert coinvariants.module_rank() == invariants.module_rank()
        if ring is QQ:
            character = representation.character()
            rendered(character)
            assert character(group.one()) == degree
