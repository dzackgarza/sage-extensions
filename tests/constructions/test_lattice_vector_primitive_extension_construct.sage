r"""A primitive generator of (A_1) gives a trivial primitive extension."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a1_primitive_generator_has_trivial_extension_index() -> None:
    lattice = NamedLattices.A1
    root = lattice.basis_vector(0)
    extension = lattice.vector_primitive_extension(root)

    assert extension.index == 1
    assert extension.complement.module_rank() == cardinal(0)
    assert extension.inclusion.codomain() is lattice
