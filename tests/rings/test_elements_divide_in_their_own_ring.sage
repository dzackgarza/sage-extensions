r"""Division in a ring, and the scalar division of a module over it.

A ring's elements divide in the ring, by the inverse of the divisor taken on the
right: $a / b = a b^{-1}$.  The elements of a module over a ring divide by a
scalar through the module's scalar action, $v / r = r^{-1} v$.  A ring is a left
module over itself, so the element class of a ring carries both operations, and
the two agree exactly when the ring commutes.

In $M_2(\mathbf{Q})$, $e_{12} / (1 + e_{21}) = e_{12}(1 - e_{21}) = e_{12} -
e_{11}$, while $(1 + e_{21})^{-1} e_{12} = e_{12} - e_{22}$: one division of two
matrices tells the two orders apart.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def test_a_matrix_divides_by_the_inverse_of_the_divisor_on_the_right() -> None:
    r"""$e_{12} / (1 + e_{21}) = e_{12} - e_{11}$, and not $e_{12} - e_{22}$.

    ``1 + e_{21}`` has inverse ``1 - e_{21}``, since $e_{21}^2 = 0$; the quotient
    $e_{12}(1 - e_{21})$ is $e_{12} - e_{11}$ because $e_{12} e_{21} = e_{11}$.
    The product in the other order, $(1 - e_{21}) e_{12}$, is $e_{12} - e_{22}$
    because $e_{21} e_{12} = e_{22}$, so a quotient that multiplied by the
    inverse on the left would be a different matrix.
    """
    matrices = QQ.matrix_space(2)
    e11 = matrices.matrix_unit(0, 0)
    e12 = matrices.matrix_unit(0, 1)
    e21 = matrices.matrix_unit(1, 0)
    e22 = matrices.matrix_unit(1, 1)
    divisor = matrices.one() + e21
    inverse = ~divisor

    quotient = e12 / divisor

    assert inverse == matrices.one() - e21
    assert quotient == e12 - e11
    assert quotient != inverse * e12
    assert inverse * e12 == e12 - e22


def test_a_vector_divides_by_the_unit_inverse_of_its_scalar() -> None:
    r"""$v / r = r^{-1} v$ for a vector $v$ of a module over $R$ and a unit $r$."""
    module = QQ.free_module(("v",))
    vector = module.module_generator("v")

    assert vector / 2 == module.scalar_multiple(QQ(2).inverse_of_unit(), vector)
    assert (2 * vector) / 2 == vector
    assert vector / QQ(2) == (QQ(1) / QQ(2)) * vector


def test_a_nonunit_of_the_scalar_ring_does_not_divide_a_vector() -> None:
    r"""A lattice over $\mathbf{Z}$ is a $\mathbf{Z}$-module, where $2$ is no unit."""
    lattice = Lattices(ZZ)(2)

    with pytest.raises(ZeroDivisionError):
        lattice.an_element() / 2


def test_a_field_states_its_reciprocal_as_its_division_of_one() -> None:
    r"""$1/(\sqrt{2} - 1) = \sqrt{2} + 1$, and $\tilde{x} = 1/x$ in both fields."""
    root = RR(2).sqrt()

    assert 1 / (root - 1) == root + 1
    assert RR(4).inverse_of_unit() == RR(1) / RR(4)
    assert CC(4).inverse_of_unit() == CC(1) / CC(4)
