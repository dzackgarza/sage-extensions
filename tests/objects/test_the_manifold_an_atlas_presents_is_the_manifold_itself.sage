r"""An atlas presents the manifold it is selected on, not a second copy of it.

The charts of an atlas are charts of the space they are selected on, so the
manifold they present is that space: for the real line's one-chart atlas it is
``RR`` itself, the same object and not a manifold built beside it (``OWN-15``,
``OWN-19``).  A manifold of class ``C^k`` or higher answers every lower degree,
and an atlas whose class is above the manifold's presents no manifold of that
class, which it says rather than answering with one.
"""

import pytest

from sage_extensions.all import *


def test_the_manifold_the_real_lines_atlas_presents_is_the_line_itself() -> None:
    r"""``RR`` is the topological manifold and the smooth manifold its one-chart atlas presents."""
    topological = RR.standard_topological_atlas()
    smooth = RR.standard_smooth_atlas()

    assert topological.topological_manifold() is RR
    assert smooth.real_ck_manifold() is RR
    assert smooth.real_ck_manifold() in SmoothManifolds()


def test_a_finite_degree_atlas_presents_the_smooth_line_at_that_degree() -> None:
    r"""``RR`` is smooth, so a ``C^2`` atlas selected on it presents ``RR`` as a ``C^2`` manifold."""
    atlas = RealCkAtlases(2).on(
        RR,
        {RR: RR},
        {RR: Sets().Mor(RR, RR).identity()},
        {RR: Sets().Mor(RR, RR).identity()},
        {},
        {},
    )

    assert atlas.real_ck_manifold() is RR


def test_an_atlas_above_the_manifolds_class_presents_no_manifold_of_that_class() -> None:
    r"""A ``C^1`` manifold carries no ``C^2`` charts, so a ``C^2`` atlas selected on it presents nothing."""
    line = DifferentiableManifolds()(1, "C1line", 1)
    atlas = RealCkAtlases(2).on(
        line,
        {line: line},
        {line: Sets().Mor(line, line).identity()},
        {line: Sets().Mor(line, line).identity()},
        {},
        {},
    )

    with pytest.raises(AssertionError):
        atlas.real_ck_manifold()
