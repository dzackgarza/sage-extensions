r"""The tetrahedron is the regular polytope with Schlaefli symbol {3,3}."""

from sage_extensions.all import *  # noqa: F401,F403


def test_tetrahedron_from_its_schlaefli_symbol() -> None:
    tetrahedron = RegularPolytopes()((3, 3))

    assert tetrahedron in RegularPolytopes()
    assert tetrahedron.schlafli_symbol() == (3, 3)
    assert tetrahedron.dimension() == 3
    assert tetrahedron.symmetry_group().order() == 24
