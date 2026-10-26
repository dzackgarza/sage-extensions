r"""The rank-one square lattice has theta series (1+2q+2q^4+cdots)."""

from sage_extensions.all import *  # noqa: F401,F403


def test_rank_one_square_lattice_theta_series_begins_with_square_counts() -> None:
    lattice = Lattices(ZZ)(ZZ^1)
    theta = lattice.theta_series(precision=5)

    assert theta[0] == 1
    assert theta[1] == 2
    assert theta[2] == 0
    assert theta[3] == 0
    assert theta[4] == 2
