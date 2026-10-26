r"""LLL reduction returns an isometric reframing of the same lattice."""

from sage_extensions.all import *  # noqa: F401,F403


def test_square_lattice_lll_reduction_preserves_rank_and_determinant() -> None:
    lattice = Lattices(ZZ)(ZZ^2)
    reduction = lattice.lll_reduction()

    assert reduction.reduced.rank() == cardinal(2)
    assert abs(reduction.reduced.determinant()) == 1
    assert reduction.isometry.domain() is reduction.reduced
    assert reduction.isometry.codomain() is lattice


def test_lll_reduction_uses_sages_column_transformation_without_transposing() -> None:
    lattice = Lattices(ZZ)(
        [
            [1205612955, 24365],
            [24365, 2],
        ]
    )

    reduction = lattice.lll_reduction()

    assert tuple(
        tuple(int(reduction.change_of_basis_matrix[row, column]) for column in range(2))
        for row in range(2)
    ) == ((0, -1), (1, 12183))
    labels = tuple(reduction.reduced.module_generating_set())
    assert tuple(
        tuple(
            int(
                reduction.reduced.b(
                    reduction.reduced.module_generator(labels[row]),
                    reduction.reduced.module_generator(labels[column]),
                )
            )
            for column in range(2)
        )
        for row in range(2)
    ) == ((2, 1), (1, 908786343))
