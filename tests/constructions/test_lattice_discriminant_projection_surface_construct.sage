r"""A lattice exposes its discriminant projection from the selected dual lattice."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a2_lattice_discriminant_projection_has_expected_endpoints() -> None:
    lattice = Lattices(ZZ)("A2")
    discriminant = lattice.discriminant_module()
    projection = lattice.discriminant_projection()

    assert projection.domain() is lattice.dual_lattice()
    assert projection.codomain() is discriminant


def test_a2_lattice_discriminant_class_is_projection_of_dual_lift() -> None:
    lattice = Lattices(ZZ)("A2")
    discriminant = lattice.discriminant_module()
    generator = discriminant.module_generator(0)
    lift = discriminant.dual_lattice_lift(generator)

    assert lattice.discriminant_projection()(lift) == generator
    assert lattice.discriminant_class(lift) == generator
