r"""A unimodular (Uoplus U) self-comparison has only the identity discriminant class."""

from sage_extensions.all import *  # noqa: F401,F403


def test_unimodular_two_u_self_gluing_route_has_one_discriminant_class() -> None:
    lattice = NamedLattices.U + NamedLattices.U
    first, second = lattice.module_generators()[:2]
    vector = first + second
    classes = lattice.gluing_route_discriminant_classes(vector, vector)

    assert len(classes) == 1
    assert classes[0] == lattice.discriminant_group().O().one()
