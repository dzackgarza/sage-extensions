r"""A regular tetrahedron's symmetry group is the group of its Coxeter diagram."""

from sage_extensions.all import *  # noqa: F401,F403


def test_tetrahedron_symmetry_diagram() -> None:
    tetrahedron = RegularPolytopes()((3, 3))

    assert tetrahedron.symmetry_coxeter_diagram().coxeter_group() == tetrahedron.symmetry_group()
    assert tetrahedron.symmetry_group().order() == 24
