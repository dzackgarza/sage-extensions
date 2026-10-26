r"""The primitive extension cut out by the (A_1) root retains its discriminant quotient representatives."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a1_vector_extension_complement_is_definite_and_discriminant_classes_round_trip() -> None:
    lattice = NamedLattices.A1
    extension = lattice.vector_primitive_extension(lattice.basis_vector(0))

    assert extension.complement_is_definite()
    assert extension.complement.module_rank() == cardinal(0)
    for discriminant_class in extension.discriminant_form.elements():
        representative = extension.representative_of(discriminant_class)
        assert extension.class_of_representative(representative) == discriminant_class
