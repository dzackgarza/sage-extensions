r"""A section trivializes a rank-one bundle only if it vanishes nowhere, and that is decided.

A rank-one bundle is trivial when it is isomorphic to $M \times \mathbb R$, and the
isomorphism is read in a section that is a basis of every fibre: the map
$(p, a) \mapsto aE_p$ is an isomorphism exactly when $E_p \neq 0$ at every point, since
that is what makes one vector a basis of a line (Lee, *Introduction to Smooth
Manifolds*, 2nd ed., Ch. 10).  A section that vanishes somewhere therefore divides by
zero somewhere and states no trivialization, and "the coordinate does not vanish" is
a statement about a function, not a sample of its values: the component of $E$ on a
chart is a polynomial in that chart's coordinate, and a real polynomial with no real
root vanishes at no point of the chart's image.

The specimen is the circle's frame $E = (1 + x^2)\partial_x = -(1 + y^2)\partial_y$,
whose components are $x^2 + 1$ and $-(y^2 + 1)$ -- no real root either -- against the
zero section and a section that vanishes at the point of coordinate $1$.
"""

import pytest

from sage_extensions.all import *


def _the_circle():
    r"""$S^1$, its two charts, their coordinates, and the tangent bundle's sections."""
    circle = SmoothManifolds().sphere(1)
    north = circle.atlas()["U_N"]
    south = circle.atlas()["U_S"]
    return circle, south, north.coordinate(0), south.coordinate(0), circle.tangent_bundle().sections()


def _the_frame(circle, x, y):
    r"""$E$, with components $1 + x^2$ and $-(1 + y^2)$ in the two charts."""
    return circle.tangent_bundle().sections().section(
        {"U_N": (1 + x**2,), "U_S": (-(1 + y**2),)}
    )


def test_the_frame_of_the_circle_is_decided_to_vanished_nowhere() -> None:
    r"""$1 + x^2$ and $-(1 + y^2)$ have no real root, so $E$ is a basis of every fibre.

    A real polynomial with no real root is never zero, and it is a polynomial of one
    variable on each chart of a one-dimensional manifold; so the components of $E$ are
    nonzero at every point of their charts, $E$ trivializes $TS^1$, and the module of
    sections is free of rank one.
    """
    circle, _south, x, y, sections = _the_circle()
    frame = _the_frame(circle, x, y)

    trivialized = sections.trivialized_by(frame)

    assert trivialized.module_rank() == 1
    assert trivialized.basis() == (frame,)


def test_the_zero_section_states_no_trivialization() -> None:
    r"""The zero section vanishes everywhere, so it is no basis of any fibre.

    Its two components agree -- both are zero -- so it is a section; what refuses it is
    that it is zero at every point, which the components' common real root decides.
    """
    circle, _south, _x, _y, sections = _the_circle()

    with pytest.raises(AssertionError):
        sections.trivialized_by(sections.zero())


def test_a_section_that_vanishes_at_one_point_states_no_trivialization() -> None:
    r"""$x - 1$ on the north chart and $y^2 - y$ on the south are one section, zero at the point of coordinate $1$.

    The two components agree on the overlap -- $(x - 1)(-1/x^2) = 1/x^2 - 1/x$ under
    $y = 1/x$ -- so this is a section, and its common real root is the point where it
    vanishes.  A line with a zero vector at a point is not trivialized by it, however
    few the points are.
    """
    circle, _south, x, y, sections = _the_circle()
    at_one = circle.point((1,), "U_N")

    vanishing = sections.section({"U_N": (x + (-1),), "U_S": (y**2 + (-y),)})

    assert vanishing.components()["U_N"][0](at_one) == RR.zero()
    assert vanishing.components()["U_S"][0](at_one) == RR.zero()
    with pytest.raises(AssertionError):
        sections.trivialized_by(vanishing)
