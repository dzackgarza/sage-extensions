r"""A degree-four determinant that is bounded away from zero is decided, and one that is not is refused.

A polynomial of degree $2d$ is a sum of squares of polynomials of degree $d$ exactly when some
positive semidefinite matrix $G$ satisfies $P = u^{T} G u$ for $u$ the monomials of degree
$d$; with a positive constant term that makes $P$ bounded away from zero (Lasserre,
*Moments, Positive Polynomials and Their Applications*, Ch. 2).  The certificate for a
quartic in two variables is a $3 \times 3$ Gram matrix in $x^2, xy, y^2$, found by
distributing each monomial over the ways it splits into two of them.

The specimens are $x^4 - 2x^2y^2 + 2y^4 + 1$, whose Gram matrix in $x^2, y^2$ is
$\begin{pmatrix}1&-1\\-1&2\end{pmatrix}$ and which is at least $3/2$, and $x^4 - 2x^2y^2 + y^4$,
which is $(x^2 - y^2)^2$ and vanishes on the two lines $y = \pm x$.
"""

import pytest

from sage_extensions.all import *


def _the_plane():
    r"""The plane, its chart, and the two coordinates."""
    plane = SmoothManifolds()(2, "R^2")
    chart = plane.chart("U", "x y")
    return plane, chart, chart.coordinate(0), chart.coordinate(1)


def test_a_quartic_bounded_away_from_zero_makes_the_family_a_frame() -> None:
    r"""The frame whose determinant is $x^4 - 2x^2y^2 + 2y^4 + 1$ is a basis of every fibre.

    The determinant is $2(t - 1/2)^2 + 3/2$ in $t = y^2/x^2$, so it is at least $3/2$, and
    the Gram certificate finds the positive definite matrix that says so.
    """
    plane, chart, x, y = _the_plane()
    ring = chart.function_ring()
    sections = plane.tangent_bundle().sections()
    quartic = x**4 + (-2) * x**2 * y**2 + 2 * y**4 + ring.one()

    frame = (
        sections.section({"U": (quartic, ring.zero())}),
        sections.section({"U": (ring.zero(), ring.one())}),
    )

    assert sections.trivialized_by(frame).module_rank() == 2


def test_a_quartic_that_vanishes_on_two_lines_states_no_frame() -> None:
    r"""$x^4 - 2x^2y^2 + y^4 = (x^2 - y^2)^2$ vanishes wherever $y = \pm x$, so it is no determinant of a frame."""
    plane, chart, x, y = _the_plane()
    ring = chart.function_ring()
    sections = plane.tangent_bundle().sections()
    square = x**4 + (-2) * x**2 * y**2 + y**4

    with pytest.raises(AssertionError):
        sections.trivialized_by(
            (
                sections.section({"U": (square, ring.zero())}),
                sections.section({"U": (ring.zero(), ring.one())}),
            )
        )
