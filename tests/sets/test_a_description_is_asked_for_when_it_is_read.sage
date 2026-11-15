r"""A finite ordered set's description is asked for when it is read, not when it is built.

A set that carries a name carries a description of itself.  Rendering it is a
reader's act, and a construction that renders it has computed a display nobody
asked for -- so the name is a function of what the set was built from, and the
set asks it when its description is requested.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_a_description_is_asked_for_when_it_is_read() -> None:
    r"""Building a named set asks its name for nothing; reading the description asks once."""
    asked = []

    def description():
        asked.append(1)
        return "the even squares"

    points = FiniteOrderedSets().from_indexed(
        Sets.Δ[3], lambda position: (2 * int(position),), name=description
    )

    assert tuple(asked) == ()
    assert points.description() == "the even squares"
    assert tuple(asked) == (1,)
