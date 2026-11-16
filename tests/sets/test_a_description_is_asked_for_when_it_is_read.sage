r"""A finite ordered set's description is asked for when it is read, and rendered once.

A set is given a name, or a description of the source it was carved out of: two
keywords, and a construction that states both is refused.  Rendering the
description is a reader's act, and a construction that rendered it has computed
a display nobody asked for -- so the description is a function, and the set asks
it when its description is requested.  What a set was built from does not change
while the set exists, so the set keeps the rendering: the second reader asks
nothing either.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def test_a_description_is_asked_for_when_it_is_read() -> None:
    r"""Building a described set asks its description for nothing; the first read asks once, the second asks nothing."""
    asked = []

    def description():
        asked.append(1)
        return "the even numbers"

    points = FiniteOrderedSets().from_indexed(
        Sets.Δ[3], lambda position: (2 * int(position),), description=description
    )

    assert tuple(asked) == ()
    assert points.description() == "the even numbers"
    assert tuple(asked) == (1,)
    points.description()
    points.__repr__()
    assert tuple(asked) == (1,)


def test_an_ordered_subset_displays_the_description_its_construction_stated() -> None:
    r"""A filtered set's display reads that description, not the function that stated it.

    The subset of the even numbers below six is cut out by a condition and named
    by a description.  Its display is its description -- rendering the function
    itself would be no display at all -- and reading the description twice asks
    the function once.
    """
    asked = []

    def description():
        asked.append(1)
        return "the even numbers below six"

    evens = FiniteOrderedSets().from_indexed(
        Sets.Δ[3], lambda position: (2 * int(position),), name="the even numbers"
    )
    below_six = evens.filtered(lambda point: point[0] < 6, description=description)

    assert tuple(asked) == ()
    assert below_six.description() == "the even numbers below six"
    assert tuple(asked) == (1,)
    displayed = below_six.__repr__()
    assert displayed == "the even numbers below six"
    assert tuple(asked) == (1,)


def test_a_set_is_named_or_described_and_not_both() -> None:
    r"""A construction that states a name and a description is refused.

    The two keywords answer the same question -- what this set is called when it
    is read -- so a set given both would silently lose one of them.
    """
    with pytest.raises(ValueError):
        FiniteOrderedSets().from_indexed(
            Sets.Δ[3],
            lambda position: (2 * int(position),),
            name="the even numbers",
            description=lambda: "the even numbers below six",
        )
