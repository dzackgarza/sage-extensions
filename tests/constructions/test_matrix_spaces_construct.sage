r"""Finite matrices as linear maps between framed free modules.

The rectangular matrix ``[[1,0,1],[0,1,1]]`` is a map ``ZZ^3 -> ZZ^2`` of
rank two.  Square specimens additionally exercise determinant, inverse, Smith
form, transpose and multiplicative order, all as operations on the same owned
matrix-morphism elements.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _rectangular_space():
    return ZZ.matrix_space(2, 3)


def _square_space():
    return ZZ.matrix_space(2, 2)


def test_matrix_space_retains_row_column_indices_shape_and_constructors() -> None:
    space = _rectangular_space()
    rows = [[1, 0, 1], [0, 1, 1]]
    matrix = space.from_rows(rows)

    assert space in MatrixSpaces(ZZ)
    assert space.nrows() == 2
    assert space.ncols() == 3
    assert space.row_index_set().cardinality() == cardinal(2)
    assert space.column_index_set().cardinality() == cardinal(3)
    assert space.matrix_shape() == (2, 3)
    assert space.from_flat_entries([1, 0, 1, 0, 1, 1]) == matrix
    assert space.matrix_unit(0, 2) == space.from_rows([[0, 0, 1], [0, 0, 0]])
    assert space.from_tensor(tensor.matrix(ZZ, rows)) == matrix
    assert isinstance(matrix, space.ElementType)


def test_matrix_element_exposes_entries_rows_columns_and_shape() -> None:
    space = _rectangular_space()
    matrix = space.from_rows([[1, 2, 3], [4, 5, 6]])

    assert matrix.matrix() == matrix
    assert matrix.matrix_entry(0, 1) == 2
    assert matrix[1, 2] == 6
    assert matrix.nrows() == 2
    assert matrix.ncols() == 3
    assert matrix.matrix_shape() == (2, 3)
    assert len(tuple(matrix.rows())) == 2
    assert len(tuple(matrix.columns())) == 3
    assert matrix.row(0) == matrix.rows()[0]
    assert matrix.column(1) == matrix.columns()[1]


def test_matrix_transpose_and_change_of_ring_preserve_entries() -> None:
    matrix = _rectangular_space().from_rows([[1, 2, 3], [4, 5, 6]])
    transpose = matrix.transpose()
    rational = matrix.change_ring(QQ)

    assert matrix.T() == transpose
    assert transpose.matrix_shape() == (3, 2)
    assert transpose.matrix_entry(1, 0) == 2
    assert rational.matrix_entry(1, 2) == QQ(6)


def test_square_matrix_determinant_inverse_rank_and_order() -> None:
    space = _square_space()
    matrix = space.from_rows([[2, 1], [1, 1]])
    inverse = space.from_rows([[1, -1], [-1, 2]])
    rotation = space.from_rows([[0, -1], [1, 0]])

    assert matrix.det() == matrix.determinant() == 1
    assert matrix.matrix_rank() == 2
    assert matrix.inverse() == inverse
    assert matrix.multiplicative_order() == Infinity
    assert rotation.multiplicative_order() == 4


def test_matrix_solve_right_and_smith_data_have_the_standard_values() -> None:
    plane = ZZ.free_module(2)
    e0, e1 = plane.module_generator(0), plane.module_generator(1)
    matrix = _square_space().from_rows([[2, 1], [1, 1]])
    smith_source = _square_space().from_rows([[2, 4], [6, 8]])
    smith = smith_source.smith_form()
    normal = smith_source.smith_normal_form()

    assert matrix.solve_right(e0) == e0 - e1
    assert tuple(smith_source.invariant_factors()) == (2, 4)
    assert normal.matrix_entry(0, 0) == 2
    assert normal.matrix_entry(1, 1) == 4
    assert smith["diagonal"] == normal
