r"""The thin categories of cardinals and of ordinals, and the arithmetic acting on their arrows.

$\mathbf{Card}$ has one arrow $\kappa \to \lambda$ exactly when
$\kappa \le \lambda$, so composites and identities are forced.  Cardinal
sum, product and power with a nonzero base are monotone, so they act on
arrows: $2 \le 3$ and $4 \le 5$ give $6 \le 8$, $8 \le 15$ and
$16 \le 243$.  A finite sum $\sum_{i=0}^{3} (i + 1) = 10$, and
$\sum_{i \in \mathbb{N}} 1 = \aleph_0$.  For ordinals, $\omega + 1 \ne
1 + \omega = \omega$, $2 \cdot \omega = \omega \ne \omega \cdot 2$ and
$2^\omega = \omega$; natural (Hessenberg) sum is commutative.  All of these
are the definitions of the operations on order types.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_comparisons_of_cardinals_compose_and_are_carried_by_the_arithmetic() -> None:
    cardinals = Cardinalities()
    two_three = cardinals.Mor(2, 3).unique_morphism()
    four_five = cardinals.Mor(4, 5).unique_morphism()
    three_five = cardinals.Mor(3, 5).unique_morphism()

    assert three_five * two_three == cardinals.Mor(2, 5).unique_morphism()
    assert cardinals.Mor(3, 3).identity() == cardinals.Mor(3, 3).unique_morphism()
    assert cardinals.sum_morphism(two_three, four_five) == cardinals.Mor(6, 8).unique_morphism()
    assert cardinals.product_morphism(two_three, four_five) == cardinals.Mor(8, 15).unique_morphism()
    assert cardinals.power_morphism(two_three, four_five) == cardinals.Mor(16, 243).unique_morphism()
    assert cardinals.Mor(3, 2).is_empty()
    assert cardinal(2).Mor(3).cardinality() == cardinal(1)


def test_finite_indexed_sums_suprema_and_comparisons_of_cardinals() -> None:
    cardinals = Cardinalities()

    assert cardinals.indexed_sum(Sets.Δ[3], lambda index: cardinal(index + 1)) == cardinal(10)
    assert cardinals.supremum(cardinal(3), aleph0) == aleph0
    assert cardinals.compare(cardinal(3), cardinal(5)) is CardinalComparison.LESS
    assert cardinals.compare(aleph0, cardinal(5)) is CardinalComparison.GREATER
    assert cardinals(Infinity) == aleph0


def test_the_countable_sum_of_ones_is_aleph_zero() -> None:
    assert Cardinalities().indexed_sum(NN, lambda _index: cardinal(1)) == aleph0


def test_a_finite_cardinal_is_the_natural_number_it_counts() -> None:
    r"""$|\{0, 1, 2\}| = 3$, and the finite cardinal $7$ read in $\mathbb{Z}$ and $\mathbb{Q}$ is $7$."""
    assert cardinal(3) == 3
    assert Sets.Δ[2].cardinality() == 3
    assert ZZ(cardinal(7)) == 7
    assert QQ(cardinal(7)) == 7


def test_ordinal_sum_product_and_power_are_not_commutative() -> None:
    ordinals = Ordinals()
    first_infinite = omega(0)

    assert first_infinite.ordinal_sum(1) != first_infinite
    assert ordinals(1).ordinal_sum(first_infinite) == first_infinite
    assert ordinals(2).ordinal_product(first_infinite) == first_infinite
    assert first_infinite.ordinal_product(2) != first_infinite
    assert ordinals(2).ordinal_power(first_infinite) == first_infinite
    assert ordinals.proves_le(3, first_infinite)
    assert not ordinals.proves_le(first_infinite, 3)


def test_ordinary_ordinal_arithmetic_is_canonical_order_type_arithmetic() -> None:
    two = Ordinals()(2)
    first = omega(0)
    second = omega(1)

    assert Ordinals()(1).ordinal_sum(first) == first
    assert two.ordinal_product(first) == first
    assert two.ordinal_power(first) == first

    omega_plus_one = first.ordinal_sum(1)
    omega_times_two = first.ordinal_product(2)
    omega_squared = first.ordinal_power(2)
    assert omega_plus_one.ordinal_sum(first) == omega_times_two
    assert omega_plus_one.ordinal_product(first) == omega_squared
    assert two.ordinal_power(omega_times_two) == omega_squared

    assert two.ordinal_product(second) == second
    assert two.ordinal_power(second) == second
    assert first < omega_plus_one < omega_times_two < omega_squared < second


def test_natural_sums_of_initial_ordinals_commute_and_omega_one_follows_omega() -> None:
    first = omega(0)
    second = omega(1)

    assert first + second == second + first
    assert first + second == second.ordinal_sum(first)
    assert first * second == second.ordinal_product(first)
    assert first.ordinal_sum(second) == second
    assert second > first
    assert second.initial_index() == Ordinals()(1)
    assert Ord.Mor(first, second).unique_morphism().domain() is first
    assert Ord.Mor(second, second).identity().is_identity()


def test_order_type_is_a_functor_from_well_orders_to_ord() -> None:
    labels = finite_ordered_set(("a", "b", "c"))
    standard = Sets.Δ[2]
    well_orders = WellOrderedSets()

    forward = well_orders.Mor(labels, standard)(
        lambda point: labels.ranking_map()(point)
    )
    inverse = well_orders.Mor(standard, labels)(
        lambda position: labels.ranking_map().inverse()(position)
    )
    isomorphism = well_orders.Core().Mor(labels, standard)(forward, inverse)
    order_type = well_orders.order_type_functor()

    assert standard in AugmentedSimplexCategory()
    assert labels in WellOrderedSets()
    assert order_type(labels) is Ordinals()(3)
    assert order_type(standard) is Ordinals()(3)
    assert order_type(isomorphism) == Ord.Mor(3, 3).identity()


def test_infinite_well_order_type_uses_its_core_isomorphism() -> None:
    well_orders = WellOrderedSets()
    order_type = well_orders.order_type_functor()
    identity = well_orders.Mor(NN, NN).identity()
    selected_isomorphism = well_orders.Core().Mor(NN, NN)(identity, identity)
    assert NN in well_orders
    assert NN in TotallyOrderedSets()
    assert order_type(NN) is NN.order_type()
    assert order_type(selected_isomorphism).is_identity()


def test_nonidentity_well_order_maps_compose_with_exact_endpoints() -> None:
    well_orders = WellOrderedSets()
    source = Sets.Δ[1]
    target = Sets.Δ[2]
    inclusion = well_orders.Mor(source, target)(lambda point: target(int(point) + 1))
    shift = well_orders.Mor(target, target)(lambda point: target(min(2, int(point) + 1)))
    composite = shift * inclusion
    assert composite.parent() is well_orders.Mor(source, target)
    assert composite.underlying_set_morphism().domain() is source
    assert composite.underlying_set_morphism().codomain() is target
    assert tuple(int(composite(point)) for point in source) == (2, 2)
    try:
        well_orders.Mor(target, target)(lambda point: target(2 - int(point)))
    except ValueError:
        pass
    else:
        raise AssertionError("an order-reversing map was admitted to well-ordered Mor")


def test_finite_ordered_set_operations_retain_selected_well_orders() -> None:
    left = finite_ordered_set(("b", "a", "c"))
    right = finite_ordered_set(("c", "d"))
    union = left.union(right)
    intersection = left.intersection(right)
    difference = left.difference(right)
    assert tuple(union) == ("b", "a", "c", "d")
    assert tuple(intersection) == ("c",)
    assert tuple(difference) == ("b", "a")
    assert all(result in WellOrderedSets() for result in (union, intersection, difference))
    assert (union.order_type(), intersection.order_type(), difference.order_type()) == (
        Ordinals()(4), Ordinals()(1), Ordinals()(2)
    )


def test_ordered_union_requires_a_selected_order_on_both_inputs() -> None:
    r"""A finite cardinality does not provide a canonical order for the union."""
    from sage_extensions.categories.sets.set_categories import Set

    left = finite_ordered_set(("a", "b"))
    unordered = Set(("b", "c"))
    try:
        left.union(unordered)
    except (AssertionError, TypeError):
        pass
    else:
        raise AssertionError("unordered finite points were treated as an ordered union")


def test_literal_union_preserves_unenumerated_finite_image() -> None:
    from sage_extensions.categories.sets.set_categories import Set
    from sage_extensions.logic import AtomicProposition

    left = Set((0, 1))
    unknown_subset = Sets().condition_set(
        left, lambda point: AtomicProposition("unspecified_member", point)
    )
    # The retained ambient inclusion establishes B subset A, so A union B
    # is literally A without enumerating B or deciding its predicate.
    assert left.union(unknown_subset) is left
    universe = Sets.Δ[2]
    undecided = Sets().condition_set(
        universe, lambda point: AtomicProposition("unspecified_member", point)
    )
    assert undecided in Sets().Finite()
    union = left.union(undecided)
    assert union in Sets().Finite()
    assert union not in EnumeratedSets()
    for point in left:
        assert union.is_parent_of(point) is not False
    assert union.is_parent_of(universe(2)) is not False


def test_literal_union_with_infinite_set_keeps_its_coproduct_image() -> None:
    from sage_extensions.categories.sets.set_categories import Set

    finite = Set((0, 1))
    union = finite.union(NN)
    assert union in Sets()
    assert union not in Sets().Finite()
    assert union.source_set().index_set().cardinality() == cardinal(2)
    assert union.source_set().cofactor(union.source_set().index_set()(1)) is NN


def test_literal_intersection_and_difference_preserve_undecided_membership() -> None:
    from sage_extensions.categories.sets.set_categories import Set
    from sage_extensions.logic import AtomicProposition

    ambient = Sets.Δ[2]
    left = Set(tuple(ambient))
    undecided = Sets().condition_set(
        ambient, lambda point: AtomicProposition("unspecified_member", point)
    )
    meet = left.intersection(undecided)
    complement = left.difference(undecided)
    assert meet in Sets().Finite() and complement in Sets().Finite()
    for point in ambient:
        assert isinstance(meet.is_parent_of(point), AtomicProposition)
        assert complement.is_parent_of(point) is not True
        assert complement.is_parent_of(point) is not False


def test_ordered_intersection_retains_finite_predicate_when_membership_is_undecided() -> None:
    from sage_extensions.logic import AtomicProposition

    ordered = finite_ordered_set(("a", "b", "c"))
    unknown = Sets().condition_set(
        ordered, lambda value: AtomicProposition("unspecified_member", value)
    )
    meet = ordered.intersection(unknown)
    complement = ordered.difference(unknown)
    for result in (meet, complement):
        assert result in Sets().Finite()
        assert result not in EnumeratedSets()
        for value in ordered:
            assert result.is_parent_of(value) is not True
            assert result.is_parent_of(value) is not False


def test_ordered_and_unordered_sets_do_not_have_false_structural_equality() -> None:
    from sage_extensions.categories.sets.set_categories import Set

    ascending = finite_ordered_set(("a", "b"))
    descending = finite_ordered_set(("b", "a"))
    underlying = Set(("a", "b"))
    assert ascending != descending
    assert ascending != underlying and underlying != ascending
    assert descending != underlying and underlying != descending
    assert tuple(ascending) == ("a", "b")
    assert tuple(descending) == ("b", "a")


def test_finite_indexed_enumeration_evaluates_selected_points_once() -> None:
    r"""The finite presentation retains its chosen values across all operations."""
    from sage_extensions.categories.sets.finite_ordered_sets import FiniteOrderedSets

    indices = Sets.Δ[2]
    calls = []

    def selected(index):
        calls.append(int(index))
        return ("point", int(index))

    points = FiniteOrderedSets().from_indexed(indices, selected)
    assert len(calls) == 3
    assert tuple(points) == (("point", 0), ("point", 1), ("point", 2))
    assert points.is_parent_of(("point", 1)) is True
    assert int(points.ranking_map()(("point", 2))) == 2
    assert len(calls) == 3
