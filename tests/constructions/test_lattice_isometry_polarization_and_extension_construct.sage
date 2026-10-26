r"""The identity A2 isometry retains invariant polarization and trivial primitive-extension index."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a2_identity_retains_a_nonzero_invariant_polarization() -> None:
    lattice = Lattices(ZZ)("A2")
    identity = lattice.O().one()
    polarization = lattice.module_generator(0)
    polarized = identity.polarized(polarization)

    assert polarized is identity.polarized(polarization)


def test_a2_identity_primitive_extension_has_index_one() -> None:
    lattice = Lattices(ZZ)("A2")
    identity = lattice.O().one()

    assert identity.primitive_extension().index() == 1
