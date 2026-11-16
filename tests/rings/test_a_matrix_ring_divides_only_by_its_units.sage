r"""Division in the matrix ring $M_2(\mathbf{Z})$, by a unit and by a nonunit.

A matrix divides in $M_2(\mathbf{Z})$ exactly by a unit of that ring: the
quotient $AB^{-1}$ is an integral matrix again only when $B$ has an inverse in
the ring.  Such a unit is a matrix with an integral two-sided inverse,
$\begin{pmatrix}2&1\\1&1\end{pmatrix}^{-1}=\begin{pmatrix}1&-1\\-1&2\end{pmatrix}$
because its determinant is $1$, while $2I$ has determinant $4$ and its inverse
$\frac{1}{2}I$ lies outside the ring.  So the identity divides by the first and
is refused by the second, and the refusal is the ring's statement that the
divisor is not a unit, not an engine failing to convert a rational to an
integer on its way to one.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def test_a_matrix_divides_by_the_unit_inverse_of_its_divisor() -> None:
    r"""$I/A = A^{-1} = \begin{pmatrix}1&-1\\-1&2\end{pmatrix}$ and $A/A = I$ in $M_2(\mathbf{Z})$.

    $\det A = 2 \cdot 1 - 1 \cdot 1 = 1$, and $A\,A^{-1}$ is the identity, so
    $A^{-1}$ is an integral matrix and $A$ is a unit of the ring.
    """
    matrices = ZZ.matrix_space(2)
    a = matrices.from_rows([[2, 1], [1, 1]])
    inverse = matrices.from_rows([[1, -1], [-1, 2]])

    assert a.determinant() == 1
    assert a.is_unit() is True
    assert matrices.one() / a == inverse
    assert a / a == matrices.one()
    assert a.inverse_of_unit() == inverse
    assert a @ inverse == matrices.one()


def test_a_matrix_divides_by_the_unit_inverse_on_the_right() -> None:
    r"""$e_{12}/(1+e_{21}) = e_{12}-e_{11}$ in $M_2(\mathbf{Z})$, not $e_{12}-e_{22}$.

    ``1 + e_{21}`` has inverse ``1 - e_{21}`` because $e_{21}^2 = 0$, and
    $e_{12}(1-e_{21}) = e_{12}-e_{11}$ since $e_{12}e_{21} = e_{11}$, while the
    product in the other order is $e_{12}-e_{22}$.  Both matrices are integral,
    so the ring contains the unit and its quotient either way, and only one of
    them is $ab^{-1}$.
    """
    matrices = ZZ.matrix_space(2)
    e11 = matrices.matrix_unit(0, 0)
    e12 = matrices.matrix_unit(0, 1)
    e21 = matrices.matrix_unit(1, 0)
    e22 = matrices.matrix_unit(1, 1)
    divisor = matrices.one() + e21

    assert divisor.is_unit() is True
    assert e12 / divisor == e12 - e11
    assert e12 / divisor != e12 - e22
    assert (~divisor) @ e12 == e12 - e22


def test_a_matrix_that_is_no_unit_of_the_ring_divides_nothing() -> None:
    r"""$2I$ has determinant $4$, so it is no unit and the ring refuses the quotient.

    $2I$ has no inverse in $M_2(\mathbf{Z})$: its inverse in $M_2(\mathbf{Q})$ is
    $\frac{1}{2}I$, whose entries are not integers.  Both spellings of the
    inverse -- the multiplication by the inverse of the divisor that division
    is, and the unit inverse alone -- are refused by the ring.
    """
    matrices = ZZ.matrix_space(2)
    two = matrices(2)

    assert two.determinant() == 4
    assert two.is_unit() is False
    with pytest.raises(ZeroDivisionError):
        matrices.one() / two
    with pytest.raises(ZeroDivisionError):
        two.inverse_of_unit()
