r"""Monotone morphisms of finite partial orders."""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def test_diamond_order_monotone_maps_and_composition() -> None:
    four = Sets.Δ[3]
    two = Sets.Δ[1]
    diamond = PartiallyOrderedSets()(
        four,
        lambda x, y: x == y or int(x) == 0 or int(y) == 3,
    )
    chain = PartiallyOrderedSets()(two, lambda x, y: int(x) <= int(y))

    collapse = PartiallyOrderedSets().Mor(diamond, chain)(
        lambda x: chain(0 if int(x) == 0 else 1), check=True
    )
    top = PartiallyOrderedSets().Mor(chain, chain)(lambda _x: chain(1), check=True)

    assert collapse(diamond(0)) == chain(0)
    assert collapse(diamond(1)) == collapse(diamond(2)) == chain(1)
    assert (top * collapse)(diamond(0)) == chain(1)
    assert (top * collapse)(diamond(3)) == chain(1)

    with pytest.raises(ValueError):
        PartiallyOrderedSets().Mor(diamond, chain)(
            lambda x: chain(1 if int(x) == 0 else 0), check=True
        )
