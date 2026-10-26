r"""Finite products and coproducts expose their universal structure maps."""

from sage_extensions.all import *  # noqa: F401,F403


def test_cartesian_product_components_and_universal_map() -> None:
    three = Set((1, 2, 3))
    two = Sets.Δ[1]
    product = Sets().product((three, two))
    point = product((three(2), two(1)))

    assert product.has_finite_index_set()
    assert product.factor(0) is three
    assert product.factor(1) is two
    assert point.component(0) == three(2)
    assert point.component(1) == two(1)
    assert product.projection(0)(point) == three(2)
    assert product.projection(1)(point) == two(1)

    source = Set(("x",))
    assembled = product.from_maps(
        source,
        lambda index: Sets().Mor(source, product.factor(index))(
            lambda _value: three(1) if index == 0 else two(0)
        ),
    )
    assert assembled(source("x")).component(0) == three(1)
    assert assembled(source("x")).component(1) == two(0)


def test_coproduct_injections_and_universal_map() -> None:
    three = Set((1, 2, 3))
    two = Sets.Δ[1]
    coproduct = Sets().coproduct((three, two))
    point = coproduct.injection(1)(two(0))

    assert coproduct.cofactor(0) is three
    assert coproduct.cofactor(1) is two
    assert point.summand_index() == 1
    assert point.summand_element() == two(0)

    target = Set(("left", "right"))
    folded = coproduct.from_maps(
        target,
        lambda index: Sets().Mor(coproduct.cofactor(index), target)(
            lambda _value: target("left") if index == 0 else target("right")
        ),
    )
    assert folded(coproduct.injection(0)(three(1))) == target("left")
    assert folded(coproduct.injection(1)(two(1))) == target("right")
