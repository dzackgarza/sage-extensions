r"""The integer line has center density one half."""

from sage_extensions.all import *  # noqa: F401,F403


def test_integer_line_has_center_density_one_half() -> None:
    lattice = Lattices(ZZ)(ZZ^1)

    assert lattice.center_density() == QQ(1) / 2
