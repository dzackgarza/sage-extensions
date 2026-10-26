r"""The complement of an anisotropic vector in (Uoplus U) has stable root reflections."""

from sage_extensions.all import *  # noqa: F401,F403


def test_two_u_stable_complement_root_reflections_fix_the_selected_vector() -> None:
    lattice = NamedLattices.U + NamedLattices.U
    first, second = lattice.module_generators()[:2]
    vector = first + second
    reflections = lattice.stable_complement_root_reflections(vector)

    assert len(reflections) >= 1
    assert all(reflection(vector) == vector for reflection in reflections)
    assert all(reflection in lattice.stable_orthogonal_group() for reflection in reflections)
