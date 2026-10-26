r"""Cartesian products and disjoint unions of finite and countable sets.

$|X \times Y| = |X| |Y|$ and $|X \sqcup Y| = |X| + |Y|$, so
$\{0, 1\} \times \{0, 1, 2\}$ has $6$ points and $\{0, 1\} \sqcup \{0, 1, 2\}$
has $5$; $\mathbb{N} \times \mathbb{N}$ and $\mathbb{N} \sqcup \{0, 1\}$ are
countably infinite.  An enumeration of $\mathbb{N} \times \mathbb{N}$ by
diagonals lists each pair once, so the rank of the $k$-th listed pair is
$k$.  The product functor sends $(\sigma, \mathrm{id})$ to
$(a, b) \mapsto (\sigma a, b)$.  These are the definitions of cardinal
arithmetic and of the product functor.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_indexed_family_cache_does_not_decide_undecidable_index_equality() -> None:
    from sage_extensions.categories.sets.indexed_families import IndexedFamily
    from sage_extensions.logic import AtomicProposition

    class SymbolicIndex:
        def __hash__(self):
            return 1

        def __eq__(self, other):
            return AtomicProposition("equal_symbolic_indices", self, other)

    first, second = SymbolicIndex(), SymbolicIndex()
    values = []

    def construct(label):
        value = object()
        values.append((label, value))
        return value

    family = IndexedFamily(NN, construct)
    # Directly enter the cache boundary, whose contract assumes normalized
    # indices: no membership assertion about these synthetic labels is made.
    a = family._value_at_normalized_index(first)
    b = family._value_at_normalized_index(second)
    assert a is not b
    assert family._value_at_normalized_index(first) is a
    assert family._value_at_normalized_index(second) is b
    assert len(values) == 2

    # An undecidable comparison with an earlier presentation must not
    # prevent reuse of a later, exactly identified cached presentation.
    third = SymbolicIndex()
    c = family._value_at_normalized_index(third)
    assert c is not a and c is not b
    assert family._value_at_normalized_index(third) is c
    assert len(values) == 3


def test_indexed_family_cache_reuses_only_decided_equal_labels() -> None:
    from sage_extensions.categories.sets.indexed_families import IndexedFamily

    class PresentedIndex:
        def __init__(self, key):
            self.key = key

        def __hash__(self):
            return hash(self.key)

        def __eq__(self, other):
            if not isinstance(other, PresentedIndex):
                return NotImplemented
            return self.key == other.key

    first = PresentedIndex("same")
    equal_presentation = PresentedIndex("same")
    distinct = PresentedIndex("different")
    selected = []

    def construct(label):
        value = object()
        selected.append((label, value))
        return value

    family = IndexedFamily(NN, construct)
    first_value = family._value_at_normalized_index(first)
    assert family._value_at_normalized_index(first) is first_value
    assert family._value_at_normalized_index(equal_presentation) is first_value
    distinct_value = family._value_at_normalized_index(distinct)
    assert distinct_value is not first_value
    assert family._value_at_normalized_index(distinct) is distinct_value
    assert len(selected) == 2


def test_indexed_family_cache_equality_is_not_limited_to_hash_buckets() -> None:
    from sage_extensions.categories.sets.indexed_families import IndexedFamily

    class PresentedIndex:
        def __init__(self, key, hash_value):
            self.key = key
            self.hash_value = hash_value

        def __hash__(self):
            return self.hash_value

        def __eq__(self, other):
            return isinstance(other, PresentedIndex) and self.key == other.key

    first = PresentedIndex("same", 1)
    equal_presentation = PresentedIndex("same", 2)
    selected = []
    family = IndexedFamily(NN, lambda label: selected.append(label) or object())

    first_value = family._value_at_normalized_index(first)
    assert family._value_at_normalized_index(equal_presentation) is first_value
    assert len(selected) == 1


def test_finite_product_of_additive_monoids_has_componentwise_addition() -> None:
    from sage_extensions.categories.group.magmas import AdditiveMonoids
    from sage_extensions.categories.sets.set_categories import (
        CartesianProductsOfAdditiveMonoids,
    )

    factor = AdditiveMonoids().an_object()
    product = Sets().product((factor, factor))
    assert product in CartesianProductsOfAdditiveMonoids()
    assert product in AdditiveMonoids()
    zero = product.zero()
    point = product(lambda index: factor.one())
    assert point + zero == point
    assert zero + point == point
    assert (point + point).component(product.index_set()(0)) == factor.one() + factor.one()
    projection = product.projection(product.index_set()(0))
    assert projection.parent() is AdditiveMonoids().Mor(product, factor)
    assert projection(zero) == factor.zero()
    assert projection(point + point) == projection(point) + projection(point)
    identity = AdditiveMonoids().Mor(factor, factor).identity()
    induced = product.from_maps(factor, lambda _index: identity)
    assert induced.parent() is AdditiveMonoids().Mor(factor, product)
    assert all(product.projection(index)(induced(factor.one())) == factor.one() for index in product.index_set())
    assert all(product.projection(index)(induced(factor.zero())) == factor.zero() for index in product.index_set())
    try:
        product.from_maps(factor, lambda _index: Sets().Mor(factor, factor).identity())
    except TypeError:
        pass
    else:
        raise AssertionError("untyped set maps incorrectly certified an additive product arrow")


def test_finite_set_product_and_coproduct_accept_stronger_mor_legs() -> None:
    from sage_extensions.categories.group.magmas import AdditiveMonoids

    factor = AdditiveMonoids().an_object()
    identity = AdditiveMonoids().Mor(factor, factor).identity()
    # Read the product explicitly through its Sets construction, even though
    # its factors also endow it with an additive-monoid structure.
    set_product = Sets().product((factor, Sets.Δ[0]))
    point = Sets.Δ[0]
    constant = Sets().Mor(point, factor)(lambda _p: factor.zero())
    induced = set_product.from_maps(point, lambda i: constant if int(i) == 0 else Sets().Mor(point, point).identity())
    assert set_product.projection(0)(induced(point(0))) == factor.zero()

    coproduct = Sets().coproduct((factor, factor))
    folded = coproduct.from_maps(factor, lambda _i: identity)
    for label in coproduct.index_set():
        assert folded(coproduct.injection(label)(factor.zero())) == factor.zero()


def test_finite_additive_product_factors_a_verified_nonconstant_diagram() -> None:
    from sage_extensions.categories.abstract_categories.functors import DiscreteCategory
    from sage_extensions.categories.functors.core import NaturalTransformation
    from sage_extensions.categories.group.magmas import AdditiveMonoids, AdditiveGroups
    from sage_extensions.categories.sets.indexed_families import indexed_family

    additive = AdditiveMonoids()
    first, second = additive.an_object(), AdditiveGroups().an_object()
    product = Sets().product((first, second))
    labels = product.index_set()
    shape = DiscreteCategory(labels)
    diagram = Cat().Mor(shape, additive).discrete_diagram(
        indexed_family(labels, lambda label: product.factor(label))
    )
    constant = Cat().Mor(shape, additive).constant_functor(first)
    legs = NaturalTransformation(
        constant, diagram,
        lambda obj: additive.Mor(first, product.factor(obj.value()))(
            lambda _point: product.factor(obj.value()).zero()
        ),
    )
    induced = product.from_maps(first, legs)
    assert induced.parent() is additive.Mor(first, product)
    for label in labels:
        assert product.projection(label)(induced(first.zero())) == product.factor(label).zero()


def test_finite_product_accepts_validated_nonconstant_diagram_cone() -> None:
    from sage_extensions.categories.abstract_categories.functors import DiscreteCategory
    from sage_extensions.categories.functors.core import NaturalTransformation
    from sage_extensions.categories.sets.indexed_families import indexed_family

    factors = (Sets.Δ[0], Sets.Δ[1])
    product = Sets().product(factors)
    index = product.index_set()
    shape = DiscreteCategory(index)
    diagram = Cat().Mor(shape, Sets()).discrete_diagram(
        indexed_family(index, lambda label: product.factor(label))
    )
    source = Sets.Δ[0]
    constant = Cat().Mor(shape, Sets()).constant_functor(source)
    legs = NaturalTransformation(
        constant, diagram,
        lambda obj: Sets().Mor(source, product.factor(obj.value()))(
            lambda _point: product.factor(obj.value())(0)
        ),
    )
    induced = product.from_maps(source, legs)
    for label in index:
        assert product.projection(label)(induced(source(0))) == product.factor(label)(0)


def test_finite_indexed_family_rank_cache_supplies_product_factors() -> None:
    from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
    from sage_extensions.categories.sets.indexed_families import indexed_family

    labels = finite_ordered_set(([0], [1]))
    factor = Sets.Δ[1]
    evaluations = []

    def selected(label):
        evaluations.append(label[0])
        return factor

    family = indexed_family(labels, selected)
    product = Sets().product(family)
    assert product.factor([0]) is factor
    assert product.factor([0]) is family(labels.ranking_map().inverse()(0))
    assert product.factor([1]) is factor
    assert tuple(value for value in family) == (factor, factor)
    assert tuple(family.items()) == ((labels.ranking_map().inverse()(0), factor),
                                    (labels.ranking_map().inverse()(1), factor))
    assert evaluations == [0, 1]
    point = product((factor(0), factor(1)))
    assert product.projection([0])(point) == factor(0)
    assert product.projection([1])(point) == factor(1)


def test_finite_family_hash_does_not_require_hashable_index_labels() -> None:
    from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
    from sage_extensions.categories.sets.indexed_families import indexed_family

    labels = finite_ordered_set(([0], [1]))
    first = indexed_family(labels, lambda label: Sets.Δ[1] if label[0] == 0 else Sets.Δ[2])
    second = indexed_family(labels, lambda label: Sets.Δ[1] if label[0] == 0 else Sets.Δ[2])
    assert first == second
    assert hash(first) == hash(second)

    # The values need not support hashing either: equality is their own
    # extensional relation, not the hashability of their representatives.
    unhashable_first = indexed_family(labels, lambda label: [label[0]])
    unhashable_second = indexed_family(labels, lambda label: [label[0]])
    assert unhashable_first == unhashable_second
    assert hash(unhashable_first) == hash(unhashable_second)


def test_infinite_constant_additive_product_retains_its_monoid_and_projections() -> None:
    from sage_extensions.categories.group.magmas import AdditiveMonoids
    from sage_extensions.categories.sets.indexed_families import indexed_family
    from sage_extensions.categories.sets.set_categories import (
        CartesianProductsOfAdditiveMonoids,
    )

    factor = AdditiveMonoids().an_object()
    family = indexed_family(NN, factor)
    product = Sets().product(family)
    assert family.constant_value() is factor
    assert factor in family
    assert Sets.Δ[1] not in family
    assert factor not in indexed_family(Sets.Δ[-1], factor)
    assert product in CartesianProductsOfAdditiveMonoids()
    assert product in AdditiveMonoids()
    varying = product(lambda index: factor(int(index)))
    unit = product(lambda index: factor.one())
    zero = product.zero()
    projection = product.projection(NN(2))
    assert projection.parent() is AdditiveMonoids().Mor(product, factor)
    assert projection(varying) != projection(product(lambda index: factor.zero()))
    assert projection(varying + zero) == projection(varying)
    assert projection(varying + unit) == projection(varying) + projection(unit)
    assert projection(zero) == factor.zero()

    nonmonoid = Sets().product(indexed_family(NN, Sets.Δ[1]))
    assert nonmonoid not in CartesianProductsOfAdditiveMonoids()
    assert nonmonoid not in AdditiveMonoids()
    try:
        indexed_family(NN, Sets.Δ[1], value_category=AdditiveMonoids())
    except ValueError:
        pass
    else:
        raise AssertionError("an infinite constant nonmonoid was admitted as additive")


def test_infinite_constant_additive_product_universal_morphism() -> None:
    """The categorical cone has all its projection equations, not just object placement."""
    from sage_extensions.categories.abstract_categories.functors import DiscreteCategory
    from sage_extensions.categories.functors.core import NaturalTransformation
    from sage_extensions.categories.group.magmas import AdditiveMonoids
    from sage_extensions.categories.sets.indexed_families import indexed_family

    additive = AdditiveMonoids()
    factor = additive.an_object()
    index = DiscreteCategory(NN)
    constant = Cat().Mor(index, additive).constant_functor(factor)
    product = Sets().product(indexed_family(NN, factor))
    identity = additive.Mor(factor, factor).identity()
    legs = NaturalTransformation(constant, constant, lambda _obj: identity)
    factorization = product.from_maps(factor, legs)
    assert factorization.parent() is additive.Mor(factor, product)
    for label in (NN(0), NN(2), NN(9)):
        for value in (factor.zero(), factor.one()):
            assert product.projection(label)(factorization(value)) == identity(value)

    # A Set arrow is not an additive-monoid cone leg merely because its
    # underlying function has the right domain and codomain.
    wrong = NaturalTransformation(
        constant, constant,
        lambda _obj: Sets().Mor(factor, factor).identity(),
    )
    invalid_factorization = product.from_maps(factor, wrong)
    try:
        product.projection(NN(4))(invalid_factorization(factor.one()))
    except TypeError:
        pass
    else:
        raise AssertionError("a Set-valued component falsely supplied an additive cone")


def test_unproved_infinite_value_category_cannot_place_monoid_product() -> None:
    from sage_extensions.categories.group.magmas import AdditiveMonoids
    from sage_extensions.categories.sets.indexed_families import indexed_family
    from sage_extensions.categories.sets.set_categories import CartesianProductsOfAdditiveMonoids

    factor = AdditiveMonoids().an_object()
    for value in (lambda index: factor, lambda index: factor if int(index) % 2 == 0 else Sets.Δ[1]):
        try:
            indexed_family(NN, value, value_category=AdditiveMonoids())
        except TypeError:
            pass
        else:
            raise AssertionError("unchecked infinite callback falsely established category-valued diagram")
    try:
        indexed_family(Sets.Δ[0], lambda _index: Sets.Δ[1], value_category=AdditiveMonoids())
    except ValueError:
        pass
    else:
        raise AssertionError("nonmonoid set admitted to an additive-monoid diagram")


def test_unchecked_discrete_diagram_cannot_certify_infinite_factors() -> None:
    from sage_extensions.categories.abstract_categories.functors import DiscreteCategory
    from sage_extensions.categories.group.magmas import AdditiveMonoids
    from sage_extensions.categories.sets.indexed_families import indexed_family

    factor = AdditiveMonoids().an_object()
    index_category = DiscreteCategory(NN)
    raw = indexed_family(NN, lambda index: factor if int(index) % 2 == 0 else Sets.Δ[1])
    unchecked = Cat().Mor(index_category, AdditiveMonoids()).discrete_diagram(raw)
    try:
        indexed_family(NN, unchecked)
    except TypeError:
        pass
    else:
        raise AssertionError("unchecked infinite diagram claimed an invalid additive placement")

    selected = Cat().Mor(index_category, AdditiveMonoids()).constant_functor(factor)
    family = indexed_family(NN, selected)
    product = Sets().product(family)
    assert product in AdditiveMonoids()
    assert product.projection(NN(3))(product.zero()) == factor.zero()


def test_finite_diagram_restricted_to_infinite_parity_family() -> None:
    from sage_extensions.categories.abstract_categories.functors import DiscreteCategory
    from sage_extensions.categories.group.magmas import AdditiveMonoids, AdditiveGroups
    from sage_extensions.categories.sets.indexed_families import indexed_family
    from sage_extensions.categories.sets.set_categories import CartesianProductsOfAdditiveMonoids

    labels = Sets.Δ[1]
    finite_index = DiscreteCategory(labels)
    infinite_index = DiscreteCategory(NN)
    even = AdditiveMonoids().an_object()
    odd = AdditiveGroups().an_object()
    diagram = Cat().Mor(finite_index, AdditiveMonoids()).discrete_diagram(
        indexed_family(labels, lambda i: even if i == labels(0) else odd)
    )
    parity = Cat().Mor(infinite_index, finite_index).from_object_map(
        lambda n: labels(int(n) % 2)
    )
    selected = diagram.restrict(parity)
    family = indexed_family(NN, selected)
    product = Sets().product(family)
    assert family.selected_diagram() is selected
    assert product in CartesianProductsOfAdditiveMonoids()
    assert family(NN(0)) is even and family(NN(1)) is odd
    point = product(lambda n: family(n)(int(n)))
    unit = product(lambda n: family(n).one())
    projection = product.projection(NN(3))
    assert projection.parent() is AdditiveMonoids().Mor(product, odd)
    assert projection(point + unit) == projection(point) + projection(unit)
    assert projection(product.zero()) == odd.zero()

    # The nonconstant product also has the actual AddMon universal arrow.
    # The common source is the even factor, and its selected zero maps give
    # compatible legs into both kinds of factors without identifying them.
    from sage_extensions.categories.functors.core import NaturalTransformation

    source_diagram = Cat().Mor(infinite_index, AdditiveMonoids()).constant_functor(even)
    components = NaturalTransformation(
        source_diagram, selected,
        lambda obj: AdditiveMonoids().Mor(even, family(obj.value()))(
            lambda _value: family(obj.value()).zero()
        ),
    )
    induced = product.from_maps(even, components)
    assert induced.parent() is AdditiveMonoids().Mor(even, product)
    for index in (NN(0), NN(1), NN(6), NN(7)):
        assert product.projection(index)(induced(even.one())) == family(index).zero()

    wrong_components = NaturalTransformation(
        source_diagram, selected,
        lambda obj: Sets().Mor(even, family(obj.value()))(
            lambda _value: family(obj.value()).zero()
        ),
    )
    wrong_induced = product.from_maps(even, wrong_components)
    try:
        product.projection(NN(3))(wrong_induced(even.one()))
    except TypeError:
        pass
    else:
        raise AssertionError("a Set-map component falsely certified the nonconstant additive product")

    unchecked = Cat().Mor(infinite_index, AdditiveMonoids()).discrete_diagram(
        indexed_family(NN, lambda n: even if int(n) % 2 == 0 else Sets.Δ[1])
    )
    identity = Cat().Mor(infinite_index, infinite_index).from_object_map(lambda n: n)
    for candidate in (unchecked, unchecked.restrict(identity)):
        try:
            indexed_family(NN, candidate)
        except TypeError:
            pass
        else:
            raise AssertionError("unchecked infinite diagram incorrectly certified additive placement")


def test_infinite_indexed_functor_map_retains_canonical_category_inclusion() -> None:
    """A diagram in AddGroups maps through AddMon -> Sets without losing its arrows."""
    from sage_extensions.categories.abstract_categories.functors import DiscreteCategory
    from sage_extensions.categories.group.magmas import AdditiveGroups, AdditiveMonoids
    from sage_extensions.categories.sets.indexed_families import indexed_family

    shape = DiscreteCategory(NN)
    group = AdditiveGroups().an_object()
    diagram = Cat().Mor(shape, AdditiveGroups()).constant_functor(group)
    family = indexed_family(NN, diagram)
    forget_structure = AdditiveMonoids().inclusion_into(Sets())
    mapped = family.map(forget_structure)
    assert mapped.selected_diagram() is not None
    assert mapped.selected_diagram().codomain() is Sets()
    assert mapped.value(NN(4)) is group
    assert mapped.selected_diagram()(shape.identity(shape.object(NN(4)))).domain() is group


def test_the_product_of_two_and_three_points_has_six_points() -> None:
    two = Sets.Δ[1]
    three = Sets.Δ[2]
    product = Sets().product((two, three))
    corner = product((two(1), three(2)))

    assert product.cardinality() == cardinal(6)
    assert sum(1 for _point in product) == 6
    assert corner == product((two(1), three(2)))
    assert corner != product((two(0), three(2)))


def test_the_disjoint_union_of_two_and_three_points_has_five_points() -> None:
    union = Sets().coproduct((Sets.Δ[1], Sets.Δ[2]))

    assert union.cardinality() == cardinal(5)
    assert sum(1 for _point in union) == 5


def test_coproduct_induced_map_requires_compatible_component_morphisms() -> None:
    source = Sets().coproduct((Sets.Δ[0], Sets.Δ[1]))
    target = Sets.Δ[1]
    components = lambda index: Sets().Mor(source.cofactor(index), target)(
        lambda point: target(0) if index == source.index_set()(0) else target(1)
    )
    induced = source.from_maps(target, components)
    assert induced.parent() is Sets().Mor(source, target)
    from sage_extensions.categories.abstract_categories.functors import DiscreteCategory
    from sage_extensions.categories.functors.core import NaturalTransformation
    shape = DiscreteCategory(source.index_set())
    summands = source.family().selected_diagram()
    if summands is None:
        summands = Cat().Mor(shape, Sets()).discrete_diagram(source.family())
    constant_target = Cat().Mor(shape, Sets()).constant_functor(target)
    typed = NaturalTransformation(summands, constant_target,
                                  lambda obj: components(obj.value()))
    induced_typed = source.from_maps(target, typed)
    assert induced_typed.parent() is Sets().Mor(source, target)
    for index in source.index_set():
        component = components(index)
        for point in source.cofactor(index):
            assert induced(source.injection(index)(point)) == component(point)
            assert induced_typed(source.injection(index)(point)) == component(point)

    wrong = Sets().Mor(target, target).identity()
    try:
        source.from_maps(target, lambda _index: wrong)
    except TypeError:
        pass
    else:
        raise AssertionError("coproduct accepted a map with incorrect component endpoints")

    from sage_extensions.categories.sets.indexed_families import indexed_family

    infinite = Sets().coproduct(indexed_family(NN, Sets.Δ[0]))
    try:
        infinite.from_maps(
            Sets.Δ[0],
            lambda _index: Sets().Mor(Sets.Δ[0], Sets.Δ[0]).identity(),
        )
    except TypeError:
        pass
    else:
        raise AssertionError("unchecked infinite coproduct component callback admitted")

    from sage_extensions.categories.abstract_categories.functors import DiscreteCategory
    from sage_extensions.categories.functors.core import NaturalTransformation

    shape = DiscreteCategory(NN)
    constant = Cat().Mor(shape, Sets()).constant_functor(Sets.Δ[0])
    components = NaturalTransformation(
        constant, constant,
        lambda _object: Sets().Mor(Sets.Δ[0], Sets.Δ[0]).identity(),
    )
    induced = infinite.from_maps(Sets.Δ[0], components)
    assert induced.parent() is Sets().Mor(infinite, Sets.Δ[0])
    wrong_source = Cat().Mor(shape, Sets()).constant_functor(Sets.Δ[1])
    unrelated = NaturalTransformation(
        wrong_source, constant,
        lambda _object: Sets().Mor(Sets.Δ[1], Sets.Δ[0])(
            lambda _value: Sets.Δ[0](0)
        ),
    )
    try:
        infinite.from_maps(Sets.Δ[0], unrelated)
    except ValueError:
        pass
    else:
        raise AssertionError("a cocone over a different source diagram was admitted")
    for index in (NN(0), NN(1), NN(5)):
        inclusion = infinite.injection(index)
        assert induced(inclusion(Sets.Δ[0](0))) == components.component(shape.object(index))(Sets.Δ[0](0))
    bad = NaturalTransformation(
        constant, constant,
        lambda _object: Sets().Mor(Sets.Δ[1], Sets.Δ[0])(lambda _value: Sets.Δ[0](0)),
    )
    bad_induced = infinite.from_maps(Sets.Δ[0], bad)
    try:
        bad_induced(infinite.injection(NN(1))(Sets.Δ[0](0)))
    except TypeError:
        pass
    else:
        raise AssertionError("an incorrectly typed natural-transformation component was admitted")


def test_componentwise_coproduct_morphism_checks_its_source_and_target_summands() -> None:
    from sage_extensions.categories.sets.set_categories import _coproduct_morphism

    left = Sets.Δ[1]
    right = Sets.Δ[2]
    source = Sets().coproduct((left, right))
    target = Sets().coproduct((right, left))
    index_set = source.index_set()
    first = Sets().Mor(left, right)(lambda point: right(int(point)))
    second = Sets().Mor(right, left)(lambda point: left(int(point) % 2))
    arrow = _coproduct_morphism(source, target, lambda index: first if index == index_set(0) else second)
    assert arrow.parent() is Sets().Mor(source, target)
    for index in index_set:
        component = first if index == index_set(0) else second
        for point in source.cofactor(index):
            assert arrow(source.injection(index)(point)) == target.injection(index)(component(point))

    try:
        _coproduct_morphism(source, target, lambda _index: first)
    except TypeError:
        pass
    else:
        raise AssertionError("a component with wrong coproduct endpoints was admitted")


def test_finite_coproduct_rank_layer_has_direct_inverse() -> None:
    factors = (Sets.Δ[1], Sets.Δ[3], Sets.Δ[0])
    coproduct = Sets().coproduct(factors)
    listing = tuple(coproduct)
    ranking = coproduct.ranking_map()
    assert len(listing) == 7
    for position, element in enumerate(listing):
        assert ranking(element) == position
        assert ranking.inverse()(position) == element


def test_empty_index_coproduct_enumeration_terminates() -> None:
    empty = Sets().coproduct(())
    assert empty.cardinality() == cardinal(0)
    assert tuple(empty) == ()


def test_constant_countable_coproduct_has_diagonal_enumeration() -> None:
    from sage_extensions.categories.sets.indexed_families import indexed_family

    coproduct = Sets().coproduct(indexed_family(NN, Sets.Δ[1]))
    assert coproduct in EnumeratedSets()
    ranking = coproduct.ranking_map()
    for index in (0, 1, 3):
        for point in (0, 1):
            element = coproduct.injection(NN(index))(Sets.Δ[1](point))
            assert ranking.inverse()(ranking(element)) == element

    empty = Sets().coproduct(indexed_family(NN, Sets.Δ[-1]))
    assert empty in EnumeratedSets()
    assert tuple(empty) == ()


def test_selected_nonconstant_countable_coproduct_is_enumerated() -> None:
    from sage_extensions.categories.abstract_categories.functors import DiscreteCategory
    from sage_extensions.categories.sets.indexed_families import indexed_family

    labels = Sets.Δ[1]
    finite_shape = DiscreteCategory(labels)
    infinite_shape = DiscreteCategory(NN)
    factor_diagram = Cat().Mor(finite_shape, EnumeratedSets()).discrete_diagram(
        indexed_family(labels, lambda i: Sets.Δ[0] if i == labels(0) else Sets.Δ[1])
    )
    parity = Cat().Mor(infinite_shape, finite_shape).from_object_map(
        lambda n: labels(int(n) % 2)
    )
    family = indexed_family(NN, factor_diagram.restrict(parity))
    coproduct = Sets().coproduct(family)
    assert coproduct in EnumeratedSets()
    ranking = coproduct.ranking_map()
    for index in (0, 1, 3):
        point = coproduct.injection(NN(index))(family(NN(index))(0))
        assert ranking.inverse()(ranking(point)) == point




def test_mixed_finite_infinite_coproduct_rank_uses_summand_layers() -> None:
    coproduct = Sets().coproduct((Sets.Δ[1], NN, Sets.Δ[0]))
    ranking = coproduct.ranking_map()
    assert ranking(coproduct.injection(0)(Sets.Δ[1](0))) == 0
    assert ranking(coproduct.injection(1)(NN(0))) == 1
    assert ranking(coproduct.injection(2)(Sets.Δ[0](0))) == 2
    assert ranking(coproduct.injection(1)(NN(1000))) == 1003
    assert ranking.inverse()(1003) == coproduct.injection(1)(NN(1000))


def test_the_square_of_the_natural_numbers_is_countable_and_listed_by_diagonals() -> None:
    square = Sets().product((NN, NN))
    listing = iter(square)
    first_six = [next(listing) for _step in range(6)]

    assert square.cardinality() == aleph0
    assert first_six[0] == square((NN(0), NN(0)))
    assert all(
        square((NN(a), NN(b))) in first_six for a in range(3) for b in range(3) if a + b <= 2
    )


def test_the_diagonal_enumeration_of_the_square_of_the_naturals_is_ranked() -> None:
    square = Sets().product((NN, NN))
    ranking = square.ranking_map()
    listing = iter(square)

    assert [ranking(next(listing)) for _step in range(6)] == [0, 1, 2, 3, 4, 5]


def test_the_natural_numbers_plus_two_points_are_countable_and_enumerated() -> None:
    union = Sets().coproduct((NN, Sets.Δ[1]))
    listing = iter(union)
    first_five = [next(listing) for _step in range(5)]

    assert union.cardinality() == aleph0
    assert all(first_five[i] != first_five[j] for i in range(5) for j in range(i))


def test_the_product_functor_applies_a_transposition_to_the_first_coordinate() -> None:
    two = Sets.Δ[1]
    three = Sets.Δ[2]
    pairs = Cat().product([Sets(), Sets()])
    transposition = Sets().Mor(two, two)(lambda x: two(1) if x == 0 else two(0))
    identity = Sets().Mor(three, three).identity()
    induced = Sets().product_functor()(pairs.Mor(pairs(two, three), pairs(two, three))((transposition, identity)))
    product = induced.domain()

    assert induced(product((two(1), three(2)))) == product((two(0), three(2)))
    assert induced(product((two(0), three(0)))) == product((two(1), three(0)))


def test_componentwise_product_morphism_rejects_wrong_factor_map() -> None:
    from sage_extensions.categories.sets.set_categories import _cartesian_product_morphism

    small, large = Sets.Δ[1], Sets.Δ[2]
    source = Sets().product((small, large))
    target = Sets().product((large, small))
    labels = source.index_set()
    first = Sets().Mor(small, large)(lambda x: large(int(x)))
    second = Sets().Mor(large, small)(lambda x: small(int(x) % 2))
    induced = _cartesian_product_morphism(source, target, lambda i: first if i == labels(0) else second)
    assert induced.parent() is Sets().Mor(source, target)
    corner = source((small(1), large(2)))
    assert induced(corner).component(labels(0)) == first(small(1))
    assert induced(corner).component(labels(1)) == second(large(2))
    try:
        _cartesian_product_morphism(source, target, lambda _i: first)
    except TypeError:
        pass
    else:
        raise AssertionError("product admitted a component with incorrect target factor")


def test_componentwise_set_maps_accept_additive_diagrams() -> None:
    from sage_extensions.categories.abstract_categories.functors import DiscreteCategory
    from sage_extensions.categories.functors.core import NaturalTransformation
    from sage_extensions.categories.group.magmas import AdditiveMonoids
    from sage_extensions.categories.sets.indexed_families import indexed_family
    from sage_extensions.categories.sets.set_categories import (
        _cartesian_product_morphism, _coproduct_morphism,
    )

    additive = AdditiveMonoids()
    factor = additive.an_object()
    diagram = Cat().Mor(DiscreteCategory(NN), additive).constant_functor(factor)
    legs = NaturalTransformation(diagram, diagram, lambda _obj: additive.Mor(factor, factor).identity())
    family = indexed_family(NN, diagram)
    product = Sets().product(family)
    coproduct = Sets().coproduct(family)
    product_map = _cartesian_product_morphism(product, product, legs)
    coproduct_map = _coproduct_morphism(coproduct, coproduct, legs)
    for index in (NN(0), NN(3)):
        assert product_map(product.zero()).component(index) == factor.zero()
        point = coproduct.injection(index)(factor.zero())
        assert coproduct_map(point) == point


def test_finite_componentwise_set_maps_inherit_additive_morphisms() -> None:
    from sage_extensions.categories.group.magmas import AdditiveMonoids
    from sage_extensions.categories.sets.set_categories import (
        _cartesian_product_morphism, _coproduct_morphism,
    )

    additive = AdditiveMonoids()
    factor = additive.an_object()
    identity = additive.Mor(factor, factor).identity()
    product = Sets().product((factor, factor))
    coproduct = Sets().coproduct((factor, factor))
    product_map = _cartesian_product_morphism(product, product, lambda _i: identity)
    coproduct_map = _coproduct_morphism(coproduct, coproduct, lambda _i: identity)
    for index in product.index_set():
        assert product_map(product.zero()).component(index) == factor.zero()
        selected = coproduct.injection(index)(factor.zero())
        assert coproduct_map(selected) == selected


def test_infinite_componentwise_set_maps_use_a_selected_natural_transformation() -> None:
    from sage_extensions.categories.abstract_categories.functors import DiscreteCategory
    from sage_extensions.categories.functors.core import NaturalTransformation
    from sage_extensions.categories.sets.indexed_families import indexed_family
    from sage_extensions.categories.sets.set_categories import (
        _cartesian_product_morphism, _coproduct_morphism,
    )

    point = Sets.Δ[0]
    index_category = DiscreteCategory(NN)
    diagram = Cat().Mor(index_category, Sets()).constant_functor(point)
    components = NaturalTransformation(
        diagram, diagram, lambda _index: Sets().Mor(point, point).identity()
    )
    family = indexed_family(NN, point)
    product = Sets().product(family)
    coproduct = Sets().coproduct(family)
    product_map = _cartesian_product_morphism(product, product, components)
    coproduct_map = _coproduct_morphism(coproduct, coproduct, components)
    section = product(lambda _index: point(0))
    assert product_map.parent() is Sets().Mor(product, product)
    assert coproduct_map.parent() is Sets().Mor(coproduct, coproduct)
    for index in (NN(0), NN(1), NN(5)):
        assert product_map(section).component(index) == section.component(index)
        selected = coproduct.injection(index)(point(0))
        assert coproduct_map(selected) == selected
    other = Sets.Δ[1]
    wrong_diagram = Cat().Mor(index_category, Sets()).constant_functor(other)
    wrong = NaturalTransformation(
        wrong_diagram, wrong_diagram,
        lambda _index: Sets().Mor(other, other).identity(),
    )
    for construct in (
        lambda: _cartesian_product_morphism(product, product, wrong),
        lambda: _coproduct_morphism(coproduct, coproduct, wrong),
    ):
        try:
            construct()
        except ValueError:
            pass
        else:
            raise AssertionError("componentwise arrow accepted a different factor object")
