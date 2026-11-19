r"""A determinant in two variables is decided when it takes no real zero, so a frame over it is a basis.

A frame is a basis of every fibre exactly when the determinant of its components on each
chart takes no zero there (Lee, *Introduction to Smooth Manifolds*, 2nd ed., Ch. 10).  A
determinant written in two coordinates is a polynomial in two variables, and one class of
them is decided outright: a polynomial whose monomials all have even exponents with
coefficients of one sign and a nonzero constant term is bounded away from zero --
$1 + x^2 + x^2y^2 \ge 1$ -- so it vanishes at no point of the chart.  A polynomial that
does take the value zero, $x^2 + y^2$ at the origin, is decided the other way.

The specimen is the plane, whose tangent bundle is trivial in every frame: the coordinate
frame (determinant one), a frame whose determinant is $1 + x^2 + x^2y^2$, and a frame
whose determinant is $x^2 + y^2$.
"""

import pytest

from sage_extensions.all import *


def _the_plane():
    r"""The plane, its chart, the two coordinates, and the tangent bundle's sections."""
    plane = SmoothManifolds()(2, "R^2")
    chart = plane.chart("U", "x y")
    return plane, chart, chart.coordinate(0), chart.coordinate(1), plane.tangent_bundle().sections()


def test_a_determinant_with_no_real_zero_makes_the_family_a_frame() -> None:
    r"""The components $\begin{pmatrix}1 + x^2 & y \\ y & 1 + y^2\end{pmatrix}$ have determinant $1 + x^2 + x^2y^2$, which is at least one.

    Every monomial has even exponents, the coefficients are positive, and the constant term
    is one, so the determinant is bounded away from zero on the whole chart; the family is
    a basis of every fibre and the module of sections is free of rank two.
    """
    _plane, _chart, x, y, sections = _the_plane()
    ring = _chart.function_ring()
    first = sections.section({"U": (ring.one() + x**2, y)})
    second = sections.section({"U": (y, ring.one() + y**2)})

    trivialized = sections.trivialized_by((first, second))

    assert trivialized.module_rank() == 2
    assert trivialized.basis() == (first, second)


def test_a_determinant_that_takes_the_value_zero_states_no_frame() -> None:
    r"""The components $\begin{pmatrix}x & -y \\ y & x\end{pmatrix}$ have determinant $x^2 + y^2$, which is zero at the origin.

    A line and a plane that collapse at one point are not a basis there, so the family is
    refused, and the refusal is the decision that the determinant does take a zero.
    """
    _plane, chart, x, y, sections = _the_plane()

    with pytest.raises(AssertionError):
        sections.trivialized_by(
            (
                sections.section({"U": (x, -y)}),
                sections.section({"U": (y, x)}),
            )
        )


def test_the_coordinate_frame_is_still_a_frame() -> None:
    r"""The coordinate frame's determinant is one: the constant case is decided as it was."""
    _plane, _chart, _x, _y, sections = _the_plane()
    ring = _chart.function_ring()

    trivialized = sections.trivialized_by(
        (
            sections.section({"U": (ring.one(), ring.zero())}),
            sections.section({"U": (ring.zero(), ring.one())}),
        )
    )

    assert trivialized.module_rank() == 2
