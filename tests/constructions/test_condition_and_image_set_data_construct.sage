r"""Condition sets and image sets retain the data that defines them."""

from sage_extensions.all import *  # noqa: F401,F403


def test_real_condition_set_retains_its_universe_and_predicate() -> None:
    nonnegative = lambda x: x >= 0
    subset = RR.condition_set(nonnegative)

    assert subset.universe() is RR
    assert subset.predicate() is nonnegative


def test_real_image_set_retains_source_map_and_selected_inverse() -> None:
    shift = lambda x: x + 1
    unshift = lambda y: y - 1
    image = RR.image_set(shift, inverse=unshift)

    assert image.source_set() is RR
    assert image.image_map() is shift
    assert image.inverse_on_image() is unshift
    assert image.is_injective_image()
