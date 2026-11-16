r"""Division in a matrix ring $M_2(R)$: by its units, and refusal of everything else.

A matrix divides in $M_n(R)$ exactly by a unit of that ring: the quotient
$AB^{-1}$ is a matrix over $R$ again only when $B$ has an inverse in the ring,
and $B$ has one exactly when $\det B$ is a unit of $R$, since
$B\operatorname{adj}(B) = \det(B)I$ and $\det$ is multiplicative.  Over
$\mathbf{Z}$ the unit is
$\begin{pmatrix}2&1\\1&1\end{pmatrix}^{-1}=\begin{pmatrix}1&-1\\-1&2\end{pmatrix}$,
whose determinant is $1$, while $2I$ has determinant $4$ and its inverse
$\frac{1}{2}I$ lies outside the ring.  Over $\mathbf{Z}/4$ the matrix
$\begin{pmatrix}3&0\\0&1\end{pmatrix}$ is its own inverse because
$3^2\equiv1 \pmod 4$, and $\begin{pmatrix}2&0\\0&1\end{pmatrix}$ is no unit
because $2\cdot2\equiv0$: that ring is not even a domain.  Over
$\mathbf{Z}[x]$ the shear $\begin{pmatrix}1&x\\0&1\end{pmatrix}$ inverts to
$\begin{pmatrix}1&-x\\0&1\end{pmatrix}$.  So the identity divides by the units
and is refused by the rest, and the refusal is the ring's statement that the
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


def test_a_matrix_over_the_integers_mod_four_is_its_own_inverse() -> None:
    r"""$A = \begin{pmatrix}3&0\\0&1\end{pmatrix}$ over $\mathbf{Z}/4$ satisfies $A^2 = I$.

    $\det A = 3$ and $3 \cdot 3 = 9 \equiv 1 \pmod 4$, so $3$ is a unit of
    $\mathbf{Z}/4$ with inverse $3$, and $A^{-1} = \operatorname{diag}(3, 1)$,
    which is $A$ itself.  The inverse is in the ring, so the ring inverts it
    although $\mathbf{Z}/4$ has no fraction field.
    """
    ring = ZZ.quotient_ring(ZZ.ideal(4))
    matrices = ring.matrix_space(2)
    a = matrices.from_rows([[3, 0], [0, 1]])

    assert a.determinant() == ring(3)
    assert ring(3) * ring(3) == ring.one()
    assert a.is_unit() is True
    assert a @ a == matrices.one()
    assert ~a == a
    assert a.inverse() == a
    assert a.inverse_of_unit() == a
    assert matrices.one() / a == a
    assert a / a == matrices.one()


def test_a_matrix_over_a_polynomial_ring_inverts_by_its_unit_determinant() -> None:
    r"""$U = \begin{pmatrix}1&x\\0&1\end{pmatrix}$ over $\mathbf{Z}[x]$ inverts to $\begin{pmatrix}1&-x\\0&1\end{pmatrix}$.

    $\det U = 1$, and the units of $\mathbf{Z}[x]$ are $\pm 1$, so $U^{-1}$ is
    an integral matrix: $U(1 - e_{12}x) = I$ because $e_{12}^2 = 0$.  The ring
    inverts $U$ in its own arithmetic and needs no fraction field.
    """
    ring = ZZ.polynomial_ring("x")
    x = ring.algebra_generator("x")
    matrices = ring.matrix_space(2)
    u = matrices.from_rows([[1, x], [0, 1]])
    inverse = matrices.from_rows([[1, -x], [0, 1]])

    assert u.determinant() == ring.one()
    assert u.is_unit() is True
    assert u @ inverse == matrices.one()
    assert ~u == inverse
    assert u.inverse() == inverse
    assert u.inverse_of_unit() == inverse
    assert matrices.one() / u == inverse
    assert u / u == matrices.one()


def test_a_matrix_over_the_integers_mod_four_whose_determinant_is_no_unit_is_refused() -> None:
    r"""$\begin{pmatrix}2&0\\0&1\end{pmatrix}$ over $\mathbf{Z}/4$ is no unit: $2 \cdot 2 \equiv 0 \pmod 4$.

    Its determinant $2$ is no unit of $\mathbf{Z}/4$, so the matrix has no
    inverse in the ring, and every spelling of the inverse is the ring's
    refusal.
    """
    ring = ZZ.quotient_ring(ZZ.ideal(4))
    matrices = ring.matrix_space(2)
    a = matrices.from_rows([[2, 0], [0, 1]])

    assert a.determinant() == ring(2)
    assert ring(2) * ring(2) == ring.zero()
    assert a.is_unit() is False
    with pytest.raises(ZeroDivisionError):
        ~a
    with pytest.raises(ZeroDivisionError):
        a.inverse_of_unit()
    with pytest.raises(ZeroDivisionError):
        a.inverse()


def test_the_public_inverse_of_2I_over_the_integers_is_refused_by_the_ring() -> None:
    r"""$2I$ over $\mathbf{Z}$ has no inverse there, and $2I.\mathrm{inverse}()$ says so.

    The inverse of $2I$ in $M_2(\mathbf{Q})$ is $\frac{1}{2}I$, whose entries
    are not integers.  The determinant $4$ is no unit of $\mathbf{Z}$, so the
    ring states that the matrix has no inverse in it instead of reading the
    rational matrix back.
    """
    matrices = ZZ.matrix_space(2)
    two = matrices(2)

    assert two.determinant() == 4
    with pytest.raises(ZeroDivisionError):
        two.inverse()
