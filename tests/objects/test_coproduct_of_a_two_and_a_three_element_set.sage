from sage_extensions.all import *


def factors():
    return Sets.Δ[1], Sets.Δ[2]


def coproduct():
    return Sets().coproduct(factors())


def test_the_category_and_the_object_constructions_agree() -> None:
    two, three = factors()
    assert two.coproduct_with(three) == coproduct()


def test_the_categories_of_the_coproduct() -> None:
    assert coproduct() in Sets()
    assert coproduct() in FiniteSets()


def test_proved_finite_factors_give_finite_products_and_coproducts() -> None:
    r"""A finite family of finite sets has finite limit and colimit."""
    subset = Sets().condition_set(Sets.Δ[2], lambda point: True)
    assert subset.is_finite() is True
    factors = (subset, Sets.Δ[1])
    assert Sets().product(factors) in FiniteSets()
    assert Sets().coproduct(factors) in FiniteSets()


def test_zero_factor_annihilates_a_product_with_an_infinite_factor() -> None:
    product = Sets().product((Sets.Δ[-1], NN))
    assert product in FiniteSets()
    assert product.cardinality() == 0


def test_the_coproduct_is_the_disjoint_union() -> None:
    assert coproduct().cardinality() == 5


def test_the_injections() -> None:
    two, three = factors()
    union = coproduct()
    assert union.injection(0).domain() is two
    assert union.injection(1).domain() is three
    assert union.injection(0).is_injective()
    assert union.injection(1).is_injective()
    assert union.injection(0)(two(0)) != union.injection(1)(three(0))


def test_the_coproduct_has_one_endomorphism_category() -> None:
    union = coproduct()
    endomorphisms = union.Mor(union)
    identity = endomorphisms.identity()
    assert endomorphisms in Cat()
    assert union.Mor(union) is endomorphisms
    assert identity * identity == identity
