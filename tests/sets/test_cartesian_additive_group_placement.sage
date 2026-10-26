r"""Additive-group placement requires componentwise inverses, not only zero and addition."""

from sage_extensions.all import *  # noqa: F401,F403


def test_additive_group_product_category_supplies_a_group_object() -> None:
    from sage_extensions.categories.sets.set_categories import CartesianProductsOfAdditiveGroups

    product = CartesianProductsOfAdditiveGroups().an_object()
    assert product in CartesianProductsOfAdditiveGroups()
    assert product in AdditiveGroups()
    assert product.zero() + (-product.zero()) == product.zero()
    for label in product.index_set():
        assert product.factor(label) in AdditiveGroups()


def test_infinite_constant_additive_group_product_has_pointwise_inverses() -> None:
    product = Sets().product(indexed_family(NN, ZZ))
    assert product in AdditiveGroups()
    assert product in AdditiveGroups().AdditiveCommutative()
    section = product(lambda index: ZZ(int(index) + 1))
    opposite = -section
    other = product(lambda index: ZZ(2 * int(index)))
    assert product.projection(NN(3))(section + other) == product.projection(NN(3))(other + section)
    for position in (0, 1, 5):
        label = NN(position)
        projection = product.projection(label)
        assert projection.parent() is AdditiveGroups().Mor(product, ZZ)
        assert projection(opposite) == -projection(section)
        assert projection(section + opposite) == ZZ.zero()


def test_empty_additive_product_has_trivial_group_structure() -> None:
    # The empty product is terminal in additive monoids and additive groups;
    # the vacuous all-factor hypotheses must give a genuine group, not merely
    # a set with one element.
    empty = Sets().product(indexed_family(Sets.Δ[-1], ZZ))
    assert empty in AdditiveGroups()
    assert empty in AdditiveGroups().AdditiveCommutative()
    unit = empty.zero()
    assert -unit == unit
    assert unit + unit == unit


def test_infinite_constant_additive_monoid_does_not_gain_inverses() -> None:
    product = Sets().product(indexed_family(NN, NN))
    assert product in AdditiveMonoids()
    assert product in AdditiveMonoids().AdditiveCommutative()
    assert product not in AdditiveGroups()
    left = product(lambda n: NN(int(n)))
    right = product(lambda n: NN(2 * int(n) + 1))
    for position in (0, 2, 5):
        projection = product.projection(NN(position))
        assert projection(left + right) == projection(right + left)


def test_infinite_group_cone_factors_as_an_additive_group_morphism() -> None:
    from sage_extensions.categories.abstract_categories.functors import DiscreteCategory
    from sage_extensions.categories.functors.core import NaturalTransformation

    groups = AdditiveGroups()
    index = DiscreteCategory(NN)
    constant = Cat().Mor(index, groups).constant_functor(ZZ)
    identity = groups.Mor(ZZ, ZZ).identity()
    legs = NaturalTransformation(constant, constant, lambda _index: identity)
    product = Sets().product(indexed_family(NN, ZZ))
    diagonal = product.from_maps(ZZ, legs)
    assert diagonal.parent() is groups.Mor(ZZ, product)
    for position in (0, 3, 9):
        projection = product.projection(NN(position))
        assert projection(diagonal(ZZ(-5))) == ZZ(-5)
        assert projection(diagonal(-ZZ(5))) == -projection(diagonal(ZZ(5)))


def test_group_product_retains_monoid_universal_property() -> None:
    product = Sets().product((ZZ, ZZ))
    source = NN
    additive = AdditiveMonoids()
    inclusion = additive.Mor(source, ZZ)(lambda n: ZZ(int(n)))
    induced = product.from_maps(source, lambda _index: inclusion)
    assert induced.parent() is additive.Mor(source, product)
    for label in product.index_set():
        assert product.projection(label)(induced(source(3))) == ZZ(3)


def test_infinite_group_product_retains_monoid_cones() -> None:
    from sage_extensions.categories.abstract_categories.functors import DiscreteCategory
    from sage_extensions.categories.functors.core import NaturalTransformation

    index = DiscreteCategory(NN)
    additive = AdditiveMonoids()
    source_diagram = Cat().Mor(index, additive).constant_functor(NN)
    target_diagram = Cat().Mor(index, additive).constant_functor(ZZ)
    inclusion = additive.Mor(NN, ZZ)(lambda n: ZZ(int(n)))
    components = NaturalTransformation(source_diagram, target_diagram, lambda _index: inclusion)
    product = Sets().product(indexed_family(NN, ZZ))
    induced = product.from_maps(NN, components)
    assert induced.parent() is additive.Mor(NN, product)
    for position in (0, 2, 7):
        projection = product.projection(NN(position))
        assert projection(induced(NN(4))) == ZZ(4)
        assert projection(induced(NN(2) + NN(3))) == ZZ(5)


def test_mixed_finite_monoid_product_is_not_an_additive_group() -> None:
    mixed = Sets().product((ZZ, NN))
    assert mixed in AdditiveMonoids()
    assert mixed in AdditiveMonoids().AdditiveCommutative()
    assert mixed not in AdditiveGroups()
    assert mixed not in AdditiveGroups().AdditiveCommutative()
    section = mixed((ZZ(-2), NN(3)))
    assert mixed.projection(mixed.index_set()(0))(section) == ZZ(-2)
    assert mixed.projection(mixed.index_set()(1))(section) == NN(3)


def test_opaque_infinite_callback_does_not_claim_additive_group_structure() -> None:
    opaque = Sets().product(indexed_family(NN, lambda _index: ZZ))
    assert opaque not in AdditiveGroups()
    assert opaque not in AdditiveMonoids()


def test_nonconstant_infinite_group_diagram_retains_group_structure() -> None:
    from sage_extensions.categories.abstract_categories.functors import DiscreteCategory
    from sage_extensions.categories.functors.core import NaturalTransformation

    labels = Sets.Δ[1]
    finite_index = DiscreteCategory(labels)
    infinite_index = DiscreteCategory(NN)
    groups = AdditiveGroups()
    diagram = Cat().Mor(finite_index, groups).discrete_diagram(
        indexed_family(labels, lambda label: ZZ if label == labels(0) else QQ)
    )
    parity = Cat().Mor(infinite_index, finite_index).from_object_map(
        lambda n: labels(int(n) % 2)
    )
    family = indexed_family(NN, diagram.restrict(parity))
    product = Sets().product(family)
    assert product in AdditiveGroups()
    section = product(lambda label: family(label)(int(label) + 1))
    for position in (0, 1, 4, 5):
        projection = product.projection(NN(position))
        assert projection.parent() is groups.Mor(product, family(NN(position)))
        assert projection(-section) == -projection(section)
        assert projection(section + (-section)) == family(NN(position)).zero()

    constant_source = Cat().Mor(infinite_index, groups).constant_functor(ZZ)
    legs = NaturalTransformation(
        constant_source, family.selected_diagram(),
        lambda obj: groups.Mor(ZZ, family(obj.value()))(
            lambda integer: family(obj.value())(int(integer))
        ),
    )
    diagonal = product.from_maps(ZZ, legs)
    assert diagonal.parent() is groups.Mor(ZZ, product)
    for position in (0, 1, 4, 5):
        label = NN(position)
        projection = product.projection(label)
        assert projection(diagonal(ZZ(-3))) == family(label)(-3)
        assert projection(diagonal(ZZ(3) + ZZ(-3))) == family(label).zero()
