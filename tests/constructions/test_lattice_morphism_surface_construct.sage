r"""A lattice morphism is a linear map preserving the selected bilinear form."""

from sage_extensions.all import *  # noqa: F401,F403


def _hyperbolic_plane_identity():
    lattice = NamedLattices.U
    identity = lattice.Mor(lattice).identity()
    return lattice, identity


def test_lattice_identity_is_linear_and_preserves_the_form() -> None:
    lattice, identity = _hyperbolic_plane_identity()
    e = lattice.module_generator(0)
    f = lattice.module_generator(1)

    assert identity.domain() is lattice
    assert identity.codomain() is lattice
    assert identity.linearity_decision() is True
    assert identity(e) == e
    assert identity(f) == f
    assert lattice.b(identity(e), identity(f)) == lattice.b(e, f)


def test_lattice_morphism_composition_preserves_the_form() -> None:
    lattice, identity = _hyperbolic_plane_identity()
    composite = identity * identity
    e = lattice.module_generator(0)
    f = lattice.module_generator(1)

    assert composite(e) == e
    assert composite(f) == f
    assert lattice.b(composite(e), composite(f)) == lattice.b(e, f)
