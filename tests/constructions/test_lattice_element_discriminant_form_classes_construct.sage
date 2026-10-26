r"""Primitive lattice vectors expose their classes in the discriminant forms."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a2_vector_class_in_discriminant_bilinear_form_uses_primitive_dual() -> None:
    lattice = Lattices(ZZ)("A2")
    vector = lattice.basis_vector(0)
    form = lattice.discriminant_bilinear_form()

    assert vector.primitive_dual_in_discriminant_bilinear_form() == (
        form.discriminant_class(vector.primitive_dual())
    )


def test_a2_vector_class_in_discriminant_quadratic_form_uses_primitive_dual() -> None:
    lattice = Lattices(ZZ)("A2")
    vector = lattice.basis_vector(0)
    form = lattice.discriminant_quadratic_form()

    assert vector.primitive_dual_in_discriminant_quadratic_form() == (
        form.discriminant_class(vector.primitive_dual())
    )
