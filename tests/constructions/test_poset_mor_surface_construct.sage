r"""A poset Mor object remembers its poset and its unique comparable arrow."""

from sage_extensions.all import *  # noqa: F401,F403


def test_comparable_poset_mor_exposes_its_category_and_unique_arrow() -> None:
    category = PosetCategory(
        Sets.Δ[2],
        le=lambda left, right: int(left) <= int(right),
    )
    zero = category(0)
    one = category(1)
    morphisms = category.Mor(zero, one)
    arrow = morphisms.unique()

    assert morphisms.poset_category() is category
    assert arrow.parent() is morphisms
    assert arrow.domain() is zero
    assert arrow.codomain() is one
