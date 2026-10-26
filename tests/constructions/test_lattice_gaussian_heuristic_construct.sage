r"""The unit-covolume plane has Gaussian-heuristic radius (1/sqrt{pi})."""

from sage_extensions.all import *  # noqa: F401,F403


def test_standard_rank_two_lattice_gaussian_heuristic_has_square_one_over_pi() -> None:
    lattice = Lattices(ZZ)(ZZ^2)

    assert lattice.gaussian_heuristic() ** 2 == 1 / pi
