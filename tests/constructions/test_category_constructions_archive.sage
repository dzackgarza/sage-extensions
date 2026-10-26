r"""Archive reconciliation for opposite and product categories.

The archived constructions were constructions in Cat, not merely object
wrappers: opposite composition reverses the underlying arrows and product
composition acts componentwise.  The live owner retains those Hom-level
semantics and checks each factor's actual morphism category.
"""

import pytest

from sage_extensions.categories.abstract_categories.cat import Cat
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
from sage_extensions.categories.sets.set_categories import Sets

ARCHIVE_RECONCILIATION = {
    "archive_module": "preamble/categories/abstract_categories/category_constructions.sage",
    "live_owner": "sage_extensions/categories/abstract_categories/category_constructions.py",
    "disposition": "reconciled-live-owner",
}


def _two_points_and_maps():
    points = finite_ordered_set(("a", "b"))
    swap = Sets().Mor(points, points)(lambda point: "b" if point == "a" else "a")
    collapse = Sets().Mor(points, points)(lambda _point: "a")
    return points, swap, collapse


def test_opposite_category_reverses_underlying_composition() -> None:
    points, swap, collapse = _two_points_and_maps()
    opposite = Sets().opposite()
    obj = opposite(points)
    hom = opposite.Mor(obj, obj)

    assert opposite in Cat()
    assert obj in opposite
    assert obj not in Cat()
    assert obj.underlying_object() is points
    first = hom(swap) * hom(collapse)
    second = hom(collapse) * hom(swap)

    assert first.underlying_arrow()("a") == "a"
    assert second.underlying_arrow()("a") == "b"
    assert opposite.opposite_category() is Sets()
    assert opposite(opposite.base_category().an_object()).underlying_object() in Sets()


def test_product_category_composes_nonidentity_maps_componentwise() -> None:
    points, swap, collapse = _two_points_and_maps()
    product = Cat().product((Sets(), Sets()))
    obj = product(points, points)
    hom = product.Mor(obj, obj)
    arrow = hom(swap, collapse)
    involution = hom(swap, swap)

    assert product in Cat()
    assert obj in product
    assert obj not in Cat()
    assert arrow.first() is swap
    assert arrow.second() is collapse
    assert (involution * involution) == hom.identity()
    assert (arrow * involution).first() == swap * swap
    assert (arrow * involution).second() == collapse * swap


def test_product_and_opposite_respect_a_restricted_factor_category() -> None:
    points, swap, collapse = _two_points_and_maps()
    injections = Sets().WideSubcategory(Sets().MonomorphismArrowCategory())
    product = Cat().product((injections, Sets()))
    obj = product(points, points)

    assert product.Mor(obj, obj)(swap, swap).first() is swap
    with pytest.raises(ValueError):
        product.Mor(obj, obj)(collapse, swap)

    opposite = injections.opposite()
    opposite_obj = opposite(points)
    assert opposite.Mor(opposite_obj, opposite_obj)(swap).underlying_arrow() is swap
    with pytest.raises(ValueError):
        opposite.Mor(opposite_obj, opposite_obj)(collapse)
