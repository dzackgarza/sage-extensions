r"""The integer line has covering radius one half."""

from sage_extensions.all import *  # noqa: F401,F403


def test_integer_line_has_covering_radius_one_half() -> None:
    lattice = Lattices(ZZ)(ZZ^1)

    assert lattice.covering_radius() == QQ(1) / 2
