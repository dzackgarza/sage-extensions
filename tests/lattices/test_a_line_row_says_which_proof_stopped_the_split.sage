r"""A line row's no-split answer names the proof that gave it.

`isotropic_line_stabilizer_image` answers either that nothing splits or with a
class-point family.  The three no-split arguments are different -- a reflection
exhibited, a divided class equal to zero, a sign space spanned -- so the answer
carries which one, and the two accessors below are how a reader asks: whether a
datum is the no-split answer, and which witnesses can be named.

`U + U(2) + <-2>` is where the two answers both occur: the `O(L)`-orbit whose
line has divided class `0` does not split, and the other one does.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _specimen():
    r"""`U + U(2) + <-2>`: two ambient line orbits, one of which does not split."""
    return (
        Lattices(ZZ)("U")
        + Lattices(ZZ)([[0, 2], [2, 0]])
        + Lattices(ZZ)([[-2]])
    )


def test_the_two_ambient_orbits_answer_differently_and_the_answer_says_why():
    r"""One orbit is the no-split answer with a named witness; the other is not.

    The reasons are the library's own tuple, so the assertion names no string:
    it asks whether the witness the answer carries is one the call can give.
    """
    lattice = _specimen()
    quotient = lattice.stable_orthogonal_group().finite_character_quotient()
    answers = tuple(
        quotient.isotropic_line_stabilizer_image(line)
        for line in lattice.Aut().isotropic_orbit_representatives(1)
    )

    no_split = tuple(answer for answer in answers if quotient.is_no_split(answer))
    split = tuple(answer for answer in answers if not quotient.is_no_split(answer))

    assert sum(1 for _answer in no_split) == int(1)
    assert sum(1 for _answer in split) == int(1)
    assert no_split[0].reason in quotient.no_split_reasons()
    assert quotient.no_split_reasons()[0] != quotient.no_split_reasons()[1]
