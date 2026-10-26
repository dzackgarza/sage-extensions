r"""Products in groups of factors with no finite realization or presentation.

The product of groups ``G_1 x G_2`` is the set of pairs with the
componentwise law, with projections ``p_i`` and factor inclusions
``g |-> (g, 1), (1, g)`` (lean-categories#91 requests its formalization).

Specimens:

- ``U + U`` with ``G_i = <s>``, ``s`` the swap ``e <-> f`` of ``U``.  Each
  ``G_i`` has order two, so ``G_1 x G_2`` has order four, ``p_1 i_1`` is the
  identity and ``p_2 i_1`` is trivial.  The orthogonal-sum map
  ``(g_1, g_2) |-> g_1 + g_2`` into ``O(U + U)`` is injective: ``(s, 1)``
  moves only the first summand and ``(1, s)`` only the second, and the image
  of ``(s, s)`` exchanges ``e_i`` and ``f_i`` in both summands.
- ``O(K) x <s>`` for ``K = <1> + <-2>``.  The isometry ``t`` of ``K`` with
  ``e_0 |-> 3 e_0 + 2 e_1``, ``e_1 |-> 4 e_0 + 3 e_1`` preserves
  ``x^2 - 2 y^2``, since ``(3x + 4y)^2 - 2 (2x + 3y)^2 = x^2 - 2y^2``; its
  matrix has trace 6, so it has infinite order, and ``O(K)`` is not placed
  finite (rank two, ``-det = 2`` not a square).  In the product the point
  ``x = (t, s)`` has components ``t`` and ``s``, ``x^2 = (t^2, 1)`` and
  ``x != 1``.
- The image of the orthogonal-sum map ``<s> x <s> -> O(U + U)`` is the range
  of a function out of a group of order four, so it is finite (Mathlib
  ``Set.finite_range``, ``Mathlib/Data/Set/Finite/Range.lean``) although
  ``O(U + U)`` is not placed finite; by injectivity it has order four.  The
  image of ``C4 -> C2``, ``a |-> b``, is all of ``C2``.  A morphism out of the
  infinite free group ``F(x)`` into itself, ``x |-> x^2``, has the infinite
  image ``<x^2>``, so the finite-source rule does not place it finite.

These specimens passed final-runtime execution on 2026-10-19.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _swap_subgroup():
    plane = NamedLattices.U
    e, f = plane.module_generators()[0], plane.module_generators()[1]
    swap = plane.Aut()({0: f, 1: e})
    return plane, swap, plane.O().subgroup(Set((swap,)))


def test_product_of_two_swap_groups_has_order_four_with_projections_and_inclusions() -> None:
    plane, swap, group = _swap_subgroup()
    construction = Groups().product_construction((group, group))
    product = construction.object()
    shape = construction.diagram().domain()
    first, second = shape(0), shape(1)
    left = construction.structure_morphism(first)
    right = construction.structure_morphism(second)
    assert product.cardinality() == cardinal(4)
    assert left.codomain() is group and right.codomain() is group

    identity = group.Mor(group).identity()
    trivial = group.Mor(group).elementwise(lambda _element: group.one())
    cone = construction.diagram().Cones().cone(
        group, lambda index: identity if index == first else trivial
    )
    inclusion = construction.factor(cone).apex_map()
    assert left(inclusion(group(swap))) == group(swap)
    assert right(inclusion(group(swap))) == group.one()


def test_orthogonal_sum_map_of_the_swap_groups_into_O_of_U_plus_U() -> None:
    plane, swap, group = _swap_subgroup()
    lattice = plane + plane
    construction = Groups().product_construction((group, group))
    both = construction.object()
    diagram = construction.diagram()
    shape = diagram.domain()
    first, second = shape(0), shape(1)
    sum_map = lattice.orthogonal_sum_map(construction)
    assert sum_map.domain() is both and sum_map.codomain() is lattice.O()

    identity = group.Mor(group).identity()
    trivial = group.Mor(group).elementwise(lambda _element: group.one())
    diagonal = construction.factor(diagram.Cones().cone(group, lambda _index: identity)).apex_map()
    on_first_factor = construction.factor(
        diagram.Cones().cone(group, lambda index: identity if index == first else trivial)
    ).apex_map()
    on_second_factor = construction.factor(
        diagram.Cones().cone(group, lambda index: identity if index == second else trivial)
    ).apex_map()

    e1, f1, e2, f2 = lattice.module_generators()
    double_swap = sum_map(diagonal(group(swap)))
    assert double_swap(e1) == f1 and double_swap(f1) == e1
    assert double_swap(e2) == f2 and double_swap(f2) == e2

    # Injectivity: (s, 1) and (1, s) go to distinct nonidentity isometries,
    # each moving only its own summand, and their product is (s, s).
    on_first = sum_map(on_first_factor(group(swap)))
    on_second = sum_map(on_second_factor(group(swap)))
    assert on_first(e1) == f1 and on_first(e2) == e2
    assert on_second(e1) == e1 and on_second(e2) == f2
    assert on_first * on_second == double_swap
    assert on_first in sum_map.image() and on_second in sum_map.image()


def test_product_with_an_infinite_orthogonal_group_is_componentwise() -> None:
    plane, swap, group = _swap_subgroup()
    split = Lattices(ZZ)(1) + Lattices(ZZ)(1).twist(-2)
    first_label, second_label = split.module_generating_set()
    e0, e1 = split.module_generator(first_label), split.module_generator(second_label)
    t = split.Aut()({first_label: 3 * e0 + 2 * e1, second_label: 4 * e0 + 3 * e1})
    orthogonal = split.O()
    assert orthogonal not in Groups().Finite()

    construction = Groups().product_construction((orthogonal, group))
    product = construction.object()
    shape = construction.diagram().domain()
    left = construction.structure_morphism(shape(0))
    right = construction.structure_morphism(shape(1))
    diagram = construction.diagram()

    def inclusion(position, factor):
        identity = factor.Mor(factor).identity()
        return construction.factor(
            diagram.Cones().cone(
                factor,
                lambda index: identity
                if index == shape(position)
                else factor.Mor(diagram(index)).elementwise(lambda _element, index=index: diagram(index).one()),
            )
        ).apex_map()

    point = inclusion(0, orthogonal)(orthogonal(t)) * inclusion(1, group)(group(swap))
    assert left(point) == orthogonal(t)
    assert right(point) == group(swap)
    assert left(point * point) == orthogonal(t) * orthogonal(t)
    assert right(point * point) == group.one()
    assert point != product.one()
    assert left(~point) == ~orthogonal(t)


def test_images_of_morphisms_out_of_finite_groups_are_placed_finite() -> None:
    plane, swap, group = _swap_subgroup()
    lattice = plane + plane
    construction = Groups().product_construction((group, group))
    sum_map = lattice.orthogonal_sum_map(construction)
    assert lattice.O() not in Groups().Finite()
    assert sum_map.image() in Groups().Finite()
    assert sum_map.image().cardinality() == cardinal(4)

    cyclic_four, cyclic_two = Groups.C(4), Groups.C(2)
    a, b = cyclic_four.group_generators()[0], cyclic_two.group_generators()[0]
    reduction = cyclic_four.Mor(cyclic_two)({a: b})
    assert reduction.image() in Groups().Finite()
    assert reduction.image().cardinality() == cardinal(2)

    free = Groups.Free(1)
    x = free.group_generators()[0]
    squaring = free.Mor(free)({next(iter(free.free_basis())): x * x})
    assert squaring.image() not in Groups().Finite()
