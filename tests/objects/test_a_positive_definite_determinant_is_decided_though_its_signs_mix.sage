r"""A determinant that is a positive definite quadratic is decided, though its coefficients have both signs.

A quadratic form $q(x) = x^{T}Ax + b^{T}x + c$ in any number of variables is decided
exactly: when $A$ is positive definite the form has a minimum, at $x = -\tfrac{1}{2}A^{-1}b$,
and its value there is $c - \tfrac{1}{4}b^{T}A^{-1}b$.  So $x^2 - 2xy + 2y^2 + 1$ is
positive everywhere although its coefficients have both signs, and a form whose minimum is
zero takes the value zero.  A form with an indefinite quadratic part is unbounded both ways,
so it takes the value zero somewhere (Lee, *Introduction to Smooth Manifolds*, 2nd ed.,
Ch. 10, for the determinant that makes a frame a basis).

The specimen is the plane's tangent bundle, whose triviality is read off the determinant of
a frame's components: $x^2 - 2xy + 2y^2 + 1$ is a frame's, and $(x - y)^2$ is not.
"""

import pytest

from sage_extensions.all import *


def _the_plane():
    r"""The plane, its chart, the two coordinates, and the tangent bundle's sections."""
    plane = SmoothManifolds()(2, "R^2")
    chart = plane.chart("U", "x y")
    return plane, chart, chart.coordinate(0), chart.coordinate(1), plane.tangent_bundle().sections()


def test_a_positive_definite_determinant_makes_the_family_a_frame() -> None:
    r"""The components $\begin{pmatrix}1 & (x-y)^2 \\ -1 & y^2+1\end{pmatrix}$ have determinant $x^2 - 2xy + 2y^2 + 1$, whose minimum is one.

    The quadratic part has matrix $\begin{pmatrix}1 & -1\\ -1 & 2\end{pmatrix}$ with leading
    minors $1$ and $1$, so it is positive definite and the form's minimum is its constant
    term; the determinant is positive everywhere, the family is a basis of every fibre, and
    the module of sections is free of rank two.
    """
    _plane, _chart, x, y, sections = _the_plane()
    ring = _chart.function_ring()
    first = sections.section({"U": (ring.one(), -ring.one())})
    second = sections.section({"U": ((x + (-y)) * (x + (-y)), y**2 + ring.one())})

    trivialized = sections.trivialized_by((first, second))

    assert trivialized.module_rank() == 2


def test_a_determinant_whose_minimum_is_zero_states_no_frame() -> None:
    r"""$\begin{pmatrix}(x-y)^2 & 0\\ 1 & 1\end{pmatrix}$ has determinant $(x-y)^2$, which is zero on the line $x = y$."""
    _plane, _chart, x, y, sections = _the_plane()
    ring = _chart.function_ring()
    square = (x + (-y)) * (x + (-y))

    with pytest.raises(AssertionError):
        sections.trivialized_by(
            (
                sections.section({"U": (square, ring.one())}),
                sections.section({"U": (ring.zero(), ring.one())}),
            )
        )


def test_an_indefinite_determinant_states_no_frame() -> None:
    r"""A form with an indefinite quadratic part, $x^2 - y^2 + 1$, takes the value zero on the hyperbola $x^2 - y^2 = -1$."""
    _plane, _chart, x, y, sections = _the_plane()
    ring = _chart.function_ring()

    with pytest.raises(AssertionError):
        sections.trivialized_by(
            (
                sections.section({"U": (ring.one(), -ring.one())}),
                sections.section({"U": (y**2 + (-x**2) + (-ring.one()), ring.one())}),
            )
        )
