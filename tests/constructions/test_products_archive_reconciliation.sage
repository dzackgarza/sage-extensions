r"""Archive reconciliation for product and coproduct universal constructions.

The archived products module represented chosen product cones and coproduct
cocones explicitly.  The live construction keeps the same mathematical data
on the product/coproduct object itself: factors, projections/injections and the
unique mediator assembled by ``from_maps``.
"""

from sage_extensions.all import Sets

ARCHIVE_RECONCILIATION = {
    "archive_module": "preamble/categories/abstract_categories/products.sage",
    "live_owner": "sage_extensions/categories/abstract_categories/products.py",
    "owner_overrides": {
        "Sets.product": "sage_extensions/categories/sets/set_categories.py",
        "Sets.coproduct": "sage_extensions/categories/sets/set_categories.py",
    },
    "disposition": "reconciled-live-owner",
}


def test_archived_product_cone_is_the_live_product_with_its_universal_map() -> None:
    two = Sets.Δ[1]
    three = Sets.Δ[2]
    product = Sets().product((two, three))
    source = Sets.Δ[2]
    first = Sets().Mor(source, two)(lambda point: two(int(point) % 2))
    second = Sets().Mor(source, three).identity()

    mediator = product.from_maps(
        source,
        lambda index: first if int(index) == 0 else second,
    )

    assert product.factor(0) is two
    assert product.factor(1) is three
    assert product.projection(0).codomain() is two
    assert product.projection(1).codomain() is three
    assert mediator.domain() is source
    assert mediator.codomain() is product
    assert product.projection(0) * mediator == first
    assert product.projection(1) * mediator == second


def test_archived_coproduct_cocone_is_the_live_coproduct_with_its_universal_map() -> None:
    two = Sets.Δ[1]
    three = Sets.Δ[2]
    coproduct = Sets().coproduct((two, three))
    target = Sets.Δ[2]
    first = Sets().Mor(two, target)(lambda point: target(int(point)))
    second = Sets().Mor(three, target).identity()

    mediator = coproduct.from_maps(
        target,
        lambda index: first if int(index) == 0 else second,
    )

    assert coproduct.cofactor(0) is two
    assert coproduct.cofactor(1) is three
    assert coproduct.injection(0).domain() is two
    assert coproduct.injection(1).domain() is three
    assert mediator.domain() is coproduct
    assert mediator.codomain() is target
    assert mediator * coproduct.injection(0) == first
    assert mediator * coproduct.injection(1) == second
