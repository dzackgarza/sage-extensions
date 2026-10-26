r"""Rational ruled surfaces ``P(O(a) + O(b))`` over ``P^1``.

Source: Hartshorne, *Algebraic Geometry*, Lemma II.7.9 (``Proj`` of ``S * L`` is
isomorphic to ``Proj S`` over ``X``; for ``S = Sym E`` this gives
``P(E tensor L) = P(E)``), Corollary V.2.13 (for each ``e >= 0`` there is exactly one
rational ruled surface ``X_e = P(O + O(-e))``, and these are pairwise distinct) and
Example V.2.11.5 (``X_1`` is ``P^2`` blown up at a point).  So
``P(O + O(1)) = P(O(-1) + O) = X_1``, ``P(O(1) + O(1)) = P(O + O) = P^1 x P^1 = X_0``, and
``P(O(1) + O(2)) = P(O + O(1))``.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _ruled_surface(line, first, second):
    return line.O(first).direct_sum(line.O(second)).projectivization()


def test_every_fibre_of_the_first_hirzebruch_surface_is_a_projective_line() -> None:
    r"""``P(O + O(1)) -> P^1`` is a ``P^1``-bundle: the fibre over ``[0 : 1]`` is ``P^1``, the total space a surface."""
    line = ProjectiveSpaces(QQ)(1)
    projection = _ruled_surface(line, 0, 1)

    assert projection.codomain() is line
    assert projection.domain().dimension() == 2
    assert projection.fiber(line.point((0, 1))).is_isomorphic(line)


def test_the_first_hirzebruch_surface_is_not_the_quadric() -> None:
    r"""``X_1 != X_0``: ``P(O + O(1))`` is not ``P^1 x P^1`` (Corollary V.2.13)."""
    line = ProjectiveSpaces(QQ)(1)

    assert not _ruled_surface(line, 0, 1).domain().is_isomorphic(Schemes(QQ).product((line, line)))


def test_twisting_by_o_one_does_not_change_the_ruled_surface() -> None:
    r"""Lemma II.7.9: ``P(O(1) + O(2)) = P(O + O(1))`` and ``P(O(1) + O(1)) = P^1 x P^1``."""
    line = ProjectiveSpaces(QQ)(1)

    assert _ruled_surface(line, 1, 2).domain().is_isomorphic(_ruled_surface(line, 0, 1).domain())
    assert _ruled_surface(line, 1, 1).domain().is_isomorphic(Schemes(QQ).product((line, line)))


def test_the_first_hirzebruch_surface_is_the_plane_blown_up_at_a_point() -> None:
    r"""Example V.2.11.5: ``X_1 = Bl_p P^2``."""
    line = ProjectiveSpaces(QQ)(1)
    plane = ProjectiveSpaces(QQ)(2)

    assert _ruled_surface(line, 0, 1).domain().is_isomorphic(plane.blowup(plane.point((0, 0, 1))))
