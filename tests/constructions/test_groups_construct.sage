r"""Group constructions a mathematician expects.

The catalogue groups with their orders, subgroups and cosets, automorphism
groups and Hom sets, abelianizations, presentations, actions on finite sets
and on modules, and absolute Galois groups.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403

FINITE = {
    "S3": (lambda: Groups.S(3), 6),
    "S4": (lambda: Groups.S(4), 24),
    "A4": (lambda: Groups.A(4), 12),
    "A5": (lambda: Groups.A(5), 60),
    "C6": (lambda: Groups.C(6), 6),
    "D4": (lambda: Groups.D(4), 8),
    "Q8": (lambda: Groups.Q(), 8),
    "V4": (lambda: Groups.V4(), 4),
    "C2xC4": (lambda: Groups.Abelian([2, 4]), 8),
    "GL(2,3)": (lambda: Groups.GL(2, GF(3)), 48),
    "SL(2,3)": (lambda: Groups.SL(2, GF(3)), 24),
    "PSL(2,7)": (lambda: Groups.PSL(2, GF(7)), 168),
    "W(A3)": (lambda: Groups.Coxeter(["A", 3]), 24),
    "W(B2)": (lambda: Groups.Weyl(["B", 2]), 8),
    "M11": (lambda: Groups.Mathieu(11), 7920),
}
INFINITE = {
    "F2": lambda: Groups.Free(2),
    "B3": lambda: Groups.Braid(3),
    "Heisenberg": lambda: Groups.Heisenberg(),
    "GL(2,ZZ)": lambda: Groups.GL(2, ZZ),
    "W(A~2)": lambda: Groups.Coxeter(["A", 2, 1]),
}
ABELIANIZATION_ORDER = {
    "S3": 2, "S4": 2, "A4": 3, "A5": 1, "C6": 6, "D4": 4, "Q8": 4, "V4": 4,
    "C2xC4": 8, "GL(2,3)": 2, "SL(2,3)": 3, "PSL(2,7)": 1, "W(A3)": 2, "W(B2)": 4,
}
ABELIAN = {"C6", "V4", "C2xC4"}


@pytest.fixture(params=sorted(FINITE), ids=str)
def finite_group(request):
    return request.param, FINITE[request.param][0](), FINITE[request.param][1]


def test_finite_catalogue_groups_have_their_orders(finite_group) -> None:
    name, group, order = finite_group
    assert group in Groups()
    assert group in FiniteGroups()
    assert group in FinitelyGeneratedGroups()
    assert group in FinitelyPresentedGroups()
    assert group.order() == order
    assert group.cardinality() == cardinal(order)
    assert group.is_finite()
    assert group.is_abelian() == (name in ABELIAN)
    assert (group in AbelianGroups()) == (name in ABELIAN)
    assert (group in FiniteAbelianGroups()) == (name in ABELIAN)


@pytest.mark.parametrize("name", sorted(INFINITE))
def test_infinite_catalogue_groups_are_infinite(name) -> None:
    group = INFINITE[name]()
    assert group in Groups()
    assert group not in FiniteGroups()
    assert not group.is_finite()
    assert group.cardinality() == aleph0
    assert group in FinitelyGeneratedGroups()


def test_abelianization_of_every_finite_catalogue_group(finite_group) -> None:
    name, group, _ = finite_group
    if name not in ABELIANIZATION_ORDER:
        return
    abelianization = Groups().abelianization()(group)
    assert abelianization in AbelianGroups()
    assert abelianization in Modules(ZZ)
    assert abelianization.order() == ABELIANIZATION_ORDER[name]


def test_abelianization_of_the_free_group_is_free_abelian() -> None:
    abelianization = Groups().abelianization()(Groups.Free(2))
    assert abelianization in AbelianGroups()
    assert abelianization in Modules(ZZ)
    assert not abelianization.is_finite()
    assert abelianization.is_isomorphic_to(Groups.Abelian([0, 0]))


def test_group_elements_and_inverses(finite_group) -> None:
    _, group, _ = finite_group
    element = group.an_element()
    assert element * element.inverse() == group.one()
    assert element.inverse() * element == group.one()
    assert group.one() * element == element
    assert group.subgroup([element]).order() == element.order()
    assert group.subgroup([group.one()]).order() == 1


def test_subgroups_cosets_and_centralizers_of_the_symmetric_group() -> None:
    group = Groups.S(3)
    transposition = next(g for g in group.group_generators() if g.order() == 2)
    subgroup = group.subgroup([transposition])

    assert subgroup in Subgroups(group)
    assert subgroup in Groups()
    assert subgroup.order() == 2
    assert subgroup.supergroup() is group
    assert subgroup.inclusion().is_injective()
    assert group.left_cosets(subgroup).cardinality() == cardinal(3)
    assert group.right_cosets(subgroup).cardinality() == cardinal(3)
    assert group.centralizer(transposition).order() == 2
    assert group.centralizer(group.one()) == group
    assert group.conjugacy_classes_representatives().cardinality() == cardinal(3)
    assert Groups.S(4).conjugacy_classes_representatives().cardinality() == cardinal(5)


@pytest.mark.parametrize(
    "name, order",
    [("S3", 6), ("C6", 2), ("V4", 6), ("Q8", 24), ("S4", 24), ("A4", 24), ("D4", 8)],
)
def test_automorphism_groups(name, order) -> None:
    group = FINITE[name][0]()
    automorphisms = group.Aut()
    assert automorphisms in Groups()
    assert automorphisms.order() == order
    identity = automorphisms.one()
    assert identity(group.an_element()) == group.an_element()


@pytest.mark.parametrize(
    "source, target, count",
    [("C2", "S3", 4), ("S3", "C2", 2), ("C3", "S3", 3), ("S3", "C3", 1), ("C6", "C4", 2), ("V4", "C2", 4)],
)
def test_counting_group_homomorphisms(source, target, count) -> None:
    def group(name):
        if name.startswith("C"):
            return Groups.C(int(name[1:]))
        return FINITE[name][0]()

    homset = group(source).Mor(group(target))
    assert homset.cardinality() == cardinal(count)
    trivial = homset.an_element()
    assert trivial(group(source).one()) == group(target).one()


def test_the_free_group_maps_freely() -> None:
    free = Groups.Free(1)
    for name, order in (("S3", 6), ("Q8", 8), ("C6", 6)):
        assert free.Mor(FINITE[name][0]()).cardinality() == cardinal(order)
    assert Groups.Free(2).Mor(Groups.C(2)).cardinality() == cardinal(4)


def test_presentations() -> None:
    free = Groups.Free(2)
    a, b = free.group_generators()
    symmetric = free.quotient_by_relators([a**2, b**3, (a * b) ** 2])

    assert free in GroupsWithChosenFinitePresentation()
    assert free.group_generators().cardinality() == cardinal(2)
    assert symmetric in GroupsWithChosenFinitePresentation()
    assert symmetric.order() == 6
    assert symmetric.is_isomorphic_to(Groups.S(3))
    assert not symmetric.is_abelian()
    assert symmetric.presenting_free_group() is free
    assert symmetric.defining_relations().cardinality() == cardinal(3)
    native_symmetric = Groups.S(3)
    assert native_symmetric in FinitelyPresentedGroups()
    assert native_symmetric not in GroupsWithChosenFinitePresentation()
    assert native_symmetric.presentation() in GroupsWithChosenFinitePresentation()
    assert Groups.S(3).is_isomorphic_to(Groups.D(3))
    assert not Groups.Q().is_isomorphic_to(Groups.D(4))


def test_the_natural_action_of_the_symmetric_group_is_transitive() -> None:
    group = Groups.S(3)
    points = (1, 2, 3)
    natural = FiniteGSets(group)(points, lambda g, x: g(x))
    trivial = FiniteSets().trivial_action(group)(points)

    assert natural in FiniteGSets(group)
    assert natural.acting_group() is group
    assert natural.fixed_points().cardinality() == cardinal(0)
    assert trivial.fixed_points().cardinality() == cardinal(3)
    assert natural.point_set().cardinality() == cardinal(3)
    generator = group.group_generators()[0]
    assert natural.act(generator, 1) == generator(1)


def test_group_modules_and_their_invariants(pid) -> None:
    r"""$C_2$ swapping the coordinates of $R^2$: invariants of rank one, coinvariants of rank one."""
    ring = pid
    group = Groups.C(2)
    module = ring.free_module(2)
    e0, e1 = module.module_generator(0), module.module_generator(1)
    swap = module.Mor(module)({0: e1, 1: e0})

    def action(group_element, vector):
        return vector if group_element == group.one() else swap(vector)

    acted = Modules(ring[group])(module, action)
    assert acted.group() is group
    assert acted.action_of(group.one())(e0) == e0
    assert acted.is_invariant(e0 + e1)
    assert not acted.is_invariant(e0)
    invariants = acted.module_invariants()
    coinvariants = acted.module_coinvariants()
    assert invariants.module_rank() == cardinal(1)
    assert coinvariants.module_rank() == cardinal(1)
    assert invariants in Modules(ring)


def test_absolute_galois_groups() -> None:
    finite = AbsoluteGaloisGroup(GF(5))
    rational = AbsoluteGaloisGroup(QQ)
    gaussian = AbsoluteGaloisGroup(QuadraticField(-1, "i"))

    assert finite in ProfiniteGroups()
    assert finite.is_profinite()
    assert finite.is_abelian()
    assert not finite.is_finite()
    assert finite.topological_group_generators().cardinality() == cardinal(1)
    assert finite.characteristic() == 5
    assert rational in ProfiniteGroups()
    assert not rational.is_abelian()
    assert rational.characteristic() == 0
    assert gaussian in ProfiniteGroups()
    assert not gaussian.is_abelian()
