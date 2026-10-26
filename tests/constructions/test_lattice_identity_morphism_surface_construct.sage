r"""A lattice exposes its selected identity automorphism through the object API."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_plane_identity_morphism_is_the_lattice_automorphism_identity() -> None:
    lattice = NamedLattices.U
    identity = lattice.identity_morphism()
    e = lattice.basis_vector(0)
    f = lattice.basis_vector(1)

    assert identity.parent() is lattice.Aut()
    assert identity(e) == e
    assert identity(f) == f
    assert identity == lattice.Aut().identity()


def test_lattice_identity_morphism_is_composition_identity() -> None:
    lattice = NamedLattices.U
    identity = lattice.identity_morphism()

    assert identity * identity == identity
