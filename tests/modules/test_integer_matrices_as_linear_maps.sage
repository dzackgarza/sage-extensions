r"""Integer $2 \times 2$ matrices as linear maps $\mathbb Z^2 \to \mathbb Z^2$.

$A = \begin{pmatrix} 2 & 1 \\ 1 & 1 \end{pmatrix}$ has $\det A = 1$, $\operatorname{tr} A = 3$,
$A^2 = \begin{pmatrix} 5 & 3 \\ 3 & 2 \end{pmatrix}$, $A^{-1} = \begin{pmatrix} 1 & -1 \\ -1 & 2 \end{pmatrix}$
integral, and infinite order (its eigenvalues $(3 \pm \sqrt 5)/2$ are not roots of unity); $Ax = e_0$
has the solution $x = e_0 - e_1$.  The rotation $\begin{pmatrix} 0 & -1 \\ 1 & 0 \end{pmatrix}$ has order $4$.
$\begin{pmatrix} 1 & 2 \\ 2 & 4 \end{pmatrix}$ has rank $1$ and determinant $0$.  The Smith form of
$\begin{pmatrix} 2 & 4 \\ 6 & 8 \end{pmatrix}$ is $\operatorname{diag}(2, 4)$: $d_1 = \gcd$ of the entries
$= 2$ and $d_1 d_2 = \lvert\det\rvert = 8$.   The ring
$M_2(\mathbb Z)$ is not commutative and $M_1(\mathbb Z) = \mathbb Z$ is.  All values by hand.
"""

from sage_extensions.all import *  # noqa: F401,F403


def matrices():
    return ZZ.matrix_space(2, 2)


def test_determinant_trace_square_and_transpose() -> None:
    r"""$\det A = 1$, $\operatorname{tr} A = 3$, $A^2 = [[5, 3], [3, 2]]$, $A^t = A$, and the transpose of
    $[[1, 2], [3, 4]]$ is $[[1, 3], [2, 4]]$; $A_{01} = 1$."""
    space = matrices()
    a = space.from_rows([[2, 1], [1, 1]])

    assert a.determinant() == 1
    assert a.trace() == 3
    assert a @ a == space.from_rows([[5, 3], [3, 2]])
    assert a.transpose() == a
    assert space.from_rows([[1, 2], [3, 4]]).transpose() == space.from_rows([[1, 3], [2, 4]])
    assert a[0, 1] == 1
    assert a.matrix_rank() == 2


def test_constructing_matrices_from_entries_units_and_diagonals() -> None:
    r"""The flat entries $1, 2, 3, 4$ fill the rows; $E_{01}$, $\operatorname{diag}(2, 3)$ and $I_2$."""
    space = matrices()

    assert space.from_flat_entries([1, 2, 3, 4]) == space.from_rows([[1, 2], [3, 4]])
    assert space.matrix_unit(0, 1) == space.from_rows([[0, 1], [0, 0]])
    assert space.diagonal([2, 3]) == space.from_rows([[2, 0], [0, 3]])
    assert space.identity_matrix() == space.from_rows([[1, 0], [0, 1]])


def test_reading_a_type_one_one_tensor_as_a_matrix() -> None:
    r"""The tensor with components $[[1, 2], [3, 4]]$ is the matrix $[[1, 2], [3, 4]]$."""
    space = matrices()

    assert space.from_tensor(tensor.matrix(ZZ, [[1, 2], [3, 4]])) == space.from_rows([[1, 2], [3, 4]])


def test_solving_a_x_equals_e0() -> None:
    r"""$A(e_0 - e_1) = e_0$; for $B = [[1, 0, 1], [0, 1, 1]]$, $B e_0 = e_0$."""
    plane = ZZ ^ 2
    e0, e1 = plane.module_generator(0), plane.module_generator(1)
    a = matrices().from_rows([[2, 1], [1, 1]])
    b = ZZ.matrix_space(2, 3).from_rows([[1, 0, 1], [0, 1, 1]])
    solution = b.solve_right(e0)

    assert a.solve_right(e0) == e0 - e1
    assert b(solution) == e0
    assert b.matrix_rank() == 2


def test_the_inverse_of_a_is_the_integer_matrix_1_minus_1_minus_1_2() -> None:
    r"""$\det A = 1$, so $A^{-1} = [[1, -1], [-1, 2]] \in M_2(\mathbb Z)$."""
    space = matrices()

    assert space.from_rows([[2, 1], [1, 1]]).inverse() == space.from_rows([[1, -1], [-1, 2]])


def test_the_orders_of_a_and_of_the_quarter_turn() -> None:
    r"""$A$ has infinite order and the quarter turn has order $4$."""
    space = matrices()

    assert space.from_rows([[2, 1], [1, 1]]).multiplicative_order() == Infinity
    assert space.from_rows([[0, -1], [1, 0]]).multiplicative_order() == 4


def test_a_rank_one_matrix_is_singular() -> None:
    r"""$[[1, 2], [2, 4]]$ has proportional rows: rank $1$, determinant $0$."""
    singular = matrices().from_rows([[1, 2], [2, 4]])

    assert singular.matrix_rank() == 1
    assert singular.determinant() == 0


def test_the_smith_form_of_2_4_6_8_is_diag_2_4() -> None:
    r"""$\operatorname{SNF}([[2, 4], [6, 8]]) = \operatorname{diag}(2, 4)$, with invariant factors $2, 4$."""
    smith = matrices().from_rows([[2, 4], [6, 8]]).smith_normal_form()

    assert smith[0, 0] == 2
    assert smith[1, 1] == 4
    assert smith[0, 1] == 0
    assert smith[1, 0] == 0


def test_the_invariant_factors_of_2_4_6_8_are_2_and_4() -> None:
    r"""$d_1 = 2$, $d_2 = 8/2 = 4$."""
    assert tuple(matrices().from_rows([[2, 4], [6, 8]]).invariant_factors()) == (2, 4)


def test_square_matrices_commute_only_in_size_one() -> None:
    r"""$E_{01} E_{10} = E_{00} \neq E_{11} = E_{10} E_{01}$, while $M_1(\mathbb Z) = \mathbb Z$."""
    assert not matrices().is_commutative()
    assert ZZ.matrix_space(1, 1).is_commutative()


def test_a_is_a_unit_and_diag_2_1_is_not() -> None:
    r"""$\det A = 1 \in \mathbb Z^\times$; $\det \operatorname{diag}(2, 1) = 2 \notin \mathbb Z^\times$."""
    space = matrices()

    assert space.from_rows([[2, 1], [1, 1]]).is_unit()
    assert not space.from_rows([[2, 0], [0, 1]]).is_unit()
